# -*- coding: utf-8 -*-
"""
Selecteurs
Les selecteurs sont des structures servant a decrire une selection de tables de base de donnees
Un selecteur peut couvrir diverses bases de donnees
en cas de selecteur multibase les conflits sont geres par des options du selecteur
les selecteurs sont soit crees dynamiquement lors d un acces a une base (dbalpha, dbgeo...)
soit crees explicitement par dbselect
les selecteurs crees explicitement sont nommes et peuvent etre reutilises a plusieurs endroits.
"""
import re
import time
import os
import logging
import itertools
from collections import namedtuple
from pyetl.vglobales import DEFCODEC
from .outils import scandirs, hasbom, _extract

DEBUG = False
LOGGER = logging.getLogger("pyetl")
# modificateurs de comportement reconnus
DBACMODS = {"A", "T", "V", "=", "NOCASE"}
DBDATAMODS = {"S", "L"}
DBMODS = DBACMODS | DBDATAMODS

descripteur = namedtuple(
    "descripteur",
    ("type", "niveau", "classe", "attribut", "condition", "valeur", "mapping"),
)


class TableBaseSelector(object):
    """conditions de selection de tables dans une base
       il y a un Tablebaseselector par base concernee par une selection """

    def __init__(self, regle_ref, base=None, map_prefix="", schemaref=None):
        self.mapper = regle_ref.stock_param
        self.regle_ref = regle_ref
        self.base = base
        self.nombase = base if base != "*" else ""
        self.type_base = ""
        self.chemin = ""
        self.racine = ""
        self.connect = None
        self.nobase = False
        # si vrai une liste de classes direct est fournie
        # dans ce cas le selecteur ne gere que la liste de classes et pas le schema
        self.schemaref = schemaref
        self.valide = bool(base or schemaref)
        self.map_prefix = map_prefix
        self.reg_prefix(map_prefix)
        self.descripteurs = []
        self.dyndescr = []
        # un descripteur est un tuple
        # (type,niveau,classe,attribut,condition,valeur,mapping)
        self.static = dict()
        self.dynlist = dict()

    def __repr__(self):
        return (
            str(self.base)
            + ":"
            + str(len(self.descripteurs))
            + "->"
            + str(len(self.static))
            + ","
            + str(len(self.dynlist))
        )

    def reg_prefix(self, map_prefix):
        """enregistre les prefixes a appliquesr aux noms des schemas et/ou de classe
            en cas de conflit pour des selections multibases"""
        if "." in map_prefix:
            self.np, self.cp = map_prefix.split(".", 1)
        else:
            self.np, self.cp = map_prefix, ""
        self.map_prefix = map_prefix

    def add_descripteur(self, descripteur):
        """stocke un descripteur de selection il y a un descripteur par niveau ou expression
           de selection de niveau
           un descripteur peut etre statique s il n integere aucun element dependant de l objet courant
           ou dynamique s il depend de l objet courant
        """
        # print("ajout descripteur", self.base, descripteur)
        # raise
        niveau, classes, attr, valeur, fonction = descripteur
        dyn = any(["[" in i for i in classes])
        if "[" in attr:
            dyn = True
        if attr and valeur:
            att, defaut = valeur
            if att:
                print(" element dynamique", att)
                dyn = True
        if dyn:
            self.dyndescr.append(descripteur)
        else:
            self.descripteurs.append(descripteur)

    def resolve_static(self):
        """transformation de la liste de descripteurs statiques en liste de classes
           le selecteur gere la connection a la base se donnees"""
        if self.static:
            return
        mod = self.regle_ref.getvar("mod")
        # print("resolution statique", mod)
        set_prefix = self.regle_ref.getvar("set_prefix") == "1"
        prefix = ""
        if self.base != "__filedb":
            self.mapper.load_paramgroup(self.base, nom=self.base)
            prefix = self.regle_ref.getvar("prefix_" + self.base)
        # print(
        #     "variables",
        #     self.regle_ref.getvar("set_prefix"),
        #     set_prefix,
        #     prefix,
        #     self.base,
        #     # self.regle_ref.stock_param.context.vlocales,
        # )
        # raise
        if not self.nobase:
            if self.nombase != "__filedb":
                print("connection ", self.nombase)
                self.connect = self.mapper.getdbaccess(self.regle_ref, self.nombase)
                self.schemabase = self.connect.schemabase
                prefix = self.connect.prefix
                if set_prefix:
                    self.reg_prefix(prefix)
            else:
                return
        # print("resolve", self.base, mod, set_prefix, prefix, self.nobase)

        mod = mod.upper()
        # print("traitement descripteurs", self.descripteurs)
        for niveau, classes, attr, valeur, fonction in self.descripteurs:

            if niveau == "#":
                pass  # placeholder genere une entree base mais pas de classes
            vref = valeur[1] if valeur else ""
            for j in classes:
                self.static.update(
                    self.add_classlist(
                        niveau, j, attr, vref, fonction, mod, nobase=self.nobase
                    )
                )

    def set_prefix(self, cldef):
        """prefixage ses noms pour lea gestion des conflits entre base"""
        niveau, classe = cldef[:2]
        map_n = "_".join((self.np, niveau)) if self.np else niveau
        map_c = "_".join((self.cp, classe)) if self.cp else classe
        return (map_n, map_c)

    def add_classlist(self, niveau, classe, attr, valeur, fonction, mod, nobase=False):
        """transformation effective d un descripteur en liste de classes"""
        multi = not ("=" in mod)
        mod = mod.replace("=", "")
        nocase = "NOCASE" in mod
        mod = mod.replace("NOCASE", "")
        if not mod:
            mod = "A"
        if nobase:
            classlist = [(niveau, classe)]
        else:
            classlist = self.schemabase.select_niv_classe(
                niveau, classe, attr, tables=mod, multi=multi, nocase=nocase
            )
        direct = dict()
        for i in classlist:
            mapped = self.set_prefix(i)
            direct[mapped] = (i, attr, valeur, fonction)
        # print("classlist", direct)
        return direct

    def resolve(self, obj):
        """fonction de transformation de la liste de descripteurs en liste de classe
            et preparation du schema de travail"""
        self.nobase = self.nobase or self.regle_ref.getvar("nobase") == "1"
        if self.base == "__filedb":
            if obj and obj.attributs["#groupe"] == "__filedb":
                self.static = dict()
                self.nombase = obj.attributs.get("#nombase")
                nombase = obj.attributs.get("#nombase")
                base = obj.attributs.get("#base")
                self.chemin = obj.attributs["#chemin"]
                self.racine = obj.attributs["#racine"]
                self.type_base = obj.attributs["#type_base"]
                self.regle_ref.setlocal("base_" + nombase, self.base)
                self.regle_ref.setlocal("db_" + nombase, self.type_base)
                self.regle_ref.setlocal(
                    "server_" + nombase, os.path.join(self.racine, self.chemin, base)
                )
            else:
                return False

        self.resolve_static()
        complet = self.resolve_dyn(obj)
        if not self.nobase:
            self.getschematravail(self.regle_ref)
        else:
            liste_classes, liste_mapping = self.getmapping()
            # print("mapping", liste_mapping)
            self.mapping = {(i0, i1): (m0, m1) for m0, m1, i0, i1 in liste_mapping}
        return complet

    def resolve_dyn(self, obj):
        """transformation de descripteurs dynamiques en liste de classes
        les elements dynamiques sont resolus a partir des champs de l objet courant"""
        mod = self.regle_ref.getvar("mod")
        mod = mod.upper()
        if obj is None and self.dyndescr:
            print("elements dynamiques", self.dyndescr)
            return False
        self.dynlist = dict()
        for niveau, classes, attr, valeur, fonction in self.dyndescr:
            if attr.startswith("["):
                attr = obj.attributs.get(attr[1:-1])
            if niveau.startswith("["):
                niveau = obj.attributs.get(niveau[1:-1])
                for classe in classes:
                    if classe.startswith("["):
                        classe = obj.attributs.get(classe[1:-1])
                    valeur = obj.attributs.get(*valeur)
                    self.dynlist.update(
                        self.add_classlist(
                            niveau,
                            classe,
                            attr,
                            valeur,
                            fonction,
                            mod,
                            nobase=self.nobase,
                        )
                    )
        return True

    def classlist(self):
        """retourne un iterateur sur la liste de classes resolue"""
        yield from itertools.chain(self.static.items(), self.dynlist.items())

    def getmapping(self):
        liste_mapping = []
        liste_classes = []
        for mapping, definition in self.classlist():
            # print(" getmapping", self.base, mapping, definition)
            ident = definition[0]
            liste_mapping.append((*mapping, *ident))
            liste_classes.append(ident)
        return liste_classes, liste_mapping

    def get_liste_extraction(self):
        liste_classes, liste_mapping = self.getmapping()
        return liste_classes

    def getschematravail(self, regle, nom=""):
        """recupere le schema correspondant a la selection de la base demandee"""
        liste_classes, liste_mapping = self.getmapping()
        # print(" creation schema travail", self.base, len(liste_classes))
        if not self.nombase:
            return None
        if not nom:
            nom = self.nombase
        schema_travail, liste2 = self.schemabase.creschematravail(
            regle, liste_classes, nom
        )
        schema_travail.init_mapping(liste_mapping)
        self.schema_travail = schema_travail
        # schema_travail.printelements_specifiques()
        return schema_travail


