# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
"""
import re
import os
import logging
from itertools import zip_longest, count
from io import StringIO
from functools import partial


# from collections import namedtuple
import pyetl.formats.format_temporaire as T


class Branch(object):
    """gestion des liens avec possibilite de creer de nouvelles sorties"""

    enchainements = {"", "sinon", "fail", "next", "gen"}

    def __init__(self):
        self.brch = {"ok": None, "sinon": None, "fail": None, "next": None, "gen": None}
        self.suivante = False

    def __repr__(self):
        return repr(self.liens_num())

    def setlink(self, lien):
        """positionne les liens"""
        self.brch.update({i: lien for i in self.brch})

    def setclink(self, lien):
        """positionne les liens s'ils ne le sont pas"""
        self.brch.update({i: lien for i in self.brch if self.brch[i] is None})

    def addsortie(self, sortie):
        """positionne iune sortie supplementaire"""
        if sortie not in self.brch:
            self.brch[sortie] = None
            self.enchainements.add(sortie)

    def liens_num(self):
        """retourne les numeros de regles """
        liens_num = {
            i: self.brch[i].numero if self.brch[i] else 99999 for i in self.brch
        }
        return liens_num

    def liens_pos(self):
        """retourne les index dans la liste de regles finale avec les inclus"""
        liens_num = {
            i: self.brch[i].index if self.brch[i] else 99999 for i in self.brch
        }
        return liens_num

    def changeliens(self, regles):
        """reassigne les liens en cas de copie d'un ensemble de regles sert pour
        le fonctionnement en mode multiprocessing"""
        liens_pos = self.liens_pos()
        brch2 = {i: regles[j] for i, j in liens_pos.items()}
        self.brch = brch2

    def setsuivante(self, regle):
        """positionne le lien vers la prochaine regle a executer"""
        if regle:
            self.suivante = regle
        else:
            self.suivante = self.brch["sinon"].suivante if self.brch["sinon"] else None


class Valdef(object):
    """classe de stockage d'un parametre"""

    def __init__(
        self,
        val,
        num,
        liste,
        dyn,
        definition,
        origine,
        texte,
        defaut,
        typedef,
        regle_ref,
    ):
        self._val = val
        self.regle_ref = regle_ref
        self.num = num
        self.liste = liste
        if liste and all(":" in i for i in liste):  # liste de type clef:valeur
            try:
                self.vdict = dict([tuple(i.split(":", 1)) for i in liste])
            except TypeError:
                print(
                    "valdef: type incompatible",
                    texte,
                    [tuple(i.split(":", 1)) for i in liste],
                )
        else:
            self.vdict = dict()
        self.dyn = dyn
        self.definition = definition
        #        self.besoin = None
        self.origine = origine  # valeur dynamique issue d'un champs de l'objet
        self.defaut = defaut
        self.texte = texte
        self.typedef = typedef
        # print("parametre", repr(self))

    def update(self, obj):
        """mets a jour les elements a partir de l'objet"""
        self.val = obj.attributs.get(self.origine, "")

    def __repr__(self):
        return self.texte + "->" + str(self.val) + "L:" + repr(self.liste)

    def getval(self, obj, defaut=None):
        if self.origine:
            return obj.attributs.get(
                self.origine, defaut if defaut is not None else self.defaut
            )
        return self.val


class Valp(Valdef):
    def getvar(self):
        if self.origine in self.regle_ref.stock_param.fonctions:
            return self.regle_ref.stock_param.fonctions[self.origine]()
        return self.regle_ref.getvar(self.origine)

    val = property(getvar)


class Vals(Valdef):
    def getstatic(self):
        return self._val

    val = property(getstatic)


