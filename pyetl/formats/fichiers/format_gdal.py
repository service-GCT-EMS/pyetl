# -*- coding: utf-8 -*-
""" format geojson en lecture et ecriture"""

import os

from pyetl.formats.geometrie.format_ewkt import ecrire_geom_ewkt

printtime = False
if printtime:
    import time

    t1 = time.time()
    # print("start gdal")
from collections import defaultdict, OrderedDict
import itertools
from osgeo import ogr, osr, gdal

from osgeo import ogr

POINT = 1
LINE = 2
POLY = 3
M = 1
MULTI = 1
CURVE = 1

GEOMETRY_TYPES = {
    ogr.wkbPoint: ("Point", POINT, 0, 2, 0, 0),
    ogr.wkbPoint25D: ("Point25D", POINT, 0, 3, 0, 0),
    ogr.wkbPointM: ("PointM", POINT, 0, 2, 0, M),
    ogr.wkbPointZM: ("PointZM", POINT, 0, 3, 0, M),
    ogr.wkbMultiPoint: ("MultiPoint", POINT, 0, 2, MULTI, 0),
    ogr.wkbMultiPoint25D: ("MultiPoint25D", POINT, 0, 3, MULTI, 0),
    ogr.wkbMultiPointM: ("MultiPointM", POINT, 0, 2, MULTI, M),
    ogr.wkbMultiPointZM: ("MultiPointZM", POINT, 0, 3, MULTI, M),
    ogr.wkbLineString: ("LineString", LINE, 0, 2, 0, 0),
    ogr.wkbLineString25D: ("LineString25D", LINE, 0, 3, 0, 0),
    ogr.wkbLineStringM: ("LineStringM", LINE, 0, 2, 0, M),
    ogr.wkbLineStringZM: ("LineStringZM", LINE, 0, 3, 0, M),
    ogr.wkbCurve: ("Curve", LINE, CURVE, 2, 0, 0),
    ogr.wkbCurveZ: ("Curve", LINE, CURVE, 2, 0, 0),
    ogr.wkbCurveZM: ("Curve", LINE, CURVE, 2, 0, 0),
    ogr.wkbCurveM: ("Curve", LINE, CURVE, 2, 0, 0),
    ogr.wkbPolygon: ("Polygon", POLY, 2, 0, 0),
    ogr.wkbPolygon25D: ("Polygon25D", POLY, 2, 0, 0),
    ogr.wkbPolygonM: ("PolygonM", POLY, 2, 0, 0),
    ogr.wkbPolygonZM: ("PolygonZM", POLY, 2, 0, 0),
    ogr.wkbMultiPoint: ("MultiPoint"),
    ogr.wkbMultiPoint25D: ("MultiPoint25D"),
    ogr.wkbMultiPointM: ("MultiPointM"),
    ogr.wkbMultiPointZM: ("MultiPointZM"),
    ogr.wkbMultiLineString: ("MultiLineString"),
    ogr.wkbMultiLineString25D: ("MultiLineString25D"),
    ogr.wkbMultiLineStringM: ("MultiLineStringM"),
    ogr.wkbMultiLineStringZM: ("MultiLineStringZM"),
    ogr.wkbMultiPolygon: ("MultiPolygon"),
    ogr.wkbMultiPolygon25D: ("MultiPolygon25D"),
    ogr.wkbMultiPolygonM: ("MultiPolygonM"),
    ogr.wkbMultiPolygonZM: ("MultiPolygonZM"),
    ogr.wkbGeometryCollection: ("GeometryCollection"),
    ogr.wkbGeometryCollection25D: ("GeometryCollection25D"),
    ogr.wkbGeometryCollectionM: ("GeometryCollectionM"),
    ogr.wkbGeometryCollectionZM: ("GeometryCollectionZM"),
    ogr.wkbCircularString: "CircularString",
    ogr.wkbCompoundCurve: "CompoundCurve",
    ogr.wkbCurvePolygon: "CurvePolygon",
    ogr.wkbMultiCurve: "MultiCurve",
    ogr.wkbMultiSurface: "MultiSurface",
    ogr.wkbSurface: "Surface",
    ogr.wkbPolyhedralSurface: "PolyhedralSurface",
    ogr.wkbTIN: "TIN",
    ogr.wkbTINZ: "TIN",
    ogr.wkbTINM: "TIN",
    ogr.wkbTINZM: "TIN",
    ogr.wkbTriangle: "Triangle",
}


