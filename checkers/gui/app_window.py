import urllib.request

import cv2
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap, QFont
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

from checkers.image.board import detect_board, create_board_matrix
from checkers.image.pawncolours import PawnColour, opposite
from checkers.logic.move import check_move
from checkers.logic.move_status import MoveStatus


class Worker(QObject):
    new_board_ready_signal = pyqtSignal(np.ndarray)
    new_image_ready_signal = pyqtSignal(QImage)
    new_label_ready_signal = pyqtSignal(str)
    new_pawns_label_ready_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        self.should_emit = False
        self.before_matrix = None
        self.after_matrix = None
        self.player_colour = PawnColour.WHITE
        self.i = 0

    # With camera
    @pyqtSlot()
    def capture_video(self):
        url = 'http://192.168.1.58:8080/shot.jpg'
        while True:
            img_response = urllib.request.urlopen(url)
            img_np = np.array(bytearray(img_response.read()), dtype=np.uint8)
            image = cv2.imdecode(img_np, -1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            q_image = q_image.scaled(640, 480, Qt.KeepAspectRatio)
            self.new_image_ready_signal.emit(q_image)
            if self.should_emit:
                print('Click!')
                self.before_matrix = self.after_matrix
                board = detect_board(image)
                if board is not None:
                    self.after_matrix = create_board_matrix(board)
                    if self.before_matrix is not None:
                        self.__make_move()
                    else:
                        self.emit_new_board(self.after_matrix)
                        self.emit_new_pawns_label(self.count_pawns_and_display(self.after_matrix))
                self.should_emit = False

    # Without camera
    @pyqtSlot()
    def capture_video_no_cam(self):
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
                    elif check_move(self.before_matrix, self.after_matrix, self.player_colour) == MoveStatus.INCORRECT:
                        text = 'Incorrect move'
                    elif check_move(self.before_matrix, self.after_matrix, self.player_colour) == MoveStatus.UNDEFINED:
                        text = 'Undefined move'
                    else:
                        text = 'No change detected'
                    self.player_colour = opposite(self.player_colour)
                    self.emit_new_label(text + ' - ' + str(self.player_colour)[11:].lower() + ' turn')
                    print(self.player_colour)

                self.i = self.i + 1
                self.should_emit = False

    @pyqtSlot(np.ndarray)
    def emit_new_board(self, board):
        self.new_board_ready_signal.emit(board)

    def set_should_emit(self):
        self.should_emit = True

    @pyqtSlot(str)
    def emit_new_label(self, text):
        self.new_label_ready_signal.emit(text)

    @pyqtSlot(str)
    def emit_new_pawns_label(self, text):
        self.new_pawns_label_ready_signal.emit(text)

    def __make_move(self):
        move = check_move(self.before_matrix, self.after_matrix, self.player_colour)
        if move == MoveStatus.CORRECT:
            self.emit_new_board(self.after_matrix)
            self.player_colour = opposite(self.player_colour)
            self.emit_new_label('Correct move - ' + str(self.player_colour)[11:].lower() + ' turn')
        elif move == MoveStatus.INCORRECT:
            self.emit_new_label('Incorrect move - ' + str(self.player_colour)[11:].lower() + ' turn')
            self.after_matrix = self.before_matrix
        elif move == MoveStatus.UNDEFINED:
            self.emit_new_label('Undefined move - ' + str(self.player_colour)[11:].lower() + ' turn')
            self.after_matrix = self.before_matrix
        elif move == MoveStatus.NO_CHANGE:
            self.emit_new_label('No change detected - ' + str(self.player_colour)[11:].lower() + ' turn')

    @staticmethod
    def count_pawns_and_display(board):
        white_pawns = 0
        black_pawns = 0
        for i in np.nditer(board):
            if i == 1:
                black_pawns += 1
            if i == 2:
                white_pawns += 1

        return "White pawns number: " + str(white_pawns) + " \t Black pawns number: " + str(black_pawns)


class AppWindow(QWidget):
    should_emit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__init_worker_thread()
        self.__init_ui()

    def __init_worker_thread(self):
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
        self.setWindowIcon(QIcon('assets/app_icon.png'))

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
