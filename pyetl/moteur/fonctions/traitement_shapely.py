# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de manipulation de geometries shapely
"""
# import re
import math as M
from shapely import geometry as SG

from .traitement_geom import setschemainfo

# ===============================================fonctions du module shapely============================================


def r_orient(geom):
    sgeom = geom.sgeom or geom.__shapelygeom__
    return sgeom.minimum_rotated_rectangle


def calculeangle(p1, p2):
    """ valeur d'angle en degres"""
    angle = M.atan2(p2[0] - p1[0], p2[1] - p1[1]) * 180 / M.pi
    return angle


def f_rectangle_oriente(regle, obj):
    """#aide||calcul du rectangle oriente minimal
    #pattern||;;;r_min;;
      #test1||obj;ligne3p||^;;;r_min;;||atv;#type_geom;3
      #test2||obj;ligne3p||^;;;r_min;;||^Z;;;aire||^Z;;Z;round;5;||atn;Z;2
    """
    if obj.geom_v.sgeom or obj.initgeom():
        sgeom = r_orient(obj.geom_v)
        obj.geom_v.setsgeom(sgeom)
        setschemainfo(regle, obj, multi=False, type="3")


def h_angle(regle):
    """preparation angle"""
    if regle.elements["cmp1"].group(0):
        tmp = regle.elements["cmp1"].group(0).split(":")
        regle.ip1 = int(tmp[0])
        regle.ip2 = int(tmp[1]) if len(tmp) > 1 else -1
    else:
        regle.ip1 = None


def f_angle(regle, obj):
    """#aide||calcule un angle de reference de l'objet
    #aide_spec||N:N indices des point a utiliser, P creation d'un point au centre
    #pattern||S;;;angle;?N:N;?=P
    #schema||ajout_attribut
    #test1||obj;poly||^Z;;;angle;;||atv;Z;0.0
    #test2||obj;poly||^Z;;;angle;;P||^X,Y;;;coordp;;||atv;X;0.5
    #test3||obj;ligne||^Z;;;angle;;P||^X,Y;;;coordp;;||atv;Y;0.5
    #test4||obj;ligne45||^Z;;;angle;;P||^X,Y;;;coordp;;||atv;Z;45.0
    """
    if obj.initgeom():
        geom = obj.geom_v
        npt = geom.npt
        if npt == 1:
            angle = geom.angle
            pt1 = list(geom.coords)[0]
            pt2 = None
        elif npt == 2:
            pt1, pt2 = list(geom.coords)[:2]
            angle = calculeangle(pt1, pt2)
            longueur = geom.longueur
        elif regle.ip1 is not None:
            tmp = list(geom.coords)
            pt1 = tmp[regle.ip1]
            pt2 = tmp[regle.ip2]
            angle = calculeangle(pt1, pt2)
            longueur = geom.longueur
        else:
            # print('calcul angle rectangle')
            ror = r_orient(geom)
            longueur = geom.longueur
            if isinstance(ror, SG.Polygon):
                pt1, pt2, pt3, pt4 = list(ror.exterior.coords)[:4]
                # print('coordonnées',ror.exterior.coords)
                angle = (calculeangle(pt1, pt3) + calculeangle(pt4, pt2)) / 2
                pt2 = pt3
            elif isinstance(ror, SG.LineString):  # cas du rectangle degénéré
                pt1, pt2 = list(ror.coords)[:2]
                angle = calculeangle(pt1, pt2)
            else:  # cas de 3 points identiques: ne devrait pas exister
                angle = 0
                return False
        if regle.params.cmp2 and pt2 is not None:
            geom.setpoint(
                [(i + j) / 2 for i, j in zip(pt1, pt2)],
                dim=len(pt1),
                angle=angle,
                longueur=longueur,
            )
            setschemainfo(regle, obj, multi=False, type="1", dyn=True)

        regle.setval_sortie(obj, str(angle))
        return True


def h_buffer(regle):
    """calcul d'un buffer"""
    regle.resolution = int(regle.getvar("resolution", 16))
    regle.cap_style = int(regle.getvar("cap_style", 1))
    regle.join_style = int(regle.getvar("join_style", 1))
    regle.mitre_limit = float(regle.getvar("mitre_limit", 5.0))
    regle.limite = regle.params.cmp1.num
    regle.largeur = (
        regle.params.val_entree.num if regle.params.att_entree.val == "" else 0
    )


