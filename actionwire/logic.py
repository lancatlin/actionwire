import sys
import argparse
import wave
import reactivex as rx
from reactivex.observable.observable import Observable
import reactivex.operators as ops
from actionwire import config, convert_audio, matching, mic, voice_detection
from actionwire.action import BrightnessAction, PrintAction, Action
from actionwire.light import LifxLightController, AbsLightController
from actionwire.rule import KeyRule
from actionwire.data_types import Match

def subscribe(action: Action):
    print(action)
    action.do()

def create_events(source: Observable[Match]) -> Observable[Action]:
    p_light = LifxLightController(config.lights[0], name="Philosopher")
    w_light = AbsLightController(name="Who is the speaker")

    # 自己
    self_stream = source.pipe(
        ops.filter(lambda match: match.word == '自己'),
        ops.map(lambda match: BrightnessAction(p_light, config.brightness_step))
    )

    # 醒來
    wake_stream = source.pipe(
        ops.filter(lambda match: match.word == '醒来'),
        ops.map(lambda _: BrightnessAction(p_light, config.brightness_step))
    )

    # 轉換
    change_stream = source.pipe(
        ops.filter(lambda match: match.word == '转换'),
        ops.scan(lambda last, _: -last, config.brightness_step),
        ops.flat_map(lambda value: rx.of(BrightnessAction(p_light, -value), BrightnessAction(w_light, value)))
    )

    # 就像你
    like_you_stream = source.pipe(
        ops.filter(lambda match: match.word == '就像你'),
        ops.flat_map(lambda _: rx.of(BrightnessAction(p_light, config.brightness_step), BrightnessAction(w_light, -config.brightness_step)))
    )

    # 喝茶
    tea_stream = source.pipe(
        ops.filter(lambda match: match.word == '喝茶'),
        ops.map(lambda match: PrintAction(f"喝茶: {match.timecode()}"))
    )

    # 喝這杯水
    drink_stream = source.pipe(
        ops.filter(lambda match: match.word in ['喝这杯水', '喝杯水']),
        ops.map(lambda match: PrintAction(f"喝這杯水: {match.timecode()}"))
    )

    return rx.merge(
        self_stream,
        change_stream,
        tea_stream,
        wake_stream,
        like_you_stream,
        drink_stream
    )

def from_audio_file(file: str):
    with wave.open(file, 'rb') as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            sys.exit(1)

        framerate = wf.getframerate()
        # detection_stream = rx.from_list(matching.load_detections('./data/detections.csv'))
        audio_stream = convert_audio.create_from_audio(wf)
        vosk_stream = audio_stream.pipe(
            voice_detection.create_vosk(framerate)
        )
        detection_stream = voice_detection.create_detection_stream(vosk_stream)
        scanner = matching.KeywordScanner(config.keywords)
        keyword_stream = scanner.scan(detection_stream)

        create_events(keyword_stream).subscribe(subscribe)


def from_mic():
    # detection_stream = rx.from_list(matching.load_detections('./data/detections.csv'))
    audio_stream = mic.mic_stream
    vosk_stream = audio_stream.pipe(
        voice_detection.create_vosk(config.samplerate)
    )
    detection_stream = voice_detection.create_detection_stream(vosk_stream)
    scanner = matching.KeywordScanner(config.keywords)
    keyword_stream = scanner.scan(detection_stream)

    keyword_stream.subscribe(print)
    create_events(keyword_stream).subscribe(subscribe)


def from_csv():
    detection_stream = rx.from_list(matching.load_detections('./data/detections.csv'))
    scanner = matching.KeywordScanner(config.keywords)
    keyword_stream = scanner.scan(detection_stream)

    create_events(keyword_stream).subscribe(subscribe)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare detections.csv and script.csv files')
    parser.add_argument('-f')
    parser.add_argument('--mode', choices=['file', 'mic', 'csv'], default='mic',
                    help='Mode to run: file (from audio file), mic (from microphone), or csv (from detections file)')

    args = parser.parse_args()

    if args.mode == 'file':
        if not args.f:
            print("Error: Audio file path required for file mode")
            sys.exit(1)
        from_audio_file(args.f)
    elif args.mode == 'mic':
        from_mic()
    elif args.mode == 'csv':
        from_csv()
