class LightController:
    def __init__(self, brightness: int = 50):
        self.brightness = brightness

    def adjust_brightness(self, diff: int):
        self.brightness += diff
        print(f"Brightness: change {diff}. Now {self.brightness}")
