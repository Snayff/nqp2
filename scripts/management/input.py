import pygame
from pygame.locals import *

class Input:
    def __init__(self, game):
        self.game = game

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.game.quit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.game.quit()
