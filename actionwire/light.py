from typing import override
from lifxlan import Light  # type:ignore

MAX_BRIGHTNESS = 65535


class AbsLightController:
    def __init__(self, name: str = "", brightness: int = 0):
        self.name = name
        self.brightness = brightness

    def adjust_brightness(self, diff: int):
        self.set_brightness(self.brightness + diff)
        print(f"{self.name} brightness: change {diff}. Now {self.brightness}")

    def set_brightness(self, brightness: int):
        self.brightness = min(max(brightness, 0), 100)


class LifxLightController(AbsLightController):
    def __init__(self, addr: tuple[str, str], **kwargs):
        super().__init__(**kwargs)
        self.light = Light(addr[0], addr[1])
        self.set_brightness(self.brightness)

    @override
    def set_brightness(self, brightness: int, duration: int = 1000):
        super().set_brightness(brightness)
        self.light.set_brightness(self._normalize(self.brightness), duration=duration)

    @staticmethod
    def _normalize(brightness: int) -> int:
        scaled = int(brightness / 100 * MAX_BRIGHTNESS)
        return min(max(scaled, 0), MAX_BRIGHTNESS)
