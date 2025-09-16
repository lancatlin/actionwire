from lifxlan import Light   # type:ignore

MAX_BRIGHTNESS = 65535

class AbsLightController:
    def __init__(self, name: str = "", brightness: int = 0):
        self.name = name
        self.brightness = brightness

    def adjust_brightness(self, diff: int):
        self.brightness = min(max(self.brightness + diff, 0), 100)
        print(f"{self.name} brightness: change {diff}. Now {self.brightness}")

class LifxLightController(AbsLightController):
    def __init__(self, addr: tuple[str, str], **kwargs):
        super().__init__(**kwargs)
        self.light = Light(addr[0], addr[1])
        self._set_brightness()

    def adjust_brightness(self, diff: int):
        super().adjust_brightness(diff)
        self._set_brightness()

    def _set_brightness(self):
        self.light.set_brightness(self._normalize(self.brightness), duration=1000)

    @staticmethod
    def _normalize(brightness: int) -> int:
        scaled = int(brightness / 100 * MAX_BRIGHTNESS)
        return min(max(scaled, 0), MAX_BRIGHTNESS)
