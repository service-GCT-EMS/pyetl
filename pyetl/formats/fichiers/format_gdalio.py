# -*- coding: utf-8 -*-
""" format geojson en lecture et ecriture"""

import os

printtime = False
if printtime:
    import time

    t1 = time.time()
    print("start gdalio")
from collections import defaultdict, OrderedDict
import itertools

# import fiona
# from fiona.crs import from_epsg

if printtime:
    print("    fiona      ", time.time() - t1)
    t1 = time.time()
from .fileio import FileWriter

if printtime:
    print("    filewriter ", time.time() - t1)
    t1 = time.time()

import fiona
from fiona.crs import from_epsg

# global fiona, from_epsg


# def importer():

#     import fiona
#     from fiona.crs import from_epsg


def formatte_entree(type_orig):
    """cree un formattage d'entree pour la gestion des decimales"""
    format_entree = ""
    dec = None
    taille = None
    type_att = type_orig
    if ":" in type_orig:
        vv_tmp = type_orig.split(":")
        type_att = vv_tmp[0]
        taille = vv_tmp[1]
        if "." in taille:
            vv_tmp = taille.split(".")
            taille = vv_tmp[0]
            dec = vv_tmp[1]

    if type_att == "float" or type_att == "F":
        if dec == "0":
            type_att = "long" if taille is not None and int(taille) >= 10 else "int"
    # print( 'traitement shapefile', type_orig,'->',type_att, taille, dec)

    return type_att, taille, dec


def recup_schema_fiona(schema_courant, ident, description, driver):
    """cree un schema a partir d une description fiona"""
    code_g = {
        "Point": "1",
        "LineString": "2",
        "MultiLineString": "2",
        "Polygon": "3",
        "MultiPolygon": "3",
        "None": "0",
    }
    types_a = {
        "str": "T",
        "int": "E",
        "long": "EL",
        "float": "F",
        "datetime": "D",
        "date": "DS",
        "time": "D",
    }
    # print ('recup_schema fiona:', ident, description, schema_courant)
    # sc_classe = schema_courant.get_classe(ident)
    # #    print ('gdalio:recherche schema ',ident, sc_classe, schema_courant.nom,
    # #           schema_courant.classes.keys())
    # if sc_classe:
    #     for nom,desc  in sc_classe.attributs.items():
    #         type_att = desc.type_attribut
    #         taille =desc.taille
    #         dec =desc.dec
    #         type_att, taille ,dec, format_entree = formatte_entree(type_att, driver = driver)
    #         if format_entree:
    #             sc_classe.set_format_lecture(i, format_entree)
    #     return sc_classe
    # if ident in schema_courant.classes:
    #     return schema_courant.classes[ident]

    sc_classe = schema_courant.setdefault_classe(ident)
    multigeom = False
    if "geometry" in description:
        nom_geom = description["geometry"]
        type_geom = code_g.get(nom_geom, "-1")
        dimension = 2
        if "3D " in nom_geom:
            dimension = 3
            nom_geom = nom_geom.split(" ")[1]
            type_geom = code_g.get(nom_geom, "-1")
        if "Multi" in nom_geom or (driver == "ESRI Shapefile" and type_geom > "1"):
            multigeom = True
    else:
        nom_geom = ""
        type_geom = "0"
        dimension = 0
    # print('type geometrique fiona', type_geom, nom_geom)
    sc_classe.stocke_geometrie(
        type_geom, dimension=dimension, srid="3948", multiple=multigeom
    )
    # sc_classe.info["type_geom"] = type_geom
    for i in description["properties"]:
        type_att = description["properties"][i]
        type_att, taille, dec = formatte_entree(type_att)
        sc_classe.stocke_attribut(
            i,
            types_a[type_att],
            # dimension=dimension,
            force=True,
            taille=int(taille) if taille else 0,
            dec=int(dec) if dec else None,
            ordre=-1,
        )
    return sc_classe


