def format_timecode(sec: float) -> str:
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"
