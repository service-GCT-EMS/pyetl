# -*- coding: utf-8 -*-
"""
Acces aux bases de donnees droits web sur une table
principe les droits web sont une restriction des droits desktop
il s agit de roles redondants dans la base
3 roles web existent
 wc consultation (inutile car lie aux droits desktop)
 wa maj alpha    (l utilisateur doit disposer d un role a
                  en base wa et wf sont des roles de lecture)
 wf maj complete
 si une table peut etre mis a jour en web on definit un role wa ou wf dessus

necessite la librairie psycopg2 et l acces au loader psql pour le chargement de donnees

"""
import os

import re
from collections import namedtuple
import psycopg2


class Cursinfo(object):
    """contient un curseur de base de donnees et des infos complementaires (requete,liste...)"""

    def __init__(self, connecteur, volume=0, nom=""):
        connection = connecteur.connection
        self.cursor = None
        if connection:
            if hasattr(connection, "autocommit"):
                connection.autocommit = True
            self.cursor = connection.cursor()
            self.ssc = False
            # print ('creation curseur standard', volume, nom)
        self.connecteur = connecteur
        self.requete = None
        self.schema_req = None
        self.data = None
        self.attlist = None
        self.volume = volume

    def fetchall(self):
        """recupere tous les elements"""
        return self.cursor.fetchall() if self.cursor else ()

    def fetchval(self):
        """recupere tous les elements"""
        return self.cursor.fetchval() if self.cursor else ()

    def close(self):
        """ferme le curseur"""
        if self.cursor:
            self.cursor.close()

    def execute(self, requete, data=None, attlist=None, newcursor=False):
        """execute une requete"""

        # print("dans execute ", requete, data)
        cursor = self.connecteur.connection.cursor() if newcursor else self.cursor
        if cursor:
            try:
                if data is not None:
                    cursor.execute(requete, data)
                else:
                    cursor.execute(requete)
            except Exception as err:
                print("erreur requete", err, requete)
                return None
            if not newcursor:
                self.requete = requete
                self.data = data
                self.attlist = attlist
                if not self.ssc:
                    # si on utilise des curseurs serveur le decompte est faux
                    # print('calcul decile',self.cursor)
                    self.decile = int(self.rowcount / 10 + 1)
                    if self.decile == 1:
                        self.decile = 100000
        return cursor
        # if attlist is None:
        #     self.attlist=self.schemaclasse
        # print ('fin')

    @property
    def rowcount(self):
        """compte les resultats"""

        if self.cursor:
            try:
                return self.cursor.rowcount
            except:
                pass
        return self.volume

    @property
    def namelist(self):
        if self.attlist is None:
            self.attlist = list(
                [
                    i.nom_attr
                    for i in sorted(self.infoschema, key=attrgetter("num_attribut"))
                ]
            )
        return self.attlist

    @property
    def infoschema(self):
        """fournit un schema issu de la requete"""
        # print(" dans infoschema")
        if self.schema_req:
            return self.schema_req
        if self.cursor:
            try:
                # print("dans cursor.schemaclasse", self.cursor.description)
                if self.cursor.description:
                    attlist = []
                    typelist = []
                    for num, colonne in enumerate(self.cursor.description):
                        (
                            name,
                            datatype,
                            display_size,
                            internal_size,
                            precision,
                            scale,
                            null_ok,
                        ) = colonne
                        nomtype = self.connecteur.getdatatype(datatype)
                        # print("lecture requete", name, datatype, nomtype, internal_size)
                        attdef = self.connecteur.attdef(
                            nom_attr=name, type_attr=nomtype, num_attribut=num + 1
                        )
                        attlist.append(attdef)
                        # typelist.append(type.__name__)
                    print("attlist", attlist)
                    self.schema_req = attlist
                    return attlist
            except Exception as err:
                print("planté dans cursor.schemaclasse ", err)
                raise
                pass
        return []


class PgCursinfo(Cursinfo):
    @property
    def infoschema(self):
        """retourne le schema issu de la requete"""
        if self.schema_req:
            return self.schema_req
        if self.requete:
            tmp = self.requete.split("\n")
            tmprequete = " ".join(tmp).strip()
            if tmprequete.endswith(";"):
                tmprequete = tmprequete[:-1]
            req = (
                "create TEMP TABLE tmp__0001 AS select * from ("
                + tmprequete
                + ") as x limit 0 "
            )

            self.execute(req, self.data, newcursor=True)
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
            # print("retour requete", attlist)
            self.execute("drop TABLE pg_temp.tmp__0001", newcursor=True)
            self.schema_req = attlist
        return self.schema_req

    #    attlist.append((name, nomtype, internal_size, precision))


class PgrConnect(DbConnect):
    """connecteur de la base de donnees postgres"""

    reqs = REQS  # requetes de fallback our les infos base
    requetes = reqs
    codecinfo = {"utf-8": "UTF8", "cp1252": "WIN1252"}

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
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

    def set_searchpath(self):
        """positionne les path pour la session"""
        cur = self.connection.cursor()
        cur.execute("select set_config('search_path','public',false)", ())
        cur.close()

    def get_cursinfo(self, volume=0, nom=""):
        """recupere un curseur"""
        # print(" postgres get cursinfo")
        return PgCursinfo(self, volume=volume, nom=nom) if self.connection else None

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
        """ remplace les \\ par des /"""
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
        print("postgres: traitement sql", host, self.base, os.path.basename(file))
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
        # try:
        #     import psycopg2
        # except ImportError:
        #     print("error: postgr2: erreur import module postgres")
        #     return None, None
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
            print("error: postgres: connection impossible ")
            print(
                "info:  postgres: parametres ",
                self.serveur,
                self.base,
                self.user,
                self.passwd,
            )
            print("error", err)

            raise

    def get_droits(self, user, table):
        entete = "schema;nom;definition;materialise"
        infos = self.request(self.requetes["info_vues"])
        vals = {(i[0], i[1]): (i[2], str(i[3])) for i in infos}
        # print("recup vues", len(vals))
        return (entete, vals)

    #        print('pgr --------- selection info triggers ', len(triggers))

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
        """ selectionne les elements specifiques pour coller a une restriction de schema"""
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
        if any(len(els[i][1]) for i in els):
            print(
                "elements specifiques gardes", dict([(i, len(els[i][1])) for i in els])
            )
            # print ("def trigger", els["def_triggers"])

    @property
    def req_tables(self):
        """recupere les tables de la base"""
        return self.requetes["info_tables"], None

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

    def dbload(self, schema, ident, source):
        """charge des objets en base de donnees par dbload"""
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
