
# -*- coding: utf-8 -*-
'''modification d'attributs en fonction d'un fichier de parametrage avec
prise en charge des expressions regulieres'''
import time
#t1=time.time()
#print ('pyetl start import ')
import os
#import sys
import re
#import platform
import logging
import itertools
from collections import defaultdict

from  .formats.ressources import GestionSorties, DEFCODEC # formats entree et sortie
from  .formats.formats import Reader, Stat, ExtStat
from  .moteur.interpreteur_csv import lire_regles_csv, reinterprete_regle,\
         interprete_ligne_csv, map_vars
from  .moteur.compilateur import compile_regles
from  .moteur.moteur import Moteur, Macro
from  .moteur.fonctions import COMMANDES, SELECTEURS
from  .moteur.fonctions.outils import scandirs
from  .schema.schema_interne import init_schema # schemas
from  .schema.schema_io import ecrire_schemas, retour_schemas # schemas
#from  .outils.crypt import crypter, decrypt

VERSION = "0.8.2.2_e"
LOGGER = logging.getLogger('pyetl') # un logger
MODULEDEBUG = False

def initlogger(fichier=None, niveau_f=logging.DEBUG, niveau_p=logging.WARNING):
    """ création de l'objet logger qui va nous servir à écrire dans les logs"""
# on met le niveau du logger à DEBUG, comme ça il écrit tout dans le fichier log s'il existe
    if not LOGGER.handlers:
# création d'un handler qui va rediriger chaque écriture de log sur la console
        LOGGER.setLevel(niveau_p)
        print_handler = logging.StreamHandler()
        printformatter = logging.Formatter('%(levelname)s %(funcName)s: %(message)s')
        print_handler.setFormatter(printformatter)

        print_handler.setLevel(niveau_p)
        LOGGER.addHandler(print_handler)
    if fichier:
        LOGGER.setLevel(niveau_f)
        # création d'un formateur qui va ajouter le temps, le niveau
        # de chaque message quand on écrira un message dans le log
        fileformatter = logging.Formatter('%(asctime)s::%(levelname)s::%(module)s.%(funcName)s'+
                                          '::%(message)s')
#        infoformatter = logging.Formatter('%(asctime)s::%(levelname)s::%(message)s')
        # création d'un handler qui va rediriger une écriture du log vers
        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        file_handler = logging.FileHandler(fichier)
        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        file_handler.setLevel(niveau_f)
        file_handler.setFormatter(fileformatter)
        LOGGER.addHandler(file_handler)
        LOGGER.info("pyetl:"+VERSION)

initlogger()



def initcontext(traitement, env=None, log=None):
    """initialise le contexte (parametres de site environnement)"""
    if traitement.inited:
        return # on a deja fait le boulot
    env = env if env is not None else os.environ
    if log and not traitement.worker:
        traitement.set_param('logfile', log)
        initlogger(fichier=log)
    traitement.init_environ(env)
    traitement.aff = traitement._patience(0, 0) # on initialise le gestionnaire d'affichage
    next(traitement.aff)

def initpyetl(traitement, commandes, args, env=None, log=None):
    """ initialisation standardisee: cree l'objet pyetl de base"""

    initcontext(traitement, env, log)
    try:
        traitement.prepare_module(commandes, args)
        return True
    except SyntaxError as err:
        LOGGER.critical('erreur script '+str(commandes)+' '+str(err)+
                        ' worker:'+str(traitement.worker))
    return False

def getlog(args):
    '''recherche s il y a une demande de fichier log dans les arguments'''
    log = None
    for i in args:
        if 'log=' in i:
            log = i.split('=')[1]
    return log


def runpyetl(commandes, args, env=None, log=None):
    """ lancement standardise c'est la fonction appelee au debut du programme"""
    log = getlog(args)
    print("pyetl", VERSION, commandes, args, log)

    if initpyetl(MAINMAPPER, commandes, args, env=env, log=log):
        MAINMAPPER.process()
    else:
        print('arret du traitement ')
        return
    nb_total = MAINMAPPER.get_param('_st_lu_objs', 0)
    nb_fichs = MAINMAPPER.get_param('_st_lu_fichs', 0)
    if nb_total:
        print(nb_total, "objets lus dans", nb_fichs, 'fichiers ')

    if MAINMAPPER.moteur:
        print(MAINMAPPER.get_param('_st_obj_duppliques', 0), "objets dupliques")
    n_ecrits = MAINMAPPER.get_param('_st_wr_objs', 0)
    if n_ecrits:
        print(n_ecrits, "objets ecrits dans ", MAINMAPPER.get_param('_st_wr_fichs', 0),
              "fichiers ")
    MAINMAPPER.signale_fin()
    duree, _ = next(MAINMAPPER.maintimer)
    duree += 0.001
    print("fin traitement total :", nb_fichs, "fichiers traites en ",
          int(duree*1000), "millisecondes")
    if nb_total:
        print('perf lecture  :', int(nb_total/duree), 'o/s')
    if n_ecrits:
        print('perf ecriture :', int(n_ecrits/duree), 'o/s')


def initparallel(parametres):
    """initialisatin d'un process worker pour un traitement parallele"""
#    commandes, args, params, macros, env, log = parametres
    params, macros, env, log = parametres

    if MAINMAPPER.inited:
#        print("pyetl double init", os.getpid())
        time.sleep(1)
        return None
#    print("pyetl initworker", os.getpid(), commandes, args)
    LOGGER.info("pyetl initworker "+str(os.getpid()))
    MAINMAPPER.worker = True
    initcontext(MAINMAPPER, env, log)
    MAINMAPPER.inited = True
    MAINMAPPER.macros.update(macros)
    MAINMAPPER.parms.update(params)
    MAINMAPPER.parametres_lancement = parametres
    time.sleep(1)
#    if initpyetl(MAINMAPPER, commandes, args, env=env, log=log):
##       time.sleep(2)
#       return (os.getpid(), True)
    return (os.getpid(), True)


