# -*- coding: utf-8 -*-
"""
Acces aux services web wfs

commandes disponibles :

    * requete getcapabilities et analyse des donnees disponibles


necessite la librairie requests et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:


"""
from copy import Error
import sys

# from pyetl.formats.csv import geom_from_ewkt, ecrire_geom_ewkt
from .database import DbConnect
from .gensql import DbGenSql
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import ParseError
import requests

# global ET, requests, ParseError


# def importer():

#     import xml.etree.cElementTree as ET
#     from xml.etree.ElementTree import ParseError
#     import requests


TYPES_A = {
    "T": "T",
    "F": "F",
    "D": "D",
    "DS": "DS",
    "E": "E",
    "EL": "EL",
    "N": "N",
    "B": "B",
    "S": "S",
    "xsd:string": "T",
    "string": "T",
    "xsd:date": "DS",
    "date": "DS",
    "xsd:int": "E",
    "xsd:short": "E",
    "int": "E",
    "integer": "E",
    "long": "EL",
    "xsd:long": "EL",
    "xsd:dateTime": "D",
    "dateTime": "D",
    "xsd:double": "F",
    "xsd:decimal": "F",
    "double": "F",
}

TYPES_G = {
    "gml:PointPropertyType": "1",
    "gml:GeometryPropertyType": "-1",
    "gml:MultiPolygonPropertyType": "3",
    "gml:PolygonPropertyType": "3",
    "gml:MultiLineStringPropertyType": "2",
    "gml:LineStringPropertyType": "2",
}

ALLTYPES = dict(TYPES_A)
ALLTYPES.update(TYPES_G)


def getnamespace(root):
    """extrait les namespaces xml"""
    roottag = root.tag
    namespace = ""
    if "}" in roottag:
        namespace = roottag.split("}")[0] + "}"
    return namespace


