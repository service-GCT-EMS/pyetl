# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces aux bases de donnees
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
    """condition de selection de tables dans un schema"""

    def __init__(self, mapper, base=None, map_prefix="", schemaref=None):
        self.mapper = mapper
        self.base = base
        self.type_base = ""
        self.chemin = ""
        self.racine = ""
        self.connect = None
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
        return str(self.base) + str(len(self.descripteurs) + len(self.descripteurs))

    def reg_prefix(self, map_prefix):
        if "." in map_prefix:
            self.np, self.cp = map_prefix.split(".", 1)
        else:
            self.np, self.cp = map_prefix, ""
        self.map_prefix = map_prefix

    def add_descripteur(self, descripteur):
        # print("ajout descripteur", self.base, descripteur)
        # raise
        niveau, classes, attr, valeur, fonction = descripteur
        dyn = any(["[" in i for i in classes])
        if "[" in attr:
            dyn = True
        if valeur:
            att, defaut = valeur
            if att:
                dyn = True
        if dyn:
            self.dyndescr.append(descripteur)
        else:
            self.descripteurs.append(descripteur)

    def resolve_static(self, regle):
        if self.static:
            return
        self.connect = self.mapper.getdbaccess(regle, self.base)
        self.schemabase = self.connect.schemabase
        mod = regle.getvar("mod")
        set_prefix = regle.getvar("prefix") == "1"
        if set_prefix:
            prefix = self.connect.prefix
            self.reg_prefix(prefix)
        mod = mod.upper()
        print("resolve", self.base, mod, set_prefix)
        for niveau, classes, attr, valeur, fonction in self.descripteurs:
            vref = valeur[1] if valeur else ""
            for j in classes:
                self.static.update(
                    self.add_classlist(niveau, j, attr, vref, fonction, mod)
                )

    def set_prefix(self, cldef):
        niveau, classe = cldef[:2]
        map_n = "_".join((self.np, niveau)) if self.np else niveau
        map_c = "_".join((self.cp, classe)) if self.cp else classe
        return (map_n, map_c)

    def add_classlist(self, niveau, classe, attr, valeur, fonction, mod):
        multi = not ("=" in mod)
        mod = mod.replace("=", "")
        nocase = "NOCASE" in mod
        mod = mod.replace("NOCASE", "")
        if not mod:
            mod = "A"
        classlist = self.schemabase.select_niv_classe(
            niveau, classe, attr, tables=mod, multi=multi, nocase=nocase
        )
        direct = dict()
        for i in classlist:
            mapped = self.set_prefix(i)
            direct[mapped] = (i, attr, valeur, fonction)
        # print("classlist", direct)
        return direct

    def resolve(self, regle, obj):

        self.resolve_static(regle)
        self.resolve_dyn(regle, obj)
        self.getschematravail(regle)

    def resolve_dyn(self, regle, obj):
        mod = regle.getvar("mod")
        mod = mod.upper()
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
                        self.add_classlist(niveau, classe, attr, valeur, fonction, mod)
                    )

    def classlist(self):
        return itertools.chain(self.static.items(), self.dynlist.items())

    def getschematravail(self, regle):
        liste_mapping = []
        liste_classes = []
        for mapping, definition in self.classlist():
            ident = definition[0]
            liste_mapping.append((*mapping, *ident))
            liste_classes.append(ident)
        print(" creation schema travail", self.base, len(liste_classes))
        schema_travail, liste2 = self.schemabase.creschematravail(
            regle, liste_classes, self.base
        )
        schema_travail.init_mapping(liste_mapping)
        self.schema_travail = schema_travail
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
        self.autobase = base == "*" or not base
        self.base = base
        self.schema_travail = None
        self.defaultbase = base
        self.baseselectors = dict()
        self.classes = dict()
        self.inverse = dict()
        self.refbases = set()
        self.onconflict = "add"

    def __repr__(self):
        return repr([repr(bs) for bs in self.baseselectors.values()])

    def add_descripteur(
        self, base, niv, classes=[""], attribut="", valeur=(), fonction="="
    ):
        descripteur = (niv, classes, attribut, valeur, fonction)
        map_prefix = ""
        base = (base or self.defaultbase) if self.autobase else self.base
        # print("add descripteur", self.autobase, base, descripteur)
        self.add_selector(base, descripteur)

    def add_niv_class(self, base, niveau, classe, attribut="", valeur=(), fonction="="):
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
        if base is None:
            return
        if base not in self.baseselectors:
            self.baseselectors[base] = TableBaseSelector(self.mapper, base, "")
        self.baseselectors[base].add_descripteur(descripteur)

    def idbase(self, base):
        """identifie une base de donnees"""
        if base in self.mapper.dbref:
            base = self.mapper.dbref[base]
            return base
        print("base inconnue", base, self.mapper.dbref)
        return None

    def resolve(self, regle, obj):
        for base in self.baseselectors:
            self.baseselectors[base].resolve(regle, obj)

    def get_classes(self):
        for base in self.baseselectors:
            yield from self.baseselectors[base].static.items()
        for base in self.baseselectors:
            yield from self.baseselectors[base].dynlist.items()

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

    def getschematravail(self, regle):
        for basesel in self.baseselectors.values():
            schema_travail = basesel.getschematravail(self, regle)
            if self.schema_travail is None:
                self.schema_travail = schema_travail.copy()
            else:
                self.fusion_schema(schema_travail)


