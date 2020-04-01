# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de manipulation d'attributs
"""
# import re
import itertools
import math as M
from pyetl.projection import conversion as P
from shapely import geometry as SG


def setschemainfo(regle, obj, multi=None, type=None, dyn=False):
    """ reporte les infos sur le schema en cas de modification de la geometrie """
    obj.attributs["#dimension"] = str(obj.geom_v.dimension)
    tgeom = obj.geom_v.type_geom
    obj.attributs["#type_geom"] = tgeom
    if obj.schema and obj.schema.amodifier(regle, dyn):
        obj.schema.info["dimension"] = str(obj.geom_v.dimension)
        if multi is not None:
            obj.schema.multigeom = multi
        obj.schema.info["type_geom"] = tgeom if type is None else type


def setschemadim(regle, obj, dyn=False):
    """ reporte les infos sur le schema en cas de modification de la geometrie """
    obj.attributs["#dimension"] = str(obj.geom_v.dimension)
    if obj.schema and obj.schema.amodifier(regle, dyn):
        obj.schema.info["dimension"] = str(obj.geom_v.dimension)


def setschema_typegeom(regle, obj, dyn=False):
    """ reporte les infos sur le schema en cas de modification de la geometrie """
    obj.attributs["#type_geom"] = obj.geom_v.type
    if obj.schema and obj.schema.amodifier(regle, dyn):
        obj.schema.info["type_geom"] = obj.geom_v.type


# fonctions de traitement geometrique
# creation de la geometrie vectorielle
def h_initgeom(regle):
    """prepositionne un type geom"""
    if regle.params.cmp1.num:
        regle.setvar("type_geom", regle.params.cmp1.val)
    regle.use_shapely = regle.params.cmp2.val


def f_initgeom(regle, obj):
    """#aide||force l'interpretation de la geometrie
       #pattern||;;;geom;?N;?=S
       #schema||set_geom
       #test||obj;asc||^;;;geom||;has:geomV;;;X;1;;set||atv;X;1
       #test2||obj;asc||^;;;geom;;S||;has:geomV;;;X;1;;set||atv;X;1
    """
    if obj.virtuel:
        return True
    geom_ok = obj.initgeom()
    if regle.use_shapely and geom_ok:
        obj.geom_v.__shapelygeom__
    return geom_ok


# remise a zero de la geometrie (comme si l'objet venait d'etre lu)


def f_resetgeom(_, obj):
    """#aide||annulle l'interpretation de la geometrie
    #pattern||;;;resetgeom;;
     #schema||set_geom
       #test||obj;ligne||^;;;resetgeom||;!has:geomV;;;C1;1;;set||atv;C1;1
    """
    # on fait comme si on avait pas traite la geometrie
    return obj.virtuel or obj.geompending()


# creation de geometries


def cregeompoint(obj, point, srid):
    """cree un point"""
    if point is None:
        return False
    dim = len(point)
    if dim == 2:
        point.append(0.0)
    obj.geom_v.setpoint(point, None, dim)
    if srid:
        obj.geom_v.setsrid(srid)
    return obj.finalise_geom()


def f_setpoint(regle, obj):
    """#aide||ajoute une geometrie point a partir des coordonnes en attribut
 #parametres||defauts;attribut contenant les coordonnees separees par des ,;numero de srid
   #pattern1||;LC;?A;setpoint;?N;
       #test||obj||^;1,2;;setpoint||atv;#type_geom;1
    """
    if obj.virtuel:
        return True
    try:
        #        point = [float(i) for i in obj.attributs.get(regle.params.att_entree.val,\
        #                 regle.params.val_entree.val).split(',')]
        point = list(map(float, regle.getval_entree(obj).split(",")))
    except (ValueError, TypeError):
        #        coords = [i for i in obj.attributs.get(regle.params.att_entree.val,\
        #                 regle.params.val_entree.val).split(',')]
        point = None
        obj.geom_v.setpoint(None, None, 2)
        obj.finalise_geom()
        #        coords = [obj.attributs.get(i, regle.params.val_entree.val)
        #                 for i in regle.params.att_entree.liste]
        #        print('set point : erreur valeurs entree ',coords)
        return False
    #    print ('set point',point)
    cregeompoint(obj, point, regle.params.cmp1.val)
    setschemainfo(regle, obj, multi=False, type="1")
    return True


def f_setpoint_liste(regle, obj):
    """#aide||ajoute une geometrie point a partir des coordonnes en liste
        #aide_spec||N: numero de srid
    #aide_spec2||defauts, liste d' attribut (x,y,z) contenant les coordonnees
       #pattern2||;N?;L;setpoint;?N;
       #test||obj||^;;V1,V2;setpoint||atv;#type_geom;1
    """
    if obj.virtuel:
        return True
    try:
        point = [
            float(obj.attributs.get(i, regle.params.val_entree.val))
            for i in regle.params.att_entree.liste
        ]
    except (ValueError, TypeError):
        #        print('set point : erreur valeurs entree ',
        #              [obj.attributs.get(i, regle.params.val_entree.val)
        #               for i in regle.params.att_entree.liste],
        #              regle.ligne[:-1])
        #        coords = [obj.attributs.get(i, regle.params.val_entree.val)
        #                 for i in regle.params.att_entree.liste]
        obj.geom_v.setpoint(None, None, len(regle.params.att_entree.liste))
        obj.finalise_geom()
        setschemainfo(regle, obj, multi=False, type="1")

        #        coords = [obj.attributs.get(i, regle.params.val_entree.val)
        #                 for i in regle.params.att_entree.liste]
        #        print('set point : erreur valeurs entree ',coords)
        return False
    cregeompoint(obj, point, regle.params.cmp1.val)
    setschemainfo(regle, obj, multi=False, type="1")
    #    print ('creation point',list(obj.geom_v.coords),list(point))
    return True


def f_addgeom(regle, obj):
    """#aide||cree une geometrie pour l'objet
  #aide_spec||N:type geometrique
 #aide_spec1||ex: A;addgeom  avec A = (1,2),(3,3) -> (1,2),(3,3)
 #aide_spec2||  X,Y;addgeom avec X=1,2,3,4 et Y=6,7,8,9 -> (1,6),(2,7),(3,8),(4,9)
   #pattern1||;?C;?A;addgeom;N;||entree
   #pattern2||;?C;?L;addgeom;N;||entree
      #test1||obj||^;(1,2),(3,3);;addgeom;2;||atv;#type_geom;2
      #test2||obj||^;(0,0),(0,1),(1,1),(1,0),(0,0);;addgeom;3;||atv;#type_geom;3
    """
    if obj.virtuel:
        return True
    type_geom = regle.params.cmp1.val
    if type_geom == "1":
        try:
            if len(regle.params.att_entree.liste) > 1:
                point = list(map(float, regle.getliste_entree(obj).split(",")))
            #                point = [float(obj.attributs.get(i, regle.params.val_entree.val))
            #                         for i in regle.params.att_entree.liste]
            else:
                point = list(map(float, regle.getval_entree(obj).split(",")))
        #                point = [float(i) for i in
        #                         obj.attributs.get(regle.params.att_entree.val,
        #                                           regle.params.val_entree.val).split(',')]
        except (ValueError, TypeError):
            print("add geom : erreur valeurs entree ", regle.ligne[:-1])
            return False
        dim = len(point)
        if dim == 2:
            point.append(0.0)
        obj.geom_v.setpoint(point, None, dim)
    else:
        if len(regle.params.att_entree.liste) > 1:
            #            coordonnees = zip(*[obj.attributs.get(i, regle.params.val_entree.val).split(',')
            #                                for i in regle.params.att_entree.liste])
            coordonnees = zip(*[i.split(",") for i in regle.getliste_entree(obj)])
        else:
            coords = regle.getval_entree(obj).replace(" ", "").split("),(")
            coords[0] = coords[0][1:]
            coords[-1] = coords[-1][:-1]
            coordonnees = [i.split(",") for i in coords]
        for vals in coordonnees:
            # print ("stockage point", point)
            try:
                point = [float(i) for i in vals]
            except (ValueError, TypeError):
                print("add geom : erreur valeurs entree ", vals, regle.ligne)
                return False
            dim = len(point)
            if dim == 2:
                point.append(0.0)
            obj.geom_v.addpoint(point, dim)

    obj.finalise_geom(type_geom=type_geom)
    setschemainfo(regle, obj)
    #        print ('addgeom ',obj.attributs['#type_geom'])
    obj.geomnatif = False

    return True


# forcage de types geometriques
def f_force_pt(regle, obj):
    """#aide||transforme un objet en point en recuperant le n eme point
    #aide_spec||les points sont comptes a partir de 0 negatif pour compter depuis la fin
    #aide_spec1||si il n'y a pas de position donnee on prends le centre de l'emprise
       #pattern||;?C;?A;force_pt;;
       #helper||setval
       #test||obj;ligne||^;1;;force_pt||^;0;;coordp;||atn;#y;1
    """
    if obj.virtuel:
        return True
    if not obj.initgeom():
        return False
    if obj.attributs["#type_geom"] == "0":
        return False
    if obj.geom_v.type > "1":
        position = regle.get_entree(obj)
        if position:
            position = int(position)
            try:
                #                print('changement en point ', obj.attributs['#type_geom'])
                obj.geom_v.setpoint(
                    obj.geom_v.getpoint(position),
                    None,
                    int(obj.attributs["#dimension"]),
                )
                obj.finalise_geom()
            #                print('point :', position, list(obj.geom_v.coords),obj.attributs['#type_geom'])
            except ValueError:
                return False
        else:  # pas de position on prends le centroide
            xmin, ymin, xmax, ymax = obj.geom_v.emprise()
            obj.geom_v.setpoint((xmin + xmax) / 2, (ymin + ymax) / 2, None, 2)

    setschemainfo(regle, obj, multi=False, type="1")
    return True


def f_forceligne(regle, obj):  # force la geometrie en ligne
    """#aide||force la geometrie en ligne
       #pattern||;;;force_ligne;;
       #test||obj;poly||^;;;force_ligne||atv;#type_geom;2
       #
    """
    if obj.virtuel:
        return True
    obj.geom_v.forceligne()
    obj.infogeom()
    obj.geomnatif = False
    if obj.attributs["#type_geom"] == "2":
        setschemainfo(regle, obj, type="2")
        return True
    print(
        "force_ligne,erreur conversion type",
        obj.attributs["#type_geom"],
        obj.geom_v.type,
    )
    return False


def f_forcepoly(regle, obj):
    """ force la geometrie en polygone cmp1 peut prender les valeurs :
        ferme : force la fermeture
        si le mode n'est pas ferme des objets non fermes retournent une erreur
       #aide||force la geometrie en polygone
       #pattern||;;;forcepoly;?=force;
       #schema||set_geom
       #test||obj;ligne_fermee||^;;;forcepoly;||atv;#type_geom;3
        """
    if obj.virtuel:
        return True
    if obj.initgeom():
        #        print ('force poly',obj.geom_v.valide,obj.attributs['#type_geom'])
        obj.geom_v.forcepoly(force=regle.params.cmp1.val)
        #        print ('apres force poly',obj.geom_v.valide,obj.attributs['#type_geom'])

        obj.infogeom()
        obj.geomnatif = False
        if obj.attributs["#type_geom"] == "3":
            setschemainfo(regle, obj, type="3")
            return True
        if regle.params.cmp1.val:  # on force donc si ca passe pas on annulle la geom
            #            print ('fpoly: on invalide la geometrie',regle.params.cmp1.val)
            obj.setnogeom()  # on invalide la geometrie
            setschemainfo(regle, obj)
        print(
            "erreurs force poly",
            obj.ido,
            obj.geom_v.valide,
            obj.attributs["#type_geom"],
        )

    return False


def f_force_couleur(regle, obj):
    """#aide||remplace une couleur par une autre
       #pattern||;;;change_couleur;C;C
       #test||obj;asc_c||^;;;change_couleur;2;3||^;;;extract_couleur;3||atv;#points;2
    """
    if obj.virtuel:
        return True
    if obj.initgeom():
        obj.geom_v.forcecouleur(regle.params.cmp1.val, regle.params.cmp2.val)
        obj.geomnatif = False
        return True
    return False


def f_multigeom(regle, obj):
    """#aide||definit la geometrie comme multiple ou non
       #pattern||;N;;multigeom;;
       #test||obj;ligne||^;1;;multigeom;||^V4;multigeom;;info_schema;;||atv;V4;1
    """
    #        if obj.schema:
    if obj.virtuel:
        return True
    obj.schema.multigeom = bool(regle.params.val_entree.num)

    return True


# calculs :


def f_longueur(regle, obj):
    """#aide||calcule la longueur de l'objet
        #pattern||S;;;longueur;;
        #test||obj;ligne||^#len;;;longueur||atn;#len;1
    """
    #    if True:
    if obj.virtuel:
        return False
    if obj.initgeom():
        regle.setval_sortie(obj, str(obj.geom_v.longueur))
        return True
    return False


def f_aire(regle, obj):
    """#aide||calcule l'aire de l'objet
        #pattern||S;;;aire;;
        #test||obj;poly||^#aire;;;aire||atn;#aire;1
    """
    #    if True:
    if obj.virtuel:
        return False
    if obj.geom_v.sgeom or obj.initgeom():
        regle.setval_sortie(obj, str(obj.geom_v.area))
        return True
    return False


def f_coordp(regle, obj):
    """#aide||extrait les coordonnees d'un point en attributs
  #aide_spec||les coordonnees sont sous #x,#y,#z
    #pattern||?M;?N;?A;coordp;;
     #helper||setval
       #test||obj;ligne||^;1;;coordp||atn;#y;1
       #test1||obj;point||^;0;;coordp||atn;#y;2
       #test2||obj;point||^;;;coordp||atn;#y;2
    """
    if obj.virtuel:
        return False
    if obj.initgeom():
        if obj.attributs["#type_geom"] == "0" or obj.geom_v.null:
            return False
        position = regle.get_entree(obj)
        if not position:
            position = 0
        else:
            position = int(position)

        try:
            # refpt = list(obj.geom_v.coords)[position]
            refpt = list(obj.geom_v.coords)[position]
            # print("coordp: ",list(obj.geom_v.coords),position,refpt)
            if regle.params.att_sortie.val:
                regle.setval_sortie(
                    obj, [str(i) for i in refpt[0 : obj.geom_v.dimension]]
                )
            else:
                obj.attributs.update(
                    zip(
                        ("#x", "#y", "#z"),
                        [str(i) for i in refpt[0 : obj.geom_v.dimension]],
                    )
                )
            return True
        except IndexError:
            return False
    return False


def grille(orig, pas, vmin, vmax):
    """ retourne des intervalles regulier """
    #    print ("detection case",vmin, vmax, orig, pas,
    #           range(int((vmin-orig)/pas),int((vmax-orig)/pas)+1))
    return range(int((vmin - orig) / pas), int((vmax - orig) / pas) + 1)


def grille2(orig, pas, pmin, pmax):
    """ retourne des intervalles regulier """
    #    print ("detection case",vmin, vmax, orig, pas,
    #           range(int((vmin-orig)/pas),int((vmax-orig)/pas)+1))

    grx = range(int((pmin[0] - orig[0]) / pas), int((pmax[0] - orig[0]) / pas) + 1)
    gry = range(int((pmin[1] - orig[1]) / pas), int((pmax[1] - orig[1]) / pas) + 1)
    return list(itertools.product(grx, gry))


def fgrid2(regle, obj, cases, double=True):
    """fonction qui fait le decoupage; on dupplique les objets a cheval"""
    cgx, cgy = cases[0]
    obj.attributs[regle.gx] = str(cgx)
    obj.attributs[regle.gy] = str(cgy)
    #    print ('grille', obj, obj.geom_v, obj.geom_v.emprise())

    if len(cases) > 5:
        xmin, ymin, xmax, ymax = obj.geom_v.emprise()
        print("tres gros objet", len(cases), xmin, ymin, xmax, ymax, obj.ident)
    if double:
        for case in cases[1:]:
            obj2 = obj.dupplique()
            cgx, cgy = case
            obj2.attributs[regle.gx] = str(cgx)
            obj2.attributs[regle.gy] = str(cgy)
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["ok"])
    return True


def h_grid(regle):
    """initialise les parametres de grille"""
    regle.orig_grille = (
        float(regle.params.cmp1.liste[0]),
        float(regle.params.cmp1.liste[1]),
    )
    regle.gx, regle.gy = regle.params.att_sortie.liste


def f_grid(regle, obj):
    """#aide||decoupage en grille
   #aide_pat||code;;;grid;x,y orig;pas
    #pattern||L;;;grid;LC;N
    #test||obj;point;5||^;;V0,V0,V0;translate||^X,Y;;;grid;0.5,0.5;1||^;;;sample-;3;1||atv;X;3
    """
    if obj.virtuel:
        return False
    if obj.initgeom():
        xmin, ymin, xmax, ymax = obj.geom_v.emprise()
        pmin = (xmin, ymin)
        pmax = (xmax, ymax)
        cases = grille2(regle.orig_grille, regle.params.cmp2.num, pmin, pmax)
        fgrid2(regle, obj, cases)
        #    print ('valeur de X', obj.attributs.get('X'))
        return True
    return False


def fgrid(regle, obj, cases):
    """fonction qui fait le decoupage; on dupplique les objets a cheval"""
    obj.attributs[regle.params.att_sortie.val] = str(cases[0])
    #    print ('grille', obj, obj.geom_v, obj.geom_v.emprise())

    if len(cases) > 5:
        xmin, ymin, xmax, ymax = obj.geom_v.emprise()
        print("tres gros objet", len(cases), xmin, ymin, xmax, ymax, obj.ident)
    for case in cases[1:]:
        obj2 = obj.dupplique()
        obj2.attributs[regle.params.att_sortie.val] = str(case)
        regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["ok"])
    return True


def f_gridx(regle, obj):
    """#aide||decoupage grille en x
   #aide_pat||code;;;gridx;origine;pas
    #pattern||A;;;gridx;N;N
    #test||obj;point;5||^;;V0,V0,V0;translate||^X;;;gridx;0.5;1||^;;;sample-;3;1||atv;X;3
    """
    if obj.virtuel:
        return False
    if obj.initgeom():
        xmin, ymin, xmax, ymax = obj.geom_v.emprise()
        fgrid(
            regle, obj, grille(regle.params.cmp1.num, regle.params.cmp2.num, xmin, xmax)
        )
    #    print ('valeur de X', obj.attributs.get('X'))
    return True


def f_gridy(regle, obj):
    """#aide||decoupage grille en x
       #aide_pat||,,,gridx,origine,pas
       #pattern||A;;;gridy;N;N
          #test||obj;point;5||^;;V0,V0,V0;translate||^X;;;gridy;0.5;1||^;;;sample-;3;1||atv;X;4

    """
    if obj.virtuel:
        return False
    if obj.initgeom():
        xmin, ymin, xmax, ymax = obj.geom_v.emprise()
        fgrid(
            regle, obj, grille(regle.params.cmp1.num, regle.params.cmp2.num, ymin, ymax)
        )
    return True


# --------------------------manipulation de la geometrie
#  manipulation de la 3 eme dimension


def f_geom_2d(regle, obj):
    """#aide||passe la geometrie en 2D
       #pattern||;;;geom2D;;
       #test||obj;point3D||^;;;geom2D;||atv;#dimension;2
    """
    #        if obj.is_3d:
    if obj.virtuel:
        return True
    if obj.initgeom():
        if obj.dimension == 3:
            obj.geom_v.set_2d()
            obj.infogeom()
            obj.geomnatif = False
            setschemadim(regle, obj)
        return True
    return False


def f_geom_3d(regle, obj):
    """#aide||passe la geometrie en 2D
       #pattern||;N;?A;geom3D;?C;
       #helper||setval
       #test||obj;point||^;1;;geom3D;||atv;#dimension;3
    """
    if obj.virtuel:
        return True
    if obj.initgeom():
        obj.geom_v.setz(float(regle.get_entree(obj)), force=regle.params.cmp1.val)
        obj.infogeom()
        setschemadim(regle, obj)
        obj.geomnatif = False
        return True
    return False


def h_mod_3d(regle):
    """preparation modif 3D"""
    cond = regle.params.cmp1.val
    if cond:  # test sur les valeurs 3D
        regle.sel3D = regle.params.compilefonc(cond, "z", debug=regle.debug)
    else:
        regle.sel3D = regle.ftrue


def f_mod_3d(regle, obj):
    """#aide||modifie la 3D  en fonction de criteres sur le Z
        #aide_spec|| valeur de remplacement att/val cond cmp1
       #pattern||;N;;mod3D;C;
       #test||obj;point3D||^;5;;mod3D;z==3||^;;;coordp||atn;#z;5
    """
    if obj.virtuel:
        return True
    if obj.initgeom():
        if obj.dimension == 2:
            return False

        select = regle.sel3D
        valeur = float(
            obj.attributs.get(regle.params.att_entree.val, regle.params.val_entree.val)
        )
        #        print("geomv",obj.geom_v.type, list(obj.geom_v.coords))
        for point in obj.geom_v.coords:
            #            print ("select 3D", pt[2], select(pt[2]))

            if select(point[2]):
                point[2] = valeur
        obj.geomnatif = False
        return True


# ----- decoupage
def h_splitcouleur(regle):
    """ ajoute des sorties par couleur """
    regle.liste_couleurs = set(regle.params.cmp1.liste)
    if regle.liste_couleurs:
        for i in regle.liste_couleurs:
            regle.branchements.addsortie(i)
        regle.branchements.addsortie("#autre")
    #    print ('preparation split_couleurs',regle.branchements, regle.liste_couleurs)
    return True


def f_splitcouleur(regle, obj):
    """ #aide||decoupe la geometrie selon la couleur
        #aide_spec||  une liste de couleurs ou par couleur si aucune couleur n'est precisee
        #aide_spec2||  ajoute des sorties par couleur si une liste est donnee
        #pattern||A;;;split_couleur;?LC;
        #test||obj;asc_c||^C;;;split_couleur||cnt;2;
    """
    #    print ('split_couleurs ', regle.params,obj)
    if obj.virtuel:
        return True
    couleurs = regle.liste_couleurs
    if obj.virtuel:
        #            print("objet virtuel")
        return True
    if obj.initgeom():
        geoms = obj.geom_v.split_couleur(couleurs)
    else:

        print(
            "split_couleur,geometrie invalide ",
            obj.ident,
            obj.numobj,
            obj.geom_v.type,
            " ->",
            obj.schema.info["type_geom"],
        )
        if obj.attributs.get("#erreurs"):
            print(obj.attributs.get("#erreurs"))
        return False

    if obj.schema.info["type_geom"] == "3":
        obj.schema.info["type_geom"] = "2"
    obj.geom_v = None
    obj.geomnatif = False

    liste_coul = list(geoms.keys())
    defaut_dest = regle.branchements.brch["ok"]
    for i in liste_coul[1:]:
        obj2 = obj.dupplique()
        obj2.geom_v = geoms[i]
        obj2.finalise_geom(type_geom="2")
        obj2.attributs[regle.params.att_sortie.val] = i
        obj2.infogeom()
        regle.stock_param.moteur.traite_objet(
            obj2, regle.branchements.brch.get(i, defaut_dest)
        )
        # on l'envoie dans la tuyauterie'
    if geoms:
        obj.geom_v = geoms[liste_coul[0]]
        obj.finalise_geom(type_geom="2")
        obj.redirect = liste_coul[0]
        obj.infogeom()
    else:
        print("splitcouleur: attention pas de geometrie", obj)
        #        raise
        obj.setnogeom()
    obj.attributs[regle.params.att_sortie.val] = liste_coul[0] if liste_coul else ""
    return True


def h_extractcouleur(regle):
    """ extrait des couleurs """
    regle.liste_couleurs = set(regle.params.cmp1.liste)
    return True


def f_extractcouleur(regle, obj):
    """ #aide||decoupe la geometrie selon la couleur
        #aide_spec|| ne garde que les couleurs precisees
        #schema||set_geom
        #pattern||;;;extract_couleur;LC;
        #test||obj;asc_c||^;;;extract_couleur;2||atv;#points;2;
    """
    if obj.virtuel:
        return True
    couleurs = regle.liste_couleurs
    if obj.initgeom():
        geom = obj.geom_v.extract_couleur(couleurs)
        obj.geom_v = geom
        obj.geomnatif = False
        if obj.finalise_geom(type_geom="2"):
            setschema_typegeom(regle, obj, dyn=True)
            #            print ('extract_couleur',couleur,obj,list(obj.geom_v.coords))
            return True
        return False
    print(
        "extract_couleur,geometrie invalide ",
        obj.ident,
        obj.numobj,
        obj.geom_v.type,
        " ->",
        obj.schema.info["type_geom"],
    )
    if obj.attributs.get("#erreurs"):
        print(obj.attributs.get("#erreurs"))
    return False


def h_csplit(regle):
    """preparation selection de coordonnees"""
    regle.selcoords = regle.params.compilefonc(regle.params.cmp1.val, "x,y,z")


def crepoint_copie(obj, point, dimension, numero, att_sortie=None):
    """cree un point en duppliquant un objet de reference"""
    obj2 = obj.dupplique()
    obj2.setnogeom(tmp=True)
    obj2.geom_v.setpoint(point, None, dimension)
    obj2.finalise_geom()
    obj2.infogeom()
    if att_sortie:
        obj2.attributs[att_sortie] = str(numero)
    return obj2


def f_csplit(regle, obj):
    """#aide||decoupage conditionnel de lignes en points
       #aide_spec||extrait les points satisfaisant une condition sur les coordonnees
       #aide_spec||expression sur les coordonnes : x y z
       #pattern||?A;;;csplit;C;
       #test||obj;poly||^;;;csplit>;y==1||cnt;2;
       #test1||obj;poly||^;;;csplit;y==1||cnt;3;
    """
    if obj.virtuel:
        return False
    if obj.attributs["#type_geom"] == "0":
        return False
    if obj.initgeom():
        valide = False
        geom = obj.geom_v
        obj.geom_v = None
        npt = 0
        att_sortie = regle.params.att_sortie.val
        for point in geom.coords:
            if regle.selcoords(*point[:3]):
                npt += 1
                obj2 = obj.dupplique()
                obj2.setnogeom(tmp=True)
                obj2.geom_v.setpoint(point, None, geom.dimension)
                obj2.finalise_geom()
                obj2.infogeom()
                if att_sortie:
                    obj2.attributs[att_sortie] = str(npt)
                regle.stock_param.moteur.traite_objet(
                    obj2, regle.branchements.brch["gen"]
                )
                valide = True
        obj.geom_v = geom
        return valide
    return False


def f_splitgeom(regle, obj):
    """#aide||decoupage inconditionnel des lignes en points
       #pattern||?A;;;splitgeom;;
       #test||obj;poly||^;;;splitgeom;;||cnt;6;
       #test1||obj;poly||^;;;splitgeom>;;||cnt;5;
       #test2||obj;poly||^np;;;splitgeom;;||#type_geom;3;;;;;;pass>||^;;;pass||cnt;5;
    """
    if obj.geom_v.type == "0":
        return True
    if obj.initgeom():
        geom = obj.geom_v
        obj.geom_v = None
        att_sortie = regle.params.att_sortie.val
        for npt, point in enumerate(geom.coords):
            obj2 = obj.dupplique()
            obj2.setnogeom(tmp=True)
            obj2.geom_v.setpoint(point, None, geom.dimension)
            obj2.finalise_geom()
            obj2.infogeom()
            if att_sortie:
                obj2.attributs[att_sortie] = str(npt)
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
        obj.geom_v = geom
        return True
    return False


# modification


def f_prolonge(regle, obj):
    """#aide||prolongation de la ligne d'appui pour les textes
    #aide_spec||longueur;[attibut contenant la  longueur];prolonge;code_prolongation
    #aide spec2||code prolongation : 1: debut, 2: fin, 3:  les 2 cotes (11,12,13) chaque segment
       #pattern||;?N;?A;prolonge;?N;
       #test||obj;ligne||^;1;;prolonge;3||^#l;;;longueur||atn;#l;3
    """
    if obj.virtuel:
        return False
    longueur = obj.attributs.get(
        regle.params.att_entree.num, regle.params.val_entree.num
    )
    if obj.initgeom():
        retour = obj.geom_v.prolonge(longueur, regle.params.cmp1.num)
        obj.infogeom()
        #        print("prolonge",obj.geom_v.longueur)
        obj.geomnatif = False
        return retour
    return False


def h_reproj(regle):
    """ initialise la reprojection """
    srid_sortie = {"LL": "900913", "CC48": "3948", "CC49": "3949", "L93": "2154"}
    regle.srid = srid_sortie.get(regle.params.cmp1.val, "")
    # print('reproj srid sortie', regle.srid)
    regle.projection = P.init_proj(
        regle.params.val_entree.val, regle.params.cmp1.val, regle.params.cmp2.val
    )
    if not regle.projection:
        print(" erreur projection ")
        regle.erreurs.append(
            "projection introuvable %s->%s (%s)"
            % (regle.params.val_entree, regle.params.cmp1, regle.params.cmp2)
        )
        regle.valide = False


def f_reproj(regle, obj):
    """#aide||reprojette la geometrie
    #aide_spec||attribut pour la grille utilisee;systeme d'entree;reproj;systeme de sortie;
              ||[grilles personnalisées] NG: pas de grilles cus
       #pattern||?A;C;;reproj;C;?C
       #schema||ajout_attribut
       #test||obj;point||^;LL;;reproj;CC48;NG||^;;;coordp||^#x;;#x;round||atn;#x;1404842
        """
    if obj.virtuel:
        return False
    proj = regle.projection
    grilles = dict()
    if obj.initgeom():
        obj.geom_v.srid = regle.srid
        for pnt in obj.geom_v.coords:
            if isinstance(pnt, tuple):
                print("proj", obj)
            try:
                gril, pnt[0], pnt[1] = proj.calcule_point_proj(pnt[0], pnt[1])
                # print (" projection calculee",gril, pnt[0], pnt[1])
                # print ('apres',obj.geom_v)
            except ValueError:
                print("erreur projection", pnt)
                obj.setnogeom()
                return False
            #        print ('---- projection ',p1,'------>',pnt)
            grilles[gril] = grilles.get(gril, 0) + 1
        #    print ('liste de grilles'), grilles
        if regle.params.att_sortie.val:
            obj.attributs[regle.params.att_sortie.val] = ";".join(grilles.keys())
        obj.geomnatif = False
        return True
    return False


def f_translate(regle, obj):
    """#aide||translate un objet
      #aide_spec||translation d un objet par une liste de coordonnees (dans un attribut)
    #pattern||;?LN;?A;translate;;
    #test||obj;ligne;||^dec;1,1;;set||^;;dec;translate||^;1;;coordp||atn;#x;2

    """
    liste_trans = obj.attributs.get(
        regle.params.att_entree.val, regle.params.val_entree.val
    ).split(",")
    liste_trans = [float(i) for i in liste_trans]
    if len(liste_trans) < 3:
        liste_trans.extend([0, 0, 0])
    if obj.initgeom():
        obj.geom_v.translate(*liste_trans[:3])
        obj.infogeom()
        return True
    return False


def h_translatel(regle):
    """ prepare la fonction translate"""
    if len(regle.params.att_entree.liste) < 3:
        regle.tz = None
    else:
        regle.tx, regle.ty, regle.tz = regle.params.att_entree.liste[:3]
    #    print ("translate",)
    liste1 = [int(i) for i in regle.params.val_entree.liste if i] + [0, 0, 0]
    regle.dx, regle.dy, regle.dz = liste1[:3]


def f_translatel(regle, obj):
    """#aide translate un objet
  #aide_spec||translation d un objet par une liste de coordonnees(liste d attributs)
    #pattern||;?LN;L;translate;;
      #test2||obj;ligne;||^;1,1;;translate||^;1;;coordp||atn;#x;2
    """
    if obj.virtuel:
        return True
    dec_x = float(obj.attributs.get(regle.tx, regle.dx))
    dec_y = float(obj.attributs.get(regle.ty, regle.dy))
    dec_z = float(obj.attributs.get(regle.tz, regle.dz))

    if obj.initgeom():
        obj.geom_v.translate(dec_x, dec_y, dec_z)
        obj.infogeom()
        return True
    return False
