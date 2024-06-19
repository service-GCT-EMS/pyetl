# -*- coding: utf-8 -*-

"""
Acces aux bases de donnees oracle spatial (locator)

commandes disponibles :

    * lecture des structures
    * extraction multitables et par selection sur un attribut ou geometrique

necessite la librairie cx_Oracle et un client oracle 64 bits

il est necessaire de positionner les parametres suivant:


"""

from .base_oracle import OraConnect, OraGenSql
oracle=None
try:
    import oracledb as oracle
except ImportError:
    try:
        import cx_Oracle as oracle
    except ImportError:
        pass

TYPES_A = {"SDO_GEOMETRY": "GEOMETRIE"}
# global cx_Oracle


# def importer():

#     import cx_Oracle


class OrwConnect(OraConnect):
    """connecteur de la base de donnees oracle"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        # importer()

        self.types_base.update(TYPES_A)
        self.accept_sql = "geo"
        self.type_base = "oracle_spatial"

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
        return requete, ()

    @property
    def req_attributs(self):
        """recupere le schema complet avec tous ses champs
        nomschema,nomtable,attribut,alias,type_attribut,graphique,multiple,
        defaut,obligatoire,enum,dimension,num_attribut,index,uniq,
        clef_primaire,clef_etrangere,cible_clef,parametres,taille,decimales"""
        requete = """
        SELECT DISTINCT   col.owner as nomschema,
                col.table_name as nomtable,
                col.column_name as attribut,
                CASE WHEN com.comments IS NOT NULL THEN com.comments
                    ELSE ''
                    END AS alias,
                CASE WHEN col.data_type = 'NUMBER' AND col.data_scale = 0 THEN 'E'
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
                (select ic.column_position from all_ind_columns ic where table_name=col.table_name and col.owner=owner and col.cilumn_name=column_name) as index,
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

        return requete, ()

    def get_surf(self, nom):
        """calcul de surface"""
        return "SDO_GEOM.SDO_AREA(%s,0.001)" % nom

    def get_perim(self, nom):
        """calcul de perimetre"""
        return "SDO_GEOM.SDO_LENGTH(%s,0.001)" % nom

    def get_long(self, nom):
        """calcul de longueur"""
        return "SDO_GEOM.SDO_LENGTH(%s,0.001)" % nom

    def get_geom(self, nom):
        """recup de la geometrie en WKT"""
        return "SDO_UTIL.TO_WKTGEOMETRY(%s)" % nom

    def set_geom(self, geom, srid):
        """cree une geometrie"""
        return "SDO_GEOMETRY('%s',%s)" % (geom, srid)

    def set_geomb(self, geom, srid, buffer):
        """cree un buffer"""
        return "SDO_GEOMETRY('%s',%s,%f,0.001))" % (geom, srid, buffer)

    def cond_geom(self, nom_fonction, nom_geometrie, geom2):
        """definition d'ne condition geometrique"""
        if nom_fonction == "dans_emprise":
            cond = (
                "SDO_FILTER("
                + nom_geometrie
                + ","
                + geom2
                + "','querytype=WINDOW') = 'TRUE'"
            )
        else:
            masque = ""
            if nom_fonction == "intersect":
                masque = "anyinteract"
            elif nom_fonction == "dans":
                masque = "coveredby+inside"
            cond = (
                "SDO_RELATE("
                + nom_geometrie
                + ","
                + geom2
                + ",'mask="
                + masque
                + "') = 'TRUE'"
            )
        return cond

    def connect(self):
        if self.connection:
            return
        super().connect()
        if not self.connection:
            raise StopIteration(3)

        def output_type_handler(cursor, name, default_type, size, precision, scale):
            if default_type == oracle.BLOB:
                return cursor.var(oracle.LONG_BINARY, arraysize=cursor.arraysize)

        self.connection.outputtypehandler = output_type_handler


class OrwGenSql(OraGenSql):
    """creation des sql de modif de la base"""

    pass


DBDEF = {
    "oracle_spatial_ewkt": (
        OrwConnect,
        OrwGenSql,
        "server",
        "",
        "#ewkt",
        "base oracle spatial (format ewkt)",
    )
}
