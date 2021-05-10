from __future__ import annotations

import random
from typing import TypeVar

import pygame

_V = TypeVar("_V", int, float)  # to represent where we don't know which type is being used


def swap_color(img, old_c, new_c):
    img.set_colorkey(old_c)
    surface = img.copy()
    surface.fill(new_c)
    surface.blit(img, (0, 0))
    surface.set_colorkey((0, 0, 0))
    return surface


def clip(surface, x, y, x_size, y_size):
    handle_surf = surface.copy()
    clip_r = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clip_r)
    image = surface.subsurface(handle_surf.get_clip())
    return image.copy()


def offset(list, offset, offset_mult=1):
    for i, val in enumerate(list):
        list[i] += offset[i] * offset_mult

    return list


def lerp(initial_value: float, target_value: float, lerp_fraction: float) -> float:
    """
    Linear interpolation between initial and target by amount. Fraction clamped between 0 and 1. >=0.99 is treated
    as 1 to handle float imprecision.
    """
    clamped_lerp_fraction = clamp(lerp_fraction, 0, 1)

    if clamped_lerp_fraction >= 0.99:
        return target_value
    else:
        return initial_value * (1 - clamped_lerp_fraction) + target_value * clamped_lerp_fraction


def clamp(value: _V, min_value: _V, max_value: _V) -> _V:
    """
    Return the value, clamped between min and max.
    """
    return max(min_value, min(value, max_value))


def roll(min_value: int = 0, max_value: int = 99) -> int:
    """
    Roll for a number between min and max
    """
    return random.randint(min_value, max_value)

def itr(iterable):
    '''
    An iteration tool for easy removal.
    '''
    return sorted(enumerate(iterable), reverse=True)
