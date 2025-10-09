from time import sleep
from actionwire.light import AbsLightController
from actionwire.synchan import SynchanController
from actionwire.utils import parse_timecode


class Action:
    def do(self):
        pass

    def __str__(self) -> str:
        return f"{type(self).__name__}"


class PrintAction(Action):
    def __init__(self, text: str):
        self.text = text

    def do(self):
        print("Print action:", self.text)


class BrightnessAction(Action):
    def __init__(self, controller: AbsLightController, diff: int):
        self.controller = controller
        self.diff = diff

    def do(self):
        self.controller.adjust_brightness(self.diff)
        self.controller.sync(200)


class FlashAction(Action):
    def __init__(self, controller: AbsLightController, length: float = 0.5):
        super().__init__()
        self.controller: AbsLightController = controller
        self.length: float = length

    def do(self):
        original = self.controller.brightness()
        self.controller.set_brightness(2 << 15)
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

    def do(self):
        self.controller.set_color(self.color)
        self.controller.adjust_brightness(self.diff)
        self.controller.sync(500)


class SwapColorAction(Action):
    def __init__(self, controller: AbsLightController, colors: list[list[int]]):
        super().__init__()
        self.controller: AbsLightController = controller
        self.colors: list[list[int]] = colors

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
            self.target: int = parse_timecode(target)
        else:
            self.target = target

    def do(self):
        self.controller.seek(self.target)
        self.controller.play()
