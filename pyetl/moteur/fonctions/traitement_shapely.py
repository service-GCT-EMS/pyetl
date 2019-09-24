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
    sgeom = geom.__shapelygeom__
    return sgeom.minimum_rotated_rectangle


def calculeangle(p1, p2):
    """ valeur d'angle en degres"""
    angle = M.atan2(p2[0] - p1[0], p2[1] - p1[1]) * 180 / M.pi
    return angle


def f_rectangle_oriente(regle, obj):
    """#aide||calcul du rectangle oriente minimal
    #pattern||;;;r_min;;
      #test2||obj;poly||^;;;r_min;;||;has:geomV;;;X;1;;set||atv;X;1
    """
    if obj.initgeom():
        sgeom = r_orient(obj.geom_v)
        obj.geom_v.setsgeom(sgeom)
        setschemainfo(regle, obj, multi = False, type = '3')
        # print ('rectangle',ror )


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
    #aide_spec||N:N indices des pointsd a utiliser, P creation d'un point au centre
    #pattern||S;;;angle;?N:N;?=P
    #test1||obj;poly||^Z;;;angle;;||atv;Z;0.0
    #test2||obj;poly||^Z;;;angle;;P||^X,Y;;;coordp;;||atv;X;0.5
    #test3||obj;ligne||^Z;;;angle;;P||^X,Y;;;coordp;;||atv;Y;0.5
    #test4||obj;ligne45||^Z;;;angle;;P||^X,Y;;;coordp;;||atv;Z;-45.0
    """
    if obj.initgeom():
        geom = obj.geom_v
        npt = geom.npt
        if npt == 1:
            angle = geom.angle
            pt1 = list(geom.coords)[0]
            pt2=None
        elif npt == 2:
            pt1, pt2 = list(geom.coords)[:2]
            angle = calculeangle(pt1, pt2)
            longueur=geom.longueur
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
            elif isinstance(ror, SG.LineString): # cas du rectangle degénéré
                pt1, pt2 = list(ror.coords)[:2]
                angle = calculeangle(pt1, pt2)
            else: # cas de 3 points identiques: ne devrait pas exister
                 angle = 0
                 return False
        if regle.params.cmp2 and pt2 is not None:
            geom.setpoint(
                [(i + j) / 2 for i, j in zip(pt1, pt2)], dim=len(pt1), angle=angle, longueur=longueur
            )
            setschemainfo(regle, obj, multi = False, type = '1')

        regle.fstore(regle.params.att_sortie, obj, str(angle))
        return True


def h_buffer(regle):
    """calcul d'un buffer"""
    regle.resolution = int(regle.getvar("resolution", 16))
    regle.cap_style = int(regle.getvar("cap_style", 1))
    regle.join_style = int(regle.getvar("join_style", 1))
    regle.mitre_limit = float(regle.getvar("mitre_limit", 5.0))
    regle.limite = regle.params.cmp1.num


def optimise_buffer_aire(geom, regle):
    """ calcule un buffer selon l'aire"""
    aire_ref = geom.aire
    aire_demandée = aire_ref * regle.limite
    aire_courante = aire_ref
    vb = 0.1
    buffer = geom.buffer(
        vb, regle.resolution, regle.cap_style, regle.join_style) #, regle.mitre_limit)

    aire_courante = buffer.aire
    dvb = vb * (aire_courante / aire_ref - regle.limite)
    while dvb > 0.01:
        vb = vb + dvb
        buffer = geom.buffer(
            vb, regle.resolution, regle.cap_style, regle.join_style, regle.mitre_limit
        )
        dvb = vb * (aire_courante / aire_ref - regle.limite)
    return buffer, vb


def f_buffer(regle, obj):
    """#aide||calcul d'un buffer
    #pattern||;C;?A;buffer;?C;
      #test||obj;poly||^;1;;buffer;;||;has:geomV;;;X;1;;set||atv;X;1
    """
    if obj.initgeom():
        sgeom = obj.geom_v.__shapelygeom__
        buffer = sgeom.buffer(
            float(regle.get_entree(obj)),
            regle.resolution,
            regle.cap_style,
            regle.join_style) #,regle.mitre_limit,)
        if regle.limite:
            aire_init = sgeom.area
            if buffer.area / aire_init < regle.limite:
                buffer, largeur = optimise_buffer_aire(sgeom, regle)
        print (buffer)
        obj.geom_v.setsgeom(buffer)
        setschemainfo(regle, obj, multi=True, type='3')
        # print ('rectangle',ror )
