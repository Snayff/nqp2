from __future__ import annotations

from enum import auto, IntEnum
from pathlib import Path

VERSION: str = "0.0.1"

INFINITE: int = 999

# paths
ROOT_PATH = Path(__file__).parent.parent.parent  # constants.py is 2 directories deep
DATA_PATH = ROOT_PATH / "data/"
ASSET_PATH = ROOT_PATH / "assets/"
SAVE_PATH = DATA_PATH / "saves/"
DEBUGGING_PATH = ROOT_PATH / ".debug"
LOGGING_PATH = DEBUGGING_PATH / "logging"
PROFILING_PATH = DEBUGGING_PATH / "profiling"

# sizes
DEFAULT_IMAGE_SIZE = 16

# algorithm/formula constants
WEIGHT_SCALE = 5
DEFENSE_SCALE = 10
PUSH_FORCE = 14


# states
class GameState(IntEnum):
    PLAYING = auto()
    EXITING = auto()


class CombatState(IntEnum):
    UNIT_CHOOSE_CARD = auto()
    UNIT_SELECT_TARGET = auto()
    ACTION_CHOOSE_CARD = auto()
    ACTION_SELECT_TARGET_FREE = auto()
    WATCH = auto()


class MapState(IntEnum):
    LOADING = auto()
    READY = auto()


class NodeState(IntEnum):
    REACHABLE = auto()  # could reach the node
    SELECTABLE = auto()  # can select the node
    NOT_REACHABLE = auto()  # could never reach the node


class NodeType(IntEnum):
    COMBAT = auto()
    EVENT = auto()
    INN = auto()
    TRAINING = auto()
    UNKNOWN = auto()


class SceneType(IntEnum):
    COMBAT = auto()
    REWARD = auto()
    EVENT = auto()
    INN = auto()
    TRAINING = auto()
    OVERWORLD = auto()
    MAIN_MENU = auto()
    TROUPE = auto()
    RUN_SETUP = auto()


class RewardType(IntEnum):
    UNIT = auto()
    ACTION = auto()
    UPGRADE = auto()
    RESOURCE = auto()
