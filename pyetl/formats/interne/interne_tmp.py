# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 14:08:15 2018

@author: 89965
stockage interne pour des operations de comparaisons
"""
from collections import namedtuple


class ObjStore(object):
    """structure de stockage d'objets en memoire"""

    def __init__(self, nom, schema, clef):
        self.nom = nom
        self.schema = schema
        self.data = dict()
        self.strlist = schema.liste_attributs()
        struct = ["n_" + i for i in self.strlist]  # pour avoir des noms valides
        struct.append("geometrie")
        self.structure = namedtuple(nom, struct)
        self.key = clef
        self.nbval = 0

    def write(self, obj):
        """ stocke un objet """
        clef = obj.attributs.get(self.key)
        if clef in self.data:
            print("interne:clef duppliqueee", self.nom, self.key, clef)
            return False
        liste = [obj.attributs[i] for i in self.strlist]
        liste.append(obj.geom_v)
        tmp = self.structure(liste)
        self.data[clef] = tmp
        self.nbval += 1
        return True

    def get(self, clef):
        """recuper un objet"""
        return self.data.get(clef)


def intstreamer(obj, regle):  # ecritures non bufferisees
    """ ecrit des objets csv en streaming"""
    store = regle.stock_param.store

    if obj.ident != regle.dident:
        groupe, classe = obj.ident
        #        if obj.schema:
        schema_courant = obj.schema
        nom = ".".join(obj.ident)

        ressource = store.get(nom)
        if ressource is None:
            ressource = ObjStore(nom, schema_courant, regle.params.cmp2.val)
            store[nom] = ressource

        regle.ressource = ressource
        regle.dident = (groupe, classe)
    else:
        schema_courant = obj.schema
    ressource = regle.ressource
    ressource.write(obj)


def ecrire_objets_int(regle, _):
    """ ecrit des objets csv a partir du stockage interne"""
    nb_obj, nb_fich = 0, 0
    dident = None
    store = regle.stock_param.store
    #    print("csv:ecrire csv", regle.stockage.keys())
    ressource = None
    for groupe in list(regle.stockage.keys()):
        # on determine le schema
        nom = ""
        for obj in regle.recupobjets(groupe):
            groupe, classe = obj.ident
            if obj.ident != dident:
                schema_courant = obj.schema
                nom = ".".join(obj.ident)
                ressource = store.get(nom)
                if ressource is None:
                    nb_fich += 1
                    ressource = ObjStore(nom, schema_courant, regle.params.cmp2.val)
                    store[nom] = ressource
                dident = (groupe, classe)
            retour = ressource.write(obj)
            if retour:
                nb_obj += 1
    return nb_obj, nb_fich
