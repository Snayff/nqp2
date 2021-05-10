from __future__ import annotations

from typing import TYPE_CHECKING

from scripts.ui.event import EventUI

if TYPE_CHECKING:
    from scripts.management.game import Game

__all__ = ["Event"]


class Event:
    """
    Handles Event interactions and consolidates the rendering. Event is used to give players a text choice.
    """

    def __init__(self, game: Game):
        self.game: Game = game

        self.ui: EventUI = EventUI(game)

    def update(self):
        self.ui.update()

    def render(self):
        self.ui.render(self.game.window.display)


## IMPLEMENTATION NOTES ##
# triggering an event node can cause any node to trigger, including an event.
# chance of each node type is weighted, event being most likely
# when an event is activated roll for the type of event (grab one at random, using rarity as weighting)
# all of this randomness needs to use the seed
#
# how can we articulate the choices and results in json?

## TO DO LIST ##
# TODO - load the data from json
# TODO - display the description and the choices
# TODO - pick event at random, using seed
# TODO - have choice trigger a response; we'll need vars to alter, e.g. gold.
