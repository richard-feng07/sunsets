import re
from typing import Any, Optional


def format_place(name: Optional[str], fallback: str) -> str:
    """
    Condenses location names into the format City, Region
    """
    if not name:
        return fallback

    parts = [re.sub(r"\(.*?\)", "", p).strip() for p in name.split(",")]
    parts = [p for p in parts if p]
    if not parts:
        return fallback

    if len(parts) > 1:
        parts.pop()
    if len(parts) > 1 and any(char.isdigit() for char in parts[-1]):
        parts.pop()

    return parts[0] if len(parts) == 1 else f"{parts[0]}, {parts[-1]}"


def relative_error(this: float, target: float) -> float:
    """
    Calculates the relative error between a given and target value.
    """
    try:
        return round(abs(this - target) / target, 4)
    except ZeroDivisionError:
        return 0


def get_sunset_time_average(minutes: int, category: str, sunsets: list[Any]) -> float:
    """
    Returns the weighted value of a category given the minute of the sunset.
    """
    weight_one: float = (60 - minutes) / 60
    weight_two: float = 1 - weight_one
    ans: float = 0
    ans += (sunsets[3]["values"][category]) * weight_one
    ans += (sunsets[4]["values"][category]) * weight_two
    ans = round(ans, 4)
    return ans
