# ╔══════════════════════════════════════════╗
# ║       Miss Cherry - Time Parser          ║
# ╚══════════════════════════════════════════╝

import re


def parse_time(time_str: str) -> int:
    """
    Convert time string to seconds.
    Examples: "3h" → 10800, "5m" → 300, "2d" → 172800, "1w" → 604800
    Returns 0 if invalid.
    """
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    match = re.fullmatch(r"(\d+)([smhdw])", time_str.strip().lower())
    if not match:
        return 0
    return int(match.group(1)) * units[match.group(2)]


def seconds_to_str(seconds: int) -> str:
    """
    Convert seconds to human readable string.
    Example: 3661 → "1h 1m 1s"
    """
    if seconds <= 0:
        return "0s"
    parts = []
    for unit, val in [("w", 604800), ("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]:
        if seconds >= val:
            parts.append(f"{seconds // val}{unit}")
            seconds %= val
    return " ".join(parts)
