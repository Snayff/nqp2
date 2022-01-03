from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from scripts.core.base_classes.ui import UI
from scripts.core.constants import DEFAULT_IMAGE_SIZE, FontType, GAP_SIZE
from scripts.scenes.combat.elements.camera import Camera
from scripts.scenes.combat.elements.terrain import Terrain
from scripts.ui_elements.frame import Frame
from scripts.ui_elements.panel import Panel

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Type, Union

    import pygame

    from scripts.core.game import Game
    from scripts.ui_elements.unit_stats_frame import UnitStatsFrame


__all__ = ["WorldUI"]


######### TO DO LIST ###############


class WorldUI(UI):
    """
    Represent the UI of a scene
    """

    def __init__(self, game: Game):
        super().__init__(game)

        self.camera: Camera = Camera()
        self.terrain: Terrain = Terrain(self.game)
        self.biome = "plains"
        self.speed = 0
        self.combat_speed = 1
        self.force_idle = False

    def update(self, delta_time: float):
        super().update(delta_time)

        self.speed = self.combat_speed * delta_time

        if not self.force_idle:
            self.terrain.update(self.speed)

    def render(self, surface: pygame.surface):
        # show core info
        self.draw_instruction(surface)

        self.draw_elements(surface)

        self.camera.bind(self.terrain.boundaries)
        combat_surf = pygame.Surface(self.game.window.display.get_size())
        self.terrain.render(combat_surf, self.camera.render_offset())

        self.game.window.display.blit(
            combat_surf,
            (
                -(combat_surf.get_width() - self.game.window.display.get_width()) // 2,
                -(combat_surf.get_height() - self.game.window.display.get_height()) // 2,
            ),
        )

    def rebuild_ui(self):
        super().rebuild_ui()

        self.terrain.generate(self.biome)

