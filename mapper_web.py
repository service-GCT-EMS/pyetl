# -*- coding: utf-8 -*-
"""modification d'attributs en fonction d'un fichier de parametrage avec
prise en charge des expressions regulieres"""
import time

STARTTIME = time.time()
import sys

from pyetl_webapp import app

# print ('mapper: fin import modules',int(time.time()-t1))
# import cProfile as profile
# ---------------debut programme ---------------
# lancement flask run mapper_web

if __name__ == "__main__":
    # execute only if run as a script
    args = dict((i.split("=",1) for i in sys.argv if '=' in i))
    port = int(args.get("port",3000))
    app.run(port=port)
