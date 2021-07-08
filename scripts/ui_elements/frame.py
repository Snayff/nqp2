from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from scripts.core.base_classes.ui_element import UIElement
from scripts.core.constants import DEFAULT_IMAGE_SIZE, StatModifiedStatus
from scripts.scenes.combat.elements.unit import Unit
from scripts.ui_elements.font import Font

if TYPE_CHECKING:
    from typing import List, Tuple, Optional

    from scripts.core.game import Game


__all__ = ["Frame"]


class Frame(UIElement):
    def __init__(self, game: Game, pos: Tuple[int, int], size: Tuple[int, int], image: Optional[pygame.surface] = None,
            text: Optional[str] = None):
        super().__init__(pos, size)

        self.game: Game = game

        if image is None:
            image = pygame.Surface((0, 0))
        self.image: pygame.Surface = image
        self.text: str = text

        self.default_font: Font = self.game.assets.fonts["default"]
        self.disabled_font: Font = self.game.assets.fonts["disabled"]
        self.warning_font: Font = self.game.assets.fonts["warning"]
        self.positive_font: Font = self.game.assets.fonts["positive"]
        self.instruction_font: Font = self.game.assets.fonts["instruction"]

        self.rebuild_surface()



    def update(self, delta_time: float):
        pass

    def rebuild_surface(self):
        surface = self.surface
        image = self.image
        text = self.text
        default_font = self.default_font
        warning_font = self.warning_font
        positive_font = self.positive_font
        instruction_font = self.instruction_font
        gap = 2
        font_height = 12  # FIXME - get actual font height
        start_x = 0
        start_y = 0

        surface.blit(image, (0, 0))

        default_font.render(text, surface, (image.get_width() + gap, font_height // 2))


