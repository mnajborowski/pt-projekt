import urllib.request

import cv2
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QImage

from checkers.image.board import detect_board, create_board_matrix
from checkers.image.pawn_colour import PawnColour, opposite
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
        elif move == MoveStatus.GAME_OVER:
            self.emit_new_board(self.after_matrix)
            self.emit_new_label('Game over - ' + str(self.player_colour)[11:].lower() + ' wins')
        elif move == MoveStatus.NO_CHANGE:
            self.emit_new_label('No change detected - ' + str(self.player_colour)[11:].lower() + ' turn')

    @staticmethod
    def count_pawns_and_display(board):
        white_pawns_count = 0
        black_pawns_count = 0
        for i in np.nditer(board):
            if i == 1:
                black_pawns_count += 1
            if i == 2:
                white_pawns_count += 1

        return "White pawns count: " + str(white_pawns_count) + " \t Black pawns count: " + str(black_pawns_count)
