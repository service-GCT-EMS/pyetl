# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 13:33:58 2015

@author: 89965
format interne geometrique pour le stockage en fichier temporaire
"""
from itertools import chain


def _extendlist(liste):
    """utilitaire d'applatissement d'une liste de liste
    c est une syntaxe qui ne s'invente pas alors quand on l'a on la garde"""
    #    return [x for slist in liste for x in slist]
    return chain.from_iterable(liste)
    # l=liste[0]
    # print 'liste a applatir',l
    # for j in liste[1:]: l.extend(j)
    # return l


def _ecrire_section_tmp(section):
    """ecrit une section en format temporaire"""
    #    print     ("S,"+str(section.couleur) + "," + str(section.courbe) + ',' + section.__list_if__)

    return "S," + section.couleur + "," + str(section.courbe) + "," + section.__list_if__


# def ecrire_ligne_tmp(ligne):
#    return (["L"].extend([ecrire_section_tmp(j) for j in ligne.sections])).append("M")
def _ecrire_ligne_tmp(ligne):
    """ecrit une ligne en format temporaire"""
    #    print("ligne", len(ligne.sections))
    #    print('ecrire_ligne',['L']+[_ecrire_section_tmp(j) for j in ligne.sections])
    #    print('fin_ligne')
    return ["L"] + [_ecrire_section_tmp(j) for j in ligne.sections]


def _ecrire_lignes_tmp(lignes):
    """ecrit un ensemble de  lignes en format temporaire"""
    return _extendlist([_ecrire_ligne_tmp(j) for j in lignes])


def _ecrire_polygone_tmp(poly):
    """ecrit un polygone en format temporaire"""
    #    print("polygone", len(poly.lignes))
    #    print('longueur lignes',[len(j.sections) for j in poly.lignes])
    #    print('liste')
    return ["P"] + (_extendlist([_ecrire_ligne_tmp(j) for j in poly.lignes])) + ["Q"]


def _ecrire_polygones_tmp(polygones):
    """ecrit un ensemble de  polygones en format temporaire"""
    return _extendlist([_ecrire_polygone_tmp(j) for j in polygones])


def ecrire_geometrie_gml(geom):
    """ecrit une geometrie en format temporaire"""
    if geom.type == "1":
        return ["O"] + geom.point.__list_if__
    elif geom.type == "2":
        #        print("geom_tmp",geom,geom.type,len(geom.lignes) )
        if len(geom.lignes) > 1:
            return _ecrire_lignes_tmp(geom.lignes)
        return _ecrire_ligne_tmp(geom.lignes[0])
    elif geom.type == "3":
        #        print("geom_tmp",geom,geom.type,len(geom.polygones) )

        if len(geom.polygones) > 1:
            return _ecrire_polygones_tmp(geom.polygones)
        return _ecrire_polygone_tmp(geom.polygones[0])
    else:
        raise TypeError("geometrie inconnue: " + geom.type)


def geom_from_gml(obj):
    """convertit une geometrie en format temporaire en geometrie interne"""
    geom_v = obj.geom_v
    geom_v.type = "2"
    poly = None
    nouvelle_ligne = False
    for i in obj.geom:
        code = i[0]
        if code == "P":
            poly = geom_v.polygones
            geom_v.type = "3"
        elif code == "L":
            nouvelle_ligne = True
        elif code == "S":
            sect_parts = i.split(",")
            couleur, arc = sect_parts[1:2]
            coords = [list(map(float, j.split(" "))) for j in sect_parts[3:]]
            if nouvelle_ligne:
                lig = geom_v.nouvelle_ligne_s()
            lig.ajout_section(couleur, arc, len(coords[0]), coords)
        elif code == "M":  # fin ligne
            geom_v.ajout_ligne(lig)
            if poly:
                poly.ajout_contour(lig)
        elif code == "Q":  # fin polygone
            geom_v.ajout_polygone(poly)
            poly = None
        elif code == "O":
            pnt = [float(j) for j in i[1:].split(" ")]
            geom_v.setpoint(pnt, None, len(pnt))
    return geom_v


GEOMDEF = {"#gml": (ecrire_geometrie_gml, geom_from_gml)}
