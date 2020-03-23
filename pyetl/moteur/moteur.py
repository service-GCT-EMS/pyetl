# -*- coding: utf-8 -*-
"""moteur de traitement principal : gere l'enchainement des regles """
import logging
import re
import typing as T
from pyetl.formats.interne.objet import Objet  # objets et outils de gestiion
from .fonctions.outils import printexception

# import pyetl.schema.schema_io as SC
# import pyetl.schema.fonctions_schema as FSC

LOGGER = logging.getLogger("pyetl")


class Moteur(object):
    """gestionnaire de traitements """

    def __init__(self, mapper):
        self.regles = ()
        self.mapper = mapper
        self.debug = 0
        self.ident_courant = ""
        self.regle_debut = 0
        self.dupcnt = 0
        self.ncnt = 0
        self.suppcnt = 0

    @property
    def regle_sortir(self):
        """ retourne la regle finale"""
        return self.regles[-1]

    def setregles(self, regles, debug=0):
        self.regles = regles
        self.debug = debug
        if self.debug:
            self.debug_moteur()

    def debug_moteur(self):
        print("moteur: mode debug")
        for i in self.regles:
            print(i)

    def traitement_virtuel(self, unique=0):
        """ cree un objet virtuel et le traite pour toutes les classes non utilisees """

        #        if self.debug != 0:
        #        print("moteur: traitement virtuel", unique)
        LOGGER.info("traitement virtuel" + str(unique))
        #        for i in self.regles:
        #            print (i.chargeur, i)
        if unique:  # on lance un virtuel unique pour les traitements sans entree
            # on lance un virtuel unique puis on verifie toutes les regles de chargement
            self.traite_regles_chargement()
        else:
            for sch in list(self.mapper.schemas.values()):
                # print("traitement virtuel: schema a traiter", sch.nom, sch.origine)
                if sch.origine in "LB" and not sch.nom.startswith("#"):
                    print(
                        "moteur: traitement schema",
                        sch.nom,
                        sch.origine,
                        len(sch.classes),
                    )
                    LOGGER.info("traitement schema" + sch.nom + " " + sch.origine)

                    # (on ne traite que les schemas d'entree')
                    force_virtuel = self.mapper.getvar("force_virtuel") == "1"
                    for schemaclasse in list(sch.classes.values()):
                        # print(
                        #     "traitement virtuel", schemaclasse.nom, schemaclasse.utilise
                        # )
                        if schemaclasse.utilise and not force_virtuel:
                            #                            print ('traitement virtuel classe ignoree',schemaclasse.identclasse)
                            continue
                        #                        print('traitement objet virtuel ', schemaclasse.identclasse)
                        groupe, classe = schemaclasse.identclasse
                        obj = Objet(
                            groupe, classe, conversion="virtuel", schema=schemaclasse
                        )
                        obj.attributs["#categorie"] = "traitement_virtuel"
                        #                        obj = Objet(groupe, classe)
                        #                        obj.virtuel = True
                        #                        obj.setschema(schemaclasse)
                        #                        obj.initattr()
                        obj.attributs["#type_geom"] = schemaclasse.info["type_geom"]
                        # print("tv:traitement obj", obj)
                        self.traite_objet(obj, self.regles[0])

    def traite_regles_chargement(self):
        """ declenche les regles de chargement pour les traitements sans entree"""
        #        if self.debug:
        #        print('moteur: regles de chargement pour un traitement sans entree', self.regles[0].mode)
        self.regles[0].chargeur = True  # on force la premiere
        #        if self.regles[0].mode == "start": #on prends la main dans le script
        #            self.regles[0].fonc(self.regles[0], None)
        #            return
        for i in self.regles:
            #            print ('-------------------------------traite_charge ', i.declenchee ,i.chargeur,i )
            if not i.declenchee and i.chargeur:
                if i.mode == "start":  # on prends la main dans le script
                    i.fonc(i, None)
                obj = Objet(
                    "_declencheur",
                    "_chargement",
                    format_natif="interne",
                    conversion="virtuel",
                )
                i.mode_chargeur = True
                self.traite_objet(obj, i)
                i.mode_chargeur = False

    def traite_objet(self, obj, regle):
        """traitement basique toutes les regles sont testees """
        last = None
        while regle:
            last = regle
            regle.declenchee = True
            self.ncnt += 1
            try:
                if regle.selstd is None or regle.selstd(obj):
                    #                    print ('moteur:select', regle.numero, obj.ident, regle.fonc)
                    if regle.copy:
                        #                        print ('moteur: copie', regle.numero, regle.branchements.brch["copy"],
                        #                               regle.branchements.brch["fail"])
                        self.traite_objet(
                            obj.dupplique(), regle.branchements.brch["copy"]
                        )
                        # on envoie une copie dans le circuit qui ne passe pas la regle
                        if not obj.virtuel:
                            self.dupcnt += 1
                        # print "apres copie ", obj.schema
                    #                print("traitement regle",regle)
                    resultat = regle.fonc(regle, obj)
                    #                print ('params:action schema',regle.params.att_sortie.liste,
                    #                           resultat,obj.schema,regle.action_schema)

                    if resultat:
                        if obj.schema is not None:
                            if regle.action_schema:
                                # print("action schema", regle, regle.action_schema)
                                # print("schema avant", obj.schema)
                                regle.action_schema(regle, obj)
                            if regle.changeclasse:
                                regle.changeclasse(regle, obj)

                        if regle.changeschema:
                            regle.changeschema(regle, obj)
                        if regle.debugvalid:
                            obj.debug("apres", attlist=regle.champsdebug)
                    obj.is_ok = resultat

                    if regle.mode_chargeur:  # la on fait des monocoups
                        regle = None
                    else:
                        if obj.redirect and obj.redirect in regle.branchements.brch:
                            regle = regle.branchements.brch[obj.redirect]
                            obj.redirect = None
                        else:
                            regle = (
                                regle.branchements.brch["ok"]
                                if resultat
                                else regle.branchements.brch["fail"]
                            )

                else:
                    if regle.debug and "+" in regle.v_nommees["debug"]:
                        regle.affiche("--non executee--->")
                        print("suite", regle.branchements.liens_num()["sinon"])
                    regle = regle.branchements.brch["sinon"]
                # if regle and regle.valide=="done":
                #     regle = regle.branchements.brch["ok"]
            except StopIteration as abort:
                #                print ('stopiteration', ab.args)
                if abort.args[0] == "1":  # arret de traitement de l'objet
                    return
                raise  # on la passe au niveau au dessus
            except NotADirectoryError as exc:
                print("==========erreur de traitement repertoire inconnu", exc)
                print("====regle courante:", regle)
                if regle.stock_param.worker:
                    print("====mode parallele: process :", regle.getvar("_wid"))
                #                printexception()
                raise StopIteration(3)

            except NotImplementedError as exc:
                print("==========erreur de traitement fonction inexistante", exc)
                print("====regle courante:", regle)
                if regle.stock_param.worker:
                    print("====mode parallele: process :", regle.getvar("_wid"))
                printexception()
                raise StopIteration(3)

            except Exception as exc:
                print("==========erreur de traitement non gérée")
                print("====regle courante:", regle)
                if regle.stock_param.worker:
                    print("====mode parallele: process :", regle.getvar("_wid"))
                printexception()
                if regle.getvar("debuglevel", "0") != "0":
                    print("==========environnement d'execution")
                    print(
                        "====pyetl :",
                        regle.stock_param.nompyetl,
                        regle.stock_param.idpyetl,
                    )
                    print("====objet courant :", obj)
                    print("====parametres\n", regle.params)
                    print(regle.context)
                    if regle.getvar("debuglevel", "0") > "1":
                        print(
                            "========================= variables globales==========",
                            regle.stock_param.context,
                        )
                    print("========== fin erreur de traitement")

                raise StopIteration(3)
        #                raise
        if last and not last.store:
            if last.filter or last.supobj:
                self.suppcnt += 1
            if obj.schema:  # c est un objet qui a ete jete par une regle filtrante
                obj.schema.objcnt -= 1

        # print ('fin de l objet ',last.filter,last.store,last.supobj last, obj, obj.schema.objcnt)

    def vide_stock(self):
        """vidange des tuyeaux"""
        stock = True
        while stock:
            stock = False
            for regle in self.regles:
                if regle.store and regle.nbstock:
                    # print("--------menage_final ", regle, regle.nbstock)
                    stock = True
                    regle.traite_stock(regle)


