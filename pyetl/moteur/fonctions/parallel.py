# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 11:06:21 2019

@author: 89965
gestion du parallelisme sur les entrees/sorties

"""
from logging import StreamHandler
import os
from queue import Empty
import time

from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager, Queue

from pyetl.vglobales import getmainmapper

from pyetl.schema.schema_io import integre_schemas, retour_schemas
from pyetl.formats.interne.stats import ExtStat
from .outils import renseigne_attributs_batch, getfichs, printexception

paralleldebug = 0


def setparallel(mapper):
    """enregistre les fonctions de gestion du parallelisme"""
    mapper.execparallel_ext = execparallel_ext
    mapper.iterparallel_ext = iterparallel_ext
    mapper.traite_parallel = traite_parallel
    mapper.gestion_parallel_batch = gestion_parallel_batch
    mapper.gestion_parallel_load = gestion_parallel_load
    mapper.parallelmanager = None
    mapper.msgqueue = None
    mapper.loglistener = None
    mapper.stoplistener = stoplistener


def getmanager(mapper):
    if mapper.worker:
        return None
    if not mapper.parallelmanager:
        mapper.parallelmanager = Manager()
    return mapper.parallelmanager


def getqueue():
    """recupere le gestionnaire de files"""
    mapper = getmainmapper()
    if not mapper.msgqueue:
        manager = getmanager(mapper)
        if manager:
            mapper.msgqueue = mapper.parallelmanager.Queue()
            mapper.logqueue = mapper.parallelmanager.Queue()
    # mapper.msgqueue = Queue() # ne marche pas sous windows
    # mapper.logqueue = Queue()
    return mapper.msgqueue, mapper.logqueue


def setqueuhandler(queue, wid=""):
    """ ajoute une gestion de file de messages pour le traitment en multiprocessing"""
    import logging
    import logging.handlers

    mapper = getmainmapper()
    if queue is None:
        loglistener = logging.handlers.QueueListener(
            mapper.logqueue, *mapper.logger.handlers, respect_handler_level=True
        )
        loglistener.start()
        mapper.logger.info("gestionnaire logs parallele : demarrage listener:", wid)
        # print("-------------------demarrage listener")
        mapper.loglistener = loglistener
    else:
        # on est sur le worker on ajoute un writer de file
        mapper.logqueue = queue
        queueformatter = logging.Formatter("(W" + str(wid) + "):%(message)s")
        queuehandler = logging.handlers.QueueHandler(queue)
        queuehandler.setFormatter(queueformatter)
        mapper.logger.addHandler(queuehandler)


def stoplistener():
    mapper = getmainmapper()
    # print("arret listener", mapper.loglistener)

    if mapper.loglistener:
        # mapper.logger.info("arret listener")
        mapper.loglistener.enqueue_sentinel()
        # time.sleep(1)
        mapper.loglistener.stop()
        # mapper.logqueue._close()
        # mapper.logqueue.join_thread()
        # mapper.loglistener = None
    # print("listener arrete")


def initparallel(parametres):
    """initialisatin d'un process worker pour un traitement parallele"""
    #    commandes, args, params, macros, env, log = parametres
    if parametres:
        params, macros, env, loginfo, schemas, msgq, logqueue = parametres
        # print("initialisation worker", os.getpid(), loginfo, msgq, logqueue)
    else:
        print("initialisation sans parametres")
        return (os.getpid(), False)
    mainmapper = getmainmapper()
    if mainmapper is None:
        print("erreur initialisation", os.getpid())
        return None

    if mainmapper.gestion_log.loginited:
        #        print("pyetl double init", os.getpid())
        time.sleep(1)
        return None
    if paralleldebug:
        print(
            "pyetl initworker",
            os.getpid(),
            schemas.keys(),
            mainmapper,
            mainmapper.schemas,
        )
    mainmapper.worker = True
    mainmapper.context.update(params)
    mainmapper.initlog()
    mainmapper.macrostore.macros.update(macros)
    mainmapper.msgqueue = msgq
    mainmapper.logqueue = logqueue

    # print("initparallel: recuperation parametres", loginfo)
    # print ('initparallel: valeur de import',params.get('import'))
    integre_schemas(mainmapper, schemas)
    mainmapper.parametres_lancement = parametres
    time.sleep(1)
    return (os.getpid(), True)


