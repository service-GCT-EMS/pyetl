# -*- coding: utf-8 -*-
''' format texte en lecture et ecriture'''

#import time
#import pyetl.schema as SC
import sys
from collections import defaultdict


def _set_liste_attributs(schemaclasse, attributs):
    '''positionne la liste d'attributs a sortir'''
    if attributs:
        return attributs
    if schemaclasse:
        return schemaclasse.get_liste_attributs()
    return None

def _defaultconverter(obj, liste_att, transtable=None, separ=None):
    '''convertisseur d'objets de base'''
    obj.liste_attributs = liste_att
    return obj.__json_if__()

class FileWriter(object):
    """superclasse des classes writer de fichiers"""
    INIT = 0
    OPEN = 1
    CLOSE = 2
    FINAL = 3
    FAIL = 4


    def __init__(self, nom, liste_att=None, converter=_defaultconverter, separ=None,
                 encoding='utf-8', liste_fich=None, srid='3948', schema=None,
                 f_sortie=None):
        self.nom = nom
        self.f_sortie = f_sortie
        if f_sortie:
            self.writerparms = f_sortie.writerparms
        self.liste_att = _set_liste_attributs(schema, liste_att)
        self.fichier = None
        self.etat = self.INIT
        self.stats = liste_fich if liste_fich is not None else defaultdict(int)
        self.encoding = encoding
        self.converter = converter
        self.srid = srid
        self.separ = separ
        self.schema = schema
        self.htext = ""
        self.hinit = ""
        self.ttext = ""
        self.transtable = None

    def header(self, init=None):
        """entete du fichier"""
        if init:
            return self.hinit
        return self.htext


    def tail(self):
        """fin de fichier"""
        return self.ttext

    def open(self):
        """ouverture de fichier"""
        if self.etat != self.INIT: # le fichier est deja la on essaye de reouvrir
            self.reopen(self)
            return
        try:
            self.fichier = sys.stdout if self.nom == "#print" else\
                           open(self.nom, 'w', encoding=self.encoding)#stdout

            self.fichier.write(self.header())
            self.stats[self.nom] = self.stats.get(self.nom, 0)
            self.etat = self.OPEN
        except IOError:
            self.etat = self.FAIL
            print("erreur ouverture fichier")

    def reopen(self):
        """reouverture"""
        if self.etat == self.CLOSE:
            try:
                self.fichier = sys.stdout if self.nom == "#print" else\
                               open(self.nom, 'a', encoding=self.encoding)#stdout
            except IOError:
                self.etat = self.FAIL
                print("erreur ouverture fichier", self.nom)


    def close(self):
        """fermeture"""
#        print("fileeio fermeture", self.nom)
        if self.nom == "#print":
            return # stdout
        try:
            self.etat = self.CLOSE
            self.fichier.close()
        except AttributeError:
            print('error: fw  : writer close: fichier non defini', self.nom)

    def changeclasse(self, schemaclasse, attributs=None):
        ''' ecriture multiclasse on change de schema'''
#        print ("changeclasse schema:", schemaclasse, schemaclasse.schema)
        self.liste_att = _set_liste_attributs(schemaclasse, attributs)


    def finalise(self):
        """fermeture definitive (ecrit la fin de fichier)"""
        end = self.tail()
        if end:
            try:
                if self.fichier.closed:
                    self.reopen()
            except AttributeError:
                print('error: fw  : writer finalise: fichier non defini', self.nom)
            self.fichier.write(end)
            self.etat = self.FINAL
        self.close()

    def set_liste_att(self, liste_att):
        """cache la liste d:attributs"""
        self.liste_att = liste_att

    def write(self, obj):
        '''ecrit un objet complet'''
        chaine = self.converter(obj, self.liste_att, transtable=self.transtable)
        self.fichier.write(chaine)
        if chaine[-1] != "\n":
            self.fichier.write("\n")
        self.stats[self.nom] += 1
        return True
