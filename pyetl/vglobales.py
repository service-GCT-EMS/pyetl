# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 13:47:55 2019

@author: 89965
"""
#import logging

VERSION = "0.8.2.3p"
# version de developpement 21/2/2019
#LOGGER = logging.getLogger('pyetl') # un logger
MAINMAPPER = None


def set_mainmapper(val):
    '''positionnement du point d entree pou les traitements paralleles'''
    global MAINMAPPER
#    print ('positionnement de mainMapper', val)
    MAINMAPPER = val

def getmainmapper():
    '''recup du point d entree pour les traitements paralleles'''

    return MAINMAPPER