gdal.UseExceptions()
# import fiona
# from fiona.crs import from_epsg

if printtime:
    print("    gdal      ", time.time() - t1)
    t1 = time.time()
from .fileio import FileWriter

if printtime:
    print("    filewriter ", time.time() - t1)
    t1 = time.time()

#
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


def decode_wkbgeomtyp(geomtyp):
    type_geom = 0
    dimension = 0
    mesure = 0
    courbe = 0
    multi = 0

    if geomtyp is not None:
        type_geom = -1
        if geomtyp > 3000:
            dimension = 3
            mesure = 1
            gt = geomtyp - 3000
        elif geomtyp > 2000:
            dimension = 2
            mesure = 1
            gt = geomtyp - 2000
        elif geomtyp > 1000:
            dimension = 3
            gt = geomtyp - 1000
        else:  # (truc bizarre)
            nom_geom = ogr.GeometryTypeToName(geomtyp)
            dimension = 3 if "3D" in nom_geom else 2
            if "Point" in nom_geom:
                type_geom = 1
            elif "Line" in nom_geom:
                type_geom = 2
            elif "Polygon" in nom_geom:
                type_geom = 3
            multi = "Multi" in nom_geom
            return type_geom, multi, courbe, dimension, mesure
        multi = gt in {4, 5, 6}
        type_geom = gt - 3 if multi else gt
        if gt in {11, 12}:
            multi = True
            courbe = 1
            type_geom = gt - 9
        elif gt in {8, 9}:
            type_geom = 2
        elif gt == 10:
            type_geom = 3
        elif gt == 7:
            type_geom = 9
        elif gt == 0:
            type_geom = -1
        elif gt == 100:
            type_geom = 0
    print(
        "decodage type",
        geomtyp,
        "->",
        ogr.GeometryTypeToName(geomtyp),
        type_geom,
        multi,
        courbe,
        dimension,
        mesure,
    )
    return type_geom, multi, courbe, dimension, mesure


def code_wkbgeomtyp(type_geom, multi, courbe, dimension, mesure):
    gt = 0
    if type_geom == 1:
        gt = 4 if multi else 1
        if mesure:
            gt = gt + 3000 if dimension == 3 else gt + 2000
    elif type_geom == 2:
        if courbe:
            gt = 11 if multi else 9
            if dimension == 3:
                gt = gt + 1000
            if mesure:
                gt = gt + 2000
        else:
            gt = 5 if multi else 2
            if mesure:
                gt = gt + 3000 if dimension == 3 else gt + 2000
    elif type_geom == 3:
        if courbe:
            gt = 12 if multi else 10
            if dimension == 3:
                gt = gt + 1000
            if mesure:
                gt = gt + 2000
        else:
            gt = 6 if multi else 3
            if mesure:
                gt = gt + 3000 if dimension == 3 else gt + 2000
    elif type_geom == -1:
        gt = 0
    elif type_geom == 9:
        gt = 7
        if mesure:
            gt = gt + 3000 if dimension == 3 else gt + 2000
    # print ('code geom wkb',(type_geom, multi, courbe, dimension, mesure),gt)
    return gt