class TableSelector(object):
    """condition de selection de tables dans des base de donnees ou des fichiers
        generes par des condition in: complexes
        le selecteur est un objet persistant qui peut etre reutilise par differentes commandes
        notamment des commandes de mapping
        un selecteur peut contenir de nombreux sous selecteurs lies a des bases
        si les memes tables existent dans diverses bases il y a potentiellement conflit
        3 modes de resolution existent:
            priorite : une base est prioritaire sur l autre: seule la base prioritaire est retenue
            mapping : les objets sont renommes en fonction d un prefixe devant le niveau
            concatenation: les objets sont sortis dans la meme classe (c est l option par defaut)
        """

    def __init__(self, regle, base=None):
        self.regle_ref = regle
        self.mapper = regle.stock_param
        self.autobase = base == "*"
        self.base = base if base != "*" else ""
        self.schema_travail = None
        self.defaultbase = "*"
        self.baseselectors = dict()
        self.classes = dict()
        self.inverse = dict()
        self.refbases = set()
        self.resolved = False
        self.nobase = False
        self.onconflict = "add"

    def __repr__(self):
        return repr([repr(bs) for bs in self.baseselectors.values()])

    def add_descripteur(
        self, base, niv, classes=[""], attribut="", valeur=(), fonction="="
    ):
        descripteur = (niv, classes, attribut, valeur, fonction)
        # print("add descripteur", base, descripteur)
        self.add_selector(base, descripteur)

    def add_niv_class(self, base, niveau, classe, attribut="", valeur=(), fonction="="):
        if not base:
            base = "__filedb"
        self.add_descripteur(base, niveau, [classe], attribut, valeur, fonction)

    def add_class_list(self, base, liste):
        tmp = dict()
        for niveau, classe in liste:
            if niveau in tmp:
                tmp[niveau].add(classe)
            else:
                tmp[niveau] = [classe]
        for niveau, classes in tmp.items():
            self.add_descripteur(base, niveau, classes)

    def add_selector(self, base, descripteur):
        if "." in base:
            tmp = base.split(".")
            if len(tmp) >= 3:
                base = tmp[0]
                descripteur = tmp[1:]
        if self.autobase:
            base = self.idbase(base)
        else:
            base = self.base
        if not base:
            base = "__filedb"
        if base not in self.baseselectors:
            self.baseselectors[base] = TableBaseSelector(self.regle_ref, base, "")
        # print("add descripteur", base, descripteur)
        self.baseselectors[base].add_descripteur(descripteur)

    def idbase(self, base):
        """identifie une base de donnees"""
        if base in self.mapper.dbref:
            base = self.mapper.dbref[base]
            return base
        print("base inconnue", base)
        return base

    def resolve(self, obj=None):
        # print(" debut resolve", self.baseselectors.keys(), self.resolved)
        if self.resolved:
            return True
        complet = len(self.baseselectors)
        self.nobase = self.nobase or self.regle_ref.getvar("nobase") == "1"

        for base in self.baseselectors:
            complet = complet and self.baseselectors[base].resolve(obj)
        self.resolved = complet
        # print(" fin resolve", self.baseselectors.keys(), self.resolved, complet)
        return complet

    def get_classes(self):
        for base in self.baseselectors:
            for item in self.baseselectors[base].classlist():
                yield base, item

    def fusion_schema(self, schema_tmp):
        """fusionne 2 schemas en se basant sur les poids ou les maxobj pour garder le bon"""
        schema = self.schema_travail
        if not schema_tmp:
            print("schema vide fusion impossible")
            return
        for i in schema_tmp.conformites:
            if i in schema.conformites:
                pass
                # la il faudrait faire quelque chose
            else:
                schema.conformites[i] = schema_tmp.conformites[i]
        for i in schema_tmp.classes:
            # print ('fusion schema' , i)
            if i in schema.classes:
                if self.onconflict == "add":
                    if schema.classes[i].compare(schema_tmp.classes[i]):
                        pass
                    else:
                        print("attention schemas incompatibles", i)
                # la il faudrait faire quelque chose
            else:
                schema.ajout_classe(schema_tmp.classes[i])
        schema_tmp.map_classes()
        liste_mapping = schema_tmp.mapping_schema(fusion=True)
        # print ('mapping_fusion','\n'.join(liste_mapping[:10]))
        schema.init_mapping(liste_mapping)

    def getschematravail(self, regle, nom=""):
        for basesel in self.baseselectors.values():
            schema_travail = basesel.getschematravail(self, regle)
            if self.schema_travail is None:
                self.schema_travail = schema_travail.copy(nom)
            else:
                self.fusion_schema(schema_travail)
        # print("tableselecteur")
        # schema_travail.printelements_specifiques()


