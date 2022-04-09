from __future__ import annotations

import logging
import os
import time
from typing import Any, TYPE_CHECKING

import pygame

from nqp.core.constants import ASSET_PATH
from nqp.core.debug import Timer

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple

    from nqp.core.game import Game

__all__ = ["Audio"]


class Audio:
    """
    The Audio Engine. It manages all sound interactions
    """

    def __init__(self, game: Game):
        with Timer("Audio: initialised"):

            self._game: Game = game
            self._sounds: Dict[str, pygame.mixer.Sound] = self._load_sounds()
            self._unique_sounds: Dict[str, float] = {}  # sounds that cant be duplicated. sound_name, remaining_duration

    def update(self, delta_time: float):
        # reduce timers in unique sounds
        for sound_name, time_remaining in self._unique_sounds.items():
            self._unique_sounds[sound_name] = time_remaining - delta_time

    @staticmethod
    def _load_sounds() -> Dict[str, pygame.mixer.Sound]:
        """
        Load all sounds from /assets/sounds
        """
        sounds = {}
        sound_counter = 0

        path = ASSET_PATH / "sounds"
        for sound_name in os.listdir(path):
            if sound_name.split(".")[-1] == "wav" or sound_name.split(".")[-1] == "mp3":

                # avoid duplicates
                if sound_name in sounds.keys():
                    logging.warning(f"{sound_name} already loaded, non-unique file name.")

                sound = pygame.mixer.Sound(str(path / sound_name))
                sounds[sound_name.split(".")[0]] = sound

                sound_counter += 1

        logging.debug(f"Audio: {sound_counter} Sounds loaded. ")

        return sounds

    def play_sound(
        self,
        sound_name: str,
        loops: int = 0,
        max_time: float = -1,
        fade_in_ms: float = -1,
        allow_duplicates: bool = True,
    ):
        """
        Play sound. Set loops = -1 to make the sound loop infinitely. Can still be stopped.
        """
        # check if currently blocked as unique
        if sound_name in self._unique_sounds.keys():
            logging.debug(f"{sound_name} already playing as unique so not played again.")

        try:
            sound = self._sounds[sound_name]

            # normalise values to pygame's expected defaults
            if max_time == -1:
                max_time = 0
            if fade_in_ms == -1:
                fade_in_ms = 0

            sound.play(loops, max_time, fade_in_ms)

            if not allow_duplicates:
                # get length
                if max_time != 0:
                    duration = sound.get_length() * (1 + loops)
                else:
                    duration = min(sound.get_length() * (1 + loops), max_time)

                self._unique_sounds[sound_name] = duration

        except KeyError:
            logging.warning(f"Sound [{sound_name} not found.")
