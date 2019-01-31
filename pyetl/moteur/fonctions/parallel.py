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
from pyetl.formats.formats import ExtStat
from .outils import renseigne_attributs_batch, prepare_batch_from_object, execbatch, getfichs

LOGGER = logging.getLogger('pyetl') # un logger

def setparallel(mapper):
    mapper.execparallel_ext = execparallel_ext
    mapper.iterparallel_ext = iterparallel_ext
    mapper.traite_parallel = traite_parallel
    mapper.gestion_parallel_batch = gestion_parallel_batch
    mapper.gestion_parallel_load = gestion_parallel_load



def initparallel(parametres):
    """initialisatin d'un process worker pour un traitement parallele"""
#    commandes, args, params, macros, env, log = parametres
    params, macros, env, log, schemas= parametres
    MAINMAPPER=getmainmapper()

    if MAINMAPPER.inited:
#        print("pyetl double init", os.getpid())
        time.sleep(1)
        return None
    print("pyetl initworker", os.getpid(), schemas.keys())
    LOGGER.info("pyetl initworker "+str(os.getpid()))
    MAINMAPPER.worker = True
    MAINMAPPER.initcontext(env, log)
    MAINMAPPER.inited = True
    MAINMAPPER.macros.update(macros)
    MAINMAPPER.parms.update(params)
    integre_schemas(MAINMAPPER.schemas, schemas)
    MAINMAPPER.parametres_lancement = parametres
    time.sleep(1)
#    if initpyetl(MAINMAPPER, commandes, args, env=env, log=log):
##       time.sleep(2)
#       return (os.getpid(), True)
    return (os.getpid(), True)


def setparallelid(parametres):
    """positionne un numero de worker et initialise les commandes """
    pidset, commandes, args = parametres
    MAINMAPPER=getmainmapper()

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
    init = MAINMAPPER.initpyetl(commandes, args, log=log)

    return (os.getpid(), MAINMAPPER.get_param('_wid'), init)


def set_parallelretour(mapper, valide):
    '''positionne les variables de retour pour l'execution en parallele'''
#    print ('retour parallel',mapper.get_param('_wid'), mapper.stats.keys())
    schema = retour_schemas(mapper.schemas, mode=mapper.get_param('force_schema', 'util'))
    stats_generales = mapper.getstats()
    retour_stats = {nom: stat.retour() for nom, stat in mapper.stats.items()}
#    print ('retour parallel', mapper.get_param('_wid'), retour_stats)
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
    MAINMAPPER = getmainmapper()
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
    MAINMAPPER=getmainmapper()
    try:
#        print ('worker:lecture', file, regle)
        nom, parms = file
        nb_lu = MAINMAPPER.lecture(file, reglenum=regle, parms=parms)
    except StopIteration as arret:
        return numero, -1
    return numero, nb_lu

def endparallel(test=None):
    '''termine un traitement parallele'''
    schema = None
    MAINMAPPER=getmainmapper()
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



def parallelexec(executor, nprocs, fonction, args):
    '''gere les appels de fonction uniques d'un pool de process
       et s'assure que chaque process du pool est appelé'''

    rfin = dict()
#    print('start pexec')
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
    rfin=dict()
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
                mapper.aff.send(('fich', 1, lus))
    work[:] = attente
    return rfin





def parallelmap_suivi(mapper, executor, fonction, arglist, work=None):
    '''gere les appels classique mais avec des retours d'infos'''

    rfin = dict()
#    print('start pexec')
    if work is None:
        work = [executor.submit(fonction, *arg) for arg in arglist]

    while work:
        rfin.update(suivi_job(mapper,work))
        time.sleep(0.1)
    return rfin


def paralleliter_suivi(regle, executor, fonction, argiter):
    '''gere les appels classique mais avec des retours d'infos en s'appuyant sur
        un iterateur ce qui permet de lancer les traitements sans que toutes les
        entree soient généréés'''
    rfin = dict()
    mapper=regle.stock_param
#    print('start pexec')
#    work = [executor.submit(fonction, *arg) for arg in arglist]
    jobs = []
    for arg in argiter:
