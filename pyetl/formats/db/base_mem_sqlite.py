# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:33:53 2016

@author: 89965
acces a la base de donnees
"""
import sys

from .base_sqlite import SqltConnect, SqltGenSql

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

TYPES_G = {"POINT": "1", "MULTILINESTRING": "2", "MULTIPOLYGON": "3"}


class SqlmConnect(SqltConnect):
    """connecteur de la base de donnees oracle"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.types_base.update(TYPES_A)
        self.connect()

    #        self.encoding =

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        try:
            import sqlite3

            self.errs = sqlite3.DatabaseError
        #        import pyodbc as odbc
        except ImportError:
            print("error: sqlite: erreur import: module sqlite non accessible")
            return None

        print("info : dbacces:connection sqlite memoire", self.base)
        if self.connection:
            return
        try:
            self.connection = sqlite3.connect(":memory:")
            version = self.request("select sqlite_version()", ())
            print("ouverture sqlite memoire", version)
            self.connection.enable_load_extension(True)
            self.connection.execute('SELECT load_extension("libspatialite")')
            self.connection.execute("SELECT InitSpatialMetaData();")
        except self.errs as err:
            print(
                "error: sqlite: utilisateur ou mot de passe errone sur la base sqlite",
                self.base,
            )
            print("error: sqlite: ", err)
            sys.exit(1)
            return None

    def _set_tablelist(self):
        """ produit la liste des tables pour definir les tables a recuperer (systeme ou pas) """
        requete = """select name, type from sqlite_master
                        where name not like 'spatial_ref_sys%'
                        and name not in ('spatialite_history',  'sqlite_sequence',
                        'geom_cols_ref_sys', 'sql_statements_log', 'SpatialIndex', 'ElementaryGeometries')
                        and name not like '%geometry_columns%'
                        and name not like 'idx_%'
                        and name not like 'vector_layers_%'
                        and (type='table' or type='view')"""
        tables = self.request(requete, None)
        return tables

    def get_tables(self):
        """ retourne la liste des tables """
        return self.tables

    def get_attributs(self):
        """description des attributs de la base sqlite
        structure fournie :
            nom_groupe;nom_classe;nom_attr;alias;type_attr;graphique;multiple;\
            defaut;obligatoire;enum;dimension;num_attribut;index;unique;clef_primaire;\
            clef_etrangere;cible_clef;taille;decimales"""

        attlist = []
        self.tables = []
        tables = self._set_tablelist()
        print("sqlite: lecture tables", tables)
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
            requete = 'pragma table_info("' + nomtable + '")'
            attributs = self.request(requete, None)
            for att in attributs:
                num_att, nom_att, type_att, notnull, defaut, ispk = att
                attlist.append(
                    self.attdef(
                        (
                            schema,
                            nom,
                            nom_att,
                            "",
                            type_att,
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
                )
                if nom_att == "GEOMETRY":
                    table_geom = type_att
                    table_dim = 2

            nouv_table = [
                schema,
                nom,
                "",
                table_geom,
                table_dim,
                -1,
                type_table,
                "",
                "",
                "",
                "",
            ]
            self.tables.append(nouv_table)
        return attlist

    @property
    def req_enums(self):
        return "", ()

    def get_type(self, nom_type):
        if nom_type in TYPES_G:
            return nom_type
        return self.types_base.get(nom_type.upper(), "?")

    def get_surf(self, nom):
        return "ST_area(%s)" % nom

    def get_perim(self, nom):
        return "ST_perimeter(%s)" % nom

    def get_long(self, nom):
        return "ST_length(%s)" % nom

    def get_geom(self, nom):
        return "ST_asEWKT(%s)" % nom

    def set_geom(self, geom, srid):
        return "ST_GeomFromText('%s',%s)" % (geom, srid)

    def set_geomb(self, geom, srid, buffer):
        return "ST_buffer(ST_GeomFromText('%s',%s),%f))" % (geom, srid, buffer)

    def set_limit(self, maxi, _):
        if maxi:
            return " LIMIT " + str(maxi)
        return ""

    def cond_geom(self, nom_fonction, nom_geometrie, geom2):
        if nom_fonction == "dans_emprise":
            cond = geom2 + " && " + nom_geometrie
        else:
            fonction = None
            if nom_fonction == "intersect":
                fonction = "ST_Intersects("
            elif nom_fonction == "dans":
                fonction = "ST_Contains("
            if fonction:
                cond = fonction + geom2 + "," + nom_geometrie + ")"
                return cond
        print("fonction non definie", nom_fonction)
        return ""

    def execrequest(self, requete, data, attlist=None):
        cur = self.get_cursinfo()
        #        print('sqlite:execution requete', requete)
        try:
            cur.execute(requete, data, attlist=attlist)
            return cur
        except self.errs as err:
            #            err, =ee.args
            print(
                "error: sqlite interne: erreur acces base ", requete, "-->", data, err
            )
            #            print('error: sqlite: variables ', cur.bindnames())
            cur.close()
            #            raise
            return None

    def iterreq(self, requete, data, attlist=None, has_geom=False, volume=0, nom=""):
        cur = self.execrequest(requete, data, attlist=attlist) if requete else None
        if cur is None:
            return iter(())

        while True:
            try:
                elem = cur.cursor.fetchone()
            except self.errs as err:
                print("erreur " + self.type_base)
                continue
            if elem is None:
                break
            #                yield i
            tmp = list(elem)
            if has_geom:
                var = tmp[-1].read()
                tmp[-1] = var
            yield tmp
        cur.cursor.close()
        return


class SqlmGenSql(SqltGenSql):
    """generateur sql"""

    pass


DBDEF = {
    "mem_sqlite": (
        SqlmConnect,
        SqlmGenSql,
        "server",
        "",
        "#ewkt",
        "base sqlite en memoire",
    )
}
