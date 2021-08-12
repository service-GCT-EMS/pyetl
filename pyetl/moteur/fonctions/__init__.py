# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965

gestionaire de fonctions de traitements
les fonctions sont enregistrees en les mettant dans des fichiers python qui
commencent par traitement

"""


# import inspect
import os
import re
import importlib
from itertools import chain


# NOMS_MODULES = ['.traitement_alpha', '.traitement_geom', '.traitement_divers',
#                '.traitement_schema', '.traitement_db']
#
printtime = False
if printtime:
    import time

    t1 = time.time()


class DefinitionAttribut(object):
    """decrit un attribut de fonction
    clef:(regex,type,groupe)"""

    # non capturing groupe : (?: .....)
    # variable : #?[a-zA-Z_][a-zA-Z0-9_]*
    asdef = r"#?[a-zA-Z_][a-zA-Z0-9_]*"  # description simple de nom de champs
    #    asdef = r'(#?[a-zA-Z_\-][a-zA-Z0-9_\-]*)' # description simple de nom de champs
    #    aldef = r'(?:'+asdef+')|&'
    adef = r"(" + asdef + r")(?:\((.+)\))?"  # description champs avec details
    vdef = r"\[(" + asdef + r")\]"  # contenu champs
    ndef = r"-?[0-9]*.?[0-9]*|[0-9]+"
    # definition des expressions utilisables pour la description d un champs
    # sous la forme :  clef : apparair dans le parrern de la fonction
    #                   tuple contenant l'expression, la categorie et le groupe (fonctions de sortie)
    #                   expresion : regex standard avec des captures pour les elements signifiants
    #                   categorie : A attribut / C chaine quelquonque / N numerique
    #                                / P variable moteur / H hstore
    #                   groupe : S simple / M multiple / H hstore / D dynamique / P variable moteur
    relist = {
        "A": (r"^" + adef + r"$", "A", "S", "attribut"),  # attribut
        # "AH": (r"^" + adef + r"$", "A:H", "S"),  # variable hstore
        "AE": (r"^" + adef + r"$", "A:E", "S", "attribut entier"),  # variable entiere
        "AN": (
            r"^" + adef + r"$",
            "A:F",
            "S",
            "attribut numerique",
        ),  # variable numerique
        "AD": (r"^" + adef + r"$", "A:D", "S", "attribut date"),  # variable date
        "AV": (r"^$", "A", "S"),  # vide pour des definitions ou sortie=entree
        "+A": (r"^\+" + adef + r"$", "A", "S", "attribut"),
        "A+": (r"^" + adef + r"\+$", "A", "S", "attribut"),
        "A*": (r"^" + adef + r"\*$", "A", "D", "attribut"),
        "*A": (r"^\*" + adef + r"$", "A", "D", "attribut"),
        "H:A": (r"^H:(" + asdef + r")$", "A:H", "H", "attribut"),
        "+H:A": (r"^\+H:(" + asdef + r")$", "A:H", "H", "attribut"),
        "*": (r"^\*$", "C", "D", "libre"),
        "[A]": (r"^" + vdef + "$", "A", "S", "indirect"),
        "+[A]": (r"^\+" + vdef + "$", "A", "S", "indirect"),
        "[A]+": (r"^" + vdef + r"\+$", "A", "S", "indirect"),
        "|L": (r"^(" + asdef + r"(?:\|" + asdef + r")*)$", "S", "S", "liste"),  # liste
        "L": (
            r"^(" + asdef + r"(?:[:,]" + asdef + r")*|\*)$",
            "L",
            "M",
            "liste",
        ),  # liste
        "LV": (r"^$", "L", "M", "liste"),  # liste avec defauts
        "L2": (r"^(" + asdef + r"(?:\|" + asdef + r")*|\*)$", "L", "M", "liste"),
        "LC": (r"^(.+(?:,.*)*)$", "C", "", "liste"),  # liste de valeurs
        "T:": (r"^T:([A-Z]+)$", "L", "", "type"),
        "+L": (r"^\+(" + asdef + r"(?:," + asdef + r")*)$", "L", "M", "liste"),  # liste
        "L+": (r"^(" + asdef + r"(?:," + asdef + r")*)\+$", "L", "M", "liste"),  # liste
        "P": (r"^[Pp]:(" + asdef + r")$", "P", "P", "parametre"),
        "N:N": (r"^(" + ndef + r"(?::" + ndef + r")?)$", "N", "", "numerique"),
        "LN": (r"^(" + ndef + r"(?:,(" + ndef + r"))*)$", "N", "", "liste numerique"),
        "N": (r"^([" + ndef + r")$", "N", "", "numerique"),
        "NC:": (r"^(.*(:?(:?N:|C:) ?(" + asdef + r").*)$)", "S", "", "expression"),
        "NC2:": (r"^(.*(:?(:?N:|C:) .*).*$)", "S", "", "expression"),
        "re": (r"(.+)", "C", "", "expression reguliere"),
        "=:": (r"^=:(.+)", "C", "", "expression"),
        "re:re": (r"^re:(.+)$", "C", "", "expression"),
        "C": (r"(.+)", "C", "", "texte"),
        "F": (r"F:(.+)", "C", "", "F:nom de fichier"),
        "C:C": (r"^C:(.*)$", "C", "", "texte double"),
        "C[]": (r"^(.*\[[CDF]\].*)$", "C", "", "nom de fichier"),
        "#C": (r"(#.+)", "C", "", "texte"),
        "?": (r"(.*)", "C", "", "texte"),
        ".": (r"(.+)", "C", "", "texte"),
        "": (r"(^$)", "", "", "vide"),
        "in:fich": (r"^in:([^#][^(]+)$", "C", "", "en fichier"),
        "in:fich(re)": (r"^in:([^#].+?)\((.*)\)$", "C", "", "en fichier"),
        "in:mem": (r"^in:(#[a-zA-Z][a-zA-Z0-9_]*)$", "C", "", "en memoire"),
        "in:list": (r"^in:\{?(.+(?:,.*)*)\}?$", "C", "", "liste"),
        "in:list(re)": (r"^in:\{?(.+(?:,.*)*)\}?\((.*)\)$", "C", "", "liste"),
        "haskey:A": (r"^haskey:(" + asdef + ")$", "A", "", "clef hstore"),
        "schema:A": (r"^schema:(" + asdef + ")$", "A", "", "schema"),
        "schema:A:": (r"^schema:(" + asdef + ")=$", "A", "", "schema"),
        "schema:T:": (
            r"^schema:T:([A-Z]+)",
            "A",
            "",
            "schema",
        ),  # selection par type d'attribut
        "hasval:C": (r"^hasval:(.*)$", "A", "", "valeur hstore"),
        "A.C": (r"^(" + asdef + ")\.(.*)$", "A", "", "sous element"),
        "A:C": (r"^(" + asdef + "):(.*)$", "A", "", "element hstore"),
        "M": (r"", "G", "M", "liste"),  # multiple (groupes de sortie)
        "S": (r"", "G", "S", "attribut"),  # simple
        "D": (r"", "G", "D", "attributs dynamiques"),  # dynamique
        "H": (r"", "G", "H", "hstore"),  # hstore
    }

    grouplist = {
        "M": ("sortie", "G", "M"),  # multiple (groupes de sortie)
        "S": ("sortie", "G", "S"),  # simple
        "D": ("sortie", "G", "D"),  # dynamique
        "H": ("sortie", "G", "H"),  # hstore
    }

    def __init__(self, ident, pattern):
        self.ident = ident
        self.pattern = pattern
        self.groupe = ""
        self.deftype = "T"
        vide = pattern == ""
        self.expression = ""
        self.commonlist = 0
        self.obligatoire = vide or not "?" in pattern
        if "~?" in pattern:
            self.commonlist = 1
            pattern = pattern.replace("~?", "")
        if pattern != "?":
            pattern = pattern.replace("?", "")
        if pattern == "":
            self.priorite = 9
            self.nature = "vide"
        elif "=" in pattern and not "=:" in pattern:
            self.nature = "fixe"
            self.priorite = 1
            self.expression = "^(" + pattern.replace("=", "") + ")$"
        elif pattern.startswith("("):
            self.nature = "A"
            tmp = re.match(r"^\(([a-z_:]+)\)(.*)", pattern)
            if tmp:
                compl = (
                    (self.relist[tmp.group(2)][0][1:])
                    if tmp.group(2) in self.relist
                    else ""
                )
                self.expression = "^" + tmp.group(1) + compl
                self.groupe = ""
                # print (" detecte expression",compl, tmp.groups(),self.expression)
                self.priorite = 2
        elif pattern in self.relist:
            self.priorite = 4
            self.expression, self.nature, self.groupe, self.aide = self.relist[pattern]
            if ":" in self.nature:
                self.nature, self.deftype = self.nature.split(":", 1)
            if self.groupe:
                self.priorite = 6
            if self.groupe == "M":
                self.priorite = 7
        else:
            print("detection pattern inconnu", ident, pattern)
            self.nature = "erreur"
            self.priorite = 999
        try:
            self.regex = re.compile(self.expression)
        except re.error as err:
            print("erreur expression reguliere ", ident, pattern, self.expression)
            print("nature ", err)

        if not self.obligatoire:
            self.priorite += 1

    #        self.helper = None

    def match(self, texte):
        """ determine si un texte est compatible avec la definition"""
        if texte:
            if self.pattern != "":
                return self.regex.match(texte)
            return None
        if self.obligatoire and self.pattern != "":
            return None
        return re.match("", "")

    def __repr__(self):
        return (
            "definition_attribut "
            + self.ident
            + "->"
            + self.pattern
            + "||"
            + self.expression
            + "("
            + self.deftype
            + ")\n"
        )


class ModuleInfo(object):
    """gere l, initialisation d un module et son aide"""

    def __init__(self, nom, fonction):
        self.nom_module = nom
        self.initable = callable(fonction)
        self.disponible = not self.initable
        self.fonction = fonction
        self.commandes = set()
        self.selecteurs = set()
        self.aux = set()
        self.help = ""
        self.titre = nom.split("_")[-1]

    def init(self):
        if self.disponible:
            return True
        if self.initable:
            self.disponible = self.fonction()


class FonctionTraitement(object):
    """ description d une fonction de traitment """

    def __init__(self, nom, fonction, description, definition):
        self.nom = nom
        self.module = ModuleInfo(nom, None)
        self.subfonctions = []
        self.fonctions_sortie = dict()
        self.description = description
        self.groupe_sortie = None
        pat = description.get("#pattern")
        if not pat:
            print("erreur definition fonction", nom)
            pat = ["", ""]
        self.pattern = pat[0]
        self.patternnum = description["pn"]
        self.work = fonction
        self.helper = []
        self.shelper = None
        self.definition = definition  # definition_champs
        # self.definition = None  # definition_champs
        self.fonction_schema = None
        self.prepare = description.get("#helper", "")
        self.priorite = 99
        self.style = "N"
        # gestion des clefs secondaires :
        self.clef_sec = ""
        self.subpatterns = set()

    #        if len(self.pattern.split(";")) > 1:
    #            self.clef_sec = pat[1] if len(pat) > 1 else ""
    #            if self.clef_sec and self.clef_sec not in self.definition:
    #                print("erreur clef fonction ", self.nom, ">"+self.clef_sec+"<", pat)

    def subfonc(
        self,
        nom,
        fonction,
        description,
        definition,
        groupe_sortie,
        clef_sec,
        style,
        module,
    ):
        """ sous fonction : fait partie du meme groupe mais accepte des attributs differents"""
        # self.definition = None
        pnum = description["pn"]
        # if not "#aide_spec" + pnum in description:
        #     description["#aide_spec"] = description.get("#aide")
        tsubfonc = FonctionTraitement(nom, fonction, description, definition)
        tsubfonc.groupe_sortie = groupe_sortie
        tsubfonc.style = style
        tsubfonc.patternnum = pnum
        tsubfonc.module = module
        priorite = 99
        if clef_sec:
            priorite = tsubfonc.definition[clef_sec].priorite
            #            print("enregistrement",nom,clef_sec,priorite)
            tsubfonc.clef_sec = clef_sec
        pattern = tsubfonc.pattern
        if pattern:
            if pattern not in self.subpatterns:
                self.subfonctions.append(tsubfonc)
                tsubfonc.priorite = priorite
                self.subpatterns.add(pattern)
                # print("pattern nouveau", pattern, nom, self.nom)

            else:
                print("pattern existant", pattern)
        else:
            print("subfunction incompatible", description)

    def __repr__(self):
        return (
            "fonction_traitement "
            + self.module.nom_module
            + ":"
            + self.nom
            + ":"
            + repr(self.definition)
            + repr(self.work)
        )


def interprete_doc(listedoc):
    """decompose la docstring pour extraire les exemples"""
    description_fonction = dict()
    lastel = ""
    for i in listedoc:
        ligne = i.strip()
        if ligne.startswith("#"):
            elements = ligne.split("||")
            description_fonction[elements[0]] = elements[1:]
            lastel = elements[0]
        if ligne.startswith("+") or ligne.startswith("||"):
            elements = ligne.split("||")
            description_fonction[lastel].extend(elements[1:])

    #    print ("description retenue",description_fonction,listedoc)
    return description_fonction


def controle_pattern(pattern, noms):
    """validation"""
    definition_champs = {
        nom: DefinitionAttribut(nom, pat)
        for nom, pat in zip(noms, pattern.split(";"))
        if nom != "commande"
    }
    if [
        print(i.ident, "c: pattern inconnu", i.pattern)
        for i in definition_champs.values()
        if i.nature == "erreur"
    ]:
        return False
    # if "xmlextract" in pattern:
    #     print("controle:", pattern, "\n", definition_champs)
    return definition_champs


def reg_fonction(stockage, info_module, nom, fonction, description_fonction):
    """stockage d une description de fonction standard"""
    for i in list(description_fonction.keys()):
        # on passe tout ce qu'on a defini pour la fonction
        description = dict(description_fonction)
        if "#pattern" in i:
            style = "C" if "C" in i else "N"
            description["#pattern"] = description_fonction[i]
            description["pn"] = i.replace("#pattern", "")
            #                        print ('enregistrement',nom[2:],desc["#pattern"])

            descr = description.get("#pattern", [""])
            pattern = descr[0]
            clef_sec = descr[1] if len(descr) > 1 else ""
            #    print ('controle:',pattern)

            noms = ("sortie", "defaut", "entree", "commande", "cmp1", "cmp2")
            definition_champs = controle_pattern(pattern, noms)
            if not definition_champs:
                continue
            #                print ('lecure',nom,pattern,description)
            clef = pattern.split(";")[3] if pattern else None
            info_module.commandes.add(clef)
            if clef is None:
                print("fonction incompatible", nom)
            if clef_sec and clef_sec not in definition_champs:
                print("erreur clef fonction ", nom, ">" + clef_sec + "<", pattern)
                continue

            else:
                if clef not in stockage:  # la clef existe
                    fct = FonctionTraitement(
                        nom, fonction, description, definition_champs
                    )
                    fct.module = info_module
                    fct.style = style
                    stockage[clef] = fct
                #        print ('definitions',definition)
                groupe_sortie = definition_champs["sortie"].groupe
                stockage[clef].subfonc(
                    nom,
                    fonction,
                    description,
                    definition_champs,
                    groupe_sortie,
                    clef_sec,
                    style,
                    info_module,
                )
                # if clef == "xmlextract":
                #     print(
                #         "enregistrement",
                #         clef,
                #         clef_sec,
                #         groupe_sortie,
                #         definition_champs,
                #         pattern,
                #         stockage[clef].subfonctions,
                #     )


def reg_stockage(store, info_module, nom, fonction, description):
    """ enregistre les fonctions de stockage """
    pattern = description.get("#pattern")
    description["pn"] = "0"

    cref = "sortie"
    if not pattern:
        print("fonction stockage incompatible", nom)
        return
    def_sortie = DefinitionAttribut(cref, pattern[0])
    sdef = {cref: def_sortie}
    priorite = def_sortie.priorite
    if len(pattern) > 1:
        def_sortie.groupe = pattern[1]
    if sdef[cref].nature == "erreur":
        print("fonction stockage incompatible", nom)
    else:
        fct = FonctionTraitement(pattern[0], fonction, description, sdef)
        fct.priorite = priorite
        fct.module = info_module
        #            print ('stockage fonction' ,fct.work,priorite)
        store[pattern[0]] = fct
        info_module.aux.add(pattern[0])


def reg_select(fonctions, info_module, nom, fonction, description_fonction):
    """stockage d une description de fonction de selection"""
    for i in list(description_fonction.keys()):
        # on passe tout ce qu'on a defini pour la fonction
        description = dict(description_fonction)
        if "#pattern" in i:
            description["#pattern"] = description_fonction[i]
            description["pn"] = i.replace("#pattern", "")
            #                        print ('enregistrement',nom[2:],desc["#pattern"])
            descr = description.get("#pattern", [""])
            pattern = descr[0]
            pri = descr[1]
            if pri:
                priorite = int(pri)
            else:
                priorite = 99
            noms = ("attr", "vals")
            definition_champs = controle_pattern(pattern, noms)
            if not definition_champs:
                continue
            # print("lecture selecteur", nom, pattern, description)
            clef = pattern if pattern else None
            if clef is None:
                print("fonction incompatible", nom)
            else:
                fct = FonctionTraitement(nom, fonction, description, definition_champs)
                fct.module = info_module
                fct.priorite = priorite
                fonctions[clef] = fct
                info_module.selecteurs.add(clef)


def regwarnings(module, nom, store, storetype):
    """ emets des warnings si on ecrase une fonction"""
    if nom in store:
        print(
            "!!!!!!!!!!!attention la fonction ",
            module,
            nom,
            "\n a deja ete enregistree dans",
            storetype,
            store[nom],
        )


def reghelpers(module, nom, fonction, stockage, storetype):
    """enregistre les helpers"""
    regwarnings(module, nom, stockage, storetype)
    stockage[nom] = fonction


def register(nom_module, module, store, prefixes, simple_prefix):
    """ enregistre toutes les fonctions du module """
    #    for nom, fonction in inspect.getmembers(module, inspect.isfunction):
    #        if nom[:2] == 'f_':
    initer = getattr(module, "_initer") if "_initer" in dir(module) else None
    infomodule = ModuleInfo(nom_module, initer)
    moduledoc = module.__doc__.split("\n")
    for i in moduledoc:
        if i.startswith("#titre"):
            infomodule.titre = i.split("||")[-1]

    for nom in dir(module):
        fonction = getattr(module, nom)
        #        print ('traitement ',module.__name__, nom)
        if not callable(fonction):  # on prends toutes les fonctions
            continue
        pref = nom.split("_")[0]
        if pref not in prefixes:  # autre fonction
            continue
        if not fonction.__doc__:  # sans docstring on rale
            print("erreur fonction ", module.__name__, nom)
            continue
        nom_fonction = nom.replace(pref + "_", "", 1)
        listedoc = fonction.__doc__.split("\n")
        description_fonction = interprete_doc(
            listedoc
        )  # on decoupe la doc sous forme de listes
        stockage = store[pref]
        if pref in simple_prefix:
            reghelpers(
                nom_module, nom_fonction, fonction, stockage, simple_prefix[pref]
            )

        if pref == "f":  # c'est une fonction de traitement
            #            print ('fonction ',module.__name__, nom)
            #                regwarnings(nom_module, nom[2:], COMMANDES, 'fonctions de traitement')
            regwarnings(nom_module, nom_fonction, stockage, "traitement")
            reg_fonction(
                stockage, infomodule, nom_fonction, fonction, description_fonction
            )

        elif pref == "s":  # c'est une fonction de stockage
            regwarnings(nom_module, nom_fonction, stockage, "stockage")
            reg_stockage(
                stockage, infomodule, nom_fonction, fonction, description_fonction
            )

        elif pref == "sel":  # c'est une fonction de selection
            regwarnings(nom_module, nom_fonction, stockage, "selecteur")
            reg_select(
                stockage, infomodule, nom_fonction, fonction, description_fonction
            )
    return infomodule


def get_fonction(nom, store, clef):
    """recupere la fonction de preparation associee a une fonction d entree"""
    fonctions = store[clef]
    if nom and nom not in fonctions:
        print("erreur definition de fonction helper", nom, sorted(fonctions.keys()))
        return None
    #        print ('recup fonction schema ', nom, fschema.get(nom))
    return fonctions.get(nom)


def add_helper(sbf, nom, store, clef):
    """ ajoute un helper s il n est pas deja la"""
    if nom in store[clef]:
        helper = get_fonction(nom, store, clef)
        if helper not in sbf.helper:
            sbf.helper.append(helper)


def set_helper(sbf, store, clef):
    """complete la fonction acec les sorties et les assitants"""
    add_helper(sbf, sbf.nom, store, clef)
    #    else:
    #        print("non trouve ",sbf.nom)
    #    if sbf.description.get("#helper"):
    if sbf.prepare:
        for i in sbf.prepare:
            add_helper(sbf, i, store, clef)


def complete_fonction(sbf, store):
    """complete la fonction acec les sorties et les assitants"""
    stockage = store["s"]
    naturestock = sbf.definition["sortie"].nature
    groupestock = sbf.definition["sortie"].groupe
    if naturestock == "G":  # c'est une definition de groupe
        grouperef = sbf.definition["sortie"].groupe
        sbf.fonctions_sortie = {
            k: stockage[k]
            for k in stockage
            if stockage[k].definition["sortie"].groupe == grouperef
        }
    else:
        if naturestock in stockage:
            sbf.fonctions_sortie = {naturestock: stockage[naturestock]}

    # print(
    #     "completement fonction",
    #     sbf.nom,
    #     "\t\t",
    #     naturestock,
    #     "\t",
    #     groupestock,
    #     sbf.fonctions_sortie.keys(),
    # )

    for i in sbf.fonctions_sortie.values():
        #            print ('fonction schema ',i.nom, i.description.get('#schema'))
        i.fonction_schema = get_fonction(
            i.description.get("#schema", [""])[0], store, "fschema"
        )
        i.helper = get_fonction(i.description.get("#shelper", [""])[0], store, "sh")
    #        print ("detecte groupe",grouperef,sbf.nom,len(sbf.fonctions_sortie))

    set_helper(sbf, store, "h")

    if sbf.description.get("#shelper"):
        sbf.shelper = get_fonction(
            sbf.description.get("#shelper", [""])[0], store, "sh"
        )

    sbf.changeclasse = get_fonction("change_classe", store, "fschema")
    sbf.changeschema = get_fonction("change_schema", store, "fschema")

    #    print ('fonction schema ',sbf.nom, sbf.description.get('#schema'))
    sbf.fonction_schema = get_fonction(
        sbf.description.get("#schema", [""])[0], store, "fschema"
    )


def moduleloader(modulename):
    """charge un module"""
    if printtime:
        t2 = time.time()
    try:
        imported = importlib.import_module(modulename, package=__package__)
    except ImportError as err:
        print("module ", modulename, "non disponible:", err)
        return None
    if printtime:
        print("     ", modulename, time.time() - t2)
    return imported


def loadmodules(module=None, force=False):
    """charge les modules et enregistre les fonctions"""
    global COMMANDES, SELECTEURS, MODULES, store, prefixes
    if module in MODULES:
        return  # on a deja fait le job
    modules = dict()
    commanddir = os.path.dirname(__file__)
    if force:
        for i in prefixes:
            store[i] = dict()
    if module is None:
        cc = os.path.join(commanddir, "cache_commandes.csv")
        if os.path.isfile(cc) and not force:
            COMMANDES = dict((i[:-1].split(";") for i in open(cc, "r")))
            loadmodules(module=".traitement_aux")
            loadmodules(module=".traitement_selecteurs")
            return
        for fich_module in os.listdir(commanddir):
            if fich_module.startswith("traitement"):
                module = "." + os.path.splitext(fich_module)[0]
                imported = moduleloader(module)
                if imported:
                    modules[module] = moduleloader(module)
    else:
        # print("loadmodules", module, MODULES)
        imported = moduleloader(module)
        if imported:
            modules[module] = moduleloader(module)

    simple_prefix = {
        "h": "helper fonction",
        "sh": "helper stockage",
        "selh": "helper selecteur",
        "fschema": "schemas",
    }

    for nom in modules:
        infomodule = register(nom, modules[nom], store, prefixes, simple_prefix)
        MODULES[nom] = infomodule

    COMMANDES.update(store["f"])
    SELECTEURS.update(store["sel"])
    #    print(" selecteurs lus ",selecteurs.keys())
    for i in sorted(COMMANDES):
        fct = COMMANDES[i]
        if isinstance(fct, str):
            continue
        # complete_fonction(fct, store)
        for sbf in fct.subfonctions:
            complete_fonction(sbf, store)
        fct.subfonctions = sorted(fct.subfonctions, key=lambda i: i.priorite)

    for i in SELECTEURS:
        sel = SELECTEURS[i]
        set_helper(sel, store, "selh")
    #        print (" enregistrement selecteurs",sel.nom,sel.helper)

    return


COMMANDES = dict()
SELECTEURS = dict()
MODULES = dict()
store = dict()
prefixes = {"f", "s", "sel", "selh", "fschema", "h", "sh"}
for i in prefixes:
    store[i] = dict()

loadmodules()
