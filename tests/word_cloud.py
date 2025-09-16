from collections import Counter
import json
import jieba
import sys

def word_cloud(content: str):
    words = jieba.lcut(content)
    print(words[:100])
    return Counter(words)

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        content = f.read()
        counter = word_cloud(content)
        words = []
        for (word, count) in counter.most_common(200):
            # print(f"{word}: {count}")
            words.append(word)
        with open('./data/words.json', 'w') as wf:
            # print(counter.keys())
            json.dump(words, wf, ensure_ascii=False, indent=4)
