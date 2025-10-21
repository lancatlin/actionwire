import argparse
import sys
from typing import Callable
import wave
import reactivex as rx
from reactivex.observable import Observable

from actionwire import config, convert_audio, matching, mic, voice_detection
from actionwire.action import Action
from actionwire.data_types import Match
from actionwire.light import GroupLightController, LifxLightController
from actionwire.logic import create_events
from actionwire.synchan import SynchanController, create_synchan


def subscribe(action: Action):
    print(action)
    action.do()


def callback(keyword_stream: Observable[Match]):
    c = config.load_config(config.CONFIG_PATH)
    p_light = GroupLightController(
        c.p_lights,
        name="Philosopher",
        color=config.YELLOW,
        brightness=config.initial_brightness,
    )
    w_light = GroupLightController(
        c.w_lights,
        name="Who is the speaker",
        color=config.YELLOW,
        brightness=config.initial_brightness,
    )
    synchan = SynchanController(c.synchan_url)
    keyword_stream.subscribe(print)
    print("Create events")
    create_events(
        keyword_stream, create_synchan(c.synchan_url), p_light, w_light, synchan
    ).subscribe(on_next=subscribe, on_error=print)


def from_audio_file(file: str, cb: Callable[[Observable[Match]], None]):
    with wave.open(file, "rb") as wf:
        if (
            wf.getnchannels() != 1
            or wf.getsampwidth() != 2
            or wf.getcomptype() != "NONE"
        ):
            print("Audio file must be WAV format mono PCM.")
            sys.exit(1)

        framerate = wf.getframerate()
        # detection_stream = rx.from_list(matching.load_detections('./data/detections.csv'))
        audio_stream = convert_audio.create_from_audio(wf)
        vosk_stream = audio_stream.pipe(voice_detection.create_vosk(framerate))
        detection_stream = voice_detection.create_detection_stream(vosk_stream)
        scanner = matching.KeywordScanner(config.keywords)
        cb(scanner.scan(detection_stream))


def from_mic(cb: Callable[[Observable[Match]], None]):
    # detection_stream = rx.from_list(matching.load_detections('./data/detections.csv'))
    audio_stream = mic.mic_stream
    vosk_stream = audio_stream.pipe(voice_detection.create_vosk(config.samplerate))
    detection_stream = voice_detection.create_detection_stream(vosk_stream)
    scanner = matching.KeywordScanner(config.keywords)
    cb(scanner.scan(detection_stream))


def from_csv(cb: Callable[[Observable[Match]], None]):
    detection_stream = rx.from_list(matching.load_detections("./data/detections.csv"))
    scanner = matching.KeywordScanner(config.keywords)
    cb(scanner.scan(detection_stream))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare detections.csv and script.csv files"
    )
    parser.add_argument("-f")
    parser.add_argument(
        "--mode",
        choices=["file", "mic", "csv"],
        default="mic",
        help="Mode to run: file (from audio file), mic (from microphone), or csv (from detections file)",
    )

    args = parser.parse_args()

    if args.mode == "file":
        if not args.f:
            print("Error: Audio file path required for file mode")
            sys.exit(1)
        from_audio_file(args.f, callback)
    elif args.mode == "mic":
        from_mic(callback)
    elif args.mode == "csv":
        from_csv(callback)
