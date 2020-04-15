# -*- coding: utf-8 -*-
"""modification d'attributs en fonction d'un fichier de parametrage avec
prise en charge des expressions regulieres"""
import time

# t1=time.time()
# print ('pyetl start import ')
import os

# import sys
import re
import psutil

# import platform
import logging
import itertools
from collections import defaultdict
from types import MethodType
from pathlib import Path
from zipfile import ZipFile


# print('base',time.time()-t1)

from .vglobales import VERSION, set_mainmapper, DEFCODEC

# print ('globales',time.time()-t1)
from .formats.generic_io import Reader, Writer, READERS, WRITERS
from .formats.mdbaccess import dbaccess

# print('formats',time.time()-t1)

from .formats.ressources import GestionSorties  # formats entree et sortie
from .formats.interne.stats import Statstore  # , Stat, ExtStat
from .moteur.interpreteur_csv import (
    lire_regles_csv,
    reinterprete_regle,
    interprete_ligne_csv,
)
from .moteur.regles import RegleTraitement
from .moteur.compilateur import compile_regles
from .moteur.moteur import Moteur, MacroStore, Context
from .moteur.fonctions import COMMANDES, SELECTEURS
from .moteur.fonctions.outils import scan_entree
from .moteur.fonctions.traitement_crypt import paramdecrypter

from .schema.schema_interne import init_schema  # schemas
from .schema.schema_io import ecrire_schemas, lire_schemas_multiples

# integre_schemas # schemas
from .moteur.fonctions.parallel import setparallel

LOGGER = logging.getLogger("pyetl")  # un logger
# MODULEDEBUG = False


def initlogger(fichier=None, log="DEBUG", affich="WARNING"):
    """ création de l'objet logger qui va nous servir à écrire dans les logs"""
    # on met le niveau du logger à DEBUG, comme ça il écrit tout dans le fichier log s'il existe
    loglevels = {
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "INFO": logging.INFO,
    }
    niveau_f = loglevels.get(log, logging.INFO)
    niveau_p = loglevels.get(affich, logging.ERROR)
    # print ('niveaux de logging',niveau_f,niveau_p)
    if not LOGGER.handlers:
        # création d'un handler qui va rediriger chaque écriture de log sur la console
        LOGGER.setLevel(niveau_p)
        print_handler = logging.StreamHandler()
        printformatter = logging.Formatter(
            "\n!!!%(levelname)8s %(funcName)10s: %(message)s"
        )
        print_handler.setFormatter(printformatter)
        print_handler.setLevel(niveau_p)
        LOGGER.addHandler(print_handler)
    if fichier:
        LOGGER.setLevel(niveau_f)
        # création d'un formateur qui va ajouter le temps, le niveau
        # de chaque message quand on écrira un message dans le log
        fileformatter = logging.Formatter(
            "%(asctime)s::%(levelname)s::%(module)s.%(funcName)s" + "::%(message)s"
        )
        #        infoformatter = logging.Formatter('%(asctime)s::%(levelname)s::%(message)s')
        # création d'un handler qui va rediriger une écriture du log vers
        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        file_handler = logging.FileHandler(fichier)
        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        file_handler.setLevel(niveau_f)
        file_handler.setFormatter(fileformatter)
        LOGGER.addHandler(file_handler)
        LOGGER.info("----pyetl:" + VERSION)


def getlog(args):
    """recherche s il y a une demande de fichier log dans les arguments"""
    log = None
    log_level = None
    log_print = None
    for i in args:
        if "log=" in i:
            log = i.split("=")[1]
        if "log_level=" in i:
            log_level = i.split("=")[1]
        if "log_print=" in i:
            log_print = i.split("=")[1]
    return log, log_level, log_print


def runpyetl(commandes, args):
    """ lancement standardise c'est la fonction appelee au debut du programme"""
    loginfo = getlog(args)
    print(
        "::".join(("====== demarrage pyetl == ", VERSION, repr(commandes), repr(args)))
    )
    if MAINMAPPER.initpyetl(commandes, args, loginfo=loginfo):
        MAINMAPPER.process()
    else:
        print("arret du traitement ")
        return
    nb_total = MAINMAPPER.getvar("_st_lu_objs", 0)
    nb_fichs = MAINMAPPER.getvar("_st_lu_fichs", 0)
    if nb_total:
        print(nb_total, "objets lus dans", nb_fichs, "fichiers ")

    if MAINMAPPER.moteur:
        print(MAINMAPPER.getvar("_st_obj_duppliques", 0), "objets dupliques")
    n_ecrits = MAINMAPPER.getvar("_st_wr_objs", 0)
    if n_ecrits:
        print(
            n_ecrits,
            "objets ecrits dans ",
            MAINMAPPER.getvar("_st_wr_fichs", 0),
            "fichiers ",
        )
    MAINMAPPER.signale_fin()
    duree, _ = next(MAINMAPPER.maintimer)
    duree += 0.001
    print(
        "fin traitement total :",
        nb_fichs,
        "fichiers traites en ",
        int(duree * 1000),
        "millisecondes",
    )
    if nb_total:
        print("perf lecture  :", int(nb_total / duree), "o/s")
    if n_ecrits:
        print("perf ecriture :", int(n_ecrits / duree), "o/s")


# ---------------debut programme ---------------


