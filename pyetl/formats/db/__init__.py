# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 17:37:44 2016

@author: 89965
description des formats de base de donnees connus
"""
import os
from collections import namedtuple
import importlib

printtime = False
if printtime:
    import time


DBDEF = namedtuple(
    "database",
    (
        "acces",
        "gensql",
        "svtyp",
        "fileext",
        "geom",
        "description",
        "converter",
        "geomwriter",
        "doc",
        "module",
    ),
)
# ("acces", "gensql", "svtyp", "fileext", 'description')


def loaddb(module):
    """charge un module"""
    if printtime:
        t2 = time.time()
    try:
        # print("chargement db --------------------", module)
        format_def = importlib.import_module(module, package=__package__)
        doc = format_def.__doc__
        for nom, desc in getattr(format_def, "DBDEF").items():
            if nom in DATABASES and not isinstance(DATABASES[nom], str):
                print("attention : redefinition du format de base", nom)
            DATABASES[nom] = DBDEF(*desc, None, None, doc, module)
            # print("chargement db --------------", nom)
            # a ce stade les fonctions ne sont pas connues
    except (ImportError, AttributeError) as err:
        print("module ", module[1:], "non disponible", err)
    if printtime:
        print("     ", module, time.time() - t2)
        t2 = time.time()


def loaddbmodules(module=None, force=False):
    """lit toutes les descriptions de format depuis le repertoire courant
    et enregistre les readers et writers"""
    global DATABASES
    formatdir = os.path.dirname(__file__)
    if module is None:
        cr = os.path.join(formatdir, "cache_databases.csv")
        if os.path.isfile(cr) and not force:
            DATABASES = dict((i[:-1].split(";") for i in open(cr, "r")))
        else:
            for fich_module in os.listdir(formatdir):
                if fich_module.startswith("base_"):
                    module = "." + os.path.splitext(fich_module)[0]
                    loaddb(module)
    else:
        loaddb(module)
    if "postgis" in DATABASES:
        DATABASES["sql"] = DATABASES["postgis"]
    return


DATABASES = dict()
loaddbmodules()
# generique
