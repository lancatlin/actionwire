class Action:
    def do(self):
        pass

class PrintAction(Action):
    def __init__(self, text: str):
        self.text = text

    def do(self):
        print("Print action:", self.text)

