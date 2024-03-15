# -*- coding: utf-8 -*-
"""
Acces aux bases de donnees via sqlalchemy

commandes disponibles :

    * lecture des structures et de droits
    * lecture des fonctions et des triggers et tables distantes gestion des clefs etrangeres
    * extraction multitables et par selection sur un attribut et par geometrie
    * ecriture de structures en fichier sql
    * ecritures de donnees au format copy et chargment en base par psql
    * passage de requetes sql
    * insert et updates en base '(beta)'

necessite la librairie psycopg2 et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:


"""
import os

# from pyetl.formats.mdbaccess import DbWriter

# import re
import subprocess
import re
from collections import namedtuple
from sqlalchemy import inspect, create_engine, URL

#
from .database import Cursinfo, DbConnect
from .init_sigli import requetes_sigli as REQS


# global psycopg2


# def importer():

#     import psycopg2


TYPES_A = {
    "T": "T",
    "": "T",
    "TEXTE": "T",
    "TEXT": "T",
    "ALPHA": "T",
    "NAME": "T",
    '"CHAR"': "T",
    "CHAR": "T",
    "CHARACTER": "T",
    "UUID": "T",
    "REGCLASS": "T",
    "CHARACTER VARYING": "T",
    "INFORMATION_SCHEMA.SQL_IDENTIFIER": "T",
    "INFORMATION_SCHEMA.CHARACTER_DATA": "T",
    "E": "E",
    "ENTIER": "E",
    "INTEGER": "E",
    "INT": "E",
    "INT2": "E",
    "INT4": "E",
    "EL": "EL",
    "INT8": "EL",
    "BIGINT": "EL",
    "LONG": "EL",
    "ENTIER_LONG": "EL",
    "D": "D",
    "DS": "DS",
    "DATE": "DS",
    "TIMESTAMP": "D",
    "TIMESTAMP WITHOUT TIME ZONE": "D",
    "TIMESTAMP WITH TIME ZONE": "D",
    "TIME WITHOUT TIME ZONE": "D",
    "TIME WITH TIME ZONE": "D",
    "F": "F",
    "FLOAT": "F",
    "FLOAT4": "F",
    "REEL": "F",
    "REAL": "F",
    "FLOTTANT": "F",
    "DECIMAL": "N",
    "H": "H",
    "HSTORE": "H",
    "DOUBLE PRECISION": "F",
    "NUMERIC": "N",
    "B": "B",
    "BOOLEEN": "B",
    "BOOLEAN": "B",
    "BOOL": "B",
    "CASE A COCHER": "B",
    "S": "S",
    "SEQUENCE": "S",
    "SEQ": "S",
    "SERIAL": "S",
    "BIGSERIAL": "BS",
    "I": "I",
    "SMALLINT": "I",
    "INTERVALLE": "I",
    "OID": "I",
    "JSON": "J",
    "JSONB": "J",
    "BYTEA": "BIN",
    "XML": "XML",
    "UNKNOWN": "T",
}
TYPES_PG = {
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
    "DS": "date",
    "ds": "date",
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
    "b": "boolean",
    "N": "numeric",
    "n": "numeric",
    "S": "serial NOT NULL",
    "BS": "bigserial NOT NULL",
    "J": "json",
    "XML": "XML",
    "XB": "bytea",
}
GTYPES_DISC = {
    "alpha": "",
    "ALPHA": "",
    "ponctuel": "geometry(point,3948)",
    "POINT": "geometry(point,3948)",
    "POINT MULTIPLE": "geometry(point,3948)",
    "POINT 3D": "geometry(pointz,3948)",
    "LIGNE": "geometry(linestring,3948)",
    "lineaire": "geometry(linestring,3948)",
    "lineaire MULTIPLE": "geometry(linestring,3948)",
    "LIGNE MULTIPLE": "geometry(multilinestring,3948)",
    "LIGNE 3D": "geometry(linestringZ,3948)",
    "LIGNE MULTIPLE 3D": "geometry(multilinestringZ,3948)",
    "POLYGONE": "geometry(polygon,3948)",
    "surfacique": "geometry(polygon,3948)",
    "surfacique MULTIPLE": "geometry(polygon,3948)",
    "POLYGONE 3D": "geometry(polygonZ,3948)",
    "POLYGONE MULTIPLE": "geometry(multipolygon,3948)",
    "POLYGONE MULTIPLE 3D": "geometry(multipolygonZ,3948)",
    "GEOMETRIE": "geometry",
    "GEOMETRIE MULTIPLE": "geometry",
    "GEOMETRIE MULTIPLE 3D": "geometry",
    "GEOMETRIE 3D": "geometry",
}
GTYPES_CURVE = {
    "alpha": "",
    "ALPHA": "",
    "ponctuel": "geometry(point,3948)",
    "POINT": "geometry(point,3948)",
    "POINT MULTIPLE": "geometry(point,3948)",
    "POINT 3D": "geometry(pointz,3948)",
    "LIGNE": "geometry(linestring,3948)",
    "lineaire": "geometry(linestring,3948)",
    "lineaire MULTIPLE": "geometry(linestring,3948)",
    "LIGNE MULTIPLE": "geometry(multicurve,3948)",
    "LIGNE 3D": "geometry(linestringZ,3948)",
    "LIGNE MULTIPLE 3D": "geometry(multicurveZ,3948)",
    "POLYGONE": "geometry(polygon,3948)",
    "surfacique": "geometry(polygon,3948)",
    "surfacique MULTIPLE": "geometry(polygon,3948)",
    "POLYGONE 3D": "geometry(polygonZ,3948)",
    "POLYGONE MULTIPLE": "geometry(multisurface,3948)",
    "POLYGONE MULTIPLE 3D": "geometry(multisurfaceZ,3948)",
    "GEOMETRIE": "geometry",
    "GEOMETRIE MULTIPLE": "geometry",
    "GEOMETRIE MULTIPLE 3D": "geometry",
    "GEOMETRIE 3D": "geometry",
}


