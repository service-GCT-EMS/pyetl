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
from .outils import prepare_mode_in


DEBUG = False
LOGGER = logging.getLogger("pyetl")
# modificateurs de comportement reconnus
DBACMODS = {"A", "T", "V", "=", "NOCASE"}
DBDATAMODS = {"S", "L"}
DBMODS = DBACMODS | DBDATAMODS


class TableBaseSelector(object):
    """condition de selection de tables dans un schema"""

    def __init__(self, mapper, base=None, map_prefix="", schemaref=None):
        self.mapper = mapper
        self.base = base
        self.schemaref = schemaref
        self.valide = bool(base or schemaref)
        self.set_prefix(map_prefix)
        self.descripteurs = []
        self.dyndescr = []
        # un descripteur est un tuple
        # (type,niveau,classe,attribut,condition,valeur,mapping)
        self.direct = dict()

    # def add_classe(self, classe):
    #     self.direct.add(classe)

    def set_prefix(self, map_prefix):
        if "." in map_prefix:
            self.np, self.cp = map_prefix.split(".", 1)
        else:
            self.np, self.cp = map_prefix, ""
        self.mapprefix = map_prefix


    def add_descripteur(self, descripteur):
        niveau, classe, attr, mod = descripteur
        if "[" in niveau or "[" in classe:
            self.dyndescr.append(descripteur)
        else:
            self.descripteurs.append(descripteur)

    def prepare_direct(self, regle):
        connect = self.mapper.getdbaccess(regle, self.base)
        self.schemabase = connect.schemabase
        self.direct = {
            i: j for i, j in self.direct.items() if i in self.schemabase.classes
        }

    def set_prefix(self, cldef):
        niveau, classe = cldef[:2]
        map_n = "_".join((self.np, niveau)) if self.np else niveau
        map_c = "_".join((self.cp, classe)) if self.np else classe
        return (map_n, map_c)

    def add_classlist(self, niveau, classe, attr, mod):
        mod = mod.upper()
        multi = "=" in mod
        mod = mod.replace("=", "")
        nocase = "NOCASE" in mod
        mod = mod.replace("NOCASE", "")
        classlist = self.schemabase.select_classes(
            niveau, classe, attr, tables=mod, multi=multi, nocase=nocase
        )
        for i in classlist:
            mapped = self.set_prefix(i)
            self.direct[i] = mapped

    def resolve_static(self, regle):
        """convertit une liste de descripteurs en liste de classes"""
        self.prepare_direct(regle)
        for descripteur in self.descripteurs:
            niveau, classe, attr, mod = descripteur
            self.add_classlist(niveau, classe, attr, mod)

    def resolve_dyn(self, regle, obj):
        self.prepare_direct(regle)
        for descripteur in self.dyndescr:
            niveau, classe, attr, mod = descripteur
            if niveau.startswith("["):
                niveau = obj.attributs.get(niveau[1:-1])
            if classe.startswith("]"):
                niveau = obj.attributs.get(classe[1:-1])
            self.add_classlist(niveau, classe, attr, mod)


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
        self.autobase = base is None
        self.base = base
        self.baseselectors = dict()
        self.classes = dict()
        self.inverse = dict()
        self.refbases = set()
        self.onconflict = "add"

    def __repr__(self):
        return repr([repr(bs) for bs in self.baseselectors.values()])


    def make_descripteur(
        self, base, liste, classes=[""], attribut=[""], valeur="", fonction="="
    ):
        niv = ""
        cla = classes
        if len(liste) == 1:
            niv = liste[0]
        elif len(liste) == 2:
            niv, cla = liste
        elif len(liste) == 3:
            _, niv, cla = liste
        descripteur = (niv, cla, attribut, valeur, fonction)
        map_prefix = ""
        if self.autobase:
            if base not in self.refbases:
                map_prefix = base
        else:
            base = self.base
        self.add_selector(base, descripteur, map_prefix)

    def split_pt(self, element):
        if not element:
            return [""]
        tmp = element.split(".")
        tmp2 = [tmp[0]]
        for j in tmp[1:]:
            if j and j[0].isalpha():
                tmp2[-1] = tmp2[-1] + "." + j
            else:
                tmp2.append(j)
        return tmp2

    def make_nivlist(self, niveau):
        nivlist = []
        if not niveau:
            return []
        if not isinstance(niveau, list):
            niveau = [niveau]
        for i in niveau:
            nivlist.append(self.split_pt(i))
            tmp = i.split(".")
            tmp2 = [tmp[0]]
            for j in tmp[1:]:
                if j and j[0].isalpha():
                    tmp2[-1] = tmp2[-1] + "." + j
                else:
                    tmp2.append(j)

    def add_niveau(self, niveau, attribut, valeur, fonction):
        """ajoute un descripteur de niveau simple"""
        self.make_descripteur(niveau, [], attribut, valeur, fonction)

    def add_niv_class(self, niveau, classe, attribut, valeur, fonction):
        if not niveau:
            niveau = [""]
        for i in niveau:
            self.make_descripteur(i, classe, attribut, valeur, fonction)

    def add_selector(self, base, descripteur, map_prefix=""):
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
            self.baseselectors[base] = TableBaseSelector(self.mapper, base, map_prefix)
        self.baseselectors[base].add_descripteur(descripteur)

    def idbase(self, base):
        """identifie une base de donnees"""
        if base in self.mapper.dbref:
            if isinstance(base, str):
                return base
            return self.mapper.dbref[base]
        print("base inconnue", base, self.mapper.dbref)
        return None

    def resolve(self, regle):
        for base in self.baseselectors:
            self.baseselectors[base].resolve_static(regle)
            for ident, id2 in self.baseselectors[base].direct.items():
                b2 = self.inverse.get(id2)
                if b2 and b2 != base:
                    print(" mapping ambigu", ident, "dans", base, "et", b2)
                    continue
                self.inverse[id2] = base

    def getschematravail(self, schemabase):
        pass


