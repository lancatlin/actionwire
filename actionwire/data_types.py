
import utils


class Detection:
    def __init__(self, start: float, word: str):
        self.start = start
        self.word = word

    def __str__(self):
        return f"Detection({utils.format_timecode(self.start)}, {self.word})"

class Match:
    def __init__(self, start: float, word: str):
        self.start = start
        self.word = word

    def __str__(self):
        return f"Match({utils.format_timecode(self.start)}, {self.word})"
    
    def format_csv(self):
        return f"{utils.format_timecode(self.start)},{self.word}"
