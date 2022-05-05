from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from nqp.base_classes.image import Image
from nqp.core.constants import AnimationState, DEFAULT_IMAGE_SIZE

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

__all__ = ["Animation"]


class Animation:
    """
    Class to hold visual information for a series of images
    """

    def __init__(
        self,
        frames: Dict[str, List[Image]],
        frame_duration: float = 0.6,
        loop: bool = True,
        starting_frame_set_name: str = None,
        uses_simulation_time: bool = True,
    ):
        self._frame_sets: Dict[str, List[Image]] = frames
        self._frame_duration: float = max(frame_duration, 0.1)  # must be greater than 1
        self._is_looping: bool = loop
        if starting_frame_set_name:
            self._current_frame_set_name: str = starting_frame_set_name
        else:
            self._current_frame_set_name: str = list(self._frame_sets)[0]
        self.uses_simulation_time: bool = uses_simulation_time  # simulation or absolute, i.e. uses game speed

        self._current_num_frames: int = len(self.current_frame_set)
        self._animation_length: float = self._current_num_frames * self._frame_duration

        # flags
        self.delete_on_finish: bool = True

        # progress
        self._state: AnimationState = AnimationState.PLAYING
        self._current_frame_num: int = 0
        self._duration: float = 0
        self._flash_timer: float = 0
        self._flash_colour: None | Tuple[int, int, int] = None

    def update(self, delta_time: float, game_speed: float):
        # exit if not playing
        if self._state != AnimationState.PLAYING:
            return

        # mod delta time if needed
        if self.uses_simulation_time:
            delta_time = delta_time * game_speed
        else:
            delta_time = delta_time

        # update timers
        self._duration += delta_time
        if self._flash_timer > 0:
            self._flash_timer -= delta_time

        # have we reached the end?
        if self._duration >= self._animation_length:
            # reset duration if looping
            if self._is_looping:
                self._duration = 0
            else:
                self._state = AnimationState.FINISHED

        # update frame
        self._current_frame_num = (
            int(self._duration / self._frame_duration * self._current_num_frames) % self._current_num_frames
        )

    def set_current_frame_set_name(self, frame_set_name: str):
        """
        Set the frame set to be used.

        If the name given isnt a valid key no action is taken.
        """
        # catch if we have been passed current frame set
        if frame_set_name == self._current_frame_set_name:
            return

        if frame_set_name in self._frame_sets.keys():
            self._current_frame_set_name = frame_set_name

            # update frame count
            self._current_num_frames = len(self.current_frame_set)
        else:
            logging.warning(f"Tried to set frame set to {frame_set_name} but it doesnt exist.")

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
        self._current_frame_num = 0
        self.delete_on_finish = True

    def get_frame(self, frame_num: int) -> Image:
        """
        Return the Image of the nth frame
        """
        try:
            frame = self.current_frame_set[frame_num]

        except IndexError:
            logging.debug(f"Asked for frame {frame_num} but only have {len(self._frame_sets)}.")
            frame = Image(image=pygame.Surface((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)))

        return frame

    @property
    def image(self) -> Image:
        """
        Return the current frame.
        """
        return self.get_frame(self._current_frame_num)

    @property
    def surface(self) -> pygame.Surface:
        """
        Return the current frame's surface.
        """
        surf = self.get_frame(self._current_frame_num).surface

        # apply flash
        if self._flash_timer > 0:
            surf = surf.copy()
            colour_surf = pygame.Surface(surf.get_size()).convert_alpha()
            colour_surf.fill(self._flash_colour)
            surf.blit(colour_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        return surf

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
        return self.current_frame_set[0].width

    @property
    def height(self) -> int:
        return self.current_frame_set[0].height

    @property
    def current_frame_set(self) -> List[Image]:
        return self._frame_sets[self._current_frame_set_name]

    def flash(self, colour: Tuple[int, int, int], duration: float = 0.05):
        """
        Change the colour of the sprite for a given period.
        """
        self._flash_timer = duration
        self._flash_colour = colour
