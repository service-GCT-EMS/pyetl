import sys
import os

from pdfrw import PdfReader, PdfWriter

recto,verso,= sys.argv[1:]
pages_recto = PdfReader(recto).pages
pages_verso = reversed(PdfReader(verso).pages)
out = 'assemble.' + os.path.basename(recto)
writer = PdfWriter()
for i,j in zip(PdfReader(recto).pages,reversed(PdfReader(verso).pages)):
    writer.addpage(i)
    # j.Rotate=180
    writer.addpage(j)
writer.write(out)