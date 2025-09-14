
import utils


class Detection:
    def __init__(self, start: float, word: str, confidence: float):
        self.start = start
        self.word = word
        self.confidence = confidence

    def __str__(self):
        return f"Detection({utils.format_timecode(self.start)}, {self.word}, conf: {self.confidence:.2f})"

    def format_csv(self):
        return f"{utils.format_timecode(self.start)},{self.word},{self.confidence}\n"

class Match(Detection):
    # def __init__(self, start: float, word: str):
    #     self.start = start
    #     self.word = word

    def __str__(self):
        return f"Match({utils.format_timecode(self.start)}, {self.word}, conf: {self.confidence:.2f})"

    # def format_csv(self):
    #     return f"{utils.format_timecode(self.start)},{self.word}"

    def timecode(self):
        return utils.format_timecode(self.start)
