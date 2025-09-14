import sys
import threading
import time
import wave
from reactivex import Observable, create
from reactivex.abc import ObserverBase
from reactivex.operators import flat_map, filter, map

from actionwire import config, utils
from actionwire.data_types import Match
from actionwire.matching import KeywordScanner
import voice_detection
from shlex import join


def create_from_audio(wf: wave.Wave_read) -> Observable[bytes]:
    """Create an Observable stream from an audio file.

    Args:
        file: Path to the audio file
        chunk_size: Size of each chunk to read (default: 1024 bytes)

    Returns:
        Observable that emits audio data as bytes
    """
    def subscribe(observer: ObserverBase[bytes], scheduler=None):
        try:
            while True:
                chunk = wf.readframes(8000)
                if len(chunk) == 0:
                    observer.on_completed()
                    break
                observer.on_next(chunk)
                # Small delay to simulate real-time processing
        except Exception as e:
            observer.on_error(e)

    return create(subscribe)

if __name__ == '__main__':
    with wave.open(sys.argv[1], 'rb') as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            sys.exit(1)

        framerate = wf.getframerate()
        audio_stream = create_from_audio(wf)
        vosk_stream = audio_stream.pipe(
            voice_detection.create_vosk(framerate=framerate),
        )
        detection_stream = voice_detection.create_detection_stream(vosk_stream)
        # detection_stream.subscribe(print)

        with open("./data/detections.csv", "w") as f:
            f.write("timecode,keyword\n")
            scanner = KeywordScanner(config.keywords)
            scanner.scan(detection_stream).pipe(
                    map(Match.format_csv)
                ).subscribe(f.write)
            # input("Press enter to stop")
