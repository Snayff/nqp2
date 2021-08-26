from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.constants import StatModifiedStatus
from scripts.core.utility import itr
from scripts.scenes.combat.elements.entity import Entity

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    from scripts.core.game import Game

__all__ = ["Unit"]


class Unit:
    def __init__(self, game: Game, id_: int, unit_type: str, team: str):
        self.game: Game = game

        # persistent
        unit_data = self.game.data.units[unit_type]
        self.id = id_
        self.type: str = unit_type
        self.team: str = team  # this is derived from the Troupe but can be overridden in combat

        # stats that dont use base values
        self.type: str = unit_data["type"]
        self.tier: int = unit_data["tier"]
        self.default_behaviour: str = unit_data["default_behaviour"]

        # stats that include
        base_values = self.game.data.config["unit_base_values"][f"tier_{unit_data['tier']}"]
        self._health: int = unit_data["health"] + base_values["health"]
        self._attack: int = unit_data["attack"] + base_values["attack"]
        self._defence: int = unit_data["defence"] + base_values["defence"]
        self._range: int = unit_data["range"] + base_values["range"]
        self._attack_speed: float = unit_data["attack_speed"] + base_values["attack_speed"]
        self._move_speed: int = unit_data["move_speed"] + base_values["move_speed"]
        # ensure faux-null value is respected
        if unit_data["ammo"] == -1:
            ammo_ = -1
        else:
            ammo_ = unit_data["ammo"] + base_values["ammo"]
        self._ammo: int = ammo_  # number of ranged shots
        self.count: int = unit_data["count"] + base_values["count"]  # number of entities spawned
        self.size: int = unit_data["size"] + base_values["size"]  # size of the hitbox
        self.weight: int = unit_data["weight"] + base_values["weight"]
        self.gold_cost: int = unit_data["gold_cost"] + base_values["gold_cost"]

        self.modifiers: Dict[str, List[int]] = {}

        # during combat
        self.behaviour = self.game.data.behaviours.unit_behaviours[self.default_behaviour](self)
        self.alive: bool = True
        self.colour = (0, 0, 255)
        self.entities: List[Entity] = []
        self.pos: List[int, int] = [0, 0]
        self.placed: bool = False

    @property
    def health(self) -> int:
        value = self._health

        try:
            for mod in self.modifiers["health"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def attack(self) -> int:
        value = self._attack

        try:
            for mod in self.modifiers["attack"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def defence(self) -> int:
        value = self._defence

        try:
            for mod in self.modifiers["defence"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def attack_speed(self) -> float:
        value = self._attack_speed

        try:
            for mod in self.modifiers["attack_speed"]:
                value += mod

        except KeyError:
            pass

        return value

    @property
    def range(self) -> int:
        value = self._range

        try:
            for mod in self.modifiers["range"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def move_speed(self) -> int:
        value = self._move_speed

        try:
            for mod in self.modifiers["move_speed"]:
                value += mod

        except KeyError:
            pass

        return int(value)

    @property
    def ammo(self) -> int:
        value = self._ammo

        try:
            for mod in self.modifiers["ammo"]:
                value += mod

        except KeyError:
            pass

        return value

    def update(self, dt):
        self.update_pos()

        # a unit is alive if all of its entities are alive
        self.alive = bool(len(self.entities))

        self.behaviour.process(dt)

        for i, entity in itr(self.entities):
            entity.update(dt)

            # remove if dead
            if not entity.alive:
                self.entities.pop(i)

    def render(self, surface: pygame.Surface, shift=(0, 0)):
        for entity in self.entities:
            entity.render(surface, shift=shift)

    def reset_for_combat(self):
        """
        Reset the in combat values ready to begin combat.
        """
        self.behaviour = self.game.data.behaviours.unit_behaviours[self.default_behaviour](self)
        self.alive = True
        self.placed = False

        if self.team == "player":
            self.colour = (0, 0, 255)
        else:
            self.colour = (255, 0, 0)

        self.entities = []

    def spawn_entities(self):
        """
        Spawn the unit's entities.
        """
        for i in range(self.count):
            self.entities.append(Entity(self))

    def update_pos(self):
        """
        Update unit "position" by averaging the positions of all its entities.
        """
        if len(self.entities):
            pos = [0, 0]
            for entity in self.entities:
                pos[0] += entity.pos[0]
                pos[1] += entity.pos[1]
            self.pos[0] = pos[0] / len(self.entities)
            self.pos[1] = pos[1] / len(self.entities)

    def add_modifier(self, stat: str, amount: int):
        """
        Add a modifier to a stat.
        """
        if stat in self.modifiers:
            self.modifiers[stat].append(amount)

        else:
            self.modifiers[stat] = [amount]

    def get_modified_status(self, stat: str) -> StatModifiedStatus:
        """
        Check if a given stat is modified.
        """
        modifiers = self.modifiers

        if stat in modifiers:
            has_negatives = any(n < 0 for n in modifiers[stat])
            has_positives = any(n > 0 for n in modifiers[stat])

            if has_negatives and has_positives:
                status = StatModifiedStatus.POSITIVE_AND_NEGATIVE
            elif has_negatives and not has_positives:
                status = StatModifiedStatus.NEGATIVE
            else:
                # not has_negatives and has_positives
                status = StatModifiedStatus.POSITIVE
        else:
            status = StatModifiedStatus.NONE

        return status