def setparallelid(parametres):
    """positionne un numero de worker et initialise les commandes """
    pidset, commandes, args = parametres
    mainmapper = getmainmapper()

    if mainmapper.getvar("_wid"):
        time.sleep(1)
        return None
    wid = str(pidset[os.getpid()])
    mainmapper.setvar("_wid", wid)
    init = mainmapper.initpyetl(commandes, args)
    setqueuhandler(mainmapper.logqueue, wid=wid)
    mainmapper.logger.info("pyetl initworker " + str(os.getpid()))
    if paralleldebug:
        print("setparallelid apres init", mainmapper.getvar("_wid"), commandes, args)

    return (os.getpid(), mainmapper.getvar("_wid"), init)


def set_parallelretour(mapper, valide):
    """positionne les variables de retour pour l'execution en parallele"""

    retour = {
        "pid": os.getpid(),
        "wid": mapper.getvar("_wid"),
        "valide": valide,
        "stats_generales": mapper.getstats(),
        "retour": mapper.retour,
        "schemas": retour_schemas(
            mapper.schemas, mode=mapper.getvar("force_schema", "util")
        ),
        # "stats": {nom: stat.retour() for nom, stat in mapper.statstore.stats.items()},
        "stats": mapper.statstore.retour(),
        "timers": {
            "fin": time.time(),
            "debut": mapper.starttime,
            "duree": round(time.time() - mapper.starttime, 2),
        },
    }
    return retour


def parallelbatch(id, parametres_batch, regle):
    """execute divers traitements en parallele"""
    #    print ("pyetl startbatch",os.getpid(), parametres_batch[:3])
    numero, mapping, entree, sortie, args = parametres_batch
    mainmapper = getmainmapper()
    processor = mainmapper.getpyetl(
        mapping, liste_params=args, entree=entree, rep_sortie=sortie
    )
    if processor is None:
        print("pyetl echec batchworker", os.getpid(), mapping, args)
        return (numero, {})

    processor.process()
    retour = set_parallelretour(processor, True)
    processor.logger.info(
        "retour batchworker (%d:%d) %s %s -> %s",
        os.getpid(),
        processor.idpyetl,
        str(mapping),
        str(args),
        str(processor.retour),
    )
    # print(
    #     "pyetl batchworker",
    #     os.getpid(),
    #     processor.idpyetl,
    #     mapping,
    #     args,
    #     "->",
    #     processor.retour,
    # )
    processor.cleanschemas()
    return (numero, retour)


def parallelprocess(numero, file, regle):
    """traitement individuel d'un fichier"""
    mainmapper = getmainmapper()
    try:
        # print ('---------------------------------------' + mainmapper.getvar("_wid") + '-worker:lecture', file, regle)
        nom, parms = file
        nb_lu = mainmapper.lecture(file, reglenum=regle, parms=parms)
    except StopIteration as arret:
        return numero, -1
    except Exception as exc:
        print(
            "===="
            + mainmapper.getvar("_wid")
            + "=erreur de traitement parallele non gérée"
        )
        print("====regle courante:", regle)
        printexception()
        raise
    return numero, nb_lu


def objprocess(numero, objet, regle):
    mainmapper = getmainmapper()


def endparallel(test=None):
    """termine un traitement parallele"""
    mainmapper = getmainmapper()
    nb_total = 0
    nb_fichs = 0
    if mainmapper.ended:
        #        print("pyetl double end", os.getpid())
        time.sleep(1)
        return None
    try:
        mainmapper.menage_final()
        succes = True
    except StopIteration:
        nb_total, nb_fichs = mainmapper.sorties.final(mainmapper.idpyetl)
        mainmapper.padd("_st_wr_fichs", nb_fichs)
        mainmapper.padd("_st_wr_objs", nb_total)
        succes = False
    retour = set_parallelretour(mainmapper, succes)

    #    print("-----pyetl batchworker end", os.getpid(), succes, nb_total, nb_fichs)
    if succes:
        mainmapper.logger.info(
            "-----pyetl batchworker end "
            + str(os.getpid())
            + " succes "
            + str(nb_total)
            + " "
            + str(nb_fichs)
        )
    else:
        mainmapper.logger.error(
            "-----pyetl batchworker end "
            + str(os.getpid())
            + " echec "
            + str(nb_total)
            + " "
            + str(nb_fichs)
        )

    mainmapper.ended = True

    return (os.getpid(), retour)


