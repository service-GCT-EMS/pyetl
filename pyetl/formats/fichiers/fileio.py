# -*- coding: utf-8 -*-
""" format texte en lecture et ecriture"""

# import time
# import pyetl.schema as SC
import sys
import os
import io


def _defaultconverter(obj, liste_att, transtable=None, separ=None):
    """convertisseur d'objets de base"""
    return obj.__json_if__(liste_att)


#########################################################################
# format csv et txt geo etc
# tous les fichiers tabules avec ou sans entete
#########################################################################


class FileWriter(object):
    """superclasse des classes writer de fichiers"""

    INIT = 0
    OPEN = 1
    CLOSE = 2
    FINAL = 3
    FAIL = 4

    def __init__(self, nom, schema=None, regle=None):
        self.nom = nom
        self.schemaclasse = schema
        self.output = regle.output
        self.regle = regle
        self.writerparms = self.output.writerparms
        self.liste_att = (
            schema.get_liste_attributs(liste=self.output.liste_att)
            if schema
            else self.output.liste_att
        )
        self.fichier = None
        self.geomwriter = self.writerparms["geomwriter"]
        self.null = self.writerparms.get("null")
        self.extension = self.writerparms.get("extension", self.output.nom)
        self.srid = self.output.srid
        self.separ = self.writerparms.get("separ", ";")
        self.encoding = regle.output.encoding
        newlines = self.writerparms.get("newlines", None)
        if newlines == "unix":
            newlines = "\n"
        elif newlines == "windows":
            newlines = "\r\n"
        elif newlines == "auto" or not newlines:
            newlines = None
        else:
            print("newlines inconnu -> defaut", newlines)
            newlines = None
        self.newlines = newlines
        self.schema = schema.schema if schema else None
        self.htext = ""
        self.hinit = ""
        self.ttext = ""
        self.transtable = str.maketrans("", "")
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
            if self.regle.stock_param.mode.startswith("web"):
                self.fichier = io.StringIO()
                if self.layer in self.regle.stock_param.webstore:
                    self.regle.stock_param.webstore[self.layer].append(self.fichier)
        elif self.nom == "#attw":
            self.fichier = io.StringIO()
        else:
            # print("filewriter: ouvrir", self.nom)
            try:
                self.fichier = open(
                    self.nom,
                    mode,
                    encoding=self.encoding,
                    errors="backslashreplace",
                    newline=self.newlines,
                )
            except FileNotFoundError as err:
                if self.regle:
                    self.regle.stock_param.logger.error(
                        "fichier inexistant %s", self.nom
                    )
                else:
                    print("fichier inexistant " + str(self.nom))
                self.fichier = None

    def open(self):
        """ouverture de fichier"""
        # print ("filewriter: open")
        self.ouvrir("w")
        self.ressource.etat = 1
        if self.fichier:
            self.fichier.write(self.header())

    def reopen(self):
        """reouverture"""
        self.ouvrir("a")
        self.ressource.etat = 1

    def closed(self):
        return self.fichier.closed if self.fichier else True

    def close(self):
        """fermeture"""
        #        print("fileeio fermeture", self.nom)
        if self.nom == "#print":
            return  # stdout
        try:
            self.fichier.close()
            self.ressource.etat = 2
        except AttributeError:
            print("error: fw  : writer close: fichier non defini", self.nom)
            raise

    def changeclasse(self, schemaclasse, attributs=None):
        """ ecriture multiclasse on change de schema"""
        #        print ("changeclasse schema:", schemaclasse, schemaclasse.schema)
        self.layer = schemaclasse.identclasse
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
        if chaine:
            self.fichier.write(chaine)
            if chaine[-1] != "\n":
                self.fichier.write("\n")
        return True