#        print ('piter: ', mapper.get_param('_wid'), 'recu ', arg, jobs)

        if arg is not None:
            dest,nom,ext = arg
            file = os.path.join(*nom)+'.'+ext
            chemin = os.path.dirname(file)
            nom = os.path.basename(file)
            clef = os.path.join(dest,chemin,nom)
            loadarg = (clef , (dest,chemin,nom,ext))
#            print ('appel parallele ',arg,'->',loadarg, regle, regle.index)
            jobs.append(executor.submit(fonction, 1,loadarg,regle.index))
            rfin.update(suivi_job(mapper,jobs))
            print ('attente', len(jobs))

            while len(jobs) > 20:
                rfin.update(suivi_job(mapper,jobs))
                time.sleep(0.1)
        time.sleep(0.1)
#        attente = []
#        for job in jobs:
#            if job.done():
#                retour_process = job.result()
##                print('retour pexec ',job,retour_process)
#                if retour_process is not None:
#                    num_obj, lus = retour_process
#                    rfin[num_obj] = lus
#                    mapper.aff.send(('fich', 1, lus))
#            else:
#                attente.append(job)
#        jobs =  attente
#    print ('---------------fin piter')
    rfin.update(parallelmap_suivi(mapper, None, None, None, work=jobs))





    return rfin


def prep_parallel(regle, fonction):
    ''' initialise le mecanisme pour la parallelisation d'une regle'''
    multi, _ = regle.get_max_workers()
    if multi>1 and not regle.stock_param.worker:
        regle.store = True
        regle.traite_stock = fonction
        regle.nbstock = 0
        regle.traite = 0
        regle.tmpstore = []
    return multi



def gestion_parallel_load(regle):
    '''prepare les chargements paralleles'''
    multi = prep_parallel(regle, traite_parallel_load)
#    print("preparation parallel_loader", multi, regle.chargeur, 'st:',regle.store)

def prepare_env_parallel(regle):
    '''prepare les parametres pour un lancement en parallele'''
    mapper = regle.stock_param
    env = mapper.env if isinstance(mapper.env, dict) else None
    def_regles = mapper.liste_regles if mapper.liste_regles else mapper.fichier_regles
#        print("preparation exec parallele", def_regles, mapper.liste_params)
    LOGGER.info(' '.join(("preparation exec parallele", str(def_regles),
                              str(mapper.liste_params))))
    schemas = retour_schemas(mapper.schemas, mode='int')
    return schemas, env, def_regles

def traite_parallel(regle):
    '''traite les operations en parallele'''

    mapper = regle.stock_param

    nprocs, _ = regle.get_max_workers()
    num_regle = regle.index
    rdict = dict()
    schemas, env, def_regles = prepare_env_parallel(regle)
    print('passage en mode parallel', schemas.keys())
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
#TODO en python 3.7 l'initialisation peut se faire dans le pool
        rinit = parallelexec(executor, nprocs, initparallel,
                             (mapper.parms, mapper.macros, env, None, schemas))
        workids = {pid:n+1 for n, pid in enumerate(rinit)}
#        print ('workids',workids)
        LOGGER.info(' '.join(('workids', str(workids))))
        parallelexec(executor, nprocs, setparallelid,
                     (workids, def_regles, mapper.liste_params))
        if regle.debug:
            print('retour init', rinit, num_regle)
#        results = executor.map(parallelprocess, idobj, entrees, num_regle)
        rdict = paralleliter_suivi(regle, executor, parallelprocess, regle.listgen)
        rfin = parallelexec(executor, nprocs, endparallel, '')
#        if regle.debug:
#        print ('retour')
    for i in rfin:
        retour = rfin[i][0]
        print (i, 'worker', retour['wid'], 'traites',
               retour['stats_generales']['_st_lu_objs'],
               list(sorted(retour['schemas'].keys())))
        for param in retour['stats_generales']:
            mapper.padd(param, retour['stats_generales'][param])
        LOGGER.info('retour stats'+str(sorted(retour['stats_generales'].items())))
        fichs = retour['fichs']
        for nom, nbr in fichs.items():
            mapper.liste_fich[nom] = mapper.liste_fich.get(nom, 0)+nbr
