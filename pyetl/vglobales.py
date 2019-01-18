# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 13:47:55 2019

@author: 89965
"""
#import logging

VERSION = "0.8.2.2_e"
#LOGGER = logging.getLogger('pyetl') # un logger
MAINMAPPER = None


def set_mainmapper(val):
    global MAINMAPPER
#    print ('positionnement de mainMapper', val)
    MAINMAPPER =  val

def getmainmapper():
    return MAINMAPPER

#def initlogger(fichier=None, niveau_f=logging.DEBUG, niveau_p=logging.WARNING):
#    """ création de l'objet logger qui va nous servir à écrire dans les logs"""
## on met le niveau du logger à DEBUG, comme ça il écrit tout dans le fichier log s'il existe
#    if not LOGGER.handlers:
## création d'un handler qui va rediriger chaque écriture de log sur la console
#        LOGGER.setLevel(niveau_p)
#        print_handler = logging.StreamHandler()
#        printformatter = logging.Formatter('%(levelname)s %(funcName)s: %(message)s')
#        print_handler.setFormatter(printformatter)
#
#        print_handler.setLevel(niveau_p)
#        LOGGER.addHandler(print_handler)
#    if fichier:
#        LOGGER.setLevel(niveau_f)
#        # création d'un formateur qui va ajouter le temps, le niveau
#        # de chaque message quand on écrira un message dans le log
#        fileformatter = logging.Formatter('%(asctime)s::%(levelname)s::%(module)s.%(funcName)s'+
#                                          '::%(message)s')
##        infoformatter = logging.Formatter('%(asctime)s::%(levelname)s::%(message)s')
#        # création d'un handler qui va rediriger une écriture du log vers
#        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
#        file_handler = logging.FileHandler(fichier)
#        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
#        # créé précédement et on ajoute ce handler au logger
#        file_handler.setLevel(niveau_f)
#        file_handler.setFormatter(fileformatter)
#        LOGGER.addHandler(file_handler)
#        LOGGER.info("pyetl:"+VERSION)