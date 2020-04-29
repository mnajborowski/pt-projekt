import sys

import cv2
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

from checkers.image.board import create_board_matrix, cut_the_board, detect_board


# test_matrix = np.array(
#     [[0, 0, 1, 1, 0, 0, 0, 0],
#      [0, 0, 0, 0, 0, 0, 2, 0],
#      [0, 2, 0, 2, 0, 2, 0, 2],
#      [0, 0, 0, 0, 0, 0, 1, 0],
#      [0, 0, 0, 2, 0, 0, 0, 0],
#      [0, 0, 0, 0, 2, 0, 0, 0],
#      [0, 1, 0, 0, 0, 0, 0, 2],
#      [2, 0, 2, 0, 2, 0, 0, 0]],
#     dtype=int
# )
# test_matrix2 = np.array(
#     [[0, 2, 0, 2, 0, 2, 0, 2],
#      [0, 2, 0, 2, 0, 2, 0, 2],
#      [0, 2, 0, 2, 0, 2, 0, 2],
#      [0, 2, 0, 2, 0, 2, 0, 2],
#      [0, 2, 0, 2, 0, 2, 0, 2],
#      [0, 2, 0, 2, 0, 2, 0, 2],
#      [0, 2, 0, 2, 0, 2, 0, 2],
#      [0, 2, 0, 2, 0, 2, 0, 2]],
#     dtype=int
# )


class Worker(QObject):
    new_board_ready_signal = pyqtSignal(np.ndarray)
    new_image_ready_signal = pyqtSignal(QImage)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.should_emit = False

    @pyqtSlot()
    def capture_video(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, image = cap.read()
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            q_image = q_image.scaled(640, 480, Qt.KeepAspectRatio)
            self.new_image_ready_signal.emit(q_image)
            if self.should_emit:
                print('Click!')
                board = detect_board(image)
                matrix = create_board_matrix(board)
                self.emit_new_board(matrix)
                self.should_emit = False

    @pyqtSlot(np.ndarray)
    def emit_new_board(self, board):
        self.new_board_ready_signal.emit(board)

    # @pyqtSlot()
    def set_should_emit(self):
        self.should_emit = True


class AppWindow(QWidget):
    should_emit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Create Worker and Thread
        self.worker = Worker()
        self.should_emit_signal.connect(self.worker.set_should_emit)
        self.thread = QThread()
        self.thread.started.connect(self.worker.capture_video)
        self.worker.new_image_ready_signal.connect(self.set_camera_image)
        self.worker.new_board_ready_signal.connect(self.draw_checkerboard)
        self.worker.moveToThread(self.thread)
        self.thread.start()

        # Init UI
        self.__init_ui()

    def __init_ui(self):
        self.setWindowIcon(QIcon('assets/app_icon.png'))
        # self.setMinimumSize(640, 640)

        self.button = QPushButton('Update the board')
        self.button.clicked.connect(self.update_checkerboard)

        self.image_label = QLabel()

        self.grid_layout = QGridLayout()
        for i in range(8):
            self.grid_layout.setRowMinimumHeight(i, 80)
            self.grid_layout.setColumnMinimumWidth(i, 80)
        self.grid_layout.setSpacing(0)

        self.v_box_layout = QVBoxLayout()
        self.v_box_layout.addWidget(self.button)
        self.v_box_layout.addLayout(self.grid_layout)
        # self.v_box_layout.setContentsMargins(0, 0, 0, 0)

        self.h_box_layout = QHBoxLayout()
        self.h_box_layout.addWidget(self.image_label)
        self.h_box_layout.addLayout(self.v_box_layout)
        self.setLayout(self.h_box_layout)

        self.draw_checkerboard()

    @pyqtSlot(QImage)
    def set_camera_image(self, img):
        self.image_label.setPixmap(QPixmap.fromImage(img))

    @pyqtSlot()
    def update_checkerboard(self):
        self.should_emit_signal.emit()

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