def recup_schema_gdal(schema_courant, ident, layer, driver, crs=None):
    """cree un schema a partir d une description fiona"""

    types_a = {
        "String": "T",
        "Integer": "E",
        "Integer64": "EL",
        "Real": "F",
        "DateTime": "D",
        "Date": "DS",
        "Time": "D",
    }

    sc_classe = schema_courant.setdefault_classe(ident)
    geomtyp = layer.GetGeomType()
    nom_geom = layer.GetGeometryColumn()
    if not nom_geom:
        nom_geom = "geometrie"
    type_geom, multi, courbe, dimension, mesure = decode_wkbgeomtyp(geomtyp)
    type_geom = str(type_geom)

    print(
        "---------recup schema gdal",
        ident,
        ":type geometrique gdal",
        geomtyp,
        ogr.GeometryTypeToName(geomtyp),
        type_geom,
        nom_geom,
    )
    spatialref = layer.GetSpatialRef()
    srid = str(spatialref.GetAttrValue("AUTHORITY", 1))
    print(
        ident,
        ":spatialref gdal",
        spatialref.GetName(),
        spatialref.AutoIdentifyEPSG(),
        spatialref.GetAttrValue("AUTHORITY", 1),
    )
    if not srid:
        srid = "3948"

    sc_classe.stocke_geometrie(
        type_geom,
        dimension=dimension,
        srid=srid,
        multiple=multi,
        courbe=courbe,
        mesure=mesure,
    )
    layerDefinition = layer.GetLayerDefn()
    # sc_classe.info["type_geom"] = type_geom
    for i in range(layerDefinition.GetFieldCount()):
        fielddef = layerDefinition.GetFieldDefn(i)
        fieldName = fielddef.GetName()
        fieldTypeCode = fielddef.GetType()
        fieldType = fielddef.GetFieldTypeName(fieldTypeCode)
        fieldWidth = fielddef.GetWidth()
        GetPrecision = fielddef.GetPrecision()
        sc_classe.stocke_attribut(
            fieldName,
            types_a[fieldType],
            # dimension=dimension,
            force=True,
            taille=int(fieldWidth) if fieldWidth else 0,
            dec=int(GetPrecision) if GetPrecision else None,
            ordre=-1,
        )
    return sc_classe


def schema_gdal(sc_classe, liste_attributs=None, l_nom=0):
    """cree une description gdal d un schema"""
    nom_g_s = {"1": "Point", "2": "LineString", "3": "Polygon"}
    nom_g_sc = {"1": "Point", "2": "CompoundCurve", "3": "CurvedPolygon"}
    nom_g_m = {"1": "MultiPoint", "2": "MultiLineString", "3": "MultiPolygon"}
    nom_g_mc = {"1": "MultiPoint", "2": "MultiCurve", "3": "MultiSurface"}
    nom_a = {
        "T": ogr.OFTString,
        "E": ogr.OFTInteger,
        "EL": ogr.OFTInteger64,
        "F": ogr.OFTReal,
        "D": ogr.OFTDateTime,
        "DS": ogr.OFTDate,
        "H": ogr.OFTStringList,
        "B": ogr.OFSTBoolean,
    }
    description = dict()
    type_geom = sc_classe.info["type_geom"]
    if type_geom == "indef":
        type_geom = "0"
    if type_geom > "0":
        if sc_classe.multigeom:
            nom_geom = (
                nom_g_mc[type_geom]
                if sc_classe.info["courbe"] == "1"
                else nom_g_m[type_geom]
            )
        else:
            nom_geom = (
                nom_g_sc[type_geom]
                if sc_classe.info["courbe"] == "1"
                else nom_g_s[type_geom]
            )
        if sc_classe.info["dimension"] == "3":
            nom_geom = "3D " + nom_geom
        description["geometry"] = nom_geom
    elif type_geom == "-1":
        print("schema gdal: geometrie inconnue", sc_classe.info)
        description["geometry"] = None
    else:
        description["geometry"] = None

    props = OrderedDict()
    description["properties"] = props
    if l_nom:
        sc_classe.use_noms_courts = True
    # print(
    #     "schema gdal",
    #     sc_classe.identclasse,
    #     sc_classe.get_liste_attributs(liste=liste_attributs),
    # )
    for i in sc_classe.get_liste_attributs(liste=liste_attributs):
        att = sc_classe.attributs[i]
        if l_nom and att.nom_court:
            nom = att.nom_court
        else:
            nom = att.nom
        nom = sc_classe.minmajfunc(nom)
        if att.conformite:
            att.type_att = "T"
            att.taille = att.conformite.taille if att.conformite.taille else 0
        # graphique="oui" if att.graphique else 'non'
        taille = ""

        type_att = nom_a.get(att.type_att, nom_a["T"])
        attdef = ogr.FieldDefn(nom, type_att)
        # print(
        #     "schema gdal:",
        #     sc_classe.nom,
        #     " attribut",
        #     i,
        #     att.nom,
        #     att.type_att,
        #     type_att,
        #     attdef.GetTypeName(),
        #     attdef.GetName(),
        # )

        if att.taille:
            attdef.SetWidth(att.taille)
        if att.dec:
            attdef.SetPrecision(att.dec)
        if att.alias:
            attdef.SetAlternativeName(att.alias)
        if att.defaut:
            attdef.SetDefault(att.defaut)
        props[nom] = attdef
    if not props:
        props[sc_classe.minmajfunc("gid")] = ogr.OFTInteger
    # print ("gdal sortie schema:", sc_classe.nom,description,sc_classe.minmajfunc)
    # print("schema gdal", props)
    return description


