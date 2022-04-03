from __future__ import annotations

import logging
import random
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

from snecs.typedefs import EntityID

from scripts.world_elements.unit2 import Unit2

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union, Dict
    from scripts.core.game import Game

__all__ = ["EntityBehaviour"]

PATH_UPDATE_FREQ = 0.4  # TODO - move to constants


class EntityBehaviour(ABC):
    def __init__(self, game: Game, unit: Unit2, entity: EntityID):
        self._game: Game = game  # need for terrain interactions
        self._unit: Unit2 = unit
        self._entity = entity

        self.current_path = None
        self.movement_mode = "path"
        self.state = self.movement_mode
        self.target_unit = None
        self.target_entity = None
        self.target_position = None
        self.visibility_line = False

        # update flags
        self.new_move_speed: Optional[float] = None
        self.reset_move_speed: bool = False

        # put entities on different path update cycles
        self.last_path_update = PATH_UPDATE_FREQ * random.random()

    @abstractmethod
    def update(self, delta_time: float):
        pass

    def update_target(self):
        """
        Pick a new target from valid options, as per Unit Behaviour.
        """
        if len(self._unit.behaviour.valid_targets):
            self.target_entity = random.choice(self._unit.behaviour.valid_targets)
        else:
            self.target_entity = None


