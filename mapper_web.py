# -*- coding: utf-8 -*-
"""modification d'attributs en fonction d'un fichier de parametrage avec
prise en charge des expressions regulieres"""
import time

STARTTIME = time.time()
import sys
from pyetl.pyetl import runpyetl
from pyetl.vglobales import VERSION
from app import app

# print ('mapper: fin import modules',int(time.time()-t1))
# import cProfile as profile
# ---------------debut programme ---------------

if __name__ == "__main__":
    # execute only if run as a script
    app()
