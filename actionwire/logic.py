import reactivex as rx
import reactivex.operators as ops
from actionwire import config, matching, mic, voice_detection
from actionwire.action import BrightnessAction, PrintAction, Action
from actionwire.light import LightController
from actionwire.rule import KeyRule
from re import sub

def subscribe(action: Action):
    print(action)
    action.do()


def main():
    # stream = rx.from_list(matching.load_detections('./data/detections.csv'))
    vosk_stream = mic.mic_stream.pipe(
        voice_detection.create_vosk(config.samplerate)
    )
    detection_stream = voice_detection.create_detection_stream(vosk_stream)
    scanner = matching.KeywordScanner(config.keywords)
    keyword_stream = scanner.scan(detection_stream)

    light_controller = LightController()

    self_stream = keyword_stream.pipe(
        ops.filter(lambda match: match.word == '自己'),
        ops.map(lambda match: BrightnessAction(light_controller, 5))
    )

    tea_stream = keyword_stream.pipe(
        ops.filter(lambda match: match.word == '喝茶'),
        ops.map(lambda match: PrintAction(f"喝茶: {match.timecode()}"))
    )

    rx.merge(self_stream, tea_stream).subscribe(subscribe)
    keyword_stream.subscribe(print)

if __name__ == '__main__':
    main()
