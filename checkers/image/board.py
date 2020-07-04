import cv2
import numpy as np
from skimage.exposure import rescale_intensity
from skimage.filters import threshold_yen

from checkers.image.pawn import pawn_exists, detect_pawn_colour


def detect_board(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_resized = cv2.resize(img, (0, 0), fx=0.6, fy=0.6)
    img_gray_resized = cv2.resize(img_gray, (0, 0), fx=0.6, fy=0.6)
    ret, thresh = cv2.threshold(img_gray_resized, 90, 255, cv2.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    erosion = cv2.erode(thresh, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return crop_board(img_resized, contours)


def create_board_matrix(img):
    board_matrix = np.zeros([8, 8], dtype=int)
    yen_threshold = threshold_yen(img)
    bright = rescale_intensity(img, (0, yen_threshold), (0, 255))
    without_noise = cv2.fastNlMeansDenoisingColored(bright, None, 5, 5, 7, 21)
    for i in range(8):
        for j in range(8):
            square = get_square(img, i, j)
            bright_square = get_square(without_noise, i, j)
            if pawn_exists(square, bright_square):
                colour = detect_pawn_colour(square)
                board_matrix[i][j] = colour.value
    return board_matrix


def crop_board(img, contours):
    filtered_contours = [contour for contour in contours if 1700 < cv2.contourArea(contour) < 3500]
    flat_list_x = []
    flat_list_y = []
    for sublist in filtered_contours:
        for item in sublist:
            flat_list_x.append(item[0][0])
            flat_list_y.append(item[0][1])
    if len(flat_list_x) != 0 and len(flat_list_y) != 0:
        minx = min(flat_list_x)
        maxx = max(flat_list_x)
        miny = min(flat_list_y)
        maxy = max(flat_list_y)
        return img[miny:maxy, minx:maxx]
    print("Cannot detect the board!")


def get_square(img, row, col):
    width = img.shape[0]
    square = width // 8
    x1, y1 = row * square, col * square
    x2, y2 = x1 + square, y1 + square
    return img[x1:x2, y1:y2]
