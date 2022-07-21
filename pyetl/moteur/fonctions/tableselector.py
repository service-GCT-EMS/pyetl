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
import xml.etree.ElementTree as ET
from collections import namedtuple
from pyetl.vglobales import DEFCODEC
from .outils import scandirs, hasbom, _extract


DEBUG = False
LOGGER = logging.getLogger(__name__)
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
    il y a un Tablebaseselector par base concernee par une selection"""

    def __init__(self, selecteur, base=None, map_prefix="", schemaref=None):
        self.selecteur = selecteur
        self.regle_ref = selecteur.regle_ref
        self.mapper = self.regle_ref.stock_param
        self.base = base
        self.nombase = base if base != "*" else ""
        self.dynbase = self.base[1:-1] if self.base.startswith("[") else ""
        self.type_base = ""
        self.chemin = ""
        self.racine = ""
        self.connect = None
        self.nobase = False
        # si vrai une liste de classes direct est fournie
        # dans ce cas le selecteur ne gere que la liste de classes et pas le schema
        self.schemaref = schemaref
        self.schemabase = None
        self.schema_travail = None
        self.valide = bool(base or schemaref)
        self.map_prefix = map_prefix
        self.reg_prefix(map_prefix)
        self.descripteurs = []
        self.dyndescr = []
        self.mapping = {}
        # un descripteur est un tuple
        # (type,niveau,classe,attribut,condition,valeur,mapping)
        self.staticlist = dict()
        self.dynlist = dict()
        self.unresolved = set()

    def __repr__(self):
        return (
            str(self.base)
            + ":"
            + str(len(self.descripteurs))
            + "->"
            + str(len(self.staticlist))
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

    def stocke_descripteur(self, descripteur):
        """stocke un descripteur de selection il y a un descripteur par niveau ou expression
        de selection de niveau
        un descripteur peut etre statique s il n integere aucun element dependant de l objet courant
        ou dynamique s il depend de l objet courant
        """
        # print("ajout descripteur", self.base, self.nombase, descripteur)
        # raise
        niveau, classes, attr, valeur, fonction = descripteur

        dyn = any(["[" in i for i in classes]) or "[" in niveau
        if "[" in attr or "[" in valeur:
            dyn = True
        if dyn:
            self.dyndescr.append(descripteur)
        else:
            self.descripteurs.append(descripteur)

    def resolve_static(self, obj):
        """transformation de la liste de descripteurs statiques en liste de classes
        le selecteur gere la connection a la base se donnees"""
        if self.dynbase and obj.attributs.get(self.dynbase) != self.base:
            self.staticlist = dict()
            self.base = obj.attributs.get(self.dynbase)
            # self.nombase = self.base if self.base != "*" else ""
            if not self.base:
                return False
            self.nombase = self.base if self.base != "*" else ""
        if self.staticlist:
            return

        mod = self.regle_ref.mods
        # print("resolution statique", mod)
        set_prefix = self.regle_ref.getvar("set_prefix") == "1"
        prefix = ""
        if self.base and os.path.isfile(self.base):  # bases fichier
            self.base = "__filedb"
        if self.base and self.base != "__filedb":
            try:
                self.mapper.load_paramgroup(self.base, nom=self.base)
            except KeyError:
                self.nobase = True
            prefix = self.regle_ref.getvar("prefix_" + self.base)
            # print("acces base", self.base)
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
            # print("connection ", self.nombase, self.base)
            if self.base != "__filedb":
                try:
                    self.connect = self.mapper.getdbaccess(self.regle_ref, self.nombase)
                except StopIteration:
                    print("connection impossible", self.nombase)
            else:
                type_base = os.path.splitext(self.nombase)[-1]
                if type_base.startswith("."):
                    type_base = type_base[1:]
                self.connect = self.mapper.getdbaccess(
                    self.regle_ref,
                    self.nombase,
                    type_base=type_base,
                )
            if self.connect:
                self.schemabase = self.connect.schemabase
                prefix = self.connect.prefix
                if set_prefix:
                    self.reg_prefix(prefix)
            else:
                self.schemabase = None
        # print("resolve", self.base, mod, set_prefix, prefix, self.nobase)

        mod = [i.upper() for i in mod]
        # print("traitement descripteurs", self.descripteurs)
        for niveau, classes, attr, valeur, fonction in self.descripteurs:
            if niveau == "#":
                pass  # placeholder genere une entree base mais pas de classes
            vref = valeur[1] if valeur else ""
            for j in classes:
                classlist = self.add_classlist(
                    niveau, j, attr, vref, fonction, mod, nobase=self.nobase
                )
                if classlist:
                    self.staticlist.update(classlist)
                else:
                    self.unresolved.add((niveau, j))

    def set_prefix(self, cldef):
        """prefixage ses noms pour lea gestion des conflits entre base"""
        niveau, classe = cldef[:2]
        map_n = "_".join((self.np, niveau)) if self.np else niveau
        map_c = "_".join((self.cp, classe)) if self.cp else classe
        return (map_n, map_c)

    def add_classlist(self, niveau, classe, attr, valeur, fonction, mod, nobase=False):
        """transformation effective d un descripteur en liste de classes"""
        mod = "".join(mod)
        mod = mod.upper()
        multi = not ("=" in mod or "=" in fonction)
        nocase = "NOCASE" in mod
        mod = mod.replace("=", "")
        mod = mod.replace("NOCASE", "")
        if not mod:
            mod = {"A"}
        if nobase:
            classlist = [(niveau, classe)]
        else:
            classlist = (
                self.schemabase.select_niv_classe(
                    niveau, classe, attr, tables=mod, multi=multi, nocase=nocase
                )
                if self.schemabase
                else ()
            )
        direct = dict()
        # print("add classlist: multi", multi, classlist)
        for i in classlist:
            mapped = self.set_prefix(i)
            direct[mapped] = (i, attr, valeur, fonction)
        # print("classlist", direct)
        return direct

    def resolve(self, obj):
        """fonction de transformation de la liste de descripteurs en liste de classe
        et preparation du schema de travail"""
        self.nobase = self.nobase or self.regle_ref.getvar("nobase") == "1"
        # print("resolve: base=", self.base)
        if self.base == "__filedb":
            if obj and obj.attributs["#groupe"] == "__filedb":
                self.staticlist = dict()
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

        self.resolve_static(obj)
        if self.dyndescr:
            # print("resolve dyn", obj)
            solved = self.resolve_dyn(obj)
        else:
            solved = True
        if solved:
            if not self.nobase:
                self.getschematravail(self.regle_ref)
            else:
                liste_classes, liste_mapping = self.getmapping()
                # print("mapping", liste_mapping)
                self.mapping = {(i0, i1): (m0, m1) for m0, m1, i0, i1 in liste_mapping}
            if self.schema_travail:
                self.schema_travail.metas["restrictions"] = self.selecteur.metainfos
        return solved

    def resolve_dyn(self, obj):
        """transformation de descripteurs dynamiques en liste de classes
        les elements dynamiques sont resolus a partir des champs de l objet courant"""
        mod = self.regle_ref.mods
        # print("resolve dyn :regleref mod", mod)
        mod = [i.upper() for i in mod]
        if obj is None and self.dyndescr:
            # print("elements dynamiques", self.dyndescr)
            return False
        self.dynlist = dict()
        # if self.dyndescr:
        # print("resolution descripteur dynamique", self.dyndescr)
        for niveau, classes, attr, valeur, fonction in self.dyndescr:
            # print("descripteur dynamique", niveau, classes, attr, valeur, fonction, obj)
            if attr.startswith("["):
                attr = obj.attributs.get(attr[1:-1])
            if niveau.startswith("["):
                niveau = obj.attributs.get(niveau[1:-1])
            if attr:
                if valeur:
                    valeur = (
                        obj.attributs.get(valeur[0], valeur[1])
                        if valeur[0]
                        else valeur[1]
                    )
            for classe in classes:
                # print("dyn: traitement classe", classe)
                if classe.startswith("["):
                    classe = obj.attributs.get(classe[1:-1])

                # print("prepare dynlist:", niveau, classe, attr, valeur, fonction, mod)
                self.dynlist.update(
                    self.add_classlist(
                        niveau, classe, attr, valeur, fonction, mod, nobase=self.nobase
                    )
                )
        # print("dynlist:", self.dynlist)
        return True

    def classlist(self):
        """retourne un iterateur sur la liste de classes resolue"""
        n = 0
        maxsel = self.selecteur.maxsel
        if self.schema_travail:
            for i in self.schema_travail.ordre:
                mapped = self.set_prefix(i)
                if mapped in self.staticlist:
                    yield mapped, self.staticlist[mapped]
                elif mapped in self.dynlist:
                    yield mapped, self.dynlist[mapped]
                else:
                    yield mapped,(i, "", "", "")
                n += 1
                if maxsel and n > maxsel:
                    break
        else:
            for i in itertools.chain(self.staticlist.items(), self.dynlist.items()):
            # print("dans classlist", maxsel, n)
                yield i
                n += 1
                if maxsel and n > maxsel:
                    break

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
        if not self.schemabase:
            return None
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
        self.autobase = (base == "*") or (regle.getvar("autobase") == "1")
        self.base = base if base != "*" else ""
        self.schema_travail = None
        self.defaultbase = "*"
        self.dynbase = self.base[1:-1] if self.base.startswith("[") else ""
        self.baseselectors = dict()
        self.classes = dict()
        self.inverse = dict()
        self.refbases = set()
        self.resolved = False
        self.static = True
        self.nobase = False
        self.onconflict = "add"
        self.nom = "S" + str(self.regle_ref.numero)
        self.metainfos = ""
        self.maxsel = 0
        self.dbref=dict()

    def __repr__(self):
        return self.nom + repr([repr(bs) for bs in self.baseselectors.values()])

    def add_descripteur(
        self, base, niv, classes=[""], attribut="", valeur=(), fonction="="
    ):
        descripteur = (niv, classes, attribut, valeur, fonction)
        # print("add descripteur", base, descripteur)
        self.add_descripteur_to_base(base, descripteur)

    def add_niv_class(self, base, niveau, classe, attribut="", valeur=(), fonction="="):
        if not base:
            return
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

    def add_descripteur_to_base(self, base, descripteur):
        if "." in base:
            tmp = base.split(".")
            if len(tmp) >= 3:
                base = tmp[0]
                descripteur = tmp[1:]
        if self.autobase or not self.base:
            base = self.idbase(base)
        else:
            base = self.base
        if not base:
            print(" pas de base", descripteur, self.autobase)
            return
        if base not in self.baseselectors:
            self.baseselectors[base] = TableBaseSelector(self, base, "")
        # print("add descripteur", base, descripteur)
        self.baseselectors[base].stocke_descripteur(descripteur)
        if self.static and self.baseselectors[base].dyndescr:
            self.static = False

    def merge(self, selecteur):
        """fusionne 2 selecteurs"""
        for base, bsel in selecteur.baseselectors.items():
            for descripteur in bsel.descripteurs:
                self.add_descripteur_to_base(base, descripteur)
            for descripteur in bsel.dyndescr:
                self.add_descripteur_to_base(base, descripteur)
        self.metainfos = self.metainfos + " " + selecteur.metainfos

    def removebase(self, base):
        """supprime une base d un selecteur multibase"""
        try:
            del self.baseselectors[base]
            print("suppression base", base)
            return True
        except KeyError:
            print("suppression base : keyerror", base, self.baseselectors.keys())
            return False

    def setdbref(self):
        """identifie les references de bases de donnees pour qgis"""
        priorites = dict()
        refbases=set(self.regle_ref.getvar("baselist").split(",")) if self.regle_ref else {}
        ## variable:baselist:liste de bases prioritaires pour les selections qgis(override du defaut du site_params)
        for nom,variables  in self.mapper.site_params.items():
            base, host, port = "", "", ""
            priorite = 99
            for clef, val in variables:
                if clef == "server":
                    if "port" in val and "host" in val:
                        host, port = val.split(" ", 1)
                    else:
                        host = val
                elif clef == "base":
                    base = val
                elif clef == "priorite":
                    priorite = int(val)
            if nom in refbases:
                priorite=-99
            if base:
                tb = (base, host, port)
                if tb in priorites:
                    if priorite > priorites[tb]:
                        # print("non retenu", nom, tb, priorite, priorites[tb])
                        self.dbref[nom] = self.dbref[tb]
                        for i, j in self.dbref.items():
                            if j == nom:
                                self.dbref[i] = self.dbref[tb]
                        continue
                # base non prioritaire on a deja la definition on la remappe sur l autre
                # print("retenu", nom, tb, priorite, priorites.get(tb))
                priorites[tb] = priorite
                self.dbref[tb] = nom
                self.dbref[",".join(tb)] = nom
                self.dbref[nom] = nom









    def idbase(self, base):
        """identifie une base de donnees"""
        if not self.dbref:
            self.setdbref()
        if not base:
            print("idbase: pas de base definie", base)
        if base in self.dbref:
            base = self.dbref[base]
        elif base == "*":
            pass
        elif base.startswith("*"):  # service
            pass
        elif base == "__filedb":  # fichier
            pass
        else:
            print("idbase: base inconnue", base)
        return base

    def resolve(self, obj=None):
        # print(" debut resolve", self.baseselectors.keys(), self.resolved, self.static)
        if self.resolved and self.static:
            return True
        complet = len(self.baseselectors)
        self.nobase = self.nobase or self.regle_ref.istrue("nobase")
        static = True
        for base in self.baseselectors:
            complet = complet and self.baseselectors[base].resolve(obj)
            self.static = (
                self.static
                and not bool(self.baseselectors[base].dyndescr)
                and not bool(self.baseselectors[base].dynbase)
            )
        self.resolved = complet
        # print(
        #     " fin resolve",
        #     self,
        #     self.baseselectors.keys(),
        #     self.resolved,
        #     self.static,
        #     len(list(self.classlist())),
        #     self.schema_travail,
        # )
        return complet

    def classlist(self):
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

    def check(self, regle, obj=None):
        """verifie si les classes d un selecteur existent dans les bases associees"""
        if not self.resolved:
            self.resolve(obj)
        for baseselector in self.baseselectors.values():
            print("analyse base"), baseselector.base
            print("classes trouvees", list(baseselector.classlist()))
            print("classes non trouvees", baseselector.base, baseselector.unresolved)


# =============================================================
# =============outils de preparation de selecteurs=================
# =============================================================


def select_in(regle, fichier, base, classe=[], att="", valeur=(), nom=""):
    """precharge les elements des selecteurs:
    in:{a,b,c}                  -> liste de valeurs dans la commande
    in:#schema:nom_du_schema    -> liste des tables d'un schema
    in:#sel:                    -> selecteur stocke
    in:nom_de_fichier           -> contenu d'un fichier
    in:[att1,att2,att3...]      -> attributs de l'objet courant
    in:(attributs)              -> noms des attributs de l'objet courant
    in:st:nom_du_stockage       -> valeurs des objets en memoire (la clef donne l'attribut)
    in:db:nom_de_la_table       -> valeur des attributs de l'objet en base (la clef donne le nom du champs)
    """
    stock_param = regle.stock_param
    # print("select in ", fichier, base, classe)

    fichier = fichier.strip()
    #    valeurs = get_listeval(fichier)
    liste_valeurs = fichier[1:-1].split(",") if fichier.startswith("{") else []
    liste_atts = (
        fichier[1:-1].split(",")
        if (fichier.startswith("[") and fichier.endswith("]"))
        else []
    )
    valeurs = {i: i for i in liste_valeurs}
    LOGGER.info("element a lire: %s base: %s", fichier, base)

    if fichier.startswith("#sel:"):  # selecteur externe
        selecteur = stock_param.namedselectors.get(fichier[5:])
        if not selecteur:
            LOGGER.error("selecteur inconnu %s,(%s)", fichier[5:], regle.ligne)
            # print(
            #     "selecteur inconnu",
            #     regle,
            #     fichier[5:],
            #     stock_param.namedselectors.keys(),
            # )
            raise StopIteration(2)
        sel1 = getselector(regle, base=base, nom=nom)
        sel1.merge(selecteur)
        return sel1

    selecteur = getselector(regle, base=base, nom=nom)

    selecteur.metainfos = fichier
    if liste_atts:
        selecteur.static = False
        for att in liste_atts:
            selecteur.add_descripteur(base, "[" + att + "]")
        print("selecteur dans attributs", selecteur)
        return selecteur

    if fichier.startswith("#schema:"):  # liste de classes d'un schema
        nomschema = fichier[7:]
        if nomschema in stock_param.schemas:
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
            # LOGGER.info("lecture statique %s", fichier)
            mode = "in_s"  # jointure statique
            try:
                selecteur_from_fich(regle, fichier, selecteur)
            except FileExistsError:
                LOGGER.error("fichier ou repertoire inexistant %s", fichier)
                return None
        # LOGGER.info("selecteur lu  %s", repr(selecteur))
        return selecteur


def _select_from_qgs(fichier, selecteur, codec=DEFCODEC):
    """prechargement d un fichier projet qgis"""
    # selecteur.autobase = True
    try:
        codec = hasbom(fichier, codec)
        with open(fichier, "r", encoding=codec) as fich:
            # LOGGER.info("projet %s", fichier)
            # print("----------------select projet qgs", fichier)
            for i in fich:
                if "datasource" in i and not "<datasource></datasource>" in i:
                    table = _extract(i, "table=")
                    database = _extract(i, "dbname=")
                    service = _extract(i, "service=")
                    host = _extract(i, "host=").lower()
                    port = _extract(i, "port=").lower()
                    niveau, classe = (
                        table.split(".") if "." in table else ("tmp", table)
                    )
                    niveau = niveau.replace('"', "")
                    classe = classe.replace('"', "")
                    if database:
                        base = (database, "host=" + host, "port=" + port)
                    elif service:
                        base = "*" + service
                    else:
                        print("analyse qgs: identification filedb", i)
                        base = "__filedb"
                    selecteur.add_descripteur(base, niveau, [classe], fonction="=")
                    # print("qgs : descripteur", base, niveau, [classe])
                    LOGGER.debug("descripteur %s %s %s", base, niveau, classe)
                elif "provider" in i:
                    pass
                # print(" provider", i)
    except FileNotFoundError:
        LOGGER.error("fichier qgs introuvable %s", fichier)
        # print("fichier qgs introuvable ", fichier)

    LOGGER.info("lu fichier qgis " + fichier)
    # print("lus fichier qgis ", fichier, selecteur)
    return True


def adapt_qgs_datasource(regle, obj, fichier, selecteur, destination, codec=DEFCODEC):
    """modifie un fichier qgs pour adapter les noms des bases et des niveaux"""
    # print ("adapt_qgs", fichier, destination)
    regle.mods="="
    if selecteur and not selecteur.resolved:
        selecteur.resolve(obj)
    destbase = regle.base
    basedict = regle.basedict
    enums_to_list = regle.istrue("enums_to_list")
    if os.path.isfile(fichier):
        flist=[(os.path.basename(fichier),"")]
        fichier=os.path.dirname(fichier)
    else:
        flist=scandirs(fichier, "", rec=True)
    for fich, chemin in flist:
        if not fich:  # un peu bizarre on a donne un fichier a la place d un repertoire
            element = os.path.join(fichier, chemin) if chemin else fichier
        else:
            element = os.path.join(fichier, chemin, fich)
        nom = os.path.basename(element)
        
        if not (element.endswith(".qgs") or element.endswith(".qlr")):
            continue
        codec = hasbom(element, codec)
        fdest = os.path.join(destination, chemin, nom)
        os.makedirs(os.path.dirname(fdest), exist_ok=True)
        sortie = open(fdest, "w", encoding=codec)
        if fdest==element:
            regle.stock_param.logger.warning(
                "attention ecrasement du fichier %s-> non traite", element
            )
            continue
        seldef = select_in(regle, element, "*") if not selecteur else selecteur
        seldef.resolve(obj)
        regle.stock_param.logger.info(
            "traitement (%s) %s->" + fdest, seldef.nom, element
        )

        with open(element, "r", encoding=codec) as entree:
            # print("adapt projet qgs", element)
            for i in entree:
                if "datasource" in i or 'source="' in i:
                    table = _extract(i, "table=")
                    database = _extract(i, "dbname=")
                    service = _extract(i, "service=")
                    inithost = _extract(i, "host=")
                    host = inithost.lower()
                    initport = _extract(i, "port=")
                    port = initport.lower()
                    niveau, classe = (
                        table.split(".") if "." in table else ("tmp", table)
                    )
                    ident = (niveau, classe)
                    if database:
                        base = (database, "host=" + host, "port=" + port)
                        idbase = seldef.idbase(base)
                        tablemap = (niveau, classe)
                        if idbase in seldef.baseselectors:
                            baseselector = seldef.baseselectors[idbase]
                            if seldef.nobase or baseselector.schema_travail is None:
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
                        dbkey = (
                            "dbname='" + database + "' host=" + host + " port=" + port
                        )
                        if tablemap:
                            i = i.replace(
                                oldtable, '"' + tablemap[0] + '"."' + tablemap[1] + '"'
                            )
                        destbase = regle.base if regle.base else basedict.get(dbkey)

                        if destbase:
                            i = i.replace(olddbdef, destbase)
                        else:
                            print("datasource inconnue", olddbdef, basedict)

                    # print("datasource=>", i)

                sortie.write(i)

    # print ('lus fichier qgis ',fichier,list(stock))
    return True

def convert_qgs_enums(nom,selecteur):
    """convertit les enums d un projet qgis en liste de valeurs"""
    projet = ET.parse(nom)
    racine = os.path.dirname(nom)
    for layer in projet.iter("maplayer"):
        provider = layer.find("provider")
        #        print ('couches',layer.find('layername').text, ' type : ',layer.find('provider').text, layer.find('datasource').text)
        #        print ('valeur de provider',provider)
        if provider is not None:
            #            print ('-------------------------valeur de provider',provider)

            sourcetype = provider.text
            source = layer.find("datasource")
            ligne_source = source.text
            if sourcetype == "postgres":
                # traitement base postgres : on passe en base locale et on modifie les elements
                l = ligne_source.split(" ")
                table, dbname, svname, port = ("", "", "", "")
                
                for k in l:
                    v = k.split("=")
                    if "dbname" in v[0]:
                        dbname = v[1].replace("'", "")
                    if v[0] == "table":
                        table = v[1].replace('"', "")
                        if table in selecteur.schema_travail.classes:
                            table = selecteur.schema_travail.classes[table]
                    if v[0] == "host":
                        svname = v[1]
                    if v[0] == "port":
                        port = v[1]
                base = (dbname, "host=" + svname, "port=" + port)
                idbase = selecteur.idbase(base)
                if idbase in selecteur.baseselectors:
                    baseselector = selecteur.baseselectors[idbase]
                # print ('detecte base', dbname,svdef)
                table = table.replace('"', "")
                idtable = tuple(table.split("."))
                tabledef=baseselector.schematravail.classes.get(idtable)
                source.text = ligne_source
                # === analyse et modification des editeurs
                for editeur in layer.iter("edittype"):
                    widgettype = editeur.get("widgetv2type")
                    if (
                        editeur.get("widgetv2type") == "Enumeration"
                    ):  # c'est une enum : on modifie
                        nom_att_enum = editeur.get("name")
                        if nom_att_enum:
                            print("detection enum", dbname, "->", nom_att_enum)
                        if (nom_att_enum in tabledef.attributs):
                            nom_enum = tabledef.attributs[nom_att_enum].conformite
                            if (nom_enum in baseselector.schematravail.enumerations):
                                print("enum traitable:", nom_enum)
                                editeur.set("widgetv2type", "ValueMap")
                                config = editeur.find("widgetv2config")
                                for item in baseselector.schematravail.enumerations[nom_enum]:
                                    newvalue = ET.Element(
                                        "value", attrib={"key": item, "value": item}
                                    )
                                    config.append(newvalue)

                print ('transformation',source.text)

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
    et un mapping attributaire sous forme att=>nouveau,... elle n est pas utilisee par le selecteur
    """
    # print("select from csv", fichier, codec)
    try:
        codec = hasbom(fichier, codec)
        with open(fichier, "r", encoding=codec) as fich:
            for i in fich:
                ligne = i.replace("\n", "")  # on degage le retour chariot
                ligne = ligne.strip()
                if ligne.startswith("!"):
                    if ligne.startswith("!!"):
                        ligne = ligne[1:]
                    else:
                        continue
                if not ligne:
                    continue
                liste = [i.strip() for i in ligne.split(";")]
                # supprime les elements vides a la fin
                while liste:
                    if not liste[-1]:
                        liste.pop()
                    else:
                        break
                base, niveau, classe, attribut, valeur = [""] * 5
                if not liste:
                    continue
                if "." in liste[0]:  # niveau.classe ou base.niveau.classe
                    l2 = liste[0].split(".")
                    if len(l2) == 2:
                        niveau, classe = l2
                    elif len(l2) == 3:
                        base, niveau, classe = l2
                    if len(liste) == 2:  # on est au mapping
                        attribut = liste[1]
                    if len(liste) == 3:
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
                    if "." in attribut:  # c' est un mapping
                        attribut, valeur = "", ""
                classe = classe.split(",")

                # print(
                #     "analyse ligne",
                #     liste,
                #     "->",
                #     "-".join(
                #         (base, str(niveau), str(classe), str(attribut), str(valeur))
                #     ),
                # )

                for niv in niveau.split(","):
                    fonction = "="
                    if "*" in niveau or "*" in classe:
                        fonction = ""
                    selecteur.add_descripteur(
                        base, niveau, classe, attribut, valeur, fonction
                    )
    except FileNotFoundError:
        # print("fichier liste introuvable ", fichier)
        LOGGER.warning("fichier liste introuvable " + fichier)
    except UnicodeDecodeError:
        LOGGER.error("erreur encodage " + fichier + " n'est pas en " + codec)
        raise StopIteration(4)
    # print("prechargement selecteur csv", selecteur)


def selecteur_from_fich(regle, fichier, selecteur):
    # print("sel_from_fich:scandirs", fichier)
    LOGGER.debug("scandirs %s", fichier)

    for fich, chemin in scandirs("", fichier, rec=True):
        element = os.path.join(chemin, fich)
        # print("sel_from_fich:lu", element)
        if fich.endswith(".qgs") or fich.endswith(".qlr"):
            codec_qgs = regle.getvar("codec_qgs", DEFCODEC)
            _select_from_qgs(element, selecteur, codec_qgs)
        elif fich.endswith(".csv"):
            codec_csv = regle.getvar("codec_csv", DEFCODEC)
            _select_from_csv(element, selecteur, codec_csv)
    selecteur.metainfos = fichier
    # LOGGER.info("selecteur from fich %s", str(selecteur.baseselectors.keys()))
    # for nom, sel in selecteur.baseselectors.items():
    #     print(nom, "====>", sel.descripteurs)
    # raise


def getselector(regle, base=None, nom=""):
    """recuperation d un selecteur stocke"""
    if not nom:
        return TableSelector(regle, base)
    if nom in regle.stock_param.conditions:
        selecteur = regle.stock_param.namedselectors[nom]
    else:
        selecteur = TableSelector(regle, base)
        selecteur.nom = nom
        regle.stock_param.namedselectors[nom] = selecteur
    return selecteur
