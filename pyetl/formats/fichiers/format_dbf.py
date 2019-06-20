# -*- coding: utf-8 -*-
# formats d'entree sortie
"""gestion des formats d'entree et de sortie.
"""


import os
import codecs
from dbfread import DBF
# from numba import jit

def decode_entetes_dbf(reader,fich):
    """prepare l'entete et les noma d'un fichier csv"""

    noms_attributs = list(fich.field_names)
    if reader.newschema:
        for i in noms_attributs:
            if i[0] != "#":
                reader.schemaclasse.stocke_attribut(i, "T")
    return noms_attributs



def lire_objets_dbf(reader, rep, chemin, fichier):
    """lit des objets a partir d'un fichier csv"""
    reader.prepare_lecture_fichier(rep,chemin,fichier)
    # nom_schema, nom_groupe, nom_classe = getnoms(rep, chemin, fichier)
    try:
        with open(os.path.join(rep, chemin, fichier), "r", encoding=reader.encoding) as fich:
            noms_attributs= decode_entetes_dbf(reader,fich)
            reader.prepare_attlist(noms_attributs)
            for record in fich:

                valeurs = [str(j) for j in record]

                obj = reader.getobj(valeurs=valeurs)
                obj.attributs["#type_geom"] = 0
                obj.attributs["#chemin"] = chemin
                reader.process(obj)

    except UnicodeError:
        print("erreur encodage le fichier", fichier, "n'est pas en ", reader.encoding)
    return

#                  reader,geom,hasschema,auxfiles
READERS = {"dbf": (lire_objets_dbf, None, True, (), None)}