# =============================================================
# =============outils de preparation de selecteurs=================
# =============================================================


def select_in(regle, fichier, base, classe=[], att="", valeur=(), nom=""):
    """precharge les elements des selecteurs:
        in:{a,b,c}                  -> liste de valeurs dans la commande
        in:#schema:nom_du_schema    -> liste des tables d'un schema
        in:nom_de_fichier           -> contenu d'un fichier
        in:[att1,att2,att3...]      -> attributs de l'objet courant
        in:(attributs)              -> noms des attributs de l'objet courant
        in:st:nom_du_stockage       -> valeurs des objets en memoire (la clef donne l'attribut)
        in:db:nom_de_la_table       -> valeur des attributs de l'objet en base (la clef donne le nom du champs)
    """
    stock_param = regle.stock_param

    fichier = fichier.strip()
    #    valeurs = get_listeval(fichier)
    liste_valeurs = fichier[1:-1].split(",") if fichier.startswith("{") else []
    valeurs = {i: i for i in liste_valeurs}
    print("fichier a lire ", fichier, valeurs)
    if fichier.startswith("#sel:"):  # selecteur externe
        selecteur = stock_param.namedselectors.get(fichier[5:])
        if not selecteur:
            print(
                "selecteur inconnu",
                regle,
                fichier[5:],
                stock_param.namedselectors.keys(),
            )
            raise StopIteration(2)
        return selecteur
    selecteur = getselector(regle, base=base, nom=nom)
    if fichier.startswith("#schema:"):  # liste de classes d'un schema
        nom = fichier[7:]
        if nom in stock_param.schemas:
            # print("lecture schema", nom)
            classes = stock_param.schemas.get(nom).classes.keys()
            selecteur.add_class_list(base, classes)
            return selecteur
    if fichier.startswith("st:"):
        fichier = fichier[3:]
        classes = stock_param.store.get(fichier)
        selecteur.add_class_list(base, classes)
        return selecteur
    elif fichier.startswith("db:"):
        mode = "in_db"
        fichier = fichier[3:]
        return selecteur
    else:
        if re.search(r"\[[CF]\]", fichier):
            mode = "in_d"  # dynamique en fonction du repertoire de lecture
        else:
            mode = "in_s"  # jointure statique
            selecteur_from_fich(fichier, selecteur)
        return selecteur