def parallelexec(executor, nprocs, fonction, args):
    """gere les appels de fonction uniques d'un pool de process
    et s'assure que chaque process du pool est appelé"""

    rfin = dict()
    # print('pexec', fonction)
    retours = [executor.submit(fonction, args) for i in range(nprocs)]
    while len(rfin) < nprocs:
        if len(retours) < nprocs:
            retours.append(executor.submit(fonction, args))
        attente = []
        #        print ('retours', retours)
        for i in retours:
            if not i.done():
                attente.append(i)
            else:
                # print ('termine',i)
                exception = i.exception()
                if exception:
                    print("retour en erreur", exception)
                    nprocs -= 1
                    continue
                retour_final = i.result()
                #                print('retour pexec ',retour_final)
                if retour_final is not None:
                    rfin[retour_final[0]] = retour_final[1:]
        retours = attente
    return rfin


def suivi_job(mapper, work):
    """suit un ensemnle de process en parallele"""
    rfin = dict()
    attente = []
    # getqueue()
    mapper.aff.send(("check", 0, 0))
    for job in work:
        if not job.done():
            attente.append(job)
        else:
            #            print ('termine',job)
            #            print ('retour', job.result())
            retour_process = job.result()
            # print('retour pexec ',job,retour_process)
            if retour_process is not None:
                num_obj, retour = retour_process
                if isinstance(retour, dict):  # c'est un retour complet de type batch
                    rfin[num_obj] = 0
                    try:
                        mapper.logger.info(
                            "retour batch %s : %s obj  en %s s",
                            num_obj,
                            retour["stats_generales"]["_st_lu_objs"],
                            retour["timers"]["duree"],
                        )
                    except KeyError:
                        mapper.logger.error("erreur batch %d ", num_obj)
                    # print(
                    #     "retour batch",
                    #     num_obj,
                    #     retour["stats_generales"]["_st_lu_objs"],
                    #     retour["timers"]["duree"],
                    #     "s",
                    # )

                else:
                    rfin[num_obj] = (
                        retour + rfin[num_obj] if num_obj in rfin else retour
                    )
                    # print("retour job", retour)
                    # mapper.aff.send(("interm", 1, retour))
                    mapper.aff.send(("fich", 1, retour))
    work[:] = attente
    return rfin


def parallelmap_suivi(mapper, executor, fonction, arglist, work=None):
    """gere les appels classique mais avec des retours d'infos"""

    rfin = dict()
    #    print('start pexec')
    if work is None:
        work = [executor.submit(fonction, *arg) for arg in arglist]

    while work:
        rfin.update(suivi_job(mapper, work))
        time.sleep(0.1)
    return rfin


def paralleliter_suivi(regle, executor, fonction, argiter):
    """gere les appels classique mais avec des retours d'infos en s'appuyant sur
    un iterateur ce qui permet de lancer les traitements sans que toutes les
    entree soient généréés"""
    rfin = dict()
    mapper = regle.stock_param
    paralleldebug = 0
    if paralleldebug:
        print("start paralleliter_suivi", fonction, argiter)
    #    work = [executor.submit(fonction, *arg) for arg in arglist]
    waitlist = []
    jobs = []
    marge = executor._max_workers + 2
    for arg in argiter:
        if paralleldebug:
            print("paralleliter_suivi : arg", arg)
        if arg is not None:
            #            print ('piter: recu ', arg, len(jobs))
            waitlist.append(arg)
            if paralleldebug:
                print("liste:", waitlist)
            if len(jobs) < marge:
                try:
                    waitlist.sort()
                    taille, job = waitlist.pop()
                    if paralleldebug:
                        print("traitement job", job, fonction)
                    # submit_job(jobs, job, regle, executor, fonction)
                    jobs.append(executor.submit(fonction, 1, job, regle.index))
                except IndexError:
                    time.sleep(0.1)
            # print("paralleliter_suivi : fin traitement", arg, jobs)
        rfin.update(suivi_job(mapper, jobs))
        # print('paralleliter_suivi : dodo', arg)
        time.sleep(0.1)
    for arg in sorted(waitlist, reverse=True):
        taille, job = arg
        jobs.append(executor.submit(fonction, 1, job, regle.index))
        # submit_job(jobs, job, regle, executor, fonction)

    rfin.update(parallelmap_suivi(mapper, None, None, None, work=jobs))
    return rfin