class PgCursinfo(Cursinfo):
    @property
    def infoschema(self):
        """retourne le schema issu de la requete"""
        if self.schema_req:
            return self.schema_req
        if self.requete:
            tmp = self.requete.split("\n")
            tmprequete = "\n".join(tmp).strip()
            if tmprequete.endswith(";"):
                tmprequete = tmprequete[:-1]
            req = (
                "create TEMP TABLE tmp__0001 AS select * from ("
                + tmprequete
                + ") as x limit 0 "
            )
            attlist = None
            if self.execute(req, self.data, newcursor=True):
                # cursor = self.execute("select current_schemas('t')", newcursor=True)
                # temp_schema = cursor.fetchall()[0][0][0]
                # print("temp_schema", temp_schema)
                inforeq = (
                    REQS["info_attributs"].replace("AND n.nspname !~~ 'pg_%'::text", "")
                    + " WHERE t4.nomtable='tmp__0001'"
                )
                cursor = self.execute(inforeq, newcursor=True)
                retour = cursor.fetchall()
                attlist = [self.connecteur.attdef(*i) for i in retour]
                # on recupere la structure du schema temporaire
                # print("retour requete", "\n".join([repr(i) for i in attlist]))
                self.execute("drop TABLE pg_temp.tmp__0001", newcursor=True)
            self.schema_req = attlist
        return self.schema_req

    #    attlist.append((name, nomtype, internal_size, precision))


