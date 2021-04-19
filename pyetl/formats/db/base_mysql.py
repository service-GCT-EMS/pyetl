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
from mysql.connector import connect as mysqlconnect, Error as MysqlError, FieldType

# from pyetl.formats.geometrie.format_ewkt import geom_from_ewkt, ecrire_geom_ewkt

# from pyetl.formats.csv import geom_from_ewkt, ecrire_geom_ewkt
from .database import DbConnect
from .gensql import DbGenSql


TYPES_A = {
    "char": "T",
    "varchar": "T",
    "text": "T",
    "longtext": "T",
    "mediumtext": "T",
    "enum": "T",
    "STRING": "T",
    "VAR_STRING": "T",
    "ENUM": "T",
    "set": "T",
    "json": "J",
    "double": "F",
    "decimal": "N",
    "float": "F",
    "HSTORE": "H",
    "BLOB": "X",
    "datetime": "D",
    "DATE": "DS",
    "timestamp": "D",
    "TIMESTAMP": "D",
    "time": "D",
    "date": "DS",
    "year": "DS",
    "int": "E",
    "LONG": "EL",
    "SHORT": "E",
    "TINY": "E",
    "tinyint": "E",
    "smallint": "E",
    "mediumint": "E",
    "bigint": "EL",
    "BOOLEEN": "B",
    "BOOLEAN": "B",
    "SEQUENCE": "S",
    "SEQ": "S",
    "SERIAL": "S",
    "INTERVALLE": "I",
    "mediumblob": "X",
    "longblob": "X",
    "blob": "X",
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
        self.accept_sql = "geo"
        self.dateformat = "YYYY/MM/DD HH24:MI:SS"
        self.requetes = {
            "info_enums2": self.req_enums,
            "info_tables": self.req_tables,
            "info_attributs": self.req_attributs,
        }

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        if self.connection:
            return
        self.params.logger.info(
            "connection %s %s en tant que %s", self.serveur, self.base, self.user
        )
        # print(
        #     "info:mysql: connection ",
        #     self.serveur,
        #     self.base,
        #     self.user,
        #     "*" * len(self.passwd),
        # )
        port = None
        if " " in self.serveur:
            host, port = self.serveur.split(" ")
        else:
            host = self.serveur
        host = host.split("=")[-1]
        connectparams = {
            "user": self.user,
            "passwd": self.passwd,
            "host": host,
            "db": self.base,
            "charset": "utf8",
        }
        if port:
            port = port.split("=")[-1]
            connectparams["port"] = port
        try:
            connection = mysqlconnect(**connectparams)
            connection.autocommit = True
            self.connection = connection
        except self.DBError as err:
            print("error: mysql: utilisateur ou mot de passe errone sur la base ", err)

    @property
    def req_enums(self):
        """recupere les enums (lie aux colonnes sur mysql)"""
        requete = """
                SELECT
                LOWER(CONCAT_WS("_",TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME)),
                replace(substring(COLUMN_TYPE,6,char_length(COLUMN_TYPE)-6),"'",'')
                FROM INFORMATION_SCHEMA.COLUMNS WHERE DATA_TYPE="enum"
                """
        return requete

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
                            FROM
                            INFORMATION_SCHEMA.TABLES
                            WHERE TABLE_SCHEMA <> 'information_schema'
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
                    TABLE_SCHEMA as nomschema,
                    TABLE_NAME as nomtable,
                    COLUMN_NAME as attribut,
                    COLUMN_COMMENT as alias,
                    DATA_TYPE AS type_attribut,
                    'non' as graphique,
                    'non' as multiple,
                    COLUMN_DEFAULT as defaut,
                    not IS_NULLABLE as obligatoire,
                    CASE WHEN DATA_TYPE="enum" THEN
                        LOWER(CONCAT_WS("_",TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME))
                        ELSE ""
                        END AS enum,
                    CHARACTER_MAXIMUM_LENGTH as dimension,
                    ORDINAL_POSITION as num_attribut,
                    '' as indexes,
                    CASE WHEN COLUMN_KEY = "UNI" THEN "1"
                        ELSE ""
                        END AS i_unique,
                    CASE WHEN COLUMN_KEY = "PRI" THEN "1"
                        ELSE ""
                        END AS primary_key,
                    "" as fkey,
                    "" as cible,
                    "" as parametres,
                    NUMERIC_PRECISION as taille,
                    NUMERIC_SCALE as decimales

                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA <> 'information_schema'

        """
        return requete

    def get_type(self, nom_type):
        if "geometry" in nom_type:
            return nom_type
        infotype = self.types_base.get(nom_type, "?")
        # if infotype == "?":

        #     print(" mysql get type", nom_type, self.types_base.get(nom_type, "?"))
        return infotype

    def getdatatype(self, datatype):
        """recupere le type interne associe a un type cx_oracle"""
        nom = FieldType.get_info(datatype)
        # print(" getdatatype", datatype, nom, TYPES_A.get(nom, "T"))
        return nom

    def get_dateformat(self, nom):
        """formattage dates"""
        return 'TO_CHAR("' + nom + '"' + ",'" + self.dateformat + "')"

    #        return 'TO_CHAR("'+nom+'")'
    #        return nom

    def quote_table(self, ident):
        """identifiants tables"""
        return ".".join(ident)

    def quote(self, att):
        """rajoute les quotes sur une liste de valeurs ou une valeur"""
        return att

    def datecast(self, nom):
        """forcage date"""
        return "TO_DATE(" + nom + ",'" + self.dateformat + "')"

    def monoval(self, operateur="=", cast=None):
        """acces valeur"""
        if cast is not None:
            return " " + operateur + cast(":val")
        return " " + operateur + " :val"

    def get_surf(self, nom):
        return "ST_area(%s)" % nom

    def get_perim(self, nom):
        return "ST_perimeter(%s)" % nom

    def get_long(self, nom):
        return "ST_length(%s)" % nom

    def get_geom(self, nom):
        return "ST_asEWKT(%s)" % nom

    def set_geom(self, geom, srid):
        """cree une geometrie"""
        return ""

    def set_geomb(self, geom, srid, buffer):
        """cree un buffer"""
        return ""

    def set_limit(self, maxi, whereclause):
        """limite le nombre de lignes"""
        if maxi:
            return " LIMIT " + str(maxi)

        return ""

    def cond_geom(self, nom_fonction, nom_geometrie, geom2):
        """definition d'une condition geometrique"""
        return ""

    def execrequest(self, requete, data, attlist=None, regle=None):
        """passage de la requete sur la base"""
        cur = self.get_cursinfo()
        try:
            cur.execute(requete, data, attlist=attlist, regle=regle)
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

    def iterreq(
        self, requete, data, attlist=None, has_geom=False, volume=0, nom="", regle=None
    ):
        """recup d'un iterateur sur les resultats"""
        cur = (
            self.execrequest(requete, data, attlist=attlist, regle=regle)
            if requete
            else None
        )
        self.decile = 1
        if cur is None:
            return iter(())

        self.getdecile(cur)

        #        print('oracle:', requete, data)
        return cur


class MysqlGenSql(DbGenSql):
    """creation des sql de modif de la base"""

    pass


DBDEF = {"mysql": (MysqlConnect, MysqlGenSql, "server", "", "#ewkt", "base mysql")}