def prep_parallel(regle, fonction, reprog=False):
    """ initialise le mecanisme pour la parallelisation d'une regle"""
    multi, _ = regle.get_max_workers()
    if multi > 1 or reprog and not regle.stock_param.worker:
        regle.store = True
        regle.traite_stock = fonction
        regle.nbstock = 0
        regle.traite = 0
        regle.tmpstore = []
        regle.reprog = reprog  # pour le mode boucle
    return multi


def gestion_parallel_load(regle):
    """prepare les chargements paralleles"""
    multi = prep_parallel(regle, traite_parallel_load)


#    print("preparation parallel_loader", multi, regle.chargeur, 'st:',regle.store)


def prepare_env_parallel(regle):
    """prepare les parametres pour un lancement en parallele"""
    mapper = regle.stock_param
    env = mapper.env if isinstance(mapper.env, dict) else None
    def_regles = mapper.liste_regles if mapper.liste_regles else mapper.fichier_regles
    #        print("preparation exec parallele", def_regles, mapper.liste_params)
    mapper.logger.info(
        " ".join(
            ("preparation exec parallele", str(def_regles), str(mapper.liste_params))
        )
    )
    schemas = retour_schemas(mapper.schemas, mode="int")
    return schemas, env, def_regles


def traite_parallel(regle):
    """traite les operations en parallele"""

    mapper = regle.stock_param

    nprocs, _ = regle.get_max_workers()
    num_regle = regle.index
    rdict = dict()
    schemas, env, def_regles = prepare_env_parallel(regle)
    logger = regle.stock_param.logger
    logger.info("passage en mode parallel sur %d process", nprocs)
    # print("passage en mode parallel sur ", nprocs, "process", num_regle, regle)
    if mapper.worker:
        logger.error(
            "un worker ne peut pas passer en parallele %s", mapper.getvar("_wid")
        )
        # print("un worker ne peut pas passer en parallele", mapper.getvar("_wid"))
        raise RuntimeError
    fonction = parallelprocess if regle.parallelmode == "process" else parallelbatch
    msgqueue, logqueue = getqueue()
    setqueuhandler(None)
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
        # TODO en python 3.7 l'initialisation peut se faire dans le pool
        mapper.logger.info("initialisation parallele")
        # print("initialisation parallele", schemas.keys())
        rinit = parallelexec(
            executor,
            nprocs,
            initparallel,
            (
                regle.context.getvars(),
                mapper.macrostore.macros,
                env,
                None,
                schemas,
                msgqueue,
                logqueue,
            ),
        )
        workids = {pid: n + 1 for n, pid in enumerate(rinit)}
        #        print ('workids',workids)
        mapper.logger.info(" ".join(("workids", str(workids))))
        parallelexec(
            executor, nprocs, setparallelid, (workids, def_regles, mapper.liste_params)
        )
        if regle.debug or paralleldebug:
            print("traite_parallel: retour init", rinit, num_regle)
        #        results = executor.map(parallelprocess, idobj, entrees, num_regle)
        rdict = paralleliter_suivi(regle, executor, fonction, regle.listgen)
        rfin = parallelexec(executor, nprocs, endparallel, "")
    #        if regle.debug:
    #        print ('retour')
    for i in rfin:
        retour = rfin[i][0]
        if retour:
            # print(
            #     i,
            #     "worker",
            #     retour["wid"],
            #     "traites",
            #     retour["stats_generales"].get("_st_lu_objs", "0"),
            #     list(sorted(retour["schemas"].keys())),
            # )
            for param in retour["stats_generales"]:
                mapper.padd(param, retour["stats_generales"][param])
            mapper.logger.info(
                "retour stats (%s) : %s",
                retour["wid"],
                str(retour["stats_generales"].get("_st_lu_objs", "0")),
            )
            #            print ('traitement schemas ', retour["schemas"])
            integre_schemas(mapper, retour["schemas"])

            mapper.statstore.store_extstats(retour["stats"])

            # for nom, entete, contenu in retour["stats"].values():
            #     if nom not in mapper.statstore.stats:
            #         mapper.statstore.stats[nom] = ExtStat(nom, entete)
            #     mapper.statstore.stats[nom].add(entete, contenu)
        else:
            print("erreur retour", rfin)
    regle.nbstock = 0
    # time.sleep(1)  # on attend une seconde que tout se finisse


