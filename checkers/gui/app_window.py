import sys

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QLabel, QHBoxLayout

from checkers.image.board import create_board_matrix

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


class WorkerThread(QThread):
    new_board_ready = pyqtSignal(np.ndarray)
    new_image_ready = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, q_image = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(q_image, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                q_image = q_image.scaled(640, 480, Qt.KeepAspectRatio)
                self.new_image_ready.emit(q_image)
                self.new_board_ready.emit(create_board_matrix(rgb_image))


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = WorkerThread()
        self.thread.new_image_ready.connect(self.set_camera_image)
        self.thread.new_board_ready.connect(self.draw_checkerboard)

        # Init UI
        self.__init_ui()
        self.draw_checkerboard()

        self.thread.start()

    def __init_ui(self):
        self.setWindowIcon(QIcon('assets/app_icon.png'))
        # self.setMinimumSize(640, 640)

        # self.button = QPushButton('Update the board')
        # self.button.clicked.connect(self.thread.button_clicked)

        self.image_label = QLabel()

        self.grid_layout = QGridLayout()
        for i in range(8):
            self.grid_layout.setRowMinimumHeight(i, 80)
            self.grid_layout.setColumnMinimumWidth(i, 80)
        self.grid_layout.setSpacing(0)

        self.v_box_layout = QVBoxLayout()
        # self.v_box_layout.addWidget(self.button)
        self.v_box_layout.addLayout(self.grid_layout)
        # self.v_box_layout.setContentsMargins(0, 0, 0, 0)

        self.h_box_layout = QHBoxLayout()
        self.h_box_layout.addWidget(self.image_label)
        self.h_box_layout.addLayout(self.v_box_layout)
        self.setLayout(self.h_box_layout)

    @pyqtSlot(QImage)
    def set_camera_image(self, img):
        self.image_label.setPixmap(QPixmap.fromImage(img))

    @pyqtSlot(np.ndarray)
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

    sys.exit(app.exec_())
