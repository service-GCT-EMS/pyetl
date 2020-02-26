# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:33:53 2016

@author: 89965
acces a la base de donnees
"""
import sys
import sqlite3

# from pyetl.formats.csv import geom_from_ewkt, ecrire_geom_ewkt
from .database import DbConnect
from .gensql import DbGenSql

TYPES_A = {
    "T": "T",
    "VARCHAR": "T",
    "VARCHAR2": "T",
    "TEXT": "T",
    "CHAR": "T",
    "F": "F",
    "NUMBER": "F",
    "TIMESTAMP": "D",
    "DATE": "DS",
    "ROWID": "E",
    "FLOAT": "F",
    "NUMERIC": "N",
    "BOOLEEN": "B",
    "BOOLEAN": "B",
    "S": "S",
    "SEQUENCE": "S",
    "SEQ": "S",
    "SERIAL": "S",
    "I": "I",
    "SMALLINT": "E",
    "BIGINT": "I",
    "OID": "I",
    "INTEGER": "E",
    "E": "E",
}

TYPES_G = {
    "POINT": "1",
    "MULTIPOINT": "1",
    "MULTILINESTRING": "2",
    "MULTIPOLYGON": "3",
    "BLOB": "-1",
}


class SqltConnect(DbConnect):
    """connecteur de la base de donnees oracle"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.types_base.update(TYPES_A)
        self.type_base = "sqlite"
        self.connect()
        self.geographique = True
        self.accept_sql = "alpha"
        self.curtable = ""
        self.curnb = 0

    #        self.encoding =

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""

        #        import pyodbc as odbc
        print("info : dbacces:connection sqlite", self.user, "****", self.base)
        try:
            self.connection = sqlite3.Connection(self.base)
        except sqlite3.Error as err:
            print(
                "error: sqlite: utilisateur ou mot de passe errone sur la base sqlite",
                self.base,
            )
            print("error: sqlite: ", err)
            sys.exit(1)
            return None
        print("connection réussie", self.type_base)

    def _set_tablelist(self):
        """ produit la liste des tables pour definir les tables a recuperer (systeme ou pas) """
        requete = """select name, type from sqlite_master
                        where name not like 'spatial_ref_sys%'
                        and name not in ('spatialite_history',  'sqlite_sequence',
                        'sql_statements_log', 'SpatialIndex', 'ElementaryGeometries')
                        and name not like '%geometry_columns%'
                        and name not like 'idx_%'
                        and name not like 'vector_layers%'
                        and (type='table' or type='view')"""
        tables_tmp = self.request(requete, None)
        tables = []
        for i in tables_tmp:
            if i[0] == "geom_cols_ref_sys":
                self.accept_sql = "geo"
            else:
                tables.append(i)
        # print ('recup tables ', tables)
        return tables

    def get_tables(self):
        """ retourne la liste des tables """
        return self.tables

    @property
    def rowcount(self):
        """compte les resultats # on simule sqlite n'a pas de compteur"""
        if self.curtable:
            return self.curnb
        return 0

    def get_attributs(self):
        """description des attributs de la base sqlite
        structure fournie :
            nom_groupe;nom_classe;nom_attr;alias;type_attr;graphique;multiple;\
            defaut;obligatoire;enum;dimension;num_attribut;index;unique;clef_primaire;\
            clef_etrangere;cible_clef;taille;decimales"""

        attlist = []
        self.tables = []
        tables = self._set_tablelist()
        # print("sqlite: lecture tables", tables)
        for table in tables:
            nomtable, type_table = table
            if type_table == "table":
                type_table = "t"
            elif type_table == "view":
                type_table = "v"

            if "." in nomtable:
                schema, nom = nomtable.split(".")
            else:
                nom = nomtable
                schema = ""
            #            print('table', nom)
            table_geom = "ALPHA"
            table_dim = 2
            requete = 'select count(*) from "' + nomtable + '"'
            nb = self.request(requete, None)[0][0]
            # print ('retour',nb)
            requete = 'pragma table_info("' + nomtable + '")'
            attributs = self.request(requete, None)
            for att in attributs:
                # print ('att', att)
                num_att, nom_att, type_att, notnull, defaut, ispk = att
                attlist.append(
                    self.attdef(
                        schema,
                        nom,
                        nom_att,
                        "",
                        TYPES_G.get(type_att, type_att),
                        "",
                        "",
                        defaut,
                        notnull,
                        "",
                        2,
                        num_att,
                        "",
                        "",
                        ispk,
                        "",
                        "",
                        "",
                        0,
                        0,
                    )
                )
                if nom_att == "GEOMETRY" or type_att in TYPES_G:
                    table_geom = TYPES_G.get(type_att, "-1")
                    table_dim = 2

            nouv_table = [
                schema,
                nom,
                "",
                table_geom,
                table_dim,
                nb,
                type_table,
                "",
                "",
                "",
                "",
            ]
            # print ('table', nouv_table)
            self.tables.append(nouv_table)
        return attlist

    def get_enums(self):
        return ()

    def get_type(self, nom_type):
        if nom_type in TYPES_G:
            return nom_type
        return self.types_base.get(nom_type.upper(), "T")

    def get_surf(self, nom):
        return "Area(%s)" % nom

    def get_perim(self, nom):
        return "Perimeter(%s)" % nom

    def get_long(self, nom):
        return "Length(%s)" % nom

    def get_geom(self, nom):
        return "AsText(%s)" % nom

    def set_geom(self, geom, srid):
        return "GeomFromText('%s',%s)" % (geom, srid)

    def set_geomb(self, geom, srid, buffer):
        return "Buffer(GeomFromText('%s',%s),%f))" % (geom, srid, buffer)

    def set_limit(self, maxi, _):
        if maxi:
            return " LIMIT " + str(maxi)
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


class SqltGenSql(DbGenSql):
    """generateur sql"""

    pass


DBDEF = {
    "sqlite": (
        SqltConnect,
        SqltGenSql,
        "file",
        ".sqlite",
        "#ewkt",
        "base sqlite basique",
    )
}
