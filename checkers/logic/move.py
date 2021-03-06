import numpy as np

from checkers.image.pawn_colour import PawnColour
from checkers.image.pawn_colour import opposite
from checkers.logic.move_status import MoveStatus


def check_move(before_matrix, after_matrix, player_colour):
    old_white_positions, new_white_positions = get_old_and_new_positions(before_matrix, after_matrix, PawnColour.WHITE)
    old_black_positions, new_black_positions = get_old_and_new_positions(before_matrix, after_matrix, PawnColour.BLACK)

    # no moves were made
    if np.array_equal(before_matrix, after_matrix):
        return MoveStatus.NO_CHANGE
    # pawn's missing
    if (player_colour == PawnColour.WHITE and new_white_positions.size == 0) or (
            player_colour == PawnColour.BLACK and new_black_positions.size == 0):
        return MoveStatus.UNDEFINED
    # opponent's pawns were moved during players turn
    if (player_colour == PawnColour.WHITE and new_black_positions.size != 0) or (
            player_colour == PawnColour.BLACK and new_white_positions.size != 0):
        return MoveStatus.INCORRECT
    # more than 1 player's pawn was moved
    if (player_colour == PawnColour.WHITE and new_black_positions.size > 1) or (
            player_colour == PawnColour.BLACK and new_white_positions.size > 1):
        return MoveStatus.INCORRECT

    if player_colour == PawnColour.WHITE:
        correct_next_positions, had_to_attack = get_correct_next_positions(
            before_matrix,
            old_white_positions[0],
            PawnColour.BLACK
        )
        if moved_correctly(new_white_positions, correct_next_positions):
            if game_over(after_matrix, opposite(player_colour)) and had_to_attack:
                return MoveStatus.GAME_OVER
            return MoveStatus.CORRECT
    else:
        correct_next_positions, had_to_attack = get_correct_next_positions(
            before_matrix,
            old_black_positions[0],
            PawnColour.WHITE
        )
        if moved_correctly(new_black_positions, correct_next_positions):
            if game_over(after_matrix, opposite(player_colour)) and had_to_attack:
                return MoveStatus.GAME_OVER
            return MoveStatus.CORRECT

    return MoveStatus.INCORRECT


def get_old_and_new_positions(before, after, pawn_colour):
    return np.argwhere(np.logical_and(before == pawn_colour.value, after == 0)), \
           np.argwhere(np.logical_and(before == 0, after == pawn_colour.value))


def get_correct_next_positions(before_matrix, old_position, opponent_color):
    x = old_position[0]
    y = old_position[1]
    has_to_attack = False
    correct_next_positions = []
    corner_positions = [[x - 1, y - 1], [x + 1, y - 1], [x + 1, y + 1], [x - 1, y + 1]]
    behind_corner_positions = [[x - 2, y - 2], [x + 2, y - 2], [x + 2, y + 2], [x - 2, y + 2]]

    for cp, bcp in zip(corner_positions, behind_corner_positions):
        if is_on_board(cp):
            if is_opponent(before_matrix, cp, opponent_color):
                if is_on_board(bcp):
                    if is_empty(before_matrix, bcp) and not has_to_attack:
                        correct_next_positions.clear()
                        has_to_attack = True
                    correct_next_positions.append([bcp[0], bcp[1]])
            elif is_empty(before_matrix, cp) and not has_to_attack:
                if is_forward(old_position, cp, opposite(opponent_color)):
                    correct_next_positions.append([cp[0], cp[1]])
    return correct_next_positions, has_to_attack


def is_on_board(position):
    return position[0] in range(8) and position[1] in range(8)


def is_opponent(before_matrix, position, opponent_color):
    return before_matrix[position[0]][position[1]] == opponent_color.value


def is_empty(before_matrix, position):
    return before_matrix[position[0]][position[1]] == PawnColour.EMPTY.value


def is_forward(old_position, new_position, player_colour):
    if (player_colour == PawnColour.WHITE and new_position[0] >= old_position[0]) \
            or (player_colour == PawnColour.BLACK and new_position[0] <= old_position[0]):
        return False
    return True


def moved_correctly(new_positions, correct_positions):
    for pos in correct_positions:
        if new_positions[0][0] == pos[0] and new_positions[0][1] == pos[1]:
            return True
    return False


def game_over(matrix, opponent_colour):
    for pawn in np.nditer(matrix):
        if pawn == opponent_colour.value:
            return False
    return True


if __name__ == '__main__':
    before_test_matrix = np.array(
        [[0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 1, 0, 0, 0, 0],
         [0, 0, 0, 0, 2, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0]],
        dtype=int
    )

    after_test_matrix = np.array(
        [[0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 2, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0]],
        dtype=int
    )

    print(check_move(before_test_matrix, after_test_matrix, PawnColour.WHITE))