def _select_niv_in(regle, niv, autobase=False):
    """gere les requetes de type niveau in..."""
    print("mode_niv in:", niv, autobase)

    mode_in = "b" if autobase else "n"
    taille = 3 if autobase else 2
    mode_select, valeurs = prepare_mode_in(niv, regle, taille=taille, type_cle=mode_in)
    niveau = []
    classe = []
    attrs = []
    cmp = []
    base = []
    # selecteur = DB.TableSelector(regle)
    # for i in valeurs:
    #     selecteur.add_selector(*i)
    #     print("add_selector", i)
    for i in valeurs:
        liste_defs = list(i)
        # print("mode_niv in:liste_defs", liste_defs)
        bdef = liste_defs[0]
        if bdef in regle.stock_param.dbref:
            # c est une definition de base
            bdef = regle.stock_param.dbref.get(bdef)
        if autobase:
            base.append(bdef)
            liste_defs.pop(0)
        else:
            base.append("")

        niveau.append(liste_defs.pop(0) if liste_defs else "")
        classe.append(liste_defs.pop(0) if liste_defs else "")
        attrs.append(liste_defs.pop(0) if liste_defs else "")
        cmp.append(liste_defs.pop(0) if liste_defs else "")

    # print(
    #     "mode_niv in:lu ",
    #     "\n".join(str(i) for i in zip(base, niveau, classe, attrs, cmp)),
    # )
    return base, niveau, classe, attrs, cmp


def prepare_selecteur(regle):
    """ extrait les parametres d acces a la base"""
    # TODO gerer les modes in dynamiques
    base = regle.code_classe[3:]
    autobase = False
    if base == "*" or base == "":
        base = ""
        autobase = True

    niveau, classe, att = "", "", ""
    niv = regle.v_nommees["val_sel1"]
    cla = regle.v_nommees["sel2"]
    att = regle.v_nommees["val_sel2"]
    attrs = []
    cmp = []
    print("param_base", base, niv, cla, "autobase:", autobase)

    if niv.lower().startswith("in:"):  # mode in
        b_lue, niveau, classe, attrs, cmp = _select_niv_in(
            regle, niv[3:], autobase=autobase
        )
        if autobase:
            base = b_lue
        else:
            base = [base] * len(niveau)
    elif cla.lower().startswith("in:"):  # mode in
        clef = 1 if "#schema" in cla else 0
        mode_select, valeurs = prepare_mode_in(cla[3:], regle, taille=1, clef=clef)
        classe = list(valeurs.keys())
        niveau = [niv] * len(classe)
    elif "," in niv:
        niveau = niv.split(",")
        if "." in niv:
            classe = [(i.split(".") + [""])[1] for i in niveau]
            niveau = [i.split(".")[0] for i in niveau]
        else:
            classe = [cla] * len(niveau)
    elif "," in cla:
        classe = cla.split(",")
        niveau = [niv] * len(classe)

    else:
        niveau = [niv]
        classe = [cla]
    if attrs:
        att = [(i, j) for i, j in zip(attrs, cmp)]

    regle.dyn = "#" in niv or "#" in cla
    print("parametres acces base", base, niveau, classe, att, regle)

    # gestion multibase
    if isinstance(base, list):
        multibase = {i: ([], [], []) for i in set(base)}
        for b, n, c, a in zip(base, niveau, classe, att):
            # print("traitement", b, n, c, a)
            nl, cl, al = multibase[b]
            nl.append(n)
            cl.append(c)
            al.append(a)
        regle.cible_base = multibase
        # print("retour multibase", multibase)
    else:
        regle.cible_base = {base: (niveau, classe, att)}
    return True
