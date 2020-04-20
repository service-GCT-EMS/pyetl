# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 17:37:44 2016

@author: 89965
description des formats de base de donnees connus
"""
import os
from collections import namedtuple
import importlib

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
    ),
)
# ("acces", "gensql", "svtyp", "fileext", 'description')
def loadmodules():
    """lit toutes les descriptions de format depuis le repertoire courant
    et enregistre les readers et writers"""
    databases = dict()

    for fich_module in os.listdir(os.path.dirname(__file__)):
        if fich_module.startswith("base_"):
            module = "." + os.path.splitext(fich_module)[0]
            try:
                format_def = importlib.import_module(module, package=__package__)
                for nom, desc in getattr(format_def, "DBDEF").items():
                    if nom in databases:
                        print("attention : redefinition du format de base", nom)
                    databases[nom] = DBDEF(*desc, None, None)
                    # a ce stade les fonctions ne sont pas connues
            except (ImportError, AttributeError) as err:
                print("module ", module[1:], "non disponible", err)

    return databases


DATABASES = loadmodules()
if "postgis" in DATABASES:
    DATABASES["sql"] = DATABASES["postgis"]  # generique
