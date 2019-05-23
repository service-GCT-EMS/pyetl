# -*- coding: utf-8 -*-
""" lecture du format geocity """

# test de lecture de fichiers geocity depuis fme
# modif pour la lecure de classes réseau
# modif pour la lecture de partitions et la lecture de classes complexes
# modif 17 05 2010 pour lecture trous de partition
# passage des lignes en multicurve pour etre conforma apic
# modif pour suppression des geometrytraits qui ont l'air d'avoir des effets de bord
# modif pour lire la topologie de reseau
# modif pour lire des geometries 2.5 D
# ajout break sur F pour fin de fichier
#       ( evite un plantage si f est le dernier caractere du fichier)
# remise en place des traits
# adaptation pour lecture dans pyetl
import math as M
import os
import logging
from pyetl.schema.fonctions_schema import valide_dates

LOGGER = logging.getLogger("pyetl")


def calculeangle(p1_x, p1_y, p2_x, p2_y):
    """ valeur d'angle a la mode geocity"""
    angle = -M.atan2(p2_x - p1_x, p2_y - p1_y) * 180 / M.pi + 90
    return angle if angle > 0 else angle + 360


def gyr(fich):
    """iterateur sur le fichier avec suppression des newlines non significatifs"""
    iter_fich = (v for line in fich for v in line.split("|") if v != "\n")
    for i in iter_fich:
        if i and i[-1] == "\n":
            i = i[:-1] + next(iter_fich)
        #        print ('iter',i)
        yield i


def consomme(iter_fich, nb_elts):
    """ avance l'iterateur de n tokens """
    # print ('lecture_gy ',it)
    for _ in range(nb_elts):
        next(iter_fich)


def numconv(iter_fich):
    """ retourne un entier """
    return int(next(iter_fich)) / 1000.0


def nc2(iter_fich):
    """ retourne un reel """
    return float(next(iter_fich))


def sens_reseau(noeud):
    """ retourne le type de noeud (debut ou fin) """
    idnoeud = int(noeud)
    clef = "D" if idnoeud > 0 else "A"
    return clef, str(abs(idnoeud))


def coorderror(obj):
    """ affiche une erreur de coordonnees dans un fichier """
    LOGGER.error("gy: erreur coordonnees dans le fichier geocity")
    LOGGER.error("gy: objet rejeté: " + repr(obj))


def lire_objets_reseau(iter_gy, reseau, chemin, regle, getobj):
    """ lit les elements de topologie reseau """
    total = 0
    debut = next(iter_gy)
    liste_obj = []
    stock_param = regle.stock_param
    traite_objet = stock_param.moteur.traite_objet
    for courant in iter_gy:
        if courant == "F":
            print("fin_fichier ")
        total += 1
        if courant == debut:  # fin de noeud
            clef1, noeud1 = sens_reseau(courant)

            for rel in liste_obj:
                obj = getobj(niveau=reseau, classe=stock_param.fichier_courant)  # cree un objet
                obj.attributs["_porteur"] = noeud1
                obj.attributs["_relation_porteur"] = clef1
                clef2, noeud2 = sens_reseau(rel)

                obj.attributs["_cible"] = noeud2
                obj.attributs["_relation_cible"] = clef2
                obj.attributs["#chemin"] = chemin
                obj.setorig(total)
                traite_objet(obj, regle)
                total += 1
            liste_obj = []
            debut = next(iter_gy)
        else:
            liste_obj.append(courant)
    return total - 1


def gestion_types_geocity(description):
    """ convertit les types de geocity en types internes"""
    if not description:
        return "T"
    elif "entier" in description:
        type_a = "E"
    elif "reel" in description:
        type_a = "F"
    elif "texte" in description:
        type_a = "T"
    elif "date_heure" in description:
        type_a = "D"
    else:
        print("type inconnu", description)
        type_a = "T"
    # if 'enumeration' in description: #type enumere
    return type_a


