import sys

import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout

test_matrix = np.array(
    [[0, 0, 1, 1, 0, 0, 0, 0],
     [0, 0, 0, 0, 0, 0, 2, 0],
     [0, 2, 0, 2, 0, 2, 0, 2],
     [0, 0, 0, 0, 0, 0, 1, 0],
     [0, 0, 0, 2, 0, 0, 0, 0],
     [0, 0, 0, 0, 2, 0, 0, 0],
     [0, 1, 0, 0, 0, 0, 0, 2],
     [2, 0, 2, 0, 2, 0, 0, 0]],
    dtype=int
)
test_matrix2 = np.array(
    [[0, 2, 0, 2, 0, 2, 0, 2],
     [0, 2, 0, 2, 0, 2, 0, 2],
     [0, 2, 0, 2, 0, 2, 0, 2],
     [0, 2, 0, 2, 0, 2, 0, 2],
     [0, 2, 0, 2, 0, 2, 0, 2],
     [0, 2, 0, 2, 0, 2, 0, 2],
     [0, 2, 0, 2, 0, 2, 0, 2],
     [0, 2, 0, 2, 0, 2, 0, 2]],
    dtype=int
)


class Worker(QObject):
    new_board_ready = pyqtSignal(np.ndarray)

    @pyqtSlot(np.ndarray)
    def emit_new_board(self, board):
        self.new_board_ready.emit(board)


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Create Worker and Thread
        self.worker = Worker()
        self.thread = QThread()
        self.worker.new_board_ready.connect(self.draw_checkerboard)
        self.worker.moveToThread(self.thread)
        self.thread.start()

        # Init UI
        self.setWindowIcon(QIcon('assets/app_icon.png'))
        self.setMinimumSize(640, 640)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        # self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid_layout)
        self.draw_checkerboard()

    def draw_checkerboard(self, board_matrix=None):
        self.__clear_grid_layout()
        if board_matrix is None:
            for x in range(8):
                for y in range(8):
                    if (x * 7 + y) % 2:
                        square = QSvgWidget('assets/dark_square.svg')
                    else:
                        square = QSvgWidget('assets/light_square.svg')
                    self.grid_layout.addWidget(square, x, y)
        else:
            for x in range(8):
                for y in range(8):
                    if (x * 7 + y) % 2:
                        if board_matrix[x][y] == 1:
                            square = QSvgWidget('assets/dark_square_black_checker.svg')
                        elif board_matrix[x][y] == 2:
                            square = QSvgWidget('assets/dark_square_white_checker.svg')
                        else:
                            square = QSvgWidget('assets/dark_square.svg')
                    else:
                        if board_matrix[x][y] == 1:
                            square = QSvgWidget('assets/light_square_black_checker.svg')
                        elif board_matrix[x][y] == 2:
                            square = QSvgWidget('assets/light_square_white_checker.svg')
                        else:
                            square = QSvgWidget('assets/light_square.svg')

                    self.grid_layout.addWidget(square, x, y)

    def __clear_grid_layout(self):
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Checkers')

    app_window = AppWindow()
    app_window.show()
    app_window.worker.emit_new_board(test_matrix2)
    app_window.worker.emit_new_board(test_matrix)

    sys.exit(app.exec_())
