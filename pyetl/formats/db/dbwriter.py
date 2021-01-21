# -*- coding: utf-8 -*-
"""
#titre||accés aux bases de données en ecriture
fonctions de manipulation d'attributs
"""
import os
import logging
import glob

# from itertools import zip_longest
# import pyetl.formats.mdbaccess as DB


class DbWriter(object):
    """ ressource d'ecriture en base de donnees"""

    def __init__(self, nom, liste_att=None, encoding="utf-8", regle=None, connect=None):

        self.nom = nom
        self.regle = regle
        self.liste_att = liste_att
        self.fichier = None
        self.encoding = encoding
        self.schema_base = None
        self.connect = connect
        if connect is not None:
            self.schema_base = connect.schemabase
        self.buffer = []
        self.bufsize = 1000

    def dbtable(self, idtable):
        """ selectionne une table """
        schematable = self.schema_base.get_classe(idtable)
        return schematable

    def open(self, idtable):
        """ teste l existance de la table et la cree si necessaire"""
        if self.dbtable(idtable):
            self.connect.lock(idtable)

    def reopen(self, _):
        """ reouverture d'une table ferme (non utilise)"""
        return

    def close(self, _):
        """fermeture d'une table (non utilise)"""
        return

    def finalise(self, _):
        """fermeture definitive d'un fichier (non utilise)"""
        return

    def set_liste_att(self, liste_att):
        """positionne la liste d'attributs"""
        self.liste_att = liste_att

    def prepare(self, obj):
        ligne = self.fonction(self, obj)
        return ligne

    def exp_attributs(liste_att):
        """genere la liste des attributs pouur l update ou l insert"""
        return "(" + ",".join(liste_att) + ")"

    def exp_value(obj, liste_att):
        """genere la liste des valeurs pour l update ou l insert"""

    def req_update_obj(self, obj):
        """gere un update sur la base de donnees"""
        ident = obj.ident

        if ident not in self.schemabase.classes:
            return False

        attributs = self.regle.attributs

        tablekey = self.schemabase.classes[ident].getpkey
        requete = (
            " UPDATE "
            + self.quote_table(ident)
            + " SET "
            + attributs
            + " = "
            + valeur
            + " WHERE "
            + tablekey
            + "="
            + clef
        )

        #        print ('parametres',data,valeur)
        data = valeur
        if not attribut:
            requete = ""
            data = ()

        return self.request(requete, data)

    def write(self, obj):
        """ecrit un objet complet"""
        if len(self.buffer) < self.buffsize:
            self.buffer.append(self.prepare(obj))
        else:
            self.connect.execute("\n".join(self.buffer))
        return True


def dbload(regle, base, selecteur, obj):
    pass


def dbupdate(regle, base, niveau, classe, attributs, obj):
    attlist = obj
    requete = "UPDATE " + q
    pass


def ecrire_objets_db(regle, _, attributs=None, rep_sortie=None):
    """ecrit un ensemble d'objets en base"""
    # ng, nf = 0, 0
    # memoire = defs.stockage
    sorties = regle.stock_param.sorties
    rep_sortie = regle.getvar("_sortie") if rep_sortie is None else rep_sortie
    dident = None
    ressource = None
    for groupe in list(regle.stockage.keys()):
        nb_obj = 0
        for obj in regle.recupobjets(groupe):  # on parcourt les objets
            if obj.virtuel:  # on ne traite pas les virtuels
                continue
            if obj.ident != dident:
                if ressource:
                    ressource.compte(nb_obj)
                    nb_obj = 0
                groupe, classe = obj.ident
                print("dbw : regle.fanout", regle.fanout)

                if regle.fanout == "no":
                    nom = sorties.get_id(rep_sortie, "all", "", ".sql")
                elif regle.fanout == "groupe":
                    nom = sorties.get_id(rep_sortie, groupe, "", ".sql")
                else:
                    nom = sorties.get_id(rep_sortie, classe, "", ".sql")

                ressource = sorties.get_res(regle, nom)
                if ressource is None:
                    os.makedirs(os.path.dirname(nom), exist_ok=True)
                    #                    liste_att = _set_liste_attributs(obj, attributs)
                    liste_att = obj.schema.get_liste_attributs(liste=attributs)
                    dbwr = DbWriter(
                        nom, liste_att, encoding=regle.getvar("codec_sortie", "utf-8")
                    )
                    sorties.creres(regle, nom, dbwr)
                    ressource = sorties.get_res(regle, nom)
                else:
                    #                    liste_att = _set_liste_attributs(obj, attributs)
                    liste_att = obj.schema.get_liste_attributs(liste=attributs)
                    dbwr = ressource.handler
                    dbwr.set_liste_att(liste_att)
                dident = (groupe, classe)
            dbwr.write(obj)
            nb_obj += 1


def db_streamer(obj, regle, _, attributs=None, rep_sortie=None):
    """ecrit des objets sql au fil de l'eau.
    dans ce cas les objets ne sont pas stockes,  l'ecriture est effetuee
    a la sortie du pipeline (mode streaming) on groupe quand meme pour les perfs
    """
    if obj.virtuel:
        return
    rep_sortie = regle.getvar("_sortie") if rep_sortie is None else rep_sortie
    sorties = regle.stock_param.sorties
    if obj.ident != regle.dident:
        if obj.virtuel:  # on ne traite pas les virtuels
            return
        dest = obj.ident
        ressource = sorties.get_res(regle, dest)
        if ressource is None:
            liste_att = obj.schema.get_liste_attributs(liste=attributs)
            #            liste_att = _set_liste_attributs(obj, attributs)
            swr = DbWriter(
                dest,
                liste_att,
                encoding=regle.getvar("codec_sortie", "utf-8"),
                regle=regle,
            )
            sorties.creres(regle, dest, swr)
            ressource = sorties.get_res(regle, dest)
            regle.dident = dest
            regle.ressource = ressource
        else:
            if dest != regle.dident:
                #                liste_att = _set_liste_attributs(obj, attributs)
                liste_att = obj.schema.get_liste_attributs(liste=attributs)
                ressource.handler.set_liste_att(liste_att)
                regle.dident = dest
                regle.ressource = ressource
    regle.ressource.write(obj)