class Macro(object):
    """ structure de gestion des macros"""

    def __init__(self, nom, file="", vpos=None):
        self.nom = nom
        self.file = file
        self.commandes_macro = dict()
        self.help = ""
        self.help_detaillee = []
        self.parametres_pos = []
        self.vars_utilisees = []
        self.vpos = []
        self.vdef = {}
        if vpos is not None:
            self.vpos = [i.split("=")[0].strip() for i in vpos if i and i != "\n"]
            for i in vpos:
                if "=" in i:
                    nom, defaut = i.split("=", 1)
                    self.vdef[nom.strip()] = defaut
                else:
                    self.vdef[i] = ""

    def add_command(self, ligne, numero):
        """ ajoute une commande a la liste"""
        if ligne.startswith("#!help") or ligne.startswith("#!aide"):
            self.help = ligne[6:]
            return
        if ligne.startswith("#!desc"):
            self.help_detaillee.append(ligne[6:])
            return
        if ligne.startswith("#!pars"):
            self.parametres_pos.append(ligne[6:])
            return
        if ligne.startswith("#!vars"):
            self.vars_utilisees.append(ligne[6:])
            return

        self.commandes_macro[numero] = ligne

    def bind(self, liste, context):
        """mappe les variables locales et retourne un environnement"""
        macroenv = context.getmacroenv(self.nom)
        for i in self.vpos:  # on initialise le contexte local
            macroenv.setlocal(
                i, self.vdef[i] if self.vdef.get(i) else context.getvar(i)
            )
        # print ('macro bind', self.nom, self.vpos,macroenv, macroenv.vlocales)
        context.affecte(liste, context=macroenv, vpos=self.vpos)
        return macroenv

    def get_commands(self):
        """recupere les commandes de la macro"""
        return [(i, self.commandes_macro[i]) for i in sorted(self.commandes_macro)]

    def __repr__(self):
        """affichage lisible de la macro"""
        header = "&&#def;" + self.nom + ";" + ";".join(self.vpos) + "\n"
        return " ".join(
            [header]
            + [self.help]
            + self.help_detaillee
            + [self.commandes_macro[i] for i in sorted(self.commandes_macro)]
        )


