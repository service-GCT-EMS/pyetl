# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de gestion du deroulement d'un script
"""
from base64 import encode
import os
import sys
import re

import time
import logging
import copy
from collections import defaultdict
from .traitement_geom import setschemainfo


# from concurrent.futures import ProcessPoolExecutor
# from multiprocessing.pool import Pool
# import multiprocessing

from pyetl.formats.interne.objet import Objet
from .outils import renseigne_attributs_batch, getfichs


LOGGER = logging.getLogger(__name__)


def h_pass(regle):
    """ajoute un point de branchement"""
    regle.sortie = ""
    if regle.params.cmp1.val:
        regle.branchements.addsortie(regle.params.cmp1.val)
        regle.sortie = regle.params.cmp1.val
    return True


def f_pass(regle, obj):
    """#aide||ne fait rien et passe. permet un branchement distant
    #parametres||;;point de branchement si defini les objets seront sortis sur ce pt
    #pattern||;;;pass;?C;
    #test||obj||C1;X;;;C1;Z;;set||+sinon:;;;;;;;pass||+:;;;;C1;Y;;set||atv;C1;Y
    #!test4||obj||^X;1;;set;||$defaut=3||^;;;pass;;;;atts=X,defaut=2||
          ||X;1;;;X;%defaut%;;set||atv;X;3
    """
    obj.redirect = regle.sortie
    return True


def f_fail(regle, obj):
    """#aide||ne fait rien mais plante. permet un branchement distant
    #parametres||;;point de branchement si defini les objets seront sortis sur ce pt
       #pattern||;;;fail;?C;
       #helper||pass
       #test||obj||^;;;fail||+fail:;;;;C1;Y;;set||atv;C1;Y
    """
    #    print ("fail:prochaine regle",regle.branchements.brch["sinon"])
    obj.redirect = regle.sortie
    return False


def f_next(regle, obj):
    """#aide||force la sortie next
    #pattern||;;;next;;
    """
    obj.redirect = "next"
    return True


def h_return(regle):
    """ gere le return d'une macro appelee par call"""
    regle._return = True
    if regle.params.cmp1.val:
        regle.branchements.addsortie(regle.params.cmp1.val)


def f_return(regle, obj):
    """#aide||sort d une macro
    #pattern||;;;return;?C;
    """
    obj.redirect = regle.params.cmp1.val
    # print("erreurs", regle.getvar("erreurs"))
    # print("obj", obj)
    # print(
    #     "redirect==================",
    #     obj.redirect,
    #     regle.branchements.brch.get(obj.redirect),
    # )
    return True


def h_start(regle):
    """helper start"""
    regle.chargeur = True
    schema = regle.params.cmp1.val
    regle.reel = regle.params.cmp2.val
    if schema == "#schemas":
        regle.schemas = [
            regle.stock_param.schemas[i]
            for i in regle.stock_param.schemas
            if not i.startswith("#")
        ]
    else:
        schemaref = regle.stock_param.schemas.get(schema)
        regle.schemas = [schemaref] if schemaref else []
    # import osprint("trouve schemas", regle.schemas)
    return True


def f_start(regle, obj):
    """#aide||ne fait rien mais envoie un objet virtuel ou reel dans le circuit avec un schema si defini
    #pattern||;;;start;?C;=?reel
    #test||rien||^;;;start||^;;;reel||cnt;1
    """
    regle.stock_param.logger.info("start %s %s", obj.ido if obj else "", regle.reel)
    if obj:  # on a deja un objet pas la peine d'en refaire un
        return True
    if regle.schemas:
        for schema in regle.schemas:
            for ident, sc in schema.classes.items():
                niveau, classe = ident
                obj2 = Objet(
                    niveau,
                    classe,
                    format_natif="interne",
                    conversion=None if regle.reel else "virtuel",
                    schema=sc,
                )
                regle.stock_param.moteur.traite_objet(
                    obj2, regle.branchements.brch["next"]
                )
        return True
    else:
        obj2 = Objet(
            "_declencheur", "_start", format_natif="interne", conversion="virtuel"
        )
    #    print('commande start: declenchement ', obj2)
    regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["next"])
    return True


def h_end(regle):
    """helper final"""
    regle.final = True
    return True


def f_end(_, __):
    """#aide||finit un traitement sans stats ni ecritures
    #pattern||;;;end;;
    #test||obj||^;;;end;;||^V;1;;testobj;test;1;||cnt;1
    """
    return True


def h_sync(regle):
    """helper final"""
    if regle.stock_param.worker:
        regle.final = True
    return True


def f_sync(_, __):
    """#aide||finit un traitement parallele sans stats ni ecritures
    #aide_spec||permets de limiter la partie parallele du traitement a une partie du script
    #pattern||;;;end;;
    #test||obj||^;;;sync;;||^V;1;;testobj;test;1;||cnt;1
    """
    return True


