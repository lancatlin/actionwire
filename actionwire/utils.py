def format_timecode(sec: float) -> str:
    return f"{int(sec // 60):02d}:{int(sec % 60):02d}"

def tc(timecode_str):
    """Convert timecode string (MM:SS) to seconds for easier comparison."""
    try:
        parts = timecode_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        return 0
    except (ValueError, AttributeError):
        return 0