#            print ('traitement schemas ', retour["schemas"])
        integre_schemas(mapper.schemas, retour["schemas"])

        for nom, entete, contenu in retour["stats"].values():
            if nom not in mapper.stats:
                mapper.stats[nom] = ExtStat(nom, entete)
            mapper.stats[nom].add(entete, contenu)
            print ('traitement retour stats', mapper.idpyetl, nom,
                   mapper.stats[nom], len(mapper.stats[nom].lignes))

#    traite = regle.stock_param.moteur.traite_objet
#    print("retour multiprocessing ", results, retour)
#    obj = regle.objet_courant
#    obj.attributs[regle.params.att_sortie.val] = str(rdict[i])
#    traite(obj, regle.branchements.brch["end"])
    regle.nbstock = 0


def traite_parallel_load(regle):
    '''traite les chargements en parallele'''

    idobj = []
    entrees = []
    mapper = regle.stock_param

    for num, obj in enumerate(regle.tmpstore):
        fichs = getfichs(regle, obj)
        idobj.extend([num]*len(fichs))
        entrees.extend(fichs)
    arglist = [(i, j, regle.index) for i, j in zip(idobj, entrees)]
    nprocs, _ = regle.get_max_workers()
    num_regle = [regle.index]*len(entrees)
    rdict = dict()
    schemas, env, def_regles = prepare_env_parallel(regle)
#    print('parallel load',entrees,idobj, type(mapper.env))
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
#TODO en python 3.7 l'initialisation peut se faire dans le pool
        rinit = parallelexec(executor, nprocs, initparallel,
                             (mapper.parms, mapper.macros, env, None, schemas))
        workids = {pid:n+1 for n, pid in enumerate(rinit)}
#        print ('workids',workids)
        LOGGER.info(' '.join(('workids', str(workids))))
        parallelexec(executor, nprocs, setparallelid,
                     (workids, def_regles, mapper.liste_params))
        if regle.debug:
            print('retour init', rinit, num_regle)
#        results = executor.map(parallelprocess, idobj, entrees, num_regle)
        rdict = parallelmap_suivi(mapper, executor, parallelprocess, arglist)
#        rdict = paralleliter_suivi(regle, nprocs, executor, parallelprocess, arglist)

        rfin = parallelexec(executor, nprocs, endparallel, '')
#        if regle.debug:
#        print ('retour')
    for i in rfin:
        retour = rfin[i][0]
        print (i, 'worker', retour['wid'], 'traites',
               retour['stats_generales']['_st_lu_objs'],
               list(sorted(retour['schemas'].keys())))
        for param in retour['stats_generales']:
            mapper.padd(param, retour['stats_generales'][param])
        LOGGER.info('retour stats'+str(sorted(retour['stats_generales'].items())))
        fichs = retour['fichs']
        for nom, nbr in fichs.items():
            mapper.liste_fich[nom] = mapper.liste_fich.get(nom, 0)+nbr
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
        print ('fin traitement parallele', obj)
        traite(obj, regle.branchements.brch["end"])
    regle.nbstock = 0



def gestion_parallel_batch(regle):
    ''' initialise la gestion des batch en parallele'''
    if regle.params.cmp1.val == 'init':
    # lancement immediat pour utilisation par la suite
    # ( ne se relance pas dans un worker parallele)
        if not regle.stock_param.worker:
            regle.prog(regle, None)
        regle.valide = 'done' # on a fini on le relance pas

    if regle.params.cmp1.val == 'parallel_init' and regle.stock_param.worker:
        # lancement immediat pour utilisation par la suite
        #(se lance dans chaque worker parallele)
        regle.prog(regle, None)
        regle.valide = 'done' # on a fini on le relance pas

    multi = prep_parallel(regle, traite_parallel_batch)
#    print("preparation parallel_batch", multi, regle.chargeur, 'st:',regle.store)



