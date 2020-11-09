# -*- coding: utf-8 -*-
"""
Acces aux bases de donnees postgis

commandes disponibles :

    * lecture des structures et de droits
    * lecture des fonctions et des triggers et tables distantes gestion des clefs etrangeres
    * extraction multitables et par selection sur un attribut et par geometrie
    * ecriture de structures en fichier sql
    * ecritures de donnees au format copy et chargment en base par psql
    * passage de requetes sql
    * insert et updates en base '(beta)'
    * cree des styles qgis pqs defaut pour les classes en sortie

necessite la librairie psycopg2 et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:


"""

from time import strftime
from .base_postgis import PgsConnect, PgsGenSql

# from .init_sigli import requetes_sigli as REQS
# from . import database

SCHEMA_ADM = "admin_sigli"
TABLE_MONITORING = SCHEMA_ADM + ".stats_upload"


class SglConnect(PgsConnect):
    """connecteur de la base de donnees postgres"""

    fallback = PgsConnect.requetes

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.sys_cre = "date_creation"
        self.sys_mod = "date_maj"
        self.dialecte = "sigli"
        self.type_base = "sigli"
        self.schema_conf = SCHEMA_ADM
        # print ('init sigli', self.requetes)

    def spec_def_vues(self):
        """recupere des informations sur la structure des vues
           (pour la reproduction des schemas en sql"""
        requete = (
            """SELECT nomschema,nomtable,definition,materialise
                     from """
            + SCHEMA_ADM
            + """.info_vues_utilisateur
                     """
        )
        vues = dict()
        vues_mat = dict()
        for i in self.request(requete, ()):
            ident = (i[0], i[1])
            if i[3]:
                vues_mat[ident] = i[2]
            else:
                vues[ident] = i[2]

        #        print('sigli --------- selection info vues ', len(vues), len(vues_mat))
        return vues, vues_mat