def setparallelid(parametres):
    """positionne un numero de worker et initialise les commandes """
    pidset, commandes, args = parametres
    if MAINMAPPER.get_param('_wid'):
        time.sleep(1)
        return None
    wid = str(pidset[os.getpid()])
    MAINMAPPER.set_param('_wid', wid)
    log = MAINMAPPER.get_param('logfile')
    if log:
        base, ext = os.path.splitext(MAINMAPPER.get_param('logfile'))
        log = base+'_'+wid+'.'+ext
#    print('avant init', commandes, args)
    init = initpyetl(MAINMAPPER, commandes, args, log=log)

    return (os.getpid(), MAINMAPPER.get_param('_wid'), init)


def set_parallelretour(mapper, valide):
    '''positionne les variables de retour pour l'execution en parallele'''

    schema = retour_schemas(mapper.schemas, mode=mapper.get_param('force_schema', 'util'))
    stats_generales = mapper.getstats()
    retour_stats = {nom: stat.retour() for nom, stat in mapper.stats.items()}
    retour = {'pid': os.getpid(), 'wid': mapper.get_param('_wid'), 'valide': valide,
              'stats_generales': stats_generales, 'retour': mapper.retour,
              'schemas': schema, 'fichs': mapper.liste_fich, 'stats': retour_stats}
    return retour



def parallelbatch(parametres_batch):
    """execute divers traitements en parallele"""
#    print ("pyetl startbatch",os.getpid(), parametres_batch[:3])
    numero, mapping, entree, sortie, args = parametres_batch
#    if not MAINMAPPER.inited:
#        initparallel('#init_mp', '',params, macros)
    processor = MAINMAPPER.getpyetl(mapping, liste_params=args,
                                    entree=entree, rep_sortie=sortie)
    if processor is None:
        print("pyetl echec batchworker", os.getpid(), mapping, args)
        return (numero, {})

    processor.process()
    retour = set_parallelretour(processor, True)
#    print("pyetl batchworker", os.getpid(),processor.idpyetl, mapping, args,
#          '->', processor.retour)
    return (numero, retour)

def parallelprocess(numero, file, regle):
    '''traitement individuel d'un fichier'''
    try:
#        print ('worker:lecture', file)
        nom, parms = file
        nb_lu = MAINMAPPER.lecture(file, reglenum=regle, parms=parms)
    except StopIteration as arret:
        return numero, -1
    return numero, nb_lu

def endparallel(test=None):
    '''termine un traitement parallele'''
    schema = None
    if MAINMAPPER.ended:
#        print("pyetl double end", os.getpid())
        time.sleep(1)
        return None
    try:
        nb_total, nb_fichs, schema = MAINMAPPER.menage_final()

        succes = True
    except StopIteration:
        nb_total, nb_fichs = MAINMAPPER.sorties.final()
        succes = False
    retour = set_parallelretour(MAINMAPPER, succes)
#    if MAINMAPPER.moteur():
#        MAINMAPPER.padd('_st_obj_duppliques', MAINMAPPER.moteur.dupcnt)
#        MAINMAPPER.padd('_st_obj_supprimes', MAINMAPPER.moteur.suppcnt)
#    stats_generales = MAINMAPPER.getstats()

#    print("-----pyetl batchworker end", os.getpid(), succes, nb_total, nb_fichs)
    LOGGER.info("-----pyetl batchworker end "+str(os.getpid())+
                ' succes ' if succes else 'echec '+str(nb_total)+' '+str(nb_fichs))

    MAINMAPPER.ended = True
#    retour_stats = {nom: stat.retour() for nom, stat in MAINMAPPER.stats.items()}
#    retour = {'pid': os.getpid(), 'wid': MAINMAPPER.get_param('_wid'), 'valide': succes,
#              'stats_generales': stats_generales,
#              'schemas': schema, 'fichs': MAINMAPPER.liste_fich, 'stats': retour_stats}

    return (os.getpid(), retour)

#---------------debut programme ---------------

class Pyetl(object):
    ''' structure parent : instanciee une fois pour un traitement
    permet le stockage de tous les parametres globaux du traitement.
    cette structrure est passee a l'ensemble des modules '''
    # constantes de travail
    modiffonc = re.compile(r"([nc]):(#?[a-zA-Z_][a-zA-Z0-9_]*)")
    param_exp = re.compile("(%#?[a-zA-Z0-9_]+(?:#[a-zA-Z0-9_]+)?%)")
    _ido = itertools.count(1) # compteur d'instance
    version = VERSION
    # ressources communes
    compilateur = compile_regles # interpreteur par defaut
    lecteur_regles = lire_regles_csv
    interpreteur = interprete_ligne_csv
    commandes = COMMANDES
    selecteurs = SELECTEURS
    sortedsels = sorted(selecteurs.values(), key=lambda x: x.priorite)
    reconfig = reinterprete_regle
    from  .outils.crypt import crypter, decrypt
#    crypt = crypter
#    decrypt = decrypt
    init_schema = init_schema
#    formats_connus = F.LECTEURS
    reader = Reader

    def __init__(self, parent=None, nom=None):

        self.nompyetl = nom if nom else 'pyetl'
        self.starttime = time.time() # timer interne
        # variables d'instance (stockage des elements)
        self.maintimer = self._timer(init=True)
        self.statdefs = dict() # description des statistiques
        self.stats = dict() #stockage des statistiques
        self.liste_fich = defaultdict(int) # fichiers utilises pour les comptages d'objets
        self.cntr = dict() #stockage des compteurs
        self.idpyetl = next(self._ido)
        # jointures
        self.jointabs = dict() #clefs de jointure
        self.joint_fich = dict() # fichier externes de jointure
        self.jointdef = dict() # definition des champs
        self.posparm = list()
        self.store = dict()
        self.dbconnect = dict() # connections de base de donnees
        self.parms = dict() #parametres ligne de commande et variables globales
        self.parent = parent # permet un appel en cascade
        self.initparallel = initparallel
        self.parallelprocess = parallelprocess
        self.parallelbatch = parallelbatch
        self.endparallel = endparallel
        self.setparallelid = setparallelid
        self.inited = False
        self.ended = False
        self.worker = False # process esclave