def ogr_layerlist(fichier):
    """ouverture d' un fichier et lecture de la liste de couches"""
    datasource = ogr.Open(fichier)
    layerlist = []
    for layer in datasource:
        name = layer.GetName()
        layerlist.append(name)
    return layerlist, datasource


def lire_objets(self, rep, chemin, fichier):
    """lecture d'un fichier reconnu et stockage des objets en memoire"""
    # print("lecture gdal", (rep, chemin, fichier), self.schemaclasse)
    #    raise
    # ouv = None
    # importer()
    groupe, classe = self.prepare_lecture_fichier(rep, chemin, fichier)
    classe = None
    # layers = fiona.listlayers(self.fichier)

    layers, datasource = ogr_layerlist(self.fichier)
    driver = datasource.GetDriver()
    print("gdal:lecture niveaux", layers)
    for layername in layers:
        layer = datasource.GetLayer(layername)
        # layerdef = layer.GetLayerDefn()
        # print("recup fiona", source.driver, source.schema, source.crs, source.meta)
        if layername != classe:
            self.setidententree(self.groupe, layername)
        if self.newschema:
            self.schemaclasse = recup_schema_gdal(
                self.schemaclasse.schema,
                (self.groupe, self.classe),
                layer,
                driver,
            )

        for i in layer:
            # print("lecture gdal", i)
            obj = self.getobj()
            jsondef = i.ExportToJson(as_object=True)
            if "geometry" in jsondef:
                geomref = i.GetGeometryRef()
                geometrie = geomref.ExportToWkt() if geomref else ""
                obj.attributs["#geom"] = geometrie
            if "properties" in jsondef:
                attribs = jsondef["properties"]
            obj.attributs.update([(nom, val) for nom, val in attribs.items()])
            obj.attributs["#chemin"] = chemin
            obj.initgeom()
            # print ('------gdalio ',obj,'\n')
            self.process(obj)
    return


