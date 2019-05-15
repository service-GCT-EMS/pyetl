# -*- coding: utf-8 -*-
# formats d'entree sortie
"""gestion des formats d'entree et de sortie. graphiques
"""


import re

# from numba import jit

TOKEN_SPECIFICATION = [
    ("N", r"-?\d+(\.\d*)?"),  # Integer or decimal number
    ("E", r"\)|;"),  # Statement terminator
    ("C", r"[A-Z]* *\("),  # Identifiers
    ("S", r","),
    ("P", r"SRID="),
    ("K", r"[ \t]+|\n"),  # Skip over spaces and tabs
    ("M", r"."),
]  # Any other character
TOK_REGEX = re.compile("|".join("(?P<%s>%s)" % pair for pair in TOKEN_SPECIFICATION))
KEYWORDS = {
    "MULTISURFACE(": "3",
    "MULTIPOLYGON(": "3",
    "POLYGON(": "3",
    "CURVEPOLYGON(": "3",
    "MULTILINESTRING(": "2",
    "MULTICURVE(": "2",
    "COMPOUNDCURVE(": "2",
    "CIRCULARSTRING(": "2",
    "LINESTRING(": "2",
    "POINT(": "1",
    "(": "0",
    "EMPTY":'0',
    "TIN(": "4",
    "POLYHEDRALSURFACE(": "5",
}


def decode_ewkt(code):
    """ decodage du format ewkt avec expressions regulieres"""
    value = []
    liste = []
    zdef = [0.0]
    entite = ""
    dim = 2
    for token in TOK_REGEX.finditer(code):
        kind = token.lastgroup
        if kind == "N":
            value.append(float(token.group(kind)))
        #        elif kind == 'K':
        #            pass
        elif kind == "M":
            raise RuntimeError("%r unexpected on line %s" % (token.group(kind), code))
        elif kind == "S":
            if value:
                liste.append(value if dim == 3 else value + zdef)
                value = []
        elif kind == "E":
            if value:
                liste.append(value if dim == 3 else value + zdef)
                value = []
            yield ("end", entite, dim, liste)
            entite = ""
            liste = []
        elif kind == "C":
            entite = token.group(kind).replace(" ", "")
            if "Z" in entite:
                entite = entite.replace("Z", "")
                dim = 3
            liste = []
            if entite not in KEYWORDS:
                raise RuntimeError("%r inconnu" % (entite))
            yield ("start", entite, dim, liste)
        elif kind == "P":
            entite = "SRID"


def _parse_start(nature, niveau, poly, ring, nbring):
    """demarre un nouvel element"""
    type_geom = "0"
    try:
        tyg = KEYWORDS[nature]
    except KeyError:
        print("------------type geometrique inconnu", nature)
        return "0", None, None, None
    if tyg == "1":
        return "1", None, None, None
    if nature in {"POLYGON(", "CURVEPOLYGON("}:
        type_geom = "3"
        poly = niveau
    elif nature == "COMPOUNDCURVE(":
        if niveau == 1:
            type_geom = "2"
        elif poly:
            ring = niveau
            nbring += 1
    elif nature == "CIRCULARSTRING(":
        if niveau == 1:
            type_geom = "2"
        elif poly and not ring:
            ring = niveau
            nbring += 1
    elif nature == "(":
        if poly and not ring:
            ring = niveau
    else:
        type_geom = tyg
    return type_geom, poly, ring, nbring


def _parse_end(nature, valeurs, dim, nbring, niveau, geometrie):
    """finalise l'element"""
    if nature == "POINT(":
        geometrie.setpoint(valeurs[0], None, dim)
    #                    print ('detecte point ',valeurs[0], 0, dim)
    elif nature == "(":
        geometrie.cree_section(valeurs, dim, 1, 0, interieur=nbring > 1)
    elif nature == "LINESTRING(":
        geometrie.cree_section(valeurs, dim, 1, 0, interieur=nbring > 1)
    elif nature == "CIRCULARSTRING(":
        geometrie.cree_section(valeurs, dim, 1, 1, interieur=nbring > 1)
    elif nature == "SRID":
        niveau += 1  # on compense
        geometrie.setsrid(valeurs[0][0])


