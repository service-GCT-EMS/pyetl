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
        self.mapprefix = map_prefix
        self.descripteurs = []
        # un descripteur est un tuple
        # (type,niveau,classe,attribut,condition,valeur,mapping)
        self.direct = set()

    def add_classe(self, classe):
        self.direct.add(classe)

    def add_descripteur(self, descripteur):
        self.descripteurs.append(descripteur)

    def resolve(self, regle):
        """convertit une liste de descripteurs en liste de classes"""
        connect = self.mapper.getdbaccess(regle, self.base)
        self.schemabase = connect.schemabase
        self.direct = set([i for i in self.direct if i in self.schemabase.classes])
        for descripteur in self.descripteurs:
            niveau, classe, attr, mod = descripteur
            mod = mod.upper()
            multi = "=" in mod
            mod = mod.replace("=", "")
            nocase = "NOCASE" in mod
            mod = mod.replace("NOCASE", "")
            classlist = self.schemabase.select_classes(
                niveau, classe, attr, tables=mod, multi=multi, nocase=nocase
            )
            self.direct.update(classlist)


class TableSelector(object):
    """condition de selection de tables dans des base de donnees ou des fichiers
        generes par des condition in: complexes"""

    def __init__(self, regle, base=None):
        self.regle_ref = regle
        self.mapper = regle.stock_param
        self.autobase = base is None
        self.base = base
        self.baseselectors = dict()
        self.classes = dict()
        self.inverse = dict()
        self.refbases = set()
        self.mapmode = None

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

    def remap(self, ident, base):
        if self.mapmode is None:
            return ident
        niveau, classe = ident
        n2 = (base, niveau) if self.mapmode == "bn" else (niveau, base)
        return ("_".join(n2), classe)

    def resolve(self):
        for base in self.baseselectors:
            self.baseselectors[base].resolve()
            for ident in self.baseselectors[base].direct:
                id2 = self.remap(ident, base)
                b2 = self.inverse.get(id2)
                if b2 and b2 != base:
                    print(" mapping ambigu", ident, "dans", base, "et", b2)
                    continue
                self.inverse[id2] = base
                self.classes[base][ident] = id2

    def getschematravail(self, schemabase):
        pass


def _select_niv_in(regle, niv):
    """gere les requetes de type niveau in..."""
    mode_select, valeurs = prepare_mode_in(niv, regle, taille=2)
    niveau = []
    classe = []
    attrs = []
    cmp = []
    print("mode_niv in:lecture_fichier", valeurs)
    for i in valeurs:
        liste_defs = list(valeurs[i])
        print("mode_niv in:liste_defs", liste_defs)
        def1 = liste_defs.pop(0).split(".")
        if len(def1) == 1 and liste_defs and liste_defs[0]:
            # c'est de la forme niveau;classe
            defs2 = liste_defs.pop(0).split(".")
            def1.extend(defs2)
        # print("mode_niv in:def1",def1)
        niveau.append(def1[0])
        if len(def1) == 1:
            classe.append("")
            attrs.append("")
            cmp.append("")
        elif len(def1) == 2:
            classe.append(def1[1])
            attrs.append("")
            cmp.append("")
        elif len(def1) == 3:
            # print("detection attribut")
            classe.append(def1[1])
            attrs.append(def1[2])
            vals = ""
            if liste_defs:
                if liste_defs[0].startswith("in:"):
                    txt = liste_defs[0][3:]
                    vals = txt[1:-1].split(",") if txt.startswith("{") else []
                else:
                    vals = liste_defs[0]
            cmp.append(vals)
    # print ('mode_niv in:lu ','\n'.join(str(i) for i in zip(niveau, classe, attrs, cmp)))
    return niveau, classe, attrs, cmp


def prepare_selecteur(regle):
    """ attache une lise de classes a une regle (eventuellement multibase)"""
    # TODO gerer les modes in dynamiques
    base = regle.code_classe[3:]

    niveau, classe, att = "", "", ""
    niv = regle.v_nommees["val_sel1"]
    cla = regle.v_nommees["sel2"]
    att = regle.v_nommees["val_sel2"]
    attrs = []
    cmp = []
    print("param_base", base, niv, cla, att)
    if base == "*" or not base:
        regle.selecteur = regle.stock_param.selecteurs.get(niveau)
    elif niv.lower().startswith("in:"):  # mode in
        regle.selecteur = _select_niv_in(regle, niv[3:])
    elif cla.lower().startswith("in:"):  # mode in
        clef = 1 if "#schema" in cla else 0
        mode_select, valeurs = prepare_mode_in(cla[3:], regle, taille=1, clef=clef)
        classes = list(valeurs.keys())
        regle.selecteur = TableSelector(regle, base)
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
        att = (attrs, cmp)

    regle.dyn = "#" in niv or "#" in cla
    print("parametres acces base", base, niveau, classe, att, regle)

    regle.cible_base = (base, niveau, classe, att)
    return True
