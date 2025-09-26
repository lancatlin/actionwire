from time import sleep
from typing import final, override
from actionwire.light import LifxLightController


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
    def __init__(self, controller: LifxLightController, diff: int):
        self.controller = controller
        self.diff = diff

    @override
    def do(self):
        self.controller.adjust_brightness(self.diff)
        self.controller.sync()


class FlashAction(Action):
    def __init__(self, controller: LifxLightController, length: float = 0.5):
        super().__init__()
        self.controller: LifxLightController = controller
        self.length: float = length

    @override
    def do(self):
        original = self.controller.brightness()
        self.controller.set_brightness(2 << 15)
        self.controller.sync(200)
        sleep(self.length)
        self.controller.set_brightness(original)
        self.controller.sync(200)


class ColorAction(Action):
    def __init__(self, controller: LifxLightController, color: list[int], diff: int):
        super().__init__()
        self.controller: LifxLightController = controller
        self.color: list[int] = color
        self.diff: int = diff

    @override
    def do(self):
        brightness = self.controller.brightness() + self.diff
        self.controller.set_color(self.color)
        self.controller.set_brightness(brightness)
        self.controller.sync(500)


class SwapColorAction(Action):
    def __init__(self, controller: LifxLightController, colors: list[list[int]]):
        super().__init__()
        self.controller: LifxLightController = controller
        self.colors: list[list[int]] = colors

    @override
    def do(self):
        saturation = self.controller.saturation()
        for color in self.colors:
            if color[1] != saturation:
                self.controller.set_color(color)
                self.controller.sync(500)
                break
