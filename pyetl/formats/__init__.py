# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 10:14:31 2019

@author: 89965

gestionaire de formats de traitements
les formats sont enregistres en les mettant dans des fichiers python qui
commencent par format_

"""
from types import MethodType
from .db import DATABASES
from .fichiers import READERS, WRITERS
from .geometrie import GEOMDEF



class Reader(object):
    '''wrappers d'entree génériques'''
#    databases = DATABASES
    lecteurs = READERS
    geomdef = GEOMDEF
    @classmethod
    def get_formats(classe):
        return classe.lecteurs
#    auxiliaires = AUXILIAIRES
#    auxiliaires = {a:AUXILIAIRES.get(a) for a in LECTEURS}

    def __init__(self, nom, regle, regle_start, debug=0):
        self.nom_format = nom
        self.debug = debug
        self.regle = regle # on separe la regle de lecture de la regle de demarrage
        self.regle_start = regle_start
        stock_param = regle_start.stock_param
        self.traite_objets = stock_param.moteur.traite_objet
        self.set_format_entree(nom)
        if self.debug:
            print("debug:format: instance de reader ", nom)

    def set_format_entree(self, nom):
        '''#positionne un format d'entree'''
        nom = nom.replace('.', '').lower()
        if nom in self.lecteurs:
            lire, converter, cree_schema, auxiliaires = self.lecteurs[nom]
            self.lire_objets = MethodType(lire, self)
            self.nom_format = nom
            self.cree_schema = cree_schema
            self.auxiliaires = auxiliaires
            self.conv_geom = self.geomdef[converter][1]
            if self.debug:
                print("debug:format: lecture format "+ nom)
        else:
            print("error:format: format entree inconnu", nom)

    def get_info(self):
        ''' affichage du format courant : debug '''
        print('info :format: format courant :', self.nom_format)

    def get_converter(self, format_natif):
        '''retourne la fonction de conversion geometrique'''
        return self.lecteurs.get(format_natif, self.lecteurs['interne'])[1]





class Writer(object):
    '''wrappers de sortie génériques'''
    databases = DATABASES
    sorties = WRITERS
    def __init__(self, nom, debug=0):
#        print ('dans writer', nom)

        self.dialecte = None
        destination = ''
        dialecte = ''
        if ':' in nom:
            defs = nom.split(':')
#            print ('decoupage writer', nom, defs,nom.split(':'))
            nom = defs[0]
            dialecte = defs[1]
            destination = defs[2] if len(defs) > 2 else ''
            fich = defs[3] if len(defs) > 3 else ''
        self.nom_format = nom
#        self.destination = destination
        self.regle = None
        self.debug = debug
        self.writerparms = dict() # parametres specifique au format
        '''#positionne un format de sortie'''
        nom = nom.replace('.', '').lower()
        if nom in self.sorties:
            ecrire, stream, tmpgeo, schema, casse, taille, driver, fanoutmax,\
            nom_format = self.sorties[nom]
        else:
            print("format sortie inconnu '"+nom+"'", self.sorties.keys())
            ecrire, stream, tmpgeo, schema, casse, taille, driver, fanoutmax, nom_format =\
                    self.sorties['#poubelle']
        if nom == 'sql':

            if dialecte == '':
                dialecte = 'natif'
            else:
                dialecte = dialecte if dialecte in self.databases else 'sql'
                self.writerparms['dialecte'] = self.databases[dialecte]
                self.writerparms['base_dest'] = destination
                self.writerparms['destination'] = fich
        else:
            self.writerparms['destination'] = destination
        self.dialecte = dialecte
        self.ecrire_objets = ecrire
        self.ecrire_objets_stream = stream
        self.tmp_geom = tmpgeo
        self.nom_fgeo = nom_format
        self.calcule_schema = schema
        self.minmaj = casse # determine si les attributs passent en min ou en maj
        self.driver = driver
        self.nom = nom
        self.l_max = taille
        self.ext = '.'+nom
        self.multiclasse = fanoutmax != 'classe'
        self.fanoutmax = fanoutmax
#        print('writer : positionnement dialecte',nom, self.nom_format, self.writerparms)

    def get_info(self):
        ''' affichage du format courant : debug '''
        print('error:format: format courant :', self.nom_format)


