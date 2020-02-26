# -*- coding: utf-8 -*-

"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
import logging

DEBUG = False
LOGGER = logging.getLogger("pyetl")
TYPES_A = {i: i for i in "TFHGDNSIEB"}
TYPENUM = {
    "1": "POINT",
    "2": "LIGNE",
    "3": "POLYGONE",
    "-1": "GEOMETRIE",
    "0": "ALPHA",
    "indef": "ALPHA",
}

REMPLACE = dict(zip("-~èéà/", "__eea_"))
RESERVES = {"in": "ins", "as": "ass"}
GTYPES_DISC = {"alpha": "", "ALPHA": ""}
GTYPES_CURVE = {"alpha": "", "ALPHA": ""}