#        self.paramdir = os.path.join(env.get("USERPROFILE", "."), ".pyetl")
        self.username = os.getlogin()
        self.userdir = os.path.expanduser('~')
        self.paramdir = os.path.join(self.userdir, ".pyetl")
#            self.dbconnect = self.parent.dbconnect
            # on partage les sorties pour pas se manger les fichiers

#        print('params', sorted(self.parms.items()))
        self.stream = 0
        self.debug = 0
#        self.stock = False # pas de stockage

        # parametres globaux ressources
        self.bindings = dict()
        self.moteur = None
        # parametres de lancement


        self.aff = None

        # variables de stockage interne
        # commandes internes
        # strucutres de stockage partagees
        self.retour = []
        # description des fonctions statistiques (dictionnaire d'objets stats)
        # entree
        self.fichs = [] # liste des fichiers a traiter
        self.parametres_fichiers = dict() # paramteres d'acces
        self.schemas = dict() # schemas des classes
        self.regles = list()# regles de mapping
        self.regle_sortir = None
        self.racine = None
        self.fichier_regles = None

        # etats

        self.dupcnt = 0
        self.statfilter = ''
        self.statprint = False
        self.statdest = None
        self.fichier_courant = ''
        self.chemin_courant = ""

        self.temps_fermeture = 0
        self.schemadef = False
        self.rdef = None

        # identification d'une reference a un champ  dans une expression
#        self.liste_formats = [".ASC", ".SHP", ".CSV"]
#        self.sortie_defaut = "asc"
        self.f_entree = None
        self.liste_regles = None

        self.liens_variables = dict()
        self.duree = 0
        #self.durees = dict()
        self.attlists = dict()
        #self.nb_obj = 0 # nombrte d'objets traites
        #self.parms["rep_regles"] = self.rdef
#        print ('_avant______________mode sortie' ,self.stream,self.get_param("mode_sortie"))

        self.ident_courant = ("", "")
        self._set_streammode()
        self.done = False

    def init_environ(self, env=None):
        """initialise les variables d'environnement et les macros"""
        self.env = os.environ() if env is None else env
        if not os.path.isdir(self.paramdir):
            try:
                os.makedirs(self.paramdir)
            except PermissionError:
                pass
        self.site_params_def = env.get('PYETL_SITE_PARAMS', "")
        self.liste_params = None

        if self.parent is None:
            self._init_params() # positionne les parametres predefinis
            self.macros = dict()
            self.site_params = dict()
            if self.site_params_def:
                self._charge_site_params(self.site_params_def)
                # charge les parametres de site (fichier ini)
            self._charge_site_params(self.paramdir)
            # charge les parametres individuels (fichier ini)
            self._paramdecrypter() # decrypte les parametres cryptes
            self.charge_cmd_internes() # macros internes
            self.charge_cmd_internes(site="macros") # macros internes
#            self.charge_cmd_internes(site="macros") # macros internes
            self.sorties = GestionSorties()
            self.debug = int(self.get_param('debug'))

        else:
            self.macros = dict(self.parent.macros)
            self.site_params = self.parent.site_params
            self.sorties = self.parent.sorties


    def commandes_speciales(self):
        """commandes speciales"""
#        print("commandes speciales: ", self.fichier_regles)

        #on ne lit pas de regles mais on prends les commandes predefinies
        if self.fichier_regles is None:
            return
        liste_commandes = self.fichier_regles.split(',')
        commande, *pars = liste_commandes[0].split(':')
        nom = self.get_param('_sortie')

        if commande == '#help' or commande == "help":
            from .helpdef.helpmodule import print_help
            self.set_param("_sortie", "")
            print_help(self, nom)
            self.done = True

        elif commande == '#autotest' or commande == "autotest":
#            print("detecte autotest ", self.fichier_regles, self.posparm)

            from .tests.testmodule import full_autotest
            liste_regles = full_autotest(self, pars[0] if pars else nom)
            if not liste_regles:
                self.done = True
            else:
                self.fichier_regles = ""
                self.liste_regles = liste_regles
                # on a charge les commandes on neutralise l autotest

        elif commande == '#unittest' or commande == "unittest":
            from .tests.testmodule import unittests
            self.set_param("_sortie", "")
            unittests(self, nom=nom, debug=self.get_param("debug"))
            self.done = True

    def _traite_params(self, liste_params):
        """gere la liste de parametres"""
        if liste_params is not None:
            self.liste_params = liste_params[:]
            for i in liste_params:
                self._stocke_param(i)  # decodage parametres de lancement
#            print ('traite_param',len(self.posparm))
            if len(self.posparm) >= 2:
                self.set_param('_entree', self.posparm[0])
                self.set_param('_sortie', self.posparm[1])
            elif len(self.posparm) == 1:
                self.set_param('_sortie', self.posparm[0])

    def prepare_module(self, regles, liste_params):
        ''' prepare le module pyetl pour l'execution'''

        if isinstance(regles, list):
            self.nompyetl = 'pyetl'
            self.liste_regles = regles
        else:
            self.fichier_regles = regles
            self.nompyetl = regles
            self.rdef = os.path.dirname(regles) # nom de repertoire des regles
        self._traite_params(liste_params)



        LOGGER.debug('prepare_module'+ repr(regles)+  repr(liste_params)+
                     self.get_param('_sortie', 'pas_de_sortie'))

        if self.fichier_regles or self.liste_regles:
            erreurs = self.commandes_speciales()
            if not self.done:
                try:
                    erreurs = self.lecteur_regles(self.fichier_regles,
                                                  liste_regles=self.liste_regles)
                except KeyError as ker:
                    LOGGER.critical('erreur lecture '+ker.__repr__()+'('+repr(regles)+')')
                    erreurs = erreurs+1 if erreurs else 1

            if erreurs:
#                print("logger ", self.idpyetl)
                message = " erreur" if erreurs == 1 else " erreurs"
                LOGGER.critical('process '+str(self.idpyetl)+': '+
                                str(erreurs) + message+" d'interpretation des regles:"+
                                " arret du traitement ")
                for i in self.regles:
                    if i.erreurs:
                        print(i.numero, i, i.erreur)
#                print("sortie en erreur", self.idpyetl)
                return False
        self.sorties.set_sortie(self.get_param('_sortie'))
        if not self.regles:
#            print('pas de regles', self.done)
            if self.done:
                return True
            LOGGER.critical("pas de regles arret du traitement "+str(self.fichier_regles))
            return False
#        if self.parent is None:
#            self._gestion_posparm()
        self._set_streammode()
        try:
            self.compilateur(self.regles, self.debug)
            self.regle_sortir = self.regles[-1]
            self.regle_sortir.declenchee = True
#            self.stores = [[] for i in range(len(self.regles))]# stockage temporaire d'objets
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
        '''acces au temps pour les calculs de duree.'''
        if init:
            heure_debut = self.starttime
        else:
            heure_debut = time.time()
        intermediaire = 0
        prec = heure_debut
        while True:
            yield (time.time()-heure_debut, intermediaire)
            intermediaire = time.time()-prec
            prec = time.time()


    def _patience(self, nbfic, nbval):
        '''petits messages d'avancement pour faire patienter'''
        temps = self._timer()
        nbaffich = int(self.get_param('nbaffich'))
#        print ('init_patience ',self.worker, self.get_param('_wid', -1))
        prochain = nbaffich
        interm = 0.001 # temps intermediaire pour les affichages interm
        nop = 0
        nbtotal = 0
        tabletotal = 0

        def affiche(message, nbobj):
            '''gere l'affichage des messages de patience'''
            duree, interv = next(temps)
            if duree == 0:
                duree = 0.001
            cmp = '---'
            ftype = 'fichiers'
            tinterm = 0.001
            if message == 'interm':
                cmp = 'int'
            if message == 'tab':
                ftype = 'tables'
            msg = " --%s----> nombre d'objets lus %8d dans %4d %s en %5d "+\
                  "secondes %5d o/s"
            if self.worker:
                msg = 'worker%3s:'% self.get_param('_wid') + msg
            else:
                msg = 'mapper   :' + msg
            LOGGER.info(msg, cmp, nbobj, tabletotal, ftype, int(duree), int((nbobj)/duree),
                        int((nbobj-nop)/(interv+0.001)))
            if self.worker:
                if message == 'interm':
                    tinterm = interm + interv
                    msg = " --int----> nombre d'objets lus %8d en %5d secondes: %5d o/s"
                    msg = 'worker%3s:'% self.get_param('_wid') + msg
                    if interm > 1:
                        tinterm = interm + interv
                    else: # on calcule un temps moyen pour pas afficher n'importe quoi
                        tinterm = nbval/(nbobj/duree)
                    print(msg %(nbval, int(tinterm), int((nbval)/tinterm)))
            else:
                print(msg %(cmp, nbobj, tabletotal, ftype, int(duree), int((nbobj)/duree)))
            return (max(int(prochain/nbaffich), int(nbobj/nbaffich))+1)*nbaffich, tinterm

        while True:
            message, nbfic, nbval = yield
#            nbtotal += nbval
            tabletotal += nbfic
            if message == 'init':
                duree, interv = next(temps)
                interm = duree
#                print("init  : --------->", int(duree*1000), 'ms')
            elif message == 'end':
                nbtotal += nbval
#                tabletotal += nbfic
                affiche(message, nbtotal)
                break
            elif nbtotal+nbval >= prochain:
                prochain, interm = affiche(message, nbtotal+nbval)
#                if not self.worker:
#                    print (self.get_param('_wid', -1), 'prochain', prochain)
                nop = nbtotal+nbval
            if message != 'interm':
                nbtotal += nbval
                interm = 0.001

        yield duree, interv
        yield
#        yield duree, interv


    def getpyetl(self, regles, entree=None, rep_sortie=None,
                 liste_params=None, env=None, nom="", mode=None):
        ''' retourne une instance de pyetl sert pour les tests et le
        fonctionnement en fcgi et en mode batch'''
#        print(" dans getpyetl",mode)
        if not regles:
            if mode is None:
                return None

        env = env if env is not None else self.env
        petl = Pyetl(parent=self)
        petl.init_environ(env)
        if rep_sortie is not None:
            if rep_sortie.startswith('#'):
                petl.set_param('F_sortie', '#store')
            petl.set_param('_sortie', rep_sortie)
        if entree is not None:
#            print ("entree getpyetl",type(entree))
            petl.set_param('_entree', entree)
        if nom:
            petl.nompyetl = nom
        if initpyetl(petl, regles, liste_params, env=env):
            return petl
        print('erreur getpyetl', regles)
        return None


    def regmacro(self, nom, file='', liste_commandes=None, vloc=None):
        '''enregistrement d'une macro'''
        nouvelle = Macro(nom, file=file)
        if liste_commandes is not None:
            nouvelle.commandes_macro = liste_commandes
        if vloc is not None:
            nouvelle.vloc = vloc
#        print ('enrregistrement macro',nom)
        self.macros[nom] = nouvelle
        return nouvelle


    def _set_streammode(self):
        '''positionne le mode de traitement'''
        self.stream = 1 if self.get_param("mode_sortie") == "C" else False
        if self.get_param("mode_sortie") == "D":
            self.stream = 2
#        print('---------pyetl : mode sortie', self.stream, self.get_param("mode_sortie"))


    def _charge_site_params(self, origine):
        ''' charge des definitions de variables liees au site '''
        configfile = os.path.join(origine, 'site_params.csv')
        if not os.path.isfile(configfile):
            print('pas de parametres locaux')
            return
        nom = ''
