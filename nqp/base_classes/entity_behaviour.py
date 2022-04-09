from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Optional, Tuple

    from snecs.typedefs import EntityID

    from nqp.command.unit import Unit
    from nqp.core.game import Game

__all__ = ["EntityBehaviour"]

PATH_UPDATE_FREQ = 0.4  # TODO - move to constants


class EntityBehaviour(ABC):
    def __init__(self, game: Game, unit: Unit, entity: EntityID):
        self._game: Game = game  # need for terrain interactions
        self._unit: Unit = unit
        self._entity: EntityID = entity

        self.current_path: Optional[List] = None
        self.movement_mode: str = "path"
        self.state: str = self.movement_mode
        self.target_unit: Optional[Unit] = None
        self.target_entity: Optional[EntityID] = None
        self.target_position: Optional[Tuple[int, int]] = None
        self.visibility_line: bool = False
        self.attack_timer: float = 0
        self.is_active: bool = True

        # update flags
        self.new_move_speed: Optional[float] = None
        self.reset_move_speed: bool = False

        # put entities on different path update cycles
        self.last_path_update = PATH_UPDATE_FREQ * random.random()

    @abstractmethod
    def update(self, delta_time: float):
        pass

    def update_target_entity(self):
        """
        Pick a new target from valid options, as per Unit Behaviour.
        """
        if len(self._unit.behaviour.valid_targets):
            self.target_entity = random.choice(self._unit.behaviour.valid_targets)
        else:
            self.target_entity = None
