import multiprocessing
from reactivex.scheduler import ThreadPoolScheduler
import sounddevice as sd  # type: ignore

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

"""

"""

p_lights = [
    ("D0:73:D5:89:63:7B", "10.0.0.244"),  # Wancat
    ("d0:73:d5:86:d6:01", "192.168.0.102"),
]

w_lights = [
    ("D0:73:D5:89:C7:86", "10.0.0.228"),  # Wancat
    ("d0:73:d5:86:dc:21", "192.168.0.103"),
    ("d0:73:d5:86:b6:e6", "192.168.0.104"),
    ("d0:73:d5:86:d5:18", "192.168.0.105"),
]

MAX_BRIGHTNESS = 65535
MIN_BRIGHTNESS = 10000

initial_brightness = 40000
brightness_step = 10000

# Hue, Saturation, Brightness, Kelvin
RED = [65535, 65535, 65535, 3500]
ORANGE = [6500, 65535, 65535, 3500]
YELLOW = [9000, 65535, 65535, 3500]
GREEN = [16173, 65535, 65535, 3500]
CYAN = [29814, 65535, 65535, 3500]
BLUE = [43634, 65535, 65535, 3500]
PURPLE = [50486, 65535, 65535, 3500]
PINK = [58275, 65535, 47142, 3500]
WHITE = [58275, 0, 65535, 5500]
COLD_WHITE = [58275, 0, 65535, 9000]
WARM_WHITE = [58275, 0, 65535, 3200]
GOLD = [58275, 0, 65535, 2500]

# Synchan Settings

SYNCHAN_URL = "http://localhost:3000"