def prepare_liste_attributs(classe_courante, attr, iter_gy):
    """adapte la liste des attributs a des classes réseau"""
    suite = next(iter_gy)
    attsup = ""
    atttop = ""
    ast = ""
    if suite.isdigit():
        nbattr = int(suite)
    else:  # on est en presence d'une classe reseau
        consomme(iter_gy, 3)
        top = next(iter_gy)
        if top == "AT":
            atttop = "_idreseau"  # reseau avec topologie
            attsup = "_sens"
        if top == "ST":
            ast = "_idreseau"
            attsup = "_sens"
        nbattr = int(next(iter_gy))  # nombre d'attributs
    if ast:
        attr.append(ast)  # attribut l'identifiant topologique reseau
    for _ in range(nbattr - 1):  # creation de la liste des attributs
        nom_attr = next(iter_gy)
        attr.append(nom_attr)
        type_attribut = gestion_types_geocity(next(iter_gy))
        classe_courante.stocke_attribut(nom_attr, type_attribut, defaut="", type_attr_base="T")
    if atttop:
        attr.append(atttop)  # attribut l'identifiant topologique reseau
    if attsup:
        attr.append(attsup)  # attribut pour le sens d'un reseau
    #####debug####self.logger.log("attributs" + suite ,0)
    nom_geom = next(iter_gy)
    if nom_geom != "geometrie":
        attr.append(nom_geom)
        type_attribut = gestion_types_geocity(next(iter_gy))
        classe_courante.stocke_attribut(nom_geom, type_attribut, defaut="", type_attr_base="T")
        alpha = 1
        classe_courante.info["type_geom"] = "0"
        consomme(iter_gy, 2)
    else:
        consomme(iter_gy, 3)
        alpha = 0
    return alpha, attsup, atttop or ast


def gestion_noeuds(obj, attr, attsup, iter_gy, unit):
    """ gestion des noeuds de reseau """
    obj_ouvert = 1
    if not attsup:  # c'ext un point
        tk1 = next(iter_gy)
        # print ('test noeud point',t1)

        if tk1 == "1":
            # print ('mode noeud point')
            obj.attributs["#type_reseau"] = "noeud"
            obj.geom_v.setpoint([numconv(iter_gy), numconv(iter_gy)], None, 2)
            obj.infogeom()
            obj_ouvert = 0
            return obj_ouvert, attsup
    tk1 = next(iter_gy)
    if int(tk1) > 10000:  # on tape dans les coordonnees : c'est un point
        # print ('passage en mode noeud point')
        attr.pop()  # on enleve l'attribut sens de la liste des attributs
        del obj.attributs["_sens"]  # on rattrape le premier objet
        obj.attributs["#type_reseau"] = "noeud"
        obj.geom_v.setpoint([int(tk1) / unit, numconv(iter_gy)], None, 2)
        obj.infogeom()
        obj_ouvert = 0
        attsup = ""
        return obj_ouvert, attsup

    obj.attributs["#type_reseau"] = "arc"
    # print ('mode arc,lecture type reseau:',t1)
    if tk1 == "0":  # arc non orienté
        obj.attributs["#sens_reseau"] = "0"

    elif tk1 == "1":
        tk2 = next(iter_gy)
        if tk2 == "1":
            obj.attributs["#sens_reseau"] = "1"  # direct
        elif tk2 == "0":
            obj.attributs["#sens_reseau"] = "-1"  # inverse
        else:  # noeud de reseau
            obj.attributs["#type_reseau"] = "noeud"
            obj.geom_v.setpoint([int(tk2) / unit, numconv(iter_gy)], None, 2)
            obj.infogeom()
            obj_ouvert = 0
            return obj_ouvert, attsup
    elif tk1 == "2":  # point orienté
        #####debug####self.logger.log("pt_orienté",0) #*debug______
        obj.attributs["#type_reseau"] = "noeud"

        cx1, cy1 = numconv(iter_gy), numconv(iter_gy)
        cx2, cy2 = numconv(iter_gy), numconv(iter_gy)
        longueur = M.sqrt((cx2 - cx1) * (cx2 - cx1) + (cy2 - cy1) * (cy2 - cy1))
        obj.geom_v.setpoint([cx1, cy1], calculeangle(cx1, cy1, cx2, cy2), 2, longueur=longueur)
        obj.infogeom()

        obj_ouvert = 0
        return obj_ouvert, attsup

    elif tk1 == "4":  # noeud surfacique
        obj.schema.info["type_geom"] = "3"
        obj.attributs["#type_geom"] = "3"
        obj.attributs["#type_reseau"] = "noeud"
    return obj_ouvert, attsup


