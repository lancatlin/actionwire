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


class PrintAction(Action):
    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.text}"

    def do(self):
        pass


class ResetAction(Action):
    def __init__(self, controller: AbsLightController):
        self.controller: AbsLightController = controller

    def __str__(self) -> str:
        return f"{type(self).__name__}: Reset {self.controller}"

    def do(self):
        self.controller.change_color(config.INITIAL_COLOR)
        self.controller.set_brightness(config.initial_brightness)
        self.controller.set_power(False)
        self.controller.sync(0)


class TurnOnAction(Action):
    def __init__(self, controller: AbsLightController):
        self.controller: AbsLightController = controller

    def __str__(self) -> str:
        return f"{type(self).__name__}: Turn on {self.controller}"

    def do(self):
        self.controller.set_power(True)
        self.controller.sync(0)


class BrightnessAction(Action):
    def __init__(self, controller: AbsLightController, diff: int):
        self.controller = controller
        self.diff = diff

    def __str__(self) -> str:
        return f"{type(self).__name__}: Change brightness of {self.controller}"

    def do(self):
        self.controller.adjust_brightness(self.diff)
        self.controller.sync(200)


class FlashAction(Action):
    def __init__(self, controller: AbsLightController, length: float = 0.5):
        super().__init__()
        self.controller: AbsLightController = controller
        self.length: float = length

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


class ColorAction(Action):
    def __init__(self, controller: AbsLightController, color: Color, diff: int):
        super().__init__()
        self.controller: AbsLightController = controller
        self.color: Color = color
        self.diff: int = diff

    def __str__(self) -> str:
        return f"{type(self).__name__}: Change color of {self.controller} to {self.color}, {self.diff}"

    def do(self):
        self.controller.change_color(self.color)
        self.controller.adjust_brightness(self.diff)
        self.controller.sync(500)


class SwapColorAction(Action):
    def __init__(self, controller: AbsLightController, colors: list[Color]):
        super().__init__()
        self.controller: AbsLightController = controller
        self.colors: list[Color] = colors

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
