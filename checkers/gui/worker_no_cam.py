import numpy as np
from PyQt5.QtCore import pyqtSlot, QThread

from checkers.gui.worker import Worker
from checkers.image.pawn_colour import opposite
from checkers.logic.move import check_move
from checkers.logic.move_status import MoveStatus

first_matrix = np.array(
    [[0, 1, 0, 1, 0, 1, 0, 1],
     [1, 0, 0, 0, 1, 0, 1, 0],
     [0, 0, 0, 0, 0, 0, 0, 2],
     [0, 0, 2, 0, 1, 0, 0, 0],
     [0, 2, 0, 2, 0, 0, 0, 0],
     [0, 0, 0, 0, 2, 0, 0, 0],
     [0, 2, 0, 2, 0, 0, 0, 2],
     [2, 0, 2, 0, 2, 0, 2, 0]],
    dtype=int
)

second_matrix = np.array(
    [[0, 1, 0, 1, 0, 1, 0, 1],
     [1, 0, 0, 0, 1, 0, 1, 0],
     [0, 0, 0, 0, 0, 2, 0, 2],
     [0, 0, 2, 0, 0, 0, 0, 0],
     [0, 2, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 2, 0, 0, 0],
     [0, 2, 0, 2, 0, 0, 0, 2],
     [2, 0, 2, 0, 2, 0, 2, 0]],
    dtype=int
)

third_matrix = np.array(
    [[0, 1, 0, 1, 0, 1, 0, 1],
     [1, 0, 0, 0, 0, 0, 1, 0],
     [0, 0, 0, 0, 0, 0, 0, 2],
     [0, 0, 2, 0, 0, 0, 1, 0],
     [0, 2, 0, 0, 0, 0, 0, 0],
     [0, 0, 0, 0, 2, 0, 0, 0],
     [0, 2, 0, 2, 0, 0, 0, 2],
     [2, 0, 2, 0, 2, 0, 2, 0]],
    dtype=int
)


class WorkerNoCam(Worker):
    def __init__(self):
        super().__init__()
        self.i = 0

    @pyqtSlot()
    def capture_video(self):
        while True:
            QThread.usleep(16660)
            if self.should_emit:
                self.before_matrix = self.after_matrix
                if self.i == 0:
                    self.after_matrix = first_matrix
                if self.i == 1:
                    self.after_matrix = second_matrix
                if self.i == 2:
                    self.after_matrix = third_matrix
                self.emit_new_board(self.after_matrix)
                self.emit_new_pawns_label(self.count_pawns_and_display(self.after_matrix))

                if self.after_matrix is not None and self.i > 0:
                    print(check_move(self.before_matrix, self.after_matrix, self.player_colour))
                    if check_move(self.before_matrix, self.after_matrix, self.player_colour) == MoveStatus.CORRECT:
                        text = 'Correct move'
                        self.player_colour = opposite(self.player_colour)
                    elif check_move(self.before_matrix, self.after_matrix, self.player_colour) == MoveStatus.INCORRECT:
                        text = 'Incorrect move'
                    elif check_move(self.before_matrix, self.after_matrix, self.player_colour) == MoveStatus.UNDEFINED:
                        text = 'Undefined move'
                    else:
                        text = 'No change detected'
                    self.emit_new_label(text + ' - ' + str(self.player_colour)[11:].lower() + ' turn')
                    print(self.player_colour)

                self.i = self.i + 1
                self.should_emit = False
