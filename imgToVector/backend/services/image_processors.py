import cv2

def preprocess_image(path):

    img = cv2.imread(
        path,
        cv2.IMREAD_GRAYSCALE
    )

    if img.mean() < 127:
        img = cv2.bitwise_not(img)

    _, binary = cv2.threshold(
        img,
        0,
        255,
        cv2.THRESH_BINARY +
        cv2.THRESH_OTSU
    )

    return binary