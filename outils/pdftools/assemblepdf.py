import sys
import os

from pdfrw import PdfReader, PdfWriter
from PIL import Image


def getparam(clef, defaut=None):
    if "-" + clef in sys.argv:
        pos = sys.argv.index("-" + clef) + 1
        valeur = sys.argv[pos]
        return valeur
    return defaut


def getreste():
    p = 0
    liste = []
    for i in sys.argv[1:]:
        if p:
            p = 0
            continue
        if "-" in i:
            p = 1
            continue
        liste.append(i)
    return liste


if len(sys.argv) < 2:
    print("usage assemblepdf [-o sortie] [rep]|[fichier fichier...]")

sortie = getparam("o", "assemble.pdf")

liste = getreste()
liste2 = []
for i in liste:
    if os.path.isdir(i):
        docs = sys.argv[1]
        listefich = sorted(list(os.listdir(i)))
        liste2.extend([os.path.join(i, j) for j in listefich if j.endswith(".pdf")])
    else:
        liste2.append(i)

pages = []
for i in liste2:
    print(i)
    if i.endswith(".png") or i.endswith(".tif") or i.endswith(".jpg"):
        nom_image = os.path.splitext(i)[0]
        im = Image.open(i)
        im = im.convert("RGB")
        im.save(nom_image + ".pdf", resolution=300)
        pages.extend(PdfReader(nom_image + ".pdf").pages)
    else:
        pages.extend(PdfReader(i).pages)

writer = PdfWriter()
for i in pages:
    writer.addpage(i)

writer.write(sortie)
