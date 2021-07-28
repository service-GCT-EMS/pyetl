# -*- coding: utf-8 -*-
import logging
import os
from io import StringIO
import time

LOGGER = logging.getLogger("pyetl")


def getlog(args):
    """recherche s il y a une demande de fichier log dans les arguments"""
    log = None
    log_level = None
    log_print = None
    if args:
        for i in args:
            if "log_file=" in i:
                log = i.split("=")[1]
            if "log_level=" in i:
                log_level = i.split("=")[1]
            if "log_print=" in i:
                log_print = i.split("=")[1]
    # print("dans getlog", log, log_level, log_print)
    return log, log_level, log_print


class DiffLogFilTer(logging.Filter):
    def filter(self, record):
        if record.levelno >= logging.DEBUG:
            return True
        try:
            precrecord = self.precrecords.get(record.funcName)
        except AttributeError:
            self.precrecords = dict()
            precrecord = None
        # print("dans filtrage", dir(record), record)
        if (
            precrecord
            and precrecord.funcName == record.funcName
            and precrecord.msg == record.msg
        ):
            precrecord.msgcount += 1
            # print(" filtrage negatif", precrecord.msgcount)
            return False
        else:
            if precrecord and precrecord.msgcount > 1:
                LOGGER.log(
                    999,
                    "message repete %d fois :%s",
                    precrecord.msgcount,
                    precrecord.msg,
                )
        record.msgcount = 1
        self.precrecords[record.funcName] = record
        return True


