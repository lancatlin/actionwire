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
    SeekAction,
    SwapColorAction,
)
from actionwire.light import AbsLightController
from actionwire.data_types import Match
from actionwire.synchan import SynchanController, SynchanState
from actionwire.utils import format_timecode, parse_timecode


T = TypeVar('T')

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
        ops.do_action(lambda match: print("Found match: ", match)),
        ops.filter(lambda match: match.word == "喝茶"),
        ops.with_latest_from(current_times),
        # 避免影片「喝這杯水」誤觸
        ops.filter(
            lambda t: t[1] < parse_timecode("12:26") or t[1] > parse_timecode("12:55")
        ),
        ops.throttle_first(10),
        ops.flat_map(
            lambda t: rx.merge(
                rx.of(
                    SeekAction(synchan, "00:24"),
                    BrightnessAction(p_light, -config.brightness_step),
                    BrightnessAction(w_light, config.brightness_step),
                ),
                rx.timer(10).pipe(ops.map(lambda _: SeekAction(synchan, t[1]))),
            )
        ),
    )

    # 喝這杯水
    drink_stream = keywords.pipe(
        ops.filter(lambda match: match.word in ["喝这杯水", "喝杯水"]),
        ops.map(lambda match: PrintAction(f"喝這杯水: {match.timecode()}")),
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
        self_stream,
        change_stream,
        tea_stream,
        wake_stream,
        like_you_stream,
        drink_stream,
        timecode,
    )
