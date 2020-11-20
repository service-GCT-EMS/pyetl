import numpy as np
import cv2 as cv
import argparse
import os

# local modules


def detect(img, cascade):
    rects = cascade.detectMultiScale(
        img,
        scaleFactor=1.3,
        minNeighbors=4,
        minSize=(30, 30),
        flags=cv.CASCADE_SCALE_IMAGE,
    )
    if len(rects) == 0:
        return []
    rects[:, 2:] += rects[:, :2]
    return rects


def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv.rectangle(img, (x1, y1), (x2, y2), color, 2)


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image")
    args = vars(ap.parse_args())
    name, ext = os.path.splitext(args["image"])

    # args, video_src = getopt.getopt(sys.argv[1:], "", ["cascade=", "nested-cascade="])
    # try:
    #     video_src = video_src[0]
    # except:
    #     video_src = 0
    # args = dict(args)
    # cascade_fn = args.get(
    #     "--cascade", "data/haarcascades/haarcascade_frontalface_alt.xml"
    # )
    # nested_fn = args.get("--nested-cascade", "data/haarcascades/haarcascade_eye.xml")

    cascade = cv.CascadeClassifier(
        # cv.samples.findFile("haarcascades/haarcascade_frontalface_alt.xml")
        cv.samples.findFile("haarcascades/haarcascade_profileface.xml")
    )
    cascade2 = cv.CascadeClassifier(
        cv.samples.findFile("haarcascades/haarcascade_frontalface_alt.xml")
        # cv.samples.findFile("haarcascades/haarcascade_profileface.xml")
    )
    # nested = cv.CascadeClassifier(cv.samples.findFile(nested_fn))

    # cam = create_capture(
    #     video_src,
    #     fallback="synth:bg={}:noise=0.05".format(
    #         cv.samples.findFile("samples/data/lena.jpg")
    #     ),
    # )
    img = cv.imread(args["image"])
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.equalizeHist(gray)

    rects1 = detect(gray, cascade)
    rects2 = detect(gray, cascade2)
    vis = img.copy()
    draw_rects(vis, rects1, (0, 255, 0))
    draw_rects(vis, rects2, (255, 0, 0))
    # cv.imshow("facedetect", vis)
    # cv.imwrite("entree/images/0000000169F.jpg", vis)
    cv.imwrite(name + "F1" + ext, vis)
    print("detecte", len(rects1), len(rects2))


if __name__ == "__main__":
    print(__doc__)
    main()
    cv.destroyAllWindows()
