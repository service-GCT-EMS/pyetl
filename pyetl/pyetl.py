# -*- coding: utf-8 -*-
"""modification d'attributs en fonction d'un fichier de parametrage avec
prise en charge des expressions regulieres"""
import time

printtime = False
if printtime:
    t1 = time.time()
    print("pyetl start import ")
import os
import re
import io
import itertools
from queue import Empty
from .vglobales import VERSION, set_mainmapper, getmainmapper, DEFCODEC
from .outils.commandes_speciales import is_special, commandes_speciales
from .outils import gestion_logs as L

if printtime:
    print("globales", time.time() - t1)
    t1 = time.time()
from .formats.generic_io import (
    READERS,
    WRITERS,
    Reader,
    Output,
    get_converter,
    get_geomstructure,
)

if printtime:
    print("formats    ", time.time() - t1)
    t1 = time.time()
from .formats.mdbaccess import dbaccess

if printtime:
    print("databases", time.time() - t1)
    t1 = time.time()

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
from .moteur.fonctions import COMMANDES, CONDITIONS, MODULES, loadmodules
from .moteur.fonctions.outils import scan_entree
from .moteur.fonctions.traitement_crypt import paramdecrypter

if printtime:
    print("commandes", time.time() - t1)
    t1 = time.time()


from .schema.schema_interne import init_schema  # schemas
from .schema.schema_io import ecrire_schemas, lire_schemas_multiples

# integre_schemas # schemas
from .moteur.fonctions.parallel import setparallel

# MODULEDEBUG = False

def cremapper():
    """on cree l'objet parent et l'executeur principal"""
    mapper = Pyetl()
    # mapper.initpyetl("#init_mp", [])
    mapper.ismainmapper = True
    return set_mainmapper(mapper)



def runpyetl(commandes, args):
    """lancement standardise c'est la fonction appelee au debut du programme"""
    mainmapper = getmainmapper()
    if not mainmapper:
        mainmapper=cremapper()
    if not is_special(commandes):
        loginfo = L.getlog(args)
        for i, v in loginfo.items():
            mainmapper.setvar(i, v)
        mainmapper.initlog()
        mainmapper.logger.log(999, "demarrage pyetl %s", VERSION)
        mainmapper.logger.info("commande:   %s", str(commandes))
        if args:
            mainmapper.logger.info("parametres: %s", str(args))
    else:
        commandes_speciales(mainmapper, commandes, args)
        # mainmapper.gestion_log.shutdown()
        return
    mapper = mainmapper.getpyetl(commandes, liste_params=args)
    if mapper:
        mapper.process()
    else:
        mainmapper.logger.error("demarrage impossible")
        return
    wstats = mapper.get_work_stats()
    if wstats["obj_lus"]:
        if wstats["fich_lus"]:
            mapper.logger.log(
                999,
                "%d objets lus dans %d fichiers",
                wstats["obj_lus"],
                wstats["fich_lus"],
            )
        if wstats["tabl_lus"] != 0:
            mapper.logger.log(
                999,
                "%d objets lus dans %d tables",
                wstats["obj_lus"],
                wstats["tabl_lus"],
            )
    if wstats["obj_dupp"]:
        mapper.logger.log(999, "%d objets dupliques", wstats["obj_dupp"])
    if wstats["obj_ecrits"]:
        mapper.logger.log(
            999,
            "%d objets ecrits dans %d fichiers",
            wstats["obj_ecrits"],
            wstats["fich_ecrits"],
        )
    mapper.signale_fin()
    mapper.logger.log(
        999, "temps de traitement total: %d millisecondes", int(wstats["duree"] * 1000)
    )

    if wstats["obj_lus"]:
        mapper.logger.log(999, "perf lecture : %d o/s ", int(wstats["perf_r"]))
    if wstats["obj_ecrits"]:
        mapper.logger.log(999, "perf ecriture : %d o/s ", int(wstats["perf_w"]))

    mainmapper.gestion_log.shutdown()


# ---------------debut programme ---------------


