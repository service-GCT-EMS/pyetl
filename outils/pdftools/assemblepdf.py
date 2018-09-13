import sys
import os

from pdfrw import PdfReader, PdfWriter


def getparam(clef, defaut=None):
    if clef in sys.argv:
        pos = sys.argv.index('-'+clef) +1
        valeur = sys.argv[pos]
        return valeur
    return defaut

def getreste():
    p=0
    liste =[]
    for i in sys.argv[1:]:
        if p:
            p=0
            continue
        if '-' in i:
            p=1
            continue
        liste.append(i)
    return liste


if len(sys.argv)<2:
    print ("usage assemblepdf [-o sortie] [rep]|[fichier fichier...]")

sortie = getparam('o', 'assemble.pdf')

liste = getreste()
liste2=[]
for i in liste:
    if os.path.isdir(i):
        docs = sys.argv[1]
        listefich = sorted(list(os.listdir(i)))
        liste2.extend([os.path.join(i,j) for j in listefich if j.endswith('.pdf')])
    else:
        liste2.append(i)

pages = []
for i in liste2:
    print (i)
    pages.extend(PdfReader(i).pages)

writer = PdfWriter()
for i in pages:
    writer.addpage(i)

writer.write(sortie)