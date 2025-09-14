class LightController:
    def __init__(self, name: str = "", brightness: int = 50):
        self.name = name
        self.brightness = brightness

    def adjust_brightness(self, diff: int):
        self.brightness += diff
        print(f"{self.name} brightness: change {diff}. Now {self.brightness}")
