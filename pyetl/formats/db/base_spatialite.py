# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:33:53 2016

@author: 89965
acces a la base de donnees
"""
import sys
import sqlite3
import libspatialite
from .database import DbConnect, DbGenSql

TYPES_A = {
    "T": "T",
    "VARCHAR": "T",
    "VARCHAR2": "T",
    "TEXT": "T",
    "CHAR": "T",
    "F": "F",
    "NUMBER": "F",
    "TIMESTAMP": "D",
    "DATE": "D",
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


class SqltConnect(DbConnect):
    """connecteur de la base de donnees oracle"""

    def __init__(self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.types_base.update(TYPES_A)
        self.connect()
        self.geographique = True

    #        self.encoding =

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""

        errs = sqlite3.DatabaseError
        print("info : dbacces:connection sqlite", self.user, "****", self.base)
        try:
            self.connection = sqlite3.connect(self.base)
        except self.errs as err:
            print("error: sqlite: utilisateur ou mot de passe errone sur la base sqlite", self.base)
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
                attlist.append(self.attdef(
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
                ))
                if nom_att == "GEOMETRY":
                    table_geom = type_att
                    table_dim = 2

            nouv_table = [schema, nom, "", table_geom, table_dim, -1, type_table, "", "", "", ""]
            self.tables.append(nouv_table)
        return attlist

    @property
    def req_enums(self):
        return "", ()

    def get_type(self, nom_type):
        if nom_type in TYPES_G:
            return nom_type
        return self.types_base.get(nom_type.upper(), "T")

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
            if nom_fonction == "intersect":
                fonction = "ST_Intersects("
            elif nom_fonction == "dans":
                fonction = "ST_Contains("
            cond = fonction + geom2 + "," + nom_geometrie + ")"
        return cond

    def iterreq(self, requete, data, attlist=None, has_geom=False, volume=0):
        cur = self.execrequest(requete, data, attlist=attlist) if requete else None
        cur.decile = 1
        if cur is None:
            return iter(())

        cur.decile = int(cur.rowcount / 10) + 1
        if cur.decile == 1:
            cur.decile = 100000
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
        cur.close()
        return

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
        return self.iterreq(requete, data, has_geom=schema.info["type_geom"] != "0")


class SqltGenSql(DbGenSql):
    """generateur sql"""

    pass


DBDEF = {
    "spatialite": (SqltConnect, SqltGenSql, "file", ".sqlite", "#ewkt", "base spatialite basique")
}