#        print('parametres locaux', configfile)
#        init = False
        for conf in open(configfile, 'r').readlines():
            liste = (conf[:-1]+';;').split(';')
            if liste and liste[0].startswith('!'):
                continue
            if liste and liste[0].strip() == '':
                continue
            if liste and liste[0].strip() == '&&#set': # on ecrase ou on cree
                nom = liste[1]
                self.site_params[nom] = list()
            elif liste and liste[0].strip() == '&&#add': # on ajoute des valeurs
                nom = liste[1]
                if nom not in self.site_params:
                    self.site_params[nom] = list()
#                print ('chargement parametres de site ',nom)
            else:
                if nom:
                    nom_p, val = liste[0], liste[1]
                    self.site_params[nom].append((nom_p, val))
#                    self.site_params[nom].append((liste[0]+'_'+nom, liste[1]))
        self.load_paramgroup('init')
#        print("parametres de site",origine)
#        print("variables",self.parms)


    def _paramdecrypter(self): # decrypte les parametres cryptes
        """decrypte d'eventuels parametres cryptes"""
#        print ('decryptage parametres',self.parms['cryptokey'])
        keyname = self.get_param('cryptokeyname', 'defaultkey')
        key = self.get_param(keyname)
#        print ('nom de la clef', keyname, 'clef', key)
        for nom in self.site_params:
            for numero, parametre in enumerate(self.site_params[nom]):
                nom_p, val = parametre
                if nom_p.startswith('**'): # cryptage
                    nom_p = nom_p[2:]
                    val = self.decrypt(val, key=key)
                    self.site_params[nom][numero] = (nom_p, val)


    def load_paramgroup(self, clef, nom='', check='', fin=True):
        """ charge un groupe de parametres """
        if not clef:
            return
        if check: #on verifie que l'on a pas deja defini les choses avant
#            print ('validation ',check,check+nom,check+nom in self.parms)
            if check+nom in self.parms:
                return
        if clef in self.site_params:
#            print("chargement", valeur, self.site_params[valeur])
            for var, val in self.site_params[clef]:
                val, _ = map_vars(self, val) # on fait du remplacement à la volee
                self.parms[var] = val
                if nom:
                    self.parms[var+'_'+nom] = val

        elif fin:
            print('definition parametres de site >'+clef+'< introuvable')
            print('aide:groupes connus: ')
            print('\n'.join([str(i) for i in sorted(self.site_params)]))
            raise KeyError
        return -1


    def charge_cmd_internes(self, test=None, site=None, direct=None):
        ''' charge un ensemble de macros utilisables directement '''
        configfile = os.path.join(os.path.dirname(__file__),
                                  'moteur/fonctions/commandes_internes.csv')
        if test:
            testrep = self.get_param("_test_path")
            configfile = os.path.join(testrep, str(test)+'.csv')
        if site:
#            print("chargement parametres de site", self.nompyetl,
#                  self.site_params_def, site)
            configfile = os.path.join(self.site_params_def, site+'.csv')
        if direct:
            configfile = direct+'.csv'
        nom = ''
        num = 0
        if not os.path.isfile(configfile):
            print('fichier de config', configfile, 'introuvable')
            return
        for conf in open(configfile, 'r').readlines():
            num += 1
            liste = conf.split(';')
            if liste and liste[0] == '!':
                pass
            if liste and liste[0] == '&&#define':
                nom = liste[1]
                vloc = [i for i in liste[2:] if i]
                macro = self.regmacro(nom, file=configfile, vloc=vloc)
            elif nom:
                macro.add_command(conf, num)


    def charge_macros_bd(self):
        '''charge des macros depuis la base de donnees definie dans les paramettres de site'''
        if self.get_param('dbmacro') != 'oui':
            return
        # on charge la structure des tables


    def _init_params(self):
        '''initialise les parametres
        #help||parametres systeme:
        '''

        self.parms.update([("mode_sortie", "B"), ("memlimit", 100000), ('sans_entree', ''),
                           ("nbaffich", 100000), ('filtre_entree', ''), ('sans_sortie', ''),
                           ("_st_lu_objs", 0), ("_st_lu_fichs", 0), ("_st_lu_tables", 0),
                           ("_st_wr_objs", 0), ("_st_wr_fichs", 0), ("_st_wr_tables", 0),
                           ("_st_obj_duppliques", 0), ("_st_obj_supprimes", 0),
                           ("tmpdir", './tmp'), ("F_entree", ''), ('racine', '.'),
                           ("job_control", ''), ('aujourdhui', time.strftime('%Y/%m/%d 00:00:00')),
                           ("stat_defaut", "affiche"),
                           ("debug", '0'), ("fstat", ''),
                           ("force_schema", 'util'),
                           ("epsg", "3948"), ("F_sortie", 'txt'),
                           ('xmldefaultheader',
                            '<?xml-stylesheet href="xsl/dico.xsl" type="text/xsl"?>'),
                           ('codec_sortie', DEFCODEC),
                           ('codec_entree', DEFCODEC),
                           ('_paramdir', self.site_params_def),
                           ('_paramperso', self.paramdir),
                           ('_version', self.version),
                           ('_progdir', os.path.dirname(__file__))
                          ])

    def getstats(self):
        '''retourne un dictionnaire avec les valeurs des stats'''
        return {i:self.get_param(i, 0) for i in self.parms if i.startswith('_st')}

    def get_param(self, nom, defaut='', local=False, groupe=None):
        ''' fournit la valeur d'un parametre '''
        converter = type(defaut) if defaut is not None else None
        if groupe:
            valeur = self.get_param(nom+'_'+groupe, defaut=None)
            if valeur is not None:
                return converter(valeur) if converter else valeur
        if nom in self.parms:
#            print ('lecture parametre',nom,self.parms[nom],self.idpyetl)
            return converter(self.parms[nom]) if converter else self.parms[nom]
#        print ('non trouve',nom , self.idpyetl, self.parent)
        if local:
            return defaut
        return self.parent.get_param(nom, defaut) if self.parent else defaut


    def set_param(self, nom, valeur, parent=0):
        ''' positionne un parametre eventuellement sur le parent'''
        if parent > 0 and self.parent:
            self.parent.set_param(nom, valeur, parent-1)
            return
        self.parms[nom] = valeur
