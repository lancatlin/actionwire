import json
from reactivex import operators
from reactivex.abc import ObservableBase
from reactivex.observable import Observable
from reactivex.operators import filter, flat_map
from reactivex.scheduler import ImmediateScheduler
from vosk import KaldiRecognizer, Model  # type: ignore
import reactivex as rx
import vosk  # type: ignore

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
    """Flattens a speech recognition result dictionary into an Observable stream of individual word results.
    
    Args:
        match: Dictionary containing speech recognition results from Vosk
        
    Returns:
        Observable that emits individual word recognition results, or empty Observable if no results
    """
    if 'result' in match:
        return rx.from_list(match["result"], scheduler=ImmediateScheduler()) 
    else:
        # Skip results without word matches (e.g. partial results)
        return rx.empty()

def flatten_result_immediate(match: dict):
    """Alternative flatten function that returns the list directly for use with merge_map.
    
    Args:
        match: Dictionary containing speech recognition results from Vosk
        
    Returns:
        List of word results, or empty list if no results
    """
    if 'result' in match:
        return match["result"]
    else:
        return []

def high_confidence(result):
    return result['conf'] > CONFIDENCE_THRESHOLD


vosk_stream = mic.mic_stream.pipe(
    create_vosk(config.samplerate),
)

if __name__ == '__main__':
    vosk_stream.pipe(
        flat_map(flatten_result),
        filter(lambda result: result['word'] != '[unk]')
        # filter(high_confidence),
        # filter(lambda result: result['word'] in words),
    ).subscribe(print)