def schema_fiona(sc_classe, liste_attributs=None, l_nom=0):
    """cree une description fiona d un schema"""
    nom_g_s = {"1": "Point", "2": "LineString", "3": "Polygon"}
    nom_g_m = {"1": "MultiPoint", "2": "MultiLineString", "3": "MultiPolygon"}
    nom_a = {
        "texte": "str",
        "entier": "int",
        "sequence": "int",
        "entier_long": "str",
        "reel": "float",
        "date": "date",
        "horodatage sans zone": "date",
        "hstore": "str",
    }
    description = dict()
    type_geom = sc_classe.info["type_geom"]
    if type_geom == "indef":
        type_geom = "0"
    if type_geom > "0":
        # nom_geom = nom_g_m[type_geom]
        # print(
        #     "schema_fiona",
        #     sc_classe.nom,
        #     type_geom,
        #     sc_classe.multigeom,
        #     sc_classe.info["courbe"],
        # )
        nom_geom = (
            nom_g_m[type_geom]
            if sc_classe.multigeom or sc_classe.info["courbe"] or type_geom > "1"
            else nom_g_s[type_geom]
        )
        if sc_classe.info["dimension"] == "3":
            nom_geom = "3D " + nom_geom
        description["geometry"] = nom_geom
    elif type_geom == "-1":
        print("geometrie inconnue", sc_classe)
        description["geometry"] = None
    else:
        description["geometry"] = None

    props = OrderedDict()
    description["properties"] = props
    if l_nom:
        sc_classe.use_noms_courts = True
    for i in sc_classe.get_liste_attributs(liste=liste_attributs):
        att = sc_classe.attributs[i]
        if l_nom and att.nom_court:
            nom = att.nom_court
        else:
            nom = att.nom
        nom = sc_classe.minmajfunc(nom)
        # print ("fiona:", sc_classe.nom, " attribut", i, att.nom_court, nom, l_nom)
        if att.conformite:
            att.type_att = "T"
            att.taille = att.conformite.taille if att.conformite.taille else 0
        # graphique="oui" if att.graphique else 'non'
        taille = ""
        type_att = nom_a[att.get_type()]

        if att.taille:
            taille = str(att.taille + 1)
            if att.dec:
                taille = taille + "." + str(att.dec)
        if taille:
            type_att = type_att + ":" + taille
        props[nom] = type_att
    if not props:
        props[sc_classe.minmajfunc("gid")] = "int"
    #    print ("fiona:", sc_classe.nom,description,sc_classe.minmajfunc)
    return description


def lire_objets(self, rep, chemin, fichier):
    """ lecture d'un fichier reconnu et stockage des objets en memoire"""
    # print("lecture gdal", (rep, chemin, fichier), self.schemaclasse)
    #    raise
    # ouv = None
    # importer()
    groupe, classe = self.prepare_lecture_fichier(rep, chemin, fichier)

    layers = fiona.listlayers(self.fichier)
    # print('fiona:lecture niveaux',  layers)
    for layer in layers:
        with fiona.open(self.fichier, "r", layer=layer) as source:
            # print ('recup fiona',self.newschema,source.driver, source.schema)
            if layer != classe:
                self.setidententree(self.groupe, layer)
            if self.newschema:
                self.schemaclasse = recup_schema_fiona(
                    self.schemaclasse.schema,
                    (self.groupe, self.classe),
                    source.schema,
                    source.driver,
                )

            driver = source.driver

            for i in source:
                # print("lecture gdal", i)
                obj = self.getobj()
                obj.from_geo_interface(i)
                obj.attributs["#chemin"] = chemin
                # print ('------gdalio ',obj,'\n')
                self.process(obj)
    return


