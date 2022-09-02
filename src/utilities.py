def decrease(number, by):
    if is_positive(number):
        return number - by
    else:
        return number + by


def increase(number, by):
    return decrease(number, -by)


def is_positive(number):
    return number >= 0
