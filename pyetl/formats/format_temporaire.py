# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 13:33:58 2015

@author: 89965
"""
# from . import csv as E
import logging
from collections import namedtuple
from itertools import chain
from .fichiers.format_asc import ajout_attribut_asc, att_to_text
from .interne.objet import Objet

LOGGER = logging.getLogger("pyetl")


def _ecrire_section_tmp(section):
    """ecrit une section en format temporaire"""
    #    print     ("S,"+str(section.couleur) + "," + str(section.courbe) + ',' + section.__list_if__)

    return (
        "S," + section.couleur + "," + str(section.courbe) + "," + section.__list_if__
    )


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
        + list((chain.from_iterable([_ecrire_ligne_tmp(j) for j in poly.lignes])))
        + ["Q"]
    )


def _ecrire_polygones_tmp(polygones):
    """ecrit un ensemble de  polygones en format temporaire"""
    return chain.from_iterable([_ecrire_polygone_tmp(j) for j in polygones])


def ecrire_geometrie_tmp(geom):
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


def geom_from_tmp(obj):
    """convertit une geometrie en format temporaire en geometrie interne"""
    geom_v = obj.geom_v
    geom_v.type = "2"
    poly = None
    geom = obj.attributs["#geom"]
    lig = None
    for i in geom:
        code = i[0]
        if code == "P":
            poly = geom_v.polygones
            geom_v.type = "3"
        elif code == "L":
            lig = geom_v.nouvelle_ligne_s()
        elif code == "S":
            sect_parts = i.split(",")
            couleur, arc = sect_parts[1:2]
            coords = [list(map(float, j.split(" "))) for j in sect_parts[3:]]
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


def tmp_entetes(obj, form):
    """ retourne un entete en format interne
        form permet de connaitre le format de stockage de la geometrie
        en general de l'ewkt
    """
    niveau, classe = obj.ident
    if not form:
        form = ""
    entete = (
        "1"
        + niveau
        + ","
        + classe
        + ","
        + form
        + ","
        + obj.attributs["#type_geom"]
        + "\n"
    )
    return entete


def tmp_attributs(obj):
    """stockage des attributs.
        c'est de l'asc
    """

    attlist = att_to_text(obj, None, None)

    return attlist


#
def tmp_geom(obj, convertisseur):
    """serialise les geometries"""
    if obj.attributs["#type_geom"] == "0":
        return ""
    # print 'tmp-geom',self.atg,ecrire_geom_ewkt(self.geom_v,False,False,err)
    # if obj.atg : return '3'+ecrire_geom_ewkt(obj.geom_v,False,False,err)+'\n'
    if obj.geom_v.valide:
        if convertisseur is None:
            convertisseur = ecrire_geometrie_tmp
        geom = convertisseur(obj.geom_v)
    else:
        geom = obj.attributs["#geom"]
    if isinstance(geom, list):
        return "3" + "\n3".join(geom) + "\n"
    if isinstance(geom, str):
        return "3" + geom + "\n"


# =================== format temporaire ==============================
def lire_objets(fichier, stock_param):
    """relit les objets du stockage temporaire"""
    obj = None
    form = None
    for ligne in open(fichier, "r", encoding="utf-8"):
        if ligne:
            code = ligne[0]
            if code == "1":
                niveau, classe, form, type_geom = ligne[1:-1].split(",")
                obj = Objet(
                    niveau,
                    classe,
                    format_natif=form,
                    conversion=stock_param.get_converter(form),
                )
                obj.attributs["#type_geom"] = type_geom
                #                if form: print ('format natif ',form,stock_param.get_converter(form))
                if type_geom != "0":
                    obj.attributs["#geom"] = []
                continue
            if not obj:
                LOGGER.error("erreur fichier temporaire %s", ligne)
                # print("erreur fichier temporaire ", ligne)
                continue
            if code == "2" or code == "4":
                ajout_attribut_asc(obj, ligne)
            elif code == "3":
                obj.attributs["#geom"].append(ligne[1:-1])
            elif code == "5":
                if obj.attributs["#geom"] and not obj.attributs_geom:
                    LOGGER.error(
                        "geom_lue sans convertisseur %s : %", form, obj.attributs_geom
                    )
                    # print("geom_lue sans convertisseur", form, ":", obj.attributs_geom)
                #                print (obj.geom)
                obj.geomnatif = True
                yield obj
                obj = None


def ecrire_objets(nom, mode, groupe, geomwriter, nom_format="#ewkt"):
    """stocke les objets en format temporaire"""
    fichier = open(nom, mode, encoding="utf-8")
    # print('ecriture temporaire',groupe, nom_format)
    for classe in groupe:
        liste_obj = groupe[classe]
        #        print( "ecriture" , classe, len(liste_obj))
        for i in liste_obj:
            if i.geom_v.valide:
                fichier.write(tmp_entetes(i, nom_format))
            else:
                fichier.write(tmp_entetes(i, i.format_natif))
            fichier.write(att_to_text(i, None, None))
            fichier.write("\n")
            geom = tmp_geom(i, geomwriter)
            if geom:
                fichier.write(geom)
                fichier.write("\n")
            fichier.write("5fin_objet\n")
    fichier.close()
