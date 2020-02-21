# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de traitements de nuages de points
"""
import logging
import os
import io
import pdal

# ==================constructeurs de pipeline=================


def f_lasreader(regle, obj):
    """#aide||defineit les fichiers las en entree
   #pattern1||C;?;A;lasreader;C;?=D

    """


def h_lasfilter(regle):
    """extraction d'elements d'un las"""
    regle.json = open(regle.params.cmp1.val).readlines()


def f_lasfilter(regle, obj):
    """#aide||decoupage d'un attribut xml en objets
  #aide_spec||s'il n'y a pas d'attributs de sortie on cree un objet pour chaque element
   #pattern1||C;?;?A;lasfilter;C;?=D
#parametres1||repertoire de sortie;defaut;attribut;;json de traitement;D: dynamique
     #!test1||obj||^V4;a:b:cc:d;;set||^r1,r2,r3,r4;;V4;split;:;||atv;r3;cc
     #!test2||obj||^V4;a:b:c:d;;set||^;;V4;split;:;||cnt;4
    """

    tree = ET.fromstring(obj.attributs[regle.params.att_entree.val])
    for elem in tree.findall(regle.recherche):
        obj2 = obj.dupplique()
        obj2.attributs.update(((regle.prefix + i, j) for i, j in elem.items()))
        regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["next"])
    return True