def setpoint2d(obj, iter_gy, regle):
    """ enregistre un point 2d """
    try:
        obj.geom_v.setpoint([numconv(iter_gy), numconv(iter_gy)], None, 2)
        obj.infogeom()
        if obj.schema.amodifier(regle):
            obj.schema.info["type_geom"] = "1"
        regle.stock_param.moteur.traite_objet(obj, regle)
    except ValueError:
        coorderror(obj)
    return 0


def setpoint3d(obj, iter_gy, regle):
    """ enregistre un point 3d """
    try:
        obj.geom_v.setpoint([numconv(iter_gy), numconv(iter_gy), numconv(iter_gy)], None, 3)
        obj.infogeom()
        if obj.schema.amodifier(regle):
            obj.schema.info["type_geom"] = "1"
        regle.stock_param.moteur.traite_objet(obj, regle)
    except ValueError:
        coorderror(obj)
    return 0


def addpoints2d(obj, iter_gy, npts, type_geom=None, regle=None):
    """ajoute des points 2d a un objet"""
    for _ in range(npts):
        obj.geom_v.addpoint([numconv(iter_gy), numconv(iter_gy)], 2)
    if type_geom:
        obj.finalise_geom(type_geom=type_geom)
        if obj.schema.amodifier(regle):
            obj.schema.info["type_geom"] = type_geom
        regle.stock_param.moteur.traite_objet(obj, regle)
        return 0
    return 1


def addpoints25d(obj, iter_gy, valz, npts, dimension, type_geom=None, regle=None):
    """ajoute des points 2.5 d ou 2d a un objet"""
    for _ in range(npts):
        obj.geom_v.addpoint([numconv(iter_gy), numconv(iter_gy), valz], dimension)
    if type_geom:
        obj.finalise_geom(type_geom=type_geom)
        if obj.schema.amodifier(regle):
            obj.schema.info["type_geom"] = type_geom
        regle.stock_param.moteur.traite_objet(obj, regle)
        return 0
    return 1


def addpoints3d(obj, iter_gy, npts, type_geom=None, regle=None):
    """ajoute des points 3d a un objet"""
    for _ in range(npts):
        obj.geom_v.addpoint([numconv(iter_gy), numconv(iter_gy), numconv(iter_gy)], 3)
    if type_geom:
        obj.finalise_geom(type_geom=type_geom)
        if obj.schema.amodifier(regle):
            obj.schema.info["type_geom"] = type_geom
        regle.stock_param.moteur.traite_objet(obj, regle)
        return 0
    return 1


def _cotation(iter_gy, obj):
    """gere les objets cotation"""
    # stockage des attributs
    for att_cont in range(20):
        obj.attributs["#_cote_" + str(att_cont)] = next(iter_gy)
        # print ('#_cote_'+str(ac),'->', obj.attributs['#_cote_'+str(ac)])
    #    obj.geom_v.type = '2'                  # ligne
    #    dimension = 2
    #    dimcoord = 2
    #    valz = 0
    npts = int(obj.attributs["#_cote_12"])
    addpoints2d(obj, iter_gy, npts, type_geom="2")

    obj.geom_v.fin_section(1, 0)
    obj.attributs["#_cote_20"] = next(iter_gy)
    obj.finalise_geom(type_geom="2")
    # print ('#_cote_'+str(ac+1),'->', obj.attributs['#_cote_'+str(ac)])
    return 2, 2, 0


