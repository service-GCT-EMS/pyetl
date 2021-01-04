# -*- coding: utf-8 -*-
""" format texte en lecture et ecriture"""

# import time
# import pyetl.schema as SC
import sys
import os
import io


def _defaultconverter(obj, liste_att, transtable=None, separ=None):
    """convertisseur d'objets de base"""
    obj.liste_attributs = liste_att
    return obj.__json_if__()


#########################################################################
# format csv et txt geo etc
# tous les fichiers tabules avec ou sans entete
#########################################################################
# def getnoms(rep, chemin, fichier):
#     """ determine les noms de groupe et de schema"""
#     chem = chemin
#     niveaux = []
#     classe, ext = os.path.splitext(fichier)
#     schema = "schema_"+str(ext)

#     if rep and rep != ".":
#         schema = os.path.basename(rep)
#     while chem:
#         chem, nom = os.path.split(chem)
#         niveaux.append(nom)

#     if not niveaux:
#         groupe = ""
#     else:
#         groupe = "_".join(niveaux)
#     #    print(rep, "<>", chemin, "<>", fichier, "traitement", schema, "<>", groupe, "<>", classe)
#     return schema, groupe, classe


class FileWriter(object):
    """superclasse des classes writer de fichiers"""

    INIT = 0
    OPEN = 1
    CLOSE = 2
    FINAL = 3
    FAIL = 4

    def __init__(
        self,
        nom,
        # liste_att=None,
        # converter=_defaultconverter,
        # geomwriter=None,
        # separ=None,
        # encoding="utf-8",
        # srid="3948",
        schema=None,
        regle=None
        # f_sortie=None, # writer utilise
    ):
        self.nom = nom
        self.writer = regle.writer
        self.regle = regle
        self.writerparms = self.writer.writerparms
        self.liste_att = (
            schema.get_liste_attributs(liste=self.writer.liste_att)
            if schema
            else self.writer.liste_att
        )
        self.fichier = None
        self.encoding = self.writer.encoding or "utf-8"
        # self.converter = self.writer.converter
        self.geomwriter = self.writer.geomwriter
        self.extension = self.writer.extension
        self.entete = self.writer.entete
        self.null = self.writer.null
        self.srid = "3948"
        self.separ = self.writer.separ
        self.schema = schema
        self.htext = ""
        self.hinit = ""
        self.ttext = ""
        self.transtable = None
        self.regle_ref = None  # regle de reference pour l'acces aux contextes

    def header(self, init=None):
        """entete du fichier"""
        if init:
            return self.hinit
        return self.htext

    def tail(self):
        """fin de fichier"""
        return self.ttext

    def ouvrir(self, mode):
        """retourne une sortie ouverte """

        if self.nom == "#print":
            self.fichier = sys.stdout
        elif self.nom == "#attw":
            self.fichier = io.StringIO()
        else:
            self.fichier = open(
                self.nom, mode, encoding=self.encoding, errors="backslashreplace"
            )

    def open(self):
        """ouverture de fichier"""
        self.ouvrir("w")
        self.fichier.write(self.header())

    def reopen(self):
        """reouverture"""
        self.ouvrir("a")

    def closed(self):
        return self.fichier.closed if self.fichier else True

    def close(self):
        """fermeture"""
        #        print("fileeio fermeture", self.nom)
        if self.nom == "#print":
            return  # stdout
        try:
            self.fichier.close()
        except AttributeError:
            print("error: fw  : writer close: fichier non defini", self.nom)

    def changeclasse(self, schemaclasse, attributs=None):
        """ ecriture multiclasse on change de schema"""
        #        print ("changeclasse schema:", schemaclasse, schemaclasse.schema)
        self.liste_att = schemaclasse.get_liste_attributs(liste=attributs)

    def finalise(self):
        """fermeture definitive (ecrit la fin de fichier)"""
        end = self.tail()
        if end:
            try:
                if self.fichier.closed:
                    self.reopen()
            except AttributeError:
                print("error: fw  : writer finalise: fichier non defini", self.nom)
            self.fichier.write(end)
            self.close()
            return self.FINAL
        self.close()
        return self.CLOSE

    def set_liste_att(self, liste_att):
        """cache la liste d:attributs"""
        self.liste_att = liste_att

    def write(self, obj):
        """ecrit un objet complet"""
        chaine = self.converter(obj, self.liste_att, transtable=self.transtable)
        self.fichier.write(chaine)
        if chaine[-1] != "\n":
            self.fichier.write("\n")
        return True
