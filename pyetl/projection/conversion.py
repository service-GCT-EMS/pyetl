# -*- coding: utf-8 -*-
"""#projection de geometries"""
import os

from . import transfo_coord3 as TC


def init_proj(entree, sortie, repgrilles=None):
    """initialise la projection
    systemes disponibles : L1,L2,CC48,CC49,LL"""
    sens = 0
    connus = ["L1", "L2", "CC48", "CC49", "LL","L93"]
    if entree not in connus or sortie not in connus:
        print("conversion non implementee ", entree, "->", sortie)
        return None
    if entree == "L1" or entree == "L2":
        sens = 1
    if sortie == "L1" or sortie == "L2":
        sens = 2
    if repgrilles == "NG":
        repgrilles = ""
        sens = 0
    if not repgrilles:
        repgrilles = os.path.join(os.path.dirname(__file__), "grilles")
    proj = TC.Projection(repgrilles, "grilles.lst", entree, sortie, sens)
    if proj.valide:
        #        print('initialisation projection', proj.description)
        return proj
    return None


def projette_points(proj, points):
    """convertit les coordonees d'un point"""
    grilles = dict()
    for pnt in points:
        grille, pnt[0], pnt[1] = proj.calcule_point_proj(pnt[0], pnt[1])
        grilles[grille] = grilles.get(grille, 0) + 1
    print("liste de grilles ", grilles)

    return grilles


def projette_obj(proj, obj, sortie="None"):
    """reprojette l'ensemble d'un objet"""
    grilles = dict()
    if obj.initgeom():
        for pnt in obj.geom_v.coords:
            grille, pnt[0], pnt[1] = proj.calcule_point_proj(pnt[0], pnt[1])
            grilles[grille] = grilles.get(grille, 0) + 1
        if sortie:
            print("liste de grilles ", grilles)
            obj.attributs[sortie] = ",".join([i + ":" + str(grilles[i]) for i in grilles])