#        print ('positionnement variable', nom,'-->', valeur, self.idpyetl)

    def padd(self, nom, valeur, parent=0):
        '''incremente un parametre d'une valeur'''
        vinit = self.get_param(nom, 0, local=parent)
        self.set_param(nom, vinit+valeur, parent=parent)
#        print ('padd',nom,self.get_param(nom, 0, local=parent))


    def pasum(self, nom1, nom2, parent=0):
        '''incremente un parametre d'un autre parametre'''
        vinit = self.get_param(nom1, defaut=0, local=parent)
        valeur = self.get_param(nom2, defaut=0, local=parent)
        self.set_param(nom1, str(vinit+valeur), parent=parent)


    def _stocke_param(self, parametre):
        '''stockage d'un parametre'''
        if "=" in parametre:
            valeur = parametre.split("=", 1)
            if len(valeur) < 2:
                valeur.append('')
            if valeur[1] == '""':
                valeur[1] = ''
            self.parms[valeur[0]] = valeur[1]
#            print("stockage",parametre,valeur[0],self.parms[valeur[0]] )
        else:
            self.posparm.append(parametre)
            self.parms["#P_"+str(len(self.posparm))] = parametre


    def set_abrev(self, nom_schema, dic_abrev=None):
        '''cree les abreviations pour la definition automatique de snoms courts'''
        if dic_abrev is None:
            dic_abrev = self.get_param("abreviations")
        if nom_schema in self.schemas:
            self.schemas[nom_schema].dic_abrev = dic_abrev


    def charge(self, fichier, ident_fich):
        '''prechargement des fichiers de jointure ou de comparaison '''
#        print("charge: prechargement",fichier, ident_fich)

        clef = self.jointdef[ident_fich]
        self.joint_fich[ident_fich] = fichier
        stock = dict()
#        if fichier.startswith('db:'):

        if self.rdef:
            fichier = fichier.replace("D:", self.rdef+"/")
        if os.path.isfile(fichier): #si le fichier n'existe pas on cree une table vide
#            print("info :pyetl: chargement jointure", fichier)
            for i in open(fichier, "r", encoding=self.get_param('codec_entree', 'utf-8')):
                liste = i[:-1].split(";")
                stock[liste[clef].strip()] = liste
        else:
            print("erreur:pyetl: fichier jointure introuvable :", fichier)

        self.jointabs[ident_fich] = stock
#        print("charge: prechargement",fichier, ident_fich, stock)


    def _prep_chemins(self, chemin, nom):
        '''effectue la resolution des chemins '''
        # chemin du fichier de donnees
        f_intrm = nom.replace("C:", os.path.join(self.racine, chemin))
        # fichier de jointure dans le repertoire de regles
        f_intrm = f_intrm.replace("D:", self.rdef+"/")
        # nom du fichier de donnees courant
        f_final = f_intrm.replace("F:", self.fichier_courant)
        #print ("jointure dynamique",self.mapper.racine,';',chemin,';',":",nom,'->',f,'(',f1,')')
        return f_final


    def jointure(self, fichier, chemin, clef, champ):
        '''preparation d'une jointure: chemin dynamique'''
        f_final = self._prep_chemins(chemin, fichier)
        if self.joint_fich[fichier] != f_final:
            self.charge(f_final, fichier)
        return self.jointabs[fichier].get(clef.strip(), ["" for i in range(champ+1)])[champ]


    def jointure_s(self, fichier, clef, champ):
        '''jointure statique chemin absolu ou relatif au repertoire de regles'''
        cle = clef.strip()
#        print ('dans jointure ', self.jointabs)
        try:
            return self.jointabs[fichier][cle][champ]
        except KeyError:
            if self.debug:
                print('pyetl: jointure statique clef non trouvee ', fichier, clef, champ)
            return ''
#        return self.jointabs[fichier].get(clef.strip(), ["" for i in range(champ+1)])[champ]

    def get_converter(self, geomnatif):
        ''' retourne le bon convertisseur de format geometrique'''
#        print('convertisseur', geomnatif, F.lecteurs)
        _, converter, _ = Reader.lecteurs.get(geomnatif, Reader.lecteurs['interne'])
        return converter


    def process(self, debug=0):
        '''traite les entrees '''
        if self.done:
            try:
                nb_total, nb_fichs, _ = self.menage_final()
            except StopIteration:
                nb_total, nb_fichs = self.sorties.final()
            return
        if debug:
            self.debug = debug
        entree = self.get_param('_entree', None)
        if self.get_param('sans_entree'):
            entree = None
#        print("process",entree, self.regles)
        if isinstance(entree, (Stat, ExtStat)):
            nb_total = self._lecture_stats(entree)
            return

        abort = False
        duree = 0
#        lu_total, lu_fichs = 0, 0
        self.aff = self._patience(self.get_param('_st_lu_objs', 0),
                                  self.get_param('_st_lu_fichs', 0))
        # on initialise le gestionnaire d'affichage
        next(self.aff)
#        interv_affich = int(self.get_param("nbaffich", "100000"))
#        nbaffich = interv_affich
        if entree and entree.strip() and entree != '!!vide':
            print('mapper: debut traitement donnees:>'+entree+ '-->',
                  self.regle_sortir.params.cmp1.val)
            try:
                fichs = self.scan_entree()
            except NotADirectoryError as err:
                print("!!!!!!!!!!!!!!!!!!!!!attention repertoire d'entree inexistant:", err)
                print('type entree ', type(entree))
                fichs = None
            if fichs:

                self.aff.send(('init', 0, 0))
                for i in fichs:
                    #print ('mapper:traitement fichier',i)
                    #traitement.racine_fich = os.path.dirname(i)
                    try:
                        nb_lu = self.lecture(i)
                    except StopIteration as arret:
#            print("intercepte abort",abort.args[0])
                        if arret.args[0] == '2':
                            continue
                        abort = True
                        nb_lu = 0
                        break


