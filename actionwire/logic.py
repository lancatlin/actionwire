from dataclasses import dataclass
from typing import TypeVar
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
)
from actionwire.light import AbsLightController
from actionwire.data_types import Match
from actionwire.synchan import SynchanController, SynchanState
from actionwire.utils import format_timecode, tc


T = TypeVar("T")


@dataclass
class PlayState:
    triggered: bool
    emit: bool


def swap(pair: list[T], _) -> list[T]:
    return [pair[1], pair[0]]


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

    def replay_reducer(state: PlayState, t: float) -> PlayState:
        if t < 5 and not state.triggered:
            return PlayState(True, True)

        if t > tc("21:00"):
            return PlayState(False, False)

        return PlayState(state.triggered, False)

    replay_stream = current_times.pipe(
        ops.scan(replay_reducer, PlayState(False, False)),
        ops.filter(lambda state: state.emit),
        ops.flat_map(
            lambda _: rx.of(
                ResetAction(p_light),
                ResetAction(w_light),
            )
        ),
    )

    # 自己
    self_stream = keywords.pipe(
        ops.filter(lambda match: match.word == "自己"),
        ops.throttle_first(3),
        ops.map(lambda match: FlashAction(p_light, 0.4)),
    )

    # 醒來
    wake_stream = keywords.pipe(
        ops.filter(lambda match: match.word == "醒来"),
        ops.scan(swap, [p_light, w_light]),
        ops.flat_map(
            lambda pair: [
                ColorAction(pair[0], config.WHITE, config.brightness_step),
                ColorAction(pair[1], config.YELLOW, -config.brightness_step),
            ]
        ),
    )

    # 轉換
    change_stream = keywords.pipe(
        ops.filter(lambda match: match.word == "转换"),
        ops.scan(swap, [p_light, w_light]),
        ops.flat_map(
            lambda pair: [
                ColorAction(pair[0], config.YELLOW, -config.brightness_step),
                ColorAction(pair[1], config.ORANGE, config.brightness_step),
            ]
        ),
    )

    # 就像你
    like_you_stream = keywords.pipe(
        ops.filter(lambda match: match.word == "就像你"),
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

    def drink_reducer(state: PlayState, t) -> PlayState:
        if state.triggered and t > tc("20:00"):
            return PlayState(False, False)

        if not state.triggered and t > tc("12:49") and t < tc("12:59"):
            return PlayState(True, True)

        return PlayState(state.triggered, False)

    # 喝這杯水
    drink_stream = current_times.pipe(
        ops.scan(drink_reducer, PlayState(False, False)),
        ops.filter(lambda state: state.emit),
        ops.flat_map(
            lambda t: rx.merge(
                rx.of(
                    SeekAction(synchan, "00:24"),
                    BrightnessAction(p_light, -config.brightness_step),
                    BrightnessAction(w_light, config.brightness_step),
                ),
                current_times.pipe(
                    ops.filter(lambda t: t > tc("01:22")),
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
        self_stream,
        change_stream,
        tea_stream,
        wake_stream,
        like_you_stream,
        drink_stream,
        timecode,
    )
