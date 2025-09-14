import json
from reactivex import operators
from reactivex.abc import ObservableBase
from reactivex.observable import Observable
from reactivex.operators import filter, flat_map, map
from reactivex.scheduler import ImmediateScheduler
from vosk import KaldiRecognizer, Model  # type: ignore
import reactivex as rx
import vosk  # type: ignore

from actionwire.data_types import Detection
import config
import mic

CONFIDENCE_THRESHOLD = 0.7

words = [
    "喝",
    "这",
    "杯",
    "水",
    "就像",
    "你",
    "喝茶",
    "自己",
    "醒来",
    "转换",
    "[unk]",
]

def create_vosk(framerate: int):
    model = Model(model_path="./data/vosk-model-small-cn-0.22")
    keywords = json.dumps(words, ensure_ascii=False)
    # keywords = ''
    # with open('./words.json', 'r') as f:
    #     keywords = f.read()

    rec = KaldiRecognizer(model, framerate, keywords)
    rec.SetWords(True)
    rec.SetMaxAlternatives(0)
    def _vosk(source: rx.Observable[bytes]):
        def subscribe(observer: rx.Observer[object], scheduler):
            def on_next(frame: bytes):
                # print("Received:", frame)
                if rec.AcceptWaveform(frame):
                    observer.on_next(json.loads(rec.Result()))
                else:
                    # print(rec.PartialResult())
                    pass

            return source.subscribe(
                on_next,
                on_completed=observer.on_completed,
                on_error=observer.on_error,
                scheduler=scheduler
            )
        return rx.create(subscribe)
    return _vosk

def flatten_result(match: dict) -> rx.Observable[dict]:
    if 'result' in match:
        return rx.from_list(match["result"], scheduler=ImmediateScheduler())
    else:
        # Skip results without word matches (e.g. partial results)
        return rx.empty()

def high_confidence(result):
    return result['conf'] > CONFIDENCE_THRESHOLD


def create_detection_stream(source: rx.Observable[dict]) -> rx.Observable[Detection]:
    return source.pipe(
        flat_map(flatten_result),
        filter(lambda result: result['word'] != '[unk]'),
        filter(high_confidence),
        map(lambda result: Detection(start=result['start'], word=result['word'], confidence=result['conf']))
    )

if __name__ == '__main__':
    vosk_stream = mic.mic_stream.pipe(
        create_vosk(config.samplerate),
    )

    create_detection_stream(vosk_stream).subscribe(print)