#                    self.aff.send(('fich', 1, nb_lu))
                duree, _ = self.aff.send(('end', 0, 0))
            else:
                print('pas de fichiers en entree')
            print('mapper: ---------> fin traitement donnees:', int(duree))
            print('mapper: ---------> finalisation:')
        else:
            try:
                self.moteur.traitement_virtuel(unique=1)
            except StopIteration as arret:
                abort = True
        if abort:
            nb_total, nb_fichs = self.sorties.final()
        else:
            try:
                nb_total, nb_fichs, _ = self.menage_final()
                self.padd('_st_obj_duppliques', self.moteur.dupcnt)
            except StopIteration:
                nb_total, nb_fichs = self.sorties.final()
#        print('mapper: fin traitement donnees:>', entree, '-->', self.regle_sortir.params.cmp1.val)
        return
#        return (self.get_param('_st_lus_total', 0), self.get_param('_st_lus_fichs', 0),
#                nb_total, nb_fichs)


    def menage_final(self, mode_schema=None):
        '''vidage de tous les tuyaux et stats finales'''

        stock = True
        while stock:
            stock = False
            for regle in self.regles:
                if regle.store and regle.nbstock:
                    stock = True
                    regle.traite_stock(regle)

        self.debug = 0
        if self.worker: # on est en mode esclave
#            print ('worker ecrire schema csv')
            schemas = retour_schemas(self.schemas, mode=self.get_param('force_schema', 'util'))
#            print ('worker apres ecrire schema csv')
        else:
            self._ecriture_schemas()

        nf2, ng2 = self.sorties.final() # on ferme tous les fichiers

        self._ecriture_stats()
        self.padd('_st_wr_fichs', nf2)
        self.padd('_st_wr_objs', ng2)
        schemas = None


        self.macro_final()
        return ng2, nf2, schemas


    def macro_final(self):
        """ execute une macro finale"""
        macrofinale = self.get_param('_end', local=True) # on travaille par instance
        if not macrofinale:
            macrofinale = self.get_param('#end', local=True) # on travaille par instance
#        print ('finalisation commande ', macrofinale, self.idpyetl)
        if not macrofinale or (self.worker and self.parent is None):
            # le worker de base n'execute pas de macro finale
            macrofinale = self.get_param('_w_end', local=True)
            if not macrofinale:
                return
        mdef = macrofinale.split(':')
        nom_macro = mdef[0]
        variables = mdef[1:]
        macro = self.macros.get(nom_macro)
        if macro is None:
            print('macro finale inconnue', nom_macro)
            return
        if not variables:
            parametres = self.get_param('parametres_final')
            params = [i.strip('"').replace('"=>"', '=')
                      for i in parametres.split('", "')] if parametres else None
        else:
            if macro.vloc:
                params = [nom+'='+valeur for nom, valeur in zip(macro.vloc, variables)]

            else:
                params = variables

        entree = self.get_param('entree_final', self.get_param('_sortie'))
        sortie = self.get_param('sortie_final', self.get_param('_sortie'))
#        print('script final parametres', nom_macro, entree, sortie, params, variables, macro.vloc)
#        return True
        processor = self.getpyetl(nom_macro, liste_params=params,
                                  entree=entree, rep_sortie=sortie)
#        print('parametres macro', processor.nompyetl, [(i,processor.get_param(i))
#                                                       for i in macro.vloc])
        if processor is not None:
            processor.process()
            print('script final effectue', nom_macro, self.idpyetl, '->', processor.idpyetl)
        return

    def _ecriture_schemas(self):
        '''sortie des schemas '''
        modes_schema_num = {'0': 'no', # pas de sortie de schema
                            '1': 'util', # sort les schemas des classes utilisees dans le traitement
                            '2': 'non_vide', # on ne sort que les schemas des classes non vides
                            '3': 'all', # sort les schemas de toutes les classes definies
                            '4': 'int', # sort les schemas de toutes les classes y compris internes
                            '5': 'fusion' # combine les schemas en fonction des poids}
                           }
        rep_sortie = self.get_param('sortie_schema', self.get_param('_sortie'))
        if rep_sortie == '-' or not rep_sortie: # pas de sortie on ecrit pas
#            print ('schema:pas de repertoire de sortie ')
            return
        mode_schema = self.get_param('force_schema', 'util')
        mode_schema = modes_schema_num.get(mode_schema, mode_schema)
        LOGGER.info('ecriture schemas '+ str(mode_schema))
        if mode_schema in {'all', 'int', 'fusion'} and not self.done:
#            print('pyetl: traitement virtuel ', mode_schema)
            self.moteur.traitement_virtuel() # on force un peu pour creer toutes les classes
#        print('pyetl: ecriture schemas ', mode_schema)
        ecrire_schemas(self, mode_schema, formats=self.get_param("format_schema", 'csv'))

    def _ecriture_stats(self):
        '''stockage des stats '''
#        print("pyetl : stats a ecrire",self.idpyetl, self.stats.keys(), self.statprint)
        rep_sortie = self.get_param('_sortie')

        for i in self.stats:
#            if self.worker and self.parent is None:
#                continue #on ecrit pas on remonte
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
                codec_sortie = self.get_param("codec_sortie", 'utf-8')
                self.stats[i].ecrire(dest, self.statprint, self.statfilter, statdef,
                                     codec=codec_sortie, wid=self.get_param('_wid', ''))

        if self.get_param('fstat'):  # ecriture de statistiques de fichier
            if self.worker and self.parent is None:
                return #on ecrit pas on remonte
            if rep_sortie:
                if self.worker:
                    fstat = os.path.join(rep_sortie, self.get_param('fstat')+
                                         '_'+self.get_param('_wid')+".csv")
                else:
                    fstat = os.path.join(rep_sortie, self.get_param('fstat')+".csv")
                print("moteur : info ecriture stat fichier ", fstat)
                os.makedirs(os.path.dirname(fstat), exist_ok=True)
                fichier = open(fstat, "w", encoding=self.get_param('codec_sortie', 'utf-8'))
                fichier.write("repertoire;nom;nombre\n")
                for i in sorted(self.liste_fich):
                    fichier.write(';'.join((os.path.dirname(i),
                                            os.path.basename(i),
                                            str(self.liste_fich[i])))+'\n')
                fichier.close()
            else:
                print('%-60s | %10s |'%("           nom", "nombre   "))
                for i in sorted(self.liste_fich):
                    print('%-60s | %10d |'%(i, self.liste_fich[i]))
        # on ferme proprement ce qui est ouvert

    def signale_fin(self):
        '''ecrit un fichier pour signaler la fin du traitement'''
        if self.worker:
            return
        if self.get_param("job_control") and self.get_param("job_control") != 'no':
            print("info: pyetl:job_control", self.get_param("job_control"))
            open(self.get_param("job_control"), 'w').write("fin mapper\n")


    @staticmethod
    def _valide_auxiliaires(identifies, non_identifies):
        ''' valide que les fichiers trouves sont connus'''