def h_sync(regle):
    """helper final"""
    if regle.stock_params.worker:
        regle.final = True
        if regle.params.cmp1.val:
            regle.stock_params.setvar("_w_end", regle.params.cmp1.val)
    return True


def f_sync(regle, __):
    """#aide||finit un traitement en parallele et redonne la main sans stats ni ecritures
    #pattern||;;;sync;?C;
    """
    return True


def f_reel(regle, obj):
    """#aide||transforme un objet virtuel en objet reel
    #pattern||;;;reel;;
    #--test1||rien||^;;;start||^;;;reel||cnt;1
    #test2||obj;;2||;;;;;;;virtuel;;;||^;;;reel;;;||cnt;1
    """
    # print("dans reel", obj.ido)

    if obj.virtuel:
        obj.virtuel = False
        return True
    return False


def f_virtuel(_, obj):
    """#aide||transforme un objet reel en objet virtuel
    #pattern||;;;virtuel;;
       #test||obj;;2||V0;1;;;;;;virtuel||cnt;1

    """
    if obj.virtuel:
        return False
    obj.virtuel = True
    return True


def h_chargeur(regle):
    """helper generique definissant une regle comme executable"""
    regle.chargeur = True
    return True


def f_abort(regle, obj):
    """#aide||arrete le traitement
    #aide_spec||arrete l operation en cours et renvoie un message
              ||
              ||niveaux d arret
              ||
              ||* 1 arret du traitement de l'objet (defaut)
              ||* 2 arret du traitment de la classe
              ||* 3 arret du traitement pour le module
              ||* 4 sortie en catastrophe du programme
     #pattern1||;;;abort;?N;?C
     #parametres1||;niveau;message
         #test||obj;point;2;||V0;1;;;;;;abort;1;;;||^X;0;;set||cnt;1

    """
    niveau = regle.params.cmp1.val or "1"
    message = regle.params.cmp2.val
    LOGGER.info("stop iteration %s %s", niveau, repr(regle))
    if message.startswith("["):
        message = obj.attributs.get(message[1:-1])
    if message:
        # print("abort: arret du traitement ", message, regle.ligne)
        LOGGER.info("arret %s", message)
    if niveau <= "4":
        raise StopIteration(int(niveau))
    LOGGER.critical("panic!!!! arret immediat de mapper")
    exit(0)


def printfunc(regle, obj):
    """ gere le boulot de print pour choisir vers ou l on sort """
    txt = regle.params.cmp1.val or regle.params.att_sortie.val
    if txt and txt[0] == "[":
        cmp1 = obj.attributs.get(txt[1:-1])
    else:
        cmp1 = txt
    noms = regle.params.cmp2.val or regle.params.val_entree.val
    # print("affichage", obj)
    if regle.params.att_entree.dyn:
        liste = obj.get_dynlisteval(noms=noms)
    elif regle.params.att_entree.val == "#geomV":
        if not regle.params.cmp1.val:
            cmp1 = "geomV:"
        return cmp1 + repr(obj.geom_v)
    else:
        liste = obj.get_listeattval(regle.params.att_entree.liste, noms=noms)
    if len(liste) > 1:
        return str(cmp1) + ",".join(liste)
    # print(" affichage simple", regle.getval_entree(obj))
    return (
        str(cmp1) + str(regle.getval_entree(obj)) if cmp1 else regle.getval_entree(obj)
    )


def h_sample(regle):
    """prepare les parametres du sampler"""
    regle.samplers = defaultdict(int)
    regle.clef = regle.params.att_entree.val
    regle.vmin = regle.params.cmp2.num if regle.params.cmp2.num else 0
    regle.vmax = regle.params.cmp2.definition[0] if regle.params.cmp2.definition else 0
    regle.pas = int(regle.params.cmp1.num) if regle.params.cmp1.num else 1


def f_sample(regle, obj):
    """#aide||recupere un objet sur x
    #pattern||;;?A;sample;N;N:N
    #pattern2||;;?A;sample;N;?N
    #test||obj;;10||^;;#classe;sample-;7;1||atv;V0;7
    #test2||obj;;10||^;;;sample-;7;1||atv;V0;7
    """
    clef = obj.attributs.get(regle.clef)
    objnum = regle.samplers[clef]
    regle.samplers[clef] += 1
    #    print ("detecte", objnum, regle.pas,objnum % regle.pas )
    if objnum < regle.vmin:
        return False
    if regle.vmax and objnum > regle.vmax:
        return False
    if objnum % regle.pas:
        return False
    return True


def printvariable(regle):
    """ affichage de variables"""
    nomv = regle.params.cmp1.val
    if not nomv:
        return "\n".join(
            [i + "=" + str(j) for i, j in sorted(regle.context.getvars().items())]
        )

    if regle.params.cmp2.val:  # affichage de noms
        return nomv + "=" + str(regle.getvar(regle.params.cmp1.val))
    v = regle.context.getvar_b(nomv, "")
    # print("printvariable", nomv, type(v), v)
    return regle.context.getvar_b(nomv, "")