def _select_from_qgs(fichier, selecteur, codec=DEFCODEC):
    """prechargement d un fichier projet qgis"""
    try:
        codec = hasbom(fichier, codec)
        with open(fichier, "r", encoding=codec) as fich:
            # print("select projet qgs", fichier)
            for i in fich:
                if "datasource" in i:
                    table = _extract(i, "table=")
                    database = _extract(i, "dbname=")
                    host = _extract(i, "host=").lower()
                    port = _extract(i, "port=").lower()
                    niveau, classe = (
                        table.split(".") if "." in table else ("tmp", table)
                    )
                    niveau = niveau.replace('"', "")
                    classe = classe.replace('"', "")
                    base = (database, "host=" + host, "port=" + port)
                    selecteur.add_descripteur(base, niveau, [classe])
                    # print("descripteur", base, niveau, [classe])
    except FileNotFoundError:
        print("fichier qgs introuvable ", fichier)
    # print ('lus fichier qgis ',fichier,list(stock))
    return True


def adapt_qgs_datasource(regle, obj, fichier, selecteur, destination, codec=DEFCODEC):
    """ modifie un fichier qgs pour adapter les noms des bases et des niveaux
    """
    if not selecteur.resolved:
        selecteur.resolve(obj)
    destbase = regle.base
    for fich, chemin in scandirs("", fichier, rec=True):
        element = os.path.join(chemin, fich)
        if not fich.endswith(".qgs"):
            continue
        codec = hasbom(element, codec)
        fdest = os.path.join(destination, element)
        os.makedirs(os.path.dirname(fdest), exist_ok=True)
        sortie = open(fdest, "w", encoding=codec)
        with open(element, "r", encoding=codec) as fich:
            print("adapt projet qgs", element)
            for i in fich:
                if "datasource" in i:
                    table = _extract(i, "table=")
                    database = _extract(i, "dbname=")
                    inithost = _extract(i, "host=")
                    host = inithost.lower()
                    initport = _extract(i, "port=")
                    port = initport.lower()
                    niveau, classe = table.split(".")
                    ident = (niveau, classe)
                    base = (database, "host=" + host, "port=" + port)
                    idbase = selecteur.idbase(base)
                    tablemap = (niveau, classe)
                    if idbase in selecteur.baseselectors:
                        baseselector = selecteur.baseselectors[idbase]
                        if selecteur.nobase:
                            tablemap = baseselector.mapping.get(ident)
                            # print("baseselector.mapping", baseselector.mapping)
                        else:
                            tmp = baseselector.schema_travail.mapping(ident)
                            # print("baseselector.schemamapping", ident, tmp)
                            if tmp:
                                tablemap = tmp[1]
                    # print(
                    #     "adaptation qgs", base, ident, table, "->", destbase, tablemap
                    # )
                    oldtable = '"' + niveau + '"."' + classe + '"'
                    olddbdef = (
                        "dbname='"
                        + database
                        + "' host="
                        + inithost
                        + " port="
                        + initport
                    )
                    i = i.replace(
                        oldtable, '"' + tablemap[0] + '"."' + tablemap[1] + '"'
                    )
                    i = i.replace(olddbdef, destbase)
                    # print("datasource=>", i)

                sortie.write(i)

    # print ('lus fichier qgis ',fichier,list(stock))
    return True


