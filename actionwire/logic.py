import sys
import wave
import reactivex as rx
from reactivex.observable.observable import Observable
import reactivex.operators as ops
from actionwire import config, convert_audio, matching, mic, voice_detection
from actionwire.action import BrightnessAction, PrintAction, Action
from actionwire.light import LightController
from actionwire.rule import KeyRule
from actionwire.data_types import Match

def subscribe(action: Action):
    print(action)
    action.do()

def create_events(source: Observable[Match]) -> Observable[Action]:
    p_light = LightController(name="Philosopher")
    w_light = LightController(name="Who is the speaker")

    # 自己
    self_stream = source.pipe(
        ops.filter(lambda match: match.word == '自己'),
        ops.map(lambda match: BrightnessAction(p_light, 5))
    )

    # 醒來
    wake_stream = source.pipe(
        ops.filter(lambda match: match.word == '醒来'),
        ops.map(lambda _: BrightnessAction(p_light, 20))
    )

    # 轉換
    change_stream = source.pipe(
        ops.filter(lambda match: match.word == '转换'),
        ops.scan(lambda last, _: -last, 10),
        ops.flat_map(lambda value: rx.of(BrightnessAction(p_light, -value), BrightnessAction(w_light, value)))
    )

    # 就像你
    like_you_stream = source.pipe(
        ops.filter(lambda match: match.word == '就像你'),
        ops.flat_map(lambda _: rx.of(BrightnessAction(p_light, 20), BrightnessAction(w_light, -20)))
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

def main():
    with wave.open(sys.argv[1], 'rb') as wf:
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

        input("Press enter to end\n")

if __name__ == '__main__':
    main()