def traite_parallel_load(regle):
    """traite les chargements en parallele"""

    idobj = []
    entrees = []
    mapper = regle.stock_param

    for num, obj in enumerate(regle.tmpstore):
        fichs = list(getfichs(regle, obj, sort=True))
        idobj.extend([num] * len(fichs))
        entrees.extend(fichs)
    arglist = [(i, j, regle.index) for i, j in zip(idobj, entrees)]
    nprocs, _ = regle.get_max_workers()
    # num_regle = [regle.index] * len(entrees)
    rdict = dict()
    schemas, env, def_regles = prepare_env_parallel(regle)
    #    print('parallel load',entrees,idobj, type(mapper.env))
    msgqueue, logqueue = getqueue()
    setqueuhandler(None)
    # print("passage en parallele sur ", nprocs)
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
        # TODO en python 3.7 l'initialisation peut se faire dans le pool
        rinit = parallelexec(
            executor,
            nprocs,
            initparallel,
            (
                regle.context.getvars(),
                mapper.macrostore.macros,
                env,
                None,
                schemas,
                msgqueue,
                logqueue,
            ),
        )
        workids = {pid: n + 1 for n, pid in enumerate(rinit)}
        mapper.logger.info(" ".join(("workids", str(workids))))
        parallelexec(
            executor, nprocs, setparallelid, (workids, def_regles, mapper.liste_params)
        )
        if regle.debug:
            print("retour init", rinit, regle.index)
        #        results = executor.map(parallelprocess, idobj, entrees, num_regle)
        rdict = parallelmap_suivi(mapper, executor, parallelprocess, arglist)

        rfin = parallelexec(executor, nprocs, endparallel, "")
    #        if regle.debug:
    #        print ('retour')
    for i in rfin:
        retour = rfin[i][0]
        # print(
        #     i,
        #     "worker",
        #     retour["wid"],
        #     "traites",
        #     retour["stats_generales"]["_st_lu_objs"],
        #     list(
        #         sorted([(a, len(b["classes"])) for a, b in retour["schemas"].items()])
        #     ),
        # )
        for param in retour["stats_generales"]:
            mapper.padd(param, retour["stats_generales"][param])
        mapper.logger.info(
            "retour stats (" + retour["wid"] + ") : %s",
            str(retour["stats_generales"].get("_st_lu_objs", "0")),
        )
        #            print ('traitement schemas ', retour["schemas"])
        integre_schemas(mapper, retour["schemas"])

        mapper.statstore.store_extstats(retour["stats"])

        # for nom, entete, contenu in retour["stats"].values():
        #     if nom not in mapper.statstore.stats:
        #         mapper.statstore.stats[nom] = ExtStat(nom, entete)
        #     mapper.statstore.stats[nom].add(entete, contenu)

    traite = regle.stock_param.moteur.traite_objet  # fonction de traitement
    # print("retour multiprocessing ", rdict.keys(), rfin.keys(), regle.tmpstore)

    for i in sorted(rdict):
        obj = regle.tmpstore[i]
        if regle.params.att_sortie.val:
            obj.attributs[regle.params.att_sortie.val] = str(rdict[i])
        mapper.logger.info("fin traitement parallele")
        # print("fin traitement parallele", obj, rdict)
        traite(obj, regle.branchements.brch["endstore"])
    regle.nbstock = 0


def gestion_parallel_batch(regle):
    """ initialise la gestion des batch en parallele"""
    if regle.params.cmp1.val == "init":
        # lancement immediat pour utilisation par la suite
        # ( ne se relance pas dans un worker parallele)
        if not regle.stock_param.worker:
            regle.prog(regle, None)
        regle.valide = "done"  # on a fini on le relance pas

    if regle.params.cmp1.val == "parallel_init" and regle.stock_param.worker:
        # lancement immediat pour utilisation par la suite
        # (se lance dans chaque worker parallele)
        regle.prog(regle, None)
        regle.valide = "done"  # on a fini on le relance pas
    if regle.params.cmp1.val == "boucle" and not regle.stock_param.worker:
        regle.listgen = iter_boucle(regle)
        regle.parallelmode = "batch"
        regle.nbparallel = prep_parallel(regle, traite_parallel, reprog=True)
    else:
        regle.nbparallel = prep_parallel(regle, traite_parallel_batch)
    # print(
    #     "preparation parallel_batch",
    #     regle.nbparallel,
    #     regle.chargeur,
    #     "st:",
    #     regle.store,
    # )


