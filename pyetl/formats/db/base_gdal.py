# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:33:53 2016

@author: 89965
acces gdal en mode base de donnees
"""
import sys
import os
import xml.etree.ElementTree as ET

printtime = False
if printtime:
    import time

    t1 = time.time()
    print("start_gdal")

from ..fichiers.format_gdalio import formatte_entree

if printtime:
    print(" format gdalio      ", time.time() - t1)
    t1 = time.time()
from .database import DbConnect

if printtime:
    print(" dbconnect      ", time.time() - t1)
    t1 = time.time()
from .gensql import DbGenSql

if printtime:
    print(" gensql      ", time.time() - t1)
    t1 = time.time()


def importer():
    global fiona, from_epsg
    import fiona
    from fiona.crs import from_epsg


def qgisparser(file):
    return


class GdalConnect(DbConnect):
    """connecteur de la base de donnees oracle"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        # if base.endswith(".gpkg"):
        #     code = os.path.splitext(os.path.basename(base))[0]
        #     print("code base", code)
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        importer()
        self.type_base = "gpkg"
        self.connect()
        self.geographique = True
        self.accept_sql = "no"
        self.curtable = ""
        self.curnb = 0
        self.explicitcommit = False
        self.qgstree = None
        self.enuminfos = dict()
        self.layerinfos = dict()
        self.prepare_complements()

    #        self.encoding =

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        # print("info : dbacces:connection sqlite", self.user, "****", self.base)
        try:

            self.connection = fiona.open(self.base)
        except Exception as err:
            print(
                "error: gpkg: utilisateur ou mot de passe errone sur la base gpkg",
                self.base,
            )
            sys.exit(1)
            return None

        # print("connection réussie", self.type_base)

    def get_tables(self):
        """ retourne la liste des tables """
        return list(self.tables.values())

    def prepare_complements(self):
        complements = os.path.splitext(self.base)[0] + ".qgs"
        hascomplement = os.path.isfile(complements)
        if hascomplement:
            # print("complements", hascomplement)
            self.qgstree = ET.parse(complements)
            self.getqgscomplements(complements)

    def getqgscomplements(self, complements):
        """retourne les alias les enums definies dans un fichier qgis pour les tables"""
        qgstree = ET.parse(complements) if complements else None
        if qgstree is None:
            return
        start = qgstree.getroot().find("projectlayers")
        for couche in start.findall("maplayer"):
            layer = couche.find("datasource")
            if layer is not None:
                sourcename = (
                    layer.text.split("=")[1] if "=" in layer.text else layer.text
                )
            aliasdef = couche.find("layername")
            sourcalias = aliasdef.text if aliasdef is not None else ""
            self.layerinfos[sourcename] = {"alias": sourcalias, "attributs": dict()}
            attributs = self.layerinfos[sourcename]["attributs"]
            aliases = couche.find("aliases")
            if aliases is not None:
                for aliasdef in aliases.findall("alias"):
                    attributs[aliasdef.get("field")] = {"alias": aliasdef.get("name")}
            fieldconf = couche.find("fieldConfiguration")
            if fieldconf is not None:
                fields = fieldconf.findall("field")
                for field in fields:
                    nom = field.get("name")
                    editeur = field.find("editWidget")
                    if editeur and editeur.get("type") == "ValueMap":
                        definition = attributs.setdefault(nom, dict())
                        enumname = sourcename + "_" + nom
                        definition["enum"] = enumname
                        for option in editeur.iter("Option"):
                            if option.get("value"):
                                self.enuminfos.setdefault(enumname, []).append(
                                    option.get("value")
                                )

    def get_enums(self):
        for nom in self.enuminfos:
            for num, valeur in enumerate(self.enuminfos[nom]):
                yield [nom, num, valeur, ""]

    def get_attributs(self):
        """description des attributs de la base sqlite
        structure fournie :
            nom_groupe;nom_classe;nom_attr;alias;type_attr;graphique;multiple;\
            defaut;obligatoire;enum;dimension;num_attribut;index;unique;clef_primaire;\
            clef_etrangere;cible_clef;taille;decimales"""
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

        attlist = []

        layers = fiona.listlayers(self.base)
        # print("gdalshema: lecture tables", layers)
        groupe = os.path.splitext(os.path.basename(self.base))[0]
        for layer in layers:
            with fiona.open(self.base, "r", layer=layer) as source:
                # print("recup fiona", source.driver, source.schema)
                description = source.schema
                classe = layer
                ident = (groupe, classe)
                complements = self.layerinfos.get(classe, dict())
                multigeom = False
                if "geometry" in description:
                    nom_geom = description["geometry"]
                    type_geom = code_g.get(nom_geom, "-1")
                    dimension = 2
                    if "3D " in nom_geom:
                        dimension = 3
                        nom_geom = nom_geom.split(" ")[1]
                        type_geom = code_g.get(nom_geom, "-1")
                    if "Multi" in nom_geom:
                        multigeom = True
                else:
                    nom_geom = ""
                    type_geom = "0"
                    dimension = 0

                nb = 0
                attcomp = complements.get("attributs", dict())
                for nom_att in description["properties"]:
                    type_att = description["properties"][nom_att]
                    type_att, taille, dec = formatte_entree(type_att)
                    compdef = attcomp.get(nom_att, dict())
                    attlist.append(
                        self.attdef(
                            nom_groupe=groupe,
                            nom_classe=classe,
                            nom_attr=nom_att,
                            alias=compdef.get("alias", ""),
                            type_attr=types_a[type_att],
                            taille=taille,
                            decimales=dec,
                            enum=compdef.get("enum", ""),
                        )
                    )
                if type_geom != "0":
                    attlist.append(
                        self.attdef(
                            nom_groupe=groupe,
                            nom_classe=classe,
                            nom_attr="geometrie",
                            type_attr=type_geom,
                            dimension=dimension,
                            multiple=multigeom,
                        )
                    )

                nouv_table = [
                    groupe,
                    classe,
                    complements.get("alias", ""),
                    type_geom,
                    dimension,
                    nb,
                    "t",
                    "",
                    "",
                    "",
                    "",
                ]
                self.tables[ident] = nouv_table
        return attlist


class GdalGenSql(DbGenSql):
    """generateur sql"""

    pass


DBDEF = {
    "gpkg": (
        GdalConnect,
        GdalGenSql,
        "file",
        ".gpkg",
        "#ewkt",
        "base sqlite basique",
    ),
}