def h_printvar(regle):
    """#aide||affichage des parametres nommes"""
    #    print("variables:")
    if not regle.params.att_entree.val:
        regle.print(printvariable(regle))
        regle.done = True
    return True


def f_printvar(regle, _):
    """#aide||affichage des parametres nommes
    #pattern||;;?A;printv;C?;=noms?||entree
    #test||redirect||obj||$toto=ok||^;;;printv;toto||out
    #!test2||redirect||obj||$toto=ok||^;;;printv;||out
    """
    #    print("variables:")
    regle.print(printvariable(regle))
    return True


def h_version(regle):
    """affiche la version"""
    regle.print("pyetl version:" + regle.stock_param.version)
    # LOGGER.log(999, "pyetl version:%s", regle.stock_param.version)

    # print("pyetl version: ", regle.stock_param.version)
    if regle.params.cmp1.val in {"full", "True"}:
        regle.print("version python", sys.version)
    regle.valide = "done"


def f_version(*_):
    """#aide||affiche la version du logiciel et les infos
    #pattern1||;;;version;?=full;;
    #pattern2||;;;version;?=True;;
    #pattern3||;;;version;?=False;;
    #test||notest"""
    return True


def h_print(regle):
    """"affichage direct en webservice"""
    regle.printvirtuel = regle.istrue("virtuel")
    if regle.params.pattern == "3":
        # print(
        #     "affichage variable ws",
        #     regle.params.att_entree.liste,
        #     ",".join((repr(regle.getvar(i)) for i in regle.params.att_entree.liste)),
        # )
        if len(regle.params.att_entree.liste) > 1:
            regle.print([regle.getvar(i) for i in regle.params.att_entree.liste])
        else:
            regle.print(regle.getvar(regle.params.att_entree.val))

        regle.valide = "done"
    return True


def f_print(regle, obj):
    """#aide||affichage d elements de l objet courant
    #parametres||valeur defaut;liste de champs;;texte fixe;affichage noms de champs

    #pattern1||;C?;L?;print;C?;=noms?||entree
    #pattern2||;;*;print;C?;=noms?||entree
    #pattern3||=mws:;=P;?L;print;C?;=noms?||sortie
    #test||redirect||obj||^X;ok;;set||^;;X;print||out
    """
    # print("cmp1>" + regle.params.cmp1.val + "<")
    # print("cmp1>" + regle.v_nommees["cmp1"] + "<")
    if obj.virtuel and not regle.printvirtuel:
        return False
    regle.print(printfunc(regle, obj))
    return True


def f_retour(regle, obj):
    """#aide||ramene les elements apres l execution
    #pattern||;C?;L?;retour;C?;=noms?
    #test||obj||^;;C1;retour;test ok:;noms||out
    """
    # print("f_retour", regle.stock_param.idpyetl, printfunc(regle, obj), obj)
    regle.stock_param.retour.append(printfunc(regle, obj))
    #    print ("retour stocke",regle.stock_param.retour)
    return True


def h_bloc(regle):
    """initialise le compteur de blocs"""
    regle.ebloc = 1
    regle.context.type_c = "B"


def f_bloc(*_):
    """#aide||definit un bloc d'instructions qui reagit comme une seule et genere un contexte
    #pattern||;;;bloc;;
    #test||obj||^X;1;;set;||C1;BCD;;;;;;bloc;||^X;A;;set;||C1;B;;;;;;~fin_bloc;||atv;X;1;
    #test2||obj||^X;1;;set;||$vr=3||;;;;;;;bloc;;;;vr=2||^X;%vr%;;set;||;;;;;;;~fin_bloc;||atv;X;2;
    """

    return True


def h_finbloc(regle):
    """initialise le compteur de blocs"""
    regle.ebloc = -1


def f_finbloc(*_):
    """#aide||definit la fin d'un bloc d'instructions
    #pattern||;;;fin_bloc;;
    #test||obj||^X;1;;set;||C1;BCD;;;;;;~bloc;||^X;A;;set;||C1;B;;;;;;fin_bloc;||atv;X;1;
    """
    return True


def h_callmacro(regle):
    """charge une macro et gere la tringlerie d'appel"""
    regle.refs = []
    mapper = regle.stock_param
    regle.moteur = mapper.getmoteur()
    # print ("callmacro contexte", regle.context)
    # print ("callmacro variables", (context.getvars()))
    if regle.mode == "geomprocess":
        regle.setlocal("macromode", "geomprocess")

    vpos = "|".join(regle.params.cmp2.liste)
    commande = regle.params.cmp1.val + "|" + vpos if vpos else regle.params.cmp1.val
    if regle.params.pattern == "2":
        commande = regle.getlocal("_commande")
    # print("callmacro commande:", commande, regle)

    # print("regle.context.atts:",regle.context.getvar('atts'))
    mapper.pushcontext(regle.context)
    erreurs = mapper.lecteur_regles(commande, regle_ref=regle)  # cree liste_regles
    if regle.liste_regles:
        pass
        # mapper.compilateur(regle.liste_regles, regle.debug, parent=regle)
        # regle.moteur.setregles(regle.liste_regles)
    else:
        regle.valide = "done"
    mapper.popcontext(
        typecheck="C", orig="h_callmacro"
    )  # on sort du contexte de la macro
    # print("call:", regle)
    return erreurs


