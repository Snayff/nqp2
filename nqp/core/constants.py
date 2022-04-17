from __future__ import annotations

from enum import auto, Enum, IntEnum
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
GAP_SIZE = 10
TILE_SIZE = 16
BARRIER_SIZE = 10

# combat values
WEIGHT_SCALE = 5
DEFENSE_SCALE = 10
PUSH_FORCE = 14
CRIT_MOD = 2.5  # value to multiply by

# UI customisation
TEXT_FADE_OUT_SPEED = 0.5  # make sure it is slower than the fade in
TEXT_FADE_IN_SPEED = 4  # font messes up if this is greater than 4

IMG_FORMATS = ["png", "PNG", "jpg", "jpeg", "JPG"]  # acceptable image formats


# states
class GameState(IntEnum):
    LOADING = auto()
    PLAYING = auto()
    EXITING = auto()


class WorldState(IntEnum):
    CHOOSE_NEXT_ROOM = auto()
    COMBAT = auto()
    EVENT = auto()
    INN = auto()
    MOVING_NEXT_ROOM = auto()
    POST_COMBAT = auto()
    TRAINING = auto()


class CombatState(IntEnum):
    IDLE = auto()
    UNIT_CHOOSE_CARD = auto()
    UNIT_SELECT_TARGET = auto()
    ACTION_CHOOSE_CARD = auto()
    ACTION_SELECT_TARGET_FREE = auto()
    WATCH = auto()
    DEFEAT = auto()
    VICTORY = auto()


class TrainingState(IntEnum):
    IDLE = auto()
    CHOOSE_UPGRADE = auto()
    CHOOSE_TARGET_UNIT = auto()


class PostCombatState(IntEnum):
    DEFEAT = auto()
    VICTORY = auto()
    BOSS_VICTORY = auto()


class InnState(IntEnum):
    IDLE = auto()
    CHOOSE_UNIT = auto()


class EventState(IntEnum):
    IDLE = auto()
    SHOW_RESULT = auto()


class ChooseRoomState(IntEnum):
    IDLE = auto()
    CHOOSE_ROOM = auto()


class AnimationState(IntEnum):
    PLAYING = auto()
    PAUSED = auto()
    FINISHED = auto()


class SceneType(IntEnum):
    MAIN_MENU = auto()
    VIEW_TROUPE = auto()
    RUN_SETUP = auto()
    DEV_DATA_EDITOR = auto()
    DEV_GALLERY = auto()
    WORLD = auto()


class RewardType(IntEnum):
    UNIT = auto()
    ACTION = auto()
    UPGRADE = auto()
    RESOURCE = auto()


class StatModifiedStatus(IntEnum):
    NONE = auto()
    POSITIVE = auto()
    NEGATIVE = auto()
    POSITIVE_AND_NEGATIVE = auto()


class Direction(IntEnum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class FontType(Enum):
    DEFAULT = auto()
    NEGATIVE = auto()
    DISABLED = auto()
    POSITIVE = auto()
    INSTRUCTION = auto()
    NOTIFICATION = auto()


class FontEffects(IntEnum):
    FADE_IN = auto()
    FADE_OUT = auto()


class GamepadButton(IntEnum):
    UP = auto()
    LEFT = auto()
    DOWN = auto()
    RIGHT = auto()
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()
    SELECT_OR_BACK = auto()
    START = auto()
    LEFT_SHOULDER_1 = auto()
    LEFT_SHOULDER_2 = auto()
    RIGHT_SHOULDER_1 = auto()
    RIGHT_SHOULDER_2 = auto()
    LEFT_STICK = auto()
    RIGHT_STICK = auto()


class GamepadAxes(IntEnum):
    LEFT_X = auto()
    LEFT_Y = auto()
    RIGHT_X = auto()
    RIGHT_Y = auto()
    DPAD_X = auto()
    DPAD_Y = auto()


class InputType(IntEnum):
    NONE = auto()
    KEYS = auto()  # keyboard/gamepad
    MOUSE = auto()


class WindowType(IntEnum):
    BASIC = auto()
    FANCY = auto()


class EntityFacing(IntEnum):
    LEFT = auto()
    RIGHT = auto()


class GameSpeed(IntEnum):
    SLOW = 0.5
    NORMAL = 1
    FAST = 3
    FASTEST = 5


class DamageType(IntEnum):
    MUNDANE = auto()
    MAGICAL = auto()