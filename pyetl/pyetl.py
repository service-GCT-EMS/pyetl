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
from  .formats.formats import Reader, Stat
from  .moteur.interpreteur_csv import lire_regles_csv, reinterprete_regle,\
         interprete_ligne_csv, map_vars
from  .moteur.compilateur import compile_regles
from  .moteur.moteur import Moteur, Macro
from  .moteur.fonctions import COMMANDES, SELECTEURS
from  .moteur.fonctions.outils import scandirs
from  .schema.schema_interne import init_schema # schemas
from  .schema.schema_io import ecrire_schemas, ecrire_schema_csv # schemas
#from  .outils.crypt import crypter, decrypt

VERSION = "0.8.2.2_d"
LOGGER = logging.getLogger('pyetl') # un logger
MODULEDEBUG = False

def initlogger(fichier=None, niveau_f=logging.DEBUG, niveau_p=logging.ERROR):
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
        # création d'un handler qui va rediriger une écriture du log vers
        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        file_handler = logging.FileHandler(fichier)
        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        file_handler.setLevel(niveau_f)
        file_handler.setFormatter(fileformatter)
        LOGGER.addHandler(file_handler)
        LOGGER.log("pyetl:"+VERSION)

initlogger()


def initpyetl(traitement, mapping, args, env=None, log=None):
    """ initialisation standardisee: cerre l'objet pyetl de base"""
    env = env if env is not None else os.environ
    if log:
        traitement.set_param('logfile', log)
        initlogger(fichier=log)
    traitement.init_environ(env)
    try:
        traitement.prepare_module(mapping, args)
        return True
    except SyntaxError:
        LOGGER.critical('erreur script '+mapping)
    return False


def runpyetl(mapping, args, env=None, log=None):
    """ lancement standardise"""
    print("pyetl", VERSION, mapping, args, log)
    if initpyetl(MAINMAPPER, mapping, args, env=env, log=log):
        nb_total, nb_fichs, ng2, nf2 = MAINMAPPER.process()

    else:
        print('arret du traitement ')
        return
    if nb_total:
        print(nb_total, "objets lus")
    if MAINMAPPER.dbread:
        print(MAINMAPPER.dbread, "objets lus en base de donnees")
    if MAINMAPPER.moteur:
        print(MAINMAPPER.moteur.dupcnt, "objets dupliques")
    if ng2:
        print(ng2, "objets ecrits dans ", nf2, "fichiers ")
    MAINMAPPER.signale_fin()
    duree, _ = next(MAINMAPPER.maintimer)
    duree += 0.001
    print("fin traitement total :", nb_fichs, "fichiers traites en ",
          int(duree*1000), "millisecondes")

    if nb_total:
        print('perf lecture  :', int(nb_total/duree), 'o/s')
    if ng2:
        print('perf ecriture :', int(ng2/duree), 'o/s')


def initparallel(mapping, args, params, macros, env=None, log=None):
    """initialisatin d'un process worker pour un traitement parallele"""
    if initpyetl(MAINMAPPER, mapping, args, env=env, log=log):
       MAINMAPPER.macros.update(macros)
       MAINMAPPER.parms.update(params)
       return True
    return False

def parallelbatch(mapping, entree, sortie, args):
    """execute divers traitements en parallele"""
    processor = MAINMAPPER.getpyetl(mapping, liste_params=args,
                                    entree=entree, rep_sortie=sortie)
    if processor is None:
        return False
    lu_total, lu_fichs, nb_total, nb_fichs = processor.process()
    return lu_total, lu_fichs, nb_total, nb_fichs

def parallelprocess(file):
    '''traitement individuel d'un fichier'''
    try:
        nb_lu = MAINMAPPER.lecture(file)
    except StopIteration as arret:
#            print("intercepte abort",abort.args[0])
        return -1
#    MAINMAPPER.aff.send(('fich', 1, nb_lu))
    return nb_lu

def endparallel():
    '''termine un traitement parallele'''
    schema = None
    try:
        nb_total, nb_fichs, schema = MAINMAPPER.menage_final()
        retour = True
    except StopIteration:
        nb_total, nb_fichs = MAINMAPPER.sorties.final()
        retour = False
#        print('mapper: fin traitement donnees:>', entree, '-->', self.regle_sortir.params.cmp1.val)
    return (retour, nb_total, nb_fichs, schema)


def runparallel(mapping, args, entree, mode, params, macros, env=None, log=None):
    """ lancement en mode multiprocessing"""
    if env is None:
        env = os.environ
