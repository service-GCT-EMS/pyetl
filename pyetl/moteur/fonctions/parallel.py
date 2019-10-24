# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 11:06:21 2019

@author: 89965
gestion du parallelisme sur les entrees/sorties

"""
import os
import time
import logging
from concurrent.futures import ProcessPoolExecutor

from pyetl.vglobales import getmainmapper

from pyetl.schema.schema_io import integre_schemas, retour_schemas
from pyetl.formats.interne.stats import ExtStat
from .outils import (
    renseigne_attributs_batch,
    prepare_batch_from_object,
    execbatch,
    getfichs,
    printexception,
)

LOGGER = logging.getLogger("pyetl")  # un logger
paralleldebug = 0

def setparallel(mapper):
    """enregistre les fonctions de gestion du parallelisme"""
    mapper.execparallel_ext = execparallel_ext
    mapper.iterparallel_ext = iterparallel_ext
    mapper.traite_parallel = traite_parallel
    mapper.gestion_parallel_batch = gestion_parallel_batch
    mapper.gestion_parallel_load = gestion_parallel_load


def initparallel(parametres):
    """initialisatin d'un process worker pour un traitement parallele"""
    #    commandes, args, params, macros, env, log = parametres
    params, macros, env, loginfo, schemas = parametres
    mainmapper = getmainmapper()

    if mainmapper.loginited:
        #        print("pyetl double init", os.getpid())
        time.sleep(1)
        return None
    if paralleldebug:
        print("pyetl initworker", os.getpid(), schemas.keys())
    LOGGER.info("pyetl initworker " + str(os.getpid()))
    mainmapper.worker = True
    mainmapper.initenv(env, loginfo)
    mainmapper.loginited = True
    mainmapper.macros.update(macros)
    mainmapper.context.update(params)
    integre_schemas(mainmapper.schemas, schemas)
    mainmapper.parametres_lancement = parametres
    time.sleep(1)
    return (os.getpid(), True)


def setparallelid(parametres):
    """positionne un numero de worker et initialise les commandes """
    pidset, commandes, args = parametres
    mainmapper = getmainmapper()

    if mainmapper.get_param("_wid"):
        time.sleep(1)
        return None
    wid = str(pidset[os.getpid()])
    mainmapper.set_param("_wid", wid)
    log,log_level,log_print = (mainmapper.get_param("logfile"), mainmapper.get_param("log_level"), mainmapper.get_param("log_print"))
    if log:
        base, ext = os.path.splitext(mainmapper.get_param("logfile"))
        log = str(base) + "_" + wid + "." + str(ext)
    loginfo = log,log_level,log_print
    init = mainmapper.initpyetl(commandes, args, loginfo=loginfo)
    if paralleldebug:
        print('setparallelid apres init', mainmapper.get_param("_wid"), commandes, args)

    return (os.getpid(), mainmapper.get_param("_wid"), init)


def set_parallelretour(mapper, valide):
    """positionne les variables de retour pour l'execution en parallele"""
    #    print ('retour parallel',mapper.get_param('_wid'), mapper.stats.keys())
    schema = retour_schemas(mapper.schemas, mode=mapper.get_param("force_schema", "util"))
    stats_generales = mapper.getstats()
    retour_stats = {nom: stat.retour() for nom, stat in mapper.stats.items()}
    #    print ('retour parallel', mapper.get_param('_wid'), retour_stats)
    retour = {
        "pid": os.getpid(),
        "wid": mapper.get_param("_wid"),
        "valide": valide,
        "stats_generales": stats_generales,
        "retour": mapper.retour,
        "schemas": schema,
        "stats": retour_stats,
    }
    return retour


def parallelbatch(parametres_batch):
    """execute divers traitements en parallele"""
    #    print ("pyetl startbatch",os.getpid(), parametres_batch[:3])
    numero, mapping, entree, sortie, args = parametres_batch
    #    if not MAINMAPPER.inited:
    #        initparallel('#init_mp', '',params, macros)
    mainmapper = getmainmapper()
    processor = mainmapper.getpyetl(mapping, liste_params=args, entree=entree, rep_sortie=sortie)
    if processor is None:
        print("pyetl echec batchworker", os.getpid(), mapping, args)
        return (numero, {})

    processor.process()
    retour = set_parallelretour(processor, True)
    #    print("pyetl batchworker", os.getpid(),processor.idpyetl, mapping, args,
    #          '->', processor.retour)
    return (numero, retour)


