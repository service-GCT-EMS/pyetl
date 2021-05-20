# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 13:22:59 2019

@author: 89965
"""
import os
from collections import namedtuple
import importlib


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


printtime = False
if printtime:
    import time


def loadmodule(module):
    if printtime:
        t2 = time.time()
    try:
        format_def = importlib.import_module(module, package=__package__)
        for nom, desc in getattr(format_def, "WRITERS").items():
            if nom in WRITERS and not isinstance(WRITERS[nom], str):
                print("attention : redefinition du format de sortie", nom, module)
            WRITERS[nom] = wdef(*desc, None, None, module)
            # a ce stade les fonctions ne sont pas connues
        for nom, desc in getattr(format_def, "READERS").items():
            # print("definition du format d'entree", nom, desc)
            if nom in READERS and not isinstance(READERS[nom], str):
                print("attention : redefinition du format d'entree", nom, module)
            READERS[nom] = rdef(*desc, None, module)
            # print ('lecture  READERS',nom,desc,'->', readers[nom])
    except (ImportError, AttributeError) as err:
        print("module ", module[1:], "non disponible", err)
    if printtime:
        print("     ", module, time.time() - t2)


def loadformats(module=None):
    """lit toutes les descriptions de format depuis le repertoire courant
    et enregistre les readers et writers"""
    global READERS, WRITERS

    formatdir = os.path.dirname(__file__)
    if module is None:
        cr = os.path.join(formatdir, "cache_readers.csv")
        cw = os.path.join(formatdir, "cache_writers.csv")
        if os.path.isfile(cr):
            READERS = dict((i[:-1].split(";") for i in open(cr, "r")))
            WRITERS = dict((i[:-1].split(";") for i in open(cw, "r")))
            return
        else:
            for fich_module in os.listdir(formatdir):
                if fich_module.startswith("format_"):
                    module = "." + os.path.splitext(fich_module)[0]
                    loadmodule(module)
    else:
        loadmodule(module)


READERS = dict()
WRITERS = dict()
loadformats()
# print ('chargement', READERS)
