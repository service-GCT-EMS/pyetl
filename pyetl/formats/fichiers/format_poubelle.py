# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 12:41:26 2019

@author: 89965
sorties fictives
"""


def ecrire_objets_neant(self, regle, *_, **__) -> (int, int):
    """ pseudowriter ne fait rien :  poubelle"""
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):# on parcourt les objets
            if not obj.virtuel: # on ne traite pas les virtuels
                obj.setschema(None)
    return 0, 0

def stream_objets_neant(self, obj, *_, **__):
    """ pseudowriter ne fait rien :  poubelle"""
    obj.setschema(None)
    return 0, 0

def compte_obj_stream(self, obj, regle, *_, **__):
    '''poubelle avec comptage '''
    groupe, classe = obj.ident
#    obj.setschema(None)
    liste_fich = regle.stock_param.liste_fich
    nom = 'compt_'+groupe+'.'+classe
    liste_fich[nom] += 1
    return 0, 0


def compte_obj(self, regle, *_, **__):
    '''poubelle avec comptage'''
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):# on parcourt les objets
            if obj.virtuel: # on ne traite pas les virtuels
                continue
#            print ('comptage', regle)
            self.ecrire_objets_stream(obj, regle)
    return 0, 0


# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {'#poubelle':(ecrire_objets_neant, stream_objets_neant,
                        False, 'no', 0, "", 'all', None, None),
           '#comptage':(compte_obj, compte_obj_stream,
                        False, 'no', 0, "", 'all', None, None)}
#                  reader,geom,hasschema,auxfiles
READERS = {'interne': (None, None, False, ())}
