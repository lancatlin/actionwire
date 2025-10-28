from dataclasses import dataclass
from typing import Callable, List, TypeVar


def format_timecode(sec: float) -> str:
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"


def tc(timecode_str):
    """Convert timecode string (MM:SS) to seconds for easier comparison."""
    try:
        parts = timecode_str.split(":")
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        return 0
    except (ValueError, AttributeError):
        return 0


T = TypeVar("T")


def swap(pair: list[T], _) -> list[T]:
    return [pair[1], pair[0]]


@dataclass
class PlayState:
    triggered: bool
    emit: bool


def new_state():
    return PlayState(False, False)


def on_off(on: Callable[[float], bool], off: Callable[[float], bool]):
    def reducer(state: PlayState, t: float) -> PlayState:
        if not state.triggered and on(t):
            return PlayState(True, True)

        if state.triggered and off(t):
            return PlayState(False, True)

        return PlayState(state.triggered, False)

    return reducer


def before(t_code: str) -> Callable[[float], bool]:
    return lambda t: t < tc(t_code)


def after(t_code: str) -> Callable[[float], bool]:
    return lambda t: t > tc(t_code)


def between(start: str, end: str) -> Callable[[float], bool]:
    return lambda t: t > tc(start) and t < tc(end)


def in_timecodes(timecodes: List[str]) -> Callable[[float], bool]:
    def predicate(t: float) -> bool:
        for timecode in timecodes:
            s1 = tc(timecode)
            s2 = s1 + 1
            if s1 <= t and s2 >= t:
                return True
        return False

    return predicate
