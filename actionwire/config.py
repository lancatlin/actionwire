from dataclasses import dataclass
import json
import multiprocessing
from typing import Dict, List
from reactivex.scheduler import ThreadPoolScheduler
import sounddevice as sd
from vosk import os  # type: ignore
from actionwire.color import Color

device_info = sd.query_devices(kind="input")
# soundfile expects an int, sounddevice provides a float:
samplerate = int(device_info["default_samplerate"])

thread_count = multiprocessing.cpu_count()
thread_pool_scheduler = ThreadPoolScheduler(thread_count)

keywords = [
    "喝茶",
    "喝这杯水",
    "喝杯水",
    "自己",
    "醒来",
    "转换",
    "就像你",
]

MAX_BRIGHTNESS = 65535
MIN_BRIGHTNESS = 10000

initial_brightness = 40000
brightness_step = 10000

# Hue, Saturation, Brightness, Kelvin
RED = Color("RED", [65535, 65535, 65535, 3500])
ORANGE = Color("ORANGE", [6500, 65535, 65535, 3500])
YELLOW = Color("YELLOW", [9000, 65535, 65535, 3500])
GREEN = Color("GREEN", [16173, 65535, 65535, 3500])
CYAN = Color("CYAN", [29814, 65535, 65535, 3500])
BLUE = Color("BLUE", [43634, 65535, 65535, 3500])
PURPLE = Color("PURPLE", [50486, 65535, 65535, 3500])
PINK = Color("PINK", [58275, 65535, 47142, 3500])
WHITE = Color("WHITE", [58275, 0, 65535, 5500])
COLD_WHITE = Color("COLD_WHITE", [58275, 0, 65535, 9000])
WARM_WHITE = Color("WARM_WHITE", [58275, 0, 65535, 3200])
GOLD = Color("GOLD", [58275, 0, 65535, 2500])

INITIAL_COLOR = YELLOW

# Synchan Settings


@dataclass
class Config:
    synchan_url: str
    p_lights: list[tuple[str, str]]
    w_lights: list[tuple[str, str]]
    timecodes: Dict[str, list[str]]


def load_config(filename: str) -> Config:
    with open(filename, "r") as f:
        obj = json.load(f)
        return Config(
            obj["synchan"], obj["p_lights"], obj["w_lights"], obj["timecodes"]
        )


CONFIG_PATH = os.getenv("CONFIG_PATH") or "config.json"
