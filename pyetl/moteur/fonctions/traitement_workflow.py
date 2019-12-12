# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de gestion du deroulement d'un script
"""
import os
import sys

# import re
import zipfile
import time
import logging
import copy
from collections import defaultdict
from .traitement_geom import setschemainfo


# from concurrent.futures import ProcessPoolExecutor
# from multiprocessing.pool import Pool
# import multiprocessing
import ftplib
try:
    import pysftp
    SFTP=True
except ImportError:
    SFTP=False
import requests
from pyetl.formats.interne.objet import Objet
from .outils import execbatch, objloader


LOGGER = logging.getLogger("pyetl")


def f_pass(*_):
    """#aide||ne fait rien et passe
        #pattern||;;;pass;;
        #test||obj||C1;X;;;C1;Z;;set||+sinon:;;;;;;;pass||+:;;;;C1;Y;;set||atv;C1;Y
        #!test4||obj||^X;1;;set;||$defaut=3||^;;;pass;;;;atts=X,defaut=2||
              ||X;1;;;X;%defaut%;;set||atv;X;3
    """
    return True


def f_fail(*_):
    """#aide||ne fait rien mais plante
        #pattern||;;;fail;;
        #test||obj||^;;;fail||+fail:;;;;C1;Y;;set||atv;C1;Y
    """
    #    print ("fail:prochaine regle",regle.branchements.brch["sinon"])
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
    #pattern||;;;quitter;?C;
    """
    obj.redirect = regle.params.cmp1.val
    return True


def h_start(regle):
    """helper start"""
    regle.chargeur = True
    return True


def f_start(regle, obj):
    """#aide||ne fait rien mais envoie un objet virtuel dans le circuit
    #pattern||;;;start;;
    #test||rien||^;;;start||^;;;reel||cnt;1
    """
    #    print ('start',obj)
    if obj:  # on a deja un objet pas la peine d'en refaire un
        return True
    obj2 = Objet("_declencheur", "_autostart", format_natif="interne", conversion="virtuel")
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
            regle.stock_params.set_param("_w_end", regle.params.cmp1.val)
    return True


def f_sync(regle, __):
    """#aide||finit un traitement en parallele et redonne la main sans stats ni ecritures
    #pattern||;;;sync;?C;
    """
    return True


def f_reel(_, obj):
    """#aide||transforme un objet virtuel en objet reel
    #pattern||;;;reel;;
    #test||rien||^;;;start||^;;;reel||cnt;1
    #test2||obj;;2||V0;1;;;;;;virtuel||^;;;reel;;;||cnt;2
    """
    #    print("dans reel",obj)

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
  #aide_spec||usage: abort,niveau,message
 #aide_spec1||1 arret du traitement de l'objet
 #aide_spec2||2 arret du traitment de la classe
 #aide_spec3||3 arret du traitement pour le module
 #aide_spec4||4 sortie en catastrophe
    #pattern||;;;abort;?N;?C
       #test||obj;point;2;||V0;1;;;;;;abort;1;;;||^X;0;;set||cnt;1

    """
    niveau = regle.params.cmp1.val or regle.params.att_sortie.val
    message = regle.params.cmp2.val or regle.params.val_entree.val
    LOGGER.info('stop iteration '+repr(regle))
    if message.startswith("["):
        message = obj.attributs.get(message[1:-1])
    if message:
        print("abort: arret du traitement ", message, regle.ligne)
    if niveau <= "4":
        raise StopIteration(niveau)
    exit(0)


def printfunc(regle, obj):
    """ gere le boulot de print pour choisir vers ou l on sort """
    txt = regle.params.cmp1.val or regle.params.att_sortie.val
    if txt and txt[0] == "[":
        cmp1 = obj.attributs.get(txt[1:-1])
    else:
        cmp1 = txt
    noms = regle.params.cmp2.val or regle.params.val_entree.val
    #    print ('affichage', obj)
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
    return cmp1 + regle.getval_entree(obj)


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
    if not regle.params.cmp1.val:
        return "\n".join([i + "=" + str(j) for i, j in sorted(regle.context.getvars().items())])

    if regle.params.cmp2.val:
        return regle.params.cmp1.val + "=" + str(regle.context.getvar(regle.params.cmp1.val))
    return regle.context.getvar(regle.params.cmp1.val)


def f_printvar(regle, _):
    """#aide||affichage des parametres nommes
       #pattern||;;;printv;C?;=noms?||entree
       #test||redirect||obj||$toto=ok||^;;;printv;toto||end
       #!test2||redirect||obj||$toto=ok||^;;;printv;||end
    """
    #    print("variables:")
    print(printvariable(regle))
    return True


def h_version(regle):
    """affiche la version"""
    print("pyetl version: ", regle.stock_param.version)
    if regle.params.cmp1.val:
        print("version python", sys.version)
    regle.valide = "done"


def f_version(*_):
    """#aide||affiche la version du logiciel et les infos
        #pattern||;;;version;?=full;;
        #test||notest"""
    return True


