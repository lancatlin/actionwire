import sounddevice as sd    # type: ignore

device_info = sd.query_devices(None, "input")
# soundfile expects an int, sounddevice provides a float:
samplerate = int(device_info["default_samplerate"])
