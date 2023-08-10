# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de manipulation de geometries shapely
"""
# import re
import math as M
from shapely import geometry as SG
from operator import add
from functools import reduce
from .traitement_geom import setschemainfo

# print("demarrage module shapely")
# ===============================================fonctions du module shapely============================================
# global SG


def r_orient(geom):
    sgeom = geom.sgeom or geom.__shapelygeom__
    return sgeom.minimum_rotated_rectangle


def calculeangle(p1, p2):
    """valeur d'angle en degres"""
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
        obj.geomnatif = False
        setschemainfo(regle, obj, multi=False, type="3")


def h_angle(regle):
    """preparation angle"""
    # from shapely import geometry as SG

    if regle.elements["cmp1"].group(0):
        tmp = regle.elements["cmp1"].group(0).split(":")
        regle.ip1 = int(tmp[0])
        regle.ip2 = int(tmp[1]) if len(tmp) > 1 else -1
    else:
        regle.ip1 = None


def f_angle(regle, obj):
    """#aide||calcule un angle de reference de l'objet
    #pattern||S;;;angle;?N:N;?=P
    #schema||ajout_attribut
    #test1||obj;poly||^Z;;;angle;;||atv;Z;0.0
    #test2||obj;poly||^Z;;;angle;;P||^;;;coordp;;||atv;#x;0.5
    #test3||obj;ligne||^Z;;;angle;;P||^;;;coordp;;||atv;#y;0.5
    #test4||obj;ligne45||^AA;;;angle;;||atv;AA;45.0
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
    """calcule un buffer selon l'aire"""
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
        largeur = float(regle.entree)
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
        # print("buffer calcule", buffer)
        obj.geom_v.setsgeom(buffer)
        obj.geom_v.shapesync()
        # print("obj buffer", obj.geom_v)
        obj.geomnatif = False
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
    """#aide||intersection geometrique par reapport a une couche stockee
     #aide_spec1||l 'objet contenu recupere une liste d attributs de l objet contenant
    #parametres1||attributs recuperes;valeurs recuperees;attributs contenant;;;nom memoire
       #pattern1||?L;?LC;?L;geoselect;=in;C
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


def f_centre(regle, obj):
    """#aide calcule le centroide d un objet
    #pattern1||;;;centre;?=in;;"""
    # print("traitement centre,", obj.geom_v.valide, obj.geom_v)
    if obj.geom_v.valide or obj.initgeom():
        sgeom = obj.geom_v.__shapelygeom__
        if sgeom:
            point = (
                sgeom.representative_point()
                if regle.params.cmp1.val
                else sgeom.centroid
            )
        else:
            point = SG.Point()
        # print("point centre", sgeom, "->", point)
        obj.geom_v.setsgeom(point)
        obj.geomnatif = False
        setschemainfo(regle, obj, multi=False, type="1")
    return True


def geomerge_traite_liste(regle, objlist):
    """fusionne les geometries d une liste et retourne un objet"""
    if not objlist:
        return
    objref = objlist[0].dupplique()
    geoms = [obj.geom_v.__shapelygeom__ for obj in objlist]
    merged = regle.gmerge(geoms)
    # print("fusion geom", merged)

    objref.geom_v.setsgeom(merged)
    for attname, func in regle.traitement_attributs:
        objref.attributs[attname] = func([obj.get(attname, "") for obj in objlist])
    # print("recup objref", objref)
    regle.stock_param.moteur.traite_objet(objref, regle.branchements.brch["gen"])


def geomerge_traite_stock(regle):
    """traite les objets stockes dans la regle"""
    if regle.nbstock == 0:
        return
    if regle.seq:
        objlist = regle.liste
        geomerge_traite_liste(regle, objlist)
        regle.liste = []
        regle.nbstock = 0
        return
    for clef in regle.tmpstore:
        objlist = regle.tmpstore[clef]
        geomerge_traite_liste(regle, objlist)
        regle.tmpstore[clef] = []
    regle.nbstock = 0


def h_geomerge(regle):
    """fusionne des objets"""
    attmerge = {
        "add": lambda x: reduce(add, x),
        "set": set,
        "list": lambda x: x,
        "min": min,
        "max": max,
        "first": lambda x: x[0],
        "last": lambda x: x[-1],
    }
    regle.setsgeom = False
    if regle.params.cmp2.val == "union" or not regle.params.cmp2.val:
        from shapely.ops import unary_union

        regle.setsgeom = True
        regle.gmerge = unary_union
    elif regle.params.cmp2.val == "intersect":
        regle.setsgeom = True
        regle.gmerge = lambda x: reduce(lambda a, b: a.intersection(b), x)
    elif regle.params.cmp2.val == "first":
        regle.gmerge = lambda x: x[0]
    elif regle.params.cmp2.val == "last":
        regle.gmerge = lambda x: x[-1]

    regle.store = True
    regle.traite_stock = geomerge_traite_stock
    regle.final = True
    regle.nbstock = 0
    regle.tmpstore = dict()
    regle.clef = None
    regle.liste = []
    regle.keydef = set(regle.params.att_entree.liste)
    alist = regle.params.att_sortie.liste
    mergefuncs = [attmerge.get(i, attmerge["list"]) for i in regle.params.cmp1.liste]
    if len(mergefuncs) < len(alist):
        mergefuncs.extend([attmerge["list"]] * (len(alist) - len(mergefuncs)))
    regle.traitement_attributs = zip(alist, mergefuncs)
    regle.seq = regle.istrue("seq")
    regle.ordre = regle.getvar("order")


def f_geomerge(regle, obj):
    """#aide||fusionne des objets adjacents de la meme classe en fonction de champs communs
    #parametres||champs a accumuler;;champs clef;;fonctions d'accumulation;traitement geometrique
    #pattern2||?L;;?L;geomerge;?LC;?C
    """
    clef = tuple((obj.attributs.get(i, "") for i in regle.params.att_entree.liste))
    if obj.geom_v.valide or obj.initgeom():
        if regle.seq:
            if regle.clef == clef:
                regle.liste.append(obj)
                regle.nbstock += 1
            else:
                if regle.nbstock:
                    geomerge_traite_stock(regle)
                regle.liste.append(obj)
                regle.clef = clef
        else:
            if clef in regle.tmpstore:
                regle.tmpstore[clef].append(obj)
            else:
                regle.tmpstore[clef] = [obj]
            regle.nbstock += 1
        return True
    return False
