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

def load_detections(file_path):
    """Load detections.csv file."""
    detections = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['timecode'] and row['keyword']:  # Skip empty rows
                    detections.append({
                        'start': parse_timecode(row['timecode']),
                        'word': row['keyword'],
                    })
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)
    
    return detections

def parse_timecode(timecode_str):
    """Convert timecode string (MM:SS) to seconds for easier comparison."""
    try:
        parts = timecode_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        return 0
    except (ValueError, AttributeError):
        return 0

class Match:
    def __init__(self, start: float, word: str):
        self.start = start
        self.word = word

    def __str__(self):
        return f"Match({utils.format_timecode(self.start)}, {self.word})"

class Matcher:
    def __init__(self, matches: list[Match], queue: list[Match]):
        self.matches = matches
        self.queue = queue

    def match(self, detection: Match) -> 'Matcher':
        concatStr = ''.join([detection.word for detection in self.queue])
        print(utils.format_timecode(detection.start), concatStr)
        for keyword in keywords:
            if concatStr.find(keyword) != -1:
                print(f"Matched: {keyword}")
                return Matcher(self.matches + [Match(detection.start, keyword)], [])
        return Matcher(self.matches, self.queue + [detection])

    def __str__(self):
        return f"Matcher(matches={self.matches}, queue={self.queue})"

if __name__ == '__main__':
    detections = rx.from_list(load_detections("./data/detections.csv"))
    detections.pipe(
        ops.map(lambda detection: Match(detection['start'], detection['word'])),
        ops.reduce(lambda matcher, detection: matcher.match(detection), Matcher([], [])),
        ops.flat_map(lambda matcher: matcher.matches)
    ).subscribe(print)