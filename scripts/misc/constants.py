from __future__ import annotations
from enum import auto, IntEnum
from pathlib import Path

VERSION: str = "0.0.1"

INFINITE: int = 999

# paths
ROOT_PATH = Path(__file__).parent.parent.parent  # constants.py is 2 directories deep
DATA_PATH = ROOT_PATH / "data/"
ASSET_PATH = ROOT_PATH / "assets/"
IMAGE_NOT_FOUND_PATH = ASSET_PATH / "debug/image_not_found.png"
SAVE_PATH = DATA_PATH / "saves/"
DEBUGGING_PATH = ROOT_PATH / ".debug"
LOGGING_PATH = DEBUGGING_PATH / "logging"
PROFILING_PATH = DEBUGGING_PATH / "profiling"

# sizes
DEFAULT_IMAGE_SIZE = 16


class CombatState(IntEnum):
    CHOOSE_CARD = auto()
    SELECT_TARGET = auto()
    WATCH = auto()


class GameState(IntEnum):
    PLAYING = auto()
    EXITING = auto()
