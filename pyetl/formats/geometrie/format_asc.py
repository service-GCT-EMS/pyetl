# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 17:32:23 2019

@author: 89965
"""
import logging

# formats geometriques ######
FC = 1000.0  # ajoute les elements d'entete a un objet
FA = 10.0
LOGGER = logging.getLogger("pyetl")


# asc ###################################################################
def _ecrire_section_asc(sect, numero_courant):
    """ecrit une section en format asc"""
    num_sect = numero_courant[0]
    numero_courant[0] += 1
    if sect.dimension == 2:
        return (
            "1SEC %d, %d, \n" % (num_sect, len(sect.coords))
            + "\n".join(("%d, %d, " % (i[0] * FC, i[1] * FC) for i in sect.coords))
            + " %s,  %d;\n" % (sect.couleur, sect.courbe)
        )
    return (
        "1SEC3D %d, %d, \n" % (num_sect, len(sect.coords))
        + "\n".join(
            ("%d, %d, %d, " % (i[0] * FC, i[1] * FC, i[2] * FC) for i in sect.coords)
        )
        + " %s, %d;\n" % (sect.couleur, sect.courbe)
    )


def _ecrire_ligne_asc(ligne, numero_courant):
    """ecrit une ligne en format asc.
        : suite de sections"""
    return "".join((_ecrire_section_asc(i, numero_courant) for i in ligne.sections))


def ecrire_geom_asc(geom):
    """ecrit une geometrie en format asc.
        : suite de lignes """
    #    print ('asc: nblignes',len(geom.lignes))
    numeros = [1]
    return (
        "".join((_ecrire_ligne_asc(p, numeros) for p in geom.lignes)) if geom.valide else ""
    )


def _get_point(attrib, geometrie):
    """recupere une geometrie de point depuis les attributs"""
    cd_x = attrib.get("#x", 0)
    cd_y = attrib.get("#y", 0)
    cd_z = attrib.get("#z", 0)
    dim = int(attrib.get("#dimension", "2"))
    if not dim:
        if cd_x and cd_y:
            dim = 2
        if cd_z:
            dim = 3
    if dim:
        geometrie.setpoint(
            [float(cd_x), float(cd_y), float(cd_z)],
            float(attrib.get("#angle", 0)),
            int(dim),
        )
    return dim


def geom_from_asc(obj):
    """convertit une geometrie asc en format interne."""
    #    print ('conversion geometrie asc',obj.ido,obj.geom)
    if obj.geom_v.type == "1":  # c'est un point on a deja ce qu il faut
        obj.infogeom()
        return True

    geom_demandee = "-1"
    # s'il y a un schema : on force le type de geometrie demandees
    if obj.schema and obj.schema.schema.origine != "B":
        geom_demandee = obj.schema.info["type_geom"]
    #    print('gfa: geom_demandee',geom_demandee)
    geom_v = obj.geom_v
    dim = 2
    if "#geom" not in obj.attributs:
        if obj.attributs["#type_geom"] == "0":
            return True
        geom_v.erreurs.ajout_erreur("objet_sans_geometrie")
        obj.attributs.update([("#type_geom", "0"), ("#dimension", "2")])
        return False

    for pnt in obj.attributs["#geom"]:
        if pnt.startswith("1SEC"):
            dim = 3 if pnt.find("3D") > 0 else 2
            coords = []
        else:  # on est en presence de coordonnees
            lcrd = pnt.split(",")
            try:
                coord_points = [
                    float(lcrd[0]) / FC,
                    float(lcrd[1]) / FC,
                    float(lcrd[2]) / FC if dim == 3 else 0,
                ]

                coords.append(coord_points)
            except ValueError:
                geom_v.erreurs.ajout_erreur("coordonnees incompatibles " + str(pnt))
                print("error: asc  : coordonnees incompatibles ", pnt)
                geom_v.type = "0"
            if len(lcrd) > dim + 1:  # fin de ligne
                # print l
                try:
                    couleur = lcrd[dim].strip()
                    if couleur != "500":
                        courbe = int(lcrd[1 + dim].replace(";\n", ""))
                        geom_v.cree_section(coords, dim, couleur, courbe)
                #                            geom_v.fin_section(couleur, courbe)
                #                        else: geom_v.annule_section()
                #                    except ImportError:
                except ValueError:
                    geom_v.erreurs.ajout_erreur("valeurs incompatibles " + str(pnt))
                    print("error: asc  : valeurs incompatibles ", lcrd)
                    geom_v.annule_section()
    obj.finalise_geom(orientation="L", type_geom=geom_demandee)
    # print("asc:finalisation geom", obj.attributs["#classe"], obj.dimension)
    # if obj.dimension == 0:
    #     raise

    geom_v.valide = geom_v.erreurs.actif < 2
    return geom_v.valide


GEOMDEF = {"geom_asc": (ecrire_geom_asc, geom_from_asc)}