def f_callmacro(regle, obj):
    """#aide||appel de macro avec gestion de variables locales
    #pattern1||;;;call;C;?LC
    #pattern2||;;;call;;
    #!test1||obj||^X;1;;set;||^;;;call;#set;X,,2||atv;X;2
    #test2||obj||^X;1;;set;||^;;;call;#set;;;atts=X,defaut=2||atv;X;2
    #test3||obj||^X;1;;set;||$defaut=3||^;;;call;#set;;;atts=X,defaut=2||
          ||X;2;;;X;%defaut%;;set||atv;X;3
    #test4||obj||^X;1;;set;||$defaut=3||^;;;call;#set;;;atts=X,defaut=2||
          ||X;2;;;X;%defaut%;;set||atv;X;3
    """
    # print("appel macro", regle.liste_regles)
    return regle.moteur.traite_objet(obj, regle.liste_regles[0], parent=regle)


def f_geomprocess(regle, obj):
    """#aide||applique une macro sur une copie de la geometrie et recupere des attributs
    #aide_spec||permet d'appliquer des traitements destructifs sur la geometrie sans l'affecter
    #pattern||;;;geomprocess;C;?LC
    #helper||callmacro
    #
    #"""
    if obj.virtuel:
        return True
    geom = obj.geom_v
    obj.geom_v = copy.deepcopy(geom)
    sauveschema = bool(obj.schema)
    if sauveschema:
        multi = obj.schema.multigeom
        # sauvegarde infos schema geometriques"
        nom_geometrie = obj.schema.info["nom_geometrie"]
        dimension = obj.schema.info["dimension"]
        type_geom = obj.schema.info["type_geom"]
        courbe = obj.schema.info["courbe"]
    retour = regle.stock_param.moteur.traite_objet(obj, regle.liste_regles[0])
    # print ('retour geomprocess', retour)
    obj.geom_v = geom
    if sauveschema:
        setschemainfo(regle, obj, multi=multi, dyn=True)
        obj.schema.info["nom_geometrie"] = nom_geometrie
        obj.schema.info["dimension"] = dimension
        obj.schema.info["type_geom"] = type_geom
        obj.schema.info["courbe"] = courbe

    # print ('retour geomprocess')
    return retour


def h_creobj(regle):
    """ definit la regle comme createur"""
    regle.chargeur = True  # c est une regle qui cree des objets
    return True


def f_creobj(regle, obj):
    """#aide||cree des objets de test pour les tests fonctionnels
    #parametres1||liste d'attributs;liste valeurs;liste att valeurs;;nom(niv,classe);nombre d'objets a creer
    #pattern1||L;LC;?L;creobj;C;?N||sortie
    #parametres2||liste d'attributs;liste valeurs;;nom(niv,classe);nombre d'objets a creer
    #pattern2||L;LC;;testobj;C;?N||sortie
    #test||rien||^A;1;;creobj;essai;2;||cnt;2
    """

    noms = regle.params.att_sortie.liste
    vals = regle.getlist_entree(obj)
    tmp = regle.params.cmp1.liste
    #    print ('testobj: ',regle.params.cmp1,noms,vals)

    ident = (tmp[0], tmp[1]) if len(tmp) == 2 else ("niv_test", tmp[0])

    schema = regle.getschema(regle.getvar("schema_entree"))
    if schema is None:
        schema = regle.stock_param.init_schema("schema_test", origine="B", stable=False)
    gen_schema = ident not in schema.classes
    schemaclasse = schema.setdefault_classe(ident)
    modifschema = gen_schema and schemaclasse.amodifier(regle)
    if modifschema:
        schemaclasse.info["type_geom"] = "0"
    # TODO gérer les dates
    for nom, val in zip(noms, vals):
        try:
            int(val)
            type_attribut = "E"
        except (ValueError, TypeError):
            try:
                float(val)
                type_attribut = "F"
            except (ValueError, TypeError):
                type_attribut = "T"
        if modifschema:
            schemaclasse.stocke_attribut(nom, type_attribut=type_attribut)
    nombre = int(regle.params.cmp2.num) if regle.params.cmp2.num is not None else 1
    for i in range(nombre):
        obj2 = Objet(ident[0], ident[1], format_natif="interne")
        obj2.setschema(schemaclasse)
        obj2.attributs.update([j for j in zip(noms, vals)])
        # print("objet_test", obj2.ido)
        obj2.setorig(i)
        try:
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
        except StopIteration as abort:
            #            print("intercepte abort",abort.args[0])
            if abort.args[0] == 1:
                continue
            elif abort.args[0] == 2:
                break
            else:
                raise
    return True


