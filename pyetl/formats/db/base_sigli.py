# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
from .base_postgis import PgsConnect, PgsGenSql

# from .init_sigli import requetes_sigli as REQS
# from . import database

SCHEMA_ADM = "admin_sigli"


class SglConnect(PgsConnect):
    """connecteur de la base de donnees postgres"""
    fallback = PgsConnect.requetes
    # requetes = {
    # "info_schemas":"SELECT nomschema,commentaire FROM admin_sigli.info_schemas",
    # "info_tables":"""SELECT nomschema,nomtable,commentaire,type_geometrique,dimension,
    #                    nb_enreg,type_table,index_geometrique,clef_primaire,index,
    #                    clef_etrangere
    #             FROM admin_sigli.info_tables""",
    # "info_enums": "SELECT nom_enum,ordre,valeur,alias,mode FROM admin_sigli.info_enums",
    # "info_attributs": """SELECT nomschema, nomtable, attribut, alias, type_attribut, graphique,
    #                        multiple, defaut, obligatoire, enum, dimension, num_attribut,
    #                        index, uniq, clef_primaire, clef_etrangere, cible_clef, 0, 0
    #                 FROM admin_sigli.info_attributs order by nomschema, nomtable, num_attribut""",
    # "info_vues": """SELECT nomschema,nomtable,definition,materialise
    #            FROM admin_sigli.info_vues_utilisateur"""
    #               }


    def __init__(self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None):
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
        requete = """SELECT nomschema,nomtable,definition,materialise
                     from admin_sigli.info_vues_utilisateur
                     """
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
            "SELECT admin_sigli.truncate_table('"
            + niveau.lower()
            + "','"
            + classe.lower()
            + "');\n"
        )

    @staticmethod
    def _commande_sequence(niveau, classe):
        """ cree une commande de reinitialisation des sequences"""
        return (
            "SELECT admin_sigli.ajuste_sequence('"
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
                "SELECT admin_sigli.valide_triggers('"
                + niveau.lower()
                + "','"
                + classe.lower()
                + "');\n"
            )
        return (
            "SELECT admin_sigli.devalide_triggers('"
            + niveau.lower()
            + "','"
            + classe.lower()
            + "');\n"
        )


DBDEF = {"sigli": (SglConnect, SglGenSql, "server", "", "#ewkt", "base postgis avec admin_sigli")}
