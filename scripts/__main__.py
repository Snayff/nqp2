from __future__ import annotations

import logging
import sys
import traceback

import pygame

from scripts.management.game import Game
from scripts.misc import debug
from scripts.misc.constants import GameState


def main():
    """
    The entry for the game initialisation and game loop
    """

    # initialise logging
    if debug.is_logging():
        debug.initialise_logging()

    # initialise profiling
    if debug.is_profiling():
        debug.enable_profiling()

    # run the game
    try:
        game_loop()

    except Exception:
        logging.critical(f"Something went wrong and killed the game loop!")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for line in tb_list:
            clean_line = line.replace("\n", "")
            logging.critical(f"{clean_line}")
        traceback.print_exc()

    # we've left the game loop so now close everything down
    if debug.is_logging():
        debug.kill_logging()
        # print debug values
        debug.print_values_to_console()
    if debug.is_profiling():
        debug.kill_profiler()

    # clean up pygame resources
    pygame.quit()

    # exit window and python
    raise SystemExit


def game_loop():
    """
    The core game loop, handling input, rendering and logic.
    """
    game = Game()

    while game.state == GameState.PLAYING:
        game.run()


if __name__ == "__main__":  # prevents being run from other modules
    main()
