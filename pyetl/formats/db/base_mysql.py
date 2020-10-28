# -*- coding: utf-8 -*-

"""
Acces aux bases de donnees mysql

commandes disponibles :

    * lecture des structures
    * extraction multitables et par selection sur un attribut

necessite la librairie mysql-connector-python :

    conda install -c anaconda mysql-connector-python

il est necessaire de positionner les parametres suivant:

"""

import os

os.environ["NLS_LANG"] = "FRENCH_FRANCE.UTF8"
from mysql.connector import connect as mysqlconnect, Error as MysqlError

# from pyetl.formats.geometrie.format_ewkt import geom_from_ewkt, ecrire_geom_ewkt

# from pyetl.formats.csv import geom_from_ewkt, ecrire_geom_ewkt
from .database import DbConnect
from .gensql import DbGenSql

TYPES_A = {
    "VARCHAR": "T",
    "VARCHAR2": "T",
    "CLOB": "T",
    "CHAR": "T",
    "NUMBER": "N",
    "DOUBLE PRECISION": "F",
    "NUMERIC": "N",
    "FLOAT": "F",
    "HSTORE": "H",
    "BLOB": "X",
    "SDO_GEOMETRY": "GEOMETRIE",
    "TIMESTAMP(6)": "D",
    "TIMESTAMP": "D",
    "DATE": "DS",
    "ROWID": "E",
    "SMALLINT": "E",
    "OID": "E",
    "INTEGER": "E",
    "BOOLEEN": "B",
    "BOOLEAN": "B",
    "SEQUENCE": "S",
    "SEQ": "S",
    "SERIAL": "S",
    "INTERVALLE": "I",
    "LONG": "EL",
}


class MysqlConnect(DbConnect):
    """connecteur de la base de donnees mysql"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.DBError = MysqlError

        self.connect()
        #        self.errdef = errdef
        self.type_base = "mysql"
        self.types_base.update(TYPES_A)
        self.accept_sql = "alpha"
        self.dateformat = "YYYY/MM/DD HH24:MI:SS"
        self.requetes = {
            "info_enums": self.req_enums,
            "info_tables": self.req_tables,
            "info_attributs": self.req_attributs,
        }

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        if self.connection:
            return
        print(
            "info:mysql: connection ",
            self.serveur,
            self.base,
            self.user,
            "*" * len(self.passwd),
        )
        host, port = self.serveur.split(" ")
        host = host.split("=")[-1]
        port = port.split("=")[-1]
        try:
            connection = mysqlconnect(
                user=self.user, passwd=self.passwd, host=host, port=port, db=self.base
            )
            connection.autocommit = True
            self.connection = connection
        except self.DBError as err:
            print("error: mysql: utilisateur ou mot de passe errone sur la base ", err)

    @property
    def req_enums(self):
        """recupere les enums (vide sous oracle)"""
        return ""

    @property
    def req_tables(self):
        """produit les objets issus de la base de donnees"""

        requete_tables = """
                            SELECT
                            TABLE_SCHEMA as nomschema,
                            TABLE_NAME as nomtable,
                            TABLE_COMMENT as commentaire,
                            0 as type_geometrique,
                            0 as dimension,
                            TABLE_ROWS as nb_enreg,
                            CASE WHEN  TABLE_TYPE = 'BASE TABLE' THEN 'r'
                                WHEN TABLE_TYPE = 'VIEW' THEN 'v'
                                END as type_table,
                            'False' as index_geometrique,
                            '' as clef_primaire,
                            '' as nindex,
                            '' as clef_etrangere
                            WHERE TABLE_TYPE == 'BASE TABLE'
                        """

        return requete_tables

    @property
    def req_attributs(self):
        """recupere le schema complet avec tous ses champs
            nomschema,nomtable,attribut,alias,type_attribut,graphique,multiple,
            defaut,obligatoire,enum,dimension,num_attribut,index,uniq,
            clef_primaire,clef_etrangere,cible_clef,parametres, taille,decimales"""

        requete = """
                    SELECT
                    SCHEMA_NAME as nomschema,
                    TABLE_NAME as nomtable,
                    COLUMN_NAME as attribut,
                    COLUMN_COMMENT as alias,
                    DATA_TYPE as type_attribut,
                    'non' as graphique,
                    'non' as multiple,
                    COLUMN_DEFAULT as defaut,
                    not IS_NULLABLE as obligatoire,
                    '' as enum,
                    FROM INFORMATION_SCHEMA.COLUMNS

        """

        requete = """
        SELECT DISTINCT   col.owner as nomschema,
                col.table_name as nomtable,
                col.column_name as attribut,
                CASE WHEN com.comments IS NOT NULL THEN com.comments
                    ELSE ''
                    END AS alias,
                CASE WHEN col.data_type = 'NUMBER' AND col.data_scale = 0 THEN 'E'
                     WHEN col.data_type = 'LONG' AND col.data_length = 0 THEN 'T'
                     ELSE col.data_type
                     END AS type_attribut,
                'non' as graphique,
                'non' as multiple,
