# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 13:33:58 2015

@author: 89965
format interne geometrique pour le stockage en fichier temporaire
"""
from itertools import chain


def _ecrire_section_tmp(section):
    """ecrit une section en format temporaire"""
    #    print     ("S,"+str(section.couleur) + "," + str(section.courbe) + ',' + section.__list_if__)

    return (
        "S," + section.couleur + "," + str(section.courbe) + "," + section.__list_if__
    )


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
    return chain.from_iterable([_ecrire_ligne_tmp(j) for j in lignes])


def _ecrire_polygone_tmp(poly):
    """ecrit un polygone en format temporaire"""
    #    print("polygone", len(poly.lignes))
    #    print('longueur lignes',[len(j.sections) for j in poly.lignes])
    #    print('liste')
    return (
        ["P"]
        + list(chain.from_iterable([_ecrire_ligne_tmp(j) for j in poly.lignes]))
        + ["Q"]
    )


def _ecrire_polygones_tmp(polygones):
    """ecrit un ensemble de  polygones en format temporaire"""
    return chain.from_iterable([_ecrire_polygone_tmp(j) for j in polygones])


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
    geom = obj.attributs["#geom"]
    for i in geom:
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


def geom_from_osm(obj):
    """ convertit une geometrie osm"""
    geomv = obj.geom_v
    # print ('conversion osm', geomv.valide, obj.attributs["#geom"])
    if geomv.valide:
        return True
    if not obj.attributs["#geom"]:
        obj.attributs["#type_geom"] = "0"
        geomv.type=0
        return True
    exterieur = False
    interieur = []
    for desc in obj.attributs["#geom"]:
        element, role = desc
        try:
            if role == "node" or role == "label":
                geomv.type = "1"
                geomv.addpoint(element, 2)
            elif role == "outer":
                exterieur = True
                # print ('exterieur')
                geomv.cree_section(element, 2, 1, 0)
                for i in interieur:
                    geomv.cree_section(i, 2, 1, 0, interieur=True)
                interieur = []
            elif role == "inner":
                if exterieur:
                    geomv.cree_section(element, 2, 1, 0, interieur=True)
                else:
                    interieur.append(element)
            elif role in {"way", 'forward', 'part', 'main_stream'}:
                geomv.cree_section(element, 2, 1, 0)
            else:
                # print("role inconnu", role, obj)
                # print("role inconnu", role, obj.ident, obj.attributs['tags'])
                pass
        except TypeError as err:
            print ('erreur type ', err)
            print ('    objet:', obj.ident)
            print ('geometrie:', desc)
            print ('  element:', element)

    # if obj.attributs["#type_geom"] == "1":
    #     geomv.type = "1"
    #     for desc in obj.attributs["#geom"]:
    #         # print ('decodage desc', desc)
    #         pnt, role = desc
    #         geomv.addpoint(pnt, 2)
    # else:
    #     for sect, role in obj.attributs["#geom"]:
    #         print("osm:creation section ", sect, role)

    #         geomv.cree_section(sect, 2, 1, 0, interieur=role == "inner")

    obj.finalise_geom()
    return True


GEOMDEF = {"#gml": (ecrire_geometrie_gml, geom_from_gml), "#osm": (None, geom_from_osm)}
