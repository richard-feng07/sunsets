from typing import Any


def relative_error(this: float, target: float) -> float:
    """
    Calculates the relative error between a given and target value. Rounds to 4 decimal places
    """
    try:
        return round(abs(this - target) / target, 4)
    except ZeroDivisionError:
        return 0


def get_sunset_time_average(minutes: int, category: str, sunsets: list[Any]) -> float:
    """
    Returns the new value of a category given the minute of the sunset. Computes average based on weight of minute
    """
    weight_one: float = (60 - minutes) / 60
    weight_two: float = 1 - weight_one
    ans: float = 0
    ans += (sunsets[2]["values"][category]) * weight_one
    ans += (sunsets[3]["values"][category]) * weight_two
    ans = round(ans, 4)
    return ans
