# -*- coding: utf-8 -*-
# formats d'entree sortie
"""gestion des formats d'entree et de sortie.
"""


import os
import codecs
from dbfread import DBF

# import dbf
# from numba import jit


def decode_entetes_dbf(reader, noms_attributs):
    """prepare l'entete et les noma d'un fichier csv"""
    if reader.newschema:
        for i in noms_attributs:
            reader.schemaclasse.stocke_attribut(i, "T")
    return noms_attributs


import time


def lire_objets_dbf(self, rep, chemin, fichier):
    """lit des objets a partir d'un fichier csv"""
    self.prepare_lecture_fichier(rep, chemin, fichier)
    # nom_schema, nom_groupe, nom_classe = getnoms(rep, chemin, fichier)
    try:
        with DBF(os.path.join(rep, chemin, fichier)) as fich:
            self.setidententree(self.groupe, self.classe)
            noms_attributs = decode_entetes_dbf(self, fich.field_names)
            self.prepare_attlist(noms_attributs)
            # n = 0
            # t0 = time.time()
            for record in fich.records:
                # n = n + 1
                # if n % 100000 == 0:
                #     print(n, time.time() - t0)
                # attributs = ((i,str(j)) for i,j in zip(noms_attributs,record))
                # print ("dbf: attributs", record)
                # print ("dbf: attributs", list(attributs))
                self.alphaprocess(record)
                # obj = self.getobj(attributs=record)
                # if obj:
                #     obj.attributs["#type_geom"] = '0'
                #     obj.attributs["#chemin"] = chemin
                #     self.process(obj)

    except UnicodeError:
        print("erreur encodage le fichier", fichier, "n'est pas en ", reader.encoding)
    return


#                  reader,geom,hasschema,auxfiles,initer
READERS = {"dbf": (lire_objets_dbf, None, True, (), None)}
# READERS={}
WRITERS = {}