def traite_parallel_batch(regle):
    '''traite les batchs en parallele'''
    parametres = dict()
    mapper = regle.stock_param
    rdict = dict()
    nprocs = int(regle.params.cmp2.num)

    for num, obj in enumerate(regle.tmpstore):
        obj.attributs['#_batchnum'] = str(num)
        st_ordre = obj.attributs.get('ordre','999')
        ordre =  int(st_ordre) if st_ordre.isnumeric() else 999
        if ordre in parametres:
            parametres[ordre].append(prepare_batch_from_object(regle, obj))
        else:
            parametres[ordre] = [prepare_batch_from_object(regle, obj)]
    for bloc in sorted(parametres):
        if len(parametres[bloc]) == 1: # il est tout seul on a pas besoin de toute la tringlerie
            numero = parametres[bloc][0][0]
            obj = regle.tmpstore[numero]
            execbatch(regle, obj)
            continue
        with ProcessPoolExecutor(max_workers=nprocs) as executor:
#TODO en python 3.7 l'initialisation peut se faire dans le pool
            rinit = parallelexec(executor, nprocs, initparallel,
                                 (mapper.parms, mapper.macros, None, None, []))

            workids = {pid:n+1 for n, pid in enumerate(rinit)}
            parallelexec(executor, nprocs, setparallelid, (workids, '#init_mp', ''))
            if regle.debug:
                print('retour init', rinit)
            results = executor.map(parallelbatch, parametres[bloc])
    #        print('retour map',results)
            rdict.update(results)
    #        print('retour map rdict',rdict)

            rfin = parallelexec(executor, nprocs, endparallel, '')
    #        print(' retour exec')
            if regle.debug:
                print('retour end', bloc,rfin)

    traite = mapper.moteur.traite_objet
    if regle.debug:
        print("retour multiprocessing ", rdict.items()[:10])
#    print (finaux)
    for obj in regle.tmpstore:
        numero = obj.attributs['#_batchnum']
        if numero in rdict:
            parametres = rdict[numero]['retour']
            renseigne_attributs_batch(regle, obj, parametres)
        traite(obj, regle.branchements.brch["end"])
    regle.nbstock = 0

# -----------gestion de process externes en batch--------

def get_pool(maxworkers):
    '''prepare un gestionnaire de pool de process'''
    if maxworkers < 1:
        maxworkers = 1
    pool = {i: dict() for i in range(maxworkers)}
    return pool


def get_slot(pool):
    '''surveille un pool de process et determine s'il y a une disponibilité  sans attendre'''
    i=0
    for i in sorted(pool):
        if not pool[i]:
            return i
        if pool[i]['process'].poll() is not None:
            pool[i]['end'] = time.time()
            return i
    return -1

def get_slots(pool):
    '''surveille un pool de process et determine s'il y a une disponibilité  sans attendre'''
    libres = []
    for i in sorted(pool):
        if not pool[i]:
            libres.append(i)
        elif pool[i]['process'].poll() is not None:
            if pool[i]['end'] is None:
                pool[i]['end'] = time.time()
            libres.append(i)
    return libres

def wait_slot(pool):
    '''surveille un pool de process et attends une disponibilité'''
    while get_slot(pool) == -1:
        time.sleep(0.1)
        #        print ('attente zzzz', pool)
    return get_slot(pool)


def wait_end(pool):
    '''attend que le dernier process d'un pool ait terminé'''
    while len(get_slots(pool)) < len(pool):
#        print('attente ',len(actifs), actifs[0].poll(), actifs[0].args)
        time.sleep(0.1)
    return



def execparallel_ext(blocks, maxworkers, lanceur, patience=None):
    '''lance des process en parallele'''
    pool = get_pool(maxworkers)
    for tache in blocks:
        nom, params = tache
        slot = wait_slot(pool) # on cherche une place
        if pool[slot]:
            retour = pool[slot]
            nom_r = retour['nom']
#            print ('slot retour', slot, retour)
#            blocks[nom_r] = (retour['params'], retour['end']-retour['start'])
            if patience:
#                patience(nom_r, *blocks[nom_r])
                patience(nom_r, retour['params'], retour['end']-retour['start'])
        if nom is None: # on envoie un None pour reduire le pool
            del pool[slot]
            continue
        pool[slot] = {'process':lanceur(params), 'nom':nom,
                      'start':time.time(), 'params':params, 'end': None}
    wait_end(pool)
    for i in pool:
        if pool[i]:
            retour = pool[i]