def lire_objets_geocity(self, rep, chemin, fichier):
    """boucle de lecture principale -> attention methode de reader"""
    n_obj = 0
    # ouv = None
    regle = self.regle_start
    couleur = "1"
    courbe = 0
    traite_objet = self.regle_ref.stock_param.moteur.traite_objet

    maxobj = self.regle_ref.getvar("lire_maxi", 0)
    codec = self.regle_ref.getvar("codec_entree", "utf8")

    entree = os.path.join(rep, chemin, fichier)
    #    stock_param.racine = rep
    fichier_courant = os.path.splitext(fichier)[0]
    self.fichier_courant = fichier_courant
    obj = None
    with open(entree, "r", 65536, encoding=codec) as ouvert:
        try:
            if ouvert.read(1) != "|":  # fichier non geocity
                return n_obj
        except IOError as err:
            print("erreur de lecture du fichier ", entree, err)
            return n_obj

        except UnicodeError as err:
            print("erreur d'encodage", entree, err)
            return n_obj
        iter_gy = gyr(ouvert)
        unit = 1000.0
        #        print ("lecture_fichier ", fichier )
        attr = []
        base = next(iter_gy)
        consomme(iter_gy, 1)
        reseau = next(iter_gy)
        if reseau != "IGN69":  # on est en presence d'un fichier de description reseau
            n_obj += lire_objets_reseau(iter_gy, reseau, chemin, regle, self.getobj)
            return n_obj

        consomme(iter_gy, 9)

        niveau = next(iter_gy)
        classe = next(iter_gy)
        self.setidententree(niveau, classe)
        # on cree les schemas qui vont bien
        if base not in self.schemas:
            self.init_schema(base)
        schema_courant = self.schemas[base]

        classe_courante = schema_courant.def_classe((niveau, classe))
        #        print ('classe_courante', classe_courante)
        alpha, attsup, topo = prepare_liste_attributs(classe_courante, attr, iter_gy)
        obj_ouvert = 0
        # on attaque les objets
        valz = 0
        dimension = 2  # dimension de l'objet resultant
        dimcoord = 2  # nombre de coordonnees par point dans la geometrie
        mode =''
        type_geom =''
        try:
            for val in iter_gy:
                #                print ('gy:lu',val, obj_ouvert,obj)
                if val == "1" and obj_ouvert == 0:  # debut d'objet
                    obj_ouvert = 1
                    mode = "N"
                    n_obj += 1
                    obj = self.getobj()
                    obj.setschema(classe_courante)
                    obj.attributs.update((("#fichier", fichier_courant), ("#chemin", chemin)))
                    obj.setorig(n_obj)
                    if maxobj and n_obj > maxobj:
                        break
                    val_attr = ""
                    #####debug####self.logger.log("debut_objet" ,0)
                    for i in attr:
                        val_attr = next(iter_gy)
                        #####debug####self.logger.log("attrib " + i +":"+ at ,0)

                        if obj.schema.attributs[i].type_att == "D":  # traitement des dates
                            #                            print( 'detecte date', val_attr)
                            err, val_attr = valide_dates(val_attr, "in")
                        obj.attributs[i] = val_attr  # stockage des attributs
                        # if atttop or ast:
                        # print ('attribut' ,i,'->',at)
                    #                if atttop or ast: # on est en présence d'attributs de topologie
                    if topo:  # gestion des classes en  topologie de réseau
                        try:
                            obj_ouvert, attsup = gestion_noeuds(obj, attr, attsup, iter_gy, unit)

                            if obj_ouvert == 0:
                                #                                if obj.schema.amodifier(regle):
                                #                                    obj.schema.info["type_geom"] = obj.attributs['#type_geom']
                                traite_objet(obj, regle)
                        except ValueError:
                            coorderror(obj)
                            obj_ouvert = 0
                    else:
                        obj.attributs["#type_reseau"] = "non_topo"
                    if alpha:  # c'est un objet alpha pur
                        traite_objet(obj, regle)
                        obj.attributs["#type_geom"] = "0"
                        obj_ouvert = 0

                # decodage des geometries
                elif val == "":  # alpha pur
                    obj_ouvert = 0
                    obj.attributs["#type_geom"] = "0"
                    traite_objet(obj, regle)
                elif val == "F":
                    break
                elif obj_ouvert == 0:
                    pass
                    # on attaque la geometrie
                elif val == "1":
                    obj_ouvert = setpoint2d(obj, iter_gy, regle)
                elif val == "31" or val == "51":  # point 3D
                    obj_ouvert = setpoint3d(obj, iter_gy, regle)
                elif val == "2":
                    if mode == "P":
                        pass  # partition
                    else:  # point oriente : converti en ligne
                        obj_ouvert = addpoints2d(obj, iter_gy, 2, type_geom="2", regle=regle)
                elif val == "32":
                    obj_ouvert = addpoints3d(obj, iter_gy, 2, type_geom="2", regle=regle)
                elif val == "52":
                    valz = numconv(iter_gy)
                    obj_ouvert = addpoints25d(
                        obj, iter_gy, valz, 2, dimension=3, type_geom="2", regle=regle
                    )
                elif val == "3":
                    type_geom = "2"  # ligne
                    dimension = 2
                    dimcoord = 2
                    valz = 0
                elif val == "53":  # ligne 2D5
                    type_geom = "2"
                    dimension = 3
                    dimcoord = 2
                    valz = numconv(iter_gy)
                elif val == "33":  # ligne 3d
                    type_geom = "2"
                    dimension = 3
                    dimcoord = 3
                elif val == "4":  # contour
                    type_geom = "3"
                    dimension = 2
                    dimcoord = 2
                    valz = 0
                elif val == "54":  # contour 2D5
                    type_geom = "3"
                    dimcoord = 2  # dimension de lecture
                    dimension = 3
                    valz = numconv(iter_gy)
                elif val == "34":  # contour 3D
                    type_geom = "3"
                    dimcoord = 3  # dimension de lecture
                    dimension = 3

                elif val == "6" or val == "36":  # partition
                    dimcoord = 2
                    dimension = 2
                    if val == "36":
                        dimcoord = 3
                        dimension = 3
                    mode = "P"
                    type_geom = "3"
                elif val == "06":  # trou de partition
                    mode = "P"
                    type_geom = "3"
                elif val == "7":  # mode cotation
                    # stockage des attributs
                    dimension, dimcoord, valz = _cotation(iter_gy, obj)

                elif val == "C3":  # cercle :
                    if dimcoord == 2:
                        addpoints25d(obj, iter_gy, valz, 3, dimension=dimension)
                        consomme(iter_gy, 2)  # jette le 4eme identique au premier
                    else:
                        addpoints3d(obj, iter_gy, 3)
                        consomme(iter_gy, 3)  # jette le 4eme identique au premier
                    obj.geom_v.fin_section(1, "3")

                elif val == "S" or val == "PA" or val == "CO" or val == "E":
                    # spline : on rale et on traite comme une polyligne
                    print(
                        "attention spline ou autre horreur detectee :" + val + " " + self.niveau,
                        self.classe + ":" + "|".join(obj.attributs.values()),
                    )
                    couleur = "1"
                    courbe = 0
                elif val == "PL":
                    couleur = "1"
                    courbe = 0
                elif val == "D":
                    couleur = "0"  # deplacement : on mets le style à 0
                    courbe = 0
                elif val == "FA":
                    obj.geom_v.fin_section(couleur, courbe)
                elif val == "AC":
                    if dimcoord == 2:
                        addpoints25d(obj, iter_gy, valz, 3, dimension=dimension)
                    else:
                        addpoints3d(obj, iter_gy, 3)
                    courbe = 2
                    couleur = "1"
                elif val == "FL":  # ce code n'apparait que pour les brins et les contours complexes
                    if mode == "P":
                        obj.geom_v.fin_section(couleur, 0)  # c'est de la partition
                    else:  # c'est un polygone complexe
                        obj.geom_v.fin_section(couleur, 0)
                elif val == "FG":
                    obj.finalise_geom(type_geom=type_geom, desordre=mode == "P")
                    #                    print ('erreur geometrique', obj.__geo_interface__)

                    if not obj.geom_v.valide:
                        print("erreur geometrique", obj.attributs.get("#erreurs_geometriques"))

                    #                    print ('finalisation',classe, type_geom)
                    if obj.schema.amodifier(regle):
                        obj.schema.info["type_geom"] = type_geom
                    #                    print('gy:objet a traiter ', obj)
                    traite_objet(obj, regle)
                    obj_ouvert = 0
                elif int(val) > 10000:

                    if dimcoord == 2:
                        obj.geom_v.addpoint([int(val) / unit, numconv(iter_gy), valz], dimension)
                        # lecture de coordonnees
                    else:
                        obj.geom_v.addpoint(
                            [int(val) / unit, numconv(iter_gy), numconv(iter_gy)], dimension
                        )
                        # lecture de coordonnees

                else:
                    print("code inconnu " + val + " " + self.niveau, self.classe)
                    obj.debug("valeurs")
        except AttributeError:
            print("ereur lecture fichier", fichier)
            raise

    return n_obj


#                  reader,geom,hasschema,auxfiles
READERS = {"gy": (lire_objets_geocity, None, True, (), None)}
WRITERS = {}