class GdalWriter(object):
    """gestionnaire d'ecriture pour fichiers gdal"""

    def __init__(
        self,
        nom,
        schema=None,
        regle=None,
    ):
        # super().__init__(nom, schema=schema, regle=regle)
        # importer()
        self.nom = nom
        self.schemaclasse = schema
        self.output = regle.output
        self.regle = regle
        self.writerparms = self.output.writerparms
        self.liste_att = schema.get_liste_attributs(liste=self.output.liste_att)
        self.srid = self.output.srid
        self.schema = schema.schema
        self.regle = regle
        self.converter = gdalconverter
        self.layername = ""
        self.transtable = None
        self.buffer = dict()
        self.schemastore = dict()
        self.usebuffer = self.writerparms["usebuffer"]
        self.courbe = 1 if self.writerparms["force_courbe"] else 0
        self.multi = 1 if self.writerparms["force_multi"] else 0
        self.multipoint = 1 if self.writerparms["force_multipoint"] else 0
        self.flush = not self.usebuffer
        self.layerstate = dict()
        self.geomforcers = dict()
        self.geomforcer = (None, None)
        self.layers = dict()
        self.datasource = None
        self.driver = None
        self.currentlayer = None
        self.write = self.bwrite if self.usebuffer else self.swrite
        # self.write = self.swrite
        # print("----------------------------gdalwriter", nom)
        # raise

    def open(self):
        """ouvre  sur disque"""
        # print("open", self.schemaclasse, self.srid)
        if not self.schemaclasse:
            # raise
            return
        l_max = self.writerparms["attlen"]
        if l_max:
            self.schemaclasse.cree_noms_courts(longueur=l_max)
        # self.schemaclasse.minmajfunc = self.minmajfunc
        description = schema_gdal(
            self.schemaclasse, liste_attributs=self.liste_att, l_nom=l_max
        )
        # self.layername = self.schemaclasse.nom
        key = self.schemaclasse.identclasse
        self.layername = "_".join(key)
        if not self.driver:
            self.driver = ogr.GetDriverByName(self.writerparms["driver"])
            if not self.driver:
                print("gdal: driver inconnu", self.writerparms["driver"])
                return None
        if not self.datasource:
            datasource = self.driver.CreateDataSource(self.nom)
            # print ('creation',self.nom,"->",datasource)
            if datasource is None:
                print("erreur creation de la sortie", self.nom)
                raise StopIteration(3)
            self.datasource = datasource
        # print ("gdal: traitement",key )
        if key in self.layers:
            self.currentlayer = self.datasource.GetLayerByName(self.layername)
        else:
            description = schema_gdal(
                self.schemaclasse, liste_attributs=self.liste_att, l_nom=l_max
            )
            try:
                type_geom = int(self.schemaclasse.info.get("type_geom", 0))
            except ValueError:
                print(
                    "erreur type geometrique",
                    key,
                    self.schemaclasse.info.get("type_geom", 0),
                )
                type_geom = 0
            courbe = int(self.schemaclasse.info.get("courbe", 0)) or self.courbe
            nom_geometrie = ""
            if type_geom:
                if not self.schemaclasse.info["nom_geometrie"]:
                    self.schemaclasse.info["nom_geometrie"] = "geometrie"
                nom_geometrie = self.schemaclasse.info["nom_geometrie"]

            if type_geom == 2 or type_geom == 3:
                multi = int(self.schemaclasse.info.get("multiple", 0)) or self.multi
            else:
                multi = (
                    int(self.schemaclasse.info.get("multiple", 0)) or self.multipoint
                )
                # if multi:
                #     print ("multipoint",self.schemaclasse.info,self.multipoint)
            dimension = int(self.schemaclasse.info.get("dimension", 0))
            mesure = int(self.schemaclasse.info.get("mesure", 0))
            geomcode = code_wkbgeomtyp(type_geom, multi, courbe, dimension, mesure)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(int(self.srid))
            options = ["GEOMETRY_NAME=" + nom_geometrie]
            try:
                self.datasource.StartTransaction()
                error = self.datasource.CreateLayer(
                    self.layername, srs, geom_type=geomcode, options=options
                )
                self.datasource.CommitTransaction()
                self.currentlayer = self.datasource.GetLayerByName(self.layername)
                # print("creation couche", self.layername, options)
            except Exception as err:
                print("erreur creation table", self.layername, self.srid, geomcode, err)
            try:
                self.currentlayer.CreateFields(description["properties"].values())
                # print("creation champs", description["properties"].keys())
            except Exception as err:
                print("erreur creation champs", description["properties"], err)
            self.layers[key] = self.currentlayer
            # print ('creation table',self.layername,self.datasource, self.currentlayer)

            # print ('affectation', self.geomforcer,key,courbe,multi)
            self.geomforcers[key] = [courbe, multi]
        # print ("creation classe",self.layername,type_geom,multi,courbe)
        self.layerstate[key] = 1
        self.key = key
        self.geomforcer = self.geomforcers[key]

    def changeclasse(self, schemaclasse, attributs=None):
        """change de classe"""

        self.liste_att = schemaclasse.get_liste_attributs(
            liste=attributs if attributs else self.output.liste_att
        )
        # if self.ressource.etat == 1:
        #     self.close()
        key = schemaclasse.identclasse

        # crs = from_epsg(int(self.srid))
        self.schemaclasse = schemaclasse
        # schema = schema_fiona(self.schemaclasse, liste_attributs=self.liste_att, l_nom=self.l_max)
        if key not in self.layerstate:
            self.open()
        else:
            self.reopen(key)

        # print ("-------currentlayer",key, self.layerstate, '->', self.currentlayer)

    def reopen(self, key):
        """reouvre le fichier s'il a ete ferme entre temps"""
        self.currentlayer = self.layers[key]
        self.layerstate[key] = 1
        self.geomforcer = self.geomforcers[key]
        self.key = key

    def close(self):
        """fermeture"""
        #        print("fileeio fermeture", self.nom)
        key = self.schemaclasse.identclasse
        if self.nom == "#print":
            return  # stdout
        try:
            if key in self.layerstate and self.layerstate[key] == 1:
                self.layerstate[key] = 2
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
        # if obj.schema:
        return self.converter(
            obj,
            self.schemaclasse,
            self.liste_att,
            self.schemaclasse.minmajfunc,
            self.currentlayer,
            *self.geomforcer
        )
        # else:
        #     print ("obj sans schema", obj)
        #     return None

    def flush_buffer(self, ident):
        """ecrit les elements"""
        self.flush = True
        if ident in self.buffer:
            # print("recup buffer", ident, self.buffer[ident][0].schema)
            # self.changeclasse(self.schema.classes[ident])
            self.changeclasse(self.schema.classes[ident])
            # if ident in self.layerstate:
            #     self.reopen(ident)
            # else:
            #     self.open()
            # try:
            #     currentlayer=self.layers[ident]
            # except KeyError:
            #     print (ident,"inexistant", self.layers.keys())
            #     print ("buffer:", self.buffer.keys())
            # print("ecriture buffer", ident, len(self.buffer[ident]))
            # map(currentlayer.CreateFeature,self.buffer[ident])
            self.currentlayer.StartTransaction()
            # map(currentlayer.CreateFeature,self.buffer[ident])
            # map(lambda i:self.currentlayer.CreateFeature(self.convert(i)),self.buffer[ident])
            for i in self.buffer[ident]:
                # print ("apres buffer",i.ident,i.schema)
                # print("buffer", i)
                feature = self.convert(i)
                # print("feature", feature)
                # print("contenu", feature.ExportToJson(as_object=True))
                # feature=i
                if feature:
                    err = self.currentlayer.CreateFeature(feature)
                    if err:
                        print("gpkg: erreur creation objet", i)
            self.currentlayer.CommitTransaction()

            # # currentlayer.CreateFeatures(self.buffer[ident])
            del self.buffer[ident]
            self.flush = False
            return
        print("erreur changeclasse ", ident, self.schema, self.schema.classes.keys())
        raise StopIteration(2)

    def bwrite(self, obj):
        """ecriture bufferisee"""
        if not self.currentlayer or obj.ident != self.key:
            self.changeclasse(obj.schema)

        # feature = self.convert(obj)
        ident = obj.ident
        # print("bwrite", ident, obj.schema)
        # self.changeclasse(self.schema.classes[ident])
        # feature = self.convert(obj)
        if ident in self.buffer:
            # print("gdal:bwrite", len(self.buffer[ident]))
            self.buffer[ident].append(obj)
            if len(self.buffer[ident]) >= 10000:
                self.flush_buffer(ident)
        else:
            self.buffer[ident] = [obj]

        # print("bwrite2", ident, self.buffer[ident][0].schema)

        return True

    def swrite(self, obj):
        """ecrit un objet complet"""
        # print ("ecriture gdal",self.currentlayer)
        if not self.currentlayer:
            self.changeclasse(obj.schema)
        feature = self.convert(obj)
        # print ("gdal : ",feature.DumpReadable())
        try:
            self.currentlayer.CreateFeature(feature)
            feature = None
        except Exception as err:
            print(
                "erreur ecriture",
                obj.ident,
                err,
            )
        return True

    def finalise(self):
        """ferme definitivement les fichiers"""
        # print("appel finalise")
        for ident in list(self.buffer.keys()):
            self.flush_buffer(ident)
        self.layers = []
        self.currentlayer = None
        self.datasource.Destroy()
        self.datasource = None
        return 3


