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
    geomdef = dict()
    for fich_module in os.listdir(os.path.dirname(__file__)):
        if fich_module.startswith("format_"):
            module = "."+os.path.splitext(fich_module)[0]
            try:
                format_def = importlib.import_module(module, package=__package__)
                for nom, description in getattr(format_def, 'GEOMDEF').items():
                    if nom in geomdef:
                        print('attention : redefinition du format de sortie', nom)
                    geomdef[nom] =  description

            except ImportError:
                print('module ',module ,'non disponible')

    return geomdef


GEOMDEF = loadmodules()
