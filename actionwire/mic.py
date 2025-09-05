from numbers import Number
import sys
import time
import reactivex as rx
import sounddevice as sd  # type: ignore
from reactivex.abc import DisposableBase, ObserverBase, SchedulerBase, disposable

import config


def create_observable(observer: ObserverBase[int], scheduler): 
    observer.on_next(1)
    observer.on_next(2)
    observer.on_next(3)
    observer.on_completed()

ob: rx.Observable[int] = rx.create(create_observable)

ob.subscribe(print)

def create_mic(observer: ObserverBase[bytes], scheduler):
    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        observer.on_next(bytes(indata))

    def finish_callback():
        observer.on_completed()

    # Start the stream asynchronously
    with sd.RawInputStream(samplerate=config.samplerate, blocksize=8000, 
            dtype="int16", channels=1, callback=callback, finished_callback=finish_callback):
        while True:
            time.sleep(1)
            print("waiting...")
    
    

mic_stream = rx.create(create_mic)

if __name__ == "__main__":
    mic_stream.subscribe(lambda x: print("got data", len(x)))

