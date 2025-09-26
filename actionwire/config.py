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

lights = [("D0:73:D5:89:63:7B", "10.0.0.244"), ("D0:73:D5:89:C7:86", "10.0.0.228")]

initial_brightness = 40000
brightness_step = 15000

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
