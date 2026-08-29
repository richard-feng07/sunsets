from typing import Union


CategoryPair = dict[str, Union[str, float]]


def check_payload_dupes(
    sunsets: list[dict[str, list[CategoryPair]]],
    to_add: dict[str, list[CategoryPair]],
) -> None:
    """
    Checks for duplicate dates in the payload.
    Ensures all categorical key-value pairs are added under the same date
    """
    key, _value = next(iter(to_add.items()))
    a = list(set([next(iter(date.keys())) for date in sunsets]))
    if key in a:
        sunsets[-1][key].append(next(iter(to_add.values()))[0])
    else:
        sunsets.append(to_add)