#            print ('retour fin', i, retour)
            nom = retour['nom']
#            blocks[nom] = (retour['params'], retour['end']-retour['start'])
            if patience:
#                patience(nom, *blocks[nom])
                patience(nom, retour['params'], retour['end']-retour['start'])



def iterparallel_ext(blocks, maxworkers, lanceur, patience=None):
    '''lance des process en parallele et retourne les resultats des que disponible'''
    pool = get_pool(maxworkers)
    a_traiter = []
    libres = []
    print ('dans iter parallelext',maxworkers,len(blocks))
    while len(libres) < len(pool):
        try:
#            print ('itp:',a_traiter, len(libres), len(pool))
            a_traiter = sorted(a_traiter)
            taille, nom = a_traiter.pop()
            yield nom
        except IndexError:
            yield None
        for slot in get_slots(pool):
            if pool[slot]:
#                print ('trouve element a traiter',pool[slot])
                retour = pool[slot]
                nom_r = retour['nom']
                if patience:
                    patience(nom_r, retour['params'], retour['end']-retour['start'])
                a_traiter.append((retour['taille'],retour['fich']))
            if blocks:
                tache = blocks.pop()
#                print ('recu tache',tache, len(blocks))
                nom, params, dest, size = tache
                pool[slot] = {'process':lanceur(params), 'nom':nom, 'end': None,
                          'start':time.time(), 'params':params, 'fich':dest,
                          'taille':size}
            else:
#                print ('fin de tache')
                pool[slot] = None
        libres=get_slots(pool)

    a_traiter = sorted(a_traiter)
    print ('on finit les restes')
    for i in a_traiter:
        taille, nom = i
        yield nom


def parallel_load(regle):
    '''traite les chargements en parallele'''

    idobj = []
    entrees = []
    mapper = regle.stock_param

    for num, obj in enumerate(regle.tmpstore):
        fichs = getfichs(regle, obj)
        idobj.extend([num]*len(fichs))
        entrees.extend(fichs)
    arglist = [(i, j, regle.index) for i, j in zip(idobj, entrees)]
    nprocs, _ = regle.get_max_workers()
    num_regle = [regle.index]*len(entrees)
    rdict = dict()
    schemas, env, def_regles = prepare_env_parallel(regle)
#    print('parallel load',entrees,idobj, type(mapper.env))
    with ProcessPoolExecutor(max_workers=nprocs) as executor:
#TODO en python 3.7 l'initialisation peut se faire dans le pool
        rinit = parallelexec(executor, nprocs, initparallel,
                             (mapper.parms, mapper.macros, env, None, schemas))
        workids = {pid:n+1 for n, pid in enumerate(rinit)}
#        print ('workids',workids)
        LOGGER.info(' '.join(('workids', str(workids))))
        parallelexec(executor, nprocs, setparallelid,
                     (workids, def_regles, mapper.liste_params))
        if regle.debug:
            print('retour init', rinit, num_regle)
#        results = executor.map(parallelprocess, idobj, entrees, num_regle)
#        rdict = parallelmap_suivi(mapper, executor, parallelprocess, arglist)
        rdict = paralleliter_suivi(mapper, nprocs, executor, parallelprocess, arglist)

        rfin = parallelexec(executor, nprocs, endparallel, '')
#        if regle.debug:
#        print ('retour')
    for i in rfin:
        retour = rfin[i][0]
        print (i, 'worker', retour['wid'], 'traites',
               retour['stats_generales']['_st_lu_objs'],
               list(sorted(retour['schemas'].keys())))
        for param in retour['stats_generales']:
            mapper.padd(param, retour['stats_generales'][param])
        LOGGER.info('retour stats'+str(sorted(retour['stats_generales'].items())))
        fichs = retour['fichs']
        for nom, nbr in fichs.items():
            mapper.liste_fich[nom] = mapper.liste_fich.get(nom, 0)+nbr
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
        print ('fin traitement parallele', obj)
        traite(obj, regle.branchements.brch["end"])
    regle.nbstock = 0




