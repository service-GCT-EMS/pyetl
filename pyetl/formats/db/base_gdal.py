# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:33:53 2016

@author: 89965
acces gdal en mode base de donnees
"""
import os

from pyetl.formats.geometrie.format_ewkt import ecrire_geom_ewkt
import xml.etree.ElementTree as ET
printtime = False
if printtime:
    import time

    t1 = time.time()
    print("start gdal")
from collections import defaultdict, OrderedDict
import itertools
from osgeo import ogr,osr, gdal
gdal.UseExceptions()
from ..fichiers.format_gdal import decode_wkbgeomtyp, formatte_entree

if printtime:
    print(" base gdal      ", time.time() - t1)
    t1 = time.time()

from .database import DbConnect

if printtime:
    print(" dbconnect      ", time.time() - t1)
    t1 = time.time()

from .gensql import DbGenSql

if printtime:
    print(" gensql      ", time.time() - t1)
    t1 = time.time()


# def importer():
#     global fiona, from_epsg
#     import fiona
#     from fiona.crs import from_epsg


def qgisparser(file):
    return


class GdalConnect(DbConnect):
    """connecteur geopackage"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        # if base.endswith(".gpkg"):
        #     code = os.path.splitext(os.path.basename(base))[0]
        #     print("code base", code)
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        # importer()
        self.type_base = "gpkg"
        self.driver=ogr.GetDriverByName('gpkg')
        self.connect()
        self.geographique = True
        self.accept_sql = "no"
        self.curtable = ""
        self.curnb = 0
        self.explicitcommit = False
        self.qgstree = None
        self.enuminfos = dict()
        self.layerinfos = dict()
        self.rastercount= self.getraster()
        self.prepare_complements()
        print ('gdalconnect actif',self,self.connection)
        
    #        self.encoding =

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        print("info : dbacces:connection gdal", self.driver, self.base)
        try:
            self.connection = self.driver.Open(self.base)
            print (self.connection,self.base)
        except Exception as err:
            print(
                "error: gpkg: erreur acces base",
                self.base,err
            )
            raise
        if not self.connection:
            print ('erreur connection', self.base)
            raise StopIteration(1)

        # print("connection réussie", self.type_base)
    def getlayers(self):
        """ lecture de la liste de couches"""
        layerdict=dict()
        print ('couches',self.connection.GetLayerCount())
        for i in range(self.connection.GetLayerCount()):
            layer = self.connection.GetLayerByIndex(i)
            name=layer.GetName()
            layerdict[name]=layer
        return layerdict

    def getraster(self):
        """ determine si un gpkg contient des couches raster"""
        try:
            return self.connection.RasterCount
        except AttributeError:
            return 0

    def get_tables(self):
        """retourne la liste des tables"""
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
            "String": "T",
            "Integer": "E",
            "Integer64": "EL",
            "Real": "F",
            "DateTime": "D",
            "Date": "DS",
            "Time": "D",
        }
        nb=0
        attlist = []
        layers = self.getlayers()
        # print("gdalshema: lecture tables", layers)
        
        groupe = os.path.splitext(os.path.basename(self.base))[0]
        for layername,layer in layers.items():
            # sc_classe = schema_courant.setdefault_classe(ident)
            classe=layername
            ident = (groupe, classe)
            complements = self.layerinfos.get(classe, dict())
            attcomp = complements.get("attributs", dict())
            geomtyp=layer.GetGeomType()
            nom_geom=layer.GetGeometryColumn()
            if not nom_geom:
                nom_geom="geometrie"
            type_geom,multigeom,courbe,dimension,mesure=decode_wkbgeomtyp(geomtyp)
            type_geom=str(type_geom)
            srid=None
            print("---------recup schema gdal",ident,':type geometrique gdal', geomtyp,ogr.GeometryTypeToName(geomtyp), type_geom, nom_geom)
            if type_geom != '100':
                spatialref=layer.GetSpatialRef()
                if spatialref:
                    srid=str(spatialref.GetAttrValue("AUTHORITY", 1))
                    print(ident,':spatialref gdal', spatialref.GetName(),spatialref.AutoIdentifyEPSG(),srid)
                else:
                    print(ident, ':non geometrique')
            if not srid:
                srid = "3948"

            layerDefinition =  layer.GetLayerDefn()
            nb=layer.GetFeatureCount()
            # sc_classe.info["type_geom"] = type_geom
            for i in range(layerDefinition.GetFieldCount()):
                fielddef=layerDefinition.GetFieldDefn(i)
                nom_att =  fielddef.GetName()
                fieldTypeCode = fielddef.GetType()
                fieldType = fielddef.GetFieldTypeName(fieldTypeCode)
                type_att=types_a.get(fieldType,'-1')
                if type_att=="-1":
                    print ("type attribut inconnu",fieldType,fieldTypeCode)
                taille = fielddef.GetWidth()
                dec = fielddef.GetPrecision()
                attlist.append(
                        self.attdef(
                            nom_groupe=groupe,
                            nom_classe=classe,
                            nom_attr=nom_att,
                            alias=complements.get("alias", ""),
                            type_attr=type_att,
                            taille=taille,
                            decimales=dec,
                            enum=complements.get("enum", ""),
                        )
                    )
            if type_geom != "0":
                attlist.append(
                    self.attdef(
                        nom_groupe=groupe,
                        nom_classe=classe,
                        nom_attr=nom_geom,
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
                    nom_geom
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
        "base geopackage",
    ),
}
