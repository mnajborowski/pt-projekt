import cv2
import numpy as np


def search_for_pawn(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    x, dst = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=70,
                               param2=15,
                               minRadius=10,
                               maxRadius=0)
    if circles is None:
        return False
    circles = np.uint16(np.around(circles))
    i = circles[0][0]

    cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
    cv2.imshow('detected circles', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return True
