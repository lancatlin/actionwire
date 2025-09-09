import json
from reactivex.abc import ObservableBase
from reactivex.observable import Observable
from reactivex.operators import filter, flat_map
from vosk import KaldiRecognizer, Model
import reactivex as rx
import vosk

import config
import mic

CONFIDENCE_THRESHOLD = 0.9

words = [
    "喝",
    "這",
    "杯",
    "水",
    "就像",
    "你",
    "喝茶",
    "自己",
    "醒来",
    "转换",
]

def create_vosk():
    model = Model(model_path="./data/vosk-model-small-cn-0.22")
    # keywords = json.dumps(, ensure_ascii=False)
    keywords = ''
    with open('./words.json', 'r') as f:
        keywords = f.read()

    rec = KaldiRecognizer(model, config.samplerate, keywords)
    rec.SetWords(True)
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
                observer.on_completed,
                observer.on_error,
                scheduler=scheduler
            )
        return rx.create(subscribe) 
    return _vosk

def flatten_result(match):
    return rx.from_list(match["result"])

def high_confidence(result):
    return result['conf'] > CONFIDENCE_THRESHOLD


vosk_stream = mic.mic_stream.pipe(
    create_vosk()
)

if __name__ == '__main__':
    vosk_stream.pipe(
        flat_map(flatten_result),
        # filter(high_confidence),
        filter(lambda result: result['word'] in words),
    ).subscribe(print)
