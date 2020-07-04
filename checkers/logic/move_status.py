from enum import Enum


class MoveStatus(Enum):
    CORRECT = 1
    INCORRECT = 2
    NO_CHANGE = 3
    UNDEFINED = 4
    GAME_OVER = 5
