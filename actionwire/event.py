from actionwire.action import Action

class Event:
    def __init__(self, keywords: list[str]) -> None:
        self.keywords = keywords

    def check(self) -> Action | None:
        pass