#    MAINMAPPER[0] = None
    if MAINMAPPER[0] is None or mode == "PB":
        traitement = Pyetl(env=env)
        print("pyetl worker", os.getpid(), traitement.idpyetl, VERSION,
              mapping, args, mode if mode else "")
        if log:
            traitement.set_param('logfile', log)
        try:
            if traitement.prepare_module(mapping, args, mode=mode, context=(macros, params)):
                print(" module pret ", os.getpid(), traitement.idpyetl)
                MAINMAPPER[0] = traitement
            else:
                return 0, 0, []
        except SyntaxError:
            print('erreur script')
            return 0, 0, []
        try:
            traitement.set_param("entree", entree)
            nb_total, nb_fichs, ng2, nf2 = traitement.process(entree)
        except SyntaxError:
            print('erreur execution')
            return 0, 0, []
    else:
        try:
            traitement = MAINMAPPER[0]
            print("trouve module", os.getpid(), MAINMAPPER[0].idpyetl)
        except:
            print('erreur script', os.getpid(), traitement.idpyetl, mapping, args)
            return 0, 0, []

    print("pyetl work:", os.getpid(), traitement.idpyetl, VERSION,
          mapping, args, mode if mode else "")
    try:
        traitement.set_param("entree", entree)
        nb_total, nb_fichs, ng2, nf2 = traitement.process()
    except SyntaxError:
        print('erreur execution')
        return 0, 0, []

    retour = traitement.retour
    print('retour ', retour)
    return (nb_total, ng2, retour)





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
        self.runparallel = runparallel
        self.initparallel = initparallel
        self.parallelprocess = parallelprocess
        self.parallelbatch = parallelbatch
        self.endparallel = endparallel


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
        self.dbread = 0 # objets lus en base

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
#        self.prepare_module()
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

    def prepare_module(self, regles, liste_params, mode=None, context=None):
        ''' prepare le module pyetl pour l'execution'''

        if isinstance(regles, list):
            self.nompyetl = 'pyetl'
            self.liste_regles = regles
        else:
            self.fichier_regles = regles
            self.nompyetl = regles
            self.rdef = os.path.dirname(regles) # nom de repertoire des regles
#        print ('prepare_module1b',self.get_param('_sortie'))
        self._traite_params(liste_params)
#        print ('prepare_module1c',self.get_param('_sortie'))



        LOGGER.debug('prepare_module'+ repr(regles)+  repr(liste_params)+
                          self.get_param('_sortie', 'pas_de_sortie'))

        if self.fichier_regles or self.liste_regles:
            erreurs = self.commandes_speciales()
            if not self.done:
                try:
                    erreurs = self.lecteur_regles(self.fichier_regles,
                                                  liste_regles=self.liste_regles)
                except KeyError as ker:
                    LOGGER.critical('erreur lecture '+ker.__repr__())
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
        prochain = nbaffich
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
            if message == 'interm':
                cmp = 'int'
            if message == 'tab':
                ftype = 'tables'
            msg = "mapper: --%s----> nombre d'objets lus %8d dans %4d %s en %5d "+\
                  "secondes %5d o/s, inst %5d"
            LOGGER.info(msg, cmp, nbobj, tabletotal, ftype, int(duree), int((nbobj)/duree),
                        int((nbobj-nop)/(interv+0.001)))
            print(msg %(cmp, nbobj, tabletotal, ftype, int(duree), int((nbobj)/duree),
                        int((nbobj-nop)/(interv+0.001))))
            return (int(prochain/nbaffich)+1)*nbaffich

        while True:
            message, nbfic, nbval = yield
#            nbtotal += nbval
            tabletotal += nbfic
            if message == 'init':
                duree, interv = next(temps)
#                print("init  : --------->", int(duree*1000), 'ms')
            elif message == 'end':
                nbtotal += nbval
#                tabletotal += nbfic
                affiche(message, nbtotal)
                break
            elif nbtotal+nbval >= prochain:
                prochain = affiche(message, nbtotal+nbval)
                nop = nbtotal+nbval
            if message != 'interm':
                nbtotal += nbval

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
#        print('getpyetl:preparation_module' ,liste_params, petl.idpyetl, petl.get_param('_sortie'))
#        if petl.prepare_module(regles, liste_params, mode, context=None):
#            print('getpyetl:apres preparation_module' ,petl.idpyetl, petl.get_param('_sortie'))
            return petl
        print('erreur getpyetl', regles)
        return None

#    def getpool(self, nbworkers=0):
#        '''cree un pool d'execution en mode thread'''
#
#        if self.parent:
#            return []
#        #seul le processus de base a le droit de creer des threads
#        self.workers = [Worker(self, self.nompyetl + '_' + str(i), mode='worker')
#                        for i in range(nbworkers)]

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
#                    if liste[0].startswith('**'):# cryptage
#                        if not init:
#                            self.load_paramgroup('init', fin=False)
#                            init = True
#                        nom_p = nom_p[2:]
##                        print("decryptage", nom_p, val)
#                        val = self.decrypt(val)
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