class GestionLogs(object):
    def __init__(self, mapper):

        self.mainmapper = mapper
        self.print_handler = None
        self.aff_handler = None
        self.file_handler = None
        self.logger = LOGGER
        self.loginited = False
        self.loglevels = {
            "DEBUG": logging.DEBUG,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
            "INFO": logging.INFO,
            "AFFICH": 999,
        }
        self.niveau_p = "INFO"
        self.log_level = "DEBUG"
        self.niveau_f = self.log_level
        self.cur_mapper = mapper
        self.fichier = None

    def set_log(self):
        """ demarre le mode affichage normal """
        self.print_handler = logging.StreamHandler()
        self.aff_handler = logging.StreamHandler()

    def set_weblog(self):
        """ demarre le mode web qui stocke les logs dans l instance """
        store = StringIO()
        self.print_handler = logging.StreamHandler(store)
        self.aff_handler = logging.StreamHandler(store)
        self.cur_mapper.webstore["log"] = store

    def resetlog(self):
        """arrete le mode weblog"""
        if self.print_handler:
            self.logger.removeHandler(self.print_handler)
        if self.aff_handler:
            self.logger.removeHandler(self.aff_handler)
        self.print_handler = logging.StreamHandler()
        self.aff_handler = logging.StreamHandler()

    def add_handlers(self):
        if self.print_handler:
            self.logger.addHandler(self.print_handler)
        if self.aff_handler:
            self.logger.addHandler(self.aff_handler)

    def configure_print_handlers(self):
        """ genere les configs d affichage """
        self.resetlog()
        # self.set_logs()
        self.set_weblog() if self.cur_mapper.mode.startswith("web") else self.set_log()
        printformatter = logging.Formatter(
            "%(levelname)-8s %(funcName)-25s: %(message)s"
        )
        self.print_handler.setFormatter(printformatter)
        self.print_handler.prec_record = ""
        self.print_handler.addFilter(lambda x: x.levelno != 999)
        self.print_handler.addFilter(DiffLogFilTer())
        self.print_handler.setLevel(self.niveau_p)
        aff_formatter = logging.Formatter("========================== %(message)s")
        self.aff_handler.setLevel(self.loglevels["AFFICH"])
        self.aff_handler.setFormatter(aff_formatter)
        self.add_handlers()

    def resetlogfile(self, mode):
        if self.file_handler:
            self.file_handler.close()
            self.logger.removeHandler(self.file_handler)
            if mode == "del":
                os.remove(self.fichier)
                print("resetlog", self.fichier)
                self.setlogfile()
            elif mode == "rotate_w":
                jour = time.strftime("%w")
                fich, ext = os.path.splitext(self.fichier)
                fich = fich + "_" + jour
                self.fichier = fich + "." + ext
                os.remove(self.fichier)
                self.setlogfile()

    def setlogfile(self):
        fichier = self.fichier
        os.makedirs(os.path.dirname(fichier), exist_ok=True)
        fileformatter = logging.Formatter(
            "%(asctime)s::%(levelname)s::%(module)s.%(funcName)s" + "::%(message)s"
        )
        #        infoformatter = logging.Formatter('%(asctime)s::%(levelname)s::%(message)s')
        # création d'un handler qui va rediriger une écriture du log vers
        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        self.file_handler = logging.FileHandler(fichier)
        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        self.file_handler.setLevel(self.niveau_f)
        self.file_handler.setFormatter(fileformatter)
        print("ajout filehandler", self.fichier, self.niveau_f)
        self.logger.addHandler(self.file_handler)
        self.logger.log(999, "demarrage pyetl %s", self.cur_mapper.getvar("VERSION"))
        self.logger.info("commande:   %s", self.cur_mapper.getvar("pyetl_script_ref"))
        args = self.cur_mapper.getvar("pyetl_script_args")
        if args:
            self.logger.info("parametres: %s", args)

    def initlog(self, mapper, loginfo=None, force=False):
        """initialise le contexte de logging (parametres de site environnement)"""
        # if self.loginited and not force and mapper == self.cur_mapper:
        if self.loginited and not force:
            return  # on a deja fait le boulot
        print("initlog", mapper.idpyetl, loginfo)
        self.cur_mapper = mapper
        log_file = self.fichier
        log_print = self.niveau_p
        log_level = self.log_level
        if loginfo:
            logfile, loglevel, logprint = loginfo
            log_file = logfile or log_file
            log_level = loglevel or log_level
            log_print = logprint or log_print
        fichier = mapper.getvar("log_file", log_file)
        log = mapper.getvar("log_level", log_level)
        affich = mapper.getvar("log_print", log_print)
        logmode = mapper.getvar("log_mode", "prod")
        logging.captureWarnings(True)
        self.loginited = True

        #        self.aff = self._patience(0, 0) # on initialise le gestionnaire d'affichage
        #        next(self.aff)

        # def initlogger(self, fichier=None, log="DEBUG", affich="INFO"):
        """ création de l'objet logger qui va nous servir à écrire dans les logs"""
        # on met le niveau du logger à DEBUG, comme ça il écrit tout dans le fichier log s'il existe
        logger = self.logger
        if logmode == "prod":
            logging.raiseExceptions = False
        worker = mapper.worker

        self.niveau_f = self.loglevels.get(log, logging.INFO)
        self.niveau_p = self.loglevels.get(affich, logging.ERROR)
        self.loglevel = min(self.niveau_f, self.niveau_p)
        # print ('niveaux de logging',niveau_f,niveau_p)
        logger.setLevel(self.loglevel)

        if not worker:
            print("initialisation log", affich, log, "(", fichier, ")")
            self.configure_print_handlers()
            if fichier != self.fichier:
                self.resetlogfile("stop")
                self.fichier = fichier
                if self.fichier:
                    self.setlogfile()
        else:
            pass

    def setdebug(self):
        """positionne le logger en mode debug pour l affichage d objets"""
        self.logger.setLevel(min(self.loglevel, self.loglevels["DEBUG"]))
        if self.print_handler:
            self.print_handler.setLevel(min(self.niveau_p, self.loglevels["DEBUG"]))
        if self.file_handler:
            self.file_handler.setLevel(min(self.niveau_f, self.loglevels["DEBUG"]))

    def stopdebug(self):
        self.logger.setLevel(self.loglevel)
        if self.print_handler:
            self.print_handler.setLevel(self.niveau_p)
        if self.file_handler:
            self.file_handler.setLevel(self.niveau_f)

    def shutdown(self):
        self.mainmapper.logger.info("arret logs")
        if self.mainmapper.parallelmanager:
            self.mainmapper.stoplistener()
            self.mainmapper.parallelmanager.shutdown()
        logging.shutdown()
