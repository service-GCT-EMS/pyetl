# -*- coding: utf-8 -*-
""" format texte en lecture et ecriture"""

# import time
# import pyetl.schema as SC
# import sys
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


def lire_textfile_ligne(reader, rep, chemin, fichier):
    """ lecture d'un fichier et creation d un objet par ligne"""
    reader.prepare_lecture_fichier(rep, chemin, fichier)
    nlin = 0
    if reader.newschema:
        reader.schemaclasse.stocke_attribut("contenu", "T")
        reader.prepare_attlist(["contenu"])
    with open(
        reader.fichier, "r", 65536, encoding=reader.encoding, errors="backslashreplace"
    ) as ouvert:
        for ligne in ouvert:
            attrs = {"contenu": ligne[:-1]}
            obj = reader.getobj(attrs)
            if obj is None:  # gere le maxval
                continue
            # obj.attributs["contenu"] = ligne[:-1]
            nlin += 1
            obj.attributs["#num_ligne"] = str(nlin)
            reader.process(obj)  # on traite l'objet precedent
    return reader.nb_lus


def lire_textfile_pos(reader, rep, chemin, fichier):
    """ lecture d'un fichier decodage positionnel"""
    reader.prepare_lecture_fichier(rep, chemin, fichier)
    nlin = 0
    positions = []
    debut = 0
    fin = 0
    if reader.newschema:
        champs = reader.regle_ref.getvar("champs")
        if champs:
            for champ in champs.split(","):
                nom, d, f = champ.split(":")
                d = int(d)
                f = int(f)
                fin = max(fin, f)
                positions.append(nom, d, f)
                reader.schemaclasse.stocke_attribut(nom, "T", taille=f - d)
        else:
            reader.regle_ref.stock_param.logger.warning(
                "pas de schema defini lecture impossible"
            )
            raise GeneratorExit
    else:
        for att in reader.schemaclasse.attributs:
            fin = debut + att.taille
            positions.append((att, debut, fin))
            debut = fin
    with open(
        reader.fichier, "r", 65536, encoding=reader.encoding, errors="backslashreplace"
    ) as ouvert:
        for ligne in ouvert:
            if len(ligne) < fin:
                ligne = ligne + " " * (fin - len(ligne))
            attrs = {i: ligne[d:f] for i, d, f in positions}
            obj = reader.getobj(attrs)
            if obj is None:  # gere le maxval
                continue
            # obj.attributs["contenu"] = ligne[:-1]
            nlin += 1
            obj.attributs["#num_ligne"] = str(nlin)
            reader.process(obj)  # on traite l'objet precedent
    return reader.nb_lus


def lire_textfile_bloc(reader, rep, chemin, fichier):
    """ lecture d'un fichier et stockage des objets en memoire de l'ensemble du texte en memmoire"""
    reader.prepare_lecture_fichier(rep, chemin, fichier)
    if reader.newschema:
        reader.schemaclasse.stocke_attribut("contenu", "T")
        reader.prepare_attlist(["contenu"])
    with open(
        reader.fichier, "r", encoding=reader.encoding, errors="backslashreplace"
    ) as ouvert:
        contenu = "".join(ouvert.readlines())
        attrs = {"contenu": contenu}
        obj = reader.getobj(attrs)
        # obj.attributs["contenu"] = contenu
        reader.process(obj)  # on traite l'objet precedent
    return reader.nb_lus


def ecrire_objets_text(regle, _, attributs=None):
    """ecrit un fichier dont le contenu est dans un attribut
    a partir d'un stockage memoire ou temporaire"""
    # ng, nf = 0, 0
    # memoire = defs.stockage
    #    print( "ecrire_objets asc")
    rep_sortie = regle.getvar("_sortie")
    sorties = regle.stock_param.sorties
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

                ressource = sorties.get_res(regle, nom)
                if ressource is None:
                    if os.path.dirname(nom):
                        os.makedirs(os.path.dirname(nom), exist_ok=True)

                    streamwriter = TextWriter(
                        nom, encoding=regle.getvar("codec_sortie", "utf-8"), regle=regle
                    )
                    streamwriter.set_liste_att(attributs)
                    ressource = sorties.creres(nom, streamwriter)
                regle.ressource = ressource
                dident = (groupe, classe)
            ressource.write(obj, regle.idregle)


READERS = {
    "ligne": (lire_textfile_ligne, "", True, (), None, None),
    "text": (lire_textfile_bloc, "", True, (), None, None),
    "fixed": (lire_textfile_pos, "", True, (), None, None),
}
# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {"text": (ecrire_objets_text, None, False, "", 0, "", "classe", "", "", None)}