def calcul_db(geom, regle, largeur):
    buffer = geom.buffer(
        largeur,
        resolution=regle.resolution,
        cap_style=regle.cap_style,
        join_style=regle.join_style,
        mitre_limit=regle.mitre_limit,
    )

    aire_courante = buffer.area
    db = geom.buffer(
        largeur + 0.01,
        resolution=regle.resolution,
        cap_style=regle.cap_style,
        join_style=regle.join_style,
        mitre_limit=regle.mitre_limit,
    ).area
    return aire_courante, db - aire_courante


def optimise_buffer_aire(geom, regle, largeur):
    """ calcule un buffer selon l'aire"""
    aire_demandee = geom.area * regle.limite
    ecart_largeur = 1

    while abs(ecart_largeur) > 0.001:
        aire_courante, da = calcul_db(geom, regle, largeur)
        ecart_aire = aire_demandee - aire_courante
        ecart_largeur = ecart_aire / (da * 100)
        largeur = largeur + ecart_largeur
        # print ("ecart vb",largeur,ecart_largeur)
        buffer = geom.buffer(
            largeur,
            resolution=regle.resolution,
            cap_style=regle.cap_style,
            join_style=regle.join_style,
            mitre_limit=regle.mitre_limit,
        )
    return buffer, largeur


def f_buffer(regle, obj):
    """#aide||calcul d'un buffer
#parametres1||largeur buffer;attribut contenant la largeur;buffer
#parametres2||buffer;rapport de surface
  #variables||resolution:16,cap_style:1,join_style:1,mitre_limit:5
   #pattern1||?A;?N;?A;buffer;?C;
      #test1||obj;point||^;1;;buffer;;||^X;;;aire||^X;;X;round;||atn;X;3
      #test2||obj;poly||^;1;;buffer;2;||^X;;;aire;||^X;;X;round;||atn;X;2
    """
    if obj.geom_v.sgeom or obj.initgeom():
        sgeom = obj.geom_v.sgeom or obj.geom_v.__shapelygeom__
        largeur = regle.largeur or float(regle.get_entree(obj))
        buffer = sgeom.buffer(
            largeur,
            resolution=regle.resolution,
            cap_style=regle.cap_style,
            join_style=regle.join_style,
            mitre_limit=regle.mitre_limit,
        )
        if regle.limite:
            aire_init = sgeom.area
            if aire_init and buffer.area / aire_init > regle.limite:
                # print("optimisation surface")
                buffer, largeur = optimise_buffer_aire(sgeom, regle, largeur)
        # print ("buffer calcule",buffer)
        obj.geom_v.setsgeom(buffer)
        if regle.params.att_sortie.val:
            setschemainfo(regle, obj, multi=True, type="3", dyn=True)
            regle.setval_sortie(obj, str(largeur))
        else:
            setschemainfo(regle, obj, multi=True, type="3")
        # print ('rectangle',ror )


def h_ingeom(regle):
    """prepare les objets pour l'intersection"""
    regle.objets = regle.stock_param.store.get(regle.params.cmp2.val)
    if not regle.objets:
        regle.erreurs.append(
            "il faut precharger des objets pour une selection geometrique"
        )
        regle.valide = False
        return
    regle.multiple = len(regle.objets) > 1
    if not regle.multiple:
        obj = list(regle.objets.values())[0]
        regle.objref = obj
        if obj.geom_v.valide:
            regle.geomref = obj.geom_v.__shapelyprepared__
        else:
            regle.erreurs.append("l'objet de reference doit avoir une geometrie valide")
            regle.valide = False


def f_ingeom(regle, obj):
    """#aide||recupere des attributs par selection geometrique
    #aide_spec||liste des attributs a recuperer
        #pattern||L;?C;L;geoselect;=in;C
        #pattern2||;;;geoselect;=in;C
        !#test||obj;poly||^;1;;buffer;;||;;;;;;;tmpstore||atv;X;1
        """
    if obj.geom_v.sgeom or obj.initgeom():
        sgeom = obj.geom_v.sgeom or obj.geom_v.__shapelygeom__
        if regle.multiple:
            intersected = False
            for i in regle.objets.values:
                sgp = i.geom_v.__shapelyprepared__
                if sgp.intersects(sgeom):
                    if intersected:
                        o2 = obj.dupplique()
                        regle.setval_sortie(o2, regle.getlist_entree(i))
                        regle.stock_param.traite_objet(o2)
                    regle.setval_sortie(obj, regle.getlist_entree(i))
                    intersected = True
            return intersected
        else:
            return regle.geomref.intersects(sgeom)
    return False
