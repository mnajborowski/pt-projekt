import sys

import numpy as np
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout)

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
print(test_matrix.shape)


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('assets/app_icon.png'))
        self.setMinimumSize(640, 640)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        # self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid_layout)
        self.draw_checkerboard(board_matrix=test_matrix)

    def draw_checkerboard(self, board_matrix=None):
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Checkers')

    app_window = AppWindow()
    app_window.show()

    sys.exit(app.exec_())