def parallelprocess(numero, file, regle):
    """traitement individuel d'un fichier"""
    mainmapper = getmainmapper()
    try:
        # print ('---------------------------------------' + mainmapper.get_param("_wid") + '-worker:lecture', file, regle)
        nom, parms = file
        nb_lu = mainmapper.lecture(file, reglenum=regle, parms=parms)
    except StopIteration as arret:
        return numero, -1
    except Exception as exc:
        print("====" + mainmapper.get_param("_wid") + "=erreur de traitement parallele non gérée")
        print("====regle courante:", regle)
        printexception()
        raise
    return numero, nb_lu


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
        nb_total, nb_fichs = mainmapper.sorties.final()
        mainmapper.padd("_st_wr_fichs", nb_fichs)
        mainmapper.padd("_st_wr_objs", nb_total)
        succes = False
    retour = set_parallelretour(mainmapper, succes)
    #    if MAINMAPPER.moteur():
    #        MAINMAPPER.padd('_st_obj_duppliques', MAINMAPPER.moteur.dupcnt)
    #        MAINMAPPER.padd('_st_obj_supprimes', MAINMAPPER.moteur.suppcnt)
    #    stats_generales = MAINMAPPER.getstats()

    #    print("-----pyetl batchworker end", os.getpid(), succes, nb_total, nb_fichs)
    LOGGER.info(
        "-----pyetl batchworker end " + str(os.getpid()) + " succes "
        if succes
        else "echec " + str(nb_total) + " " + str(nb_fichs)
    )

    mainmapper.ended = True
    #    retour_stats = {nom: stat.retour() for nom, stat in MAINMAPPER.stats.items()}
    #    retour = {'pid': os.getpid(), 'wid': MAINMAPPER.get_param('_wid'), 'valide': succes,
    #              'stats_generales': stats_generales,
    #              'schemas': schema, 'stats': retour_stats}

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
                #                print ('termine',i)
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
    for job in work:
        if not job.done():
            attente.append(job)
        else:
            #            print ('termine',job)
            #            print ('retour', job.result())
            retour_process = job.result()
            #            print('retour pexec ',job,retour_process)
            if retour_process is not None:
                num_obj, lus = retour_process
                rfin[num_obj] = lus
                mapper.aff.send(("fich", 1, lus))
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


def submit_job(jobs, job, regle, executor, fonction):
    """ajoute une tache au traitement parallele"""
    #    print ('transmission ',job)
    #    rfin = dict()
    dest, nom, ext = job
    file = str(os.path.join(*nom) + "." + ext)
    chemin = str(os.path.dirname(file))
    nom = str(os.path.basename(file))
    clef = os.path.join(str(dest), chemin, nom)
    loadarg = (clef, (dest, chemin, nom, ext))
    # print ('appel parallele ',clef,'->',loadarg, regle, regle.index)
    jobs.append(executor.submit(fonction, 1, loadarg, regle.index))


#    print ('attente', len(jobs))


def paralleliter_suivi(regle, executor, fonction, argiter):
    """gere les appels classique mais avec des retours d'infos en s'appuyant sur
        un iterateur ce qui permet de lancer les traitements sans que toutes les
        entree soient généréés"""
    rfin = dict()
    mapper = regle.stock_param
    if paralleldebug:
        print('start paralleliter_suivi', fonction, argiter)
    #    work = [executor.submit(fonction, *arg) for arg in arglist]
    waitlist = []
    jobs = []
    marge = executor._max_workers + 2
    for arg in argiter:
        if paralleldebug:
            print('paralleliter_suivi : arg', arg)
        if arg is not None:
            #            print ('piter: recu ', arg, len(jobs))
            waitlist.append(arg)
            if paralleldebug:
                print ('liste:', waitlist)
            if len(jobs) < marge:
                try:
                    waitlist.sort()
                    taille, job = waitlist.pop()
                    if paralleldebug:
                        print ('traitement job', job, fonction)
                    submit_job(jobs, job, regle, executor, fonction)
                except IndexError:
                    time.sleep(0.1)
        # print('paralleliter_suivi : fin traitement', arg, jobs)
        rfin.update(suivi_job(mapper, jobs))
        # print('paralleliter_suivi : dodo', arg)
        time.sleep(0.1)
    for arg in sorted(waitlist, reverse=True):
        taille, job = arg
        submit_job(jobs, job, regle, executor, fonction)

    rfin.update(parallelmap_suivi(mapper, None, None, None, work=jobs))
    return rfin