--                 (CAST (col.data_default as VARCHAR2)),
                '' as defaut,
                CASE WHEN col.nullable ='Y' THEN 'oui' ELSE 'non' END AS obligatoire,
                '' as enum,
                col.data_length as dimension,
                col.column_id as num_attribut,
                ic.indexes as indexes,

                --'' as index_pos,
                CASE WHEN uniq_col.position IS NOT NULL THEN ''||uniq_col.position ELSE '' END AS i_unique,
                CASE WHEN primkey_col.position IS NOT NULL THEN ''||primkey_col.position ELSE '' END AS primary_key,
                CASE WHEN fkey_col.position IS NOT NULL THEN
                    (select t.owner||'.'|| c.table_name from all_constraints c LEFT JOIN all_tables t ON t.table_name=c.table_name
                    where c.owner=col.owner and c.constraint_name=fkey_col.r_constraint_name and rownum=1)
                     ELSE '' END AS f_key,
                CASE
                    WHEN fkey_col.position IS NOT NULL THEN
                        (select column_name from all_cons_columns cc where cc.owner=col.owner and cc.constraint_name = fkey_col.r_constraint_name and cc.position=fkey_col.position)
                    ELSE '' END AS cible,
                '' AS parametres,
                col.data_length as taille,
                col.data_scale as decimales

                FROM all_tab_columns col
                    LEFT JOIN all_col_comments com ON com.table_name=col.table_name AND com.column_name=col.column_name
                    LEFT JOIN
                        (SELECT LISTAGG(index_name||':'||column_position,' ')  WITHIN GROUP (order by index_name) as indexes,
                         table_name,column_name,table_owner from all_ind_columns
                         GROUP BY table_owner,table_name,column_name) ic
                        on ic.table_name=col.table_name AND ic.column_name=col.column_name and ic.table_owner=col.owner
                    LEFT JOIN
                        (SELECT con.table_name, cons_col.column_name, cons_col.position
                        FROM all_constraints con,all_cons_columns cons_col
                        WHERE con.table_name = cons_col.table_name
                            AND con.constraint_name = cons_col.constraint_name
                            AND con.constraint_type = 'P' ) primkey_col
                        ON  col.table_name = primkey_col.table_name AND col.column_name = primkey_col.column_name
                    LEFT JOIN
                        (SELECT con.table_name, cons_col.column_name, cons_col.position, con.constraint_name
                        FROM all_constraints con,all_cons_columns cons_col
                        WHERE con.table_name = cons_col.table_name
                            AND con.constraint_name = cons_col.constraint_name
                            AND con.constraint_type = 'U' ) uniq_col
                        ON  col.table_name = uniq_col.table_name AND col.column_name = uniq_col.column_name
                    LEFT JOIN
                        (SELECT con.table_name,
                             cons_col.column_name,
                             cons_col.position,
                             con.r_constraint_name
                        FROM all_constraints con,all_cons_columns cons_col
                        WHERE con.table_name = cons_col.table_name
                            AND con.constraint_name = cons_col.constraint_name
                            AND con.constraint_type = 'R'
                             )
                            fkey_col
                        ON  col.table_name = fkey_col.table_name AND col.column_name = fkey_col.column_name

                where col.owner<> 'SYS'
                      AND col.owner<> 'CTXSYS'
                      AND col.owner<> 'SYSTEM'
                      AND col.owner<> 'XDB'
                      AND col.owner<> 'WMSYS'
                      AND col.owner<> 'MDSYS'
                      AND col.owner<> 'EXFSYS'
                      AND col.owner<> 'CUS_DBA'

                ORDER BY col.owner,col.table_name,col.column_id
                    """

        return requete

    def getdatatype(self, datatype):
        """recupere le type interne associe a un type cx_oracle"""
        nom = datatype.__name__
        return TYPES_A.get(nom, "T")

    def get_dateformat(self, nom):
        """formattage dates"""
        return 'TO_CHAR("' + nom + '"' + ",'" + self.dateformat + "')"

    #        return 'TO_CHAR("'+nom+'")'
    #        return nom

    def datecast(self, nom):
        """forcage date"""
        return "TO_DATE(" + nom + ",'" + self.dateformat + "')"

    def monoval(self, operateur="=", cast=None):
        """acces valeur"""
        if cast is not None:
            return " " + operateur + cast(":val")
        return " " + operateur + " :val"

    def get_surf(self, nom):
        """calcul de surface"""
        return "0"

    def get_perim(self, nom):
        """calcul de perimetre"""
        return "0"

    def get_long(self, nom):
        """calcul de longueur"""
        return "0"

    def get_geom(self, nom):
        """recup de la geometrie en WKT"""
        return ""

    def set_geom(self, geom, srid):
        """cree une geometrie"""
        return ""

    def set_geomb(self, geom, srid, buffer):
        """cree un buffer"""
        return ""

    def set_limit(self, maxi, whereclause):
        """limite le nombre de lignes"""
        if maxi:
            if whereclause:
                return " AND ROWNUM <= " + str(maxi)
            return " WHERE ROWNUM <= " + str(maxi)

        return ""

    def cond_geom(self, nom_fonction, nom_geometrie, geom2):
        """definition d'ne condition geometrique"""
        return ""

    def execrequest(self, requete, data, attlist=None):
        """passage de la requete sur la base"""
        cur = self.get_cursinfo()
        #        print ('ora:execution_requet',requete)
        try:
            cur.execute(requete, data, attlist=attlist)
            return cur
        except self.DBError as errs:
            cursor = cur.cursor
            (error,) = errs.args
            print("error: mysql: erreur acces base ", self.base, self.connection)
            print("error: mysql: erreur acces base ", cursor.statement, "-->", data)
            print("error: mysql: variables ", cursor.bindnames())
            print("mysql-Error-Code:", error.code)
            print("mysql-Error-Message:", error.message)
            print("mysql-offset:", error.offset)
            print("mysql-context:", error.context)
            #            print("Oracle-complet:", errs)
            cur.close()
            #            raise
            return None

    def iterreq(self, requete, data, attlist=None, has_geom=False, volume=0, nom=""):
        """recup d'un iterateur sur les resultats"""
        cur = self.execrequest(requete, data, attlist=attlist) if requete else None
        self.decile = 1
        if cur is None:
            return iter(())

        self.decile = int(cur.rowcount / 10) + 1
        #        print('decile recup', self.decile)
        if self.decile == 1:
            self.decile = 100000

        #        print('oracle:', requete, data)
        if not has_geom:
            return cur

        def cursiter():
            """iterateur sur le curseur oracle avec decodage de la geometrie """
            while True:
                try:
                    elem = cur.cursor.fetchone()
                #                raise
                except self.DBError as err:
                    print("erreur " + self.base, err)
                    #                raise
                    continue
                if elem is None:
                    break
                #                yield i
                tmp = list(elem)
                if has_geom:
                    try:  # lecture de la geometrie en clob
                        var = tmp[-1].read()
                        tmp[-1] = var
                    except AttributeError:
                        pass
                yield tmp
            cur.close()
            return

        cur.__iter__ = cursiter
        return cur


class MysqlGenSql(DbGenSql):
    """creation des sql de modif de la base"""

    pass


DBDEF = {"mysql": (MysqlConnect, MysqlGenSql, "server", "", "", "base mysql")}
