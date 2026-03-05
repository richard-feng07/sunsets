from typing import Any


def check_payload_dupes(sunsets: list[dict[str, Any]], to_add: dict[str, Any]):
    key, _value = next(iter(to_add.items()))
    a = list(set([next(iter(date.keys())) for date in sunsets]))
    print(a)
    if key in a:
        print(key)
        sunsets[-1][key].append(next(iter(to_add.values()))[0])
    else:
        sunsets.append(to_add)