# =============================================================
# =============outils de preparation de selecteurs=================
# =============================================================


def select_in(regle, fichier, base, classe=[], att="", valeur=()):
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
        selecteur = stock_param.namedselectors.get(fichier[4:])
        if not selecteur:
            print("selecteur inconnu", fichier[4:])
            raise StopIteration(2)
        return selecteur
    selecteur = TableSelector(regle, base=base)
    if fichier.startswith("#schema:"):  # liste de classes d'un schema
        nom = fichier[7:]
        if nom in stock_param.schemas:
            print("lecture schema", nom)
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
            print("select projet qgs", fichier)
            for i in fich:
                if "datasource" in i:
                    table = _extract(i, "table=")
                    database = _extract(i, "dbname=")
                    host = _extract(i, "host=").lower()
                    port = _extract(i, "port=").lower()
                    niveau, classe = table.split(".")
                    base = (database, "host=" + host, "port=" + port)
                    selecteur.add_descripteur(base, niveau, [classe])

    except FileNotFoundError:
        print("fichier qgs introuvable ", fichier)
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


def filelist(fichier):

    """liste des fichiers de comparaison """
    clef = ""
    if "*." in os.path.basename(fichier):
        clef = os.path.basename(fichier)
        clef = os.path.splitext(clef)[-1]
        fichier = os.path.dirname(fichier)
    #        print(' clef ',clef,fichier)
    LOGGER.info("charge_liste: chargement " + str(fichier))

    #    print ('-------------------------------------------------------chargement',fichier)
    for f_interm in str(fichier).split(","):
        if os.path.isdir(f_interm):
            # on charge toutes les listes d'un repertoire (csv et qgs)
            for i in os.listdir(f_interm):
                if clef in i:
                    LOGGER.debug("chargement liste " + i + " repertoire " + f_interm)
                    if os.path.isdir(f_interm):
                        yield from filelist(f_interm)
                    #                    print("chargement liste ", i, 'repertoire:', f_interm)
                    else:
                        yield f_interm


def selecteur_from_fich(fichier, selecteur, codec=DEFCODEC):
    for fich, chemin in scandirs("", fichier, rec=True):
        element = os.path.join(chemin, fich)
        if fich.endswith(".qgs"):
            _select_from_qgs(element, selecteur, codec)
        elif fich.endswith(".csv"):
            _select_from_csv(element, selecteur, codec)
    print("selecteur from fich", selecteur.baseselectors.keys())