def f_print(regle, obj):
    """#aide||affichage d elements de l objet courant
       #pattern1||;C?;L?;print;C?;=noms?||entree
       #pattern2||;;*;print;C?;=noms?||entree
       #test||redirect||obj||^X;ok;;set||^;;X;print||end
    """
    print(printfunc(regle, obj))
    return True


def f_retour(regle, obj):
    """#aide||ramene les elements apres l execution
       #pattern||;C?;L?;retour;C?;=noms?
       #test||obj||^;;C1;retour;test ok:;noms||end
    """
    #    print ("f_retour", regle.stock_param.idpyetl, printfunc(regle, obj))
    regle.stock_param.retour.append(printfunc(regle, obj))
    #    print ("retour stocke",regle.stock_param.retour)
    return True


def h_bloc(regle):
    """initialise le compteur de blocs"""
    regle.ebloc = 1
    regle.context.type_c='B'


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
    regle.call = regle.mode in {'call'}
    # print ("callmacro contexte", regle.context)
    # print ("callmacro variables", (context.getvars()))
    if regle.mode == 'geomprocess':
        regle.context.setvar('macromode', 'geomprocess')
    mapper = regle.stock_param
    vpos = "|".join(regle.params.cmp2.liste)
    commande = regle.params.cmp1.val + "|" + vpos if vpos else regle.params.cmp1.val
    # print("callmacro commande:", commande,regle.params.cmp2.val)
    # print("regle.context.atts:",regle.context.getvar('atts'))
    mapper.pushcontext(regle.context)
    # print ('contexte macro', mapper.cur_context)
    erreurs = mapper.lecteur_regles(commande, regle_ref=regle)
    if regle.liste_regles:
        if regle.call: # la on applatit
            regle.liste_regles[-1]._return = True
        else:
            mapper.compilateur(regle.liste_regles, regle.debug) #la on appelle en mode sous programme
    # print ('contexte apres macro', mapper.cur_context)
    mapper.popcontext(typecheck='C')
    return erreurs


def f_callmacro(regle, obj):
    """#aide||appel de macro avec gestion de variables locales
       #pattern||;;;call;C;?LC
       #!test1||obj||^X;1;;set;||^;;;call;#set;X,,2||atv;X;2
       #test2||obj||^X;1;;set;||^;;;call;#set;;;atts=X,defaut=2||atv;X;2
       #test3||obj||^X;1;;set;||$defaut=3||^;;;call;#set;;;atts=X,defaut=2||
             ||X;2;;;X;%defaut%;;set||atv;X;3
       #test4||obj||^X;1;;set;||$defaut=3||^;;;call;#set;;;atts=X,defaut=2||
             ||X;2;;;X;%defaut%;;set||atv;X;3
    """
    # la on ne fait rien parce que le compilateur a applati la macro
    return True







def f_geomprocess(regle,obj):
    """#aide||applique une macro sur la geometrie et recupere des attributs et/ou la geometrie
    #aide_spec||
    #pattern||;;;geomprocess;C;?LC
    #helper||callmacro
    #
    # """
    geom = obj.geom_v
    obj.geom_v = copy.deepcopy(geom)
    multi = obj.schema.multigeom if obj.schema else None
    retour = regle.stock_param.moteur.traite_objet(obj, regle.liste_regles[0])
    # print ('retour geomprocess', retour)
    obj.geom_v = geom
    setschemainfo(regle, obj, multi=multi)

    # print ('retour geomprocess')
    return retour



