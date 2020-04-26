import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout)


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('assets/app_icon.png'))
        self.setMinimumSize(640, 640)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        # self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid_layout)
        self.draw_checkerboard()

    def draw_checkerboard(self):
        for x in range(8):
            for y in range(8):
                if (x * 7 + y) % 2:
                    square = QSvgWidget('assets/dark_square.svg')
                else:
                    square = QSvgWidget('assets/light_square.svg')
                self.grid_layout.addWidget(square, x, y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Checkers')

    app_window = AppWindow()
    app_window.show()

    sys.exit(app.exec_())
