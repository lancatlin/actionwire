import reactivex as rx
import reactivex.operators as ops
from actionwire import config, matching, mic, voice_detection
from actionwire.rule import KeyRule
from re import sub


def main():
    # stream = rx.from_list(matching.load_detections('./data/detections.csv'))
    vosk_stream = mic.mic_stream.pipe(
        voice_detection.create_vosk(config.samplerate)
    )
    detection_stream = voice_detection.create_detection_stream(vosk_stream)
    keywords = ['自己', '喝茶']
    scanner = matching.KeywordScanner(keywords)
    keyword_stream = scanner.scan(detection_stream)

    self_stream = keyword_stream.pipe(
        ops.filter(lambda match: match.word == '自己')
    ).subscribe(lambda match: print('自己:', match))

    tea_stream = keyword_stream.pipe(
        ops.filter(lambda match: match.word == '喝茶')
    ).subscribe(lambda match: print('喝茶:', match))

if __name__ == '__main__':
    main()
