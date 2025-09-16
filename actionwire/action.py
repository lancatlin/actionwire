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

    def do(self):
        self.controller.adjust_brightness(self.diff)
