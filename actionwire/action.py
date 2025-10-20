from dataclasses import dataclass
from time import sleep
from actionwire import config
from actionwire.color import Color
from actionwire.light import AbsLightController
from actionwire.synchan import SynchanController
from actionwire.utils import format_timecode, tc


class Action:
    def do(self):
        pass

    def __str__(self) -> str:
        return f"{type(self).__name__}"


@dataclass
class PrintAction(Action):
    text: str

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.text}"

    def do(self):
        pass


@dataclass
class ResetAction(Action):
    controller: AbsLightController

    def __str__(self) -> str:
        return f"{type(self).__name__}: Reset {self.controller}"

    def do(self):
        self.controller.change_color(config.INITIAL_COLOR)
        self.controller.set_brightness(config.initial_brightness)
        self.controller.set_power(False)
        self.controller.sync(0)


@dataclass
class TurnOnAction(Action):
    controller: AbsLightController
    color: Color | None = None
    brightness: int | None = None

    def __str__(self) -> str:
        return f"{type(self).__name__}: Turn on {self.controller}"

    def do(self):
        self.controller.set_power(True)
        if self.color:
            self.controller.change_color(self.color)
        if self.brightness:
            self.controller.set_brightness(self.brightness)
        self.controller.sync(0)


@dataclass
class BrightnessAction(Action):
    controller: AbsLightController
    diff: int

    def __str__(self) -> str:
        return f"{type(self).__name__}: Change brightness of {self.controller}"

    def do(self):
        self.controller.adjust_brightness(self.diff)
        self.controller.sync(200)


@dataclass
class FlashAction(Action):
    controller: AbsLightController
    length: float = 0.5

    def __str__(self) -> str:
        return f"{type(self).__name__}: Flash of {self.controller}"

    def do(self):
        original = self.controller.color.brightness
        new_brightness = (
            config.MAX_BRIGHTNESS if original < 50000 else config.MIN_BRIGHTNESS
        )
        self.controller.set_brightness(new_brightness)
        self.controller.sync(200)
        sleep(self.length)
        self.controller.set_brightness(original)
        self.controller.sync(200)


@dataclass
class ColorAction(Action):
    controller: AbsLightController
    color: Color
    diff: int

    def __str__(self) -> str:
        return f"{type(self).__name__}: Change color of {self.controller} to {self.color}, {self.diff}"

    def do(self):
        self.controller.change_color(self.color)
        self.controller.adjust_brightness(self.diff)
        self.controller.sync(500)


@dataclass
class SwapColorAction(Action):
    controller: AbsLightController
    colors: list[Color]

    def __str__(self) -> str:
        return (
            f"{type(self).__name__}: Swap color of {self.controller} to {self.colors}"
        )

    def do(self):
        old_color = self.controller.color
        for color in self.colors:
            if color.name != old_color.name:
                self.controller.change_color(color)
                self.controller.sync(500)
                break


class SeekAction(Action):
    def __init__(self, controller: SynchanController, target: int | str) -> None:
        super().__init__()
        self.controller: SynchanController = controller
        if isinstance(target, str):
            self.target: int = tc(target)
        else:
            self.target = target

    def __str__(self) -> str:
        return f"{type(self).__name__}: Seek playhead to {format_timecode(self.target)}"

    def do(self):
        self.controller.seek(self.target)
        self.controller.play()
