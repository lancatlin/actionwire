import csv
import sys
import reactivex as rx
import reactivex.operators as ops

from actionwire.data_types import Detection, Match
from actionwire import utils

keywords = [
    '喝茶',
    '喝这杯水', 
    '自己',
    '醒来',
    '转换',
    '就像你',
]

class Matcher:
    def __init__(self, queue: str, new_match: Match | None):
        self.queue = queue
        self.new_match = new_match

    def match(self, detection: Detection) -> 'Matcher':
        concatStr = self.queue + detection.word
        # print(utils.format_timecode(detection.start), concatStr)
        for keyword in keywords:
            if concatStr.find(keyword) != -1:
                # print(f"Matched: {keyword}")
                return Matcher('', Match(detection.start, keyword))
        return Matcher(concatStr, None)

    def hasMatch(self) -> bool:
        return self.new_match is not None

    def getMatch(self) -> Match:
        if self.new_match is not None:
            return self.new_match
        raise Exception("No new match")

    def __str__(self):
        return f"Matcher(matches={self.matches}, queue={self.queue})"


class KeywordScanner:
    def scan(self, source: rx.Observable[Detection]) -> rx.Observable[Match]:
        return source.pipe(
            ops.scan(Matcher.match, Matcher('', None)),
            ops.filter(Matcher.hasMatch),
            ops.map(Matcher.getMatch),
            ops.map(Match.format_csv),
        )



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
    scanner = KeywordScanner()
    scanner.scan(detections).subscribe(print)