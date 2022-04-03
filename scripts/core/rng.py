from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

from scripts.core.debug import Timer

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["RNG"]


class RNG(random.Random):
    def __init__(self, game: Game):
        with Timer("RNG: initialised"):
            super().__init__()

            self.current_seed = 0

    def set_seed(self, seed: int):
        """
        Set the seed for randomness.
        """
        self.seed(seed)
        self.current_seed = seed
        logging.info(f"Seed set to {seed}.")

    def roll(self, min_value: int = 0, max_value: int = 99) -> int:
        """
        Roll for a number between min and max. Can handle negative numbers.
        """
        return self.randint(min_value, max_value)
