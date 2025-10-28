from typing import Callable
import reactivex as rx
from reactivex.observable.observable import Observable
import reactivex.operators as ops
from actionwire import config
from actionwire.action import (
    BrightnessAction,
    FlashAction,
    PrintAction,
    Action,
    ColorAction,
    ResetAction,
    SeekAction,
    SwapColorAction,
    TurnOnAction,
)
from actionwire.light import AbsLightController
from actionwire.data_types import Match
from actionwire.synchan import SynchanController, SynchanState
from actionwire.utils import (
    format_timecode,
    in_timecodes,
    tc,
    swap,
    on_off,
    before,
    after,
    between,
    new_state,
)


def create_events(
    keywords: Observable[Match],
    timecodes: Observable[SynchanState],
    p_light: AbsLightController,
    w_light: AbsLightController,
    synchan: SynchanController,
) -> Observable[Action]:
    print("create logic")

    current_times = timecodes.pipe(
        ops.map(lambda state: state.currentTime),
        ops.share(),
    )

    def from_timecodes(k: str) -> Observable[float]:
        return current_times.pipe(ops.filter(in_timecodes(config.timecodes[k])))

    # 關燈：在開始時關燈，以及 20:26 時關燈
    replay_stream = current_times.pipe(
        ops.scan(on_off(before("00:05"), after("20:25")), new_state()),
        ops.filter(lambda state: state.emit),
        ops.flat_map(
            lambda _: rx.of(
                ResetAction(p_light),
                ResetAction(w_light),
            )
        ),
    )

    # P 開燈：在 00:10 時開 P
    p_on_stream = current_times.pipe(
        ops.scan(on_off(after("00:09"), before("00:09")), new_state()),
        ops.filter(lambda state: state.emit and state.triggered),
        ops.map(lambda _: TurnOnAction(p_light, config.YELLOW)),
    )

    # W 開燈：在 00:25 時開 W
    w_on_stream = current_times.pipe(
        ops.scan(on_off(after("00:31"), before("00:31")), new_state()),
        ops.filter(lambda state: state.emit and state.triggered),
        ops.map(lambda _: TurnOnAction(w_light, config.WHITE)),
    )

    # 自己
    self_stream = rx.merge(
        keywords.pipe(ops.filter(lambda match: match.word == "自己")),
        from_timecodes("自己"),
    ).pipe(
        ops.throttle_first(3),
        ops.map(lambda match: FlashAction(p_light, 0.4)),
    )

    # 醒來
    wake_stream = rx.merge(
        keywords.pipe(ops.filter(lambda match: match.word == "醒来")),
        from_timecodes("醒來"),
    ).pipe(
        ops.scan(swap, [p_light, w_light]),
        ops.flat_map(
            lambda pair: [
                ColorAction(pair[0], config.YELLOW, -config.brightness_step),
                ColorAction(pair[1], config.WHITE, config.brightness_step),
            ]
        ),
    )

    # 轉換
    change_stream = rx.merge(
        keywords.pipe(ops.filter(lambda match: match.word == "转换")),
        from_timecodes("轉換"),
    ).pipe(
        ops.scan(swap, [p_light, w_light]),
        ops.flat_map(
            lambda pair: [
                ColorAction(pair[0], config.YELLOW, -config.brightness_step),
                ColorAction(pair[1], config.ORANGE, config.brightness_step),
            ]
        ),
    )

    # 就像你
    like_you_stream = rx.merge(
        keywords.pipe(ops.filter(lambda match: match.word == "就像你")),
        from_timecodes("就像你"),
    ).pipe(
        ops.flat_map(
            lambda _: rx.of(
                SwapColorAction(p_light, [config.WHITE, config.YELLOW]),
                SwapColorAction(w_light, [config.YELLOW, config.WHITE]),
            )
        ),
    )

    # 喝茶
    tea_stream: Observable[Action] = keywords.pipe(
        ops.filter(lambda match: match.word == "喝茶"),
        ops.with_latest_from(current_times),
        # 避免影片「喝這杯水」誤觸
        ops.filter(
            lambda t: t[1] > tc("00:30")
            # 避免「特別差」誤觸
            # and not (t[1] >= tc("06:30") and t[1] <= tc("07:10"))
        ),
        ops.throttle_first(15),
        ops.flat_map(
            lambda t: rx.merge(
                rx.of(
                    SeekAction(synchan, "00:24"),
                    BrightnessAction(p_light, -config.brightness_step),
                    BrightnessAction(w_light, config.brightness_step),
                ),
                # 8 秒後跳回原位置
                rx.timer(8).pipe(
                    ops.flat_map(
                        lambda _: rx.of(
                            SeekAction(synchan, t[1]),
                            BrightnessAction(p_light, config.brightness_step),
                            BrightnessAction(w_light, -config.brightness_step),
                        )
                    )
                ),
            )
        ),
    )

    # 喝這杯水
    drink_stream = current_times.pipe(
        ops.scan(on_off(between("12:49", "12:59"), after("20:00")), new_state()),
        ops.filter(lambda state: state.emit and state.triggered),
        ops.flat_map(
            lambda t: rx.merge(
                rx.of(
                    SeekAction(synchan, "00:24"),
                    BrightnessAction(p_light, -config.brightness_step),
                    BrightnessAction(w_light, config.brightness_step),
                ),
                current_times.pipe(
                    ops.filter(after("01:22")),
                    ops.take(1),
                    ops.flat_map(
                        lambda _: rx.of(
                            SeekAction(synchan, "12:26"),
                            BrightnessAction(p_light, config.brightness_step),
                            BrightnessAction(w_light, -config.brightness_step),
                        )
                    ),
                ),
            )
        ),
    )

    # Timecode testing
    #
    timecode = current_times.pipe(
        ops.map(
            lambda currentTime: PrintAction(
                f"Current Time: {format_timecode(currentTime)}"
            )
        ),
    )

    return rx.merge(
        replay_stream,
        p_on_stream,
        w_on_stream,
        self_stream,
        change_stream,
        tea_stream,
        wake_stream,
        like_you_stream,
        drink_stream,
        timecode,
    ).pipe(
        ops.start_with(
            ResetAction(p_light),
            ResetAction(w_light),
        )
    )