def _prepare_batch_from_object(regle, obj):
    """extrait les parametres pertinents de l'objet decrivant le batch"""

    comm = regle.getval_entree(obj)
    commande = comm if comm else obj.attributs.get("commandes", "")

    entree = obj.attributs.get("entree", regle.getvar("_entree"))
    sortie = obj.attributs.get("sortie", regle.getvar("_sortie"))
    numero = obj.attributs.get("#_batchnum", "0")
    nom = obj.attributs.get("nom", "batch")
    #    chaine_comm = ':'.join([i.strip(" '") for i in commande.strip('[] ').split(',')])
    parametres = obj.attributs.get("parametres")  # parametres en format hstore

    params = {"_nom_batch=": nom}
    if parametres:
        params.update(i.split('"=>"', 1) for i in re.split('" *, *"', parametres[1:-1]))

        # print("recuperation parametres hstore", parametres, params)
    # print("commande batch", numero, commande, entree, sortie, params)

    return (numero, commande, entree, sortie, params)


def _execbatch(regle, obj):
    """execute un batch"""
    if obj is None:  # pas d'objet on en fabrique un sur mesure
        obj = Objet("_batch", "_batch", format_natif="interne")
        obj.attributs["nom"] = regle.getvar("_nom_batch", "batch")
        # on lui donne un nom
    _, commande, entree, sortie, params = regle.prepare(regle, obj)
    # print("------------------------- appel batch", commande, "\n", params)
    processor = regle.stock_param.getpyetl(
        commande, liste_params=params, entree=entree, rep_sortie=sortie
    )
    if processor is None:
        return False

    processor.process(debug=1)
    renseigne_attributs_batch(regle, obj, processor.retour)
    return True


def h_batch(regle):
    """definit la fonction comme etant a declencher"""
    regle.chargeur = regle.params.cmp1.val == "run"
    regle.prog = _execbatch
    regle.prepare = _prepare_batch_from_object
    if regle.params.pattern in "45":  # boucle : on compile la macro
        erreurs = regle.stock_param.lecteur_regles(
            regle.params.cmp2.val, regle_ref=regle
        )
        if regle.liste_regles:
            regle.stock_param.compilateur(
                regle.liste_regles, regle.debug
            )  # la on appelle en mode sous programme
    regle.stock_param.gestion_parallel_batch(regle)


def f_batch(regle, obj):
    """#aide||execute un traitement batch a partir des parametres de l'objet
               ||s'il n y a pas de commandes en parametres elle sont prises dans l objet
               ||les attribut utilise sont: commandes,entree,sortie et parametres
    #parametres||attribut_resultat;commandes;attribut_commandes;batch;mode_batch
    #aide_spec1||execute pour chaque objet, demarre toujours, meme sans objets
      #pattern1||A;?C;?A;batch;?=run;||cmp1
    #aide_spec2||demarre a l'initialisation du script maitre
      #pattern2||A;?C;?A;batch;=init;||cmp1
    #aide_spec3||demarre a l'initialisation de chaque process parallele
      #pattern3||A;?C;?A;batch;=parallel_init;||cmp1
    #aide_spec4||reprend le jeu de donnees en boucle
      #pattern4||A;?C;?A;batch;=boucle;C||cmp1
    #aide_spec5||passe une fois le jeu de donnees
      #pattern5||A;?C;?A;batch;=load;C||cmp1
        #schema||ajout_attribut
          #!test||obj||^parametres;"nom"=>"V1", "valeur"=>"12";;set;;;||^X;#obj,#atv;;batch||atv;X;12
          #test1||obj||^parametres;"valeur"=>"12", "nom"=>"V1";;set;;;||^X;#obj,#atv;;batch||atv;X;12
         #!test2||obj||^X;#obj,#atv:V1:12;;batch||atv;X;12
         #!test3||obj;;10||^X;#obj,#atv:V1:%z%;;batch;;;;z=12||atv;X;12
    """
    if regle.store:
        regle.tmpstore.append(obj)
        regle.nbstock += 1
        return True

    return regle.prog(regle, obj)


def f_boucle(regle, obj):
    """#aide||execute un traitement batch en boucle a partir des parametres de l'objet
    #parametres||;attribut_resultat;commandes;attribut_commandes;batch;mode_batch
    #aide_spec1|| en mode run le traitement s'autodeclenche sans objet
      #pattern1||A;?C;?A;boucle;C;?C||cmp1
       #schema||ajout_attribut
        #test2||obj||^X;#obj,#atv:V1:12;;batch||atv;X;12
    """
    regle.tmpstore.append(obj)
    regle.nbstock += 1
    return True


def h_fileloader(regle):
    """prepare la lecture"""
    if "[" in regle.params.cmp1.val:
        regle.dyn = True
    else:
        regle.dyn = False
        regle.chargeur = True
    regle.stock_param.gestion_parallel_load(regle)


