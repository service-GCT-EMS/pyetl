# -*- coding: utf-8 -*-

"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
import re
import time

from collections import namedtuple
from .dbconstants import *


class DbGenSql(object):
    """classe de generation des structures sql"""

    def __init__(self, connection=None, basic=False):
        self.geom = True
        self.courbes = False
        self.schemas = True
        self.reserves = RESERVES  # mots reserves et leur remplacement
        self.remplace = REMPLACE  # mots reserves et leur remplacement
        self.types_db = {
            "T": "text",
            "texte": "text",
            "": "text",
            "t": "text",
            "A": "text",
            "E": "integer",
            "entier": "integer",
            "EL": "bigint",
            "el": "bigint",
            "entier_long": "bigint",
            "D": "timestamp",
            "d": "timestamp",
            "H": "hstore",
            "h": "hstore",
            "hstore": "hstore",
            "F": "float",
            "reel": "float",
            "float": "float",
            "flottant": "float",
            "f": "float",
            "date": "timestamp",
            "booleen": "boolean",
            "B": "boolean",
            "S": "serial NOT NULL",
            "BS": "bigserial NOT NULL",
        }
        if basic:
            self.types_db["S"] = "integer"
            self.types_db["BS"] = "bigint"
        #        self.typenum = {'1':"POINT", '2':"LIGNE", '3':"POLYGONE",
        #                        '-1':"GEOMETRIE", '0':"ALPHA", 'indef':'ALPHA'}
        self.typenum = TYPENUM
        self.gtypes_disc = GTYPES_DISC
        self.gtypes_curve = GTYPES_CURVE
        self.types_base = TYPES_A
        self.dialecte = "sql"
        self.schema_conf = "public"

        self.connection = connection
        self.basic = basic
        self.schema = None
        self.regle_ref = None

    def setbasic(self, mode):
        """mode basic pour les bases de consultation"""
        if mode:
            self.basic = mode
            self.types_db["S"] = "integer"
            self.types_db["BS"] = "bigint"

    def initschema(self, schema, mode="All"):
        """schema courant"""

        self.schema = schema

    def conf_en_base(self, conf):
        """valide si uneconformiteexisteen base"""
        return False, False

    def ajuste_nom(self, nom):
        """ sort les caracteres speciaux des noms"""
        nom = re.sub(
            "[" + "".join(sorted(self.remplace.keys())) + "]",
            lambda x: self.remplace[x.group(0)],
            nom,
        )
        nom = self.reserves.get(nom, nom)
        return nom

    def ajuste_nom_q(self, nom):
        """ sort les caracteres speciaux des noms et rajoute des quotes"""
        return quote(self.ajuste_nom(nom))

    def valide_base(self, conf):
        """valide un schema en base"""
        return False

    def prepare_conformites(self, nom_conf, schema=None):
        """prepare une conformite et verifie qu'elle fait partie de la base sinon la cree
        non defini pour une base generique """

        return False, ""

    def cree_indexes(self, schemaclasse, groupe, nom):
        """creation des indexes"""
        ctr = []
        idx = ["-- ###### creation des indexes #######"]

        return ctr, idx

    def cree_fks(self, ident):
        """ cree les definitions des foreign keys """
        return []

    def cree_comments(self, classe, groupe, nom):
        """ cree les definitions commentaires """
        return []

    def cree_triggers(self, classe, groupe, nom):
        """ cree les triggers """
        return []

    def get_nom_base(self, ident):
        """ adapte les noms a la base de donnees """
        classe = self.schema.classes[ident]
        nom = self.ajuste_nom(classe.nom.lower())
        groupe = self.ajuste_nom(classe.groupe.lower())
        return groupe, nom

    def cree_tables(self, ident, creconf):
        """ genere le sql de creation de table """
        schema = self.schema
        # contraintes de clef etrangeres : on les fait a la fin pour que toutes les tables existent
        print(" sql brut: traitement classe ", ident)
        #        raise
        schemaclasse = self.schema.classes[ident]
        groupe, nom = self.get_nom_base(ident)
        table = quote_table((groupe, nom))
        atts = schemaclasse.get_liste_attributs()
        type_geom = schemaclasse.info["type_geom"]

        if type_geom != "0":
            geomt = type_geom
            if geomt.upper() == "ALPHA":
                return 0, False
            if geomt in self.typenum:
                geomt = self.typenum[geomt]  # traitement des types numeriques
            if schemaclasse.multigeom:
                geomt = geomt + " MULTIPLE"
            if schemaclasse.info["dimension"] == "3":
                geomt = geomt + " 3D"
        cretable = []

        cretable.append(
            "\n-- ############## creation table " + table + "###############\n"
        )

        cretable.append("CREATE TABLE " + table + "\n(")
        for j in atts:
            deftype = "text"
            sql_conf = ""
            attribut = schemaclasse.attributs[j]
            attname = attribut.nom.lower()
            attname = quote(self.reserves.get(attname, attname))
            attype = attribut.type_att
            #            print ('lecture type_attribut',an,at)
            defaut = (
                " DEFAULT " + attribut.defaut
                if attribut.defaut and attribut.defaut[0] != "!"
                else ""
            )
            if (
                attribut.defaut == "S" or attype == "S"
            ):  # on est en presence d'un serial'
                attype = "integer"
            conf = attribut.conformite
            if conf:
                attype = "text"

            if re.search(r"^t[0-9]+$", attype):
                attype = "texte"
            if re.search(r"^e[1-6]s*$", attype):
                attype = "integer"
            if re.search(r"^e[0-9]+_[0-9]+$", attype):
                attype = "integer"
            if re.search(r"^e[7-9]s*$", attype):
                attype = "integer"
            # on essaye de gerer les clefs et les sequences les types et les defauts:
            #            print ("gensql, attribut ",an,at,conf)

            elif attype in schema.conformites:
                attype = "text"
            else:
                pass

            #            if at not in self.types_db and deftype not in self.types_db:
            #                print ('type inconnu',at,deftype,'par defaut')
            cretable.append(
                "\t" + attname + " " + self.types_db.get(attype, deftype) + defaut + ","
            )
            if sql_conf:
                creconf[attype] = sql_conf
        if type_geom != "0":
            cretable.append("\tgeometrie text,")

        # contraintes et indexes
        ctr, idx = self.cree_indexes(schemaclasse, groupe, nom)

        if ctr:
            cretable.extend(ctr)

        if cretable[-1][-1] == ",":
            cretable[-1] = cretable[-1][:-1]
        cretable.append(")")
        cretable.append("WITH (OIDS=FALSE);")
        # on choisit les bons indexes:
        cretable.extend(idx)
        #        cretable.extend(self.cree_fks(classe, groupe, nom))
        cretable.extend(self.cree_triggers(schemaclasse, groupe, nom))
        cretable.extend(self.cree_comments(schemaclasse, groupe, nom))

        # creation des commentaires :

        return "\n".join(cretable)

    def creschemas(self, liste):
        """creation des schemas"""
        schemas = set()
        for ident in liste:
            groupe, _ = self.get_nom_base(ident)
            schemas.add(groupe)
        creschema = ["CREATE SCHEMA IF NOT EXISTS" + i + ";" for i in schemas]
        dropschema = ["DROP SCHEMA " + i + ";" for i in schemas]
        return creschema, dropschema, []

    def droptables(self, liste):
        """ nettoyage """
        drop = []
        for ident in liste:
            groupe, nom = self.get_nom_base(ident)
            table = quote_table((groupe, nom))
            drop.append("DROP TABLE " + table + ";")
        return drop

    def dropconf(self, liste_confs):
        """sql de suppression des types """
        return ["DROP TYPE " + self.schema_conf + "." + i + ";" for i in liste_confs]

    def sio_cretable(self, cod="utf-8", liste=None, autopk=False, role=None):
        """sortie des sql pour la creation des tables"""
        creconf = dict()
        dbcod = cod
        if self.connection:
            dbcod = self.connection.codecinfo.get(cod, cod)
        codecinfo = (
            "-- ########### encodage fichier "
            + cod
            + "->"
            + dbcod
            + " ###(controle éèàç)#####\n"
        )
        if liste is None:
            liste = list(
                [i for i in self.schema.classes if self.schema.classes[i].a_sortir]
            )

        liste_tables = liste

        #       for i in liste_tables:
        #            print('type :',i,self.schema.classes[i].type_table)
        print("definition de tables a sortir:", len(liste_tables), self.dialecte)
        print(
            "tables non sorties:",
            list(
                [i for i in self.schema.classes if not self.schema.classes[i].a_sortir]
            ),
        )
        cretables = [
            codecinfo,
            "\n-- ########### definition des tables ###############\n",
        ]
        cretables.extend(
            list([self.cree_tables(ident, creconf) for ident in liste_tables])
        )

        if self.basic != "basic":
            for ident in liste:
                cretables.extend(self.cree_fks(ident))

        droptables = self.droptables(liste_tables)

        creconfs = list(creconf.values())
        dropconfs = self.dropconf(creconf.keys())
        creconfs.insert(0, codecinfo)
        return cretables, droptables, creconfs, dropconfs

    def sio_creschema(self, cod="utf-8", liste=None):
        """sortie des sql pour la creation des schemas de base"""
        if liste is None:
            liste = [i for i in self.schema.classes if self.schema.classes[i].a_sortir]
        #        print ('------------------------------sio creschema',liste)
        return self.creschemas(liste)

    def sio_crestyle(self, cod="utf-8", liste=None):
        """ styles : pas par defaut"""
        return []

    # structures specifiques pour stocker les scrips en base
    # cree 4 tables: Macros scripts batchs logs

    def init_pyetl_script(self, nom_schema):
        """ cree les structures standard"""
        pass
