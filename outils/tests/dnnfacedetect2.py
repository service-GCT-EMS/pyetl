# USAGE
# python detect_faces.py --image rooster.jpg --prototxt deploy.prototxt.txt --model res10_300x300_ssd_iter_140000.caffemodel

# import the necessary packages
import numpy as np
import argparse
import os
import cv2
import time


class CnnDetector(object):
    "conteneur de detection"

    def __init__(self, rep, conf, values):
        self.modelsize = (2000, 2000)
        self.controlsize = (300, 300)
        self.hm = self.modelsize[0]
        self.wm = self.modelsize[1]
        self.confmini = 0.5
        self.modeldir = rep
        self.netload(rep, conf, values)

    def netload(self, rep, conf, values):
        "charge un reseau "

        # rep = "parametres/facedetection/"
        self.net = cv2.dnn.readNetFromCaffe(rep + conf, rep + values)

    def loadimage(self, file):
        name, ext = os.path.splitext(file)
        self.imagefile = file
        self.image = cv2.imread(file)
        (h, w) = self.image.shape[:2]
        self.image_h = h
        self.image_w = w
        self.controlbox = []
        self.initbox = []
        self.detectbox = []

    def prepare_grille(
        self, decw=0, dech=0, hstart=0, hstop=0, wstart=0, wstop=0, resize=True
    ):
        fh = hstop - (hstart + dech)
        fw = wstop - (wstart + decw)
        n_h = int(fh / self.hm) or 1
        n_w = int(fw / self.wm) or 1
        print("preparation grille, (%d %d) -> %d ", (self.hm, self.wm, n_h * n_w))
        self.grille_h = int(fh / n_h) if resize else self.hm
        self.grille_w = int(fw / n_w) if resize else self.wm

    def saveimage(self, modif):
        name, ext = os.path.splitext(self.imagefile)
        cv2.imwrite(name + modif + ext, self.image)

    def detect(self, imagette, modelsize, resize=True):
        if resize:
            blob = cv2.dnn.blobFromImage(
                cv2.resize(imagette, modelsize), 1.0, modelsize, (104.0, 177.0, 123.0)
            )
        else:
            blob = cv2.dnn.blobFromImage(
                imagette, 1.0, modelsize, (104.0, 177.0, 123.0)
            )
        (h, w) = imagette.shape[:2]
        # pass the blob through the network and obtain the detections and
        # predictions
        self.net.setInput(blob)
        detections = self.net.forward()
        valided = []
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
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            valided.append((box, confidence))
        return valided

    def gridanalysor(self, ih, iw, resize=True):
        """retourne les elements controles d une imagette"""
        imagette = self.image[ih : ih + self.grille_h, iw : iw + self.grille_w]
        detections = self.detect(imagette, self.modelsize, resize)
        hm = int(self.controlsize[0])
        wm = int(self.controlsize[1])
        valides = []

        for box, confidence in detections:

            (startw, starth, endw, endh) = box.astype("int")
            cw = int((endw + startw) / 2) + iw
            ch = int((endh + starth) / 2) + ih
            coinw = int(cw - wm / 2)
            coinh = int(ch - hm / 2)  # coin superieur gauche du controle
            coinw = max(coinw, 0)
            coinw = min(coinw, self.image_w - wm)
            coinh = max(coinh, 0)
            coinh = min(coinh, self.image_h - hm)
            controlimage = self.image[coinh : coinh + hm, coinw : coinw + wm]
            print(
                "detecte", (startw + iw, starth + ih, endw + iw, endh + ih), confidence
            )
            self.detectbox.append(
                ((startw + iw, starth + ih, endw + iw, endh + ih), confidence)
            )
            self.controlbox.append(((coinw, coinh, coinw + wm, coinh + hm), confidence))
            d2 = self.detect(controlimage, self.controlsize, resize=False)
            for b2, c2 in d2:
                (startw, starth, endw, endh) = b2.astype("int")
                startw = startw + coinw
                endw = endw + coinw
                starth = starth + coinh
                endh = endh + coinh
                valides.append(((startw, starth, endw, endh), c2))
                print("valide", (startw, starth, endw, endh), c2)

        return valides

    def analyse_grille(
        self, decw=0, dech=0, hstart=0, hstop=0, wstart=0, wstop=0, resize=True
    ):
        " analyse une images selon une grille"
        hstop = hstop if hstop else self.image_h
        wstop = wstop if wstop else self.image_w
        print("decalage", decw, dech)
        detections = []
        self.prepare_grille(decw, dech, hstart, hstop, wstart, wstop, resize)
        for ih in range(dech + hstart, hstop, self.grille_h):
            for iw in range(decw + hstart, wstop, self.grille_w):
                detections.extend(self.gridanalysor(ih, iw, resize))
        return detections

    def analyse_image(self):
        d1 = self.analyse_grille(hstart=1500, hstop=3500, resize=False)
        d2 = self.analyse_grille(decw=1000, hstart=1500, hstop=3500, resize=False)
        d1.extend(d2)
        return d1

    def marque(self, detections, couleur):
        for rect, conf in detections:
            # extract the confidence (i.e., probability) associated with the
            # prediction
            # couleur = (0, 0, 255)
            (startX, startY, endX, endY) = rect
            # draw the bounding box of the face along with the associated
            # probability
            text = "{:.2f}%".format(conf * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10

            cv2.rectangle(self.image, (startX, startY), (endX, endY), couleur, 2)
            cv2.putText(
                self.image,
                text,
                (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                couleur,
                2,
            )


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=False, help="path to input image")
ap.add_argument("-d", "--dir", required=False, help="repertoire image")

ap.add_argument(
    "-c",
    "--confidence",
    type=float,
    default=0.5,
    help="minimum probability to filter weak detections",
)
args = vars(ap.parse_args())

cnn = CnnDetector(
    "parametres/facedetection/",
    "deploy.prototxt.txt",
    "res10_300x300_ssd_iter_140000.caffemodel",
)


def traite_image(nom):
    start = time.time()
    print("traitement", nom)
    cnn.loadimage(nom)
    detections = cnn.analyse_image()
    cnn.marque(detections, (0, 0, 255))
    # cnn.marque(cnn.controlbox, (0, 255, 0))
    # cnn.marque(cnn.detectbox, (255, 0, 0))
    cnn.saveimage("F2")
    print("duree traitement ", time.time() - start)


if args["image"]:
    traite_image(args["image"])
elif args["dir"]:
    for nom in os.listdir(args["dir"]):
        fich = args["dir"] + "/" + nom
        traite_image(fich)