def traite_parallel_batch(regle):
    """traite les batchs en parallele"""
    parametres = dict()
    mapper = regle.stock_param
    rdict = dict()
    nprocs = regle.nbparallel

    for num, obj in enumerate(regle.tmpstore):
        obj.attributs["#_batchnum"] = str(num)
        st_ordre = obj.attributs.get("ordre", "999")
        ordre = int(st_ordre) if st_ordre.isnumeric() else 999
        if ordre in parametres:
            parametres[ordre].append(regle.prepare(regle, obj))
        else:
            parametres[ordre] = [regle.prepare(regle, obj)]
    for bloc in sorted(parametres):
        if (
            len(parametres[bloc]) == 1
        ):  # il est tout seul on a pas besoin de toute la tringlerie
            numero = parametres[bloc][0][0]
            obj = regle.tmpstore[int(numero)]
            regle.prog(regle, obj)
            continue
        msgqueue, logqueue = getqueue()
        setqueuhandler(None)
        with ProcessPoolExecutor(max_workers=nprocs) as executor:
            # TODO en python 3.7 l'initialisation peut se faire dans le pool
            rinit = parallelexec(
                executor,
                nprocs,
                initparallel,
                (
                    regle.context.getvars(),
                    mapper.macrostore.macros,
                    None,
                    None,
                    None,
                    msgqueue,
                    logqueue,
                ),
            )

            workids = {pid: n + 1 for n, pid in enumerate(rinit)}
            parallelexec(executor, nprocs, setparallelid, (workids, "#init_mp", ""))
            if regle.debug:
                print("retour init", rinit)
            results = executor.map(parallelbatch, (1, parametres[bloc], regle.index))
            #        print('retour map',results)
            rdict.update(results)
            #        print('retour map rdict',rdict)

            rfin = parallelexec(executor, nprocs, endparallel, "")
            #        print(' retour exec')
            if regle.debug:
                print("retour end", bloc, rfin)

    traite = mapper.moteur.traite_objet
    if regle.debug:
        print("retour multiprocessing ", list(rdict.items())[:10])
    #    print (finaux)
    for obj in regle.tmpstore:
        numero = obj.attributs["#_batchnum"]
        if numero in rdict:
            parametres = rdict[numero]["retour"]
            renseigne_attributs_batch(regle, obj, parametres)
        traite(obj, regle.branchements.brch["endstore"])
    regle.nbstock = 0
    time.sleep(1)


def iter_boucle(regle):
    """traite les batchs en parallele en mode bouclage (iterateur de jobs)"""
    endtime = regle.getvar("endtime", "23:59")
    minute = -1
    selector = regle.getvar("att_select", "#_timeselect")
    ordre = regle.getvar("att_ordre", "ordre")
    while time.strftime("%H:%M") < endtime:
        time.sleep(1)
        if time.localtime().tm_min == minute:
            # print("attente", time.localtime().tm_min, minute)
            # print(".", end="", flush=True)
            yield None
            continue
        minute = time.localtime().tm_min
        regle.stock_param.logger.info("traitement boucle %d", minute)
        # print("traitement boucle", minute)
        blocs = dict()
        for obj in regle.tmpstore:
            regle.stock_param.moteur.traite_objet(obj, regle.liste_regles[0])
            if obj.attributs.get(selector, "") == "1":
                passage = float(obj.attributs.get(ordre, 9999))
                if passage in blocs:
                    blocs[passage].append(obj)
                else:
                    blocs[passage] = [obj]
                # on pretraite toute la liste pour voir ce qui est executable
        for bloc in blocs:
            for obj in blocs[bloc]:
                n = 0
                if obj.attributs.get(selector, "") == "1":  # validation d' execution
                    job = regle.prepare(regle, obj)
                    n += 1
                    # print("------------------------------iter_boucle envoi", job)
                    yield (1, job)
                    # print("envoye", n, "jobs\nattente", end="", flush=True)


