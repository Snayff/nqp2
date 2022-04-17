from __future__ import annotations

import cProfile
import datetime
import gc
import io
import logging
import os
import pstats
import time
import timeit
from typing import TYPE_CHECKING

import pygame

from nqp.core.constants import DEBUGGING_PATH, FontType, INFINITE, LOGGING_PATH, PROFILING_PATH, VERSION, WorldState
from nqp.ui_elements.generic.font import Font
from nqp.ui_elements.tailored.dev_console import DevConsole

if TYPE_CHECKING:
    from typing import Callable, List, Optional, Tuple, TYPE_CHECKING, Union

    from nqp.core.game import Game

__all__ = ["Debugger", "Timer"]


class Debugger:
    def __init__(self, game: Game):
        with Timer("Debugger: initialised"):

            self._game = game

            # create required folders
            self._create_folders()

            # objects
            self.profiler: Optional[cProfile.Profile] = None
            self._dev_console: Optional[DevConsole] = None

            # counters
            self.current_fps: int = 0
            self.recent_average_fps: int = 0
            self.average_fps: int = 0
            self._frames: int = 0
            self.profile_duration_remaining: int = INFINITE

            # flags
            self.is_profiling: bool = True
            self.is_logging: bool = True
            self.debug_mode: bool = False
            self._show_debug_info: bool = True

            # values
            self._num_frames_considered_recent: int = 600

            # ui
            self._fonts: List[Font] = []

            self.initialise_logging()

    def update(self, delta_time: float):

        self._frames += 1
        self.current_fps = 1  # state.get_internal_clock().get_fps()  # FIXME - fix to new clock
        self.average_fps += (self.current_fps - self.average_fps) / self._frames

        # count down profiler duration, if it isnt running temporarily
        if self.profile_duration_remaining != INFINITE:
            self.profile_duration_remaining -= 1

        # check if profiler needs to turn off
        if self.profile_duration_remaining == 0:
            self.disable_profiling(True)

        # get recent fps
        if self._frames >= self._num_frames_considered_recent:
            frames_to_count = self._num_frames_considered_recent
        else:
            frames_to_count = self._frames
        self.recent_average_fps += (self.current_fps - self.average_fps) / frames_to_count

        if self._dev_console is not None:
            self._dev_console.update(delta_time)

        if self._show_debug_info:
            self._refresh_debug_info()

    def draw(self, surface: pygame.Surface):
        """
        Draw debug info
        """
        if self._show_debug_info:
            for font in self._fonts:
                font.draw(surface)

        if self._dev_console is not None:
            self._dev_console.draw(surface)

    @staticmethod
    def _create_folders():
        #  create folders and prevent FileNotFoundError
        path = str(DEBUGGING_PATH)
        if not os.path.isdir(path + "/"):
            os.mkdir(path)

        profiling_path = str(PROFILING_PATH)
        if not os.path.isdir(profiling_path):
            os.mkdir(profiling_path + "/")

        logging_path = str(LOGGING_PATH)
        if not os.path.isdir(logging_path):
            os.mkdir(logging_path + "/")

    def toggle_dev_console_visibility(self):
        if self._dev_console is None:
            self._dev_console = DevConsole(self._game)
            self._dev_console.focus()
            self._game.input.mode = "typing"
        else:
            self._dev_console = None
            self._game.input.mode = "default"

    def initialise_logging(self):
        """
        Initialise logging.
        """
        # Logging levels:
        #     CRITICAL - A serious error, indicating that may be unable to continue running.
        #     ERROR - A more serious problem, has not been able to perform some function.
        #     WARNING - An indication that something unexpected happened, but otherwise still working as expected.
        #     INFO - Confirmation that things are working as expected.
        #     DEBUG - Detailed information, typically of interest only when diagnosing problems
        #
        # File mode options:
        #     'r' - open for reading(default)
        #     'w' - open for writing, truncating the file first
        #     'x' - open for exclusive creation, failing if the file already exists
        #     'a' - open for writing, appending to the end of the file if it exists

        self.is_logging = True

        log_file_name = "game.log"
        log_level = logging.DEBUG
        file_mode = "w"

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # 8 adds space for 8 characters (# CRITICAL)
        log_format = "%(asctime)s| %(levelname)-8s| %(message)s"
        logging.basicConfig(
            filename=str(DEBUGGING_PATH / "logging" / log_file_name),
            filemode=file_mode,
            level=log_level,
            format=log_format,
        )

        # format into uk time
        logging.Formatter.converter = time.gmtime

        logging.debug(f"Logging initialised.")

    def kill_logging(self):
        """
        Kill logging resources
        """
        logging.shutdown()
        self.is_logging = False

    def _create_profiler(self):
        """
        Create the profiler.
        """
        self.profiler = cProfile.Profile()

    def enable_profiling(self, duration: int = INFINITE):
        """
        Enable profiling. Create profiler if one doesnt exist
        """
        # if we dont have a profiler create one
        if not self.profiler:
            self._create_profiler()

        # enable, set flag and set duration
        assert isinstance(self.profiler, cProfile.Profile)
        self.profiler.enable()
        self.is_profiling = True
        self.profile_duration_remaining = duration

    def disable_profiling(self, dump_data: bool = False):
        """
        Turn off current profiling. Dump data to file if required.
        """
        if self.profiler:
            if dump_data:
                self._dump_profiling_data()

            self.profiler.disable()
            self.is_profiling = False

    def kill_profiler(self):
        """
        Kill profiling resource
        """
        if self.profiler:
            self.disable_profiling(True)
            self.profiler = None

    def _dump_profiling_data(self):
        """
        Dump data to a readable file
        """
        if not self.is_profiling:
            return

        self.profiler.create_stats()

        # dump the profiler stats
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats("tottime")
        profiling_path = str(PROFILING_PATH) + "/"
        ps.dump_stats(profiling_path + "profile.dump")

        # convert profiling to human readable format
        date_and_time = datetime.datetime.utcnow()
        out_stream = open(profiling_path + date_and_time.strftime("%Y%m%d@%H%M") + "_" + VERSION + ".profile", "w")
        ps = pstats.Stats(profiling_path + "profile.dump", stream=out_stream)
        ps.strip_dirs().sort_stats("tottime").print_stats()

    @staticmethod
    def performance_test(
        method_descs: List[str],
        old_methods: List[Tuple[Union[str, Callable], str]],
        new_methods: List[Tuple[Union[str, Callable], str]],
        num_runs: int = 1000,
        repeats: int = 3,
    ) -> str:
        """
        Run performance testing on a collection of methods/functions. Returns a formatted string detailing
        performance  of old, new and % change between them.

        method_descs are used as descriptions only.
        old_methods/new_methods expects a list of tuples that are (method_to_test, setup). Setup can be an empty string
        but is usually an import.
        Index in each list much match, i.e. method_name[0] is the alias of the methods in old_methods[0] and
        new_methods[0].

        Outputs as "Access Trait: 0.00123 -> 0.00036(71.00033%)".

        example usage:
        method_descs = ["Set Var", "Access Skill"]
        old_methods = [("x = 1", ""),("library.get_skill_data('lunge')", "")]
        new_methods = [("x = 'one'", ""), ("library2.SKILLS.get('lunge')", "from scripts.engine import library2")]
        print( performance_test(method_descs, old_methods, new_methods) )
        """
        result = f"== Performance Test ==\n(Run {num_runs} * {repeats})"
        gc.disable()

        for x in range(0, len(method_descs)):
            name = method_descs[x]
            old = min(timeit.repeat(old_methods[x][0], setup=old_methods[x][1], number=num_runs, repeat=repeats))
            new = min(timeit.repeat(new_methods[x][0], setup=new_methods[x][1], number=num_runs, repeat=repeats))
            result += (
                f"\n{name}: {format(old, '0.5f')} -> {format(new, '0.5f')}"
                f"({format(((old - new) / old) * 100, '0.2f')}%)"
            )

        gc.enable()
        return result

    def print_values_to_console(self):
        """
        Print the debuggers stats.
        """
        print(f"Avg FPS: {format(self.average_fps, '.2f')}, R_Avg: {format(self.recent_average_fps, '.2f')}")

    def toggle_debug_info(self):
        """
        Toggle whether the debug info is shown
        """
        if self._show_debug_info:
            self._show_debug_info = False
        else:
            self._show_debug_info = True

    def _refresh_debug_info(self):
        self._fonts = []
        start_x = 1
        start_y = 1

        # FPS
        # TODO - add back in when working
        current_x = start_x
        current_y = start_y
        # current_fps = f"FPS: C={format(self.current_fps, '.2f')}, "
        # recent_fps = f"R_Avg={format(self.recent_average_fps, '.2f')}, "
        # avg_fps = f"Avg={format(self.average_fps, '.2f')}"
        # text = f"{current_fps}; {recent_fps};{avg_fps}"
        # self._fonts.append(self._game.visuals.create_font(FontType.DEFAULT, text, (current_x, current_y)))

        # current state
        current_y += 0
        world = self._game.world
        world_state = world.model.state
        sub_state_name = "not found"
        if world_state == WorldState.COMBAT:
            sub_state_name = world.combat.state.name
        elif world_state == WorldState.TRAINING:
            sub_state_name = world.training.state.name
        elif world_state == WorldState.CHOOSE_NEXT_ROOM:
            sub_state_name = world.choose_room.state.name
        elif world_state == WorldState.MOVING_NEXT_ROOM:
            sub_state_name = "n/a"

        text = f"World state is [{world_state.name}]; room state is [{sub_state_name}]."
        self._fonts.append(self._game.visual.create_font(FontType.DEFAULT, text, pygame.Vector2(current_x, current_y)))

        # game speed
        current_y += 10
        game_speed = self._game.memory.game_speed
        text = f"Game speed = {game_speed}."
        self._fonts.append(self._game.visual.create_font(FontType.DEFAULT, text, pygame.Vector2(current_x, current_y)))


class Timer:
    """
    Context manager to document program time
    """

    def __init__(self, label=None):
        self.label = label
        self.start = None
        self.duration = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.perf_counter() - self.start
        if self.label:
            logging.debug("%s in %.2f seconds.", self.label, self.duration)
        else:
            logging.debug("took %.2f seconds.", self.duration)
