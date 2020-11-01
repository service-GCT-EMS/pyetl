# -*- coding: utf-8 -*-

"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
import logging

DEBUG = False
LOGGER = logging.getLogger(__name__)
TYPES_A = {i: i for i in "TFHGDNSIEB0123"}
TYPES_A.update({i: i for i in ("DS", "EL", "-1")})
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


# def quote(att):
#     """rajoute les quotes sur une liste de valeurs ou une valeur"""
#     if att.startswith('"'):
#         return att
#     return '"%s"' % (att)


# def attqjoiner(attlist, sep):
#     """ join une liste d'attributs et ajoute les quotes"""
#     if isinstance(attlist, (list, tuple)):
#         return sep.join([quote(i) for i in attlist])
#     return quote(attlist)
