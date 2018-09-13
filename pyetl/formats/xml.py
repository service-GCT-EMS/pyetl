# -*- coding: cp1252 -*-
# formats d'entree sortie
''' format xml en sortie '''

import os
import time
import xml.etree.cElementTree as ET
import re
from .interne.objet import Objet
from .fileio import FileWriter

#print ('osm start')
#import pyetl.schema as SC

# ewkt ##################################################################
#def parse_ewkb(geometrie,texte):
def ecrire_geom_xml(geomtemplate, geom_v, type_geom, multi, erreurs):
return ""

class XmlWriter(FileWriter):
    """ gestionnaire des fichiers xml en sortie """
    def __init__(self, nom, schema, extension, separ, entete, encoding='utf-8',
                 liste_fich=None, null='', writerparms=None):
        super().__init__(nom, encoding=encoding, liste_fich=liste_fich, schema=schema)

        self.extension = extension
        self.separ = separ
        self.nom = nom
        self.schema = schema
        self.null = null
        self.writerparms = writerparms
        template = self.writerparms.get('template')
        if template:
            self.readtemplate(template)
        self.classes = set()

        self.stats = liste_fich if liste_fich is not None else dict()
        self.encoding = encoding


    def header(self, init=1):
        ''' preparation de l'entete du fichiersr xml'''
        if not self.entete:
            return ''
        geom = self.separ+"geometrie"+"\n" if self.schema.info["type_geom"] != '0' else "\n"
        return self.separ.join(self.liste_att)+geom

    def readtemplate(self, templatefile, codec=DEFCODEC):
        """lit un fichier de description de template xml"""
        
        self.template = dict()
        
        try:
            with open(templatefile, "r", encoding=codec) as fich:
                for i in fich:
                    if i.startswith('!'):
                        if i.startswith('!!'):
                            i = i[1:]
                        else:
                            continue
                    args = i.split(";")+[""]

                    if i.statrswith("xmltemplate"):
                        liste = []
                        classe = args[1] if if args[1] else "#generique"
                            
                    liste = i[:-1].split(";")
                    if taille == -1:
                        stock[i[:-1]] = liste
                    else:
                        if len(liste) < taille:
                            liste = list(itertools.islice(itertools.cycle(liste), taille))
                        stock[';'.join([liste[i] for i in positions])] = liste
            if debug:
                print("chargement liste", fichier)
        except FileNotFoundError:
            print("fichier liste introuvable ", fichier)
    #    print('prechargement csv', stock)
        return stock



    def write(self, obj):
        '''ecrit un objet'''
        if obj.virtuel:
            return False#  les objets virtuels ne sont pas sortis
        template = self.templates.get(obj.ident,"")
        if not template:
            template = self.templates.get("#generique")
        sortie = []
        for i in template:
            balise = i[0]
            nargs = len(i)
            if nargs == 1:
                sortie.append(balise)
            else:
                args = ' '.join(i[k]+'="'+obj.attributs.get(i[k+1],i[k+2])+'"'
                                for k in range(1,nargs,3))
                sortie.append(balise+args+"/>")
                geom=""
                if obj.initgeom():
                    if self.type_geom:
                        geom = ecrire_geom_xml(self.tempates, obj.geom_v, self.type_geom,
                                               self.multi, obj.erreurs)
                else:
                    print('xml: geometrie invalide : erreur geometrique',
                          obj.ident, obj.numobj, obj.geom_v.erreurs.errs,
                          obj.attributs['#type_geom'],
                          self.schema.info["type_geom"], obj.geom)
                    geom = ""
                if not geom:
                    geom = self.null
                obj.format_natif = "xml"
                obj.geom = geom
                obj.geomnatif = True
                if obj.erreurs.actif == 2:
                    print('error: writer xml :', obj.ident, obj.ido, 'erreur geometrique',
                          obj.attributs['#type_geom'], self.schema.identclasse,
                          obj.schema.info["type_geom"], obj.erreurs.errs)
                    return False
            ligne = '\n'.join("sortie")
        self.fichier.write(ligne)
        self.fichier.write('\n')
        self.stats[self.nom] += 1
        return True