class MacroStore(object):
    """ conteneur de traitement des macros """

    def __init__(self, parent=None):
        self.macros = dict() if parent is None else dict(parent.macros)

    def regmacro(self, nom, file="", liste_commandes=None, vpos=None):
        """enregistrement d'une macro"""
        nouvelle = Macro(nom, file=file, vpos=vpos)
        if liste_commandes is not None:
            nouvelle.commandes_macro = liste_commandes
        # if vpos is not None:
        #     nouvelle.vpos = vpos
        # print ('enrregistrement macro',nom, vpos, nouvelle.vpos)
        self.macros[nom] = nouvelle
        return nouvelle

    def stocke_macro(self, description, origine):
        """stocke une description de macro"""
        macro = None
        for num, conf in description:
            if not conf or conf.startswith("!"):
                continue
            if conf.startswith("&&#define"):
                liste = conf.split(";")
                nom = liste[1]
                vpos = [i for i in liste[2:] if i]
                macro = self.regmacro(nom, file=origine, vpos=vpos)
            elif macro:
                macro.add_command(conf, num)

    def getmacro(self, nom):
        return self.macros.get(nom)

    def getmacrolist(self):
        return self.macros.keys()


class Context(object):
    """contexte de stockage des variables"""

    PARAM_EXP = re.compile(r"%((\*?)#?[a-zA-Z0-9_]+(?:#[a-zA-Z0-9_]+)?)%")
    PARAM_BIND = re.compile(r"^%(\*#?[a-zA-Z0-9_]+(?:#[a-zA-Z0-9_]+)?)%$")
    SPLITTER_PV = re.compile(r"(?<!\\);")  # reconnait les ; non précédes d'un \
    SPLITTER_V = re.compile(r"(?<!\\),")  # reconnait les , non précédes d'un \
    SPLITTER_B = re.compile(r"(?<!\\)\|")  # reconnait les | non précédes d'un \
    SPLITTER_2P = re.compile(r"(?<!\\):")  # reconnait les : non précédes d'un \

    def __init__(self, parent=None, ident="", type_c="C", env=None, root=False):
        self.nom = type_c + ident
        self.ident = self.nom
        self.type_c = type_c
        self.vlocales = dict()
        self.binding = dict()
        self.search = [self.vlocales]
        self.parent = parent
        self.ref = None
        self.root = self
        self.env = env
        self.niveau = 0
        # gestion des hierarchies
        self.setparent(parent)
        if root:
            self.root = self
            self.ref = None
        # print('creation contexte', self, self.nom)

    def setref(self, context):
        """modifie l'enchainement des contextes"""
        self.ref = context

    def setparent(self, parent, ref=True):
        """modifie l'enchainement des contextes"""
        self.parent = parent
        if parent is not None:
            self.ident = parent.ident + "<-" + self.nom
            self.search.extend(parent.search)
            self.root = self.parent.root
            self.ref = parent if (ref or not parent.ref) else parent.ref
            if self.env is None:
                self.env = parent.env

    def getmacroenv(self, ident=""):
        """fournit un contexte ephemere lie au contexte de reference"""
        return Context(parent=self, ident=ident, type_c="M")

    def getblocenvenv(self, ident=""):
        """fournit un contexte ephemere lie au contexte de reference"""
        return Context(parent=self, ident=ident, type_c="B")

    def setbinding(self, nom, binding):
        """ gere les retours de parametres"""
        self.binding[nom] = binding

    def getcontext(self, ident="", liste=None, ref=False, type_c="C"):
        """fournit un nouveau contexte de reference empilé"""
        context = Context(parent=self, ident=ident, type_c=type_c)
        if ref:
            context.ref = self.ref if self.ref else self
        if liste:
            self.affecte(liste, context=context)
        return context

    def getvar(self, nom, defaut=""):
        """fournit la valeur d'un parametre selon des contextes standardises"""
        #        if nom == 'nbaffich':
        #            print ('chemin de recherche ',self.search)
        for ctx in self.search:
            #            print ('getvar recherche', nom,' dans ', c)
            if nom in ctx:
                #                print ('contexte getvar', nom, c[nom])
                return ctx[nom]
        return defaut

    def resolve(self, element: str) -> T.Tuple[str, str]:
        """effectue le remplacement de variables"""
        element = element.strip()  # on debarasse les blancs parasites
        if self.PARAM_BIND.match(element):
            return self.getvar(element[2:-1]), element[2:-1]
        while self.PARAM_EXP.search(element):
            for i, j in self.PARAM_EXP.findall(element):
                cible = "%" + j + i + "%"
                # print ('recup getvar',cible,i)
                element = element.replace(cible, self.getvar(i))
        if element.startswith("#env:") and element.split(":")[1]:
            # on affecte une variable d'environnement
            element = self.env.get(element.split(":")[1], "")
        elif element.startswith("#eval:") and element.split(":")[1]:
            if "__" in element:
                raise SyntaxError("fonction non autorisee " + element)
            element = eval(element.split(":")[1], {})
        # print('resolve ', element)
        # element = self.getfirst(element)
        element = element.strip()  # on enleve les blancs parasites
        if element.startswith(r"\ "):  # mais on garde les blancs voulus
            element = element[1:]
        if element.endswith(" \\"):  # mais on garde les blancs voulus
            element = element[:-1]
        return element, ""

    def getfirst(self, element):
        """retourne le premier non vide d'une liste d'elements"""
        liste = self.SPLITTER_B.split(element)
        for valeur in liste:
            if valeur:
                if valeur.startswith("#env:") and valeur.split(":")[1]:
                    # on affecte une variable d'environnement
                    valeur = self.env.get(valeur.split(":")[1], "")
                elif valeur.startswith("#eval:") and valeur.split(":")[1]:
                    if "__" in valeur:
                        raise SyntaxError("fonction non autorisee " + valeur)
                    valeur = eval(valeur.split(":")[1], {})
                if valeur:
                    return valeur
        return element

    def traite_egalite(self, element):
        """ gere une affectation par egal"""
        defnom, defval = element.split("=", 1)
        nom, _ = self.resolve(defnom)
        nolocal = nom.startswith("*")
        val, binding = self.resolve(defval)
        # print ('traite_egalite', defnom, nom,'=',defval,val)
        return nom, val, binding, nolocal

    def traite_hstore(self, element, context):
        """ mappe un hstore sur l'environnement"""
        val, binding = self.resolve(element[1:])  # c'est un eclatement de hstore
        liste = [i.strip().strip('"').replace('"=>"', "=") for i in val.split('","')]
        self.affecte(liste, context=context)

    def affecte(self, liste, context=None, vpos=[]):
        """gestion directe d'une affectation"""
        nolocal = False
        for num, element in enumerate(liste):
            if "=" in element:  # c'est une affectation
                nom, val, binding, nolocal = self.traite_egalite(element)
            elif element.startswith("*%"):
                self.traite_hstore(element, context)
                continue
            else:
                val, binding = self.resolve(element)
                if num < len(vpos):
                    nom = vpos[num]
                    if nom.startswith("*"):
                        nolocal = True
                        nom = nom[1:]
                else:
                    nom = val
                    val = ""
            if nom:
                nom = nom.strip()
                if not nolocal:
                    context.setlocal(nom, val) if context else self.setlocal(nom, val)
                if binding:
                    context.setbinding(nom, binding)

    def getchain(self, noms, defaut=""):
        """fournit un parametre a partir d'une chaine de fallbacks"""
        for nom in noms:
            res = self.getvar(nom, None)
            if res is not None:
                return res
        return defaut

    def getlocal(self, nom, defaut=""):
        """fournit la valeur d'un parametre selon des contextes standardises"""
        return self.vlocales.get(nom, defaut)

    def getgroup(self, prefix):
        """fournit une liste de variables respectant un prefixe"""

        retour = self.parent.getgroup(prefix) if self.parent else dict()
        # print ('getgroup',self, retour)
        retour.update(
            ((i, j) for i, j in self.vlocales.items() if i.startswith(prefix))
        )
        return retour

    def setvar(self, nom, valeur):
        """positionne une variable du contexte de reference"""
        # print ('contexte setvar', self, nom, valeur)
        if nom in self.vlocales or self.root == self:
            self.vlocales[nom] = valeur
            if nom in self.binding and self.ref:
                self.ref.setvar(self.binding[nom], valeur)
                # print ("binding",nom,"->",self.binding[nom],':',valeur, self.parent)
        else:
            self.ref.setvar(nom, valeur) if self.ref else self.setlocal(nom, valeur)

    def setlocal(self, nom, valeur):
        """positionne une variable locale du contexte"""
        # print ('contexte setlocal', self, nom, valeur)

        self.vlocales[nom] = valeur

    def setroot(self, nom, valeur):
        """positionne une variable du contexte racine"""
        #        print ('contexte setvar', nom, valeur)
        self.root.vlocales[nom] = valeur

    def setretour(self, nom, valeur):
        """positionne une variable et la mappe sur le contexte parent"""
        self.vlocales[nom] = valeur
        if nom in self.binding and self.ref:
            self.ref.setlocal(self.binding[nom], valeur)

    def setretour_env(self, nom, valeur):
        """positionne une variable et la mappe sur le contexte parent"""
        self.vlocales[nom] = valeur
        if nom in self.binding and self.root.parent:
            self.root.parent.setvar(self.binding[nom], valeur)

    def exists(self, nom):
        """la variable existe"""
        return nom in self.ref.vlocales

    def update(self, valeurs):
        """affectation en masse"""
        self.vlocales.update(valeurs)

    def getvars(self):
        """recupere toutes les variables d'un contexte"""
        vlist = set()
        for ctx in self.search:
            vlist = vlist | ctx.keys()
        return {i: self.getvar(i) for i in vlist}

    #                print ('contexte getvar', nom, c[nom])

    def __repr__(self):
        return self.ident + ("(" + self.ref.nom + ")" if self.ref else "")


##        return self.ref.vlocales.__repr__(), self.search.__repr__()
#        return self.search.__repr__()
#        return '==============================variables locales========\n' +\
#                 '\n\t'+'\n\t'.join([i+':'+str(j) for i, j in sorted(self.vlocales.items())])+\
#                 '========================= variables globales==========\n'+\
#                 '\n\t'+'\n\t'.join([i+':'+str(j) for i, j in sorted(self.ref.vlocales.items())])
def list_input(mapper, liste, reader):
    """gere les listes d entree avec acces seie ou parallele"""
    for element in liste:
        reader(mapper, element)
