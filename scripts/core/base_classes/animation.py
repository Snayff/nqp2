from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.image import Image
from scripts.core.constants import AnimationState, DEFAULT_IMAGE_SIZE

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Union

__all__ = ["Animation"]


class Animation:
    """
    Class to hold visual information for a series of images
    """

    def __init__(self, frames: List[Image], frame_duration: float = 0.6, loop: bool = True):
        self._frames: List[Image] = frames
        self._frame_duration: float = max(frame_duration, 0.1)  # must be greater than 1
        self._is_looping: bool = loop
        self._num_frames = len(self._frames)
        self._animation_length: float = self._num_frames * self._frame_duration

        self._state: AnimationState = AnimationState.PLAYING
        self._current_frame: int = 0
        self._duration: float = 0

    def update(self, delta_time: float):
        # exit if not playing
        if self._state != AnimationState.PLAYING:
            return

        self._duration += delta_time

        # have we reached the end?
        if self._duration >= self._animation_length:
            # reset duration if looping
            if self._is_looping:
                self._duration = 0
            else:
                self._state = AnimationState.FINISHED

        # update frame
        self._current_frame = int(self._duration / self._frame_duration * self._num_frames) % self._num_frames

    def play(self):
        """
        Resume the animation
        """
        self._state = AnimationState.PLAYING

    def pause(self):
        """
        Pause the animation
        """
        self._state = AnimationState.PAUSED

    def stop(self):
        """
        Finish the animation
        """
        self._state = AnimationState.FINISHED

    def reset(self):
        """
        Reset and pause the animation
        """
        self._state = AnimationState.PAUSED
        self._duration = 0
        self._current_frame = 0

    def get_frame(self, frame_num: int) -> Image:
        """
        Return the Image of the nth frame
        """
        try:
            frame = self._frames[frame_num]

        except IndexError:
            logging.debug(f"Asked for frame {frame_num} but only have {len(self._frames)}.")
            frame = Image(image=pygame.Surface((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)))

        return frame

    @property
    def image(self) -> Image:
        """
        Return the current frame.
        """
        return self.get_frame(self._current_frame)

    @property
    def surface(self) -> pygame.Surface:
        """
        Return the current frame's surface.
        """
        return self.get_frame(self._current_frame).surface

    @property
    def is_finished(self) -> bool:
        """ "
        Return True if this animation has finished playing.
        """
        if self._state == AnimationState.FINISHED:
            result = True
        else:
            result = False

        return result

    @property
    def width(self) -> int:
        return self._frames[0].width

    @property
    def height(self) -> int:
        return self._frames[0].height
