from enum import Enum


class PawnColour(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2
    UNDEFINED = 3


def opposite(colour):
    if colour == PawnColour.BLACK:
        return PawnColour.WHITE
    else:
        return PawnColour.BLACK
