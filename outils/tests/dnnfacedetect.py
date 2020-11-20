# USAGE
# python detect_faces.py --image rooster.jpg --prototxt deploy.prototxt.txt --model res10_300x300_ssd_iter_140000.caffemodel

# import the necessary packages
import numpy as np
import argparse
import os
import cv2


class CnnDetector(object):
    "conteneur de detection"

    def __init__(self, rep, conf, values):
        self.modelsize = (300, 300)
        self.confmini = 0.5
        self.modeldir = rep
        net = self.netload(rep, conf, values)

    def netload(rep, conf, values):
        "charge un reseau "

        rep = "parametres/facedetection/"
        self.net = cv2.dnn.readNetFromCaffe(
            rep + "deploy.prototxt.txt",
            rep + "res10_300x300_ssd_iter_140000.caffemodel",
        )

    def detect(self, imagette):
        blob = cv2.dnn.blobFromImage(
            cv2.resize(imagette, self.modelsize),
            1.0,
            self.modelsize,
            (104.0, 177.0, 123.0),
        )

        # pass the blob through the network and obtain the detections and
        # predictions
        # print("[INFO] computing object detections...")
        self.net.setInput(blob)
        detections = self.net.forward()

        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]
            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence

            if confidence < self.confmini:
                continue
                # compute the (x, y)-coordinates of the bounding box for the
                # object
            box = detections[0, 0, i, 3:7] * np.array(
                [grille_w, grille_h, grille_w, grille_h]
            )
            (startX, startY, endX, endY) = box.astype("int")
            startX += iter_w + dec
            endX += iter_w + dec
            startY += iter_h + dec
            endY += iter_h + dec

        return detections


def detect(net, imagette):
    blob = cv2.dnn.blobFromImage(
        cv2.resize(imagette, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
    )

    # pass the blob through the network and obtain the detections and
    # predictions
    # print("[INFO] computing object detections...")
    net.setInput(blob)
    detections = net.forward()
    return detections


def controle(image, detections, iter_w, iter_h, grille_w, grille_h, dec):
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]
        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence

        if confidence < confmini:
            continue
            # compute the (x, y)-coordinates of the bounding box for the
            # object
        box = detections[0, 0, i, 3:7] * np.array(
            [grille_w, grille_h, grille_w, grille_h]
        )
        (startX, startY, endX, endY) = box.astype("int")
        startX += iter_w + dec
        endX += iter_w + dec
        startY += iter_h + dec
        endY += iter_h + dec
        cX = abs(int(startX - endX) / 2)
        cY = abs(int(startY - endY) / 2)
        xmin = cX - 150 if (cX - 150) > 0 else 0
        ymin = cY - 150 if (cY - 150) > 0 else 0

        imagette = image[ymin : ymin + 300, xmin : xmin + 300]
        detect(net, imagette)


def marque(image, detections, iter_w, iter_h, grille_w, grille_h, dec):

    ctex = (0, 0, 255) if dec == 0 else (0, 255, 0)

    # cv2.rectangle(
    #     image, (iter_w, iter_h), (iter_w + grille_w, iter_h + grille_h), ctex, 2
    # )

    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]
        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence

        if confidence < confmini:
            continue
            # compute the (x, y)-coordinates of the bounding box for the
            # object
        box = detections[0, 0, i, 3:7] * np.array(
            [grille_w, grille_h, grille_w, grille_h]
        )
        (startX, startY, endX, endY) = box.astype("int")
        startX += iter_w + dec
        endX += iter_w + dec
        startY += iter_h + dec
        endY += iter_h + dec
        # draw the bounding box of the face along with the associated
        # probability
        text = "{:.2f}%".format(confidence * 100)
        if dec == 0:
            y = startY - 10 if startY - 10 > 10 else startY + 10
        else:
            y = endY - 10 if endY - 10 > 10 else endY + 10

        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        cv2.putText(image, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, ctex, 2)


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="path to input image")

ap.add_argument(
    "-c",
    "--confidence",
    type=float,
    default=0.5,
    help="minimum probability to filter weak detections",
)
args = vars(ap.parse_args())

# load our serialized model from disk
print("[INFO] loading model...")
# net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
modeldir = "parametres/facedetection/"
net = cv2.dnn.readNetFromCaffe(
    modeldir + "deploy.prototxt.txt",
    modeldir + "res10_300x300_ssd_iter_140000.caffemodel",
)
# load the input image and construct an input blob for the image
# by resizing to a fixed 300x300 pixels and then normalizing it
name, ext = os.path.splitext(args["image"])
image = cv2.imread(args["image"])
image2 = image.copy()
(h, w) = image.shape[:2]
n_h = int(h / 300) or 1
n_w = int(w / 300) or 1
grille_h = int(h / n_h)
grille_w = int(w / n_w)
print("decoupage en %d,%d morceaux de %d %d" % (n_h, n_w, grille_h, grille_w))
confmini = args["confidence"]
for d2 in range(2):
    dec = int(d2 * grille_w / 2)
    print("decalage", dec)
    for iter_h in range(dec, h, grille_h):
        for iter_w in range(dec, w, grille_w):
            imagette = image[iter_h : iter_h + grille_h, iter_w : iter_w + grille_w]
            detections = detect(net, imagette)
            # print("nombre de detections", detections.shape[2])
            # loop over the detections
            marque(image2, detections, iter_w, iter_h, grille_w, grille_h, dec)

# show the output image
# cv2.imshow("Output", image)
cv2.imwrite(name + "F2" + ext, image2)
# cv2.waitKey(0)