def prep_parallel(regle, fonction):
    """ initialise le mecanisme pour la parallelisation d'une regle"""
    multi, _ = regle.get_max_workers()
    if multi > 1 and not regle.stock_param.worker:
        regle.store = True
        regle.traite_stock = fonction
        regle.nbstock = 0
        regle.traite = 0
        regle.tmpstore = []
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
    LOGGER.info(" ".join(("preparation exec parallele", str(def_regles), str(mapper.liste_params))))
    schemas = retour_schemas(mapper.schemas, mode="int")
    return schemas, env, def_regles


def traite_parallel(regle):
    """traite les operations en parallele"""

    mapper = regle.stock_param

    nprocs, _ = regle.get_max_workers()
    num_regle = regle.index
    rdict = dict()
    schemas, env, def_regles = prepare_env_parallel(regle)
    print("passage en mode parallel",num_regle, regle)
    if mapper.worker:
        print("un worker ne peurt pas passer en parallele", mapper.get_param("_wid"))
        raise RuntimeError
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
        # TODO en python 3.7 l'initialisation peut se faire dans le pool
        rinit = parallelexec(
            executor, nprocs, initparallel, (mapper.context.vlocales, mapper.macros, env, None, schemas)
        )
        workids = {pid: n + 1 for n, pid in enumerate(rinit)}
        #        print ('workids',workids)
        LOGGER.info(" ".join(("workids", str(workids))))
        parallelexec(executor, nprocs, setparallelid, (workids, def_regles, mapper.liste_params))
        if regle.debug or paralleldebug:
            print("traite_parallel: retour init", rinit, num_regle)
        #        results = executor.map(parallelprocess, idobj, entrees, num_regle)
        rdict = paralleliter_suivi(regle, executor, parallelprocess, regle.listgen)
        rfin = parallelexec(executor, nprocs, endparallel, "")
    #        if regle.debug:
    #        print ('retour')
    for i in rfin:
        retour = rfin[i][0]
        if retour:
            print(
                i,
                "worker",
                retour["wid"],
                "traites",
                retour["stats_generales"].get("_st_lu_objs",'0'),
                list(sorted(retour["schemas"].keys())),
            )
            for param in retour["stats_generales"]:
                mapper.padd(param, retour["stats_generales"][param])
            LOGGER.info("retour stats" + str(sorted(retour["stats_generales"].items())))
            #            print ('traitement schemas ', retour["schemas"])
            integre_schemas(mapper.schemas, retour["schemas"])

            for nom, entete, contenu in retour["stats"].values():
                if nom not in mapper.stats:
                    mapper.stats[nom] = ExtStat(nom, entete)
                mapper.stats[nom].add(entete, contenu)
        else:
            print ('erreur retour', rfin)
    #            print ('traitement retour stats', mapper.idpyetl, nom,
    #                   mapper.stats[nom], len(mapper.stats[nom].lignes))

    #    traite = regle.stock_param.moteur.traite_objet
    #    print("retour multiprocessing ", results, retour)
    #    obj = regle.objet_courant
    #    obj.attributs[regle.params.att_sortie.val] = str(rdict[i])
    #    traite(obj, regle.branchements.brch["end"])
    regle.nbstock = 0


def traite_parallel_load(regle):
    """traite les chargements en parallele"""

    idobj = []
    entrees = []
    mapper = regle.stock_param

    for num, obj in enumerate(regle.tmpstore):
        fichs = getfichs(regle, obj)
        idobj.extend([num] * len(fichs))
        entrees.extend(fichs)
    arglist = [(i, j, regle.index) for i, j in zip(idobj, entrees)]
    nprocs, _ = regle.get_max_workers()
    num_regle = [regle.index] * len(entrees)
    rdict = dict()
    schemas, env, def_regles = prepare_env_parallel(regle)
    #    print('parallel load',entrees,idobj, type(mapper.env))
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
        # TODO en python 3.7 l'initialisation peut se faire dans le pool
        rinit = parallelexec(
            executor, nprocs, initparallel, (mapper.context.vlocales, mapper.macros, env, None, schemas)
        )
        workids = {pid: n + 1 for n, pid in enumerate(rinit)}
        #        print ('workids',workids)
        LOGGER.info(" ".join(("workids", str(workids))))
        parallelexec(executor, nprocs, setparallelid, (workids, def_regles, mapper.liste_params))
        if regle.debug:
            print("retour init", rinit, num_regle)
        #        results = executor.map(parallelprocess, idobj, entrees, num_regle)
        rdict = parallelmap_suivi(mapper, executor, parallelprocess, arglist)

        rfin = parallelexec(executor, nprocs, endparallel, "")
    #        if regle.debug:
    #        print ('retour')
    for i in rfin:
        retour = rfin[i][0]
        print(
            i,
            "worker",
            retour["wid"],
            "traites",
            retour["stats_generales"]["_st_lu_objs"],
            list(sorted(retour["schemas"].keys())),
        )
        for param in retour["stats_generales"]:
            mapper.padd(param, retour["stats_generales"][param])
        LOGGER.info("retour stats" + str(sorted(retour["stats_generales"].items())))
        #            print ('traitement schemas ', retour["schemas"])
        integre_schemas(mapper.schemas, retour["schemas"])

        for nom, entete, contenu in retour["stats"].values():
            if nom not in mapper.stats:
                mapper.stats[nom] = ExtStat(nom, entete)
            mapper.stats[nom].add(entete, contenu)
    #            print ('traitement retour stats', mapper.idpyetl, nom,
    #                   mapper.stats[nom], len(mapper.stats[nom].lignes))

    traite = regle.stock_param.moteur.traite_objet
    #    print("retour multiprocessing ", results, retour)

    for i in sorted(rdict):
        obj = regle.tmpstore[i]
        if regle.params.att_sortie.val:
            obj.attributs[regle.params.att_sortie.val] = str(rdict[i])
        print("fin traitement parallele", obj)
        traite(obj, regle.branchements.brch["end"])
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

    multi = prep_parallel(regle, traite_parallel_batch)


