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
from .formats.generic_io import Reader, READERS, WRITERS

# print('formats',time.time()-t1)

from .formats.ressources import GestionSorties  # formats entree et sortie
from .formats.interne.stats import Stat, ExtStat
from .moteur.interpreteur_csv import (
    lire_regles_csv,
    reinterprete_regle,
    interprete_ligne_csv,
)
from .moteur.compilateur import compile_regles
from .moteur.moteur import Moteur, Macro, Context
from .moteur.fonctions import COMMANDES, SELECTEURS
from .moteur.fonctions.outils import scan_entree_2
from .schema.schema_interne import init_schema  # schemas
from .schema.schema_io import ecrire_schemas, lire_schemas_multiples  # integre_schemas # schemas
from .moteur.fonctions.parallel import setparallel

# from  .moteur.fonctions.parallel import initl
# from  .outils.crypt import crypter, decrypt
# print('fin_init',time.time()-t1)
# VERSION = "0.8.2.2_e"
LOGGER = logging.getLogger("pyetl")  # un logger
# MODULEDEBUG = False






def initlogger(fichier=None, log="DEBUG", affich="WARNING"):
    """ création de l'objet logger qui va nous servir à écrire dans les logs"""
    # on met le niveau du logger à DEBUG, comme ça il écrit tout dans le fichier log s'il existe
    loglevels={'DEBUG':logging.DEBUG,'WARNING':logging.WARNING,'ERROR':logging.ERROR,'CRITICAL':logging.CRITICAL,'INFO':logging.INFO}
    niveau_f=loglevels.get(log,logging.INFO)
    niveau_p=loglevels.get(affich,logging.ERROR)
    # print ('niveaux de logging',niveau_f,niveau_p)
    if not LOGGER.handlers:
        # création d'un handler qui va rediriger chaque écriture de log sur la console
        LOGGER.setLevel(niveau_p)
        print_handler = logging.StreamHandler()
        printformatter = logging.Formatter("\n!!!%(levelname)8s %(funcName)10s: %(message)s")
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
    log_level=None
    log_print=None
    for i in args:
        if "log=" in i:
            log = i.split("=")[1]
        if "log_level=" in i:
            log_level = i.split("=")[1]
        if "log_print=" in i:
            log_print = i.split("=")[1]
    return log,log_level,log_print


