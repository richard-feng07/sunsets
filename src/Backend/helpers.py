def relative_error(this, target):
    try:
        return abs(this - target) / target
    except ZeroDivisionError:
        raise ZeroDivisionError("Can't have target value be 0")