#        auxiliaires = {a:F.AUXILIAIRES.get(a) for a in F.LECTEURS}
        auxiliaires = Reader.auxiliaires
        for chemin, nom, extinc in non_identifies:
            if (chemin, nom) in identifies:
                extref = identifies[(chemin, nom)]
                if auxiliaires.get(extref) and extinc in auxiliaires.get(extref):
#                    print ('connu ',chemin,nom,extinc,'->',extref)
                    pass
                else:
                    print('extention inconnue ', extref, '->', chemin, nom, extinc)


    def fichs_schema(self):
        '''determine les fichiers lies au schema'''
        fschemas = set()
        f_aux = {'_classes', '_mapping', '_enumerations',
                 "complements_enumerations.csv", "complements_classes.csv",
                 "complements_mapping.csv"}
        racine_entree = os.path.basename(self.get_param("schema_entree"))
        if racine_entree:
            fschemas.union({racine_entree + i for i in f_aux})
        racine_sortie = os.path.basename(self.get_param("schema_sortie"))
        if racine_sortie:
            fschemas.union({racine_sortie + i for i in f_aux})
        return fschemas


    def scan_entree(self, rep=None):
        " etablit la liste des fichiers a lire"
        entree = self.get_param('_entree') if rep is None else rep
#        print ('scan_entree', entree)

        if not entree or entree.startswith('!!vide'):
            self.fichs = []
            self.parametres_fichiers = {}
            return self.fichs
        force_format = ''
        liste_formats = Reader.lecteurs.keys()
#        auxiliaires = {a:F.AUXILIAIRES.get(a) for a in F.LECTEURS}
        force_format = self.get_param('F_entree', '')
        if self.debug:
            print('format entree forcee ', force_format)

        if os.path.isfile(entree): # traitement un seul fichier
            fichs = [(os.path.basename(entree), '')]
            entree = os.path.dirname(entree) # on extrait le repertoire
        else:
            if entree.endswith(os.path.sep) or entree.endswith('/'):
                entree = entree[:-1]
            if not os.path.isdir(entree):
                raise NotADirectoryError(entree)
            fichs = [i for i in scandirs(entree, '', True,
                                         pattern=self.get_param('_fileselect'))]
        self.set_param('_entree', entree)

#        print ('scan_entree:fichiers a traiter',fichs)

        identifies = dict()
        non_identifies = []
        filtre_entree = self.get_param('filtre_entree', '')
        if filtre_entree:
            print('filtrage entrees ', filtre_entree)
        for fichier, chemin in fichs:
            if filtre_entree:
                if not re.search(filtre_entree, fichier):
#                    print ('ignore ',filtre_entree,fichier)
                    continue

            nom = os.path.splitext(fichier)[0].lower()
            ext = force_format if force_format else\
                  os.path.splitext(fichier)[1].lower().replace('.', '')
            if ext in liste_formats:
                f_courant = os.path.join(entree, chemin, fichier)
                identifies[chemin, nom] = ext
                if self.debug:
                    print('fichier a traiter', f_courant, ext)
                self.fichs.append(f_courant)
                self.parametres_fichiers[f_courant] = (entree, chemin, fichier, ext)
#                print('fichier a traiter', f_courant, entree, chemin, fichier, ext)
            else:
                non_identifies.append((chemin, nom, ext))
        self._valide_auxiliaires(identifies, non_identifies)

        if self.debug:
            print("fichiers a traiter", self.fichs)
        return self.fichs


    def _lecture_stats(self, stat):
        """recupere une stat pour process
        """
        return stat.to_obj(self)


    def lecture(self, fich, regle=None, reglenum=0, parms=None):
        ''' lecture d'un fichier d'entree'''
        racine, chemin, fichier, ext = self.parametres_fichiers[fich] if parms is None else parms
        self.fichier_courant = fich
        self.chemin_courant = chemin
        self.racine = racine
        print('pyetl:lecture ', fich, self.racine, chemin, fichier, ext)

#        self._setformats(ext if force_sortie is None else force_sortie)
        # positionne le stockage au bon format
        self.f_entree = Reader(ext)
        regle = self.regles[reglenum] if regle is None else regle
#        reglestart = regle.branchements.brch['next:'] if reglenum else regle
        reglestart = regle.branchements.brch['next:'] if regle else self.regles[0]
#        if self.worker:
#            print('lecture batch',os.getpid(), reglestart.ligne)
        nb_obj = self.f_entree.lire_objets(self.racine, chemin, fichier, self, reglestart)
        self.padd('_st_lu_objs', nb_obj)
        self.padd('_st_lu_fichs', 1)
        self.aff.send(('fich', 1, nb_obj))
        return nb_obj


MAINMAPPER = Pyetl() # on cree l'objet parent et l'executeur principal


def _main():
    ''' mode autotest du module '''
    print('autotest complet')
    ppp = MAINMAPPER
    if ppp.prepare_module('#autotest', []):
        ppp.process()
        print('fin procedure de test', next(ppp.maintimer))
    else:
        print('execution impossible')

if __name__ == "__main__":
    # execute only if run as a script
    _main()