class Pyetl(object):
    """ structure parent : instanciee une fois pour un traitement
    permet le stockage de tous les parametres globaux du traitement.
    cette structrure est passee a l'ensemble des modules """

    # constantes de travail
    modiffonc = re.compile(r"([nc]):(#?[a-zA-Z_][a-zA-Z0-9_]*)")
    _ido = itertools.count(1)  # compteur d'instance
    version = VERSION
    # ressources communes
    compilateur = compile_regles  # interpreteur par defaut
    lecteur_regles = lire_regles_csv
    interpreteur = interprete_ligne_csv
    lire_schemas_multiples = lire_schemas_multiples
    init_schema = init_schema
    commandes = COMMANDES
    selecteurs = SELECTEURS
    sortedsels = sorted(selecteurs.values(), key=lambda x: x.priorite)
    reconfig = reinterprete_regle
    formats_connus_lecture = READERS
    formats_connus_ecriture = WRITERS

    def __init__(self, parent=None, nom=None, context=None):

        self.nompyetl = nom if nom else "pyetl"
        self.starttime = time.time()  # timer interne
        # variables d'instance (stockage des elements)
        self.maintimer = self._timer(init=True)
        self.statstore = Statstore(self)
        self.cntr = dict()  # stockage des compteurs
        self.idpyetl = next(self._ido)
        # jointures
        self.jointabs = dict()  # clefs de jointure
        self.joint_fich = dict()  # fichier externes de jointure
        self.jointdef = dict()  # definition des champs
        self.posparm = list()
        self.store = dict()
        self.keystore = dict()
        self.dbconnect = dict()  # connections de base de donnees
        if context is None:
            context = parent.context if parent else None
        self.context = Context(
            parent=context, ident=str(self.idpyetl), type_c="P", root=True
        )
        self.context.root = self.context  # on romp la chaine racine
        self.contextstack = [self.context]
        self.parent = parent  # permet un appel en cascade
        setparallel(self)  # initialise la gestion du parallelisme

        self.loginited = self.parent.loginited if self.parent else False
        self.ended = False
        self.worker = parent.worker if parent else False  # process esclave
        #        self.paramdir = os.path.join(env.get("USERPROFILE", "."), ".pyetl")
        self.username = os.getlogin()
        self.userdir = os.path.expanduser("~")
        self.paramdir = os.path.join(self.userdir, ".pyetl")

        self.stream = 0
        self.debug = 0
        #        self.stock = False # pas de stockage

        # parametres globaux ressources
        self.bindings = dict()
        self.moteur = Moteur(self)
        # parametres de lancement
        # variables de stockage interne
        # commandes internes
        # structures de stockage partagees
        self.retour = []
        # description des fonctions statistiques (dictionnaire d'objets stats)
        # entree
        #        self.parametres_fichiers = dict() # parametres d'acces
        self.schemas = dict()  # schemas des classes
        self.regles = list()  # regles de mapping
        self.regle_sortir = None
        self.regleref = RegleTraitement("", self, "", 0)
        self.regleref.context = (
            self.context
        )  # la regle de reference n'a pas de contexte propre
        self.racine = ""
        self.fichier_regles = None
        # self.stock_param = self
        # permet de deguiser mapper en regle pour la bonne cause

        self.dupcnt = 0
        self.fichier_courant = ""
        self.chemin_courant = ""

        self.temps_fermeture = 0
        self.schemadef = False
        self.rdef = None

        self.liste_regles = None

        self.liens_variables = dict()
        self.duree = 0
        self.attlists = dict()
        self.ident_courant = ("", "")
        self._set_streammode()
        self.done = False

    def _relpath(self, path):
        """cree un chemin relatif par rapport au fichier de programme"""
        if path is None:
            return None
        return os.path.join(os.path.dirname(__file__), path)

    def initenv(self, env=None, loginfo=None):
        """initialise le contexte (parametres de site environnement)"""
        if self.loginited:
            return  # on a deja fait le boulot
        env = env if env is not None else os.environ
        log_level = "INFO"
        log_print = "WARNING"
        if loginfo and not self.worker:
            log, log_level, log_print = loginfo
            self.setvar("logfile", log)
            self.setvar("log_level", log_level)
            self.setvar("log_print", log_print)

        initlogger(
            fichier=self.getvar("logfile", None), log=log_level, affich=log_print
        )
        self.init_environ(env)
        self.loginited = True

    #        self.aff = self._patience(0, 0) # on initialise le gestionnaire d'affichage
    #        next(self.aff)

    def initpyetl(self, commandes, args, env=None, loginfo=None):
        """ initialisation standardisee: cree l'objet pyetl de base"""

        self.initenv(env, loginfo)
        try:
            result = self.prepare_module(commandes, args)
        except SyntaxError as err:
            LOGGER.critical(
                "erreur script "
                + str(commandes)
                + " "
                + str(err)
                + " worker:"
                + str(self.worker)
            )
            result = False
        LOGGER.info(
            "::".join(
                (
                    "====== demarrage == ",
                    self.nompyetl,
                    str(self.idpyetl),
                    repr(commandes),
                    repr(args),
                )
            )
        )
        return result

    def init_environ(self, env):
        """initialise les variables d'environnement et les macros"""
        self.env = os.environ if env is None else env
        self.context.env = self.env
        if not os.path.isdir(self.paramdir):
            try:
                os.makedirs(self.paramdir)
            except PermissionError:
                self.paramdir = ""
        self.site_params_def = env.get("PYETL_SITE_PARAMS", "")
        self.liste_params = None
        if self.parent is None:
            self._init_params()  # positionne les parametres predefinis
            self.macrostore = MacroStore()
            self.site_params = dict()
            self.dbref = dict()
            # charge les parametres de site (fichier ini)
            self._charge_site_params(self.site_params_def)
            self._charge_site_params(self.paramdir)
            cryptinfo = (
                os.getlogin(),
                self.getvar("usergroup"),
                self.getvar("masterkey"),
                self.getvar("userkey"),
                self.getvar("defaultkey"),
                self.getvar("cryptolevel"),
                self.getvar("cryptohelper"),
            )
            paramdecrypter(self.site_params, cryptinfo)
            self._setdbref()  # reference les bases de donnees
            self.charge_cmd_internes()  # macros internes
            self.charge_cmd_internes(site="macros", opt=1)  # macros de site
            if self.paramdir is not None:
                self.charge_cmd_internes(
                    direct=os.path.join(self.paramdir, "macros"), opt=1
                )  # macros perso
            self.sorties = GestionSorties()
            self.debug = int(self.getvar("debug", 0))

        else:
            self.macrostore = MacroStore(self.parent.macrostore)
            # self.macros = dict(self.parent.macros)
            self.site_params = self.parent.site_params
            self.dbref = self.parent.dbref
            self.sorties = self.parent.sorties

    def getmacro(self, nom):
        """recupere une macro par son nom"""
        return self.macrostore.getmacro(nom)

    def stocke_macro(self, description, origine):
        return self.macrostore.stocke_macro(description, origine)

    def getmacrolist(self):
        """recupere un iterateur sur les macros"""
        return self.macrostore.getmacrolist()

    @property
    def macro(self):
        return self.macrostore.macros

    def specialenv(self, params, macros):
        """lit un bloc de parametres et de macros specifiques"""
        if params:
            self._charge_site_params(params)
        if macros:
            self.charge_cmd_internes(direct=macros)

    def commandes_speciales(self):
        """commandes speciales"""
        #        print("commandes speciales: ", self.fichier_regles)

        # on ne lit pas de regles mais on prends les commandes predefinies
        if self.fichier_regles is None:
            return
        liste_commandes = self.fichier_regles.split(",")
        commande, *pars = liste_commandes[0].split(":")
        nom = self.getvar("_sortie")

        if commande == "#help" or commande == "help":
            from pyetl.helpdef.helpmodule import print_help

            self.setvar("_sortie", "")
            print_help(self, nom)
            self.done = True

        elif commande == "#autotest" or commande == "autotest":
            #            print("detecte autotest ", self.fichier_regles, self.posparm)

            from pyetl.tests.testmodule import full_autotest

            liste_regles = full_autotest(self, pars[0] if pars else nom)
            self.setvar("_sortie", "")
            self.setvar("_testmode", "autotest")
            if not liste_regles:
                self.done = True
            else:
                self.fichier_regles = ""
                self.liste_regles = liste_regles
                # on a charge les commandes on neutralise l autotest

        elif commande == "#unittest" or commande == "unittest":
            from pyetl.tests.testmodule import unittests

            self.setvar("_sortie", "")
            self.setvar("_testmode", "unittest")
            # print("positionnement testmode", self.context)
            unittests(self, nom=nom, debug=self.getvar("debug"))
            self.done = True

        elif commande == "#formattest" or commande == "formattest":
            from pyetl.tests.testmodule import formattests

            self.setvar("_sortie", "")
            self.setvar("_testmode", "formattest")
            formattests(self, nom=nom, debug=self.getvar("debug"))
            self.done = True

    def _traite_params(self, liste_params):
        """gere la liste de parametres"""
        if liste_params is not None:
            self.liste_params = liste_params[:]
            for i in liste_params:
                self._stocke_param(i)  # decodage parametres de lancement
            #            print ('traite_param',len(self.posparm))
            if len(self.posparm) >= 2:
                self.setvar("_entree", self.posparm[0])
                self.setvar("_sortie", self.posparm[1])
            elif len(self.posparm) == 1:
                self.setvar("_sortie", self.posparm[0])

    def prepare_module(self, regles, liste_params):
        """ prepare le module pyetl pour l'execution"""

        if isinstance(regles, list):
            self.nompyetl = "pyetl"
            self.liste_regles = regles
        else:
            self.fichier_regles = regles
            self.nompyetl = regles
            self.rdef = os.path.dirname(regles)  # nom de repertoire des regles
        self._traite_params(liste_params)
        # on initialise le gestionnaire d'affichage
        self.aff = self._patience(
            self.getvar("_st_lu_objs", 0), self.getvar("_st_lu_fichs", 0)
        )
        next(self.aff)

        LOGGER.debug(
            "prepare_module"
            + repr(regles)
            + "::"
            + repr(liste_params)
            + "::"
            + self.getvar("_sortie", "pas_de_sortie")
        )
        erreurs = None
        if self.fichier_regles or self.liste_regles:
            self.commandes_speciales()
            if not self.done:
                try:
                    erreurs = self.lecteur_regles(
                        self.fichier_regles, liste_regles=self.liste_regles
                    )
                except KeyError as ker:
                    LOGGER.critical(
                        "erreur lecture " + repr(ker) + "(" + repr(regles) + ")"
                    )
                    erreurs = erreurs + 1 if erreurs else 1
                    raise

            if erreurs:
                #                print("logger ", self.idpyetl)
                message = " erreur" if erreurs == 1 else " erreurs"
                LOGGER.critical(
                    "process "
                    + str(self.idpyetl)
                    + ": "
                    + str(erreurs)
                    + message
                    + " d'interpretation des regles:"
                    + " arret du traitement "
                )
                for i in self.regles:
                    if i.erreurs:
                        print("erreur interpretation", i.numero, i, i.erreur)
                #                print("sortie en erreur", self.idpyetl)
                return False
        self.sorties.set_sortie(self.getvar("_sortie"))
        if not self.regles:
            #            print('pas de regles', self.done)
            if self.done:
                return True
            LOGGER.critical(
                "pas de regles arret du traitement " + str(self.fichier_regles)
            )
            return False

        self._set_streammode()
        try:
            self.compilateur(None, self.debug)
            self.regle_sortir = self.regles[-1]
            self.regle_sortir.declenchee = True
            self.moteur.setregles(self.regles, self.debug)
            self.moteur.regle_debut = self.regles[0].numero
            #            print('preparation module',self.getvar('_entree'), '->', self.getvar('_sortie'))
            return True
        # on refait si des choses ont change a l'initialisation
        except EOFError:
            LOGGER.critical("pas de fichier de regles arret du traitement ")
            #            print("erreurs de compilation arret du traitement ")
            return False

    def _timer(self, init=True):
        """acces au temps pour les calculs de duree."""
        heure_debut = self.starttime if init else time.time()
        intermediaire = 0
        prec = heure_debut
        while True:
            yield (time.time() - heure_debut, intermediaire)
            intermediaire = time.time() - prec
            prec = time.time()

    def _patience(self, nbfic, nbval):
        """petits messages d'avancement pour faire patienter"""
        temps = self._timer()
        nbaffich = int(self.getvar("nbaffich"))
        #        print ('init_patience ',self.worker, self.getvar('_wid', -1))
        prochain = nbaffich
        interm = 0.001  # temps intermediaire pour les affichages interm
        nop = 0
        nbtotal = 0
        tabletotal = 0
        interm = 0.001
        duree = 0

        def affiche(message, nbobj):
            """gere l'affichage des messages de patience"""
            duree, interv = next(temps)
            if duree == 0:
                duree = 0.001
            cmp = "---"
            ftype = "fichiers"
            tinterm = 0.001
            if message == "interm":
                cmp = "int"
            if message == "tab":
                ftype = "tables"
            msg = (
                " --%s----> nombre d'objets lus %8d dans %4d %s en %5d "
                + "secondes %5d o/s"
            )
            if self.worker:
                msg = "worker%3s:" % self.getvar("_wid") + msg
            else:
                msg = "mapper   :" + msg
            LOGGER.info(
                " ".join(
                    (
                        msg,
                        str(cmp),
                        str(nbobj),
                        str(tabletotal),
                        str(ftype),
                        str(int(duree)),
                        str(int(nbobj / duree)),
                        str(int((nbobj - nop) / (interv + 0.001))),
                    )
                )
            )
            if self.worker:
                if message == "interm":
                    tinterm = interm + interv
                    msg = " --int----> nombre d'objets lus %8d en %5d secondes: %5d o/s"
                    msg = "worker%3s:" % self.getvar("_wid") + msg
                    if interm > 1:
                        tinterm = interm + interv
                    else:  # on calcule un temps moyen pour pas afficher n'importe quoi
                        tinterm = nbval / (nbobj / duree)
                    print(msg % (nbval, int(tinterm), int((nbval) / tinterm)))
            else:
                print(
                    msg
                    % (
                        cmp,
                        nbobj,
                        tabletotal + 1,
                        ftype,
                        int(duree),
                        int((nbobj) / duree),
                    )
                )
            return (
                (max(int(prochain / nbaffich), int(nbobj / nbaffich)) + 1) * nbaffich,
                tinterm,
            )

        while True:
            message, nbfic, nbval = yield
            #            nbtotal += nbval
            if message == "init":
                temps = self._timer(init=not self.worker)
                duree, interv = next(temps)
                interm = 0.001
                nbtotal = 0
                prochain = nbaffich
            elif nbtotal + nbval >= prochain:
                prochain, interm = affiche(message, nbtotal + nbval)
                nop = nbtotal + nbval
            if message != "interm":
                nbtotal += nbval
                nbval = 0
                interm = 0.001
            # print ('actualisation nbtotal',message,  nbtotal,nbval,'->',nbtotal+nbval, prochain)
            tabletotal += nbfic

    def getpyetl(
        self,
        regles,
        entree=None,
        rep_sortie=None,
        liste_params=None,
        env=None,
        nom="",
        mode=None,
    ):
        """ retourne une instance de pyetl sert pour les tests et le
        fonctionnement en fcgi et en mode batch"""
        #        print(" dans getpyetl",mode)
        if not regles:
            if mode is None:
                return None

        env = env if env is not None else self.env
        petl = Pyetl(parent=self)
        petl.init_environ(env)
        if rep_sortie is not None:
            if rep_sortie.startswith("#"):
                petl.setvar("F_sortie", "#store")
                petl.setvar("force_schema", "0")
                rep_sortie = rep_sortie[1:]
                # print('getpyetl: format store',rep_sortie, regles)
            petl.setvar("_sortie", rep_sortie)
        if entree is not None:
            #            print ("entree getpyetl",type(entree))
            petl.setvar("_entree", entree)
        # print ('getpyetl entree:', petl.getvar('_entree'),'parent:', self.getvar('_entree'))
        if nom:
            petl.nompyetl = nom
        if petl.initpyetl(regles, liste_params, env=env):
            return petl
        print("erreur getpyetl", regles)
        return None

    def _set_streammode(self):
        """positionne le mode de traitement"""
        self.stream = 1 if self.getvar("mode_sortie") == "C" else False
        if self.getvar("mode_sortie") == "D":
            self.stream = 2

    #        print('---------pyetl : mode sortie', self.stream, self.getvar("mode_sortie"))

    def _setdbref(self):
        """identifie les references de bases de donnees pour qgis"""
        for nom in self.site_params:
            variables = self.site_params[nom]
            base, host, port = None, None, None
            for clef, val in variables:
                if clef == "server" and "port" in val and "host" in val:
                    host, port = val.split(" ", 1)
                elif clef == "base":
                    base = val
            if base:
                self.dbref[base, host, port] = nom

    def _charge_site_params(self, origine):
        """ charge des definitions de variables liees au site """
        if not origine:  # localisation non definie
            return
        configfile = os.path.join(origine, "site_params.csv")
        if not os.path.isfile(configfile):
            print("pas de parametres locaux", configfile)
            return
        nom = ""
        #        print('parametres locaux', configfile)
        #        init = False
        for conf in open(configfile, "r").readlines():
            liste = (conf[:-1] + ";;").split(";")
            if liste[0].startswith("!") or liste[0].strip() == "":
                continue
            if liste and liste[0].strip() == "&&#set":  # on ecrase ou on cree
                nom = liste[1]
                self.site_params[nom] = list()
            #                print ('chargement parametres de site ',nom)
            elif liste and liste[0].strip() == "&&#add":  # on ajoute des valeurs
                nom = liste[1]
                if nom not in self.site_params:
                    self.site_params[nom] = list()
            #                print ('chargement complement parametres de site ',nom)
            else:
                if nom:
                    nom_p, val = liste[0], liste[1]
                    self.site_params[nom].append((nom_p, val))
        #                    self.site_params[nom].append((liste[0]+'_'+nom, liste[1]))
        self.load_paramgroup("init", fin=False)

    #        print("parametres de site",origine)
    #        print("variables",self.parms)

    def load_paramgroup(self, clef, nom="", check="", fin=True, context=None):
        """ charge un groupe de parametres """
        # print("chargement", clef, self.site_params[clef], context)

        if not clef:
            return
        context = context if context is not None else self.context
        if check:  # on verifie que l'on a pas deja defini les choses avant
            #            print ('validation ',check,check+nom,check+nom in self.parms)
            if context.exists(check + nom):
                return True
        if clef in self.site_params:
            # print("chargement", clef, self.site_params[clef], context)
            for var, val in self.site_params[clef]:
                val, _ = context.resolve(val)  # on fait du remplacement à la volee
                context.setlocal(var, val)
                # print('loadparamgroup',setter,var,val)
                if nom:
                    context.setvar(var + "_" + nom, val)
            return True
        elif fin:
            print("definition parametres de site >" + clef + "< introuvable")
            print("aide:groupes connus: ")
            print("\n".join([str(i) for i in sorted(self.site_params)]))
            raise KeyError
        return False

    def charge_cmd_internes(self, test=None, site=None, direct=None, opt=0):
        """ charge un ensemble de macros utilisables directement """
        configfile = self._relpath("moteur/fonctions/commandes_internes.csv")
        if test:
            testrep = self.getvar("_test_path")
            configfile = os.path.join(testrep, str(test) + ".csv")
        if site:
            #            print("chargement parametres de site", self.nompyetl,
            #                  self.site_params_def, site)
            configfile = os.path.join(self.site_params_def, site + ".csv")
        if direct:
            configfile = direct + ".csv"
        if configfile is None or not os.path.isfile(configfile):
            if not opt:
                print("fichier de config", configfile, "introuvable")
            return
        description = enumerate(open(configfile, "r").readlines())
        self.stocke_macro(description, configfile)

    def _init_params(self):
        """initialise les parametres
        #help||parametres systeme:
        """

        self.context.update(
            [
                ("mode_sortie", "D"),
                ("memlimit", 100000),
                ("sans_entree", ""),
                ("nbaffich", 100000),
                ("filtre_entree", ""),
                ("sans_sortie", ""),
                ("_st_lu_objs", 0),
                ("_st_lu_fichs", 0),
                ("_st_lu_tables", 0),
                ("_st_wr_objs", 0),
                ("_st_wr_fichs", 0),
                ("_st_wr_tables", 0),
                ("_st_obj_duppliques", 0),
                ("_st_obj_supprimes", 0),
                ("tmpdir", "./tmp"),
                ("F_entree", ""),
                ("racine", "."),
                ("job_control", "no"),
                ("aujourdhui", time.strftime("%Y/%m/%d 00:00:00")),
                ("annee", time.strftime("%Y")),
                ("mois", time.strftime("%m")),
                ("jour", time.strftime("%D")),
                ("jour_a", time.strftime("%j")),
                ("jour_m", time.strftime("%d")),
                ("jour_s", time.strftime("%w")),
                ("stat_defaut", "affiche"),
                ("fstat", ""),
                ("force_schema", "util"),
                ("epsg", "3948"),
                ("_pv", ";"),
                ("F_sortie", ""),
                (
                    "xmldefaultheader",
                    '<?xml-stylesheet href="xsl/dico.xsl" type="text/xsl"?>',
                ),
                ("codec_sortie", DEFCODEC),
                ("codec_entree", DEFCODEC),
                ("_paramdir", self.site_params_def),
                ("_paramperso", self.paramdir),
                ("_version", self.version),
                ("_progdir", os.path.dirname(__file__)),
            ]
        )

    def getstats(self):
        """retourne un dictionnaire avec les valeurs des stats"""
        # print ('--------getstats', self.context,self.context.getgroup("_st_"))
        return self.context.getgroup("_st_")

    # ======================== fonctions de manipulation des contextes =====================

    def getcontext(self, context=None, ident="", ref=False, type_c="C"):
        """recupere un contexte en cascade"""
        context = self.cur_context if context is None else context
        return context.getcontext(ident=ident, ref=ref, type_c=type_c)

    def pushcontext(self, context=None, ident="", type_c="C"):
        if context is None:
            context = self.getcontext(None, ident, type_c)
        self.contextstack.append(context)
        # print("apres push",self.contextstack)
        return self.cur_context

    def popcontext(self, typecheck=None):
        # print("avant pop",self.contextstack)
        if typecheck is None or self.cur_context.type_c == typecheck:
            self.contextstack.pop()
        else:
            print(
                "=========================popcontext warning typecheck attendu",
                typecheck,
                "trouve",
                self.cur_context.type_c,
                "(",
                self.cur_context,
                ")",
            )
            # raise
        return self.cur_context

    @property
    def cur_context(self):
        return self.contextstack[-1]

    def getvar(self, nom, defaut=""):
        """recupere la valeur d une varible depuis le contexte"""
        return self.context.getvar(nom, defaut)

    def setvar(self, nom, valeur):
        """positionne une variable dans un contexte de base
           dans ce cas on positionne en local"""
        # print ('setvar:',self.context, nom,valeur)
        self.context.setlocal(nom, valeur)

    def setvar_parent(self, nom, valeur):
        """positionne une variable dans un contexte de base
           dans ce cas on positionne dans le contexte parent"""
        if self.parent:
            self.parent.setvar(nom, valeur)
        else:
            self.setvar(nom, valeur)

    def padd(self, nom, valeur):
        """incremente un parametre d'une valeur"""
        # vinit = self.context.getvar(nom, 0)
        self.setvar(nom, self.context.getvar(nom, 0) + valeur)

    #        print ('padd',nom,self.getvar(nom, 0, local=parent))

    def pasum(self, nom1, nom2):
        """incremente un parametre d'un autre parametre"""
        vinit = self.getvar(nom1, 0)
        valeur = self.getvar(nom2, 0)
        self.setvar(nom1, str(vinit + valeur))

    def _stocke_param(self, parametre):
        """stockage d'un parametre"""
        if "=" in parametre:
            valeur = parametre.split("=", 1)
            if len(valeur) < 2:
                valeur.append("")
            if valeur[1] == '""':
                valeur[1] = ""
            #            self.parms[valeur[0]] = valeur[1]
            self.setvar(*valeur)
            # print("stockage parametre:",parametre,valeur[0])
        else:
            self.posparm.append(parametre)
            #            self.parms["#P_"+str(len(self.posparm))] = parametre
            self.setvar("#P_" + str(len(self.posparm)), parametre)

    def set_abrev(self, nom_schema, dic_abrev=None):
        """cree les abreviations pour la definition automatique de snoms courts"""
        if dic_abrev is None:
            dic_abrev = self.getvar("abreviations")
        if nom_schema in self.schemas:
            self.schemas[nom_schema].dic_abrev = dic_abrev

    def charge(self, fichier, ident_fich):
        """prechargement des fichiers de jointure ou de comparaison """
        #        print("charge: prechargement",fichier, ident_fich)

        clef = self.jointdef[ident_fich]
        self.joint_fich[ident_fich] = fichier
        stock = dict()
        #        if fichier.startswith('db:'):

        if self.rdef:
            fichier = fichier.replace("D:", self.rdef + "/")
        if os.path.isfile(fichier):  # si le fichier n'existe pas on cree une table vide
            #            print("info :pyetl: chargement jointure", fichier)
            for i in open(fichier, "r", encoding=self.getvar("codec_entree", "utf-8")):
                liste = i[:-1].split(";")
                stock[liste[clef].strip()] = liste
        else:
            print("erreur:pyetl: fichier jointure introuvable :", fichier)

        self.jointabs[ident_fich] = stock

    #        print("charge: prechargement",fichier, ident_fich, stock)

    def _prep_chemins(self, chemin: str, nom: str) -> str:
        """effectue la resolution des chemins """
        # chemin du fichier de donnees
        f_intrm = nom.replace("C:", os.path.join(self.racine, chemin))
        # fichier de jointure dans le repertoire de regles
        f_intrm = f_intrm.replace("D:", self.rdef + "/")
        # nom du fichier de donnees courant
        f_final = f_intrm.replace("F:", self.fichier_courant)
        # print ("jointure dynamique",self.mapper.racine,';',chemin,';',":",nom,'->',f,'(',f1,')')
        return f_final

    def jointure(self, fichier, chemin, clef, champ):
        """preparation d'une jointure: chemin dynamique"""
        f_final = self._prep_chemins(chemin, fichier)
        if self.joint_fich[fichier] != f_final:
            self.charge(f_final, fichier)
        return self.jointabs[fichier].get(clef.strip(), ["" for i in range(champ + 1)])[
            champ
        ]

    def jointure_s(self, fichier, clef, champ):
        """jointure statique chemin absolu ou relatif au repertoire de regles"""
        cle = clef.strip()
        #        print ('dans jointure ', self.jointabs)
        try:
            return self.jointabs[fichier][cle][champ]
        except KeyError:
            if self.debug:
                print(
                    "pyetl: jointure statique clef non trouvee ", fichier, clef, champ
                )
            return ""

    #        return self.jointabs[fichier].get(clef.strip(), ["" for i in range(champ+1)])[champ]

    def get_converter(self, geomnatif):
        """ retourne le bon convertisseur de format geometrique"""
        return READERS.get(geomnatif, READERS["interne"]).converter

    def _finalise_sorties(self):
        """ vide les tuyeaux et renseigne les stats"""
        if self.sorties:
            nb_fichs, nb_total = self.sorties.final(self.idpyetl)
            self.padd("_st_wr_fichs", nb_fichs)
            self.padd("_st_wr_objs", nb_total)
        if self.moteur:
            self.padd("_st_obj_duppliques", self.moteur.dupcnt)

    def process(self, debug=0):
        """traite les entrees """
        # print ('debut_process avant macro',self.idpyetl)
        self.debug = debug
        abort = False
        duree = 0
        entree = None if self.getvar("sans_entree") else self.getvar("_entree", None)
        self.macro_entree()
        entree = None if self.getvar("sans_entree") else self.getvar("_entree", None)

        # print("process E:",entree,'S:',self.getvar("sortie"),'regles', self.regles)
        if self.done:
            pass
        elif self.statstore.isstat(entree):
            nb_total = entree.to_obj(self)
            #            nb_total = self._lecture_stats(entree)
        elif entree and entree.strip() and entree != "!!vide":
            print(
                "mapper: debut traitement donnees:>" + entree + "-->",
                self.regle_sortir.params.cmp1.val,
            )
            try:
                self.aff.send(("init", 0, 0))
                # for i in fichs:
                for fich, parms in scan_entree(
                    rep=entree,
                    force_format=self.getvar("F_entree"),
                    fileselect=self.getvar("fileselect"),
                    dirselect=self.getvar("dirselect"),
                    filtre_entree=self.getvar("filtre_entree"),
                ):
                    # print ('mapper:traitement fichier',i)
                    # traitement.racine_fich = os.path.dirname(i)
                    if self.worker:
                        self.aff.send(("init", 0, 0))
                    try:
                        # nb_lu = self.lecture(i, parms=parametres[i])
                        nb_lu = self.lecture(fich, parms=parms)
                    except StopIteration as arret:
                        #            print("intercepte abort",abort.args[0])
                        if arret.args[0] == "2":
                            continue
                        abort = True
                        nb_lu = 0
                        break
            except NotADirectoryError as err:
                print(
                    "!!!!!!!!!!!!!!!!!!!!!attention repertoire d'entree inexistant:",
                    err,
                )
                print("type entree ", type(entree))
            # else:
            #     print("pas de fichiers en entree")
            print("mapper: ---------> fin traitement donnees:", int(duree))
            print("mapper: ---------> finalisation:")
        else:
            try:
                # print ('debut_process sans entree apres macro',self.idpyetl)
                self.moteur.traitement_virtuel(unique=1)
            except StopIteration as arret:
                abort = True
        if abort:
            self._finalise_sorties()
        else:
            try:
                self.menage_final()
            except StopIteration:
                self._finalise_sorties()
        #        print('mapper: fin traitement donnees:>', entree, '-->', self.regle_sortir.params.cmp1.val)
        LOGGER.info(
            "::".join(
                (
                    "====== fin == ",
                    self.nompyetl,
                    str(self.idpyetl),
                    str(self.getvar("_st_lu_objs", "0")),
                )
            )
        )
        return

    def menage_final(self):
        """vidage de tous les tuyaux et stats finales"""
        self.moteur.vide_stock()
        self.debug = 0
        # self._finalise_sorties()
        self._ecriture_schemas()
        self._ecriture_stats()
        self._finalise_sorties()  # on ne finalise les sorties que la pour tenir compte des traitements eventuels de schemas
        self.macro_final()
        return

    def macrorunner(
        self, texte, parametres=None, entree=None, sortie=None, retour=None
    ):
        """execute une macro (initiale ou finale)"""
        regles = [(1, texte if texte.startswith("<") else "<" + texte)]
        processor = self.getpyetl(
            regles, liste_params=parametres, entree=entree, rep_sortie=sortie
        )
        #        print('parametres macro', processor.nompyetl, [(i,processor.getvar(i))
        #                                                       for i in macro.vpos])
        if processor is not None:
            processor.process()
            print("macro effectuee", texte, self.idpyetl, "->", processor.idpyetl)
            if retour:
                return {i: processor.getvar(i) for i in retour}
        return ()

    def macro_final(self):
        """ execute une macro finale"""
        if self.worker and self.parent is None:
            macrofinale = self.context.getlocal("_w_end")
        else:
            macrofinale = self.context.getlocal("_end") or self.context.getlocal("#end")
        if not macrofinale:
            return
        parametres = self.getvar("parametres_final")
        entree = self.getvar("entree_final", self.getvar("_sortie"))
        sortie = self.getvar("sortie_final", self.getvar("_sortie"))
        self.macrorunner(macrofinale, parametres, entree, sortie)
        return

    def macro_entree(self):
        """ execute une macro de demarrage"""

        if self.worker and self.parent is None:
            macroinit = self.context.getlocal("_w_start")
        else:
            macroinit = self.context.getlocal("_start") or self.context.getlocal(
                "#start"
            )
        if not macroinit:
            # print ('pas de macro initiale')
            return
        print("macro initiale", macroinit)
        parametres = self.getvar("parametres_initial")
        entree = self.getvar("entree_initial", self.getvar("_entree"))
        sortie = self.getvar("sortie_initial", self.getvar("_entree"))
        self.macrorunner(macroinit, parametres, entree, sortie)
        return

    def _ecriture_schemas(self):
        """sortie des schemas """
        modes_schema_num = {
            "0": "no",  # pas de sortie de schema
            "1": "util",  # sort les schemas des classes utilisees dans le traitement
            "2": "non_vide",  # on ne sort que les schemas des classes non vides
            "3": "all",  # sort les schemas de toutes les classes definies
            "4": "int",  # sort les schemas de toutes les classes y compris internes
            "5": "fusion",  # combine les schemas en fonction des poids}
        }
        rep_sortie = self.getvar("sortie_schema", self.getvar("_sortie"))
        # print("sortie schema:contexte",self.context, self.worker,self.getvar("_testmode"), self.getvar('test_courant'))
        if rep_sortie == "-" or not rep_sortie:  # pas de sortie on ecrit pas
            if not self.getvar("_testmode"):  # en mode test on rale pas
                print("schema:pas de repertoire de sortie")
            return
        mode_schema = self.getvar("force_schema", "util")
        mode_schema = modes_schema_num.get(mode_schema, mode_schema)
        LOGGER.info("ecriture schemas " + str(mode_schema))
        if (
            mode_schema in {"all", "int", "fusion"}
            or self.getvar("force_virtuel") == "1"
            and not self.done
        ):
            print(
                "pyetl: traitement virtuel ",
                mode_schema,
                self.worker,
                self.getvar("force_virtuel"),
            )
            self.moteur.traitement_virtuel()  # on force un peu pour creer toutes les classes
            self.moteur.vide_stock()
        #        print('pyetl: ecriture schemas ', mode_schema)
        ecrire_schemas(
            self, rep_sortie, mode_schema, formats=self.getvar("format_schema", "csv")
        )

    def _ecriture_stats(self):
        self.statstore.ecriture_stats()
        if self.getvar("fstat"):  # ecriture de statistiques de fichier
            self.statstore.ecriture_stat_fichiers()

    def signale_fin(self):
        """ecrit un fichier pour signaler la fin du traitement"""
        if self.worker or self.parent or self.getvar("job_control", "no") == "no":
            return
        print("info: pyetl:job_control", self.getvar("job_control"))
        open(self.getvar("job_control"), "w").write("fin mapper\n")

    def getreader(self, nom_format, regle, reglestart=None):
        """retourne un reader"""
        return Reader(nom_format, regle, reglestart)

    def getwriter(self, nom_format, regle):
        """retourne un reader"""
        return Writer(nom_format, regle, None)

    def getdbaccess(self, regle, nombase, type_base=None, chemin="", description=None):
        """retourne une connection et la cache"""
        if nombase in self.dbconnect:
            return self.dbconnect[nombase]
        connection = dbaccess(regle, nombase, type_base, chemin, description)
        if connection:
            self.dbconnect[nombase] = connection
        return connection

    def lecture(self, fich, regle=None, reglenum=None, parms=None):
        """ lecture d'un fichier d'entree"""
        if parms is not None:
            racine, chemin, fichier, ext = parms
        else:  # on invente
            ext = os.path.splitext(fich)[1]
            fichier = os.path.basename(fich)
            rep = os.path.dirname(fichier)
            chemin = os.path.basename(rep)
            racine = os.path.dirname(rep)
        self.fichier_courant = fich
        self.chemin_courant = chemin
        self.racine = str(racine)
        #        self._setformats(ext if force_sortie is None else force_sortie)
        # positionne le stockage au bon format
        regle = (
            self.regles[reglenum] if regle is None and reglenum is not None else regle
        )
        # print('pyetl:lecture ', fich, self.racine, chemin, fichier, ext,'->', regle)
        reglestart = regle.branchements.brch["gen"] if regle else self.regles[0]
        # print ('--------------------appel lecture ',fichier, regle, '->', reglestart)
        if regle is None:
            regle = reglestart
        if ext not in regle.lecteurs:
            regle.lecteurs[ext] = Reader(ext, regle, reglestart)
        lecteur = regle.lecteurs[ext]
        # print ('initialisation reader', ext, lecteur, lecteur.schema)
        #        print ('lecteur',lecteur.lire_objets, lecteur)
        #        print ('lecture fichier ',fichier, regle, reglestart)
        #        if self.worker:
        #            print('lecture batch',os.getpid(), reglestart.ligne)
        #            raise
        try:
            lecteur.lire_objets(self.racine, chemin, fichier)
        except GeneratorExit:
            pass
        # print ('fin lecture fichier', fichier)
        self.padd("_st_lu_objs", lecteur.lus_fich)
        self.padd("_st_lu_fichs", 1)
        if self.worker:  # en mode worker on ne compte que les intermediaires
            self.aff.send(("init", 0, 0))  # on reinitialise le compteur
        else:
            self.aff.send(("fich", 1, lecteur.lus_fich))
        return lecteur.lus_fich


# on cree l'objet parent et l'executeur principal
MAINMAPPER = Pyetl()
set_mainmapper(MAINMAPPER)


def _main():
    """ mode autotest du module """
    print("autotest complet")
    ppp = MAINMAPPER
    if ppp.prepare_module("#autotest", []):
        ppp.process()
        print("fin procedure de test", next(ppp.maintimer))
    else:
        print("execution impossible")


if __name__ == "__main__":
    # execute only if run as a script
    _main()