class ParametresFonction(object):
    """ stockage des parametres standanrds des regles """

    MODIFFONC1 = re.compile(r"([nc]):(#?[a-zA-Z_][a-zA-Z0-9_]*)")
    MODIFFONC2 = re.compile(r"P:([a-zA-Z_][a-zA-Z0-9_]*)")
    #    st_val = namedtuple("valeur", ("val", "num", "liste", "dyn", 'definition'))

    def __init__(self, regle_ref, valeurs, definition, pnum):
        # print("creation param fonction", regle_ref, valeurs, definition)
        self.regle_ref = regle_ref
        self.valeurs = valeurs
        self.definitions = definition
        # print("definition parametres", definition)
        self.att_sortie = self._crent("sortie", out=True)
        self.def_sortie = None
        self.att_entree = self._crent("entree")
        taille = len(self.att_entree.liste or self.att_sortie.liste)
        self.val_entree = self._crent("defaut", taille=taille)
        self.cmp1 = self._crent("cmp1")
        self.cmp2 = self._crent("cmp2")
        self.specif = dict()
        self.fstore = None
        self.pattern = pnum
        self.att_ref = self.att_entree if self.att_entree.val else self.att_sortie

    def _crent(self, nom, taille=0, out=False):
        """extrait les infos de l'entite selectionnee"""
        # print("creent", nom, self.valeurs[nom].groups(), self.valeurs[nom].re)
        val = ""
        defaut = ""
        try:
            val = self.valeurs[nom].group(1)
            if val.startswith("P:") and not out:
                origine = val[2:]
                val = None
            else:
                if r"\;" in val:
                    val = val.replace(r"\;", ";")  # permet de specifier un ;
        #                val = val.replace(r'\b', 'b')
        except (IndexError, AttributeError, KeyError):
            #            print ('creent erreur', self.valeurs)
            val = ""
        try:
            defin = self.valeurs[nom].group(2).split(",")
        except (IndexError, AttributeError, KeyError):
            defin = []
        liste = []
        num = None
        dyn = False
        if isinstance(val, str):
            try:
                num = float(val)
            except ValueError:
                pass
            val2 = val
            if ":" in val and not "," in val:
                val2 = val.replace(":", ",")
            if val2:
                if val2.startswith(","):
                    val2 = val2[1:]
                liste = val2.split(",")

            if taille > len(liste):
                if liste:
                    liste.extend([liste[-1]] * (taille - len(liste)))
                else:
                    liste.extend([""] * taille)
            #        print (self.definitions)
            try:
                if self.definitions[nom].pattern == "|L":
                    liste = val.split("|") if val else []
            except (IndexError, AttributeError, KeyError):
                liste = []
            dyn = "*" in val
            origine = None
            if val.startswith("["):
                # dyn = True
                origine = val[1:-1]
                if ":" in origine:
                    origine, defaut = origine.split(":", 1)

        #        var = "P:" in val
        texte = self.valeurs[nom].string if nom in self.valeurs else ""
        typedef = self.definitions[nom].deftype if nom in self.definitions else "T"
        #        return self.st_val(val, num, liste, dyn, defin)
        return (
            Vals(
                val,
                num,
                liste,
                dyn,
                defin,
                origine,
                texte,
                defaut,
                typedef,
                self.regle_ref,
            )
            if val is not None
            else Valp(
                val,
                num,
                liste,
                dyn,
                defin,
                origine,
                texte,
                defaut,
                typedef,
                self.regle_ref,
            )
        )

    def __repr__(self):
        listev = [
            "sortie:%s" % (str(self.att_sortie)),
            "entree:%s" % (str(self.att_entree)),
            "defaut:%s" % (str(self.val_entree)),
            "cmp1:%s" % (str(self.cmp1)),
            "cmp2:%s" % (str(self.cmp2)),
        ]
        return "\t" + "\n\t".join(listev) + "\n\tidcommand: pattern" + self.pattern

    def _compact(self, mode="..."):
        return ";%s;%s;%s;%s;%s;%s;" % (
            self.att_sortie.val,
            self.val_entree.val,
            self.att_entree.val,
            mode,
            self.cmp1.val,
            self.cmp2.val,
        )

    def compilefonc(self, descripteur, variable, debug=False):
        """compile une expression de champs"""
        # print("descripteur->" + descripteur + "<-")
        if descripteur.startswith("N::") or descripteur.startswith("C::"):
            # print("detection formule")
            descripteur = descripteur[3:]
        desc1 = descripteur.replace("N:", "n:")
        desc2 = desc1.replace("C:", "c:")
        desc3 = self.MODIFFONC1.sub(r"obj.atget_\1('\2')", desc2)
        desc4 = self.MODIFFONC2.sub(r"regle.getvar('\1')", desc3)
        if "__" in desc4:
            raise SyntaxError("fonction non autorisee:" + desc4)
        if debug:
            print("fonction a evaluer", "lambda " + variable + ": " + desc4)
        retour = eval("lambda " + variable + ": " + desc4, {})
        return retour


class ParametresCondition(ParametresFonction):
    """stockage des parametres des conditions"""

    def __init__(self, regle_ref, valeurs, definition, pnum):
        # print("creation param conditions", regle_ref, valeurs, definition)
        self.regle_ref = regle_ref
        self.valeurs = valeurs
        self.definitions = definition
        self.attr = self._crent("attr")
        self.vals = self._crent("vals")
        self.specif = dict()
        self.pattern = pnum

    def __repr__(self):
        listev = ["attr:%s" % (str(self.attr)), "vals:%s" % (str(self.vals))]
        return "\n\t".join(listev) + "\n\tidcommand: pattern" + self.pattern


