# -*- coding: utf-8 -*-
# formats d'entree sortie
"""gestion des formats d'entree et de sortie.
"""


import os


def importer():
    global DBF
    from dbfread import DBF


def decode_entetes_dbf(reader, noms_attributs):
    """prepare l'entete et les noma d'un fichier csv"""
    if reader.newschema:
        for i in noms_attributs:
            reader.schemaclasse.stocke_attribut(i, "T")
    return noms_attributs


def lire_objets_dbf(self, rep, chemin, fichier):
    """lit des objets a partir d'un fichier csv"""
    importer()
    self.prepare_lecture_fichier(rep, chemin, fichier)
    # nom_schema, nom_groupe, nom_classe = getnoms(rep, chemin, fichier)
    try:
        with DBF(os.path.join(rep, chemin, fichier)) as fich:
            noms_attributs = decode_entetes_dbf(self, fich.field_names)
            self.prepare_attlist(noms_attributs)

            for record in fich.records:

                self.alphaprocess(record)

    except UnicodeError:
        print("erreur encodage le fichier", fichier, "n'est pas en ", self.encoding)
    return


#                  reader,geom,hasschema,auxfiles,initer
READERS = {"dbf": (lire_objets_dbf, None, True, ("!", "shp"), None, None)}
# READERS={}
WRITERS = {}
