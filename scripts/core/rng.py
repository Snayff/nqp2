from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.core.game import Game


__all__ = ["RNG"]


class RNG(random.Random):
    def __init__(self, game: Game):
        # start timer
        start_time = time.time()

        super().__init__()

        self.current_seed = 0

        # record duration
        end_time = time.time()
        logging.debug(f"RNG: initialised in {format(end_time - start_time, '.2f')}s.")

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