class Condition(object):
    """ container pour les objets de selection """

    def __init__(self, regle, attribut, valeur):
        self.regle = regle
        self.fonction = self.true
        self.ligne = attribut + ";" + valeur
        self.v_nommees = {"attr": attribut, "vals": valeur}
        self.info = dict()
        self.params = None
        self.nom = ""
        self.valide = False
        self.initval = True
        self.static = False
        self.neg = False
        self.pattern = None
        self.erreurs = None
        self.choix_fonction(attribut, valeur)

    def __repr__(self):
        return (
            "condition:"
            + (("valide:" + self.nom) if self.valide else "invalide")
            + "->"
            + repr(self.v_nommees)
        )

    @staticmethod
    def true(*_):
        """toujours vrai"""
        return True

    @staticmethod
    def false(*_):
        """toujours faux"""
        return False

    def _selpos(self, obj):
        """condition standard """
        #        print ("dans select ", self.regle.numero, self.ligne, self.fonction)
        return self.fonction(self, obj)

    def _selneg(self, obj):
        """negation"""
        #        print (" dans select ",self.ligne, obj)
        return not self.fonction(self, obj)

    def choix_fonction(self, attribut, valeur):
        """ definition d un critere de selection """
        if not (attribut or valeur):
            return None
        self.select = self._selpos
        if valeur.startswith("!"):
            self.select = self._selneg
            self.neg = True
            self.v_nommees["vals"] = valeur[1:]
        for candidat in self.regle.stock_param.sortedconds:
            # print ("test sel ", candidat.nom, candidat.priorite, candidat.patternnum,":",candidat.pattern)
            self.valide, elements, erreurs = validepattern(
                self.v_nommees, candidat.definition, self.ligne
            )
            if self.valide:
                self.params = ParametresCondition(
                    self.regle, elements, candidat.definition, candidat.patternnum
                )

                for fhelp in candidat.helper:
                    # print("appel helper", fhelp, candidat.helper)
                    fhelp(self)
                self.fonction = candidat.work
                self.nom = candidat.nom
                self.pattern = self.params.pattern
                return
        # print("================================ erreur condition:", self.regle)
        self.afficher_erreurs("erreur condition", attribut, valeur)

    def afficher_erreurs(self, message, attribut, valeur):
        """donne des indications sur les erreurs de syntaxe dans une condition"""
        log = self.regle.stock_param.logger.error
        motif = ""

        log(
            motif + "erreur interpretation condition %s %d",
            self.regle.fichier,
            self.regle.numero,
        )
        log(motif + message)
        log(motif + " ligne      : %s", self.ligne.replace("\n", ""))
        log(motif + " contexte d'execution: %s", repr(self.regle.context))
        log(
            motif + " parametres : %s",
            ";".join((attribut, valeur)),
        )

        if self.erreurs:
            log(motif + " %s", "\n".join(self.erreurs))

        raise SyntaxError("erreurs condition")


def validepattern(v_nommees, definition, ligne):
    """validation de la signature d'une fonction"""
    # print (definition)
    elements = {None: None}
    try:
        elements = {i: definition[i].match(v_nommees[i]) for i in definition}
        # print ('elements',elements)
    except KeyError:
        print("definition erronnee", ligne, definition)
    valide = None not in elements.values()
    explication = [
        i + ":" + definition[i].pattern + "<>" + v_nommees[i]
        for i in elements
        if elements[i] is None
    ]
    # print("validepattern", valide, elements, explication)
    return valide, elements, explication


