import sys
import os

from pdfrw import PdfReader, PdfWriter

docs = sys.argv[1]
pages = []

if os.path.isdir(sys.argv[1]):
    liste = sorted(list(os.listdir(docs)))
else:
    liste = sys.argv[1:]
for i in liste:
    print (i)
    document =  os.path.join(docs,i)
    pages.append(PdfReader(document).pages[0])

out = 'assemble.pdf'
writer = PdfWriter()
for i in pages:
    writer.addpage(i)

writer.write(out)