#    print("preparation parallel_batch", multi, regle.chargeur, 'st:',regle.store)


def traite_parallel_batch(regle):
    """traite les batchs en parallele"""
    parametres = dict()
    mapper = regle.stock_param
    rdict = dict()
    nprocs = int(regle.params.cmp2.num)

    for num, obj in enumerate(regle.tmpstore):
        obj.attributs["#_batchnum"] = str(num)
        st_ordre = obj.attributs.get("ordre", "999")
        ordre = int(st_ordre) if st_ordre.isnumeric() else 999
        if ordre in parametres:
            parametres[ordre].append(prepare_batch_from_object(regle, obj))
        else:
            parametres[ordre] = [prepare_batch_from_object(regle, obj)]
    for bloc in sorted(parametres):
        if len(parametres[bloc]) == 1:  # il est tout seul on a pas besoin de toute la tringlerie
            numero = parametres[bloc][0][0]
            obj = regle.tmpstore[numero]
            execbatch(regle, obj)
            continue
        with ProcessPoolExecutor(max_workers=nprocs) as executor:
            # TODO en python 3.7 l'initialisation peut se faire dans le pool
            rinit = parallelexec(
                executor, nprocs, initparallel, (mapper.context.vlocales, mapper.macros, None, None, [])
            )

            workids = {pid: n + 1 for n, pid in enumerate(rinit)}
            parallelexec(executor, nprocs, setparallelid, (workids, "#init_mp", ""))
            if regle.debug:
                print("retour init", rinit)
            results = executor.map(parallelbatch, parametres[bloc])
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
        traite(obj, regle.branchements.brch["end"])
    regle.nbstock = 0


# -----------gestion de process externes en batch--------


def get_pool(maxworkers):
    """prepare un gestionnaire de pool de process"""
    if maxworkers < 1:
        maxworkers = 1
    pool = {i: dict() for i in range(maxworkers)}
    return pool


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
    pool = get_pool(maxworkers)
    for tache in blocks:
        nom, params = tache
        slot = wait_slot(pool)  # on cherche une place
        if pool[slot]:
            retour = pool[slot]
            nom_r = retour["nom"]
            #            print ('slot retour', slot, retour)
            #            blocks[nom_r] = (retour['params'], retour['end']-retour['start'])
            if patience:
                #                patience(nom_r, *blocks[nom_r])
                patience(nom_r, retour["params"], retour["end"] - retour["start"])
                print ('exec parallel_ext retour patience')
        if nom is None:  # on envoie un None pour reduire le pool
            del pool[slot]
            continue
        pool[slot] = {
            "process": lanceur(params),
            "nom": nom,
            "start": time.time(),
            "params": params,
            "end": None,
        }
    wait_end(pool)
    for i in pool:
        if pool[i]:
            retour = pool[i]
            #            print ('retour fin', i, retour)
            nom = retour["nom"]
            #            blocks[nom] = (retour['params'], retour['end']-retour['start'])
            if patience:
                #                patience(nom, *blocks[nom])
                patience(nom, retour["params"], retour["end"] - retour["start"])
                print ('exec parallel_ext retour patience wait end')

