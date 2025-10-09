import csv
import sys
import reactivex as rx
import reactivex.operators as ops

from actionwire.action import Action
from actionwire.data_types import Detection, Match
from actionwire import config, utils
from actionwire.rule import KeyRule

class Matcher:
    def __init__(self, keywords: list[str], queue: str, match: Match | None):
        self.queue = queue
        self.new_match = match
        self.keywords = keywords

    def match(self, detection: Detection) -> 'Matcher':
        queue = self.queue + detection.word
        # print(utils.format_timecode(detection.start), concatStr)
        for keyword in self.keywords:
            if queue.find(keyword) != -1:
                return Matcher(self.keywords, '', Match(start=detection.start, word=keyword, confidence=detection.confidence))
        return Matcher(self.keywords, queue, None)

    def hasMatch(self) -> bool:
        return self.new_match is not None

    def getMatch(self) -> Match:
        if self.new_match is not None:
            return self.new_match
        raise Exception("No new match")

    def __str__(self):
        return f"Matcher(matches={self.new_match}, queue={self.queue})"


class KeywordScanner:
    def __init__(self, keywords: list[str]):
        self.keywords = keywords

    def scan(self, source: rx.Observable[Detection]) -> rx.Observable[Match]:
        return source.pipe(
            ops.scan(Matcher.match, Matcher(self.keywords, '', None)),
            ops.filter(Matcher.hasMatch),
            ops.map(Matcher.getMatch),
            ops.share(),
            ops.subscribe_on(config.thread_pool_scheduler)
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
                        utils.tc(row['timecode']),
                        row['keyword'],
                        float(row['confidence']),
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
    scanner = KeywordScanner(config.keywords)
    scanner.scan(detections).subscribe(print)
