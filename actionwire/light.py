from typing import override
from actionwire import config
from actionwire.color import Color
from actionwire.config import WHITE
from lifxlan import Light  # type:ignore


class AbsLightController:
    def __init__(self, name: str = "", color: Color = WHITE, brightness: int = 50):
        self.name: str = name
        self.color: Color = color
        self.set_brightness(brightness)

    @override
    def __str__(self) -> str:
        return self.name

    def adjust_brightness(self, diff: int):
        self.color = self.color.adjust_brightness(diff)

    def set_brightness(self, brightness: int):
        self.color = self.color.set_brightness(brightness)

    def change_color(self, color: Color):
        self.color = self.color.change_color(color)

    def set_color(self, color: Color):
        self.color = color

    def sync(self, duration: int = 200):
        pass


class LifxLightController(AbsLightController):
    def __init__(self, addr: tuple[str, str], **kwargs):
        self.light: Light = Light(addr[0], addr[1])
        super().__init__(**kwargs)
        self.sync()

    def sync(self, duration: int = 0):
        self.light.set_color(self.color.code(), duration=duration)


class GroupLightController(AbsLightController):
    def __init__(self, addrs: list[tuple[str, str]], **kwargs):
        self.lights: list[AbsLightController] = []
        for addr in addrs:
            try:
                light = LifxLightController(addr, **kwargs)
                self.lights.append(light)
            except Exception as e:
                print(f"Cannot connect to light: {addr}", e)

        super().__init__(**kwargs)
        self.sync()

    def sync(self, duration: int = 0):
        for light in self.lights:
            light.set_color(self.color)
            try:
                light.sync(duration)
            except Exception as e:
                print(f"Cannot sync light: {light}", e)
