# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 12:41:26 2019

@author: 89965
sorties fictives
"""
from collections import namedtuple
import os


def ecrire_objets_neant(self, regle, *_, **__):
    """pseudowriter ne fait rien :  poubelle"""
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):  # on parcourt les objets
            if not obj.virtuel:  # on ne traite pas les virtuels
                obj.setschema(None)
    return 0, 0


def stream_objets_neant(self, obj, *_, **__):
    """pseudowriter ne fait rien :  poubelle"""
    obj.setschema(None)
    return 0, 0


def compte_obj_stream(self, obj, regle, *_, **__):
    """poubelle avec comptage"""
    groupe, classe = obj.ident
    #    obj.setschema(None)
    sorties = regle.stock_param.sorties
    nom = "compt_" + groupe + "." + classe
    sorties.setcnt(nom, regle)
    return 0, 0


def compte_obj(self, regle, *_, **__):
    """poubelle avec comptage"""
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):  # on parcourt les objets
            if obj.virtuel:  # on ne traite pas les virtuels
                continue
            #            print ('comptage', regle)
            self.ecrire_objets_stream(obj, regle)
    return 0, 0


def affiche_header(obj):
    """affichage entete"""
    # raise
    print("!-final----affichage", obj.ident, "----------")
    print("!" + ",".join(obj.schema.get_liste_attributs()))


def prepare_webstore(obj, regle):
    """fabrique un namedtuple pour stocker les objets"""
    idstruc = "_".join(obj.ident)
    regle.storestruct = namedtuple(idstruc, obj.schema.get_liste_attributs())


def affiche_stream(self, obj, regle, *_, **__):
    """affichage"""
    stock_param = regle.stock_param
    # print("mode affichage", stock_param.mode)
    if stock_param.mode.startswith("web"):
        print("mode web", stock_param.mode)
        if obj.ident != regle.dident:
            prepare_webstore(obj, regle)
            regle.dident = obj.ident
        res = regle.storestruct(
            *(obj.get_valeur(i) for i in obj.schema.get_liste_attributs())
        )
        # on stocke
        ident = obj.ident if stock_param.mode == "web" else "#print"
        if ident in stock_param.webstore:
            stock_param.webstore[ident].append(res)
        else:
            stock_param.webstore[ident] = [res]
    else:
        if regle.istrue("#par_attribut"):
            print("")
            print(
                "\n".join(
                    (
                        "\t" + i + ":\t" + str(obj.attributs.get(i, ""))
                        for i in obj.schema.get_liste_attributs()
                    )
                )
            )
            return 0, 0
        if obj.ident != regle.dident:
            affiche_header(obj)
            regle.dident = obj.ident
        print(
            ",".join(
                (
                    str(obj.attributs.get(i, ""))
                    for i in obj.schema.get_liste_attributs()
                )
            )
        )
    return 0, 0


# ============================= interne pour comparaison ====================


class ObjStore(object):
    """structure de stockage d'objets en memoire"""

    def __init__(self, nom, schemaclasse, clef):
        self.nom = nom
        self.schemaclasse = schemaclasse
        self.data = dict()
        self.strlist = schemaclasse.get_liste_attributs()
        struct = self.strlist[:]
        self.fold = False
        struct.append("geometrie") if self.fold else struct.append("geom_v")
        print("stockage structure", nom, struct)
        self.structure = namedtuple(nom, struct)
        self.key = clef
        self.nbval = 0

    def write(self, obj):
        """stocke un objet"""
        clef = obj.attributs.get(self.key)
        if clef in self.data:
            print("interne:clef duppliqueee", self.nom, self.key, clef)
            return False
        liste = [obj.attributs[i] for i in self.strlist]
        if obj.initgeom():
            liste.append(obj.geom_v.fold if self.fold else obj.geom_v)
        else:
            liste.append("")
        tmp = self.structure(*liste)
        self.data[clef] = tmp
        self.nbval += 1
        return True

    def get(self, clef):
        """recuper un objet"""
        return self.data.get(clef)

    def __iter__(self):
        return self.data.__iter__

    def __len__(self):
        return len(self.data)

    def values(self):
        return self.data.values()


def intstreamer(self, obj, regle, *_, **__):  # ecritures non bufferisees
    """ecrit des objets tmp en streaming"""
    store = regle.stock_param.store

    if obj.ident != regle.dident:
        groupe, classe = obj.ident
        #        if obj.schema:
        schema_courant = obj.schema
        dest = regle.getvar("_sortie")
        nom = dest if dest else "_".join(obj.ident)

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


def ecrire_objets_int(self, regle, *_, **__):
    """ecrit des objets dans le stockage interne"""
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
                dest = regle.getvar("_sortie")
                nom = dest if dest else "_".join(obj.ident)
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


def filelist_to_obj(reader, rep, chemin, fichier, entete=None, separ=None):
    """lit des objets a partir d'un fichier csv"""
    reader.prepare_lecture_fichier(rep, chemin, fichier, classe="filelist")
    obj = reader.getobj()
    if obj is None:
        return  # filtrage entree
    obj.attributs["#type_geom"] = "0"
    obj.attributs["#nom_complet"] = os.path.join(rep, chemin, fichier)
    reader.process(obj)
    return


# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {
    "#poubelle": (
        ecrire_objets_neant,
        stream_objets_neant,
        False,
        "no",
        0,
        "",
        "all",
        None,
        None,
        None,
    ),
    "#comptage": (
        compte_obj,
        compte_obj_stream,
        False,
        "no",
        0,
        "",
        "all",
        None,
        None,
        None,
    ),
    "#print": (compte_obj, affiche_stream, True, "no", 0, "", "all", None, None, None),
    "#store": (
        ecrire_objets_int,
        intstreamer,
        False,
        "",
        0,
        "",
        "classe",
        "",
        "",
        None,
    ),
}
#                  reader,geom,hasschema,auxfiles
READERS = {
    "interne": (None, None, False, (), None, None),
    "interne+s": (None, None, True, (), None, None),
    "#dir": (filelist_to_obj, False, True, (), None, None),
}
