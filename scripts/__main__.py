from __future__ import annotations

import logging
import sys
import traceback

import pygame

from scripts.core import debug
from scripts.core.constants import GameState
from scripts.core.game import Game


def main():
    """
    The entry for the game initialisation and game loop
    """
    game = Game()

    # initialise profiling
    if game.debug.is_profiling:
        game.debug.enable_profiling()

    # run the game
    try:
        game_loop(game)

    except Exception:
        logging.critical(f"Something went wrong and killed the game loop!")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for line in tb_list:
            clean_line = line.replace("\n", "")
            logging.critical(f"{clean_line}")
        traceback.print_exc()

    # we've left the game loop so now close everything down
    if game.debug.is_logging:
        game.debug.kill_logging()
        # print debug values
        game.debug.print_values_to_console()
    if game.debug.is_profiling:
        game.debug.kill_profiler()

    # clean up pygame resources
    pygame.quit()

    # exit window and python
    raise SystemExit


def game_loop(game: Game):
    """
    The core game loop, handling input, rendering and logic.
    """

    while game.state == GameState.PLAYING:
        game.run()


if __name__ == "__main__":  # prevents being run from other modules
    main()
