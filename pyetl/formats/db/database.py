# -*- coding: utf-8 -*-

"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
import re
import time
import logging
from operator import attrgetter
from collections import namedtuple
from .dbconstants import *
from .gensql import DbGenSql


DEBUG = False
LOGGER = logging.getLogger(__name__)


class DummyConnect(object):
    """simule une connection base de donnees"""

    def __init__(self):
        self.schemabase = None
        self.valide = False
        self.DBError = None

    def close(self):
        pass

    def request(self, *args):
        pass

    def commit(self):
        pass

    def cursor(self):
        return Cursinfo(self, None)


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

    def __init__(self, connecteur, volume=0, nom=""):
        connection = connecteur.connection
        self.cursor = None
        if connection:
            # if volume > 100000 and nom:
            if False:  # on invalide les curseurs nommes pour le moment
                # on cree un curseur nomme pour aller plus vite et economiser de la memoire
                connection.autocommit = False
                self.cursor = connection.cursor(nom)
                self.cursor.itersize = 100000
                # print ('creation curseur nommé', volume, nom)
                self.ssc = True
            else:
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
        self.decile = 100000 if volume == 0 else int(volume / 10 + 1)

    def __iter__(self):
        return () if self.cursor is None else self.cursor

    def __next__(self):
        if self.cursor is None:
            raise StopIteration
        return next(self.cursor)

    def fetchall(self):
        """recupere tous les elements"""
        try:
            return self.cursor.fetchall() if self.cursor else ()
        except self.connecteur.DBError as err:
            print("erreur base de donnees", err)
            return ()

    def fetchval(self):
        """recupere tous les elements"""
        return self.cursor.fetchval() if self.cursor else ()

    def close(self):
        """ferme le curseur"""
        if self.cursor:
            self.cursor.close()

    def execute(
        self, requete, data=None, attlist=None, newcursor=False, fail_silent=False
    ):
        """execute une requete"""

        # print("dans execute ", requete, data)
        cursor = self.connecteur.connection.cursor() if newcursor else self.cursor
        if cursor:
            try:
                if data is not None:
                    cursor.execute(requete, data)
                else:
                    cursor.execute(requete)
            except self.connecteur.DBError as err:
                if fail_silent == True:
                    return None
                elif fail_silent != "pass":
                    print(self.connecteur.base, "erreur requete", err, requete)
                raise

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
                        # name=colonne[0]
                        # datatype=colonne[1]
                        name, datatype, *_ = colonne
                        nomtype = self.connecteur.getdatatype(datatype)
                        # print("lecture requete", name, datatype, nomtype)
                        attdef = self.connecteur.attdef(
                            nom_attr=name, type_attr=nomtype, num_attribut=num + 1
                        )
                        attlist.append(attdef)
                        # typelist.append(type.__name__)
                    # print("attlist", attlist)
                    self.schema_req = attlist
                    return attlist
            except Exception as err:
                print("planté dans cursor.schemaclasse ", err)
                raise
                pass
        return []


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
        defaults=[""] * 11,
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
        defaults=[""] * 20,
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
        self.code = code if code is not None else base
        self.regle = params
        self.params = params.stock_param
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
        defmodeconf = self.regle.getvar("mode_enums", 1)
        self.schemabase = self.params.init_schema(
            "#" + str(code), "B", defmodeconf=defmodeconf
        )
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
        self.DBError = KeyError
        # print("====init connection", self.base, self.code)

    #        self.req_tables = ("", None)

    #  methodes specifiques a ecraser dans les subclasses ####

    def commit(self):
        """gere le commit"""
        if self.connection:
            self.connection.commit()

    def get_cursinfo(self, volume=0, nom=""):
        """recupere un curseur"""
        return Cursinfo(self, volume=volume, nom=nom) if self.connection else None

    @property
    def valide(self):
        """ vrai si la connection est valide """
        return self.connection is not None

    @property
    def idconnect(self):
        """identifiant de base : type + nom"""
        return self.type_base + ":" + self.base

    @property
    def metas(self):
        return {
            "type_base": self.idconnect,
            "date_extraction": time.asctime(),
            "serveur": self.serveur,
            "base": self.base,
            "origine": "B",
            "user": self.user,
        }

    def connect(self):

        self.connection = DummyConnect()

    def getbasicatt(self, nom_groupe, nom_classe, nom_att, type_att):
        return self.attdef(
            nom_groupe=nom_groupe,
            nom_classe=nom_classe,
            nom_att=nom_att,
            type_att=type_att,
            num_attribut=0,
            dimension=2,
            taille=0,
            decimales=0,
        )

    def getdatatype(self, datatype):
        """recupere le type interne associe a un type cx_oracle"""
        return "T"

    def quote_table(self, ident):
        """rajoute les cotes autour des noms"""
        return '"%s"."%s"' % ident

    def quote(self, att):
        """rajoute les quotes sur une liste de valeurs ou une valeur"""
        if att.startswith('"'):
            return att
        return '"%s"' % (att)

    def attqjoiner(self, attlist, sep):
        """ join une liste d'attributs et ajoute les quotes"""
        if isinstance(attlist, (list, tuple)):
            return sep.join([self.quote(i) for i in attlist])
        return self.quote(attlist)

    def getdecile(self, cur):
        """ calcule les etapes pour l' affichage"""
        # print ('nombre de valeurs', cur.rowcount)
        if cur.rowcount == -1:
            self.decile = 100000
        else:
            self.decile = int(cur.rowcount / 10) + 1
            if self.decile <= 1:
                self.decile = 100000
        return self.decile

    def schemarequest(self, nom, fallback=False):
        """passe la requete d acces au schema"""
        try:
            req = self.requetes.get(nom, "")
            if callable(req):
                return req()
            # print ("traitement",req, self.requetes)
            if req:
                return self.request(req, None)
            else:
                req = self.fallback.get(nom, "")
                fallback = True
                return self.request(req, None)
        except self.errs as err:
            print("------------------", type(self))
            print("erreur requete schema ", nom, err)
            raise
            if not fallback:
                return self.schemarequest(nom, fallback=True)
            return ()
        print("pas de requete ", nom, self.requetes.keys())
        return ()

    def get_type(self, nom_type):
        """ type en base d'un type interne """
        return self.types_base.get(nom_type, "?")

    def dbclose(self):
        """fermeture base de donnees"""
        if self.connection is not None:
            self.connection.close()

    def get_enums(self):
        """ recupere la description de toutes les enums depuis la base de donnees """
        yield from self.schemarequest("info_enums")

    def get_enums2(self):
        """ recupere la description de toutes les enums depuis la base de donnees """
        yield from self.schemarequest("info_enums2")

    def get_tablelist(self):
        """retourne la liste des tables a prendre en compte"""
        yield from self.schemarequest("tablelist")

    def get_tables(self):
        """produit les objets issus de la base de donnees"""
        # print ('infotable',self.requetes.get('info_tables', "") )
        yield from [self.tabledef(*i) for i in self.schemarequest("info_tables")]

    def get_attributs(self):
        """produit les objets issus de la base de donnees"""

        yield from [self.attdef(*i) for i in self.schemarequest("info_attributs")]

    def _recup_tables(self):
        """recupere la structure des tables"""
        for i in self.get_tables():

            if len(i) == 12:
                (
                    _,
                    nom_groupe,
                    nom_classe,
                    alias_classe,
                    type_geometrique,
                    dimension,
                    nb_obj,
                    type_table,
                    _,
                    _,
                    _,
                    _,
                ) = i
            elif len(i) == 11:
                (
                    nom_groupe,
                    nom_classe,
                    alias_classe,
                    type_geometrique,
                    dimension,
                    nb_obj,
                    type_table,
                    _,
                    _,
                    _,
                    _,
                ) = i
            else:
                print("db:table mal formee ", self.type_base, len(i), i)
                continue

            #        nom_groupe, nom_classe, alias_classe, type_geometrique, dimension, nb_obj, type_table,\
            #        index_geometrique, clef_primaire, index, clef_etrangere = i
            #        print ('mdba:select tables' ,i)
            ident = (str(nom_groupe), str(nom_classe))
            schemaclasse = self.schemabase.get_classe(ident)
            if not schemaclasse:
                if type_table == "r":
                    LOGGER.info("table sans attributs %s", ".".join(ident))
                elif type_table == "v" or type_table == "m":
                    LOGGER.info("vue sans attributs %s", ".".join(ident))

                schemaclasse = self.schemabase.setdefault_classe(ident)
            schemaclasse.setinfo("type_table", type_table)
            schemaclasse.setinfo("alias", alias_classe if alias_classe else "")
            schemaclasse.setinfo("objcnt_init", str(nb_obj) if nb_obj else "0")
            schemaclasse.setinfo("dimension", str(dimension))
            schemaclasse.fichier = self.nombase
            #        print ('_get_tables: type_geometrique',type_geometrique,schemaclasse.info["type_geom"])
            if schemaclasse.info["type_geom"] == "indef":
                schemaclasse.stocke_geometrie(type_geometrique, dimension=dimension)
                #            print('stockage type geometrique', ident, type_geometrique,
                #                  schemaclasse.info["type_geom"])
                if schemaclasse.info["type_geom"] != "0":
                    schemaclasse.info["nom_geometrie"] = "geometrie"
            if schemaclasse.info["type_geom"] == "indef":
                print(
                    ident,
                    "apres _get_tables: type_geometrique",
                    schemaclasse.info["type_geom"],
                )

            schemaclasse.settype_table(type_table)

    def update_schema_classe(self, ident, attlist1, schema, regle):
        """adapte un schema en fonction d une requete"""
        schema = schema if schema is not None else self.schemabase
        if attlist1 is None:
            return schema.classes.get(ident)
        attlist = [i for i in attlist1 if not i.nom_attr.startswith("#")]
        if ident not in schema.classes:
            return self.cree_schema_classe(ident, attlist, schema=schema)
        else:
            schemaclasse = schema.classes[ident]
            if schemaclasse.amodifier(regle):
                return self.cree_schema_classe(
                    ident, attlist, schema=schema, update=True
                )
            return schemaclasse

    def cree_schema_classe(self, ident, attlist, schema=None, update=False):
        """cree un schema de classe a partir d une liste d attributs"""
        if attlist is None:
            return None
        schema = schema if schema is not None else self.schemabase
        if ident in schema.classes and not update:
            return schema.classes[ident]
        classe = schema.setdefault_classe(ident)
        classe.info["type_geom"] = "0"
        for atd in sorted(attlist, key=attrgetter("num_attribut")):
            # num_attribut = float(atd.num_attribut)
            if atd.nom_attr.startswith("#"):  # attribut hors schema
                print(" attribut hors schema", atd, classe)
                continue
            type_ref = atd.type_attr
            if not atd.type_attr:
                LOGGER.error(
                    "attribut sans type G:%s C:%s A:%s",
                    atd.nom_groupe,
                    atd.nom_classe,
                    atd.nom_attr,
                )
                type_ref = "T"
            taille_att = atd.taille if atd.taille else 0
            if "(" in type_ref:  # il y a une taille
                tmp = atd.type_attr.split("(")
                if tmp[1][0].isnumeric():
                    type_ref = tmp[0]
                    taille_att = tmp[1][:-1]
            type_attr = self.get_type(type_ref)
            if type_attr == "?":
                LOGGER.error(
                    "%s type non trouve G:%s C:%s A:%s ->%s",
                    self.type_base,
                    atd.nom_groupe,
                    atd.nom_classe,
                    atd.nom_attr,
                    type_ref,
                )

                type_attr = "T"

            if atd.enum:
                #            print ('detection enums ',atd.enum)
                #            if enum in schema_base.conformites:
                type_attr_base = "T"
                type_attr = atd.enum
            else:
                type_attr_base = type_attr

            clef_etr = ""
            if atd.clef_etrangere:
                cible_clef = atd.cible_clef if atd.cible_clef else ""
                #            if atd.cible_clef is None:
                #                cible_clef = ''
                if not cible_clef:
                    print(
                        "mdba: erreur schema : cible clef etrangere non definie",
                        atd.nom_groupe,
                        atd.nom_classe,
                        atd.nom_attr,
                        atd.clef_etrangere,
                    )
                #            print ('trouve clef etrangere',clef_etrangere)
                clef_etr = atd.clef_etrangere + "." + cible_clef
            #        if clef:  print (clef)
            index = atd.index if atd.index is not None else ""
            #        if index is None:
            #            index = ''
            if atd.clef_primaire:
                code = "P:" + str(atd.clef_primaire)
                if code not in index:
                    index = index + " " + code if index else code

            obligatoire = atd.obligatoire == "oui"
            parametres_clef = (
                atd.parametres_clef if "parametres_clef" in self.attdef._fields else ""
            )
            # if atd.multiple=='oui':
            #     print ('attribut',atd)
            classe.stocke_attribut(
                atd.nom_attr,
                type_attr,
                defaut=atd.defaut,
                type_attr_base=type_attr_base,
                taille=taille_att,
                dec=atd.decimales,
                force=True,
                alias=atd.alias,
                dimension=atd.dimension,
                clef_etr=clef_etr,
                mode_ordre="a",
                parametres_clef=parametres_clef,
                index=index,
                unique=atd.unique,
                obligatoire=obligatoire,
                multiple=atd.multiple,
            )
        if classe.pending:
            schema.pending = True
        # print("schema requete", classe)
        return classe

    def _recup_attributs(self):
        """recupere les attributs"""
        fdebug = None
        if DEBUG:
            print("ecriture debug:", "lecture_base_attr_" + self.type_base + ".csv")
            fdebug = open("lecture_base_attr_" + self.type_base + ".csv", "w")
            fdebug.write("\n".join(self.attdef.fields) + "\n")
        infoclasses = dict()
        for atd in self.get_attributs():
            if DEBUG:
                fdebug.write(";".join([str(v) if v is not None else "" for v in atd]))
                fdebug.write("\n")
            ident = (atd.nom_groupe, atd.nom_classe)
            if ident in infoclasses:
                infoclasses[ident].append(atd)
            else:
                infoclasses[ident] = [atd]
        if DEBUG:
            fdebug.close()
        for classe, attlist in infoclasses.items():
            self.cree_schema_classe(classe, attlist)

    def get_schemabase(self, mode_force_enums=1):
        """ recupere le schema complet de la base """
        debut = time.time()
        self.schemabase.metas = self.metas
        for i in self.get_enums():
            nom_enum, ordre, valeur, alias = i[:4]
            conf = self.schemabase.get_conf(nom_enum)
            conf.stocke_valeur(valeur, alias, ordre=ordre, mode_force=mode_force_enums)
        for i in self.get_enums2():
            nom_enum, valeurs = i[:2]
            for ordre, valeur in enumerate(valeurs.split(",")):
                conf = self.schemabase.get_conf(nom_enum)
                conf.stocke_valeur(valeur, "", ordre=ordre, mode_force=mode_force_enums)
        self._recup_attributs()
        self._recup_tables()

        for i in self.db_get_schemas():
            nom, alias = i
            self.schemabase.alias_groupes[nom] = alias if alias else ""
        #        print ('recuperation alias',nom,alias)
        self.get_elements_specifiques(self.schemabase)
        self.schemabase.dialecte = self.dialecte
        LOGGER.info(
            "lecture schema base %s: %d tables en %d s(%s)",
            self.schemabase.nom,
            len(self.schemabase.classes),
            int(time.time() - debut),
            self.schemabase.dialecte,
        )

    def select_elements_specifiques(self, schema, liste_tables):
        """ selectionne les elements specifiques pour coller a une restriction de schema"""
        return None

    def getschematravail(
        self, regle, niveau, classe, tables="A", multi=True, nocase=False, nomschema=""
    ):
        """recupere le schema de travail"""
        schema_travail, liste2 = self.schemabase.getschematravail(
            regle, niveau, classe, tables="A", multi=True, nocase=False, nomschema=""
        )
        if schema_travail.elements_specifiques:
            self.select_elements_specifiques(schema_travail, liste2)
            # print("selection elements specifiques", liste2)
        # self.commit()
        LOGGER.debug(
            "schema %s: %d -->%s: %d (%d) ",
            self.schemabase.nom,
            len(self.schemabase.classes),
            schema_travail.nom,
            len(schema_travail.classes),
            len(schema_travail.conformites),
        )
        return schema_travail, liste2

    def execrequest(
        self, requete, data=None, attlist=None, volume=0, nom="", fail_silent=True
    ):
        """ lancement requete specifique base"""
        cur = self.get_cursinfo(volume=volume, nom=nom)
        #        cur.execute(requete, data=data, attlist=attlist)
        try:
            retour = cur.execute(
                requete, data=data, attlist=attlist, fail_silent=fail_silent
            )
            if retour is None:
                return None
            return cur

        except self.DBError as err:
            if fail_silent != "pass":
                LOGGER.error(
                    "erreur db %s : %s -> %s", self.type_base, requete, str(data)
                )
                LOGGER.info("requete finale %s", cur.cursor.mogrify(requete, data))
            cur.close()
            # print("erreur requete")
            raise

    #        print ('exec:recup cursinfo', type(cur))

    def request(self, requete, data=None, attlist=None, fail_silent=True):
        """ lancement requete et gestion retours"""
        cur = (
            self.execrequest(
                requete, data=data, attlist=attlist, fail_silent=fail_silent
            )
            if requete
            else None
        )
        if cur:
            liste = cur.fetchall()
            cur.close()
            return liste
        return []

    def iterreq(
        self, requete, data=None, attlist=None, has_geom=False, volume=0, nom=""
    ):
        """ lancement requete et gestion retours en mode iterateur"""
        # print('appel iterreq database', volume,nom)
        cur = self.execrequest(
            requete, data=data, attlist=attlist, volume=volume, nom=nom
        )
        return cur

    # ===================elements de formattage sql=======================

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

    def dscast(self, nom):
        """forcage date simple"""
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
            attlist2.append('"' + self.sys_fields[i][0] + '"')
        return

    def construction_champs(self, schema, surf=False, long=False):
        """ construit la liste de champs pour la requete"""
        attlist = schema.get_liste_attributs()
        attlist2 = []
        for i in attlist:
            att = schema.attributs[i]
            # if att.type_att == "X":
            #     attlist2.append("")
            if att.type_att == "D":
                attlist2.append(self.get_dateformat(self.quote(i)))
            else:
                # attlist2.append('"' + i + '"::text')
                attlist2.append(self.textcast(self.quote(i)))

        self.get_sys_fields(attlist, attlist2)
        if self.geographique:
            nom_geometrie = self.quote(schema.info["nom_geometrie"])
            if schema.info["type_geom"] == "3":  # surfaces
                if surf:  # calcul de la surface
                    attlist2.append(
                        self.get_surf(nom_geometrie) + 'as "#surface_calculee"'
                    )
                    attlist.append("#surface_calculee")
                if long:  # longueur
                    attlist2.append(
                        self.get_perim(nom_geometrie) + 'as "#longueur_calculee"'
                    )
                    attlist.append("#longueur_calculee")
            elif schema.info["type_geom"] == "2":  # lignes
                if long:  # longueur
                    attlist2.append(
                        self.get_long(nom_geometrie) + 'as "#longueur_calculee"'
                    )
                    attlist.append("#longueur_calculee")
            if schema.info["type_geom"] != "0":
                attlist2.append(self.get_geom(nom_geometrie) + "as geometrie")
        join_char = self.join_char
        atttext = join_char.join(attlist2)
        return atttext, attlist

    def getcast(self, schema, attribut):
        """prepare les conversions de valeurs"""
        if attribut in self.sys_fields:  # c est un champ systeme
            attribut, type_att = self.sys_fields[attribut]
        else:
            type_att = schema.attributs[attribut].type_att
        cast = self.nocast
        if type_att == "D":
            cast = self.datecast
        if type_att == "DS":
            cast = self.dscast
        elif type_att in "EFS":
            cast = self.numcast
        elif schema.attributs[attribut].conformite:
            cast = self.textcast
        return attribut, cast

    def prepare_condition(self, schema, attribut, valeur):
        """ prepare une requete faisant appel a des attributs"""
        if not attribut:
            return "", ()
        oper = "="
        attribut, cast = self.getcast(schema, attribut)
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
        """compte un ensemble de valeurs en base"""

        condition, data = self.prepare_condition(schema, attribut, valeur)

        requete = " SELECT count(*) FROM " + self.quote_table(ident) + condition
        resultat = self.request(requete, data)
        return resultat

    def req_alpha(self, ident, schema, attribut, valeur, mods, maxi=0, ordre=None):
        """recupere les elements d'une requete alpha"""
        niveau, classe = ident
        attlist = []
        atttext, attlist = self.construction_champs(schema, "S" in mods, "L" in mods)
        condition, data = self.prepare_condition(schema, attribut, valeur)
        requete = " SELECT " + atttext + " FROM " + self.quote_table(ident) + condition
        if ordre:
            requete = requete + " ORDER BY " + self.attqjoiner(ordre, ",")
        requete = requete + self.set_limit(maxi, bool(data))

        #        print ('parametres',data,valeur)

        self.attlist = attlist
        if not atttext:
            requete = ""
            data = ()
        # print('acces alpha', self.geographique, requete, data)
        #        raise
        #        print ('geometrie',schema.info["type_geom"])
        volinfo = int(maxi) if maxi else int(schema.info["objcnt_init"])
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
            # geom2 = self.set_geom2(geom)
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
                + self.quote_table(ident)
                + " WHERE "
                + prefixe
                + self.cond_geom(
                    nom_fonction, self.quote(schema.info["nom_geometrie"]), geom2
                )
                + self.set_limit(maxi, True)
            )

            if self.debug > 2:
                print("debug: database: requete de selection geo", requete, data)
            # curs.execute(requete,data)
            self.attlist = attlist
            volinfo = int(maxi) if maxi else int(schema.info["objcnt_init"])

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
        """recupere des elements specifiques a un format et les stocke dans une
        structure du schema"""
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
                LOGGER.warning(
                    "conformite %s ignoree: valeur trop longue %s", nom, valeur
                )
                # print("valeur trop longue ", valeur, " : conformite ignoree", nom)
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
            schemabase = self.schemabase
            if schemabase is not None and nom in schemabase.conformites:
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
        return False

    def dbload(self, schema, ident, source):
        """ charge des objets en base de donnees par dbload"""
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

    def req_update_obj(self, regle, ident, attributs, obj, clef=None):
        """recupere les elements d'une requete alpha"""
        niveau, classe = ident
        if ident not in self.schemabase.classes:
            return False
        tablekey = self.schemabase.classes[ident].getpkey
        requete = (
            " UPDATE "
            + self.quote_table(ident)
            + " SET "
            + attributs
            + " = "
            + valeur
            + " WHERE "
            + tablekey
            + "="
            + clef
        )

        #        print ('parametres',data,valeur)
        data = valeur
        if not attribut:
            requete = ""
            data = ()

        return self.request(requete, data)