class GdalWriter(FileWriter):
    """ gestionnaire d'ecriture pour fichiers gdal"""

    def __init__(
        self,
        nom,
        schema=None,
        regle=None,
    ):
        super().__init__(nom, schema=schema, regle=regle)
        # importer()
        self.converter = gdalconverter
        self.layer = ""
        self.transtable = None
        self.buffer = dict()
        self.usebuffer = self.writerparms["usebuffer"]
        self.flush = not self.usebuffer
        self.layerstate = dict()
        self.write = self.bwrite if self.usebuffer else self.swrite
        # print("gdalwriter", self.writerparms, self.write)

    def open(self):
        """ouvre  sur disque"""
        # print("open", self.layer, bool(self.layer))
        if not self.layer:
            return
        crs = from_epsg(int(self.srid))
        l_max = self.writerparms["attlen"]
        if l_max:
            self.schemaclasse.cree_noms_courts(longueur=l_max)
        # self.schemaclasse.minmajfunc = self.minmajfunc
        schema = schema_fiona(
            self.schemaclasse, liste_attributs=self.liste_att, l_nom=l_max
        )
        self.layer = self.schemaclasse.nom
        # print("fiona: ouverture", self.nom, self.layer, self.writerparms)

        self.fichier = fiona.open(
            self.nom,
            "w",
            crs=crs,
            encoding=self.encoding,
            driver=self.writerparms["driver"],
            schema=schema,
            layer=self.layer,
        )
        self.layerstate[self.layer] = 1

    def changeclasse(self, schemaclasse, attributs=None):
        """ change de classe """

        self.liste_att = schemaclasse.get_liste_attributs(liste=attributs)
        if self.ressource.etat == 1:
            self.close()
        _, classe = schemaclasse.identclasse
        # print(
        #     "fiona: changeclasse depuis",
        #     self.nom,
        #     self.layer,
        #     "vers",
        #     classe,
        # )
        self.layer = classe
        # crs = from_epsg(int(self.srid))
        self.schemaclasse = schemaclasse
        # schema = schema_fiona(self.schemaclasse, liste_attributs=self.liste_att, l_nom=self.l_max)
        #        print ('fiona: reouverture' ,self.nom, self.layer)
        if self.layer not in self.layerstate:
            self.open()
        else:
            self.reopen()
        # else:
        #     self.open()

    def reopen(self):
        """reouvre le fichier s'il a ete ferme entre temps"""
        # print("reopen", self.layer, self.ressource.etat)
        crs = from_epsg(int(self.srid))
        l_max = self.writerparms["attlen"]
        schema = schema_fiona(
            self.schemaclasse, liste_attributs=self.liste_att, l_nom=l_max
        )
        self.fichier = fiona.open(
            self.nom,
            "a",
            crs=crs,
            encoding=self.encoding,
            driver=self.writerparms["driver"],
            schema=schema,
            layer=self.layer,
        )
        self.layerstate[self.layer] = 1

    def close(self):
        """fermeture"""
        #        print("fileeio fermeture", self.nom)

        if self.nom == "#print":
            return  # stdout
        try:
            if self.layer in self.layerstate and self.layerstate[self.layer] == 1:
                self.fichier.close()
                self.layerstate[self.layer] = 2
        except AttributeError:
            print(
                "error: fw  : writer close: fichier non defini",
                self.nom,
                self.ressource.etat,
            )

    def set_liste_att(self, liste_att):
        """stocke la liste des attributs a sortir"""
        self.liste_att = self.schemaclasse.get_liste_attributs(
            liste=self.regle.output.liste_att
        )

    def convert(self, obj):
        return self.converter(obj, self.liste_att, self.minmajfunc)

    def flush_buffer(self, ident):
        """ferme definitivement les fichiers"""
        self.flush = True
        self.changeclasse(self.schema.classes[ident])
        # print("ecriture buffer", ident, len(self.buffer[ident]))
        self.fichier.writerecords(self.buffer[ident])
        del self.buffer[ident]
        self.flush = False
        self.close()
        return

    def bwrite(self, obj):
        """ecriture bufferisee"""
        chaine = self.converter(obj, self.liste_att, self.output.minmajfunc)
        if not chaine:
            return False
        # test multi
        ident = obj.ident
        # print("bwrite", ident)
        if ident in self.buffer:
            # print("gdal:bwrite", len(self.buffer[ident]))
            self.buffer[ident].append(chaine)
            if len(self.buffer[ident]) >= 10000:
                self.flush_buffer(ident)
        else:
            self.buffer[ident] = [chaine]
        return True

    def swrite(self, obj):
        """ecrit un objet complet"""
        chaine = self.converter(obj, self.liste_att, self.output.minmajfunc)
        print("gdal:write", chaine)
        try:
            self.fichier.write(chaine)
        except Exception as err:
            print(
                "erreur ecriture",
                obj.ident,
                err,
                "\nliste_att:",
                self.liste_att,
                "\nchaine:",
                chaine,
            )
        return True

    def finalise(self):
        """ferme definitivement les fichiers"""
        if self.buffer:
            self.flush = True
            for ident in self.buffer:
                if self.buffer[ident]:
                    self.changeclasse(self.schema.classes[ident])
                    print("final: ecriture buffer", ident, len(self.buffer[ident]))
                    try:
                        self.fichier.writerecords(self.buffer[ident])
                    except Exception as err:
                        print("-------------------erreur ecriture", err)
                        print(
                            "erreur ecriture",
                            ident,
                            "->",
                            self.schema.classes[ident].info["type_geom"],
                            self.buffer[ident],
                        )
            self.flush = False
            self.buffer = dict()
        self.close()
        return 3