class SglGenSql(PgsGenSql):
    """classe de generation des structures sql"""

    def __init__(self, connection=None, basic=False):
        super().__init__(connection=connection, basic=basic)
        self.geom = True
        self.courbes = False
        self.schemas = True

        self.dialecte = "sigli"
        self.defaut_schema = SCHEMA_ADM
        self.schema_conf = SCHEMA_ADM

    # scripts de creation de tables

    def db_cree_table(self, schema, ident):
        """creation d' une tables en direct """
        req = self.cree_tables(schema, ident)
        if self.connection:
            return self.connection.request(req, ())

    def db_cree_tables(self, schema, liste):
        """creation d'une liste de tables en direct"""
        if not liste:
            liste = [i for i in self.schema.classes if self.schema.classes[i].a_sortir]
        for ident in liste:
            self.db_cree_table(schema, ident)

    # structures specifiques pour stocker les scrips en base
    # cree 4 tables: Macros scripts batchs logs

    def init_pyetl_script(self, nom_schema):
        """ cree les structures standard"""
        pass

    @staticmethod
    def _commande_reinit(niveau, classe, delete):
        """commande de reinitialisation de la table"""
        #        prefix = 'TRUNCATE TABLE "'+niveau.lower()+'"."'+classe.lower()+'";\n'

        if delete:
            return 'DELETE FROM "' + niveau.lower() + '"."' + classe.lower() + '";\n'
        return (
            "SELECT "
            + SCHEMA_ADM
            + ".truncate_table('"
            + niveau.lower()
            + "','"
            + classe.lower()
            + "');\n"
        )

    @staticmethod
    def _commande_sequence(niveau, classe):
        """ cree une commande de reinitialisation des sequences"""
        return (
            "SELECT "
            + SCHEMA_ADM
            + ".ajuste_sequence('"
            + niveau.lower()
            + "','"
            + classe.lower()
            + "');\n"
        )

    @staticmethod
    def _commande_trigger(niveau, classe, valide):
        """ cree une commande de reinitialisation des sequences"""
        if valide:
            return (
                "SELECT "
                + SCHEMA_ADM
                + ".valide_triggers('"
                + niveau.lower()
                + "','"
                + classe.lower()
                + "');\n"
            )
        return (
            "SELECT "
            + SCHEMA_ADM
            + ".devalide_triggers('"
            + niveau.lower()
            + "','"
            + classe.lower()
            + "');\n"
        )

    def _commande_monitoring(self, niveau, classe, schema, mode):
        """ insere une ligne dans une table de stats"""
        regle_ref = self.connection.regle if self.connection else self.regle_ref
        # print ('monitoring', regle_ref)
        if regle_ref:
            table_monitoring = regle_ref.getvar("table_monitoring", TABLE_MONITORING)
        else:
            table_monitoring = TABLE_MONITORING
        objcnt = (
            "(SELECT COUNT(*) FROM %s.%s)" % (niveau.lower(), classe.lower())
            if ("T" in mode or "D" in mode)
            else "'%d'" % (schema.objcnt,)
        )
        ligne = (
            "INSERT INTO "
            + table_monitoring
            + " (nomschema, nomtable, nbvals, mode_chargement, nom_script, date_export)"
            + " VALUES('%s','%s',%s,'%s','%s','%s');\n"
            % (
                niveau.lower(),
                classe.lower(),
                objcnt,
                mode,
                regle_ref.getvar("_nom_batch") if regle_ref else "",
                strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        # print ('cm:',ligne)
        # print ('cm:regle', regle_ref)
        return ligne

    def cree_triggers(self, classe, groupe, nom):
        """ cree les triggers """
        evs = {"B": "BEFORE ", "A": "AFTER ", "I": "INSTEAD OF"}
        evs2 = {"I": "INSERT ", "D": "DELETE ", "U": "UPDATE ", "T": "TRUNCATE"}
        ttype = {"T": "TRIGGER", "C": "CONSTRAINT"}
        decl = {"R": "ROW", "S": "STATEMENT"}
        table = groupe + "." + nom
        if self.basic:
            return []
        trig = ["-- ###### definition des triggers ####"]
        if self.maj:
            atts = {i.lower() for i in classe.get_liste_attributs()}
            trig_std = "auteur" in atts and "date_maj" in atts
            #       for i in atts:
            #           if i.defaut[0:1]=='A:': # definition d'un trigger
            #               liste_triggers[i.nom]=i.defaut[2:]
            if trig_std:
                trig.append("CREATE TRIGGER tr_auteur")
                trig.append("\tBEFORE UPDATE")
                trig.append("\tON " + table)
                trig.append("\tFOR EACH ROW")
                trig.append("\tEXECUTE PROCEDURE " + SCHEMA_ADM + ".auteur();")
        liste_triggers = classe.triggers
        for i in liste_triggers:
            type_trigger, action, declencheur, timing, event, colonnes, condition, sql = liste_triggers[
                i
            ].split(
                ","
            )
            trigdef = (
                ttype[type_trigger],
                action,
                decl[declencheur],
                evs[timing],
                evs2[event],
                colonnes,
                condition,
                sql,
            )
            idfonc, trigsql = self.cree_sql_trigger(i, table, trigdef)
            trig.extend(trigsql)
        return trig

    # scripts de creation de tables
    def sio_crestyle(self, liste=None):
        """ genere les styles de saisie"""
        conf = True
        if self.basic == "basic":
            return []
        if liste is None:
            liste = [i for i in self.schema.classes if self.schema.classes[i].a_sortir]
        declaration = []
        for ident in liste:

            groupe, nom = self.get_nom_base(ident)
            nom_style, style = self.prepare_style(ident, conf)
            sql1 = (
                "INSERT INTO public.layer_styles (f_table_catalog,f_table_schema,"
                + "f_table_name,f_geometry_column,stylename,useasdefault) "
                + "SELECT (select catalog_name from information_schema.schemata"
                + " where schema_name='"
                + groupe
                + "'),'"
                + groupe
                + "','"
                + nom
                + "'"
                + ",'geometrie','"
                + nom_style
                + "','TRUE'\n WHERE NOT EXISTS (\n"
                + "SELECT * from public.layer_styles WHERE stylename='"
                + nom_style
                + "');"
            )
            sql2 = (
                "UPDATE public.layer_styles SET styleqml = XMLPARSE(DOCUMENT '"
                + style
                + "') WHERE stylename='"
                + nom_style
                + "';"
            )
            declaration.extend((sql1, sql2))
        return declaration


DBDEF = {
    "sigli": (
        SglConnect,
        SglGenSql,
        "server",
        "",
        "#ewkt",
        "base postgis avec " + SCHEMA_ADM,
    )
}