def objloader(regle, obj):
    """charge des objets depuis des fichiers"""
    nb_lu = 0
    lecture = regle.stock_param.lecture
    retour = False
    for i, parms in getfichs(regle, obj):
        # print("lecture", i, parms)
        try:
            nb_lu += lecture(i, regle=regle.branchements.brch["gen"], parms=parms)
            retour = True
        except StopIteration as abort:
            if abort.args[0] == 2:
                continue
    #    print("lecture",nb_lu)
    if not retour:
        print("chargeur: pas de fichiers d'entree")
    if regle.params.att_sortie.val:
        obj.attributs[regle.params.att_sortie.val] = str(nb_lu)
    return retour


def f_fileloader(regle, obj):
    """#aide||chargement d objets en fichier
     #aide_spec||cette fonction est l' équivalent du chargement initial
               ||peut fonctionner en parallele positionner multi a -1
               ||pour un nombre de process egal au nombre de processeurs
       #pattern||?A;?C;?A;charge;?C;
      #pattern2||?A;?C;?A;charge;[A];
    #parametres||sortie:nb obj lus;
        #schema||ajout_attribut
         #test2||obj||^NB;;;charge;%testrep%/refdata/lecture;;;multi=2||+gen:;;;;;;;pass>;;;||atv;NB;8
    """
    if obj.attributs.get("#categorie") == "traitement_virtuel":
        return True
        # on est en mode virtuel pour completer les schemas  il suffit de laisser passer les objets
    if regle.store:
        # print("mode parallele", os.getpid(), regle.stock_param.worker)
        # print ('regles', regle.stock_param.regles)
        regle.tmpstore.append(obj)
        regle.nbstock += 1
        return True
    # print ("appel objloader")
    return objloader(regle, obj)


def h_statprint(regle):
    """ imprime les stats a la fin"""
    #        print ('impression stats ')
    regle.stock_param.statstore.statprint = "print"
    regle.stock_param.statstore.statfilter = (
        regle.params.cmp1.val or regle.params.att_sortie.val
    )
    regle.valide = "done"


def f_statprint(*_):
    """#aide||affiche les stats a travers une macro eventuelle
    #aide_spec||statprint;macro
       #pattern||;;;statprint;?C;
       #test||notest
    """
    return True


def h_statprocess(regle):
    """ retraite les stats en appliquant une macro"""
    #    print ('impression stats ')
    regle.stock_param.statstore.statprint = "statprocess"
    regle.stock_param.statstore.statfilter = (
        regle.params.cmp1.val or regle.params.att_sortie.val
    )
    regle.stock_param.statstore.statdest = (
        regle.params.cmp2.val or regle.params.val_entree.val
    )

    regle.valide = "done"


def f_statprocess(*_):
    """#aide||retraite les stats en appliquant une macro
    #aide_spec||statprocess;macro de traitement;sortie
       #pattern||;;;statprocess;C;?C;
       #test||obj;;4||$stat_defaut=X||^T;;;stat>;cnt;||^;;;statprocess;#atv:T:4||rien
    """
    return True


def h_liste_paramgroups(regle):
    """liste les groupes de parametres selon un critere"""
    if regle.params.pattern == "2":
        paramlist = []
        if regle.params.cmp1.val:
            clef = regle.params.cmp1.val
            val = regle.params.val_entree.liste
            for nom, vals in regle.stock_param.site_params.items():
                # print("params", nom, vals)
                v2 = dict(vals)
                if clef in v2 and (v2[clef] in val or not val):
                    paramlist.append(nom)
        else:
            paramlist = list(regle.stock_param.site_params.keys())
        sortie = regle.stock_param.webstore.setdefault("#print", [])
        sortie.extend(paramlist)
        regle.valide = "done"
    return True


def f_liste_paramgroups(regle, obj):
    """#aide||liste les groupes de parametres selon un critere
    #pattern1||A;?C;?A;paramgroups;?C;;
    #pattern2||=mws:;?LC;;paramgroups;?C;;
    """
    paramlist = []
    if regle.params.cmp1.val:
        clef = regle.params.cmp1.val
        val = regle.getlist_entree(obj)
        for nom, vals in regle.stock_param.site_params.items():
            # print("params", nom, vals, clef, val)
            v2 = dict(vals)
            if clef in v2 and (v2[clef] in val or not val):
                paramlist.append(nom)
    else:
        paramlist = list(regle.stock_param.site_params.keys())
    groupe = obj.ident[0]
    classe = "paramgroups"
    virtuel = regle.istrue("virtuel")
    for i in paramlist:
        obj2 = Objet(
            groupe,
            classe,
            format_natif="interne",
            conversion="virtuel" if virtuel else None,
            attributs={regle.params.att_sortie.val: i},
        )
        try:
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
        except StopIteration as abort:
            #            print("intercepte abort",abort.args[0])
            if abort.args[0] == 2:
                break
            raise
    return True