def runpyetl(commandes, args):
    """ lancement standardise c'est la fonction appelee au debut du programme"""
    loginfo = getlog(args)
    print('::'.join(("====== demarrage pyetl == ", VERSION, repr(commandes), repr(args))))
    if MAINMAPPER.initpyetl(commandes, args, loginfo=loginfo):
        MAINMAPPER.process()
    else:
        print("arret du traitement ")
        return
    nb_total = MAINMAPPER.get_param("_st_lu_objs", 0)
    nb_fichs = MAINMAPPER.get_param("_st_lu_fichs", 0)
    if nb_total:
        print(nb_total, "objets lus dans", nb_fichs, "fichiers ")

    if MAINMAPPER.moteur:
        print(MAINMAPPER.get_param("_st_obj_duppliques", 0), "objets dupliques")
    n_ecrits = MAINMAPPER.get_param("_st_wr_objs", 0)
    if n_ecrits:
        print(n_ecrits, "objets ecrits dans ", MAINMAPPER.get_param("_st_wr_fichs", 0), "fichiers ")
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
    from pyetl.outils.crypt import crypter, decrypt

    #    crypt = crypter
    #    decrypt = decrypt

    formats_connus_lecture = READERS
    formats_connus_ecriture = WRITERS
    #    reader = Reader

    def __init__(self, parent=None, nom=None, context=None):

        self.nompyetl = nom if nom else "pyetl"
        self.starttime = time.time()  # timer interne
        # variables d'instance (stockage des elements)
        self.maintimer = self._timer(init=True)
        self.statdefs = dict()  # description des statistiques
        self.stats = dict()  # stockage des statistiques
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
        #        self.parms = dict() #parametres ligne de commande et variables globales
        if context is None:
            context = parent.context if parent else None
        self.context = Context(parent=context,ident=str(self.idpyetl),type_c='P', root=True
        )
        # print ('initialisation', self.context, self.context.parent, "P" + str(self.idpyetl))
        self.context.root = self.context # on romp la chaine racine
        self.contextstack=[self.context]
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
        self.moteur = None
        # parametres de lancement

        # variables de stockage interne
        # commandes internes
        # strucutres de stockage partagees
        self.retour = []
        # description des fonctions statistiques (dictionnaire d'objets stats)
        # entree
        #        self.parametres_fichiers = dict() # paramteres d'acces
        self.schemas = dict()  # schemas des classes
        self.regles = list()  # regles de mapping
        self.regle_sortir = None
        self.racine = ''
        self.fichier_regles = None

        # etats

        self.dupcnt = 0
        self.statfilter = ""
        self.statprint = False
        self.statdest = None
        self.fichier_courant = ""
        self.chemin_courant = ""

        self.temps_fermeture = 0
        self.schemadef = False
        self.rdef = None

        # identification d'une reference a un champ  dans une expression
        #        self.liste_formats = [".ASC", ".SHP", ".CSV"]
        #        self.sortie_defaut = "asc"
        self.liste_regles = None

        self.liens_variables = dict()
        self.duree = 0
        # self.durees = dict()
        self.attlists = dict()
        # self.nb_obj = 0 # nombrte d'objets traites
        # self.parms["rep_regles"] = self.rdef
        # print ('_avant______________mode sortie' ,self.stream,self.get_param("mode_sortie"))

        self.ident_courant = ("", "")
        self._set_streammode()
        self.done = False


    def initenv(self, env=None, loginfo=None):
        """initialise le contexte (parametres de site environnement)"""
        if self.loginited:
            return  # on a deja fait le boulot
        env = env if env is not None else os.environ
        log_level="INFO"
        log_print="WARNING"
        if loginfo and not self.worker:
            log,log_level,log_print = loginfo
            self.set_param("logfile", log)
            self.set_param("log_level", log_level)
            self.set_param("log_print", log_print)

        initlogger(fichier=self.get_param("logfile",None),log=log_level,affich=log_print)
        self.init_environ(env)
        self.loginited=True

    #        self.aff = self._patience(0, 0) # on initialise le gestionnaire d'affichage
    #        next(self.aff)

    def initpyetl(self, commandes, args, env=None, loginfo=None):
        """ initialisation standardisee: cree l'objet pyetl de base"""

        self.initenv(env, loginfo)
        try:
            result = self.prepare_module(commandes, args)
        except SyntaxError as err:
            LOGGER.critical(
                "erreur script " + str(commandes) + " " + str(err) + " worker:" + str(self.worker)
            )
            result=False
        LOGGER.info('::'.join(("====== demarrage == ",self.nompyetl, str(self.idpyetl), repr(commandes), repr(args))))
        return result

    def init_environ(self, env=None):
        """initialise les variables d'environnement et les macros"""
        self.env = os.environ if env is None else env
        self.context.env = self.env
        if not os.path.isdir(self.paramdir):
            try:
                os.makedirs(self.paramdir)
            except PermissionError:
                pass
        self.site_params_def = env.get("PYETL_SITE_PARAMS", "")
        self.liste_params = None
        if self.parent is None:
            self._init_params()  # positionne les parametres predefinis
            self.macros = dict()
            self.site_params = dict()
            if self.site_params_def:
                self._charge_site_params(self.site_params_def)
                # charge les parametres de site (fichier ini)
            self._charge_site_params(self.paramdir)

            # charge les parametres individuels (fichier ini)
            self._paramdecrypter()  # decrypte les parametres cryptes

            self.charge_cmd_internes()  # macros internes
            self.charge_cmd_internes(site="macros", opt=1)  # macros de site
            self.charge_cmd_internes(
                direct=os.path.join(self.paramdir, "macros"), opt=1
            )  # macros perso
            #            self.charge_cmd_internes(site="macros") # macros internes
            self.sorties = GestionSorties()
            self.debug = int(self.get_param("debug"))

        else:
            self.macros = dict(self.parent.macros)
            self.site_params = self.parent.site_params
            self.sorties = self.parent.sorties

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
        nom = self.get_param("_sortie")

        if commande == "#help" or commande == "help":
            from pyetl.helpdef.helpmodule import print_help

            self.set_param("_sortie", "")
            print_help(self, nom)
            self.done = True

        elif commande == "#autotest" or commande == "autotest":
            #            print("detecte autotest ", self.fichier_regles, self.posparm)

            from pyetl.tests.testmodule import full_autotest

            liste_regles = full_autotest(self, pars[0] if pars else nom)
            self.set_param("_sortie", "")
            self.set_param("_testmode", "autotest")
            if not liste_regles:
                self.done = True
            else:
                self.fichier_regles = ""
                self.liste_regles = liste_regles
                # on a charge les commandes on neutralise l autotest

        elif commande == "#unittest" or commande == "unittest":
            from pyetl.tests.testmodule import unittests

            self.set_param("_sortie", "")
            self.set_param("_testmode", "unittest")
            print ('positionnement testmode',self.context)
            unittests(self, nom=nom, debug=self.get_param("debug"))
            self.done = True

        elif commande == "#formattest" or commande == "formattest":
            from pyetl.tests.testmodule import formattests

            self.set_param("_sortie", "")
            self.set_param("_testmode", "formattest")
            formattests(self, nom=nom, debug=self.get_param("debug"))
            self.done = True

    def _traite_params(self, liste_params):
        """gere la liste de parametres"""
        if liste_params is not None:
            self.liste_params = liste_params[:]
            for i in liste_params:
                self._stocke_param(i)  # decodage parametres de lancement
            #            print ('traite_param',len(self.posparm))
            if len(self.posparm) >= 2:
                self.set_param("_entree", self.posparm[0])
                self.set_param("_sortie", self.posparm[1])
            elif len(self.posparm) == 1:
                self.set_param("_sortie", self.posparm[0])

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
            self.get_param("_st_lu_objs", 0), self.get_param("_st_lu_fichs", 0))
        next(self.aff)

        LOGGER.debug(
            "prepare_module"
            + repr(regles)+"::"
            + repr(liste_params)+"::"
            + self.get_param("_sortie", "pas_de_sortie")
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
                    LOGGER.critical("erreur lecture " + repr(ker) + "(" + repr(regles) + ")")
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
                        print('erreur interpretation',i.numero, i, i.erreur)
                #                print("sortie en erreur", self.idpyetl)
                return False
        self.sorties.set_sortie(self.get_param("_sortie"))
        if not self.regles:
            #            print('pas de regles', self.done)
            if self.done:
                return True
            LOGGER.critical("pas de regles arret du traitement " + str(self.fichier_regles))
            return False

        self._set_streammode()
        try:
            self.compilateur(None, self.debug)
            self.regle_sortir = self.regles[-1]
            self.regle_sortir.declenchee = True
            self.moteur = Moteur(self, self.regles, self.debug)
            self.moteur.regle_debut = self.regles[0].numero
            #            print('preparation module',self.get_param('_entree'), '->', self.get_param('_sortie'))
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
        nbaffich = int(self.get_param("nbaffich"))
        #        print ('init_patience ',self.worker, self.get_param('_wid', -1))
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
            msg = " --%s----> nombre d'objets lus %8d dans %4d %s en %5d " + "secondes %5d o/s"
            if self.worker:
                msg = "worker%3s:" % self.get_param("_wid") + msg
            else:
                msg = "mapper   :" + msg
            LOGGER.info(' '.join(
                (msg,
                str(cmp),
                str(nbobj),
                str(tabletotal),
                str(ftype),
                str(int(duree)),
                str(int(nbobj / duree)),
                str(int((nbobj - nop) / (interv + 0.001))))),
            )
            if self.worker:
                if message == "interm":
                    tinterm = interm + interv
                    msg = " --int----> nombre d'objets lus %8d en %5d secondes: %5d o/s"
                    msg = "worker%3s:" % self.get_param("_wid") + msg
                    if interm > 1:
                        tinterm = interm + interv
                    else:  # on calcule un temps moyen pour pas afficher n'importe quoi
                        tinterm = nbval / (nbobj / duree)
                    print(msg % (nbval, int(tinterm), int((nbval) / tinterm)))
            else:
                print(msg % (cmp, nbobj, tabletotal+1, ftype, int(duree), int((nbobj) / duree)))
            return ((max(int(prochain / nbaffich), int(nbobj / nbaffich)) + 1) * nbaffich, tinterm)

        while True:
            message, nbfic, nbval = yield
            #            nbtotal += nbval
            if message == "init" :
                temps = self._timer(init=not self.worker)
                duree, interv = next(temps)
                interm = 0.001
                nb_total = 0
                prochain = nbaffich
                # print("init  : --------->",message, int(duree*1000), 'ms', interv)
            # elif message == "end":
            #     nbtotal += nbval
            #     #                tabletotal += nbfic
            #     # affiche(message, nbtotal)
            #     print(" fin d'affichage")
            #                raise GeneratorExit
            #                break
            elif nbtotal + nbval >= prochain:
                prochain, interm = affiche(message, nbtotal + nbval)
                #                if not self.worker:
                #                    print (self.get_param('_wid', -1), 'prochain', prochain)
                nop = nbtotal + nbval
            if message != "interm":
                nbtotal += nbval
                nbval = 0
                interm = 0.001
            # print ('actualisation nbtotal',message,  nbtotal,nbval,'->',nbtotal+nbval, prochain)
            tabletotal += nbfic


    def getpyetl(
        self, regles, entree=None, rep_sortie=None, liste_params=None, env=None, nom="", mode=None,
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
                petl.set_param("F_sortie", "#store")
                petl.set_param("force_schema", "0")
                rep_sortie = rep_sortie[1:]
                # print('getpyetl: format store',rep_sortie, regles)
            petl.set_param("_sortie", rep_sortie)
        if entree is not None:
            #            print ("entree getpyetl",type(entree))
            petl.set_param("_entree", entree)
        # print ('getpyetl entree:', petl.get_param('_entree'),'parent:', self.get_param('_entree'))
        if nom:
            petl.nompyetl = nom
        if petl.initpyetl(regles, liste_params, env=env):
            return petl
        print("erreur getpyetl", regles)
        return None

    def regmacro(self, nom, file="", liste_commandes=None, vpos=None):
        """enregistrement d'une macro"""
        nouvelle = Macro(nom, file=file, vpos=vpos)
        if liste_commandes is not None:
            nouvelle.commandes_macro = liste_commandes
        # if vpos is not None:
        #     nouvelle.vpos = vpos
        #print ('enrregistrement macro',nom, vpos, nouvelle.vpos)
        self.macros[nom] = nouvelle
        return nouvelle

    def _set_streammode(self):
        """positionne le mode de traitement"""
        self.stream = 1 if self.get_param("mode_sortie") == "C" else False
        if self.get_param("mode_sortie") == "D":
            self.stream = 2

#        print('---------pyetl : mode sortie', self.stream, self.get_param("mode_sortie"))

    def valide_ulist(self, val, master, grouplist):
        """ valide les autorisations par utilisateur"""
        if val and val.endswith(")#"):  # il y a des utilisateurs
            ddv = val.index("#(")
            if ddv:
                ulist = val[ddv + 2 : -2].split(",")
                ulist = [i.strip() for i in ulist]
                if "*" in ulist:
                    return val[:ddv]
                if master or self.username in ulist or any([i in ulist for i in grouplist]):
                    return val[:ddv]
                #                    print ('decode', ulist,val)
                else:
                    return None
        return val

    def _charge_site_params(self, origine):
        """ charge des definitions de variables liees au site """
        configfile = os.path.join(origine, "site_params.csv")
        if not os.path.isfile(configfile):
            print("pas de parametres locaux")
            return
        nom = ""
        #        print('parametres locaux', configfile)
        #        init = False
        for conf in open(configfile, "r").readlines():
            liste = (conf[:-1] + ";;").split(";")
            if liste and liste[0].startswith("!"):
                continue
            if liste and liste[0].strip() == "":
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

    def _paramdecrypter(self):  # decrypte les parametres cryptes
        """decrypte d'eventuels parametres cryptes
           gere 2 clefs une clef maitre et une clef utilisateur"""
        #        print ('decryptage parametres',self.parms['cryptokey'])
        localkey = "key_" + self.username  # clef par defaut
        masterkey = self.get_param("masterkey")

        userkey = self.get_param("userkey")
        #        userkeyref = self.get_param('userkey_ref')
        usergroup = self.get_param("usergroup")
        grouplist = []
        master = False
        if masterkey:
            masterkey = self.decrypt(masterkey, key=[localkey, ""])
            userkey = self.decrypt(userkey, key=[masterkey])
            if userkey:
                master = True
        #            print ('decodege master', masterkey,userkey, userkeyref)
        elif userkey:
            userkey = self.decrypt(userkey, key=[masterkey, localkey])
            #            print ('decodege user', userkey)

            grouplist = self.decrypt(usergroup, key=[localkey])
            if not grouplist:
                grouplist = []
            else:
                grouplist = grouplist.split(",")
        #        print ('clef', masterkey, 'master', master, 'user',userkey)
        supr = set()
        for nom in self.site_params:
            for numero, parametre in enumerate(self.site_params[nom]):
                nom_p, val = parametre
                if nom_p.startswith("**"):  # cryptage
                    nom_p = nom_p[2:]
                    val2 = self.decrypt(val, key=[masterkey, userkey])
                    #                    print ('decryptage ', nom, nom_p, val2)
                    val = self.valide_ulist(val2, master, grouplist)
                    #                    print ("valide", val)
                    #                    val = val2
                    if val is None:
                        supr.add(nom)
                    else:
                        self.site_params[nom][numero] = (nom_p, val)
        for nom in supr:
            # print("suppression paramgroup", nom)
            del self.site_params[nom]

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
                val,_ = context.resolve(val)  # on fait du remplacement à la volee
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
        macro =None
        configfile = os.path.join(
            os.path.dirname(__file__), "moteur/fonctions/commandes_internes.csv"
        )
        if test:
            testrep = self.get_param("_test_path")
            configfile = os.path.join(testrep, str(test) + ".csv")
        if site:
            #            print("chargement parametres de site", self.nompyetl,
            #                  self.site_params_def, site)
            configfile = os.path.join(self.site_params_def, site + ".csv")
        if direct:
            configfile = direct + ".csv"
        nom = ""
        num = 0
        if not os.path.isfile(configfile):
            if not opt:
                print("fichier de config", configfile, "introuvable")
            return
        for conf in open(configfile, "r").readlines():
            num += 1
            if not conf or conf.startswith("!"):
                continue
            liste = conf.split(";")
            if conf.startswith("&&#define"):
                nom = liste[1]
                vpos = [i for i in liste[2:] if i]
                macro = self.regmacro(nom, file=configfile, vpos=vpos)
                continue
            if macro:
                macro.add_command(conf, num)

    def charge_macros_bd(self):
        """charge des macros depuis la base de donnees definie dans les paramettres de site"""
        if self.get_param("dbmacro") != "oui":
            return
        # on charge la structure des tables

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
                ("debug", "0"),
                ("fstat", ""),
                ("force_schema", "util"),
                ("epsg", "3948"),
                ("_pv", ";"),
                ("F_sortie", ""),
                ("xmldefaultheader", '<?xml-stylesheet href="xsl/dico.xsl" type="text/xsl"?>'),
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


    def getcontext(self, context, ident="",ref=False, type_c='C'):
        """recupere un contexte en cascade"""
        context = self.cur_context if context is None else context
        return context.getcontext(ident=ident,ref=ref,type_c=type_c)

    def pushcontext(self,context=None, ident='',type_c='C'):
        self.contextstack.append(context or self.getcontext(context, ident,type_c))
        # print("apres push",self.contextstack)
        return self.cur_context

    def popcontext(self,typecheck=None):
        # print("avant pop",self.contextstack)
        if typecheck and self.cur_context.type_c == typecheck:
            self.contextstack.pop()
        else:
            print ('=========================popcontext warning typecheck attendu',typecheck,'trouve',self.cur_context.type_c)
        return self.cur_context

    @property
    def cur_context(self):
        return self.contextstack[-1]


    def get_param(self, nom, defaut=""):
        """recupere la valeur d une varible depuis le contexte"""
        return self.context.getvar(nom, defaut)

    def set_param(self, nom, valeur):
        """positionne une variable dans un contexte de base
           dans ce cas on positionne en local"""
        # print ('set_param:',self.context, nom,valeur)
        self.context.setlocal(nom, valeur)

    def set_param_parent(self, nom, valeur):
        """positionne une variable dans un contexte de base
           dans ce cas on positionne dans le contexte parent"""
        if self.parent:
            self.parent.set_param(nom, valeur)
        else:
            self.set_param(nom, valeur)

    def padd(self, nom, valeur):
        """incremente un parametre d'une valeur"""
        # vinit = self.context.getvar(nom, 0)
        self.set_param(nom, self.context.getvar(nom, 0) + valeur)

    #        print ('padd',nom,self.get_param(nom, 0, local=parent))

    def pasum(self, nom1, nom2):
        """incremente un parametre d'un autre parametre"""
        vinit = self.get_param(nom1, 0)
        valeur = self.get_param(nom2, 0)
        self.set_param(nom1, str(vinit + valeur))

    def _stocke_param(self, parametre):
        """stockage d'un parametre"""
        if "=" in parametre:
            valeur = parametre.split("=", 1)
            if len(valeur) < 2:
                valeur.append("")
            if valeur[1] == '""':
                valeur[1] = ""
            #            self.parms[valeur[0]] = valeur[1]
            self.set_param(*valeur)
            # print("stockage parametre:",parametre,valeur[0])
        else:
            self.posparm.append(parametre)
            #            self.parms["#P_"+str(len(self.posparm))] = parametre
            self.set_param("#P_" + str(len(self.posparm)), parametre)

    def set_abrev(self, nom_schema, dic_abrev=None):
        """cree les abreviations pour la definition automatique de snoms courts"""
        if dic_abrev is None:
            dic_abrev = self.get_param("abreviations")
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
            for i in open(fichier, "r", encoding=self.get_param("codec_entree", "utf-8")):
                liste = i[:-1].split(";")
                stock[liste[clef].strip()] = liste
        else:
            print("erreur:pyetl: fichier jointure introuvable :", fichier)

        self.jointabs[ident_fich] = stock

    #        print("charge: prechargement",fichier, ident_fich, stock)

    def _prep_chemins(self, chemin: str, nom:str)-> str:
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
        return self.jointabs[fichier].get(clef.strip(), ["" for i in range(champ + 1)])[champ]

    def jointure_s(self, fichier, clef, champ):
        """jointure statique chemin absolu ou relatif au repertoire de regles"""
        cle = clef.strip()
        #        print ('dans jointure ', self.jointabs)
        try:
            return self.jointabs[fichier][cle][champ]
        except KeyError:
            if self.debug:
                print("pyetl: jointure statique clef non trouvee ", fichier, clef, champ)
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
        entree = None if self.get_param("sans_entree") else self.get_param("_entree", None)
        self.macro_entree()
        entree = None if self.get_param("sans_entree") else self.get_param("_entree", None)
        # if self.done:
        #     try:
        #         self.menage_final()
        #     except StopIteration:
        #         self._finalise_sorties()
        #     return


        # print("process E:",entree,'S:',self.get_param("sortie"),'regles', self.regles)
        if self.done:
            pass
        elif isinstance(entree, (Stat, ExtStat)):
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
                for fich , parms in scan_entree_2(
                    rep=entree,
                    force_format=self.get_param("F_entree"),
                    fileselect=self.get_param("fileselect"),
                    dirselect=self.get_param("dirselect"),
                    filtre_entree=self.get_param("filtre_entree"),
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
                print("!!!!!!!!!!!!!!!!!!!!!attention repertoire d'entree inexistant:", err)
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
        LOGGER.info('::'.join(("====== fin == ",self.nompyetl, str(self.idpyetl), str(self.get_param("_st_lu_objs", '0')))))
        return

    def menage_final(self):
        """vidage de tous les tuyaux et stats finales"""

        stock = True

        while stock:
            stock = False
            for regle in self.regles:
                if regle.store and regle.nbstock:
                    #                    print ('--------menage_final ', regle, regle.nbstock)
                    stock = True
                    regle.traite_stock(regle)

        self.debug = 0
        # self._finalise_sorties()
        self._ecriture_schemas()
        self._ecriture_stats()
        self._finalise_sorties() # on ne finalise les sorties que la pour tenir compte des traitements eventuels de schemas
        self.macro_final()
        return

    def macrorunner(self, texte, parametres=None, entree=None, sortie=None, retour=None):
        '''execute une macro (initiale ou finale)'''
        regles = [(1,texte if texte.startswith('<') else '<'+texte)]
        processor = self.getpyetl(regles, liste_params=parametres, entree=entree, rep_sortie=sortie)
        #        print('parametres macro', processor.nompyetl, [(i,processor.get_param(i))
        #                                                       for i in macro.vpos])
        if processor is not None:
            processor.process()
            print("macro effectuee", texte, self.idpyetl, "->", processor.idpyetl)
            if retour:
                return {i:processor.get_param(i) for i in retour}
        return


    def macro_final(self):
        """ execute une macro finale"""
        if (self.worker and self.parent is None):
            macrofinale = self.context.getlocal("_w_end")
        else:
            macrofinale = self.context.getlocal("_end") or self.context.getlocal("#end")
        if not macrofinale:
            return
        parametres = self.get_param("parametres_final")
        entree = self.get_param("entree_final", self.get_param("_sortie"))
        sortie = self.get_param("sortie_final", self.get_param("_sortie"))
        self.macrorunner(macrofinale, parametres, entree, sortie)
        return

    def macro_entree(self):
        """ execute une macro de demarrage"""

        if (self.worker and self.parent is None):
            macroinit = self.context.getlocal("_w_start")
        else:
            macroinit = self.context.getlocal("_start") or self.context.getlocal("#start")
        if not macroinit:
            # print ('pas de macro initiale')
            return
        print ('macro initiale', macroinit)
        parametres = self.get_param("parametres_initial")
        entree = self.get_param("entree_initial", self.get_param("_entree"))
        sortie = self.get_param("sortie_initial", self.get_param("_entree"))
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
        rep_sortie = self.get_param("sortie_schema", self.get_param("_sortie"))
        # print("sortie schema:contexte",self.context, self.worker,self.get_param("_testmode"), self.get_param('test_courant'))
        if rep_sortie == "-" or not rep_sortie:  # pas de sortie on ecrit pas
            if not self.get_param("_testmode"):  # en mode test on rale pas
                print("schema:pas de repertoire de sortie")
            return
        mode_schema = self.get_param("force_schema", "util")
        mode_schema = modes_schema_num.get(mode_schema, mode_schema)
        LOGGER.info("ecriture schemas " + str(mode_schema))
        if mode_schema in {"all", "int", "fusion"} and not self.done:
            #            print('pyetl: traitement virtuel ', mode_schema)
            self.moteur.traitement_virtuel()  # on force un peu pour creer toutes les classes
        #        print('pyetl: ecriture schemas ', mode_schema)
        ecrire_schemas(
            self, rep_sortie, mode_schema, formats=self.get_param("format_schema", "csv")
        )

    def _ecriture_stats(self):
        """stockage des stats """
        #        print("pyetl : stats a ecrire",self.idpyetl, self.stats.keys(), self.statprint)
        rep_sortie = os.path.join(self.get_param("_sortie"), self.get_param("sortie_stats"))

        for i in self.stats:
            if self.worker and self.parent is None:
                continue  # on ecrit pas on remonte
            if self.statprint == "statprocess":
                petl2 = self.getpyetl(self.statfilter, entree=self.stats[i])
                #                print ("petl2 statprocess",petl2.idpyetl,petl2.stats)
                if petl2 is not None:
                    petl2.process()
                    retour = petl2.retour
                    #                    print("retour statprocess", retour)
                    self.retour.extend(retour)
            #                    print("retour complet", self.retour)
            else:
                dest = self.statdest if self.statdest else rep_sortie
                statdef = self.get_param("stat_defaut")
                codec_sortie = self.get_param("codec_sortie", "utf-8")
                self.stats[i].ecrire(
                    dest,
                    self.statprint,
                    self.statfilter,
                    statdef,
                    codec=codec_sortie,
                    wid=self.get_param("_wid", ""),
                )

        if self.get_param("fstat"):  # ecriture de statistiques de fichier
            if self.worker and self.parent is None:
                return  # on ecrit pas on remonte
            liste_fich = self.sorties.getstats()
            if not liste_fich:
                return
            if rep_sortie:
                if self.worker:
                    fstat = os.path.join(
                        rep_sortie, self.get_param("fstat") + "_" + self.get_param("_wid") + ".csv"
                    )
                else:
                    fstat = os.path.join(rep_sortie, self.get_param("fstat") + ".csv")
                print("pyetl : info ecriture stat fichier ", fstat, "\n".join(liste_fich))
                os.makedirs(os.path.dirname(fstat), exist_ok=True)
                fichier = open(fstat, "w", encoding=self.get_param("codec_sortie", "utf-8"))
                fichier.write("repertoire;nom;nombre\n")
                for i in sorted(liste_fich):
                    fichier.write(
                        ";".join((os.path.dirname(i), os.path.basename(i), str(liste_fich[i])))
                        + "\n"
                    )
                fichier.close()
            else:
                print("%-60s | %10s |" % ("           nom", "nombre   "))
                for i in sorted(liste_fich):
                    print("%-60s | %10d |" % (i, liste_fich[i]))
        # on ferme proprement ce qui est ouvert

    def signale_fin(self):
        """ecrit un fichier pour signaler la fin du traitement"""
        if self.worker or self.parent or self.get_param("job_control","no") == "no":
            return
        print("info: pyetl:job_control", self.get_param("job_control"))
        open(self.get_param("job_control"), "w").write("fin mapper\n")


    def lecture(self, fich, regle=None, reglenum=None, parms: [str]=None):
        """ lecture d'un fichier d'entree"""
        if parms is not None:
            racine, chemin, fichier, ext = parms
        else: # on invente
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
        regle = self.regles[reglenum] if regle is None and reglenum is not None else regle
        # print('pyetl:lecture ', fich, self.racine, chemin, fichier, ext,'->', regle)
        reglestart = regle.branchements.brch["next"] if regle else self.regles[0]
        # print ('--------------------appel lecture ',fichier, regle, '->', reglestart)
        if regle is None:
            regle=reglestart
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
        if self.worker: # en mode worker on ne compte que les intermediaires
            self.aff.send(("init",0,0)) # on reinitialise le compteur
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
