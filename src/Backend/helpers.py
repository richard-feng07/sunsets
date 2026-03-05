from typing import Any


def relative_error(this, target):
    try:
        return abs(this - target) / target
    except ZeroDivisionError:
        return 0


def get_sunset_time_average(minutes: int, category: str, sunsets: list[Any]) -> float:
    weight_one: float = (60 - minutes) / 60
    weight_two: float = 1 - weight_one
    ans: float = 0
    ans += (sunsets[2]["values"][category]) * weight_one
    ans += (sunsets[3]["values"][category]) * weight_two
    ans = round(ans, 4)
    return ans