def h_schema_liste_classes(regle):
    """liste des classes d un schema"""
    # print(
    #     "h liste classes",
    #     regle.params.pattern,
    #     regle.params.cmp1.val,
    #     regle.params.val_entree,
    # )
    if regle.params.pattern == "2":
        schema = regle.getschema(regle.params.cmp1.val)
        sortie = regle.stock_param.webstore.setdefault("#print", [])
        if regle.params.val_entree.val in ("schemas", "groupes"):
            sortie.extend(list(schema.groupes.keys()))
        elif regle.params.val_entree.val == "classes":
            sortie.extend(list(schema.classes))
        else:
            return False
        regle.valide = "done"
    print("h liste classes", regle.valide)
    regle.chargeur = True
    return True


def f_schema_liste_classes(regle, obj):
    """#aide||cree des objets virtuels ou reels a partir des schemas (1 objet par classe)
    #aide_spec||liste_schema;nom;?reel
    #aide_spec2||cree des objets virtuels par defaut sauf si on precise reel
    #helper||chargeur
    #schema||change_schema
    #pattern1||?=#schema;?C;?A;liste_schema;C;?=reel
    #pattern2||=mws:;?C;;liste_schema;C;||sortie
    #pattern3||A;?C;;liste_schema;C;||sortie
    """
    schema = regle.getschema(regle.params.cmp1.val)
    print(
        "recup schema", regle.params.cmp1.val, regle.stock_param.schemas.keys(), schema
    )
    if schema is None:
        return False
    virtuel = not regle.params.cmp2.val
    if regle.params.pattern == "3":
        if regle.params.val_entree.val in ("schemas", "groupes"):
            for groupe in schema.groupes.keys():
                obj2 = obj.dupplique()
                obj2.setsortie(groupe)
                regle.stock_param.moteur.traite_objet(
                    obj2, regle.branchements.brch["gen"]
                )
        elif regle.params.val_entree.val == "classes":
            for groupe in schema.groupes.keys():
                obj2 = obj.dupplique()
                obj2.setsortie(groupe)
                regle.stock_param.moteur.traite_objet(
                    obj2, regle.branchements.brch["gen"]
                )

    classes = list(schema.classes)
    for i in classes:
        niveau, classe = i
        obj2 = Objet(
            niveau,
            classe,
            format_natif="interne",
            conversion="virtuel" if virtuel else None,
            schema=schema.classes[i],
        )
        obj2.initattr()
        try:
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
        except StopIteration as abort:
            #            print("intercepte abort",abort.args[0])
            if abort.args[0] == 2:
                break
            raise
    return True


# cas particulier : declaration de sorties supplementaires :
# a partir du moment ou elles sont declarees par
# la fonction addsortie elles sont automatiquement gerees par l'interpreteur et le compilateur
def h_filter(regle):
    """prepare les sorties pour le filtre """

    ls1 = regle.params.cmp1.liste
    ls2 = (
        regle.params.cmp2.liste if regle.params.cmp2.liste else regle.params.cmp1.liste
    )
    regle.liste_sortie = dict(zip(ls1, ls2))
    for i in ls2:
        regle.branchements.addsortie(i)
    regle.branchements.addsortie("#autre")
    regle.branchements.addsortie("#blanc")
    regle.branchements.addsortie("#vide")
    # print("filtre", regle.liste_sortie, regle.branchements.brch)
    return True


def f_filter(regle, obj):
    """#aide||filtre en fonction d un attribut
    #aide_spec||sortie;defaut;attribut;filter;liste valeurs;liste sorties
              ||si la liste de sorties est vide c'est les valeurs qui font office de sortie
      #pattern||?S;?C;A;filter;LC;?LC
         #test||obj||^WW;;C1;filter;AB,BB,C||+AB:;;;;X;1;;~set||+BB:;;;;X;2;;~set||atv;X;1
        #test2||obj||^WW;;C1;filter;AB,BB,CD;1,2,3||+1:;;;;X;1;;~set||atv;X;1
    """
    if regle.params.att_entree.val in obj.attributs:
        valeur = obj.attributs[regle.params.att_entree.val]
    elif regle.params.val_entree.val:
        valeur = regle.params.val_entree.val
    else:
        valeur = None

    if valeur is not None:
        if valeur in regle.liste_sortie:
            obj.redirect = regle.liste_sortie[valeur]
        elif not valeur:
            obj.redirect = "#blanc"
        else:
            obj.redirect = "#autre"
    else:
        obj.redirect = "#vide"

    regle.setval_sortie(obj, obj.redirect)
    # obj.redirect = obj.redirect+':'
    # print("redirect", obj.redirect, regle.branchements)
    return True


def h_idle(regle):
    """ne fait rien"""
    regle.valide = "done"


def f_idle(_, __):
    """#aide||ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)
    #pattern||;;;idle;;
    """
    return True


