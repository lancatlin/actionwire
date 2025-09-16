from lifxlan import Light   # type:ignore


class LightController:
    def __init__(self, addr: tuple[str, str], name: str = "", brightness: int = 10000):
        self.light = Light(addr[0], addr[1])
        self.name = name
        self.brightness = brightness
        self.light.set_brightness(self.brightness)

    def adjust_brightness(self, diff: int):
        self.brightness += diff
        self.light.set_brightness(self.brightness)
        print(f"{self.name} brightness: change {diff}. Now {self.brightness}")

class MockLightController(LightController):
    def __init__(self, name: str = "", brightness: int = 10000):
        self.name = name
        self.brightness = brightness

    def adjust_brightness(self, diff: int):
        self.brightness += diff
        print(f"{self.name} brightness: change {diff}. Now {self.brightness}")
