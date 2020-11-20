# test recup plaques

import cv2
import numpy as np

# Read image
img = cv2.imread("entree/images/0000000169.jpg", 1)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print("passage gris", type(img), type(gray))
# cv2.waitKey(0)

# read haarcascade
# plates_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml') #does not give me error, but result is not correct
plates_cascade = cv2.CascadeClassifier(
    "haarcascade_licence_plate_rus_16stages.xml"
)  # gives me error

# plates = plates_cascade.detectMultiScale(gray, 1.2, 4)
plates = plates_cascade.detectMultiScale(
    gray,
    scaleFactor=1.3,
    minNeighbors=4,
    minSize=(30, 30),
    flags=cv2.CASCADE_SCALE_IMAGE,
)


for (x, y, w, h) in plates:

    # detect plate with rectangle
    # rec. start point (x,y), rec. end point (x+w, y+h), blue color(255,0,0), line width 1

    plates_rec = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
    # cv2.putText(plates_rec, 'Text', (x, y-3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

    gray_plates = gray[y : y + h, x : x + w]
    color_plates = img[y : y + h, x : x + w]

    # cv2.imshow('img', gray_plates)
    # cv2.waitKey(0)

    height, width, chanel = gray_plates.shape
    print(height, width)

    # cv2.imshow("img", color_plates)
    cv2.waitKey(0)
print("Number of detected licence plates:", len(plates))
