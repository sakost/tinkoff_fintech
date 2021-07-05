from enum import IntEnum, auto
from typing import NamedTuple


class Coordinate(NamedTuple):
    """
    coordinate of something
    """
    x: int
    y: int


class Rotation(IntEnum):
    """
    this class represents all states of rotation of the ship
    """
    VERTICAL = auto()
    HORIZONTAL = auto()


class Size(NamedTuple):
    """
    size in height and width
    """
    height: int
    width: int


class ShotStatus(IntEnum):
    """
    determine the status of the made shot
    """
    MISS = auto()
    HIT = auto()
    SINK = auto()


class MoveStatus(IntEnum):
    """
    status user chose
    """
    EXIT_GAME = auto()
    MOVEMENT = auto()
    SAVE_GAME = auto()
