import urllib.request

import cv2
import numpy as np

from checkers.image.pawn import search_for_pawn
from checkers.image.pawncolours import PawnColour


def detect_board(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_resized = cv2.resize(img, (0, 0), fx=0.6, fy=0.6)
    img_gray_resized = cv2.resize(img_gray, (0, 0), fx=0.6, fy=0.6)
    ret, thresh = cv2.threshold(img_gray_resized, 90, 255, cv2.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    erosion = cv2.erode(thresh, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cnt_img = erosion.copy()
    cnt_img = cv2.cvtColor(cnt_img, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(cnt_img, contours, -1, (255, 0, 0), 5)

    board = cut_the_board(img_resized, contours)
    board_matrix = create_board_matrix(board)
    print(board_matrix)

    cv2.imshow("board", board)
    # cv2.imshow('thresh', thresh)
    # cv2.imshow('erosion', erosion)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def cut_the_board(img, contours):
    print(len(contours))
    for contour in contours:
        print(cv2.contourArea(contour))
    filtered_contours = [contour for contour in contours if 2000 < cv2.contourArea(contour) < 3300]
    flat_list_x = []
    flat_list_y = []
    for sublist in filtered_contours:
        for item in sublist:
            flat_list_x.append(item[0][0])
            flat_list_y.append(item[0][1])
    minx = min(flat_list_x)
    maxx = max(flat_list_x)
    miny = min(flat_list_y)
    maxy = max(flat_list_y)

    return img[miny:maxy, minx:maxx]


def get_square(img, row, col):
    width = img.shape[0]
    square = width // 8
    x1, y1 = row * square, col * square
    x2, y2 = x1 + square, y1 + square

    return img[x1:x2, y1:y2]


def detect_pawn_colour(square):
    gray = cv2.cvtColor(square, cv2.COLOR_BGR2GRAY)

    number_of_pixels = square.shape[0] * square.shape[1]
    hist = cv2.calcHist([gray], [0], None, [256], [0, 100])
    print('black')
    print(np.sum(hist) / number_of_pixels)
    if (np.sum(hist) / number_of_pixels) > 0.7:
        return PawnColour.BLACK
    hist = cv2.calcHist([gray], [0], None, [256], [101, 256])
    print('white')
    print(np.sum(hist) / number_of_pixels)
    if (np.sum(hist) / number_of_pixels) > 0.65:
        return PawnColour.WHITE
    return PawnColour.UNDEFINED


def create_board_matrix(img):
    board_matrix = np.zeros([8, 8], dtype=int)
    for i in range(8):
        for j in range(8):
            square = get_square(img, i, j)
            if search_for_pawn(square):
                colour = detect_pawn_colour(square)
                board_matrix[i][j] = colour.value
    return board_matrix


if __name__ == '__main__':
    # img = cv2.imread('plansza2.jpg')
    # detect_board(img)
    url = 'http://192.168.1.39:8080/shot.jpg'
    while True:
        # Use urllib to get the image from the IP camera
        imgResponse = urllib.request.urlopen(url)
        # Numpy to convert into a array
        imgNp = np.array(bytearray(imgResponse.read()), dtype=np.uint8)
        # Decode the array to OpenCV usable format
        img = cv2.imdecode(imgNp, -1)
        # img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        detect_board(img)
        # put the image on screen
        cv2.imshow('IPWebcam', img)
        # Program closes if q is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
