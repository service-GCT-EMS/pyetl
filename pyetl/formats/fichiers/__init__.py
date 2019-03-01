# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 13:22:59 2019

@author: 89965
"""
import os
import importlib

def loadmodules():
    '''lit toutes les descriptions de format depuis le repertoire courant
    et enregistre les readers et writers'''
    writers = dict()
    readers = dict()
    for fich_module in os.listdir(os.path.dirname(__file__)):
        if fich_module.startswith("format_"):
            module = "."+os.path.splitext(fich_module)[0]
            try:
                format_def = importlib.import_module(module, package=__package__)
                for nom, desc in getattr(format_def, 'WRITERS').items():
                    if nom in writers:
                        print('attention : redefinition du format de sortie', nom)
                    writers[nom] =  desc
                for nom, desc in getattr(format_def, 'READERS').items():
#                    print ('lecture  READERS',nom,desc)
                    if desc[1] is None:
                        desc = (desc[0], noconversion, desc[1], desc[2])
                    if nom in readers:
                        print("attention : redefinition du format d'entree", nom)
                    readers[nom] =  desc
            except ImportError:
                print('module ',module ,'non disponible')

    return readers, writers

def noconversion(obj):
    ''' conversion geometrique par defaut '''
    return obj.geom_v.type == '0'


READERS, WRITERS = loadmodules()
#print ('chargement', READERS)