# -----------gestion de process externes en batch--------


def get_pool(maxworkers):
    """prepare un gestionnaire de pool de process"""
    return {i: dict() for i in range(max(maxworkers, 1))}


def add_worker(pool):
    """ajoute un emplacement a un pool"""
    maxnum = max(pool.keys())
    pool[maxnum + 1] = dict()


def get_slot(pool):
    """surveille un pool de process et determine s'il y a une disponibilité  sans attendre"""
    i = 0
    for i in sorted(pool):
        if not pool[i]:
            return i
        if pool[i]["process"].poll() is not None:
            pool[i]["end"] = time.time()
            return i
    return -1


def get_slots(pool):
    """surveille un pool de process et determine s'il y a une disponibilité  sans attendre"""
    libres = []
    for i in sorted(pool):
        if not pool[i]:
            libres.append(i)
        elif pool[i]["process"].poll() is not None:
            if pool[i]["end"] is None:
                pool[i]["end"] = time.time()
            libres.append(i)
    return libres


def wait_slot(pool):
    """surveille un pool de process et attends une disponibilité"""
    while get_slot(pool) == -1:
        time.sleep(0.1)
        #        print ('attente zzzz', pool)
    return get_slot(pool)


def wait_end(pool):
    """attend que le dernier process d'un pool ait terminé"""
    while len(get_slots(pool)) < len(pool):
        #        print('attente ',len(actifs), actifs[0].poll(), actifs[0].args)
        time.sleep(0.1)
    return


def execparallel_ext(blocks, maxworkers, lanceur, patience=None):
    """lance des process en parallele"""
    for i in iterparallel_ext(blocks, maxworkers, lanceur, patience=patience):
        if i is not None:
            print("traitement effectue", i)
    return


def prepare_filejob(description):
    dest, nom, ext = description
    file = str(os.path.join(*nom) + "." + ext)
    chemin = str(os.path.dirname(file))
    nom = str(os.path.basename(file))
    clef = os.path.join(str(dest), chemin, nom)
    loadarg = (clef, (dest, chemin, nom, ext))
    return loadarg


def iterparallel_ext(blocks, maxworkers, lanceur, patience=None):
    """lance des process en parallele et retourne les resultats des que disponible"""
    pool = get_pool(maxworkers)
    a_traiter = []
    libres = len(pool)
    # print("----------------------------dans iter parallelext", maxworkers, len(blocks))
    # optimiseur de position
    getqueue()
    setqueuhandler(None)
    while blocks or libres < maxworkers:
        # print ('itp:',a_traiter, libres, len(pool))
        try:
            #            print ('itp:',a_traiter, len(libres), len(pool))
            #            a_traiter = sorted(a_traiter)
            taille, job = a_traiter.pop()
            if paralleldebug:
                print("envoi pour traitement", job, taille, len(a_traiter))
            yield (taille, job)
        except IndexError:
            yield None
        libres = 0
        # try:
        #     msg = msgq.get(block=False)
        #     print("-------------------------------retour queue", msg)
        # except Empty:
        #     time.sleep(0.1)
        for slot in get_slots(pool):
            if pool[slot]:
                # print("trouve element a traiter", pool[slot])
                retour = pool[slot]
                nom_r = retour["nom"]
                if paralleldebug:
                    print("retour parallel ext", nom_r)
                loadarg = prepare_filejob(retour["fich"])
                a_traiter.append((retour["taille"], loadarg))

                if patience:
                    patience(nom_r, retour["params"], retour["end"] - retour["start"])
                    if paralleldebug:
                        print("iterparallelext : retour patience", patience)
            if blocks:
                tache = blocks.pop()
                # print ('recu tache',tache, len(blocks))
                nom, params, dest, size = tache
                procid = lanceur(params)
                if procid:
                    pool[slot] = {
                        "process": procid,
                        "nom": nom,
                        "end": None,
                        "start": time.time(),
                        "params": params,
                        "fich": dest,
                        "taille": size,
                    }

                time.sleep(1)  # on dort un peu pour pas surcharger

            else:
                #                print ('fin de tache')
                pool[slot] = None
                libres += 1

    a_traiter = sorted(a_traiter)
    print("on finit les restes", len(a_traiter))
    yield from a_traiter