def iterparallel_ext(blocks, maxworkers, lanceur, patience=None):
    """lance des process en parallele et retourne les resultats des que disponible"""
    pool = get_pool(maxworkers)
    a_traiter = []
    libres = len(pool)
    # print("----------------------------dans iter parallelext", maxworkers, len(blocks))
    # optimiseur de position

    while blocks or libres < maxworkers:
        # print ('itp:',a_traiter, libres, len(pool))
        try:
            #            print ('itp:',a_traiter, len(libres), len(pool))
            #            a_traiter = sorted(a_traiter)
            taille, nom = a_traiter.pop()
            if paralleldebug:
                print ('envoi pour traitement',nom, taille, len(a_traiter))
            yield (taille, nom)
        except IndexError:
            yield None
        libres = 0
        for slot in get_slots(pool):
            if pool[slot]:
                #                print ('trouve element a traiter',pool[slot])
                retour = pool[slot]
                nom_r = retour["nom"]
                if paralleldebug:
                    print ('retour parallel ext', nom_r)
                a_traiter.append((retour["taille"], retour["fich"]))

                if patience:
                    patience(nom_r, retour["params"], retour["end"] - retour["start"])
                    if paralleldebug:
                        print('iterparallelext : retour patience')
            if blocks:
                tache = blocks.pop()
                # print ('recu tache',tache, len(blocks))
                nom, params, dest, size = tache
                pool[slot] = {
                    "process": lanceur(params),
                    "nom": nom,
                    "end": None,
                    "start": time.time(),
                    "params": params,
                    "fich": dest,
                    "taille": size,
                }
                time.sleep(1) # on dort un peu pour pas surcharger
            else:
                #                print ('fin de tache')
                pool[slot] = None
                libres += 1

    a_traiter = sorted(a_traiter)
    print("on finit les restes", len(a_traiter))
    # for i in a_traiter:
    #     taille, nom = i
    #     yield taille, nom
    yield from a_traiter


def parallel_load(regle):
    """traite les chargements en parallele"""

    idobj = []
    entrees = []
    mapper = regle.stock_param

    for num, obj in enumerate(regle.tmpstore):
        fichs = getfichs(regle, obj)
        idobj.extend([num] * len(fichs))
        entrees.extend(fichs)
    arglist = [(i, j, regle.index) for i, j in zip(idobj, entrees)]
    nprocs, _ = regle.get_max_workers()
    num_regle = [regle.index] * len(entrees)
    rdict = dict()
    schemas, env, def_regles = prepare_env_parallel(regle)
    #    print('parallel load',entrees,idobj, type(mapper.env))
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
        # TODO en python 3.7 l'initialisation peut se faire dans le pool
        rinit = parallelexec(
            executor, nprocs, initparallel, (mapper.context.vlocales, mapper.macros, env, None, schemas)
        )
        workids = {pid: n + 1 for n, pid in enumerate(rinit)}
        #        print ('workids',workids)
        LOGGER.info(" ".join(("workids", str(workids))))
        parallelexec(executor, nprocs, setparallelid, (workids, def_regles, mapper.liste_params))
        if regle.debug:
            print("retour init", rinit, num_regle)

        rdict = paralleliter_suivi(regle, executor, parallelprocess, arglist)

        rfin = parallelexec(executor, nprocs, endparallel, "")
    #        if regle.debug:
    #        print ('retour')
    for i in rfin:
        retour = rfin[i][0]
        print(
            i,
            "worker",
            retour["wid"],
            "traites",
            retour["stats_generales"]["_st_lu_objs"],
            list(sorted(retour["schemas"].keys())),
        )
        for param in retour["stats_generales"]:
            mapper.padd(param, retour["stats_generales"][param])
        LOGGER.info("retour stats" + str(sorted(retour["stats_generales"].items())))
        #            print ('traitement schemas ', retour["schemas"])
        integre_schemas(mapper.schemas, retour["schemas"])

        for nom, entete, contenu in retour["stats"].values():
            if nom not in mapper.stats:
                mapper.stats[nom] = ExtStat(nom, entete)
            mapper.stats[nom].add(entete, contenu)
    #            print ('traitement retour stats', mapper.idpyetl, nom,
    #                   mapper.stats[nom], len(mapper.stats[nom].lignes))

    traite = regle.stock_param.moteur.traite_objet
    #    print("retour multiprocessing ", results, retour)

    for i in sorted(rdict):
        obj = regle.tmpstore[i]
        if regle.params.att_sortie.val:
            obj.attributs[regle.params.att_sortie.val] = str(rdict[i])
        print("fin traitement parallele", obj)
        traite(obj, regle.branchements.brch["end"])
    regle.nbstock = 0
