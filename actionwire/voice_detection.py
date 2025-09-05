from reactivex.abc import ObservableBase
from vosk import KaldiRecognizer, Model
import reactivex as rx
import vosk

import config
import mic


def create_vosk():
    # model = Model(lang="cn")
    # rec = KaldiRecognizer(model, config.samplerate)
    def _vosk(source: rx.Observable[bytes]):
        def subscribe(observer: rx.Observer[str], scheduler):
            def on_next(frame: bytes):
                # print("Received:", frame)
                observer.on_next("hi")

            return source.subscribe(
                on_next,
                observer.on_completed,
                observer.on_error,
                scheduler=scheduler
            )
        return rx.create(subscribe) 
    return _vosk

vosk_stream = mic.mic_stream.pipe(
    create_vosk()
)

if __name__ == '__main__':
    vosk_stream.subscribe(print)