def gdalconverter(obj, schemaclasse, liste_att, minmajfunc, layer, courbe, multi):
    """convertit un objet dans un format compatible avec la lib gdal"""
    feature = ogr.Feature(layer.GetLayerDefn())
    # print("conversion gdal", obj.ident, schemaclasse)
    for nom in liste_att:
        val = obj.attributs.get(nom, "")
        # print("gdalconverter : champs", nom, val)
        feature.SetField(nom, str(val))
    if obj.geomnatif and obj.format_natif == "ewkt":
        geom = obj.attributs["#geom"]
    else:
        if obj.initgeom():
            geom = ecrire_geom_ewkt(
                obj.geom_v,
                epsg=False,
                multiple=multi,
                force_courbe=courbe,
            )
        else:
            geom = "EMPTY"
            print("erreur creation geometrie", obj.geom_v.erreurs, obj)
        # print ("geom ewkt", geom, obj.geom_v)
    # if multi and obj.geom_v.type=="1":
    #     print ("multipoint",obj)

    # print ("creation geometrie" , obj.geomnatif, obj.format_natif,obj.attributs["#geom"],'->',geom)
    if geom:
        feature.SetGeometry(ogr.CreateGeometryFromWkt(geom))
    else:
        if schemaclasse.info["type_geom"] != "0":
            print("warning geometrie vide", obj.ident, schemaclasse.info["type_geom"])
        feature.SetGeometry(None)
    # print("contenu", feature.ExportToJson(as_object=True))
    return feature


def init_gdal(output):
    output.writerclass = GdalWriter


def init_gdalb(output):
    init_gdal(output)
    output.writerparms["usebuffer"] = True


#                       reader,      geom,    hasschema,  auxfiles
READERS = {
    "dxf": (lire_objets, "#ewkt", True, (), None, None),
    "shp": (
        lire_objets,
        "#ewkt",
        True,
        ("dbf", "prj", "shx", "cpg", "qpj"),
        None,
        None,
    ),
    "mif": (lire_objets, "#ewkt", True, (("mid",)), None, None),
    "gpkg": (lire_objets, "#ewkt", True, (), None, None),
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
        "#ewkt",
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
        "#ewkt",
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
        "#ewkt",
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
        "no",
        "#ewkt",
        "#tmp",
        init_gdalb,
    ),
}

if printtime:
    print("     end ", time.time() - t1)
    t1 = time.time()

#########################################################################
