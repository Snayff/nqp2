import pygame

from scripts.misc.utility import offset


class Unit:
    def __init__(self, unit_type, pos=[0, 0]):
        self.type = unit_type
        self.pos = list(pos)

    def update(self):
        pass

    def render(self, surf, shift=(0, 0)):
        pygame.draw.circle(surf, (255, 0, 0), offset(shift.copy(), self.pos), 3)