def _parse_ewkt(geometrie, texte):
    """convertit une geometrie ewkt en geometrie interne"""
    dim = 2
    niveau = 0
    poly = 0
    ring = 0
    nbring = 0
    type_lu = None
    if not isinstance(texte, str):
        print("geometrie non decodable", texte)
        geometrie.type = "0"
        return
    if not texte:
        print("geometrie vide", texte)
        geometrie.type = "0"
        return
    try:
        for oper, nature, dim, valeurs in decode_ewkt(texte.upper()):
            if oper == "end":
                if poly == niveau:
                    poly = 0
                    nbring = 0
                elif ring == niveau:
                    ring = 0
                niveau -= 1

                _parse_end(nature, valeurs, dim, nbring, niveau, geometrie)

            elif oper == "start":
                dim = valeurs
                niveau += 1
                type_lu, poly, ring, nbring = _parse_start(nature, niveau, poly, ring, nbring)
                geometrie.type = type_lu
    #                if not type_geom:
    #                    print ('erreur decodage', texte, oper, nature, valeurs)
    except RuntimeError as err:
        if 'EMPTY' in texte:
            geometrie.type = "0"
            print("geometrie nulle", texte)
        else:
            geometrie.erreurs.ajout_erreur(err.args)
            print("erreur decodage geometrie", texte)


def geom_from_ewkt(obj):
    """convertit une geometrie ewkt en geometrie interne"""
    geom = obj.attributs["#geom"]
    if geom:
        geom_demandee = obj.schema.info["type_geom"] if obj.schema else "0"
        #        print ('decodage geometrie ewkt ',obj.geom)
        _parse_ewkt(obj.geom_v, geom)
        obj.finalise_geom(type_geom=geom_demandee)
    return obj.geom_v.valide


def _ecrire_coord_ewkt2d(pnt):
    """ecrit un point en 2D"""
    return "%f %f" % (pnt[0], pnt[1])


def _ecrire_coord_ewkt3d(pnt):
    """ecrit un point en 3D"""
    return "%f %f %f" % (pnt[0], pnt[1], pnt[2])


def ecrire_coord_ewkt(dim):
    """ retourne la fonction d'ecriture adequate"""
    return _ecrire_coord_ewkt2d if dim == 2 else _ecrire_coord_ewkt3d


def _ecrire_point_ewkt(point):
    """ecrit un point"""
    if point.coords:
        return (
            "POINT(" + _ecrire_coord_ewkt2d(point.coords[0]) + ")"
            if point.dimension == 2
            else "POINT(" + _ecrire_coord_ewkt3d(point.coords[0]) + ")"
        )
    return ""


def _ecrire_section_simple_ewkt(section):
    """ecrit une section """
    prefix = "("
    ecrire = ecrire_coord_ewkt(section.dimension)
    return prefix + ",".join([ecrire(i) for i in section.coords]) + ")"


def _ecrire_section_ewkt(section, poly):
    """ecrit une section """
    if section.courbe:
        prefix = "CIRCULARSTRING("
    elif poly:
        prefix = "("
    else:
        prefix = "LINESTRING("
    ecrire = ecrire_coord_ewkt(section.dimension)
    #    print('coords objet ')
    #    for i,j in enumerate(section.coords):
    #        print(i,j)
    #    print([i  for i in section.coords])
    return prefix + ",".join([ecrire(i) for i in section.coords]) + ")"


def _ecrire_ligne_ewkt(ligne, poly, erreurs, multiline=False):
    """ecrit une ligne en ewkt"""
    if poly and not ligne.ferme:
        if erreurs is not None:
            erreurs.ajout_erreur("ligne non fermee")
        return ""
    if not ligne.sections:
        if erreurs is not None:
            erreurs.ajout_erreur("ligne vide")
        return ""
    sec2 = [ligne.sections[0]]
    if sec2[0].courbe == 3:
        # print ("cercle")
        sec2[0].conversion_diametre()  # c' est un cercle# on modifie la description
    else:
        # print ('fusion sections',len(ligne.sections))
        for sect_courante in ligne.sections[1:]:  # on fusionne ce qui doit l'etre
            if sect_courante.courbe == sec2[-1].courbe:
                #                print ('fusion ',sect_courante.courbe,sec2[-1].courbe)
                sec2[-1].fusion(sect_courante)
            else:
                #                print ('ajout ',sect_courante.courbe,sec2[-1].courbe)
                sec2.append(sect_courante)
    if len(sec2) > 1:
        return "COMPOUNDCURVE(" + ",".join((_ecrire_section_ewkt(i, False) for i in sec2)) + ")"
    return _ecrire_section_ewkt(sec2[0], poly or multiline)