def _select_from_csv(fichier, selecteur, codec=DEFCODEC):
    """decodage de selecteurs en fichiers csv
    formats acceptes:
    niveau.classe
    base.niveau.classe
    niveau.classe;attribut;valeur
    base.niveau.classe;attribut;valeur
    niveau;classe
    base;niveau;classe
    nivau;classe;attribut;valeur
    base;niveau;classe;attribut;valeur
    il est possible d ajouter une info de mapping derriere sous forme niveau.classe prefix:N.:C
    et un mapping attributaire sous forme att=>nouveau,... elle n est pas utilisee par le secleteur
    """

    try:
        codec = hasbom(fichier, codec)
        with open(fichier, "r", encoding=codec) as fich:
            for i in fich:
                ligne = i.replace("\n", "")  # on degage le retour chariot
                if ligne.startswith("!"):
                    if ligne.startswith("!!"):
                        ligne = ligne[1:]
                    else:
                        continue
                liste = [i.strip() for i in ligne.split(";")]
                # supprime les elements vides a la fin
                while liste:
                    if not liste[-1]:
                        liste.pop()
                    else:
                        break
                base, niveau, classe, attribut, valeur = [""] * 5
                if "." in liste[0]:
                    l2 = liste[0].split(".")
                    if len(l2) == 2:
                        niveau, classe = l2
                    elif len(l2) == 3:
                        base, niveau, classe = l2
                    if len(liste) > 2:
                        attribut, valeur = liste[1:3]
                        if "." in attribut:  # c' est un mapping
                            attribut, valeur = "", ""
                else:
                    if len(liste) > 4:
                        base, niveau, classe, attribut, valeur = liste[:5]
                    elif len(liste) == 4:
                        niveau, classe, attribut, valeur = liste
                    elif len(liste) == 3:
                        base, niveau, classe = liste
                    elif len(liste) == 1:
                        niveau = liste[0]
                    elif len(liste) == 2:
                        niveau, classe = liste
                classe = classe.split(",")

                # print("analyse ligne", liste, base, niveau, classe)
                if "," in valeur:
                    valeur = tuple(valeur.split(",", 1))
                else:
                    valeur = ("", valeur)
                for niv in niveau.split(","):
                    selecteur.add_descripteur(base, niveau, classe, attribut, valeur)
    except FileNotFoundError:
        print("fichier liste introuvable ", fichier)
    # print("prechargement selecteur csv", selecteur)


def selecteur_from_fich(fichier, selecteur, codec=DEFCODEC):
    print("sel_from_fich:scandirs", fichier)
    for fich, chemin in scandirs("", fichier, rec=True):
        element = os.path.join(chemin, fich)
        # print("sel_from_fich:lu", element)
        if fich.endswith(".qgs"):
            _select_from_qgs(element, selecteur, codec)
        elif fich.endswith(".csv"):
            _select_from_csv(element, selecteur, codec)
    # print("selecteur from fich", selecteur.baseselectors.keys())
    # for nom, sel in selecteur.baseselectors.items():
    #     print(nom, "====>", sel.descripteurs)
    # raise


def getselector(regle, base=None, nom=""):
    """recuperation d un selecteur stocke"""
    if not nom:
        return TableSelector(regle, base)
    if nom in regle.stock_param.selecteurs:
        selecteur = regle.stock_param.namedselectors[nom]
    else:
        selecteur = TableSelector(regle, base)
        regle.stock_param.namedselectors[nom] = selecteur
    return selecteur
