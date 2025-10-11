from typing import override
from actionwire import config
from actionwire.config import WHITE
from lifxlan import Light  # type:ignore


class AbsLightController:
    def __init__(self, name: str = "", color: list[int] = WHITE, brightness: int = 50):
        self.name: str = name
        self.color: list[int] = color
        self.set_brightness(brightness)

    @override
    def __str__(self) -> str:
        return self.name

    def brightness(self) -> int:
        return self.color[2]

    def hue(self) -> int:
        return self.color[0]

    def saturation(self) -> int:
        return self.color[1]

    def adjust_brightness(self, diff: int):
        self.set_brightness(self.brightness() + diff)

    def set_brightness(self, brightness: int):
        new_brightness = min(
            max(brightness, config.MIN_BRIGHTNESS), config.MAX_BRIGHTNESS
        )
        self.color = [self.color[0], self.color[1], new_brightness, self.color[3]]

    def set_color(self, color: list[int]):
        self.color = [color[0], color[1], self.brightness(), color[3]]

    def sync(self, duration: int = 200):
        pass


class LifxLightController(AbsLightController):
    def __init__(self, addr: tuple[str, str], **kwargs):
        self.light: Light = Light(addr[0], addr[1])
        super().__init__(**kwargs)
        self.sync()

    def sync(self, duration: int = 0):
        self.light.set_color(self.color, duration=duration)


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
            light.set_brightness(self.brightness())
            try:
                light.sync(duration)
            except Exception as e:
                print(f"Cannot sync light: {light}", e)

    # def set_brightness(self, brightness: int):
    #     for light in self.lights:
    #         light.set_brightness(brightness)

    # def set_color(self, color: list[int]):
    #     for light in self.lights:
    #         light.set_color(color)
