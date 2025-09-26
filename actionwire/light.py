from typing import override
from actionwire.config import WHITE
from lifxlan import Light  # type:ignore

MAX_BRIGHTNESS = 65535


class AbsLightController:
    def __init__(self, name: str = "", brightness: int = 0):
        self.name: str = name
        self.color: list[int] = WHITE
        self.set_brightness(brightness)

    def brightness(self) -> int:
        return self.color[2]

    def hue(self) -> int:
        return self.color[0]

    def saturation(self) -> int:
        return self.color[1]

    def adjust_brightness(self, diff: int):
        self.set_brightness(self.brightness() + diff)
        print(f"{self.name} brightness: change {diff}. Now {self.brightness()}")

    def set_brightness(self, brightness: int):
        new_brightness = min(max(brightness, 0), MAX_BRIGHTNESS)
        self.color = [self.color[0], self.color[1], new_brightness, self.color[3]]

    def set_color(self, color: list[int]):
        self.color = [color[0], color[1], self.brightness(), color[3]]
        print(f"{self.name} color: Now {self.color}")


class LifxLightController(AbsLightController):
    def __init__(self, addr: tuple[str, str], **kwargs):
        self.light: Light = Light(addr[0], addr[1])
        super().__init__(**kwargs)
        self.sync()

    def sync(self, duration: int = 0):
        self.light.set_color(self.color, duration=duration)

    @staticmethod
    def _normalize(brightness: int) -> int:
        scaled = int(brightness / 100 * MAX_BRIGHTNESS)
        return min(max(scaled, 0), MAX_BRIGHTNESS)
