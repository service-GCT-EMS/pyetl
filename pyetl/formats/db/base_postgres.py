# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
import os

# import re
import subprocess
import re
from collections import namedtuple
from .database import DbConnect
from .postgres_gensql import PgrGenSql
from .init_sigli import requetes_sigli as REQS

TYPES_A = {
    "T": "T",
    "": "T",
    "TEXTE": "T",
    "TEXT": "T",
    "ALPHA": "T",
    "NAME": "T",
    '"CHAR"': "T",
    "REGCLASS": "T",
    "E": "E",
    "ENTIER": "E",
    "INTEGER": "E",
    "INT": "E",
    "EL": "EL",
    "BIGINT": "EL",
    "LONG": "EL",
    "ENTIER_LONG": "EL",
    "D": "D",
    "DATE": "D",
    "TIMESTAMP": "D",
    "TIMESTAMP WITHOUT TIME ZONE": "D",
    "TIME WITHOUT TIME ZONE": "D",
    "F": "F",
    "FLOAT": "F",
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
    "CASE_A_COCHER": "B",
    "S": "S",
    "SEQUENCE": "S",
    "SEQ": "S",
    "SERIAL": "S",
    "BIGSERIAL": "BS",
    "I": "I",
    "SMALLINT": "I",
    "INTERVALLE": "I",
    "OID": "I",
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


class PgrConnect(DbConnect):
    """connecteur de la base de donnees postgres"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.connect()
        self.types_base.update(TYPES_A)
        self.types_pg = TYPES_PG
        self.gtypes_curve = GTYPES_CURVE
        self.gtypes_disc = GTYPES_DISC
        self.rowcount = 0
        self.codecinfo = {"utf-8": "UTF8", "cp1252": "WIN1252"}
        self.load_helper = "prog_pgsql"
        self.sql_helper = "prog_pgsql"
        self.accept_sql = "alpha"
        self.valide = False
        if self.connection:
            self.set_searchpath()
            self.valide = True
        self.dialecte = "postgres"
        self.attdef = namedtuple(
            "attdef",
            (
                "nom_groupe",
                "nom_classe",
                "nom_attr",
                "alias",
                "type_attr",
                "graphique",
                "multiple",
                "defaut",
                "obligatoire",
                "enum",
                "dimension",
                "num_attribut",
                "index",
                "unique",
                "clef_primaire",
                "clef_etrangere",
                "cible_clef",
                "parametres_clef",
                "taille",
                "decimales",
            ),
        )

    def set_searchpath(self):
        """positionne les path pour la session"""
        cur = self.connection.cursor()
        #    print ('dbaccess:requete de selection table', cur.mogrify(requete,data))
        cur.execute("select set_config('search_path' , 'public',False)", ())
        cur.close()

    def runsql(self, prog, file, logfile=None, outfile=None):
        """execute un fichier sql"""
        serveur = " --".join(self.serveur.split(" "))
        chaine_connect = serveur + " --dbname=" + self.base

        if self.user:
            chaine_connect = chaine_connect + " --username=" + self.user
        if logfile:
            chaine_connect = chaine_connect + " -q -a"
        if outfile:
            chaine_connect = chaine_connect + " --outfile=" + outfile

        chaine = " --".join((prog, chaine_connect, "file=" + file))
        print("loader ", chaine)
        env = dict(os.environ)
        env["PGCLIENTENCODING"] = "UTF8"
        if self.passwd:
            env["PGPASSWORD"] = self.passwd
        if not logfile:
            print("pas de fichier log : affichage console")
            fini = subprocess.run(chaine, env=env, stderr=subprocess.STDOUT)
        else:
            print("Le fichier de log se trouve la:", logfile)
            with open(logfile, "a") as sortie:
                fini = subprocess.run(
                    chaine, env=env, stdout=sortie, stderr=subprocess.STDOUT
                )
        if fini.returncode:
            print("sortie en erreur ", fini.returncode, fini.args)

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        try:
            import psycopg2
        except ImportError:
            print("error: postgr2: erreur import module postgres")
            return None, None
        if self.base:
            chaine_connect = self.serveur + " dbname=" + self.base
        else:
            chaine_connect = "service=" + self.serveur
        if self.user:
            chaine_connect = chaine_connect + " user=" + self.user
        if self.passwd:
            chaine_connect = chaine_connect + " password=" + self.passwd
        #    print ('info:postgres: connection ', serveur,base,user,'*'*len(passwd))
        try:
            connection = psycopg2.connect(chaine_connect)
            connection.autocommit = True
            self.connection = connection
        except psycopg2.Error as err:
            print("error: postgres: connection impossible ")
            print(
                "info:  postgres: parametres ",
                self.serveur,
                self.base,
                self.user,
                self.passwd,
            )
            print("error", err)

    #        raise
    # traitement des elements specifiques

    def get_elements_specifiques(self, schema):
        """ recupere des elements specifiques a un format et les stocke dans
        une structure du schema """
        schema.elements_specifiques["def_vues"] = self._def_vues()
        schema.elements_specifiques["def_triggers"] = self._def_triggers()
        schema.elements_specifiques["def_ftables"] = self._def_ftables()
        schema.elements_specifiques[
            "def_fonctions_trigger"
        ] = self._def_fonctions_trigger()

    #        print (list(i for i in self._def_fonction_triggers() if "admin_sigli" in i))

    def _def_vues(self):
        return {(i[0], i[1]): (i[2], i[3]) for i in self.request(REQS["info_vues"])}

    def _def_fonctions_trigger(self):
        return {(i[0], i[1]): i[2] for i in self.request(REQS["def_fonctions_trigger"])}

    def _def_ftables(self):
        return {i[0]: i[1:] for i in self.request(REQS["info_tables_distantes"])}

    def _def_triggers(self):
        def_trigg = dict()
        #        print ('triggers')
        #        print (self.request(REQS["info_triggers"]))
        def_trigg["_header"] = [
            "table",
            "nom",
            "condition",
            "action",
            "declencheur",
            "timing",
            "event",
        ]
        for i in self.request(REQS["info_triggers"]):
            #            print ('triggers',i)
            ident = (i[0], i[1])
            if ident not in def_trigg:
                def_trigg[ident] = dict()
            definition = i[3:]
            nom = i[2]
            def_trigg[ident][nom] = definition
        return def_trigg

    #        print('pgr --------- selection info triggers ', len(triggers))

    def get_type_from_connect(self, typecode):
        """recupere une information de type"""
        info = self.request("select format_type(" + typecode + ",0)", None)[0]
        return info

    def select_elements_specifiques(self, schema, liste_tables):
        """ selectionne les elements specifiques pour coller a une restriction de schema"""
        a_garder = set(liste_tables)
        els = schema.elements_specifiques
        els["def_vues"] = {i: j for i, j in els["def_vues"].items() if i in a_garder}
        els["def_triggers"] = {
            i: j for i, j in els["def_triggers"].items() if i in a_garder
        }
        els["def_ftables"] = {
            i: j for i, j in els["def_ftables"].items() if i in a_garder
        }
        fonctions_a_garder = set()
        for i in els["def_triggers"].values():
            for j in i.values():
                fonction = re.sub(r"EXECUTE PROCEDURE (.*)\(.*\)", r"\1", j[1])
                fonctions_a_garder.add(tuple(fonction.split(".")))
        #        print('fonctions a garder', fonctions_a_garder)
        els["def_fonctions_trigger"] = {
            i: j
            for i, j in els["def_fonctions_trigger"].items()
            if i in fonctions_a_garder
        }
        if any(len(els[i]) for i in els):
            print("elements specifiques gardes", dict([(i, len(els[i])) for i in els]))

    @property
    def req_tables(self):
        """recupere les tables de la base"""
        return REQS["info_tables"], None

    @property
    def req_enums(self):
        """recupere les enums de la base"""
        return REQS["info_enums"], None

    @property
    def req_attributs(self):
        """recupere les attributs de la base"""
        return REQS["info_attributs"], None

    def get_type(self, nom_type):
        if "geometry" in nom_type:
            return nom_type
        return self.types_base.get(nom_type.upper(), "T")

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
        attributs = self.request(requete, data)
        # on corrige les types et les tailles
        retour = []
        for i in attributs:
            taille = 0
            dec = 0
            tmp0 = list(i)
            if "[]" in i[4]:
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
            retour.append(tmp0)
        #            if taille != 0:
        #                print ('attributs pg',i)
        return retour

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
        return nom + "::float"

    def multivaldata(self, valeurs):
        """formate les donnes pour les requetes sur les listes"""
        return {"val": "{" + ",".join(valeurs) + "}"}

    def multival(self, taille, operateur="=", cast=None):
        """ acces listes"""
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
        """# charge un fichier par copy"""
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

    def dbload(self, schema, ident, source):
        """ charge des objets en base de donnees par dbload"""
        cur = self.connection.cursor()
        colonnes = tuple(schema.classes[ident].get_liste_attributs())
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
        """ cree les structures standard"""
        pass


DBDEF = {
    "postgres": (
        PgrConnect,
        PgrGenSql,
        "server",
        "",
        "#ewkt",
        "base postgres générique",
    )
}
