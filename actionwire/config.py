import multiprocessing
from reactivex.scheduler import ThreadPoolScheduler
import sounddevice as sd    # type: ignore

device_info = sd.query_devices(kind="input")
# soundfile expects an int, sounddevice provides a float:
samplerate = int(device_info["default_samplerate"])

thread_count = multiprocessing.cpu_count()
thread_pool_scheduler = ThreadPoolScheduler(thread_count)
