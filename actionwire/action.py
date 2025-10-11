from time import sleep
from actionwire import config
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
        self.controller = controller

    def __str__(self) -> str:
        return f"{type(self).__name__}: Reset {self.controller}"

    def do(self):
        self.controller.set_color(config.YELLOW)
        self.controller.set_brightness(config.initial_brightness)
        self.controller.sync(200)


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
        original = self.controller.brightness()
        new_brightness = (
            config.MAX_BRIGHTNESS if original < 50000 else config.MIN_BRIGHTNESS
        )
        self.controller.set_brightness(new_brightness)
        self.controller.sync(200)
        sleep(self.length)
        self.controller.set_brightness(original)
        self.controller.sync(200)


class ColorAction(Action):
    def __init__(self, controller: AbsLightController, color: list[int], diff: int):
        super().__init__()
        self.controller: AbsLightController = controller
        self.color: list[int] = color
        self.diff: int = diff

    def __str__(self) -> str:
        return f"{type(self).__name__}: Change color of {self.controller} to {self.color}, {self.diff}"

    def do(self):
        self.controller.set_color(self.color)
        self.controller.adjust_brightness(self.diff)
        self.controller.sync(500)


class SwapColorAction(Action):
    def __init__(self, controller: AbsLightController, colors: list[list[int]]):
        super().__init__()
        self.controller: AbsLightController = controller
        self.colors: list[list[int]] = colors

    def __str__(self) -> str:
        return (
            f"{type(self).__name__}: Swap color of {self.controller} to {self.colors}"
        )

    def do(self):
        hue = self.controller.hue()
        saturation = self.controller.saturation()
        for color in self.colors:
            if not (color[0] == hue and color[1] == saturation):
                self.controller.set_color(color)
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
