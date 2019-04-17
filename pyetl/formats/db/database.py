# -*- coding: utf-8 -*-

"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
import re
from collections import namedtuple

TYPES_A = {i: i for i in "TFHGDNSIEB"}

REMPLACE = dict(zip("-~èéà/", "__eea_"))


RESERVES = {"in": "ins", "as": "ass"}

GTYPES_DISC = {"alpha": "", "ALPHA": ""}
GTYPES_CURVE = {"alpha": "", "ALPHA": ""}


class SpecDefs(object):
    """gere les elements speciaux d une base de donnees"""

    def __init__(self, connection):
        self.connection = connection
        self.basic = False
        self.vues = dict()
        self.is_mat = dict()
        self.ftrigs = dict()
        self.tdist = dict()
        self.def_triggers = dict()


class Cursinfo(object):
    """contient un curseur de base de donnees et des infos complementaires (requete,liste...)"""

    def __init__(self, connection, volume=0, nom=""):
        self.cursor = None
        if connection:
            if volume > 100000 and nom:
                # on cree un curseur nomme pour aller plus vite et economiser de la memoire
                self.cursor = connection.cursor(nom)
                self.cursor.itersize = 100000
                # print ('creation curseur nommé', volume, nom)
                self.ssc = True
            else:
                self.cursor = connection.cursor()
                self.ssc = False
                # print ('creation curseur standard', volume, nom)
        self.request = None
        self.data = None
        self.attlist = None
        self.volume = volume
        self.decile = 100000 if volume == 0 else int(volume / 10 + 1)

    def __iter__(self):
        if self.cursor is None:
            return ()
        return self.cursor

    def __next__(self):
        if self.cursor is None:
            raise StopIteration
        return next(self.cursor)

    def fetchall(self):
        """recupere tous les elements"""
        if self.cursor:
            return self.cursor.fetchall()
        return ()

    def close(self):
        """ferme le curseur"""
        if self.cursor:
            self.cursor.close()

    def execute(self, requete, data=None, attlist=None):
        """execute une requete"""
        self.request = requete
        self.data = data
        self.attlist = attlist
        if self.cursor:
            if data is not None:
                self.cursor.execute(requete, data)
            else:
                self.cursor.execute(requete)
            if not self.ssc:  # si on utilise des curseurs serveur le decompte est faux
                # print('calcul decile',self.cursor)
                self.decile = int(self.rowcount / 10 + 1)
                if self.decile == 1:
                    self.decile = 100000

    @property
    def rowcount(self):
        """compte les resultats"""

        if self.cursor:
            try:
                return self.cursor.rowcount
            except:
                pass
        return self.volume


