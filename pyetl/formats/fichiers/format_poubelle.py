# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 12:41:26 2019

@author: 89965
sorties fictives
"""


def ecrire_objets_neant(regle, *_, **__) -> (int, int):
    """ pseudowriter ne fait rien :  poubelle"""
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):# on parcourt les objets
            if not obj.virtuel: # on ne traite pas les virtuels
                obj.setschema(None)
    return 0, 0

def stream_objets_neant(obj, *_, **__):
    """ pseudowriter ne fait rien :  poubelle"""
    obj.setschema(None)
    return 0, 0

def compte_obj_stream(obj, regle, *_, **__):
    '''poubelle avec comptage '''
    groupe, classe = obj.ident
#    obj.setschema(None)
    liste_fich = regle.stock_param.liste_fich
    nom = 'compt_'+groupe+'.'+classe
    liste_fich[nom] += 1
    return 0, 0


def compte_obj(regle, *_, **__):
    '''poubelle avec comptage'''
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):# on parcourt les objets
            if obj.virtuel: # on ne traite pas les virtuels
                continue
            compte_obj_stream(obj, regle)
    return 0, 0




WRITERS = {'#poubelle':(ecrire_objets_neant, stream_objets_neant, ecrire_objets_neant,
                        False, 'no', 0, "", 'all', None),
           '#comptage':(compte_obj, compte_obj_stream, compte_obj,
                        False, 'no', 0, "", 'all', None)}

READERS = {'interne': (None, None, False,())}