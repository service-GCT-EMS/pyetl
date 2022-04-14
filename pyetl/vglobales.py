# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 13:47:55 2019

@author: 89965
"""
# import logging
import os
import platform


REVISION = "0.8.3p"
BUILD = 52
isdev = (
    "_dev" if os.path.isdir(os.path.join(os.path.dirname(__file__), "devenv")) else ""
)
VERSION = REVISION + " (build:" + str(BUILD) + isdev + ")"
# version de production
MAINMAPPER = [None]


def set_mainmapper(val):
    """positionnement du point d entree pou les traitements paralleles"""
    # print("positionnement de mainMapper", val)
    MAINMAPPER[0] = val


def getmainmapper():
    """recup du point d entree pour les traitements paralleles"""
    return MAINMAPPER[0]


DEFCODEC = "utf-8"
if platform.system() == "Windows" and platform.release() == "XP":
    DEFCODEC = "cp1252"
# print('codec ES positionne par defaut a ', DEFCODEC)
DEBUG = False


def getdefcodec():
    """ recupere la variable globale defcodec"""
    return DEFCODEC
