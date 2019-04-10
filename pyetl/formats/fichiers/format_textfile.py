# -*- coding: utf-8 -*-
""" format texte en lecture et ecriture"""

# import time
# import pyetl.schema as SC
#import sys
import os
import codecs
from . import fileio



class TextWriter(fileio.FileWriter):
    """writer de fichiers texte"""

    def write(self, obj):
        """ecrit un objet complet"""
        chaine = obj.attributs["contenu"]
        self.fichier.write(chaine)
        if chaine[-1] != "\n":
            self.fichier.write("\n")
        # self.stats[self.nom] += 1
        return True


def lire_textfile_ligne(self, rep, chemin, fichier):
    """ lecture d'un fichier et stockage des objets en memoire de l'ensemble du texte en memmoire"""
    self.prepare_lecture_fichier(rep, chemin, fichier)
    with open(self.fichier, "r", 65536, encoding=self.encoding, errors="backslashreplace",) as ouvert:
        for ligne in ouvert:
            obj = self.getobj()
            if obj is None: # gere le maxval
                return self.nb_lus
            obj.attributs["contenu"] = ligne
            self.process(obj)  # on traite l'objet precedent
    return self.nb_lus


def lire_textfile_bloc(self, rep, chemin, fichier):
    """ lecture d'un fichier et stockage des objets en memoire de l'ensemble du texte en memmoire"""
    self.prepare_lecture_fichier(rep, chemin, fichier)
    with open(self.fichier, "r", encoding=self.encoding, errors="backslashreplace",) as ouvert:
        contenu = "".join(ouvert.readlines())
        obj = self.getobj()
        obj.attributs["contenu"] = contenu
        self.process(obj)  # on traite l'objet precedent
    return self.nb_lus



def ecrire_objets_text(regle, _, attributs=None):
    """ecrit un fichier dont le contenu est dans un attribut
    a partir d'un stockage memoire ou temporaire"""
    # ng, nf = 0, 0
    # memoire = defs.stockage
    #    print( "ecrire_objets asc")
    rep_sortie = regle.getvar("_sortie")
    sorties = regle.stock_param.sorties
    numero = regle.numero
    dident = None
    ressource = None
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):  # on parcourt les objets
            if obj.virtuel:  # on ne traite pas les virtuels
                continue
            if obj.ident != dident:
                groupe, classe = obj.ident
                if regle.fanout == "groupe":
                    nom = sorties.get_id(rep_sortie, groupe, "", regle.ext)
                else:
                    nom = sorties.get_id(rep_sortie, groupe, classe, regle.ext)

                ressource = sorties.get_res(numero, nom)
                if ressource is None:
                    if os.path.dirname(nom):
                        os.makedirs(os.path.dirname(nom), exist_ok=True)

                    streamwriter = TextWriter(
                        nom,
                        encoding=regle.stock_param.get_param("codec_sortie", "utf-8"),
                    )
                    streamwriter.set_liste_att(attributs)
                    ressource = sorties.creres(numero, nom, streamwriter)
                regle.ressource = ressource
                dident = (groupe, classe)
            ressource.write(obj, regle.numero)


READERS = {"ligne": (lire_textfile_ligne, "", False, ())}
READERS = {"text": (lire_textfile_bloc, "", False, ())}
# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {"text": (ecrire_objets_text, None, False, "", 0, "", "classe", "", "")}
