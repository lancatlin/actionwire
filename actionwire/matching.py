import csv
import sys
import reactivex as rx
import reactivex.operators as ops

from actionwire.action import Action
from actionwire.data_types import Detection, Match
from actionwire import utils
from actionwire.rule import KeyRule

keywords = [
    '喝茶',
    '喝这杯水', 
    '自己',
    '醒来',
    '转换',
    '就像你',
]

class Matcher:
    def __init__(self, rule: KeyRule, queue: str, action: Action | None):
        self.queue = queue
        self.action = action
        self.rule = rule

    def match(self, detection: Detection) -> 'Matcher':
        queue = self.queue + detection.word
        # print(utils.format_timecode(detection.start), concatStr)
        action = self.rule.satisfies(queue)
        if action:
            return Matcher(self.rule, '', action)
        return Matcher(self.rule, queue, None)

    def hasAction(self) -> bool:
        return self.action is not None

    def getAction(self) -> Action:
        if self.action is not None:
            return self.action
        raise Exception("No new match")

    def __str__(self):
        return f"Matcher(matches={self.matches}, queue={self.queue})"


class KeywordScanner:
    def scan(self, source: rx.Observable[Detection]) -> rx.Observable[Action]:
        return source.pipe(
            ops.scan(Matcher.match, Matcher(KeyRule(keywords), '', None)),
            ops.filter(Matcher.hasAction),
            ops.map(Matcher.getAction),
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
    scanner.scan(detections).subscribe(lambda action: action.do())