#            if nom:  # noms qualifies
#                self.parms.update((i+'_'+nom, j) for i, j in self.site_params[clef])
#            self.parms.update(self.site_params[clef])
#            print ('pg:definition groupe local',nom,valeur, self.site_params[valeur])
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
            else:
                if nom:
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

        self.parms.update([("mode_sortie", "B"), ("memlimit", "100000"), ('sans_entree', ''),
                           ("nbaffich", "100000"), ('filtre_entree', ''), ('sans_sortie', ''),
                           ("tmpdir", '.'), ("F_entree", ''), ('racine', ''),
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
#        self.parms['xmlheader'] = self.get_param('xmldefaultheader')

    def get_param(self, nom, defaut='', local=False, groupe=None):
        ''' fournit la valeur d'un parametre '''
        if groupe:
            valeur = self.get_param(nom+'_'+groupe, defaut=None)
            if valeur is not None:
                return valeur
        if nom in self.parms:
#            print ('lecture parametre',nom,self.parms[nom],self.idpyetl)
            return self.parms[nom]
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

            return 0, 0, nb_total, nb_fichs
        if debug:
            self.debug = debug
        entree = self.get_param('_entree')
        if self.get_param('sans_entree'):
            entree = None
#        print("process",entree, self.regles)
        if isinstance(entree, Stat):
            nb_total = self._lecture_stats(entree)
            return nb_total, 1

        abort = False
        duree = 0
        lu_total, lu_fichs = 0, 0
#        interv_affich = int(self.get_param("nbaffich", "100000"))
#        nbaffich = interv_affich
        if entree and entree.strip() and entree != '!!vide':
            print('mapper: debut traitement donnees:>'+entree+ '-->',
                  self.regle_sortir.params.cmp1.val)
            try:
                fichs = self.scan_entree()
            except NotADirectoryError as err:
                print("!!!!!!!!!!!!!!!!!!!!!attention repertoire d'entree inexistant:", err)
                fichs = None
            if fichs:
                self.aff = self._patience(lu_fichs, lu_total)
                next(self.aff)
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
                        break
                    lu_total += nb_lu
                    lu_fichs += 1
                    self.aff.send(('fich', 1, nb_lu))
                duree, _ = self.aff.send(('end', 0, 0))
            else:
                print('pas de fichiers en entree')
            print('mapper: ---------> fin traitement donnees:', int(duree))
            print('mapper: ---------> finalisation:')
        else:
#            if mode:
##                self._setformat_sortie(mode) # on force le format de sortie si necessaire
#                print('process: forcage sortie', mode, self.moteur.regle_sortir)
##            print('traitement sans entree')
            try:
                self.moteur.traitement_virtuel(unique=1)
            except StopIteration as arret:
                abort = True
        if abort:
            nb_total, nb_fichs = self.sorties.final()
        else:
            try:
                nb_total, nb_fichs, _ = self.menage_final()
            except StopIteration:
                nb_total, nb_fichs = self.sorties.final()
#        print('mapper: fin traitement donnees:>', entree, '-->', self.regle_sortir.params.cmp1.val)
        return lu_total, lu_fichs, nb_total, nb_fichs

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

        nf2, ng2 = self.sorties.final()

        self._ecriture_stats()
        self.macro_final()

        if mode_schema == 'SS':
            schemas = ecrire_schema_csv(None, self.schemas, mode=self.get_param('force_schema', 'util') )
            return ng2, nf2, schemas

        else:
            self._ecriture_schemas()
            return ng2, nf2, None


    def macro_final(self):
        """ execute une macro finale"""
        macrofinale = self.get_param('_end', local=True) # on travaille par instance
        if not macrofinale:
            macrofinale = self.get_param('#end', local=True) # on travaille par instance
#        print ('finalisation commande ', macrofinale, self.idpyetl)
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
                            '1': 'non_vide', # on ne sort que les schemas des classes non vides
                            '2': 'util', # sort les schemas des classes utilisees dans le traitement
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
#        print ('ecriture schemas ', mode_schema)
        if mode_schema in {'all', 'int', 'fusion'} and not self.done:
            self.moteur.traitement_virtuel() # on force un peu pour creer toutes les classes
        ecrire_schemas(self, mode_schema, formats=self.get_param("format_schema", 'csv'))

    def _ecriture_stats(self):
        '''stockage des stats '''
#        print("pyetl : stats a ecrire",self.idpyetl, self.stats.keys(), self.statprint)
        rep_sortie = self.get_param('_sortie')
        for i in self.stats:
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
                                     codec=codec_sortie)

        if self.get_param('fstat'):  # ecriture de statistiques de fichier
            if rep_sortie:
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
                    print('inconnu ', chemin, nom, extinc)

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
            self.set_param('_entree', entree)
        else:
            if not os.path.isdir(entree):
                raise NotADirectoryError(entree)
            fichs = [i for i in scandirs(entree, '', True,
                                         pattern=self.get_param('_fileselect'))]
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
                self.parametres_fichiers[f_courant] = (chemin, fichier, ext)
#                print('fichier a traiter', f_courant, fichier, ext)
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

    def lecture(self, fich, regle=None):
        ''' lecture d'un fichier d'entree'''
        chemin, fichier, ext = self.parametres_fichiers[fich]
        self.fichier_courant = fich
        self.chemin_courant = chemin
        self.racine = self.get_param('_entree')
#        print('pyetl:lecture ', self.entree, self.parametres_fichiers[fich])

#        self._setformats(ext if force_sortie is None else force_sortie)
        # positionne le stockage au bon format
        self.f_entree = Reader(ext)
        reglestart = regle.branchements.brch['next:'] if regle else self.regles[0]
        nb_obj = self.f_entree.lire_objets(self.racine, chemin, fichier, self, reglestart)

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