class RegleTraitement(object):  # regle de mapping
    """ descripteur de traitement unitaire """

    _ido = count(1)  # compteur d'instance
    NOMS_CHAMPS = [
        "sel1",
        "val_sel1",
        "sel2",
        "val_sel2",
        "sortie",
        "defaut",
        "entree",
        "commande",
        "cmp1",
        "cmp2",
        "debug",
        "vlocs",
    ]

    def __init__(self, ligne, stock_param, fichier, numero, context=None):

        self.idregle = next(self._ido)

        self.ligne = ligne
        self.stock_param = stock_param
        self.branchements = Branch()
        self.params = None
        self.selstd = None
        self.code_classe = None
        self.valide = "inconnu"
        self.enchainement = ""
        self.ebloc = 0
        self.mode = ""
        self.source = fichier
        self.fichier = ""
        self.style = "N"
        #        self.traitement_schema = True
        self.niveau = 0
        self.declenchee = False
        self.chargeur = False  # definit si une regle cree des objets
        self.mode_chargeur = False
        self.debug = False  # modificateurs de comportement
        self.debugvalid = False
        self.champsdebug = None
        self.store = False
        self.blocksize = 0
        self.nonext = False
        self.fonc = None
        self.fstore = self.ftrue
        self.shelper = None
        # self.fonctions_schema = []
        self.numero = numero
        if context is None:
            context = stock_param.cur_context
        self.context = context.getcontext(ident="R" + str(numero))
        # self.context = context.getcontext(ident="R" + str(numero), ref=True)
        #        print ('contexte regle',self.ligne, self.context)
        self.val_tri = re.compile("")
        self.index = 0
        self.bloc = 0
        # -----------------flags de comportement-------------------
        self.action_schema = None
        self.dynschema = False
        self.final = False
        self.filter = False
        self.copy = False
        self.call = False
        self._return = False

        self.nom_fich_schema = ""
        #        self.nom_base = 'defaut'
        self.changeclasse = None
        self.changeschema = None
        self.supp_classe = False
        self.ajout_attributs = []
        self.elements = dict()
        self.f_sortie = None
        self.get_entree = self.getval_entree
        self.stockage = dict()
        self.discstore = dict()
        self.tmp_store = list()
        self.compt_stock = 0
        self.dident = ""
        self.selected = None
        self.schema_courant = None
        self.menage = False
        self.lecteurs = dict()
        self.memlimit = int(self.getvar("memlimit", 0))
        self.erreurs = []
        self.v_nommees = dict()
        self.liste_regles = []

    def __repr__(self):
        """pour l impression"""
        if self.ligne:
            return (
                (self.source if self.source else "")
                + ":"
                + str(self.index)
                + "("
                + str(self.numero)
                + "):"
                + (self.ligne[:-1] if self.ligne.endswith("\n") else self.ligne)
                + ":R->"
                + (self.params._compact(self.mode) if self.params else "noparams ")
                + str(self.idregle)
                + "("
                + repr(self.context)
                + ")"
                + repr(self.context.vlocales)
                + "brch"
                + repr(self.branchements)
            )
        return "regle vide"

    @property
    def getgen(self):
        return self.branchements.brch["gen"]

    # ------------------------------------fonctions d'initialisation---------------------------------
    def _select_fonc(self, fonc):
        """validation de la signature d'une fonction # pretest de la clef prioritaire"""
        if not fonc.clef_sec:
            return True
        definition = fonc.definition
        clef = fonc.clef_sec
        if (
            clef == "sortie" and fonc.fonctions_sortie
        ):  # on teste les sorties comme clef
            # print("test des fonctions de sortie ", fonc.nom, clef, "->", definition)
            for j in sorted(fonc.fonctions_sortie.values(), key=lambda x: x.priorite):
                if j.definition[clef].match(self.v_nommees[clef]):
                    # print("trouve f_sortie ", fonc.nom, clef, "->", definition)

                    return True
            return False
        if clef != "-1":
            return definition[clef].match(self.v_nommees[clef])
        return True

    def set_resultat(self, fonc):
        """ positionne la fonction de sortie de la regle"""
        cref = "sortie"
        elements = self.elements
        #                for j in sorted(fonc.fonctions_sortie.values(),key=lambda x:x.priorite):
        #                    print ('ordre choix ',j.work)
        for j in sorted(fonc.fonctions_sortie.values(), key=lambda x: x.priorite):
            #                print ('sortie')
            if j.definition[cref].match(self.v_nommees[cref]):
                self.fstore = j.work
                # self.action_schema = j.fonction_schema or self.action_schema
                # self.fonctions_schema.append(j.fonction_schema)
                self.shelper = j.helper
                #            if not regle.action_schema:
                #                print('erreur action', j.nom, j.fonction_schema,
                #                      fonc.nom, regle.ligne[:-1])
                elements[cref] = j.definition[cref].match(self.v_nommees[cref])
                break
        #
        if self.fstore:
            # print("fonction sortie", regle, "sortie:", j.work, self.fonctions_schema)
            return True
        self.erreurs.append("erreur sortie")
        elements[cref] = None
        return False

    def traite_helpers(self, fonc):
        """execute les fonctions auxiliaires """
        self.valide = True
        inited = False
        try:
            inited = fonc.module.init()
        except:
            print("erreur initialisation module", fonc.nom)
            pass
        if not inited:
            raise SyntaxError("module non disponible" + fonc.nom)

        for fhelp in fonc.helper:
            #         la fonction prevoit une sequence d'initialisation : on l'execute
            #        print ("execution helper",fonc.nom)
            mode_orig = self.mode
            fhelp(self)  # on prepare les elements
            #                print ('retour', regle.valide)
            if (
                self.mode != mode_orig
            ):  # la fonction helper a change la fonction a appeler
                fonc2 = self.stock_param.commandes.get(self.mode)
                if fonc2 and callable(fonc2.work):
                    self.fonc = fonc2.work
                else:
                    self.afficher_erreurs(fonc, "fonction non implementee:")
        if self.shelper:
            erreur = self.shelper(self)
            if erreur:
                print("erreur initialisation regle", self)
                self.valide = False
                return False
        if self.changeclasse:
            self.changeclasse = fonc.changeclasse
        if self.changeschema:
            self.changeschema = fonc.changeschema
        else:
            if self.action_schema:
                if (
                    self.params.att_sortie.origine
                    or "#classe" in self.params.att_sortie.liste
                    or "#groupe" in self.params.att_sortie.liste
                ):
                    self.changeclasse = fonc.changeclasse

                if (
                    self.params.att_sortie.origine
                    or "#schema" in self.params.att_sortie.liste
                ):
                    self.changeschema = fonc.changeschema
        #    if regle.params.att_sortie.val:
        # description_schema(self)  # mets en place le schema pour l'attribut de sortie
        return True

    def identifie_operation(self):
        """ identifie la fonction a appliquer et recupere les parametres """
        fonction = self.stock_param.getcommande(self.mode)
        # print ('detecte commande',regle.mode, regle.ligne, fonction)
        #        printpattern (fonction)
        #        definitions=[i.definition for i in fonction.subfonctions.values()]
        if not fonction:
            self.afficher_erreurs(fonction, "fonction inconnue")
            # raise SyntaxError ('fonction inconnue'+ regle.mode)
            return False, None

        valide = False
        fonc = None
        erreurs = []
        #    print( 'traitement fonction',fonction.nom,erreurs)
        for fonc in fonction.subfonctions:
            if fonc.style != self.style:
                continue
            if self._select_fonc(fonc):
                valide, self.elements, erreurs = validepattern(
                    self.v_nommees, fonc.definition, self.ligne
                )
                if valide:
                    break
        if not valide:
            self.afficher_erreurs(fonction, "fonction non valide")

        if callable(fonc.work):
            self.fonc = fonc.work
            if fonc.fonction_schema:
                # print("fonctions schema", self, fonc.fonction_schema)
                self.action_schema = fonc.fonction_schema
                # self.fonctions_schema.append(fonc.fonction_schema)
            if fonc.fonctions_sortie:
                valide = self.set_resultat(fonc)
                if not self.fstore:
                    self.afficher_erreurs(fonc, "fonction de sortie non valide")
            self.params = ParametresFonction(
                self, self.elements, fonc.definition, fonc.patternnum
            )
            self.valide = valide
            self.traite_helpers(fonc)
            return
        self.afficher_erreurs(fonc, "fonction non implementee:")

    def afficher_erreurs(self, fonc, message):
        """donne des indications sur les erreurs de syntaxe"""
        log = self.stock_param.logger.error
        motif = ""

        log(motif + "erreur interpretation regle %s %d", self.fichier, self.numero)
        log(motif + message)
        log(motif + " ligne      : %s", self.ligne.replace("\n", ""))
        log(motif + " contexte d'execution: %s", repr(self.context))
        log(
            motif + " parametres : %s",
            ";".join([self.v_nommees[i] for i in self.NOMS_CHAMPS]),
        )
        if fonc:
            log(motif + " autorises  : %s", fonc.pattern)

        if self.erreurs:
            log(motif + " %s", "\n".join(self.erreurs))
        if not self.mode:  # pas de mode en general un decalage
            log(motif + " %s", "regle vide")
            morceaux = self.context.SPLITTER_PV.split(self.ligne.replace("\n", ""))
            morceaux[7] = "???"
            print(motif, ";".join(morceaux))
        if self.elements:
            for i in self.elements:
                if self.elements[i] is None:
                    # print(
                    #     motif + "erreur commande>",
                    #     # fonc.definition,
                    #     self.mode,
                    #     "<",
                    #     i,
                    #     fonc.nom if fonc else "",
                    #     fonc.definition[i].pattern if fonc else "",
                    #     "<-//->",
                    #     self.v_nommees[i],
                    # )

                    log(
                        motif
                        + "   erreur parametre >"
                        + self.mode
                        + "< (%s) %s:       %s <-//-> %s",
                        fonc.nom if fonc else "",
                        i,
                        fonc.definition[i].pattern if fonc else "",
                        self.v_nommees[i],
                    )
        else:
            fonction = self.stock_param.commandes.get(self.mode)
            if fonction:
                patternlist = [
                    i.pattern for i in fonction.subfonctions if i.style == self.style
                ]
                print(motif + " patterns autorises ", patternlist)
            else:
                print("---------commande inconnue", self.mode)
        raise SyntaxError("erreurs parametres de commande")

    def ftrue(self, *_):
        """ toujours vrai  pour les expressions sans conditions"""
        return True

    def getregle(self, ligne, fichier, numero):
        """retourne une regle pour des operations particulieres"""
        return RegleTraitement(ligne, self.stock_param, fichier, numero)

    def test_static_false(self, condition):
        """ verifie si la condition est statique et realisee"""
        if not condition.valide:  # y a pas de condition
            return False
        if condition.static:
            if condition.initval:
                condition.valide = False  # c est comme si le test n existait pas
                self.valide = "selected"
                return False
            self.valide = "unselected"  # rien a faire on a fini le boulot
            return True
        return False

    def prepare_condition(self, v_nommees):
        """prepare la fonction de selection de la regle"""
        sel1 = Condition(self, self.code_classe, v_nommees["val_sel1"])
        sel2 = Condition(self, v_nommees["sel2"], v_nommees["val_sel2"])
        self.sel1 = sel1
        self.sel2 = sel2  # pour le debug
        if self.test_static_false(
            sel1
        ):  # le test est statique et devalide de fait la regle
            return
        if (
            not sel1.valide
        ):  # le sel1 a ete elimine on passe au sel2 et on le mets en premiere position
            sel1 = sel2
            if self.test_static_false(
                sel1
            ):  # le test est statique et devalide de fait la regle
                return
            if sel1.valide:  # une vraie fonction de selection
                self.selstd = sel1.select
            return
        # print("-------------conditions", self, sel1, sel2)
        if self.test_static_false(sel2):  # le test1 est valide on verifie le test2
            return  # statique et faux: ca devalide la regle
        if sel2.valide:
            self.selstd = lambda x: sel1.select(x) and sel2.select(x)  # test double
        else:
            self.selstd = sel1.select  # test simple

    def getvar(self, nom, defaut=""):
        """recupere une variable dans le contexte"""
        return self.context.getvar(nom, defaut)

    def istrue(self, nom, defaut=False):
        """recupere la valeur booleenne d une variable"""
        return self.context.istrue(nom, defaut)

    def getlocal(self, nom, defaut=""):
        return self.context.getlocal(nom, defaut)

    def getchain(self, noms, defaut=""):
        """recupere une variable avec une chaine de fallbacks"""
        return self.context.getchain(noms, defaut)

    def setvar(self, nom, valeur):
        """positionne une variable dans le contexte de reference"""
        self.context.setvar(nom, valeur)

    def setroot(self, nom, valeur):
        """positionne une variable dans le contexte base"""
        self.context.setroot(nom, valeur)

    def setlocal(self, nom, valeur):
        """positionne une variable dans le contexte local"""
        self.context.setlocal(nom, valeur)

    # =========================acces aux schemas=============================
    def getschema(self, nom):
        """recupere un schema"""
        if nom not in self.stock_param.schemas:
            # print("schema introuvable", nom, self.stock_param.schemas.keys())
            return None
        return self.stock_param.schemas.get(nom)

    # =========================acces standardises aux objets==================
    def getobj(self, ident, format_natif="interne"):
        """cree un objet"""
        if hasattr(self, "reader"):
            obj = self.reader.getobj(*ident, format_natif=format_natif)
            return obj
        return False

    def get_defaut(self, obj):
        """ retourne la valeur par defaut s'il n'y a pas de champ"""
        # print("get_defaut",self.params.val_entree.val)
        return self.params.val_entree.val

    def getval_entree(self, obj):
        """acces standadise a la valeur d'entree valeur avec defaut"""
        return obj.attributs.get(self.params.att_entree.val, self.params.val_entree.val)

    def getval_ref(self, obj):
        """acces standadise a la valeur d'entree valeur avec defaut"""
        #        print("recup att_ref ",self.params.att_ref,"valeur",
        #              obj.attributs.get(self.params.att_ref.val))
        return obj.attributs.get(self.params.att_ref.val, self.params.val_entree.val)

    def getlist_entree(self, obj):
        """acces standadise a la liste d'entree valeur avec defaut en liste"""
        return [
            obj.attributs.get(i) or j
            for i, j in zip_longest(
                self.params.att_entree.liste, self.params.val_entree.liste
            )
        ]

    def getdyn(self, obj, info):
        """recupere une valeur en indirection"""
        param = getattr(self.params, info)
        return obj.attributs.get(param.val) if param.dyn else param.val

    def getlist_ref(self, obj):
        """acces standadise a la liste d'entree valeur avec defaut en liste"""
        return [
            obj.attributs.get(i, j)
            for i, j in zip_longest(
                self.params.att_ref.liste, self.params.val_entree.liste
            )
        ]

    def setval_sortie(self, obj, valeurs):
        """stockage standardise"""
        # print(
        #     "----------stockage ",
        #     valeurs,
        #     self.params.att_sortie.val,
        #     "----",
        #     self.fstore,
        # )
        self.fstore(self.params.att_sortie, obj, valeurs)

        # print(
        #     "-----val stockee- ",
        #     self.params.att_sortie.val,
        #     "->",
        #     obj.attributs[self.params.att_sortie.val],
        # )

    def process_liste(self, obj, fonction):
        """applique une fonction a une liste d'attributs et affecte une nouvelle liste"""
        self.setval_sortie(obj, map(fonction, self.getlist_entree(obj)))

    def process_listeref(self, obj, fonction):
        """applique une fonction a une liste d'attributs"""
        self.setval_sortie(obj, map(fonction, self.getlist_ref(obj)))

    def process_val(self, obj, fonction):
        """applique une fonction a un attribut"""
        self.setval_sortie(obj, fonction(self.getval_entree(obj)))

    #    def process_list_inplace(self, obj, fonction):
    #        '''applique une fonction a une liste d'attributs'''
    ##        print ('application fonction',fonction,self.getlist_ref(obj),self.fstore )
    #        obj.attributs.update(zip(self.params.att_ref.liste,
    #                                 map(fonction, self.getlist_ref(obj))))

    def affiche_debug(self, origine=""):
        """fonction d'affichage de debug"""
        msg = " ".join(
            (
                origine,
                repr(self),
                ("bloc " + str(self.bloc) if self.bloc else ""),
                ("enchainement:" + str(self.enchainement) if self.enchainement else ""),
                " copy " if self.copy else "",
                " final " if self.final else "",
                " filter" if self.filter else "",
            )
        )
        # print(msg)
        self.stock_param.logger.info(msg)

    def setstore(self):
        """definit une regle comme stockante et ajuste les sorties"""
        self.branchements.brch["end"] = self.branchements.brch["ok"]
        self.branchements.brch["ok"] = None

    def endstore(self, nom_base, groupe, obj):
        """fonction de stockage avant ecriture finale necessiare si le schema
        doit etre determine a partir des donnees avant de les ecrire sur disque"""
        #        print ('regle:dans endstore',self.numero,nom_base,groupe, obj.schema)
        #        raise
        classe_ob = obj.ident
        if obj.virtuel:
            return
        if self.calcule_schema:
            if not obj.schema:
                nomschem = nom_base if nom_base else "defaut_auto"
                schem = self.stock_param.init_schema(nomschem)

                # schem = self.getschema(nomschem)
                # if not schem:
                #     schem = SC.Schema(nomschem)
                #     self.stock_param.schemas[nomschem] = schem
                if classe_ob not in schem.classes:
                    self.stock_param.logger.warning(
                        "schema de sortie non trouve "
                        + nomschem
                        + " "
                        + str(classe_ob)
                        + " -> creation"
                    )
                #                    print('init schema de sortie ', nomschem, classe_ob)
                schem.ajuste(obj)
                #                print (obj.schema.nom)
                if not self.output.minmajfunc:
                    obj.schema.setminmaj(self.output.writerparms.get("casse", ""))
                    self.output.minmajfunc = obj.schema.minmajfunc

            for nom_att, nature in obj.attributs_speciaux.items():
                if nature == "TG":
                    obj.schema.stocke_attribut(nom_att + "_X", "float", "", "reel")
                    obj.schema.stocke_attribut(nom_att + "_Y", "float", "", "reel")
                    obj.schema.stocke_attribut(nom_att + "_O", "float", "", "reel")

        if not self.final:
            obj = (
                obj.dupplique()
            )  # on cree une copie si on veut reutiliser l'objet original
        #            print ("endstore:copie de l'objet ",obj.ident,self.stock_param.stream)
        groupe_courant = self.stockage.get(groupe)
        #        print ('stockage objet ',obj.ido, obj.copie, obj.ident, obj.schema, freeze)
        if groupe_courant:
            stockage = groupe_courant.get(classe_ob)
            if stockage:
                stockage.append(obj)
            else:
                groupe_courant[classe_ob] = [obj]
        else:
            self.stockage[groupe] = {classe_ob: [obj]}
        self.compt_stock += 1
        #        gr = self.stockage.setdefault(groupe, dict())
        #        gr.setdefault(classe_ob, []).append(obj)
        #        if self.compt_stock%10000 == 0:
        #            print ("stok courant", self.compt_stock)
        if self.memlimit and self.compt_stock >= self.memlimit:
            print("stockage disque")
            #            raise
            self.tmpwrite(
                groupe,
                self.output.writerparms["tmpgeomwriter"],
                self.output.writerparms["tmp_geom"],
            )
        obj.stored = True

    def tmpwrite(self, groupe, geomwriter, nomgeom):
        """ stockage intermediaire sur disque pour limiter la consommation memoire"""
        tmpfile = os.path.join(
            self.getvar("tmpdir"),
            "tmp_"
            + self.params.cmp1.val
            + "_"
            + self.params.cmp2.val
            + "_"
            + groupe.replace("/", "_"),
        )
        os.makedirs(self.getvar("tmpdir"), exist_ok=True)
        #        if self.stock_param.debug:
        print("stockage intermediaire ", tmpfile, groupe, self.compt_stock)

        mode = "w"
        if groupe in self.discstore:
            mode = "a"
        else:
            self.discstore[groupe] = tmpfile
        T.ecrire_objets(tmpfile, mode, self.stockage[groupe], geomwriter, nomgeom)

        self.stockage[groupe] = dict()
        self.compt_stock = 0

    def recupobjets(self, groupe):
        """recuperation des objets du stockage intermediaire"""
        nb_recup = 0
        if groupe in self.discstore:  # les objets sont sur disque
            if self.stock_param.debug:
                print("regles : recupobjets ouverture", self.discstore[groupe])
            for obj in T.lire_objets(self.discstore[groupe], self.stock_param):
                schem = obj.attributs.get("#schema")
                if schem:
                    obj.schema = self.stock_param.schemas[schem].get_classe(obj.ident)
                    nb_recup += 1
                if obj.schema is None:
                    print("recup: objet sans schema", obj.ido, obj.attributs)
                yield obj

            if self.stock_param.debug:
                print("nombre d'objets relus :", nb_recup)
            os.remove(self.discstore[groupe])  # on fait le menage
            del self.discstore[groupe]
        #        print ('recupobjets',self.stockage[groupe].keys())
        #        print(self.stockage[groupe])

        for classe in self.stockage[groupe]:
            liste = self.stockage[groupe][classe]
            for obj in liste:
                if obj.schema is None:
                    print(
                        "recupliste: objet sans schema", obj.ido, obj.ident, obj.virtuel
                    )
                    continue
                #                print ('recup obj',obj.ido,obj.copie,obj.ident,'->',obj.schema,obj.virtuel)
                yield obj
        del self.stockage[groupe]

    def add_tmp_store(self, obj):
        """stockage temporaire au niveau de la regle pour les regles necessitant
        l'ensemble des donnees pour faire le traitement"""
        # TODO prevoir un stockage disque si la conso memeoire est trop forte
        self.tmp_store.append(obj)  # on stocke les objet pour l'execution de la regle

    def change_schema_nom(self, obj, nom_schema):
        """change le schema d'une classe et le cree si besoin"""
        ident = obj.ident
        # groupe, classe = ident
        schema2 = self.stock_param.init_schema(
            nom_schema,
            fich=self.nom_fich_schema,
            origine="S",
            modele=obj.schema.schema if obj.schema else None,
        )

        schema_classe = schema2.get_classe(
            ident, cree=True, modele=obj.schema, filiation=True
        )
        if not schema_classe:
            print("erreur changement classe", ident, obj.schema)
        obj.setschema(schema_classe)

    # def execute_actions_schema(self, obj):
    #     if obj.schema:
    #         if self.dynschema or obj.schema.amodifier():
    #             for tache in self.fonctions_schema:
    #                 tache(self, obj)

    def runscope(self):
        """determine si une regle peut tourner"""
        pdef = self.getvar("process")
        #        print('runscope', pdef, self.stock_param.parent is None)
        if not pdef:
            return True
        if pdef == "all":
            return True
        if pdef == "worker":
            return self.stock_param.worker
        if pdef == "master":
            return not self.stock_param.worker
        if pdef == "main":
            return self.stock_param.parent is None and not self.stock_param.worker
        if pdef == "child":
            return self.stock_param.parent is not None
        return True

    def get_max_workers(self):
        """ retourne le nombre de threads paralleles demandes"""
        try:
            multi = self.getvar("multi", "1")
            if ":" in multi:
                tmp = multi.split(":")
                process = int(tmp[0])
                ext = int(tmp[1])
            else:
                process = int(multi)
                ext = -1
        except ValueError:
            process, ext = 1, 1
        nprocs = os.cpu_count()
        if self.stock_param.worker:  # si on est deja en parallele on ne multiplie plus
            process = 1
        if nprocs is None:
            nprocs = 1
        if process < 0:
            process = -nprocs * process
        if ext < 0:
            ext = -process * ext
        return process, ext

    def print(self, *args, **kwargs):
        """fonction d impression avec gestion des retours web"""
        if self.stock_param.mode.startswith("web"):
            sortie = self.stock_param.webstore.setdefault("#print", [])
            buffer = StringIO()
            if args and len(args) == 1 and isinstance(args[0], list):
                sortie.extend(args[0])
            else:
                print(*args, **kwargs, file=buffer)
                sortie.extend(buffer.getvalue().split("\n"))
            # print("sortie webstore")
            # print(*args, **kwargs)
            # raise
        else:
            print(*args, **kwargs)

    def actions_schema(self, obj):
        """gere les actions sur les schemas"""
        if obj.schema is not None:
            if self.action_schema:
                self.action_schema(self, obj)
            if self.changeclasse:
                self.changeclasse(self, obj)
        if self.changeschema:
            self.changeschema(self, obj)

    def traite_push(self):
        """traite les objets en mode push (coroutines)"""
        suite = 1
        while suite:
            obj = yield
            if obj:
                if self.selstd is None or self.selstd(obj):
                    if self.copy:
                        self.branchements.brch["copy"].send(obj.dupplique())
                    obj.redirect = self.branchements.brch["ok"]
                    result = self.fonc(self, obj)
                    if result:
                        self.actions_schema(obj)
                    if obj.redirect and obj.redirect in self.branchements.brch:
                        self.branchements.brch[obj.redirect].send(obj)
            else:
                suite = False