class AlcConnect(DbConnect):
    """connecteur de la base de donnees postgres"""

    reqs = REQS  # requetes de fallback pour les infos base
    requetes = reqs
    codecinfo = {"utf-8": "UTF8", "cp1252": "WIN1252"}
    requetes["info_tables"] = requetes["info_tables_ng"]

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        # importer()

        try:
            self.connect()
        except psycopg2.Error:
            self.connection = None
        self.types_base.update(TYPES_A)
        self.types_pg = TYPES_PG
        self.gtypes_curve = GTYPES_CURVE
        self.gtypes_disc = GTYPES_DISC
        self.load_helper = "prog_pgsql"
        self.sql_helper = "prog_pgsql"
        self.accept_sql = "alpha"
        if self.connection:
            self.set_searchpath()
            # self.connection.commit()
            style, ordre = self.datestyle()
            self.numtypes = self._getnumtypes()
            self.regle.setroot("dateordre", ordre)
            self.regle.setroot("datestyle", style)
        self.type_base = "postgres"
        self.dialecte = "postgres"
        self.logfile = ""
        self.DBError = psycopg2.Error

    def set_searchpath(self):
        """positionne les path pour la session"""
        cur = self.connection.cursor()
        cur.execute("select set_config('search_path','public',false)", ())
        cur.close()

    def get_cursinfo(self, volume=0, nom="", regle=None):
        """recupere un curseur"""
        # print(" postgres get cursinfo")
        return (
            PgCursinfo(self, volume=volume, nom=nom, regle=regle)
            if self.connection
            else None
        )

    def datestyle(self):
        """recupere la config de formattage de dates"""
        retour = self.request("show DateStyle")
        if retour:
            datestyle = retour.pop()[0].split(",")
            return map(str.strip, datestyle)
        return "ISO", "DMY"
        # print ('retour date', *datestyle)

    @staticmethod
    def change_antislash(nom):
        """remplace les \\ par des /"""
        return nom.replace("\\", "/")

    def extsql(self, prog, file, logfile=None, outfile=None):
        """execute un fichier sql"""
        serveur = " --".join(self.serveur.split(" "))
        chaine_connect = serveur + " --dbname=" + self.base
        file = self.change_antislash(file)
        # psql -h bcsigli -p 34000 -d sigli -U sigli -f script.sql --single-transaction -L script.log 2>> script.log
        if self.user:
            chaine_connect = chaine_connect + " --username=" + self.user
        if logfile:
            chaine_connect = chaine_connect + " -L " + logfile
        if outfile:
            outfile = self.change_antislash(outfile)
            chaine_connect = chaine_connect + " --outfile=" + outfile

        chaine = " --".join(
            (prog, "tuples-only", chaine_connect, 'file="' + file + '"')
        )
        # print("loader ", chaine)
        host = (
            [i for i in serveur.split(" ") if "host" in i].pop()
            if "host" in serveur
            else ""
        )
        logger = self.params.logger
        logger.info(
            "postgres: traitement sql %s %s " + os.path.basename(file), host, self.base
        )
        env = dict(os.environ)
        env["PGCLIENTENCODING"] = "UTF8"
        if self.passwd:
            env["PGPASSWORD"] = self.passwd
        if not logfile:
            logger.info("pas de fichier log : affichage console ")
            logger.debug("traitement %s", chaine)
            try:
                fini = subprocess.run(chaine, env=env)
            except Exception as err:
                logger.error("traitement %s", chaine)
                logger.error("erreur processus %s", repr(err))
                return
        else:
            if self.logfile != logfile:
                # print("pas  sorti")
                self.logfile = logfile
                logger.info("Le fichier de log se trouve la: %s", logfile)

            with open(logfile, "a") as sortie:
                fini = subprocess.run(
                    chaine, env=env, stdout=sortie, stderr=subprocess.STDOUT
                )
        if fini.returncode:
            logger.error(
                "erreur pgsql: %s , %s", repr(fini.returncode), repr(fini.args)
            )

            # print("postgres extsql:sortie en erreur ", fini.returncode, fini.args)

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        # try:
        #     import psycopg2
        # except ImportError:
        #     print("error: postgr2: erreur import module postgres")
        #     return None, None
        self.dbtyp = self.regle.getvar("dbengine")
        self.url_object = URL.create(
            self.dbtyp,
            username=self.user,
            password=self.passwd,
            host=self.serveur,
            database=self.base,
        )

        if self.base:
            chaine_connect = self.serveur + " dbname=" + self.base
        else:
            chaine_connect = "service=" + self.serveur
        if self.user:
            chaine_connect = chaine_connect + " user=" + self.user
        if self.passwd:
            chaine_connect = chaine_connect + " password=" + self.passwd
        #    print ('info:postgres: connection ', serveur,base,user,'*'*len(passwd))
        # print('connection',chaine_connect, self.requetes)
        try:
            connection = psycopg2.connect(chaine_connect)
            connection.autocommit = True
            self.connection = connection
        except psycopg2.Error as err:
            print("error: postgres: connection impossible ", err)
            self.params.logger.error("postgres: connection impossible " + repr(err))

            print(
                "info:  postgres: parametres ",
                self.serveur,
                self.base,
                self.user,
                # self.passwd,
                # chaine_connect
            )

            print("error", err)

            raise

    # traitement des elements specifiques

    def get_elements_specifiques(self, schema):
        """recupere des elements specifiques a un format et les stocke dans
        une structure du schema"""
        debug = self.regle.istrue("debug")
        if debug:
            print("acces vues")
        schema.elements_specifiques["def_vues"] = self._def_vues()
        if debug:
            print("acces triggers")
        schema.elements_specifiques["def_triggers"] = self._def_triggers()
        if debug:
            print("acces ftables")
        schema.elements_specifiques["def_ftables"] = self._def_ftables()
        if debug:
            print("acces fonctions")
        schema.elements_specifiques["def_fonctions_trigger"] = self._def_f_trigger()
        schema.elements_specifiques["def_fonctions"] = self._def_fonctions()
        schema.elements_specifiques["roles"] = self._get_roles()
        # print(
        #     "elements specifiques",
        #     [(i, len(j[1])) for i, j in schema.elements_specifiques.items()],
        # )

    def _def_vues(self):
        entete = "schema;nom;definition;materialise"
        infos = self.request(self.requetes["info_vues"])
        vals = {(i[0], i[1]): (i[2], str(i[3])) for i in infos}
        # print("recup vues", len(vals))
        return (entete, vals)

    def _def_f_trigger(self):
        entete = "schema;nom;definition"
        infos = self.request(self.requetes["def_fonctions_trigger"])
        vals = {(i[0], i[1]): i[2] for i in infos}
        return (entete, vals)

    def _def_fonctions(self):
        entete = "schema;nom;definition"
        infos = self.request(self.requetes["def_fonctions_utilisateur"])
        vals = {(i[0], i[1]): i[2] for i in infos}
        return (entete, vals)

    def _def_ftables(self):
        entete = "nom;serveur;definition"
        infos = self.request(self.requetes["info_tables_distantes"])
        vals = {i[0]: i[1:] for i in infos}
        return (entete, vals)

    def _getnumtypes(self):
        numtypes = {i: j for i, j in self.schemarequest("num_types")}
        # print ('recup numtypes',numtypes)
        return numtypes

    def getdatatype(self, datatype):
        """recupere le type interne associe a un type cx_oracle"""
        typebase = self.numtypes.get(datatype, "T").upper().strip("_")
        # print ('recup numtype',self.numtypes.get(datatype,'inconnu'), self.types_base.get(typebase))
        return self.types_base.get(typebase, "T")

    def _def_triggers(self):
        """recupere les definitions de triggers"""
        def_trigg = dict()
        entete = "schema;table;nom;type_trigger;action;declencheur;timing;event;colonnes;condition;sql"
        for i in self.request(self.reqs["info_triggers"]):
            #            print ('triggers',i)
            identtable = (i[0], i[1])
            nom = i[2]
            definition = list((str(j) for j in i[3:]))
            if identtable not in def_trigg:
                def_trigg[identtable] = dict()
            def_trigg[identtable][nom] = definition
        return entete, def_trigg

    #        print('pgr --------- selection info triggers ', len(triggers))
    def _get_roles(self):
        """recupere les roles de la base de donnees"""
        entete = "nom;roles;description;login"
        infos = self.request(self.requetes["info_roles"])
        liste_roles = {i[0]: (i[1], i[2]) for i in infos}
        return (entete, liste_roles)

    def get_type_from_connect(self, typecode):
        """recupere une information de type"""
        info = self.request("select format_type(" + typecode + ",0)", None)[0]
        return info

    def elemrestrict(self, elem, a_garder):
        """restreint les elements specifiques aux tables a garder"""
        if elem is None:
            return None
        entete, contenu = elem
        contenu = {i: j for i, j in contenu.items() if i in a_garder}
        return (entete, contenu)

    def select_elements_specifiques(self, schema, liste_tables):
        """selectionne les elements specifiques pour coller a une restriction de schema"""
        a_garder = set(liste_tables)
        els = schema.elements_specifiques
        # print("restriction elts spec avant", [(i, len(j[1])) for i, j in els.items()])
        els["def_vues"] = self.elemrestrict(els["def_vues"], a_garder)
        els["def_triggers"] = self.elemrestrict(els["def_triggers"], a_garder)
        els["def_ftables"] = self.elemrestrict(els["def_ftables"], a_garder)
        els["def_fonctions_trigger"] = self.elemrestrict(
            els["def_fonctions_trigger"], a_garder
        )
        # print("restriction elts spec apres", [(i, len(j[1])) for i, j in els.items()])

        fonctions_a_garder = set()
        for i in els["def_triggers"][1].values():
            for j in i.values():
                fonction = re.sub(r"(.*)\(.*\)", r"\1", j[1])
                fonctions_a_garder.add(tuple(fonction.split(".")))
        #        print('fonctions a garder', fonctions_a_garder)
        # if any(len(els[i][1]) for i in els):
        # print(
        #     "elements specifiques gardes", dict([(i, len(els[i][1])) for i in els])
        # )
        # print ("def trigger", els["def_triggers"])

    @property
    def req_tables(self):
        """recupere les tables de la base"""
        return self.requetes["info_tables_ng"], None

    @property
    def req_enums(self):
        """recupere les enums de la base"""
        return self.requetes["info_enums"], None

    @property
    def req_attributs(self):
        """recupere les attributs de la base"""
        return self.requetes["info_attributs"], None

    def get_type(self, nom_type):
        if "geometry" in nom_type:
            return nom_type
        return self.types_base.get(nom_type.upper(), "?")

    def set_limit(self, maxi, _):
        if maxi:
            return " limit " + str(maxi)
        return ""

    def get_attributs(self):
        """produit les objets issus de la base de donnees

        ('nom_groupe', 'nom_classe', 'nom_attr', 'alias', 'type_attr',
         'graphique', 'multiple', 'defaut', 'obligatoire', 'enum',
         'dimension', 'num_attribut', 'index', 'unique', 'clef_primaire',
         'clef_etrangere', 'cible_clef', 'parametres_clef', 'taille', 'decimales'))
        """
        requete, data = self.req_attributs
        # print('pgattributs', requete)
        attributs = self.request(requete, data)
        # print('pgattributs fait')

        # on corrige les types et les tailles
        retour = []
        for i in attributs:
            taille = 0
            dec = 0
            tmp0 = list(i)
            if "[]" in i[4]:  # attributs multiples (tableaux)
                tmp0[6] = "oui"
                tmp0[4] = i[4].replace("[]", "")

            if "(" in i[4]:
                tmp1 = tmp0[4].split("(")
                tmp2 = tmp1[1].replace(")", "").split(",")
                if tmp2[0].isnumeric():
                    tmp0[4] = tmp1[0]
                    taille = int(tmp2[0])
                    if len(tmp2) == 2 and tmp2[1].isnumeric():
                        dec = int(tmp2[1])
            #                    print ('detection taille ',i[4],taille,dec)
            tmp0[18] = taille
            tmp0[19] = dec
            atd = self.attdef(*tmp0)
            yield (atd)
        #            if taille != 0:
        #                print ('attributs pg',i)
        # return retour

    @property
    def get_join_char(self):
        """chaine de jonction entre attributs"""
        return "::text,"

    def textcast(self, nom):
        """forcage text"""
        return nom + "::text"

    def datecast(self, nom):
        """forcage date"""
        return nom + "::timestamp"

    def numcast(self, nom):
        """forcage numerique"""
        return nom + "::float"

    def intcast(self, nom):
        """forcage entier"""
        return nom + "::int"

    def multivaldata(self, valeurs):
        """formate les donnes pour les requetes sur les listes"""
        return {"val": "{" + ",".join(valeurs) + "}"}

    def multival(self, taille, operateur="=", cast=None):
        """acces listes"""
        return " " + operateur + " ANY (%(val)s)"

    def monoval(self, operateur="=", cast=None):
        """acces valeur"""
        if cast is not None:
            return " " + operateur + " " + cast("%(val)s")
        return " " + operateur + " %(val)s"

    def extload(self, helper, files, logfile=None, reinit="0", vgeom="1"):
        """charge un fichier par copy"""
        serveur = " --".join(self.serveur.split(" "))
        chaine_connect = serveur + " --dbname=" + self.base

        if self.user:
            chaine_connect = chaine_connect + " --username=" + self.user
        if logfile:
            chaine_connect = chaine_connect + " --log-file=" + logfile + " --quiet"

        #  \copy  table [ ( column_list ) ] from 'filename' [ with ( option [, ...] ) ]

        for file in files:
            chaine = " --".join((helper, chaine_connect, "file=" + file))
            #        print ('loader ', chaine)
            env = dict(os.environ)
            env["PGCLIENTENCODING"] = "UTF8"
            if self.passwd:
                env["PGPASSWORD"] = self.passwd
            fini = subprocess.run(chaine, env=env)
            if fini.returncode:
                print("sortie en erreur ", fini.returncode, fini.args, fini.stderr)

    def dbloadfile(self, schema, ident, fichier):
        """charge un fichier par copy"""
        cur = self.connection.cursor()
        colonnes = tuple(schema.classes[ident].get_liste_attributs())
        nom = ".".join(ident)
        with open(fichier) as infile:
            try:
                cur.copy_from(infile, nom, columns=colonnes, sep="\t")
                cur.close()
                return True
            except Exception as erreur:
                print("error: sigli: chargement ", fichier, "-->", erreur)
                cur.close()
                return False

    def dbload(self, schemaclasse, ident, source):
        """charge des objets en base de donnees par dbload"""
        cur = self.connection.cursor()
        colonnes = tuple(schemaclasse.get_liste_attributs())
        nom = ".".join(ident)
        try:
            cur.copy_from(source, nom, columns=colonnes, sep="\t")
            cur.close()
            return True
        except Exception as erreur:
            print("error: sigli: chargement ", ident, "-->", erreur)
            cur.close()
            return False

    # structures specifiques pour stocker les scrips en base
    # cree 4 tables: Macros scripts batchs logs

    def init_pyetl_script(self, nom_schema):
        """cree les structures standard"""
        pass


class AlcGenSql(object):
    pass


# class PostgresWriter(DbWriter):
#     """gestion des ecritures directes en base"""

#     pass
"""acces,gensql,svtyp,fileext,geom,description,
        "converter",
        "geomwriter",
        "doc",
        "module",
    )"""

DBDEF = {
    "sqlalc": (
        AlcConnect,
        AlcGenSql,
        "server",
        "",
        "#ewkt",
        "acces sqlalchemy",
    )
}
