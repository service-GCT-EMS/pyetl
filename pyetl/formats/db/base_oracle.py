# -*- coding: utf-8 -*-

"""
Acces aux bases de donnees oracle

commandes disponibles :

    * lecture des structures
    * extraction multitables et par selection sur un attribut

necessite la librairie cx_Oracle ou oracledb et un client oracle 64 bits

il est necessaire de positionner les parametres suivant:


"""
import os

os.environ["NLS_LANG"] = "FRENCH_FRANCE.UTF8"

from .database import DbConnect
from .gensql import DbGenSql
oracle=None
try:
    import oracledb as oracle
    MODE='oracledb'
except ImportError:
    try:
        import cx_Oracle as oracle
        MODE='cx_Oracle'
    except ImportError:
        pass


TYPES_A = {
    "VARCHAR": "T",
    "VARCHAR2": "T",
    "DB_TYPE_VARCHAR": "T",
    "DB_TYPE_CHAR": "T",
    "CLOB": "T",
    "CHAR": "T",
    "NUMBER": "N",
    "DOUBLE PRECISION": "F",
    "NUMERIC": "N",
    "DB_TYPE_NUMBER": "N",
    "FLOAT": "F",
    "HSTORE": "H",
    "BLOB": "X",
    "SDO_GEOMETRY": "GEOMETRIE",
    "TIMESTAMP(6)": "D",
    "TIMESTAMP": "D",
    "DB_TYPE_DATE": "D",
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


class OraConnect(DbConnect):
    """connecteur de la base de donnees oracle"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        # importer()
        self.oracle_env()
        if MODE=="oracledb":
            env = os.environ
            orahome = env["ORACLE_HOME"]
            oracle.init_oracle_client(lib_dir=orahome)
        self.connect()
        #        self.errdef = errdef
        self.type_base = "oracle"
        self.types_base.update(TYPES_A)
        self.accept_sql = "alpha"
        self.dateformat = "YYYY/MM/DD HH24:MI:SS"
        self.requetes = {
            "info_enums": self.req_enums,
            "info_tables": self.req_tables,
            "info_attributs": self.req_attributs,
            "info_vues": self.req_vues,
        }
        if oracle:
            self.DBError = oracle.Error

    def oracle_env(self):
        """positionne les variables d'environnement pour le connecteur"""
        if self.regle:
            orahome = self.regle.getchain(("oracle_home_" + self.code, "oracle_home"))
            lang = self.regle.getchain(
                ("oracle_lang_" + self.code, "oracle_lang_"), "FRENCH_FRANCE.UTF8"
            )
            env = os.environ
            #        print('modif_environnement ',env)
            if orahome and orahome != env.get("ORACLE_HOME"):
                # on manipule les variables d'environnement
                env["ORACLE_HOME"] = orahome
                env["PATH"] = orahome + ";" + env["PATH"]
            env["NLS_LANG"] = lang

    





    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        if self.connection:
            return
        self.params.logger.info(
            "connection oracle sur %s %s en tant que %s",
            self.serveur,
            self.base,
            self.user,
        )
        # print(
        #     "info:oracle: connection ",
        #     self.serveur,
        #     self.base,
        #     self.user,
        #     "*" * len(self.passwd),
        # )
        def output_type_handler(cursor, name, default_type, size, precision, scale):
            if default_type == oracle.DB_TYPE_CLOB:
                return cursor.var(oracle.DB_TYPE_LONG, arraysize=cursor.arraysize)
            if default_type == oracle.DB_TYPE_BLOB:
                return cursor.var(oracle.DB_TYPE_LONG_RAW, arraysize=cursor.arraysize)


        if not oracle:
            raise NotImplemented("acces oracle non disponible")
        try:
            """positionne les variables d'environnement pour les programmes externes"""
            # lib_oracle=r"C:\dev\mapper\autres\instantclient_19_9"
            # init_oracle_client(lib_dir=lib_oracle)
            # env = os.environ
            # env["ORACLE_HOME"]=lib_oracle

            configdir= self.regle.getvar("oracle_config_dir")

            connection = oracle.connect(user=self.user, password=self.passwd, dsn=self.serveur, config_dir=configdir)
            connection.autocommit = True
            connection.outputtypehandler = output_type_handler
            self.connection = connection
        except Exception as err:
            self.params.logger.exception("erreur connection oracle", exc_info=err)
            # print("error: oracle: utilisateur ou mot de passe errone sur la base ", err)

    @property
    def req_enums(self):
        """recupere les enums (vide sous oracle)"""
        return ""

    @property
    def req_tables(self):
        """produit les objets issus de la base de donnees"""

        # selection de la liste des niveaux et classes
        requete_tables = """      SELECT tab.owner as nomschema,
                                tab.table_name as nomtable,
                                '' as commentaire,
                                 0 as type_geometrique,
                                 0 as dimension,
                                tab.num_rows as nb_enreg,
                                'r' as type_table,
                                'False' as index_geometrique,
                                '' as clef_primaire,
                                '' as nindex,
                                '' as clef_etrangere
                FROM all_tables tab
                where
                      """

        requete_vues = """
                SELECT vw.owner as nomschema,
                        vw.view_name as nomtable,
                        '' as commentaire,
                        0 as type_geometrique,
                        0 as dimension,
                        -1 as nb_enreg,
                        'v' as type_table,
                        'False' as index_geometrique,
                        '' as clef_primaire,
                        '' as nindex,
                        '' as clef_etrangere
                FROM all_views vw
                where
        """
        requete_mvues = """
                SELECT mvw.owner as nomschema,
                        mvw.mview_name as nomtable,
                        '' as commentaire,
                        0 as type_geometrique,
                        0 as dimension,
                        -1 as nb_enreg,
                        'm' as type_table,
                        'False' as index_geometrique,
                        '' as clef_primaire,
                        '' as nindex,
                        '' as clef_etrangere
                FROM all_mviews mvw
                where
        """
        exclusions = """ owner<> 'SYS'
                      AND owner<> 'CTXSYS'
                      AND owner<> 'SYSTEM'
                      AND owner<> 'XDB'
                      AND owner<> 'WMSYS'
                      AND owner<> 'MDSYS'
                      AND owner<> 'EXFSYS'
                      AND owner<> 'CUS_DBA'"""

        requete = (
            requete_tables
            + exclusions
            + " UNION ALL"
            + requete_vues
            + exclusions
            + " UNION ALL"
            + requete_mvues
            + exclusions
        )
        return requete

    @property
    def req_attributs(self):
        """recupere le schema complet avec tous ses champs
        nomschema,nomtable,attribut,alias,type_attribut,graphique,multiple,
        defaut,obligatoire,enum,dimension,num_attribut,index,uniq,
        clef_primaire,clef_etrangere,cible_clef,parametres, taille,decimales"""
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

    @property
    def req_vues(self):
        """accede au texte des vues"""
        requete = """SELECT v.owner as schema,v.view_name as nom,v.text as requete,'False' as materialise FROM all_views v
                    WHERE v.owner<> 'SYS'
                      AND v.owner<> 'CTXSYS'
                      AND v.owner<> 'SYSTEM'
                      AND v.owner<> 'XDB'
                      AND v.owner<> 'WMSYS'
                      AND v.owner<> 'MDSYS'
                      AND v.owner<> 'ORDSYS'
                      AND v.owner<> 'EXFSYS'
                      AND v.owner<> 'CUS_DBA'

        union all
        SELECT mv.owner as schema,mv.mview_name as nom ,mv.query as requete,'True' as materialise FROM all_mviews mv
        WHERE mv.owner<> 'SYS'
          AND mv.owner<> 'CTXSYS'
          AND mv.owner<> 'SYSTEM'
          AND mv.owner<> 'XDB'
          AND mv.owner<> 'WMSYS'
          AND mv.owner<> 'MDSYS'
          AND mv.owner<> 'ORDSYS'
          AND mv.owner<> 'EXFSYS'
          AND mv.owner<> 'CUS_DBA'
          """

        return requete

    def getdatatype(self, datatype):
        """recupere le type interne associe a un type cx_oracle"""

        nom = datatype.name
        if nom not in TYPES_A:
            print("datatype inconnu", nom)
        return TYPES_A.get(nom, "T")

    def get_dateformat(self, nom):
        """formattage dates"""
        return "TO_CHAR(" + nom + ",'" + self.dateformat + "')"

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

    def execrequest(self, requete, data, attlist=None, regle=None):
        """passage de la requete sur la base"""
        cur = self.get_cursinfo()
        #        print ('ora:execution_requet',requete)
        try:
            cur.execute(requete, data, attlist=attlist, regle=regle)
            return cur
        except self.DBError as errs:
            cursor = cur.cursor
            (error,) = errs.args
            self.params.logger.error("erreur requete sur %s", self.base)
            self.params.logger.error("requete: %s (%s)", cursor.statement, str(data))
            self.params.logger.exception("erreur oracle", exc_info=errs)
            # print("error: oracle: erreur acces base ", self.base, self.connection)
            # print("error: oracle: erreur acces base ", cursor.statement, "-->", data)
            # print("error: oracle: variables ", cursor.bindnames())
            # print("Oracle-Error-Code:", error.code)
            # print("Oracle-Error-Message:", error.message)
            # print("Oracle-offset:", error.offset)
            # print("Oracle-context:", error.context)
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

        self.decile = int(cur.rowcount / 10) + 1
        #        print('decile recup', self.decile)
        if self.decile == 1:
            self.decile = 100000

        #        print('oracle:', requete, data)
        if not has_geom:
            return cur

        def cursiter():
            """iterateur sur le curseur oracle avec decodage de la geometrie"""
            while True:
                try:
                    elem = cur.cursor.fetchone()
                #                raise
                except self.DBError as err:
                    self.params.logger.error("erreur requete sur %s", self.base)
                    self.params.logger.error(
                        "requete: %s (%s)", cursor.statement, str(data)
                    )
                    self.params.logger.exception("erreur oracle", exc_info=err)
                    # print("erreur " + self.base, err)
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

    def get_elements_specifiques(self, schema):
        """recupere des elements specifiques a un format et les stocke dans
        une structure du schema"""
        debug = self.regle.istrue("debug")
        if debug:
            print("acces vues")
        schema.elements_specifiques["def_vues"] = self._def_vues()
        # if debug:
        #     print("acces triggers")
        # schema.elements_specifiques["def_triggers"] = self._def_triggers()
        # if debug:
        #     print("acces ftables")
        # schema.elements_specifiques["def_ftables"] = self._def_ftables()
        # if debug:
        #     print("acces fonctions")
        # schema.elements_specifiques["def_fonctions_trigger"] = self._def_f_trigger()
        # schema.elements_specifiques["def_fonctions"] = self._def_fonctions()
        # print(
        #     "elements specifiques",
        #     [(i, len(j[1])) for i, j in schema.elements_specifiques.items()],
        # )

    def _def_vues(self):
        entete = "schema;nom;definition;materialise"
        # print("requete vues", self.requetes["info_vues"])
        infos = self.request(self.requetes["info_vues"])
        vals = {(i[0], i[1]): (i[2], str(i[3])) for i in infos}
        # print("recup vues", len(vals))
        return (entete, vals)


class OraGenSql(DbGenSql):
    """creation des sql de modif de la base"""

    pass


DBDEF = {"oracle": (OraConnect, OraGenSql, "server", "", "", "base oracle standard")}
