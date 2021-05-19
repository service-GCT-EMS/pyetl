# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 13:22:59 2019

@author: 89965
"""
import os
from collections import namedtuple
import importlib

printtime = True
if printtime:
    import time

    t1 = time.time()


def loadmodules():
    """lit toutes les descriptions de format depuis le repertoire courant
    et enregistre les readers et writers"""
    if printtime:
        t2 = t1
    writers = dict()
    readers = dict()
    rdef = namedtuple(
        "readerdef",
        (
            "reader",
            "geom",
            "has_schema",
            "auxfiles",
            "initer",
            "objreader",
            "converter",
            "module",
        ),
    )
    wdef = namedtuple(
        "writerdef",
        (
            "writer",
            "streamer",
            "force_schema",
            "casse",
            "attlen",
            "driver",
            "fanoutmin",
            "geom",
            "tmp_geom",
            "initer",
            "geomwriter",
            "tmpgeomwriter",
            "module",
        ),
    )

    for fich_module in os.listdir(os.path.dirname(__file__)):
        if fich_module.startswith("format_"):
            module = "." + os.path.splitext(fich_module)[0]
            try:
                format_def = importlib.import_module(module, package=__package__)
                for nom, desc in getattr(format_def, "WRITERS").items():
                    if nom in writers:
                        print("attention : redefinition du format de sortie", nom)
                    writers[nom] = wdef(*desc, None, None, module)
                    # a ce stade les fonctions ne sont pas connues
                for nom, desc in getattr(format_def, "READERS").items():
                    # print("definition du format d'entree", nom, desc)
                    if nom in readers:
                        print("attention : redefinition du format d'entree", nom)
                    readers[nom] = rdef(*desc, None, module)
                    # print ('lecture  READERS',nom,desc,'->', readers[nom])
            except (ImportError, AttributeError) as err:
                print("module ", module[1:], "non disponible", err)
            if printtime:
                print("     ", module, time.time() - t2)
                t2 = time.time()
    return readers, writers


READERS, WRITERS = loadmodules()
# print ('chargement', READERS)