def gdalconverter(obj, liste_att, minmajfunc):
    """convertit un objet dans un format compatible avec la lib gdal"""
    obj.casefold = minmajfunc
    obj.initgeom()
    type_geom = str(obj.geom_v.type_geom)
    if type_geom != "0":
        if obj.schema and type_geom < obj.schema.info["type_geom"]:
            print(
                "erreur type_geom",
                obj.ident,
                type_geom,
                "schema:",
                obj.schema.info["type_geom"],
            )
            return ""
    else:
        if obj.schema.info["type_geom"] != "0":
            return ""
    if str(obj.geom_v.type_geom) > "1" and obj.geom_v.type_geom != "indef":
        obj.set_multi()

    a_sortir = obj.__geo_interface__(liste_att)
    if not a_sortir["properties"]:
        a_sortir["properties"][obj.casefold("gid")] = a_sortir["id"]
    return a_sortir


def init_gdal(output):
    output.writerclass = GdalWriter


def init_gdalb(output):
    init_gdal(output)
    output.writerparms["usebuffer"] = True


#                       reader,      geom,    hasschema,  auxfiles
READERS = {
    "dxf": (lire_objets, None, True, (), None, None),
    "shp": (lire_objets, None, True, ("dbf", "prj", "shx", "cpg", "qpj"), None, None),
    "mif": (lire_objets, None, True, (("mid",)), None, None),
    "gpkg": (lire_objets, None, True, (), None, None),
}

# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {
    "shp": (
        "",
        "",
        True,
        "up",
        10,
        "ESRI Shapefile",
        "classe",
        None,
        "#tmp",
        init_gdal,
    ),
    "mif": (
        "",
        "",
        True,
        "",
        0,
        "MapInfo File",
        "classe",
        None,
        "#tmp",
        init_gdal,
    ),
    "dxf": (
        "",
        "",
        True,
        "",
        0,
        "DXF",
        "classe",
        None,
        "#tmp",
        init_gdal,
    ),
    "gpkg": (
        "",
        "",
        True,
        "",
        0,
        "GPKG",
        "groupe",
        None,
        "#tmp",
        init_gdalb,
    ),
}

if printtime:
    print("     end ", time.time() - t1)
    t1 = time.time()

#########################################################################