def h_testobj(regle):
    """ definit la regle comme createur"""
    regle.chargeur = True  # c est une regle qui cree des objets
    return True


def f_testobj(regle, obj):
    """#aide||cree des objets de test pour les tests fonctionnels
       #aide_spec||parametres:liste d'attributs,liste valeurs,nom(niv,classe),nombre
       #pattern||L;LC;;testobj;C;?N||sortie
       #test||rien||^A;1;;testobj;essai;2||cnt;2
    """
    #    if not obj.virtuel:
    #        return False
    return f_creobj(regle, obj)


def f_creobj(regle, obj):
    """#aide||cree des objets de test pour les tests fonctionnels
       #aide_spec||parametres:liste d'attributs,liste valeurs,nom(niv,classe),nombre
       #pattern||L;LC;?L;creobj;C;?N||sortie
       #test||obj||^A;1;;creobj;essai;2||cnt;3
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
    if gen_schema:
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
        if gen_schema:
            schemaclasse.stocke_attribut(nom, type_attribut=type_attribut)
    nombre = int(regle.params.cmp2.num) if regle.params.cmp2.num is not None else 1
    for i in range(nombre):
        obj2 = Objet(ident[0], ident[1], format_natif="interne")
        obj2.setschema(schemaclasse)
        obj2.attributs.update([j for j in zip(noms, vals)])
        #        print ("objet_test",obj2.attributs,obj2.schema.schema.nom)
        obj2.setorig(i)
        try:
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["next"])
        except StopIteration as abort:
            #            print("intercepte abort",abort.args[0])
            if abort.args[0] == "2":
                break
            raise
    return True


def h_ftpupload(regle):
    """prepare les parametres ftp"""
    regle.chargeur = True
    codeftp = regle.params.cmp1.val
    regle.destdir = regle.params.cmp2.val
    serveur = regle.context.getvar("server_" + codeftp, "")
    servertyp = regle.context.getvar("ftptyp_" + codeftp, "")
    user = regle.context.getvar("user_" + codeftp, "")
    passwd = regle.context.getvar("passwd_" + codeftp, regle.params.cmp2.val)
    regle.setlocal("acces_ftp", (codeftp, serveur, servertyp, user, passwd))
    regle.ftp = None
    regle.servertyp = servertyp

def ftpconnect(regle):
    '''connection ftp'''

    _, serveur, servertyp, user, passwd = regle.getvar("acces_ftp")
    # print ('ouverture acces ',regle.getvar('acces_ftp'))
    try:
        if servertyp == "tls":
            regle.ftp = ftplib.FTP_TLS(host=serveur, user=user, passwd=passwd)
            return True
        elif servertyp == "ftp":
            regle.ftp = ftplib.FTP(host=serveur, user=user, passwd=passwd)
            return True
    except ftplib.error_perm as err:
        print("!!!!! erreur ftp: acces non autorisé",serveur, servertyp, user, passwd)
        print("retour_erreur",err)
        return False
    if servertyp == "sftp" and SFTP:
        try:
            cno = pysftp.CnOpts()
            cno.hostkeys = None
            regle.ftp = pysftp.Connection(serveur, username=user, password=passwd, cnopts=cno)
            return True
        except pysftp.ConnectionException as err:
            print("!!!!! erreur ftp: acces non autorisé",serveur, servertyp, user, passwd)
            print("retour_erreur",err)
            return False
    else:
        print ("mode ftp non disponible", servertyp)
        return False


def f_ftpupload(regle, obj):
    """#aide||charge un fichier sur ftp
  #aide_spec||;nom fichier; (attribut contenant le nom);ftp_upload;ident ftp;
    #pattern||;?C;?A;ftp_upload;C;?C
       #test||notest
    """
    filename = regle.getval_entree(obj)
    destname = regle.destdir+ '/'+ str(os.path.basename(filename))

    # destname = regle.destdir
    if not regle.ftp:
        retour = ftpconnect(regle)
        if not retour:
            return False
        print ('connection ftp etablie')


    try:
        # print ('envoi fichier',filename,'->',destname)
        if regle.servertyp == 'sftp':
            regle.ftp.cwd(regle.destdir)
            regle.ftp.put(filename)
            print ("transfert effectue",filename,'->',destname)
        else:
            localfile = open(filename, "rb")
            regle.ftp.storbinary("STOR " + destname, localfile)
            localfile.close()
            print ("transfert effectue",filename,'->',destname)
        return True

    except ftplib.all_errors as err:
        print("!!!!! erreur ftp: acces non autorisé",serveur, servertyp, user)
        print("retour_erreur", err)
        LOGGER.error("ftp upload error: Houston, we have a %s", "major problem", exc_info=1)
        return False


def f_ftpdownload(regle, obj):
    """#aide||charge un fichier sur ftp
  #aide_spec||;nom fichier; (attribut contenant le nom);ftp_download;ident ftp;repertoire
    #pattern||;?C;?A;ftp_download;C;?C
     #helper||ftpupload
       #test||notest
    """
    if not regle.ftp:
        if not regle.ftp:
            retour = ftpconnect(regle)
            if not retour:
                return False
        print ('connection ftp etablie')


    filename = regle.getval_entree(obj)
    localdir = regle.getvar('localdir',os.path.join(regle.getvar('_sortie','.')))
    localname = os.path.join(localdir,filename)
    os.makedirs(localdir,exist_ok=True)
    print('creation repertoire',localdir)

    try:
        if regle.servertyp == 'sftp':
            print ('choix repertoire',regle.destdir)
            regle.ftp.cwd(regle.destdir)
            if filename == '*':
                regle.ftp.get_d('.',localdir, preserve_mtime=True)
            elif filename == '*/*':
                regle.ftp.get_r('.',localdir, preserve_mtime=True)
            else:
                regle.ftp.get(filename,localpath=localname, preserve_mtime=True)
        else:
            localfile = open(localname, "wb")
            regle.ftp.retrbinary("RETR " + filename, localfile.write)
            localfile.close()
        print ("transfert effectue",filename,'->',localname)
        return True

    except ftplib.all_errors as err:
        print("!!!!! erreur ftp: acces non autorisé")
        LOGGER.error("ftp download error: Houston, we have a %s", "major problem", exc_info=1)
        return False


def h_httpdownload(regle):
    """prepare les parametres http"""
    regle.chargeur = True
    path = regle.params.cmp1.val if regle.params.cmp1.val else regle.getvar("_sortie")
    os.makedirs(path, exist_ok=True)
    regle.path=path
    if regle.params.cmp2.val:
        name = os.path.join(path, regle.params.cmp2.val)
        regle.fichier = name
    else:
        regle.fichier = None

def f_httpdownload(regle, obj):
    """aide||telecharge un fichier via http
 #aide_spec||; url; (attribut contenant le url);http_download;repertoire;nom
   #pattern||;?C;?A;download;?C;?C
      #test||notest
      """
    url = regle.getval_entree(obj)
    if regle.fichier is None:
        fichier = os.path.join(regle.path, os.path.basename(url))
    else:
        fichier = regle.fichier
    print("telechargement", url)
    retour = requests.get(url, stream=True)
    print("info", retour.headers)
    taille = int(retour.headers["Content-Length"])
    decile = taille / 10
    recup = 0
    bloc = 4096
    nb_pts = 0
    debut = time.time()
    if retour.status_code == 200:
        with open(fichier, "wb") as fich:
            for chunk in retour.iter_content(bloc):
                recup += bloc  # ca c'est la deco avec des petits points ....
                if recup > decile:
                    recup = recup - decile
                    nb_pts += 1
                    print(".", end="", flush=True)
                fich.write(chunk)
        print("    ", taille, "octets télecharges en ", int(time.time() - debut), "secondes")
        return True
    return False


def h_archive(regle):
    """definit la regle comme declenchable"""
    regle.chargeur = True


def f_archive(regle, obj):
    """#aide||zippe les fichiers ou les repertoires de sortie
  #aide_spec|| parametres:liste de noms de fichiers(avec *...);attribut contenant le nom;archive;nom
    #pattern||;?C;?A;archive;C;
       #test||notest
       """
    #    if not obj.virtuel:
    #        return False
    dest = regle.params.cmp1.val + ".zip"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    stock = dict()
    print("archive",time.ctime, regle.params.val_entree.liste, dest, regle.getvar("_sortie"))
    if regle.params.att_entree.val:
        fich = obj.attributs.get(regle.params.att_entree.val)
        if fich:
            stock[fich] = fich
        mode = "a"
    else:
        mode = "w"
        LOGGER.info("archive : ecriture zip:"+','.join(regle.params.val_entree.liste)+' -> '+dest)
        for f_interm in regle.params.val_entree.liste:
            clefs = []
            if "*" in os.path.basename(f_interm):
                clefs = [i for i in os.path.basename(f_interm).split("*") if i]
                #                print( 'clefs de fichier zip',clefs)
                f_interm = os.path.dirname(f_interm)
            if os.path.isdir(f_interm):
                for fich in os.listdir(f_interm):
                    #                    print(' test fich ',fich, [i in fich for i in clefs])
                    if all([i in fich for i in clefs]):
                        stock[os.path.join(f_interm, fich)] = fich
            else:
                stock[f_interm] = f_interm

    with zipfile.ZipFile(dest, compression=zipfile.ZIP_BZIP2, mode=mode) as file:
        for i in stock:
            file.write(i, arcname=stock[i])
    print ('fin_archive',dest, time.ctime())
    LOGGER.info("fin_archive "+dest)
    return True


def h_batch(regle):
    """definit la fonction comme etant a declencher"""
    if regle.params.cmp1.val == "run":
        regle.chargeur = True
    regle.prog = execbatch
    if regle.params.pattern in '45': # boucle : on compile la macro
        mapper = regle.stock_param
        erreurs = mapper.lecteur_regles(regle.params.cmp2.val, regle_ref=regle)
        if regle.liste_regles:
            mapper.compilateur(regle.liste_regles, regle.debug) #la on appelle en mode sous programme
    regle.stock_param.gestion_parallel_batch(regle)


def f_batch(regle, obj):
    """#aide||execute un traitement batch a partir des parametres de l'objet
  #aide_spec||parametres:attribut_resultat,commandes,attribut_commandes,batch
    #pattern1||A;?C;?A;batch;?=run;?N||cmp1
    #pattern2||A;?C;?A;batch;=init;||cmp1
    #pattern3||A;?C;?A;batch;=parallel_init;||cmp1
    #pattern4||A;?C;?A;batch;=boucle;C||cmp1
    #pattern5||A;?C;?A;batch;=load;C||cmp1
     #schema||ajout_attribut
       #test||obj||^parametres;"nom"=>"V1", "valeur"=>"12";;set||^X;#obj,#atv;;batch||atv;X;12
      #test2||obj||^X;#obj,#atv:V1:12;;batch||atv;X;12
      #test3||obj;;10||^X;#obj,#atv:V1:%z%;;batch;;3;;z=12||atv;X;12
    """
    if regle.store:
        regle.tmpstore.append(obj)
        regle.nbstock += 1
        return True

    return regle.prog(regle, obj)


def h_fileloader(regle):
    """prepare la lecture"""
    if "[" in regle.params.cmp1.val:
        regle.dyn = True
    else:
        regle.dyn = False
        regle.chargeur = True
    regle.stock_param.gestion_parallel_load(regle)


def f_fileloader(regle, obj):
    """#aide||chargement d objets en fichier
  #aide_spec||cette fonction est l' équivalent du chargement initial
    #pattern||?A;?C;?A;charge;?C;?N
   #pattern2||?A;?C;?A;charge;[A];?N
     #schema||ajout_attribut
       #test||obj||^;;;charge>;%testrep%/refdata/join.csv||atv;valeur;1
      #test2||obj||^NB;;;charge;%testrep%/refdata/lecture;2;||#classe;!test;;;;;;pass>;;;
            ||atv;NB;8
    """
    if obj.attributs.get("#categorie") == "traitement_virtuel":
        return True
        # on est en mode virtuel pour completer les schemas  il suffit de laisser passer les objets
    if regle.store:
        # print( 'mode parallele', os.getpid(), regle.stock_param.worker)
        # print ('regles', regle.stock_param.regles)
        regle.tmpstore.append(obj)
        regle.nbstock += 1
        return True
    return objloader(regle, obj)





def h_statprint(regle):
    """ imprime les stats a la fin"""
    #        print ('impression stats ')
    regle.stock_param.statprint = "print"
    regle.stock_param.statfilter = regle.params.cmp1.val or regle.params.att_sortie.val
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
    regle.stock_param.statprint = "statprocess"
    regle.stock_param.statfilter = regle.params.cmp1.val or regle.params.att_sortie.val
    regle.stock_param.statdest = regle.params.cmp2.val or regle.params.val_entree.val

    regle.valide = "done"


def f_statprocess(*_):
    """#aide||retraite les stats en appliquant une macro
    #aide_spec||statprocess;macro de traitement;sortie
       #pattern||;;;statprocess;C;?C;
       #test||obj;;4||$stat_defaut=X||^T;;;stat>;cnt;||^;;;statprocess;#atv:T:4||rien
    """
    return True


def f_schema_liste_classes(regle, _):
    """#aide||cree des objets virtuels ou reels a partir des schemas (1 objet par classe)
    #aide_spec||liste_schema;nom;?reel
    #aide_spec2||cree des objets virtuels par defaut sauf si on precise reel
    #helper||chargeur
    #schema||change_schema
    #pattern||?=#schema;?C;?A;liste_schema;C;?=reel
    """
    schema = regle.getschema(regle.params.cmp1.val)
    if schema is None:
        return False
    virtuel = not regle.params.cmp2.val
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
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["next"])
        except StopIteration as abort:
            #            print("intercepte abort",abort.args[0])
            if abort.args[0] == "2":
                break
            raise
    return True


# cas particulier : declaration de sorties supplementaires :
# a partir du moment ou elles sont declarees par
# la fonction addsortie elles sont automatiquement gerees par l'interpreteur et le compilateur
def h_filter(regle):
    """prepare les sorties pour le filtre """

    ls1 = regle.params.cmp1.liste
    ls2 = regle.params.cmp2.liste if regle.params.cmp2.liste else regle.params.cmp1.liste
    regle.liste_sortie = dict(zip(ls1, ls2))
    for i in ls2:
        regle.branchements.addsortie(i)
    regle.branchements.addsortie("#autre")
    regle.branchements.addsortie("#blanc")
    regle.branchements.addsortie("#vide")
    #    print("filtre", regle.liste_sortie)
    return True


def f_filter(regle, obj):
    """#aide||filtre en fonction d un attribut
  #aide_spec||sortie;defaut;attribut;filter;liste sorties;liste valeurs
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

    if regle.fstore:
        regle.fstore(regle.params.att_sortie, obj, obj.redirect)
    #    obj.redirect = obj.redirect+':'
    #    print("redirect", obj.redirect, regle.branchements)
    return True


def h_idle(regle):
    """ne fait rien"""
    #        print ('impression stats ')
    regle.valide = "done"


def f_idle(_, __):
    """#aide||ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)
    #pattern||;;;idle;;
    """
    return True


def f_sleep(regle, obj):
    """#aide||ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)
    #pattern||;?C;?A;sleep;;
    """
    try:
        flemme = float(regle.regle.getval_entree(obj))
    except ValueError:
        flemme = 1
    # un peu de deco ....
    print ('attente:', flemme, 's')
    if flemme > 5:
        dormir = flemme/10
        for i in range(10):
            print ('.',end='',flush=True)
            time.sleep(dormir)
        print
    else:
        time.sleep(sleeptime)
    return True

def f_retry(regle,obj):
    """#aide||relance un traitement a intervalle regulier
    #pattern||A;;;retry;C;
    """
    pass