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


class FlashAction(Action):
    def __init__(self, controller: LifxLightController, length: float = 0.5):
        super().__init__()
        self.controller: LifxLightController = controller
        self.length: float = length

    @override
    def do(self):
        original = self.controller.brightness()
        self.controller.set_brightness(2 << 15, duration=200)
        sleep(self.length)
        self.controller.set_brightness(original, duration=200)


class ColorAction(Action):
    def __init__(self, controller: LifxLightController, color: list[int], diff: int):
        super().__init__()
        self.controller: LifxLightController = controller
        self.color: list[int] = color
        self.diff: int = diff

    @override
    def do(self):
        brightness = self.controller.brightness()
        color = [self.color[0], self.color[1], brightness + self.diff, self.color[2]]
        self.controller.set_color(color, duration=500)
