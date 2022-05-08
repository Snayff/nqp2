from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Union

from nqp.core.constants import GameSpeed
from nqp.core.debug import Timer

if TYPE_CHECKING:
    from typing import List

    from nqp.command.troupe import Troupe
    from nqp.core.game import Game


__all__ = ["Memory"]


class Memory:
    """
    Game related values that persist outside of individual “scenes”. E.g. achievements.
    """

    def __init__(self, game: Game):
        with Timer("Memory: initialised"):

            self._game: Game = game

            self._flags: List[str] = []  # event, game or other flags to note key happenings
            # TODO  - do we need to distinguish between in-run flags and permanent ones?
            self._last_id: int = 0

            self._game_speed: float = GameSpeed.NORMAL.value

    def initialise_run(self, troupe: Troupe, gold: int, rations: int, morale: int, charisma: int, leadership: int):
        """
        Initialise the run's values.
        """
        if self._game.world is None:
            logging.error(f"Tried to initialise a run but WorldScene doesnt exist.")
            raise Exception

        self._game.world.model.reset()

        self._game.world.model.add_troupe(troupe)
        self._game.world.model.amend_gold(gold)
        self._game.world.model.amend_rations(rations)
        self._game.world.model.amend_morale(morale)
        self._game.world.model.amend_charisma(charisma)
        self._game.world.model.amend_leadership(leadership)

    def generate_id(self) -> int:
        """
        Create unique ID for an instance, such as a unit.
        """
        self._last_id += 1
        return self._last_id

    def set_game_speed(self, speed: Union[float, GameSpeed]):
        """
        Set the game speed. 1 is default.
        """
        if isinstance(speed, GameSpeed):
            speed = speed.value

        self._game_speed = speed

    @property
    def game_speed(self) -> float:
        return self._game_speed

    def add_flag(self, flag: str | Enum):
        if isinstance(flag, Enum):
            flag = flag.value.lower()

        self._flags.append(flag)

    def remove_flag(self, flag: str | Enum):
        if isinstance(flag, Enum):
            flag = flag.value.lower()

        self._flags.remove(flag)

    def check_for_flag(self, flag: str | Enum) -> bool:
        """
        Check if a flag exists
        """
        if isinstance(flag, Enum):
            flag = flag.value.lower()

        if flag in self._flags:
            return True
        else:
            return False
