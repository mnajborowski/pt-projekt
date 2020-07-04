from pathlib import Path

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap, QFont
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

from checkers.gui.worker import Worker


class AppWindow(QWidget):
    assets_path = f'{Path(__file__).parent}/assets'
    should_emit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__init_worker_thread()
        self.__init_ui()

    def __init_worker_thread(self):
        # To use the app without camera replace Worker with WorkerNoCam below
        self.worker = Worker()
        self.should_emit_signal.connect(self.worker.set_should_emit)

        self.thread = QThread()
        # noinspection PyUnresolvedReferences
        self.thread.started.connect(self.worker.capture_video)

        self.worker.new_image_ready_signal.connect(self.set_camera_image)
        self.worker.new_board_ready_signal.connect(self.draw_checkerboard)
        self.worker.new_label_ready_signal.connect(self.update_label)
        self.worker.new_pawns_label_ready_signal.connect(self.update_pawns_label)
        self.worker.moveToThread(self.thread)

        self.thread.start()

    def __init_ui(self):
        self.setWindowIcon(QIcon(f'{self.assets_path}/app_icon.png'))

        self.button = QPushButton('Update the board')
        self.button.clicked.connect(self.update_checkerboard)

        self.text_label = QLabel()
        self.text_label.setText('Make a move - white turn')
        self.text_label.setFont(QFont('Arial', 14))
        self.text_label.setAlignment(Qt.AlignCenter)

        self.pawns_label = QLabel()
        self.pawns_label.setText('White pawns number: X \t Black pawns number: Y')
        self.pawns_label.setFont(QFont('Arial', 11, italic=True))
        self.pawns_label.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()

        self.grid_layout = QGridLayout()
        for i in range(8):
            self.grid_layout.setRowMinimumHeight(i, 80)
            self.grid_layout.setColumnMinimumWidth(i, 80)
        self.grid_layout.setSpacing(0)

        self.v_box_layout = QVBoxLayout()
        self.v_box_layout.addWidget(self.button)
        self.v_box_layout.addWidget(self.text_label)
        self.v_box_layout.addWidget(self.pawns_label)
        self.v_box_layout.addLayout(self.grid_layout)

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

    @pyqtSlot(str)
    def update_label(self, text):
        self.text_label.setText(text)

    @pyqtSlot(str)
    def update_pawns_label(self, text):
        self.pawns_label.setText(text)

    @pyqtSlot(np.ndarray)
    def draw_checkerboard(self, board_matrix=None):
        self.__clear_grid_layout()
        if board_matrix is None:
            for x in range(8):
                for y in range(8):
                    if (x * 7 + y) % 2:
                        square = QSvgWidget(f'{self.assets_path}/dark_square.svg')
                    else:
                        square = QSvgWidget(f'{self.assets_path}/light_square.svg')
                    self.grid_layout.addWidget(square, x, y)
        else:
            for x in range(8):
                for y in range(8):
                    if (x * 7 + y) % 2:
                        if board_matrix[x][y] == 1:
                            square = QSvgWidget(f'{self.assets_path}/dark_square_black_checker.svg')
                        elif board_matrix[x][y] == 2:
                            square = QSvgWidget(f'{self.assets_path}/dark_square_white_checker.svg')
                        else:
                            square = QSvgWidget(f'{self.assets_path}/dark_square.svg')
                    else:
                        if board_matrix[x][y] == 1:
                            square = QSvgWidget(f'{self.assets_path}/light_square_black_checker.svg')
                        elif board_matrix[x][y] == 2:
                            square = QSvgWidget(f'{self.assets_path}/light_square_white_checker.svg')
                        else:
                            square = QSvgWidget(f'{self.assets_path}/light_square.svg')
                    self.grid_layout.addWidget(square, x, y)

    def __clear_grid_layout(self):
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            self.grid_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()
