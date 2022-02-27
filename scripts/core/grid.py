"""
Support grid layouts

code is somewhat WIP because it will be used by other classes at some point

current behavior will wrap movements to the opposite side of the same axis

"""


def grid_up(selected: int, width: int, height: int):
    return selected - width


def grid_down(selected: int, width: int, height: int):
    index = selected + width
    length = width * height
    if index >= length:
        index -= length
    return index


def grid_left(selected: int, width: int, height: int):
    if selected % width == 0:
        index = selected + width - 1
    else:
        index = selected - 1
    return index


def grid_right(selected: int, width: int, height: int):
    index = selected + 1
    length = width * height
    if index % width == 0 or index >= length:
        index -= width
    return index