class Pyetl(object):
    """structure parent : instanciee une fois pour un traitement
    permet le stockage de tous les parametres globaux du traitement.
    cette structrure est passee a l'ensemble des modules"""

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
    conditions = CONDITIONS
    modules = MODULES

    sortedconds = sorted(conditions.values(), key=lambda x: x.priorite)
    reconfig = reinterprete_regle
    formats_connus_lecture = READERS
    formats_connus_ecriture = WRITERS
    defautcsvencoding = "cp1252"

    def __init__(self, parent=None, nom=None, context=None, env=None, mode="cmd"):

        self.starttime = time.time()  # timer interne
        # variables d'instance (stockage des elements)
        self.mode = mode
        self.maintimer = self._timer(init=True)
        self.statstore = Statstore(self)
        self.cntr = dict()  # stockage des compteurs
        self.idpyetl = next(self._ido)
        # jointures
        self.nompyetl = nom if nom else "pyetl_" + str(self.idpyetl)
        self.jointabs = dict()  # clefs de jointure
        self.joint_fich = dict()  # fichier externes de jointure
        self.jointdef = dict()  # definition des champs
        self.posparm = list()
        self.store = dict()
        self.webstore = dict()
        self.keystore = dict()
        self.dbconnect = dict()  # connections de base de donnees
        self.namedselectors = dict()
        self.msgqueue = None
        self.parent = parent  # permet un appel en cascade
        # selecteurs nommes pour des selections multibases complexes
        self.initcontext(context)

        self.username = os.getlogin()
        self.userdir = os.path.expanduser("~")
        self.paramdir = os.path.join(self.userdir, ".pyetl")
        self.ismainmapper = False

        setparallel(self)  # initialise la gestion du parallelisme
        self.ended = False
        self.is_special = False
        self.worker = parent.worker if parent else False  # process esclave
        self.stream = 0
        self.debug = 0
        #        self.stock = False # pas de stockage
        self.gestion_log = parent.gestion_log if parent else L.GestionLogs(self)
        self.logger = self.gestion_log.logger
        # parametres globaux ressources
        self.init_environ(env=env)
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
        self.refs = []
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

        self._set_streammode()
        self.done = False
        self.inited = False
        self.webworkers = dict()
        self.webmaxworkers = 10
        self.lasttime = None
        self.webnbexec = 0
        self.variables_speciales = {"log_file", "log_level"}
        self.scan_entree = scan_entree

    def getcommande(self, commande):
        fonc = self.commandes.get(commande)
        if isinstance(fonc, str):
            result = loadmodules(fonc)
            if not result:
                print("module de commandes non disponible ", commande, fonc)
                return None
            fonc = self.commandes.get(commande)
            if isinstance(fonc, str):
                print("erreur chargement commande", commande, fonc)
                return None
        return fonc

    def getmoteur(self):
        return Moteur(self)

    def settime(self):
        self.lasttime=time.time()

    def getoldest(self):
        nom=None
        for n,w in self.webworkers.items():
            if not nom:
                nom,temps=n,w.lasttime 
            elif w.lasttime<temps:
                nom,temps=n,w.lasttime 
        return nom

    def cleanoldest(self):
        nom = self.getoldest()
        if nom:
            del self.webworkers[nom]


    def _relpath(self, path):
        """cree un chemin relatif par rapport au fichier de programme"""
        if path is None:
            return None
        return os.path.join(os.path.dirname(__file__), path)

    def initlog(self, force=False):
        self.gestion_log.initlog(self, force)
        """initialise le contexte de logging (parametres de site environnement)"""

    def initcontext(self, context=None):
        """initialise les contextes"""
        if context is None:
            context = self.parent.context if self.parent else None
        self.context = Context(
            parent=context, ident=str(self.idpyetl), type_c="P", root=True
        )
        self.context.root = self.context  # on romp la chaine racine
        self.contextstack = [self.context]

    def initpyetl(self, commandes, args):
        """initialisation standardisee: cree l'objet pyetl de base"""
        if not self.inited:
            self.initlog()
        try:
            result = self.prepare_module(commandes, args)
            self.inited = True
        except SyntaxError as err:

            if self.worker:
                self.logger.exception(
                    "worker:%s erreur script %s",
                    os.getpid(),
                    repr(commandes),
                    exc_info=err,
                )
            else:
                self.logger.exception("erreur script %s", repr(commandes), exc_info=err)
            result = False

        self.logger.debug(
            "demarrage %s %s \n %s %s",
            self.nompyetl,
            str(self.idpyetl),
            repr(commandes),
            repr(args),
        )
        # print("result initialisation", result)
        return result

    def init_environ(self, env=None):
        """initialise les variables d'environnement et les macros"""
        # print("initenv", env)
        if env is None:
            if self.parent:
                self.env = self.parent.env
            else:
                self.env = os.environ
                self.context.setenv(self.env)

        elif env == "noenv":
            self.env = dict()
            self.context.setenv(None)
        else:
            self.env = env
            self.context.setenv(self.env)
        if not os.path.isdir(self.paramdir):
            try:
                os.makedirs(self.paramdir)
            except PermissionError:
                self.paramdir = ""
        self.site_params_def = self.env.get("PYETL_SITE_PARAMS", "")
        self.liste_params = None
        if self.parent is None:
            self._init_params()  # positionne les parametres predefinis
            self.macrostore = MacroStore()
            self.site_params = dict()
            # charge les parametres de site (fichier ini)
            self._charge_site_params(self.site_params_def)
            if self.getvar("_paramperso") != "noparam":
                self._charge_site_params(self.paramdir)
            print ("traitement masterkey",self.getvar("nomaster"),self.istrue("nomaster")),
            if self.istrue("nomaster"):
                self.setvar("masterkey","")
                print ("suppression masterkey", self.getvar("masterkey"))
                
            cryptinfo = (
                os.getlogin(),
                self.getvar("usergroup"),
                self.getvar("masterkey"),
                self.getvar("userkey"),
                self.getvar("cryptolevel"),
                self.getvar("cryptohelper"),
            )
            paramdecrypter(self.site_params, cryptinfo)
            self.charge_cmd_internes()  # macros internes
            self.charge_cmd_internes(site="macros", opt=1)  # macros de site
            if self.paramdir is not None:
                self.charge_cmd_internes(
                    direct=os.path.join(self.paramdir, "macros"), opt=1
                )  # macros perso
            self.sorties = GestionSorties(rep_sortie=self.getvar("_sortie"))
            self.debug = int(self.getvar("debug", 0))
            self.setvar("paramgroups", list(self.site_params.keys()))

        else:
            self.macrostore = MacroStore(self.parent.macrostore)
            # self.macros = dict(self.parent.macros)
            self.site_params = self.parent.site_params
            self.sorties = self.parent.sorties
            self.fonctions = self.parent.fonctions
            self.dbconnect=self.parent.dbconnect

    def traite_variables_speciales(self, nom):
        if nom == "log_file" or nom == "log_level":
            # print("-------------------initlog")
            self.initlog(force=True)

    def getmacro(self, nom):
        """recupere une macro par son nom"""
        return self.macrostore.getmacro(nom)

    def getmacros(self):
        """recupere les macros"""
        return self.macrostore.getmacros()

    def stocke_macro(self, description, origine):
        return self.macrostore.stocke_macro(description, origine)

    def getmacrolist(self):
        """recupere un iterateur sur les macros"""
        return self.macrostore.getmacrolist()

    def renamemacro(self, nom1, nom2):
        self.macrostore.rename(nom1, nom2)

    @property
    def macro(self):
        return self.macrostore.macros

    def specialenv(self, params, macros):
        """lit un bloc de parametres et de macros specifiques"""
        if params:
            self._charge_site_params(params)
        if macros:
            self.charge_cmd_internes(direct=macros)

    def _traite_params(self, liste_params):
        """gere la liste de parametres"""
        if liste_params is not None:
            if isinstance(liste_params, dict):
                for i, j in liste_params.items():
                    self.setvar(i, j)
                return
            self.liste_params = liste_params[:]
            for i in liste_params:
                # print("stocke_param", i)
                self._stocke_param(i)  # decodage parametres de lancement
            #            print ('traite_param',len(self.posparm))
            if len(self.posparm) >= 2:
                self.setvar("_entree", self.posparm[0])
                self.setvar("_sortie", self.posparm[1])
            elif len(self.posparm) == 1:
                self.setvar("_sortie", self.posparm[0])

    def prepare_module(self, regles, liste_params):
        """prepare le module pyetl pour l'execution"""
        # print("dans prepare_module", regles, liste_params)
        if self.inited:
            # on nettoie
            self.liste_regles = None
            self.fichier_regles = None
            self.done = False
            self.regles = []
            self.moteur = Moteur(self)
            self.initcontext()
            # self.initlog()
            for i in list(self.schemas.keys()):
                if not i.startswith("#"):
                    del self.schemas[i]
        else:
            # on initialise le gestionnaire d'affichage
            self.aff = self._patience(
                self.getvar("_st_lu_objs", 0),
                self.getvar("_st_lu_fichs", 0),
                mode=self.mode,
            )
            next(self.aff)
        # print("dans prepare_module", len(regles), regles)
        self.appel = repr(regles)
        if isinstance(regles, list):
            self.liste_regles = regles
        else:
            self.fichier_regles = regles
            self.rdef = os.path.dirname(regles)  # nom de repertoire des regles
        self._traite_params(liste_params)

        self.logger.debug(
            "prepare_module %s :: %s :: %s",
            (repr(regles), repr(liste_params), self.getvar("_sortie", "pas_de_sortie")),
        )
        erreurs = None
        # print("dans prepare_module2", self.fichier_regles, self.done)
        if self.fichier_regles or self.liste_regles:
            # if not self.done:
            try:
                # print("appel lecteur")
                erreurs = self.lecteur_regles(
                    self.fichier_regles, liste_regles=self.liste_regles
                )
                # print("retour lecteur", erreurs)
            except KeyError as ker:
                self.logger.critical(
                    "====erreur lecture %s (%s)", repr(ker), repr(regles)
                )
                erreurs = erreurs + 1 if erreurs else 1
                # raise

            if erreurs:
                message = " erreur" if erreurs == 1 else " erreurs"
                self.logger.critical(
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
                        self.logger.error(
                            "erreur interpretation %d: %s -> %s",
                            i.numero,
                            repr(i),
                            str(i.erreurs),
                        )
                        # print("erreur interpretation", i.numero, i, i.erreur)
                #                print("sortie en erreur", self.idpyetl)
                return False
        self.sorties.set_sortie(self.getvar("_sortie"))
        if not self.regles:
            # print("prepare_module pas de regles", self.done, list(self.schemas.keys()))
            if self.done:
                return True
            self.logger.critical(
                "pas de regles arret du traitement " + str(self.fichier_regles)
            )
            return False

        self._set_streammode()
        try:
            self.compilateur(self.regles, self.debug)
            self.regle_sortir = self.regles[-1]
            self.regle_sortir.declenchee = True
            self.moteur.setregles(self.regles, self.debug)
            self.moteur.regle_debut = self.regles[0].numero
            # print("fin prepare", len(self.regles), len(self.moteur.regles))
            if self.getvar("showrules"):
                self.showrules(self.regles)

            return True
        # on refait si des choses ont change a l'initialisation
        except EOFError:
            self.logger.critical("pas de fichier de regles arret du traitement ")
            #            print("erreurs de compilation arret du traitement ")
            return False

    def showrules(self, liste_regles):
        for r in liste_regles:
            print(r)
            if r.liste_regles:
                self.showrules(r.liste_regles)

    def _timer(self, init=True):
        """acces au temps pour les calculs de duree."""
        heure_debut = self.starttime if init else time.time()
        intermediaire = 0
        prec = heure_debut
        while True:
            yield (time.time() - heure_debut, intermediaire)
            intermediaire = time.time() - prec
            prec = time.time()

    def _patience(self, nbfic, nbval, mode="cmd"):
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
        nbexp = 0
        expfics = 0
        wid = self.getvar("_wid")
        mainmapper = getmainmapper()
        nbvals = dict()

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
            elif message == "tab":
                ftype = "tables"

            msg = (
                " mapper   :--%s----> nombre d'objets lus %8d dans %4d %s en %5d "
                + "secondes %5d o/s"
            )
            if nbexp:
                msg = msg + " (exportes:" + str(nbexp) + ":" + str(expfics) + ")"
            if not self.worker:
                ligne = msg % (
                    cmp,
                    nbobj,
                    tabletotal + 1,
                    ftype,
                    int(duree),
                    int((nbobj) / duree),
                )
                if mode == "cmd":
                    self.logger.info(ligne)
                    # if nbexp:
                    #     print("exporte:", nbexp)
                    # print("message recu", ligne)
            return (
                (max(int(prochain / nbaffich), int(nbobj / nbaffich)) + 1) * nbaffich,
                tinterm,
            )

        while True:
            message, nbfic, nbval = yield
            #            nbtotal += nbval
            if message == "check" and not self.worker:
                # print("check queue", self.getvar("_wid"), mainmapper.msgqueue)
                if mainmapper.msgqueue:
                    while True:
                        try:
                            msg = mainmapper.msgqueue.get(block=False)
                            message, nbfic, w_nbval, wid = msg
                            if message == "interm":
                                nbvals[wid] = w_nbval
                                nbval = sum(nbvals.values())
                                if nbval >= prochain:
                                    prochain, interm = affiche(message, nbval)
                                # print("-main:------------------retour queue", msg, nbvals)
                            elif message == "fich":
                                # print("message fich", nbfic, w_nbval, wid, nbtotal)
                                message=''
                                tabletotal += nbfic
                                nbfic = 0
                            elif message == "exp":
                                message=''
                                nbexp = sum(nbvals.values())
                                # print("patience: recu exp", nbfic, nbval, nbexp)
                        except Empty:
                            # print("queue vide")
                            break
                        except BrokenPipeError:
                            print("lecture : queue inexistante")
                            break

            if message == "init":
                temps = self._timer(init=not self.worker)
                duree, interv = next(temps)
                interm = 0.001
                nbtotal = 0
                # print("message init", wid)
                prochain = nbaffich
            elif self.worker:
                try:
                    self.msgqueue.put((message, nbfic, nbval, wid))
                except (BrokenPipeError):
                    print("ecriture: queue inexistante")

                # print(" worker : ecriture queue", (message, nbfic, nbval, wid))
            elif nbval >= prochain:
                prochain, interm = affiche(message, nbval)

                nop = nbval

            if message == "fich":
                # print("message fich", nbfic,  nbtotal, nbval, tabletotal)
                nbtotal += nbval
                interm = 0.001
                tabletotal += nbfic

            if message == "exp":
                nbexp += nbval
                expfics += nbfic

    def getpyetl(
        self,
        regles,
        entree=None,
        rep_sortie=None,
        liste_params=None,
        nom="",
        mode="cmd",
    ):
        """retourne une instance de pyetl sert pour les tests et le
        fonctionnement en fcgi et en mode batch ou parallele"""
        # print("getpyetl ", regles, liste_params)
        # print(
        #     "---------------------------- dans getpyetl",
        #     nom,
        #     mode,
        #     rep_sortie,
        #     len(self.webworkers),
        #     self.webworkers.keys(),
        # )

        if not regles:
            if mode == "web" and nom in self.webworkers:
                return self.webworkers[nom]
            if mode is None:
                self.logger.critical("getpyetl:mode non defini")
                # print("getpyetl:mode non defini")
                return None

        if mode.startswith("web"):

            if nom in self.webworkers:
                petl = self.webworkers[nom]
                self.settime()
            else:
                if len(self.webworkers) > self.webmaxworkers:
                    self.cleanoldest()
                petl = Pyetl(parent=self, nom=nom)
                self.webworkers[petl.nompyetl] = petl
        else:
            petl = Pyetl(parent=self)

        petl.setvar("pyetl_script_ref", str(regles))
        if rep_sortie is not None:
            petl.setvar("sans_sortie", "")
            if rep_sortie.startswith("#"):
                petl.setvar("F_sortie", "#store")
                petl.setvar("force_schema", "0")
                rep_sortie = rep_sortie[1:]
                # print("----------------getpyetl: format store", rep_sortie, regles)
            petl.setvar("_sortie", rep_sortie)
        if entree is not None:
            #            print ("entree getpyetl",type(entree))
            petl.setvar("_entree", entree)
        # print ('getpyetl entree:', petl.getvar('_entree'),'parent:', self.getvar('_entree'))
        if nom:
            petl.nompyetl = nom
        petl.mode = mode
        # print("appel initpyetl", petl.inited, petl.mode, petl.done)
        if petl.initpyetl(regles, liste_params):
            # print("apres initpyetl:", petl.inited, petl.mode, petl.done, petl.regles)

            return petl
        self.logger.critical("erreur getpyetl %s", str(regles))
        # print("erreur getpyetl", regles)
        return None

    def _set_streammode(self):
        """positionne le mode de traitement"""
        self.stream = 1 if self.getvar("mode_sortie") == "C" else False
        if self.getvar("mode_sortie") == "D":
            self.stream = 2

    #        print('---------pyetl : mode sortie', self.stream, self.getvar("mode_sortie"))

    
    def _charge_site_params(self, origine):
        """charge des definitions de variables liees au site"""
        if not origine:  # localisation non definie
            return
        configfile = (
            origine
            if origine.endswith(".csv")
            else os.path.join(origine, "site_params.csv")
        )
        # c est un fichier:
        # configfile = os.path.join(origine, "site_params.csv")
        if not os.path.isfile(configfile):
            self.logger.warning("pas de parametres locaux %s", configfile)
            # print("pas de parametres locaux", configfile)
            return
        nom = ""
        # print("parametres locaux", configfile)
        #        init = False
        for conf in open(configfile, "r", encoding=self.defautcsvencoding).readlines():
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
            elif liste and liste[0].strip() == "&&#include":  # on charge un fichier
                nom = liste[1]
                self._charge_site_params(nom)
            else:
                if nom:
                    nom_p, val = liste[0], liste[1]
                    self.site_params[nom].append((nom_p, val))
        #                    self.site_params[nom].append((liste[0]+'_'+nom, liste[1]))
        self.load_paramgroup("init", fin=False)
        # print("parametres:", self.site_params.keys())

    #        print("parametres de site",origine)
    #        print("variables",self.parms)

    def load_paramgroup(self, clef, nom="", check="", fin=True, context=None):
        """charge un groupe de parametres"""
        # print("chargement", clef, self.site_params[clef], context)

        if not clef or clef == "*":
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
            context.setvar("_paramgroup", clef)
            return True
        elif fin:
            print("definition parametres de site >" + str(clef) + "< introuvable")
            print("aide:groupes connus: ")
            print("\n".join([str(i) for i in sorted(self.site_params)]))
            raise KeyError
        return False

    def charge_cmd_internes(self, test=None, site=None, direct=None, opt=0):
        """charge un ensemble de macros utilisables directement"""
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
        self.fonctions = dict()
        self.fonctions["#time"] = time.time
        self.fonctions["#seconds"] = lambda: int(time.time())

        self.context.update(
            [
                ("mode_sortie", "D"),
                ("memlimit", 100000),
                ("sans_entree", ""),
                ("nbaffich", 100000),
                ("filtre_entree", ""),
                ("sans_sortie", ""),
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
                ("_login", self.username),
                ("_progdir", os.path.dirname(__file__)),
                ("cryptolevel", 2),
            ]
        )
        self.initstats()

    def initstats(self):
        self.context.update(
            [
                ("_st_lu_objs", 0),
                ("_st_lu_fichs", 0),
                ("_st_lu_tables", 0),
                ("_st_wr_objs", 0),
                ("_st_wr_fichs", 0),
                ("_st_wr_tables", 0),
                ("_st_obj_duppliques", 0),
                ("_st_obj_supprimes", 0),
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

    def popcontext(self, typecheck=None, orig="", context=None):
        # print("avant pop",self.contextstack)
        if context and context in self.contextstack:
            while self.contextstack.pop() != context:
                continue
            return
        if typecheck is None or self.cur_context.type_c == typecheck:
            if len(self.contextstack) > 1:
                self.contextstack.pop()
            else:
                print(
                    "===================warning erreur d empilement de contexte",
                    orig,
                    self.cur_context,
                )
                # raise
        else:
            print(
                orig,
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

    def istrue(self, nom, defaut=False):
        """recupere la valeur booleenne d une variable"""
        return self.context.istrue(nom, defaut)

    def isfalse(self, nom):
        """recupere la valeur booleenne d une variable"""
        return self.context.isfalse(nom)

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
        # print("stockage", parametre)
        if parametre.startswith("'") and parametre.endswith("'"):
            parametre = parametre[1:-1]
        elif "=" in parametre:
            valeur = parametre.split("=", 1)
            if len(valeur) < 2:
                valeur.append("")
            if valeur[1] == '""':
                valeur[1] = ""
            #            self.parms[valeur[0]] = valeur[1]
            self.setvar(*valeur)
            return
            # print(
            #     "stockage parametre:",
            #     parametre,
            #     valeur[0],
            #     "->",
            #     valeur[1],
            #     self.context,
            # )
        self.posparm.append(parametre)
        #            self.parms["#P_"+str(len(self.posparm))] = parametre
        self.setvar("#P_" + str(len(self.posparm)), parametre)

    def set_abrev(self, nom_schema, dic_abrev=None):
        """cree les abreviations pour la definition automatique de snoms courts"""
        if dic_abrev is None:
            dic_abrev = self.getvar("abreviations")
        if nom_schema in self.schemas and dic_abrev:
            self.schemas[nom_schema].dic_abrev = dic_abrev

    def charge(self, fichier, ident_fich):
        """prechargement des fichiers de jointure ou de comparaison"""
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
        """effectue la resolution des chemins"""
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

    def get_converter(self, geomnatif, debug=None):
        """retourne le bon convertisseur de format geometrique"""
        debug = debug or self.debug
        # print("get_converter:niveau de debug", debug)
        return get_converter(geomnatif, debug=debug)

    def get_geomstructure(self, geomnatif, debug=None):
        """retourne la structure du champs geom de format geometrique"""
        debug = debug or self.debug
        # print("get_geomstructure:niveau de debug", debug)
        return get_geomstructure(geomnatif, debug=debug)

    def _finalise_sorties(self):
        """vide les tuyeaux et renseigne les stats"""
        if self.sorties:
            nb_fichs, nb_total = self.sorties.final(self.idpyetl)
            self.padd("_st_wr_fichs", nb_fichs)
            self.padd("_st_wr_objs", nb_total)
        if self.moteur:
            self.padd("_st_obj_duppliques", self.moteur.dupcnt)
            self.padd("_st_obj_supprimes", self.moteur.suppcnt)

    def process(self, debug=0):
        """traite les entrees"""
        # print ('debut_process avant macro',self.idpyetl)
        self.debug = self.debug or debug
        abort = False
        dt, _ = next(self.maintimer)
        entree = None if self.getvar("sans_entree") else self.getvar("_entree", None)
        self.macro_entree()
        entree = None if self.getvar("sans_entree") else self.getvar("_entree", None)
        if isinstance(entree, list):
            entree = ",".join(entree)
        # print("process E:",entree,'S:',self.getvar("sortie"),'regles', self.regles)

        if self.done and not self.regles:
            self.logger.info("traitments termines a l initialisation")
            self.logger.debug("rien a faire")
        elif self.statstore.isstat(entree):
            nb_total = entree.to_obj(self)
            #            nb_total = self._lecture_stats(entree)
        elif entree and entree.strip() and entree != "!!vide":
            self.logger.info(
                "debut traitement donnees:> %s --> %s",
                entree,
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
                    # print("mapper:traitement fichier", fich)
                    # traitement.racine_fich = os.path.dirname(i)
                    if self.worker:
                        self.aff.send(("init", 0, 0))
                    try:
                        # nb_lu = self.lecture(i, parms=parametres[i])
                        nb_lu = self.lecture(fich, parms=parms)
                    except StopIteration as arret:
                        #            print("intercepte abort",abort.args[0])
                        if arret.args[0] == 2:
                            continue
                        abort = True
                        nb_lu = 0
                        break
            except NotADirectoryError as err:
                self.logger.error("repertoire d entree inexistant: %s", err)

                # print("type entree ", type(entree))
            self.moteur.vide_stock()
            ft, _ = next(self.maintimer)
            self.setvar("_st_duree", (ft - dt))
            self.logger.info("fin traitement donnees: %d s", int(ft - dt))

        else:
            try:
                self.logger.info("debut traitement sans entree %s...", self.appel[:40])
                # print ('debut_process sans entree apres macro',self.idpyetl)
                self.moteur.traitement_virtuel(unique=1)
                self.moteur.vide_stock()
            except StopIteration as arret:
                if arret.args[0] > 2:
                    abort = True
        if abort:
            self._finalise_sorties()
        else:
            try:
                self.menage_final()
            except StopIteration:
                self._finalise_sorties()
        #        print('mapper: fin traitement donnees:>', entree, '-->', self.regle_sortir.params.cmp1.val)
        ft, _ = next(self.maintimer)
        self.setvar("_st_duree", (ft - dt))
        if not self.is_special and not self.done:

            self.logger.info(
                "fin traitement %d: %s traites %s",
                self.idpyetl,
                self.nompyetl,
                self.getvar("_st_lu_objs", "0"),
            )

        return

    def menage_final(self):
        """vidage de tous les tuyaux et stats finales"""
        # print("menage-final", self.schemas.keys(), self.mode)
        self.moteur.vide_stock()
        self.debug = 0
        # self._finalise_sorties()
        self._ecriture_schemas()
        self._ecriture_stats()
        self._finalise_sorties()  # on ne finalise les sorties que la pour tenir compte des traitements eventuels de schemas
        self.macro_final()
        return

    def cleanschemas(self):
        """reinitialise tous les schemas"""
        for schema in self.schemas.values():
            schema.cleanrules()

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
            # print("macro effectuee", texte, self.idpyetl, "->", processor.idpyetl)
            if retour:
                return {i: processor.getvar(i) for i in retour}
        return ()

    def macro_final(self):
        """execute une macro finale"""
        if self.worker and self.parent is None:
            macrofinale = self.context.getlocal("_w_end")
        else:
            macrofinale = self.context.getlocal("_end") or self.context.getlocal("#end")
        if not macrofinale:
            if not self.getmacro("#end"):
                return
            self.renamemacro("#end", "#_end")  # une seule passe
            macrofinale = "#_end"
        parametres = self.getvar("parametres_final")
        entree = self.getvar("entree_final", self.getvar("_sortie"))
        sortie = self.getvar("sortie_final", self.getvar("_sortie"))
        self.macrorunner(macrofinale, parametres, entree, sortie)
        return

    def macro_entree(self):
        """execute une macro de demarrage"""

        if self.worker and self.parent is None:
            macroinit = self.context.getlocal("_w_start")
        else:
            macroinit = self.context.getlocal("_start") or self.context.getlocal(
                "#start"
            )
        if not macroinit:
            # print ('pas de macro initiale')
            return
        # print("macro initiale", macroinit)
        parametres = self.getvar("parametres_initial")
        entree = self.getvar("entree_initial", self.getvar("_entree"))
        sortie = self.getvar("sortie_initial", self.getvar("_entree"))
        self.macrorunner(macroinit, parametres, entree, sortie)
        return

    def _ecriture_schemas(self):
        """sortie des schemas"""
        modes_schema_num = {
            "0": "no",  # pas de sortie de schema
            "1": "util",  # sort les schemas des classes utilisees dans le traitement
            "2": "non_vide",  # on ne sort que les schemas des classes non vides
            "3": "all",  # sort les schemas de toutes les classes definies
            "4": "int",  # sort les schemas de toutes les classes y compris internes
            "5": "fusion",  # combine les schemas en fonction des poids}
        }

        rep_sortie = self.getvar("sortie_schema")
        if rep_sortie:
            if os.path.isabs(rep_sortie) or rep_sortie.startswith("."):
                pass
            else:
                rep_sortie = os.path.join(self.getvar("_sortie"), rep_sortie)
        else:
            rep_sortie = self.getvar("_sortie")
        # print(
        #     "rep sortie schema",
        #     self.getvar("sortie_schema", "rien"),
        #     self.getvar("_sortie", "rien"),
        # )
        if rep_sortie == "-" or not rep_sortie and not self.mode.startswith("web"):
            # pas de sortie on ecrit pas
            if (
                not self.getvar("_testmode") and self.schemas
            ):  # en mode test ou web on rale pas
                if self.istrue("sans_sortie"):
                    return " on rale pas c est voulu"
                self.logger.warning("pas de repertoire de sortie")
            return

        mode_schema = self.getvar("force_schema", "util")
        mode_schema = modes_schema_num.get(mode_schema, mode_schema)
        if (
            mode_schema in {"all", "int", "fusion"}
            or self.istrue("force_virtuel")
            and not self.done
        ):
            self.logger.debug(
                "traitement virtuel schema %s worker:%s force:%s",
                mode_schema,
                self.worker,
                self.getvar("force_virtuel"),
            )
            self.moteur.traitement_virtuel()  # on force un peu pour creer toutes les classes
            self.moteur.vide_stock()
            # print('pyetl: ecriture schemas ', mode_schema,self.schemas.keys())
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

    def get_work_stats(self):
        """retourne un dictionnaire avec les stats d execution générales"""
        duree = self.getvar("_st_duree", 0.001)

        duree = 0.001 if duree == 0 else duree
        obj_lus = self.getvar("_st_lu_objs", 0)
        obj_ecrits = self.getvar("_st_wr_objs", 0)
        wstats = {
            "obj_lus": obj_lus,
            "fich_lus": self.getvar("_st_lu_fichs", 0),
            "tabl_lus": self.getvar("_st_lu_tables", 0),
            "obj_ecrits": obj_ecrits,
            "obj_dupp": self.getvar("_st_obj_duppliques", 0),
            "fich_ecrits": self.getvar("_st_wr_fichs", 0),
            "duree": duree,
            "perf_r": int(obj_lus / duree),
            "perf_w": int(obj_ecrits / duree),
        }
        self.initstats()
        return wstats

    def get_results(self):
        """retourne un tableau de resultats contenant les sortie de #print"""
        # print(
        #     "retour processeur",
        #     os.getpid(),
        #     self.idpyetl,
        #     self.webstore.keys(),
        #     self.mode,
        # )
        # on reformate les logs qui sont des buffers
        buffer = None
        if "logbrut" in self.webstore:
            buffer = self.webstore["logbrut"]
            sortie = buffer.getvalue().split("\n")
            self.webstore["log"] = sortie
        # petite manip pour nettoyer les #
        tmp = {
            i[1:] if str(i).startswith("#") else i: self.webstore[i]
            for i in self.webstore if i !="logbrut"
        }
        if "logbrut" in self.webstore:
            self.webstore = {"logbrut": buffer}
            
        #     self.gestion_log.resetlog()
        #     self.gestion_log.set_weblog()
        if buffer:
            buffer.truncate(0)
        else:
            self.webstore = dict()
        name = "noname"
        return tmp, name

    def getreader(self, nom_format, regle, reglestart=None):
        """retourne un reader"""
        return Reader(nom_format, regle, reglestart)

    def getoutput(self, nom_format, regle):
        """retourne un writer"""
        return Output(nom_format, regle, None)

    def getdbaccess(self, regle, nombase, type_base=None, chemin=""):
        """retourne une connection et la cache"""
        if nombase in self.dbconnect:
            connection=self.dbconnect[nombase]
            if not connection.closed:
                return self.dbconnect[nombase]
        connection = dbaccess(regle, nombase, type_base)
        if connection:
            self.dbconnect[nombase] = connection
            return connection
        print("erreur connection base", nombase)
        # return None
        raise StopIteration(3)

    def lecture(self, fich, regle=None, reglenum=None, parms=None):
        """lecture d'un fichier d'entree"""
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
        self.aff.send(("fich", 1, lecteur.lus_fich))
        return lecteur.lus_fich


# # on cree l'objet parent et l'executeur principal
# mapper = Pyetl()
# # mapper.initpyetl("#init_mp", [])
# mapper.ismainmapper = True
# set_mainmapper(mapper)
cremapper()



def _main():
    """mode autotest du module"""
    print("autotest complet")
    # on cree l'objet parent et l'executeur principal
    cremapper()
    ppp = getmainmapper().getpyetl("#autotest", liste_params=[])
    if ppp:
        # if ppp.prepare_module("#autotest", []):
        ppp.process()
        print("fin procedure de test", next(ppp.maintimer))
    else:
        print("execution impossible")


if __name__ == "__main__":
    # execute only if run as a script
    _main()