def _ecrire_multiligne_ewkt(lignes, courbe, erreurs, force_courbe=False):
    """ecrit une multiligne en ewkt"""
    # courbe=True # test courbes
    code = "MULTICURVE(" if courbe or force_courbe else "MULTILINESTRING("
    return code + ",".join((_ecrire_ligne_ewkt(i, False, erreurs, True) for i in lignes)) + ")"


def _ecrire_polygone_ewkt(polygone, courbe, erreurs, multi=False, force_courbe=False):
    """ecrit un polygone en ewkt"""
    if courbe or force_courbe:
        code = "CURVEPOLYGON("
    elif multi:
        code = "("
    else:
        code = "POLYGON("
    return (
        code
        + ",".join((_ecrire_ligne_ewkt(i, True, erreurs, False) for i in polygone.lignes))
        + ")"
    )


def _ecrire_poly_tin(polygones, tin, _):
    """ecrit un tin en ewkt ne gere pas les erreurs """
    if tin:
        code = "TIN("
    else:
        code = "POLYHEDRALSURFACE("

    return (
        code
        + ",".join((_ecrire_section_simple_ewkt(i.lignes[0].sections[0]) for i in polygones))
        + ")"
    )


def _ecrire_multipolygone_ewkt(polygones, courbe, erreurs, force_courbe):
    """ecrit un multipolygone en ewkt"""
    # print 'dans ecrire_polygone',len(polygones)
    # courbe=True # test courbes
    code = "MULTISURFACE(" if courbe or force_courbe else "MULTIPOLYGON("
    return (
        code + ",".join((_ecrire_polygone_ewkt(i, courbe, erreurs, True) for i in polygones)) + ")"
    )


def _erreurs_type_geom(type_geom, geometrie_demandee, erreurs):
    if geometrie_demandee != type_geom:
        if type_geom == "1" or geometrie_demandee == "1":
            if erreurs is not None:
                erreurs.ajout_erreur(
                    "fmt:geometrie_incompatible: demande "
                    + str(type(geometrie_demandee))
                    + str(geometrie_demandee)
                    + " existante: "
                    + str(type_geom)
                    + str(type(type_geom))
                )
            return 1
        if type_geom == "2":
            if erreurs is not None:
                erreurs.ajout_erreur(
                    "fmt:la geometrie n'est pas un polygone demande "
                    + str(geometrie_demandee)
                    + " existante: "
                    + str(type_geom)
                )
                #            raise
            return 1
    else:
        return 0


def ecrire_geom_ewkt(geom, geometrie_demandee="-1", multiple=0, erreurs=None, force_courbe=False):
    """ecrit une geometrie en ewkt"""

    if geometrie_demandee == "0" or geom.type == "0" or geom.null:
        return None

    geomt = ""
    type_geom = geom.type
    geometrie_demandee = geometrie_demandee if geometrie_demandee != "-1" else geom.type

    if _erreurs_type_geom(type_geom, geometrie_demandee, erreurs):
        return None
    courbe = geom.courbe
    if geometrie_demandee == "1":
        geomt = _ecrire_point_ewkt(geom.point)
    elif geometrie_demandee == "2":
        if geom.lignes:
            geomt = (
                _ecrire_multiligne_ewkt(geom.lignes, courbe, erreurs)
                if multiple
                else _ecrire_ligne_ewkt(geom.lignes[0], False, erreurs)
            )
        else:
            if erreurs is not None:
                erreurs.ajout_erreur("pas de geometrie ligne")
            return None
    elif geometrie_demandee == "3":
        if geom.polygones:
            geomt = (
                _ecrire_multipolygone_ewkt(geom.polygones, courbe, erreurs, force_courbe)
                if multiple
                else _ecrire_polygone_ewkt(geom.polygones[0], courbe, erreurs, False, force_courbe)
            )
        else:
            if erreurs is not None:
                erreurs.ajout_erreur("polygone non ferme")
            return None

    elif geometrie_demandee > "3":  # 4: tin  5: polyhedralsurface
        geomt = _ecrire_poly_tin(geom.polygones, geometrie_demandee == "4", erreurs)

    else:
        print("ecrire ewkt geometrie inconnue", geometrie_demandee)
    return geom.epsg + geomt if geomt else None

    # nom:(multiwriter,           streamer,         tmpgeomwriter,


#                 schema, casse, taille, driver, fanoutmax, format geom)


def noconversion(obj):
    """ conversion geometrique par defaut """
    return obj.geom_v.type == "0"


def nowrite(obj):
    """ sans sortie"""
    return ""


GEOMDEF = {"#ewkt": (ecrire_geom_ewkt, geom_from_ewkt), None: (nowrite, noconversion)}
