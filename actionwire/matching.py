import csv
import re
import sys
import reactivex as rx
import reactivex.operators as ops

import utils

keywords = [
    '喝茶',
    '喝这杯水', 
    '自己',
    '醒来',
    '转换',
    '就像你',
]

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

class Matcher:
    def __init__(self, queue: list[Detection], new_match: Match | None):
        self.queue = queue
        self.new_match = new_match

    def match(self, detection: Detection) -> 'Matcher':
        concatStr = ''.join([detection.word for detection in self.queue])
        # print(utils.format_timecode(detection.start), concatStr)
        for keyword in keywords:
            if concatStr.find(keyword) != -1:
                # print(f"Matched: {keyword}")
                return Matcher([], Match(detection.start, keyword))
        return Matcher(self.queue + [detection], None)

    def getMatch(self) -> Match | None:
        return self.new_match

    def __str__(self):
        return f"Matcher(matches={self.matches}, queue={self.queue})"


def load_detections(file_path) -> list[Detection]:
    """Load detections.csv file."""
    detections: list[Detection] = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['timecode'] and row['keyword']:  # Skip empty rows
                    detections.append(Detection(
                        utils.parse_timecode(row['timecode']),
                        row['keyword']
                    ))
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)
    
    return detections

if __name__ == '__main__':
    detections = rx.from_list(load_detections("./data/detections.csv"))
    detections.pipe(
        # ops.map(lambda detection: Detection(detection['start'], detection['word'])),
        ops.scan(lambda matcher, detection: matcher.match(detection), Matcher([], None)),
        ops.map(Matcher.getMatch),
        ops.filter(lambda match: match != None)
    ).subscribe(print)