class WfsConnect(DbConnect):
    """connecteur wwfs: simule un acces base a partir du schema"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        # importer()

        self.types_base.update(TYPES_A)
        self.type_base = "wfs"
        self.tablelist = []
        self.connect()
        self.geographique = True
        self.accept_sql = "no"
        self.curtable = ""
        self.curnb = 0

    #        self.encoding =

    def connect(self):
        """effectue un getcapabilities pour connaitre le schema"""

        #        import pyodbc as odbc
        try:
            retourcaps = requests.get(
                self.serveur,
                params={
                    "REQUEST": "GetCapabilities",
                    "SERVICE": "WFS",
                    "version": "1.0.0",
                },
            )

        except Error as err:
            self.params.logger.exception("erreur wfs", exc_info=err)
            # print("erreur wfs", err)
            return False
        caps = retourcaps.text
        try:
            tree = ET.fromstring(caps)
        except ParseError as per:
            self.params.logger.exception("capabilites mal formees", exc_info=per)
            # print("capabilites mal formees", per)
            return False
        namespace = getnamespace(tree)
        nametag = namespace + "Name"
        for table in tree.iter(namespace + "FeatureType"):
            for elem in table.iter():
                # print("elem", elem)
                if elem.tag == nametag:
                    nom = elem.text
                    if ":" in nom:
                        groupe, nom = nom.split(":", 1)
                    else:
                        groupe = ""
                    # print(" nom_table", nom)
                    self.tablelist.append((groupe, nom))
        # print("retour getcap", len(caps), "->", len(self.tablelist))

        self.connection = True

    def commit(self):
        pass

    def get_tables(self):
        """ retourne la liste des tables """
        return list(self.tables.values())

    @property
    def rowcount(self):
        return -1

    def get_attr_of_classe(self, schemaclasse):
        """recupere la description d une classe"""
        ident = schemaclasse.identclasse
        groupe, nom = ident
        params = {
            "REQUEST": "DescribeFeatureType",
            "SERVICE": "WFS",
            "version": "1.0.0",
        }
        # params["TYPENAME"] = groupe + ":" + nom if groupe else nom
        params["TYPENAME"] = nom
        try:
            retour = requests.get(self.serveur, params=params)
        except Error as err:
            print("erreur wfs", params, err)
            return False
        description = retour.text
        tree = ET.fromstring(description)
        namespace = getnamespace(tree)
        attlist = []
        del schemaclasse.attributs["__pending"]
        for seq in tree.iter(namespace + "sequence"):
            for elem in seq.iter(namespace + "element"):
                xmltype = elem.get("type")
                nom_att = elem.get("name")
                pyetltype = ALLTYPES.get(xmltype)
                # if nom_att == "geo_shape":
                #     print("wfs: stocke geom", nom, xmltype, pyetltype)
                if pyetltype is None:
                    print(" type inconnu", xmltype)
                    pyetltype = "T"
                    print(
                        "attributs",
                        groupe,
                        nom,
                        elem.get("name"),
                        xmltype,
                        "->",
                        pyetltype,
                    )

                attlist.append(
                    self.attdef(
                        groupe,
                        nom,
                        nom_att,
                        "",
                        pyetltype,
                        "",
                        "",
                        "",
                        "",
                        "",
                        2,
                        0,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        0,
                        0,
                    )
                )
        # print("wfs:attlist:", attlist)
        self.cree_schema_classe(ident, attlist, schema=None)

    def get_attributs(self):
        """description des attributs du service wfs
        structure fournie :
            nom_groupe;nom_classe;nom_attr;alias;type_attr;graphique;multiple;\
            defaut;obligatoire;enum;dimension;num_attribut;index;unique;clef_primaire;\
            clef_etrangere;cible_clef;taille;decimales"""
        retourdesc = requests.get(
            self.serveur,
            params={
                "REQUEST": "DescribeFeatureType",
                "SERVICE": "WFS",
                "version": "1.0.0",
            },
        )
        tree = ET.fromstring(retourdesc.text)
        attlist = []
        tables = self.tablelist
        # print("servicewfs: get_atttributs", retourdesc.text)
        namespace = getnamespace(tree)
        groupe = self.base
        nom = "inconnu"
        for elem in tree.iter(namespace + "element"):
            if elem.get("substitutionGroup") == "gml:_Feature":
                nom = elem.get("name", "")
                groupe = elem.get("type").split(":")[0]
                continue
            else:
                xmltype = elem.get("type", "")
                nom_att = elem.get("name", "")
                pyetltype = ALLTYPES.get(xmltype)
                # if nom_att == "geo_shape":
                #     print("wfs: stocke geom", nom, xmltype, pyetltype)
                if pyetltype is None:
                    print(" type inconnu", xmltype)
                    pyetltype = "T"
            att = self.attdef(
                groupe,
                nom,
                nom_att,
                "",
                pyetltype,
                "",
                "",
                "",
                "",
                "",
                2,
                0,
                "",
                "",
                "",
                "",
                "",
                "",
                0,
                0,
            )
            attlist.append(att)
            ident = (groupe, nom)
            nouv_table = [groupe, nom, "", "", "", -1, "", "", "", "", ""]
            # print ('table', nouv_table)
            self.tables[ident] = nouv_table
        return attlist

    def get_enums(self):
        return ()

    def get_type(self, nom_type):
        if nom_type in TYPES_G:
            return nom_type
        return self.types_base.get(nom_type.upper(), "?")

    def get_surf(self, nom):
        return ""

    def get_perim(self, nom):
        return ""

    def get_long(self, nom):
        return ""

    def get_geom(self, nom):
        return ""

    def set_geom(self, geom, srid):
        return ""

    def set_geomb(self, geom, srid, buffer):
        return ""

    def set_limit(self, maxi, _):
        if maxi:
            return "maxFeatures=" + str(maxi)
        return ""

    def cond_geom(self, nom_fonction, nom_geometrie, geom2):
        cond = ""
        fonction = ""
        if nom_fonction == "dans_emprise":
            cond = "MbrWithin(" + nom_geometrie + " , " + geom2 + " )"
            return geom2 + " && " + nom_geometrie
        if nom_fonction == "intersect":
            fonction = "Intersects("
        elif nom_fonction == "dans":
            fonction = "Contains("
        if fonction:
            return fonction + geom2 + "," + nom_geometrie + ")"
        return ""

    def req_alpha(self, ident, schema, attribut, valeur, mods, maxi=0, ordre=None):
        """recupere les elements d'une requete alpha"""
        niveau, classe = ident
        requete = ""
        data = ""
        schema.resolve()
        # if schema.pending:
        #     self.get_attr_of_classe(schema)
        attlist = []
        atttext, attlist = self.construction_champs(schema, "S" in mods, "L" in mods)
        if attribut:
            if attribut in self.sys_fields:  # c est un champ systeme
                attribut, type_att = self.sys_fields[attribut]
            else:
                type_att = schema.attributs[attribut].type_att
            cast = self.nocast
            if type_att == "D":
                cast = self.datecast
            elif type_att in "EFS":
                cast = self.numcast
            elif schema.attributs[attribut].conformite:
                cast = self.textcast

            if isinstance(valeur, (set, list)) and len(valeur) > 1:

                data = self.multivaldata(valeur)
                #                data = {'val':"{'"+"','".join(valeur)+"'}"}
                cond = self.multival(len(data), cast=cast)
            else:
                if isinstance(valeur, (set, list)):
                    val = valeur[0]
                oper = "="
                val = valeur
                if val:
                    if val[0] in "<>=~":
                        oper = val[0]
                        val = val[1:]
                    if val[0] == "\\":
                        val = val[1:]
                cond = self.monoval(oper, cast)
                data = {"val": val}
                print("valeur simple", valeur, oper, cond, cast, data)
        reqparams = {
            "REQUEST": "GetFeature",
            "SERVICE": "WFS",
            "version": "1.1.0",
            # "subtype": "gml/3.1.1",
            "typeName": classe,
        }
        if maxi:
            reqparams["maxFeatures"] = str(maxi)
        if attribut:
            reqparams["propertyName"] = str(valeur)
        self.attlist = attlist

        has_geom = schema.info["type_geom"] != "0"
        retourdesc = requests.get(self.serveur, params=reqparams)
        print("retour descriptif", retourdesc.text)
        print("retour valeurs", retourdesc)
        return


class WfstGenSql(DbGenSql):
    """generateur sql"""

    pass


DBDEF = {"wfs": (WfsConnect, WfstGenSql, "server", "", "#gml", "acces wfs")}