class DbConnect(object):
    """connecteur de base de donnees generique
        tous les connecteurs sont des sousclasses de celui ci"""

    tabledef = namedtuple(
        "tabledef",
        (
            "nom_groupe",
            "nom_classe",
            "alias_classe",
            "type_geometrique",
            "dimension",
            "nb_obj",
            "type_table",
            "index_geometrique",
            "clef_primaire",
            "index",
            "clef_etrangere",
        ),
    )
    attdef = namedtuple(
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
    typenum = {
        "1": "POINT",
        "2": "LIGNE",
        "3": "POLYGONE",
        "-1": "GEOMETRIE",
        "0": "ALPHA",
        "indef": "ALPHA",
    }

    requetes = {"schemas": "", "tables": "", "enums": "", "attributs": "", "vues": ""}

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        self.serveur = serveur
        self.base = base
        self.user = user
        self.passwd = passwd
        self.code = code
        self.params = params
        self.type_base = "generique"
        self.debug = debug
        self.system = system
        self.types_base = TYPES_A
        self.join_char = ","
        self.reserves = RESERVES
        self.remplace = REMPLACE
        self.conflen = 62
        #        self.typenum = {'1':"POINT", '2':"LIGNE", '3':"POLYGONE",
        #                        '-1':"GEOMETRIE", '0':"ALPHA", 'indef':'ALPHA'}
        self.geom_from_natif = None
        self.geom_to_natif = None
        self.nombase = base
        self.type_serveur = "non defini"
        self.accept_sql = "non"  # determine si la base accepte des requetes
        self.codecinfo = dict()
        self.geographique = False
        self.connection = None
        self.schemabase = None
        #        self.connect()
        self.gensql = DbGenSql()
        self.decile = 100000
        self.attlist = []
        self.sys_cre = None  # champs contenant les dates de creation et modif auto
        self.sys_mod = None
        self.tables = dict()
        self.sys_fields = dict()
        self.sql_helper = None
        self.load_helper = None
        self.load_ext = ""
        self.dump_helper = None
        self.dialecte = "sql"
        self.fallback = {}
        self.errs = KeyError

    #        self.req_tables = ("", None)

    #  methodes specifiques a ecraser dans les subclasses ####

    def get_cursinfo(self, volume=0, nom=""):
        """recupere un curseur"""
        return (
            Cursinfo(self.connection, volume=volume, nom=nom)
            if self.connection
            else None
        )

    def connect(self):
        """retourne la connection a la base"""
        return None

    @property
    def valide(self):
        """ vrai si la connection est valide """
        return self.connection is not None

    @property
    def idconnect(self):
        """identifiant de base : type + nom"""
        return self.type_base + ":" + self.base

    def schemarequest(self, nom, fallback=False):
        """passe la requete d acces au schema"""
        try:
            req = self.requetes.get(nom, "")
            # print ("traitement",req)
            if req:
                return self.request(req, None)
            else:
                req = self.fallback.get(nom, "")
                fallback = True
                return self.request(req, None)
        except self.errs as err:
            print("------------------", type(self))
            print("erreur requete ", nom, err)
            raise
            if not fallback:
                return self.schemarequest(nom, fallback=True)
            return ()
        print("pas de requete ", nom, self.requetes.keys())
        return ()

    def get_type(self, nom_type):
        """ type en base d'un type interne """
        if nom_type not in self.types_base:
            print(self.nombase, "db:type inconnu", nom_type, self.types_base)
        return self.types_base.get(nom_type, "T")

    def dbclose(self):
        """fermeture base de donnees"""
        if self.connection is not None:
            self.connection.close()

    def get_enums(self):
        """ recupere la description de toutes les enums depuis la base de donnees """
        return self.schemarequest("info_enums")

    def get_tablelist(self):
        """retourne la liste des tables a prendre en compte"""
        return self.schemarequest("tablelist")

    def get_tables(self):
        """produit les objets issus de la base de donnees"""
        return self.schemarequest("info_tables")

    def get_attributs(self):
        """produit les objets issus de la base de donnees"""
        return self.schemarequest("info_attributs")

    def execrequest(self, requete, data=None, attlist=None, volume=0, nom=""):
        """ lancement requete specifique base"""
        cur = self.get_cursinfo(volume=volume, nom=nom)
        #        cur.execute(requete, data=data, attlist=attlist)

        try:
            cur.execute(requete, data=data, attlist=attlist)
            return cur

        except self.errs as err:
            print(
                "dtb:error: ",
                self.type_base,
                ":erreur acces base ",
                requete,
                "-->",
                data,
                err,
            )
            #            print('dtb',cur.mogrify(requete, data))
            cur.close()
            raise StopIteration(2)

    #        print ('exec:recup cursinfo', type(cur))

    def request(self, requete, data=None, attlist=None):
        """ lancement requete et gestion retours"""
        # print('dans request ',self.type_base, self)
        cur = self.execrequest(requete, data=data, attlist=attlist) if requete else None
        liste = cur.fetchall()
        cur.close()
        return liste

    def iterreq(
        self, requete, data=None, attlist=None, has_geom=False, volume=0, nom=""
    ):
        """ lancement requete et gestion retours en mode iterateur"""
        print('appel iterreq database', volume,nom)

        cur = self.execrequest(
            requete, data=data, attlist=attlist, volume=volume, nom=nom
        )

        return cur

    #        return iter(())

    # elements de formattage sql

    def get_dateformat(self, nom):
        """formattage dates"""
        return nom

    def nocast(self, nom):
        """ pas de formattage"""
        return nom

    def textcast(self, nom):
        """forcage text"""
        return nom

    def datecast(self, nom):
        """forcage date"""
        return nom

    def numcast(self, nom):
        """forcage numerique"""
        return nom

    def get_join_char(self):
        """ separateur de liste"""
        return ","

    def multivaldata(self, valeurs):
        """formate les donnes pour les requetes sur les listes"""
        return {"v" + str(i): j for i, j in enumerate(valeurs)}

    def multival(self, _, operateur="=", cast=None):
        """ acces listes"""
        if cast is not None:
            return cast(" " + operateur + " ANY (val)") + "[]"
        return " " + operateur + " ANY (val)"

    def monoval(self, operateur="=", cast=None):
        """acces valeur"""
        if cast is not None:
            return " " + operateur + cast("(val)")
        return " " + operateur + " (val)"

    def db_get_schemas(self):
        """recupere les schemas de base"""
        return ()

    def get_geom(self, nom):
        """ acces a la geometrie """
        return nom

    def get_surf(self, nom):
        """surface d un polygone"""
        return nom

    def get_perim(self, nom):
        """perimetre d un polygone"""
        return nom

    def get_long(self, nom):
        """longueur d une ligne"""
        return nom

    def set_geom(self, geom, srid):
        """cree la geometrie"""
        return geom, srid

    def set_geomb(self, geom, srid, buffer):
        """cree la geometrie avec un buffer"""
        return ""

    def cond_geom(self, nom_fonction, nom_geometrie, geom2):
        """ sql pour une condition geometrique"""
        return ""

    def set_limit(self, maxi, whereclause):
        """ limite le nombre de retours """
        return ""

    def get_sys_fields(self, attlist, attlist2):
        """ ajoute des champs systeme"""
        for i in self.sys_fields:
            attlist.append(i)
            attlist2.append(self.sys_fields[i][0])
        return

    def construction_champs(self, schema, surf=False, long=False):
        """ construit la liste de champs pour la requete"""
        attlist = schema.get_liste_attributs()
        attlist2 = []
        for i in attlist:
            att = schema.attributs[i]
            # print ('dbaccess:type_attribut ', i,att.type_att)
            if att.type_att == "X":
                attlist2.append("")
            if att.type_att == "D":
                attlist2.append(self.get_dateformat(i))
            else:
                # attlist2.append('"' + i + '"::text')
                attlist2.append(self.textcast(i))

        self.get_sys_fields(attlist, attlist2)
        if self.geographique:
            nom_geometrie = schema.info["nom_geometrie"]
            if schema.info["type_geom"] == "3":  # surfaces
                if surf:  # calcul de la surface
                    attlist2.append(self.get_surf(nom_geometrie))
                    attlist.append("#surface_calculee")
                if long:  # longueur
                    attlist2.append(self.get_perim(nom_geometrie))
                    attlist.append("#longueur_calculee")
            elif schema.info["type_geom"] == "2":  # lignes
                if long:  # longueur
                    attlist2.append(self.get_long(nom_geometrie))
                    attlist.append("#longueur_calculee")
            if schema.info["type_geom"] != "0":
                attlist2.append(self.get_geom(nom_geometrie))
        join_char = self.join_char
        atttext = join_char.join(attlist2)
        return atttext, attlist

    def prepare_attribut(self, schema, attribut, valeur):
        """ prepare une requete faisant appel a des attributs"""

        if attribut in self.sys_fields:  # c est un champ systeme
            attribut, type_att = self.sys_fields[attribut]
        else:
            type_att = schema.attributs[attribut].type_att
        cast = self.nocast
        if type_att == "D":
            cast = self.datecast
        elif type_att in "EFS":
            cast = self.numcast
        elif schema.attributs[attribut].conformite:
            cast = self.textcast

        if isinstance(valeur, (set, list)) and len(valeur) > 1:

            data = self.multivaldata(valeur)
            #                data = {'val':"{'"+"','".join(valeur)+"'}"}
            cond = self.multival(len(data), cast=cast)
        else:
            if isinstance(valeur, (set, list)):
                val = valeur[0]
            else:
                val = valeur
                oper = "="
            #                oper = '='
            #                val = valeur
            #                print ('dbalpha valeur a traiter',val)

            if val:
                if val[0] in "<>=~":
                    oper = val[0]
                    val = val[1:]
                if val[0] == "\\":
                    val = val[1:]
            cond = self.monoval(oper, cast)
            data = {"val": val}
        #                print('valeur simple', valeur, oper, cond, cast, data)

        condition = " WHERE " + cast(attribut) + cond
        return condition, data

    def req_count(self, ident, schema, attribut, valeur, mods):
        """compte un enesemble de valeurs en base"""
        niveau, classe = ident
        data = ()
        condition = ""
        if attribut:
            condition, data = self.prepare_attribut(schema, attribut, valeur)

        requete = " SELECT count(*) FROM " + niveau + "." + classe + condition
        resultat = self.request(requete, data)
        return resultat

    def req_alpha(self, ident, schema, attribut, valeur, mods, maxi=0, ordre=None):
        """recupere les elements d'une requete alpha"""
        niveau, classe = ident

        attlist = []
        atttext, attlist = self.construction_champs(schema, "S" in mods, "L" in mods)
        if attribut:
            condition, data = self.prepare_attribut(schema, attribut, valeur)

            requete = (
                " SELECT " + atttext + " FROM " + niveau + "." + classe + condition
            )
        #                          " WHERE "+cast(attribut) + cond
        else:
            requete = " SELECT " + atttext + " FROM " + niveau + "." + classe
            data = ()
        if ordre:
            if isinstance(ordre, list):
                requete = requete + " ORDER BY " + ",".join(ordre)
            else:
                requete = requete + " ORDER BY " + ordre

        requete = requete + self.set_limit(maxi, bool(data))

        #        print ('parametres',data,valeur)

        self.attlist = attlist
        if not atttext:
            requete = ""
            data = ()
        #        print('acces alpha', self.geographique, requete, data)
        #        raise
        #        print ('geometrie',schema.info["type_geom"])
        volinfo = maxi if maxi else int(schema.info["objcnt_init"])
        # print( 'appel iterreq', volinfo,classe)
        return self.iterreq(
            requete,
            data,
            attlist=attlist[:],
            has_geom=schema.info["type_geom"] != "0",
            volume=volinfo,
            nom=classe,
        )

    def req_geom(self, ident, schema, mods, nom_fonction, geometrie, maxi=0, buffer=0):
        """requete geometrique"""
        if not self.geographique:
            return iter(())
        if schema.info["type_geom"] != "0":
            niveau, classe = ident
            atttext, attlist = self.construction_champs(
                schema, "S" in mods, "L" in mods
            )
            prefixe = ""
            #            geom2="SDO_UTIL.FROM_WKTGEOMETRY('"+geometrie+"')"
            geomdef = geometrie.split(";", 1)
            if len(geomdef) == 2:
                srid = geomdef[0].split("=")[1]
                geom = geomdef[1]
            else:
                geom = geometrie
                srid = "3948"

            #            geom2="SDO_GEOMETRY('%s',%s)" % (geom,srid)
            geom2 = self.set_geom(geom, srid)
            if buffer:
                geom2 = self.set_geomb(geom, srid, buffer)

            #                data = {'geom':geometrie,'buf':buffer}
            #            else:
            #                data = {'geom':geometrie}
            data = ()
            if nom_fonction and nom_fonction[0] == "!":
                prefixe = "NOT "
                nom_fonction = nom_fonction[1:]

            requete = (
                " SELECT "
                + atttext
                + " FROM "
                + niveau
                + "."
                + classe
                + " WHERE "
                + prefixe
                + self.cond_geom(nom_fonction, schema.info["nom_geometrie"], geom2)
                + self.set_limit(maxi, True)
            )

            if self.debug > 2:
                print("debug: database: requete de selection geo", requete, data)
            # curs.execute(requete,data)
            self.attlist = attlist
            volinfo = maxi if maxi else int(schema.info["objcnt_init"])

            return self.iterreq(
                requete,
                data,
                attlist=attlist[:],
                has_geom=schema.info["type_geom"] != "0",
                volume=volinfo,
                nom=classe,
            )
        else:
            print("error: classe non geometrique utilisee dans une requete geometrique")
            return iter(())

    def get_elements_specifiques(self, schema):
        """ recupere des elements specifiques a un format et les stocke dans une
        structure du schema """
        schema.elements_specifiques = dict()
        return

    # preparation ecriture en base

    def prepare_conf(self, conf):
        """preparation des conformites pour ecriture en base"""
        conf.ctrl = set()
        conf.cc = []
        nom = conf.nombase
        for j in sorted(list(conf.stock.values()), key=lambda v: v[2]):
            # print (nom,j[0])
            valeur = j[0].replace("'", "''")
            if len(j[0]) > self.conflen:
                print("valeur trop longue ", valeur, " : conformite ignoree", nom)
                return False
            if valeur not in conf.ctrl:
                conf.cc.append(valeur)
                conf.ctrl.add(valeur)
            else:
                print("attention valeur ", valeur, "en double dans", nom)

    def conf_en_base(self, conf):
        """verifie si une conformite est en base"""
        # retourne existe, conforme
        existe, conforme = True, True
        manque, non_conforme = False, False
        if conf.valide_base:
            return existe, conforme
        nom = conf.nombase
        if self.valide:
            schemabase = self.connection.schemabase
            if schemabase and nom in schemabase.conformites:
                # si elle existe on verifie qu'elle est bonne
                self.prepare_conf(conf)
                conf_base = schemabase.conformites[nom]
                conf_base = {j[0] for j in conf.stock.values()}
                if conf_base == conf.ctrl:
                    conf.valide_base = True
                    return existe, non_conforme
                return existe, conforme
            return manque, conforme

    def db_cree_table(self, schema, ident):
        """creation d' une tables en direct
           possible qu avec une connection"""
        if self.valide:
            req = self.gensql.cree_tables(schema, ident)
            return self.connection.request(req, ())

    def db_cree_tables(self, schema, liste):
        """creation d'une liste de tables en direct"""
        if self.valide:
            if not liste:
                liste = [i for i in schema.classes if schema.classes[i].a_sortir]
            for ident in liste:
                self.db_cree_table(schema, ident)
        return False

    def dbloadfile(self, schema, ident, fichier):
        """# charge un fichier par copy"""
        if not self.valide:
            return False
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
        if not self.valide:
            return False
        cur = self.connection.cursor()
        colonnes = tuple(schema.classes[ident].getcodes_erreur_liste_attributs())
        nom = ".".join(ident)
        try:
            cur.copy_from(source, nom, columns=colonnes, sep="\t")
            cur.close()
            return True
        except Exception as erreur:
            print("error: sigli: chargement ", ident, "-->", erreur)
            cur.close()
            return False

    def extload(self, helper, files, logfile=None, reinit="0", vgeom="1"):
        """ charge des objets en base de donnees par dbload"""
        return False

    def recup_maxval(self, niveau, classe, clef):
        """ recupere le max d 'un champs """
        if not self.valide:
            return False
        requete = "SELECT max(" + clef + ") as maxval FROM " + niveau + "." + classe
        print("requete maxval ", requete)
        curs = self.request(requete, ())
        valeur = curs[0][0]
        return valeur


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
        self.typenum = DbConnect.typenum
        self.gtypes_disc = GTYPES_DISC
        self.gtypes_curve = GTYPES_CURVE
        self.types_base = TYPES_A
        self.dialecte = "sql"
        self.schema_conf = "public"

        self.connection = connection
        self.basic = basic
        self.schema = None

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

        table = groupe + "." + nom
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
            attname = self.reserves.get(attname, attname)
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
            table = groupe + "." + nom
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
            liste = [i for i in self.schema.classes if self.schema.classes[i].a_sortir]

        liste_tables = liste

        #       for i in liste_tables:
        #            print('type :',i,self.schema.classes[i].type_table)
        print("definition de tables a sortir:", len(liste_tables), self.dialecte)
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
        return None

    # structures specifiques pour stocker les scrips en base
    # cree 4 tables: Macros scripts batchs logs

    def init_pyetl_script(self, nom_schema):
        """ cree les structures standard"""
        pass
