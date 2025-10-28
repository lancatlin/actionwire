import csv
import json
from typing import Dict, List


def read_script(file: str) -> Dict[str, List[str]]:
    with open(file, "r") as f:
        reader = csv.DictReader(f, ["timecode", "keyword", "event", "action", "p", "w"])
        reader.__next__()

        result: Dict[str, List[str]] = {}
        for row in reader:
            print(row)
            keyword, timecode = row["keyword"], row["timecode"]
            if keyword in result:
                result[keyword].append(timecode)
            else:
                result[keyword] = [timecode]

        return result


if __name__ == "__main__":
    result = read_script("./data/script.csv")
    print(json.dumps(result, ensure_ascii=False))
