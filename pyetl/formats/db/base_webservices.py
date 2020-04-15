# -*- coding: utf-8 -*-
"""
acces services wfs pour extraction de donnees

@author: 89965
acces a la base de donnees
"""
from copy import Error
import sys
import requests

# version patchee de owslib pour eviter un crash sur data.strasbourg.eu
from owslib.wfs import WebFeatureService

# from pyetl.formats.csv import geom_from_ewkt, ecrire_geom_ewkt
from .database import DbConnect
from .gensql import DbGenSql

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
    "int": "E",
    "xsd:dateTime": "D",
    "dateTime": "D",
    "xsd:double": "F",
    "double": "F",
}

TYPES_G = {"GeometryCollection": "-1", "Point": "1"}

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
        self.types_base.update(TYPES_A)
        self.type_base = "wfs"
        self.tablelist = []
        self.connect()
        self.geographique = True
        self.accept_sql = "no"
        self.curtable = ""
        self.curnb = 0

    def connect(self):
        """effectue un getcapabilities pour connaitre le schema"""
        try:
            print("connection wfs", self.serveur)
            if "version=" in self.serveur:
                serveur, vdef = self.serveur.split(" ", 1)
                version = vdef.split("=")[1]
            else:
                serveur = self.serveur
                version = "1.1.0"
            self.connection = WebFeatureService(url=serveur, version=version)
        except Error as err:
            print("erreur wfs", err)
            return False
        self.tablelist = [tuple(i.split(":", 1)) for i in self.connection.contents]
        print("retour getcap", len(self.tablelist))

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
        print("analyse classe", ident)
        groupe, nom = ident
        wfsid = ":".join(ident)
        schemadef = self.connection.get_schema(wfsid)
        # print("recup attlist ", attdict)
        del schemaclasse.attributs["__pending"]
        if schemadef is None:
            print("schema non present sur le serveur", ident)
            return
        attdict = schemadef["properties"]
        if attdict is not None:
            for nom_att, xmltype in attdict.items():
                # print(nom_att, xmltype)
                pyetltype = ALLTYPES.get(xmltype)
                if pyetltype is None:
                    print(" type inconnu", xmltype)
                    pyetltype = "T"
                schemaclasse.stocke_attribut(nom_att, pyetltype)
        type_geom = schemadef.get("geometry")
        if type_geom:
            if type_geom in TYPES_G:
                type_geom = TYPES_G[type_geom]
            else:
                print("geometrie inconnue", type_geom)
                type_geom = "-1"
            nom_geom = schemadef["geometry_column"]
            dimension = 2
            schemaclasse.stocke_geometrie(
                type_geom, dimension=dimension, srid="3948", multiple=1, nom=nom_geom
            )

    def get_attributs(self):
        """description des attributs de la base sqlite
        structure fournie :
            nom_groupe;nom_classe;nom_attr;alias;type_attr;graphique;multiple;\
            defaut;obligatoire;enum;dimension;num_attribut;index;unique;clef_primaire;\
            clef_etrangere;cible_clef;taille;decimales"""

        attlist = []
        tables = self.tablelist
        # print("sqlite: lecture tables", tables)

        for groupe, nom in tables:
            att = self.attdef(
                groupe,
                nom,
                "__pending",
                self.get_attr_of_classe,
                "T",
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

            requete = (
                " SELECT "
                + atttext
                + ' FROM "'
                + niveau
                + "."
                + classe
                + '" WHERE '
                + cast(attribut)
                + cond
            )
        else:
            requete = " SELECT " + atttext + ' FROM "' + niveau + "." + classe + '"'
            data = ()
        if ordre:
            if isinstance(ordre, list):
                requete = requete + " ORDER BY " + ",".join(ordre)
            else:
                requete = requete + " ORDER BY " + ordre

        requete = requete + self.set_limit(maxi, bool(data))
        self.attlist = attlist
        if not atttext:
            requete = ""
            data = ()
        #        print('acces alpha', self.geographique, requete, data)
        #        raise
        #        print ('geometrie',schema.info["type_geom"])
        print("sqlite req alpha ", requete)
        print("sqlite appel iterreq", type(self.iterreq))
        has_geom = schema.info["type_geom"] != "0"
        aa = self.iterreq(requete, data, has_geom=has_geom)
        print("sqlite apres iterreq", type(aa))
        return aa


class WfstGenSql(DbGenSql):
    """generateur sql"""

    pass


DBDEF = {"wfs2": (WfsConnect, WfstGenSql, "server", "", "#gml", "acces wfs")}