def f_sleep(regle, obj):
    """#aide||attends;;
    #parametres||duree defaut;att_duree
    #pattern||;?C;?A;sleep;;
    #test||obj||^A;P:#seconds;;set||^;1;;sleep||^B;P:#seconds;;set||^res;;N:B-N:A;set||atn;res;1
    """
    try:
        flemme = float(regle.getval_entree(obj))
    except ValueError:
        flemme = 1
    # un peu de deco ....
    # print("attente:", flemme, "s")
    LOGGER.info("attente: %d s", flemme)
    if flemme > 5 and not regle.stock_param.worker:
        dormir = flemme / 10
        for i in range(10):
            print(".", end="", flush=True)
            time.sleep(dormir)
        print()
    else:
        time.sleep(flemme)
    return True


def f_retry(regle, obj):
    """#aide||relance un traitement a intervalle regulier
    #pattern||A;;;retry;C;
    """
    pass


def h_attreader(regle):
    """initialise le reader"""
    format = regle.params.cmp1.val
    if format not in regle.stock_param.formats_connus_lecture:
        raise SyntaxError("format de lecture inconnu:" + format)
    regle.reader = regle.stock_param.getreader(format, regle)

    regle.nom_att = regle.params.att_entree.val
    regle.format = format
    regle.keepdata = regle.istrue("keepdata")


def f_attreader(regle, obj):
    """#aide||traite un attribut d'un objet comme une source de donnees
    #parametres||defaut;attribut;;format
     #aide_spec||par defaut attreader supprime le contenu de l attribut source
               ||pour le conserver positionner la variable keepdata a 1
       #pattern||?L;?C;A;attreader;C;?C
    """
    # print("attaccess", obj.attributs[regle.params.att_entree.val])
    regle.reader.attaccess(obj)
    # print("attaccess", obj.attributs[regle.params.att_entree.val])

    if not regle.keepdata:  # on evite du duppliquer des gros xml
        obj.attributs[regle.params.att_entree.val] = ""


def h_attsave(regle):
    """prepare les repertoires"""
    regle.destdir = os.path.join(regle.getvar("_sortie"), regle.params.cmp1.val)
    regle.encoding = regle.getvar("encoding", "utf-8")
    return True


def f_attsave(regle, obj):
    """#aide||stocke le contenu d un attribut comme un fichier
    #parametres||;attribut;;fichier
    #pattern||A;?C;A;attsave;?C
    """
    fich = os.path.join(regle.destdir, regle.getval_entree(obj))
    destdir = os.path.dirname(fich)
    os.makedirs(destdir, exist_ok=True)
    contenu = obj.attributs.get(regle.params.att_sortie.val)
    # print("attsave", type(contenu))
    if contenu:
        if isinstance(contenu, str):
            with open(fich, "w", encoding=regle.encoding) as sortie:
                sortie.write(contenu)
            # print("attsave: ecrit", contenu)
        elif isinstance(contenu, list):
            with open(fich, "w", encoding=regle.encoding) as sortie:
                sortie.writelines(contenu)
        elif isinstance(contenu, dict):
            with open(fich, "w", encoding=regle.encoding) as sortie:
                sortie.writelines((";".join(i) for i in contenu.items()))
        else:
            with open(fich, "wb") as sortie:
                sortie.write(contenu)
        return True
    else:
        return False


def h_attload(regle):
    """prepare les repertoires"""
    regle.loaddir = os.path.join(regle.getvar("_entree"), regle.params.cmp1.val)
    regle.encoding = regle.getvar("encoding", "utf-8")
    regle.format = regle.params.cmp2.val
    return True


def f_attload(regle, obj):
    """#aide||stocke le contenu d un fichier dans un attribut
    #parametres||;attribut;;fichier
    #pattern||A;?C;A;attload;?C;?C
    """
    fich = os.path.join(regle.loaddir, regle.getval_entree(obj))
    if regle.format == "B":
        contenu = open(
            fich,
            "rb",
        ).read()
    else:
        contenu = open(fich, "r", encoding=regle.encoding).readlines()
    # print("attload", type(contenu))
    if contenu:
        obj.attributs[regle.params.att_sortie.val] = contenu
        return True
    else:
        return False


def h_parallel(regle):
    """ preparation parrallel """
    pass


def f_parallel(regle, obj):
    """passe en paralele
    #aide||passe le traitement en parralele les objets sont dispatches sur les workers
    #pattern||;;;parallel;?N;?N
    """
    pass


def h_endpar(regle):
    """fin parralele"""
    if regle.stock_param.worker:
        regle.final = True
    regle.valide = "done"
    return True


def f_endpar(regle, obj):
    """finit un traitement parralele
    #pattern||;;;end_parallel;;
    #"""
    pass


def h_resetlog(regle):
    "reinitialise le log"
    if not regle.stock_param.worker:  # ne marche que sur le process maitre
        regle.stock_param.gestion_log.resetlogfile(
            regle.params.cmp1.val, regle.params.cmp2.val
        )
    regle.valide = "done"
    return True


def f_resetlog(regle, obj):
    """reinitialise les fichiers log
    #pattern||;;;resetlog;=del;C
    #"""
    pass
