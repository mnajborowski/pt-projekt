import cv2


def search_for_pawn(img, bright):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_bright = cv2.cvtColor(bright, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=75,
                               param2=17,
                               minRadius=18)
    circles_bright = cv2.HoughCircles(gray_bright, cv2.HOUGH_GRADIENT, 1, 20,
                                      param1=75,
                                      param2=17,
                                      minRadius=18)
    if circles is None and circles_bright is None:
        return False

    return True
