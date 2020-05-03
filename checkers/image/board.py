import cv2
import numpy as np

from checkers.image.pawn import find_pawn, detect_pawn_colour


def detect_board(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_resized = cv2.resize(img, (0, 0), fx=0.2, fy=0.2)
    img_gray_resized = cv2.resize(img_gray, (0, 0), fx=0.2, fy=0.2)
    ret, thresh = cv2.threshold(img_gray_resized, 90, 255, cv2.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    erosion = cv2.erode(thresh, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return crop_board(img_resized, contours)


def create_board_matrix(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    board_matrix = np.zeros([8, 8], dtype=int)
    for i in range(8):
        for j in range(8):
            square = get_square(final, i, j)
            if find_pawn(square):
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
    print("Cannot detect the board! (TUBUDUBU)")


def get_square(img, row, col):
    width = img.shape[0]
    square = width // 8
    x1, y1 = row * square, col * square
    x2, y2 = x1 + square, y1 + square
    return img[x1:x2, y1:y2]
