import cv2
import numpy as np

from checkers.image.pawncolours import PawnColour


def find_pawn(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=75,
                               param2=17,
                               minRadius=18)

    if circles is None:
        return False
    return True


def detect_pawn_colour(square):
    gray = cv2.cvtColor(square, cv2.COLOR_BGR2GRAY)

    number_of_pixels = square.shape[0] * square.shape[1]
    hist = cv2.calcHist([gray], [0], None, [256], [0, 100])
    if (np.sum(hist) / number_of_pixels) > 0.6:
        return PawnColour.BLACK
    hist = cv2.calcHist([gray], [0], None, [256], [101, 256])
    if (np.sum(hist) / number_of_pixels) > 0.6:
        return PawnColour.WHITE
    return PawnColour.UNDEFINED
