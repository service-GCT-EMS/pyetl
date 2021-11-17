# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de structurelles diverses
"""
import os
import subprocess
from pathlib import Path
from collections import namedtuple
import shutil
import time
from typing import NamedTuple

# import win32con
try:
    import win32security
except ImportError:
    print("module  win32security non disponible : pas d info utilisateurs")
    win32security = None
from .outils import getfichs


def commandrunner(regle, chaine):
    """execute une commande et renvoie eventuellement le resultat"""
    # print ("commandrunner",regle)
    # print ("commandrunner",regle.params.cmp1.val,regle.params.cmp2.val)
    chaine = regle.params.cmp1.val + " " + chaine
    try:
        if regle.params.att_sortie.val:
            fini = subprocess.run(
                chaine, capture_output=True, shell=True, encoding=regle.consoleencoding
            )
            retour = fini.stdout + fini.stderr
            if retour.endswith("\n"):
                retour = retour[:-1]
            if regle.debug:
                print("commandrunner", chaine, "->", retour)
            return retour
        else:
            fini = subprocess.run(
                chaine,
                stderr=subprocess.STDOUT,
                shell=True,
                encoding=regle.consoleencoding,
            )
            return None
    except OSError as err:
        regle.stock_param.logger.error("erreur d execution %s -> %s", chaine, err)
        raise StopIteration(1)


def h_run(regle):
    """execution unique si pas d'objet dans la definition"""
    regle.consoleencoding = regle.getvar("console_encoding", "CP850")
    # print('valeurs parametres', regle.getvar('import'))
    if regle.params.pattern == "1":
        return True
    retour = commandrunner(regle, regle.params.cmp2.val)
    if regle.debug:
        print("commandrunner ", retour)
    if regle.params.att_sortie.val:
        regle.setvar(regle.params.att_sortie.val, retour)
    regle.valide = "done"


def f_run(regle, obj):
    """#aide||execute une commande externe
       #pattern1||?A;?C;?A;run;C;
       #pattern3||P;;;run;C;?C;
     #aide_spec1||execution a chaque objet avec recuperation d'un resultat (l'attribut d'entree ou la valeur par defaut doivent etre remplis)
     #aide_spec3||execution en debut de process avec sans recuperation eventuelle d'un resultat dans une variable
    #parametres||attribut qui recupere le resultat;parametres par defaut;attribut contenant les parametres;commande,parametres
      #variables||process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
                ||\t\t en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
         #schema||ajout_attribut
           #test||obj||^P:aaa;;;run;echo;tété;||ptv:aaa:tété
          #test1||obj||$xx=toto;||^P:aaa;;;run;echo;%xx%;||ptv:aaa:toto
          #test2||obj||^X;toto;;run;echo;;||atv:X:toto
    """
    try:
        retour = commandrunner(regle, regle.getval_entree(obj))
        if regle.params.att_sortie.val:
            obj.attributs[regle.params.att_sortie.val] = retour
        return True
    except StopIteration:
        return False


def fileprep(regle, fonction, dest=False):
    """prepare l'execution d'une fonction generique d'operation sur fichier"""
    regle.dest = dest
    if regle.params.att_entree.val:
        regle.chemin_orig = (
            regle.params.cmp2.val if regle.params.cmp2.val else regle.params.cmp1.val
        )
        regle.chemin_final = regle.params.cmp1.val
        regle.valide = True
    else:
        try:
            if dest:
                regle.chemin_final = os.path.dirname(regle.params.cmp1.val)
                if regle.chemin_final and not os.path.exists(regle.chemin_final):
                    os.makedirs(regle.chemin_final)
            if regle.params.cmp2.val:
                fonction(regle.params.cmp2.val, regle.params.cmp1.val)
            else:
                fonction(regle.params.cmp1.val)
            regle.valide = "done"
        except (FileNotFoundError, FileExistsError, OSError) as err:
            print(
                "erreur ",
                regle.mode,
                regle.params.cmp2.val,
                "->",
                regle.params.cmp1.val,
                err,
            )
            regle.valide = "fail"


def fileop(regle, obj, fonction):
    """fonction generique d'operation sur fichier"""

    try:
        if regle.dest:
            os.makedirs(
                os.path.dirname(
                    os.path.join(
                        regle.chemin_final,
                        obj.attributs.get(regle.params.att_sortie.val, ""),
                    )
                ),
                exist_ok=True,
            )
        fonction(
            os.path.join(regle.chemin_orig, regle.getval_entree(obj)),
            os.path.join(
                regle.chemin_final, obj.attributs.get(regle.params.att_sortie.val, "")
            ),
        )
        print(
            "operation",
            fonction.__name__,
            os.path.join(regle.chemin_orig, regle.getval_entree(obj)),
            os.path.join(
                regle.chemin_final, obj.attributs.get(regle.params.att_sortie.val, "")
            ),
        )
        return True
    except (FileNotFoundError, FileExistsError, OSError):
        raise
        return False


def h_filerename(regle):
    """renomme un fichier execution unique si pas d'objet dans la definition"""
    fileprep(regle, os.rename, dest=True)
    return True


def f_filerename(regle, obj):
    """#aide||renomme un fichier
       #pattern1||;;;os_ren;C;C
       #pattern2||A;?C;A;os_ren;?C;?C
     #aide_spec1||execution unique au demarrage
    #parametres1||nom destination;nom d origine
     #variables1||process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
                ||\t\t en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
     #aide_spec2||execution pour chaque objet
    #parametres2||nom destination,nom d origine;chemin destination;chemin origine
       #req_test||testwriterep
           #test||obj||^;;;os_copy;%testwriterep%;%testrep%/refdata/liste.csv||
                ||is:file;%testwriterep%/liste2.csv;;;;;;os_del;%testwriterep%/liste2.csv||
                ||^;;;os_ren;%testwriterep%/liste2.csv;%testwriterep%/liste.csv||
                ||is:file;%testwriterep%/liste2.csv;;;X;1;;set||atv:X:1
    """
    return fileop(regle, obj, os.rename)


def h_filecopy(regle):
    """renomme un fichier execution unique si pas d'objet dans la definition"""
    fileprep(regle, shutil.copy2, dest=True)
    return True


def f_filecopy(regle, obj):
    """#aide||copie un fichier
      #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
       #pattern1||;;;os_copy;C;C
       #pattern2||A;?C;A;os_copy;?C;?C
     #aide_spec1||execution unique au demarrage
    #parametres1||nom destination;nom d origine
     #variables1||process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
                ||\t\t en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
     #aide_spec2||execution pour chaque objet
    #parametres2||nom destination,nom d origine;chemin destination;chemin origine
       #req_test||testwriterep
           #test||obj||^;;;os_copy;%testwriterep%;%testrep%/refdata/liste.csv||
                ||is:file;%testwriterep%/liste2.csv;;;;;;os_del;%testwriterep%/liste2.csv||
                ||^;;;os_copy;%testwriterep%/liste2.csv;%testwriterep%/liste.csv||
                ||is:file;%testwriterep%/liste2.csv;;;X;1;;set||atv:X:1
    """
    return fileop(regle, obj, shutil.copy2)


def h_filemove(regle):
    """renomme un fichier execution unique si pas d'objet dans la definition"""
    fileprep(regle, shutil.move, dest=True)
    return True


def f_filemove(regle, obj):
    """#aide||deplace un fichier
      #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
       #pattern1||;;;os_move;C;C
       #pattern2||A;?C;A;os_move;?C;?C
     #aide_spec1||execution unique au demarrage
    #parametres1||nom destination;nom d origine
     #variables1||process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
                ||\t\t en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
     #aide_spec2||execution pour chaque objet
    #parametres2||nom destination,defaut,nom d origine;chemin destination;chemin origine
       #req_test||testwriterep
           #test||obj||^;;;os_copy;%testwriterep%;%testrep%/refdata/liste.csv||
                ||is:file;%testwriterep%/liste2.csv;;;;;;os_del;%testwriterep%/liste2.csv||
                ||^;;;os_move;%testwriterep%/liste2.csv;%testwriterep%/liste.csv||
                ||is:file;%testwriterep%/liste2.csv;;;X;1;;set||atv:X:1
    """
    return fileop(regle, obj, shutil.move)


def h_filedel(regle):
    """renomme un fichier execution unique si pas d'objet dans la definition"""
    fileprep(regle, os.remove)
    return True


def f_filedel(regle, obj):
    """#aide||supprime un fichier
      #aide_spec||suppression d'un fichier
       #pattern1||;;;os_del;C;
       #pattern2||;?C;A;os_del;?C;
     #aide_spec1||execution unique au demarrage
    #parametres1||;nom du fichier a supprimer
     #aide_spec2||execution pour chaque objet
    #parametres2||defaut;nom du fichier a supprimer;;chemin
       #req_test||testwriterep
           #test||obj||is:file;%testwriterep%/liste.csv;;;;;;os_del;%testwriterep%/liste.csv||
                ||^;;;os_copy;%testwriterep%;%testrep%/refdata/liste.csv||
                ||is:file;%testwriterep%/liste.csv;;;;;;os_del;%testwriterep%/liste.csv||
                ||is:file;!%testwriterep%/liste.csv;;;X;1;;set||atv:X:1
    """
    try:
        os.remove(os.path.join(regle.chemin_orig, regle.params.att_entree.val))
        return True
    except (FileNotFoundError, OSError):
        return False


def fileinfo(fichier, regle):
    """recupere les infos detaillees d'un fichier"""
    # print ('infos', fichier)
    ajout_attributs = regle.ajout_attributs
    tmp = Path(fichier)
    definition = [str(tmp), str(tmp.parent), tmp.stem, tmp.suffix]
    infos = [0, "inexistant", "inexistant"]
    try:
        if win32security:
            sd = win32security.GetFileSecurity(
                fichier, win32security.OWNER_SECURITY_INFORMATION
            )
            owner_sid = sd.GetSecurityDescriptorOwner()
            uname, domain, typef = win32security.LookupAccountSid(None, owner_sid)
        else:
            uname, domain = "", ""
        statinfo = os.stat(fichier)
        taille = statinfo.st_size
        creation = statinfo.st_ctime
        modif = statinfo.st_mtime
        acces = statinfo.st_atime
        infos = [
            taille,
            domain,
            uname,
            time.ctime(creation),
            time.ctime(modif),
            time.ctime(acces),
        ]
    except NameError:
        uname, domain = "", ""
    except Exception as err:
        print("info:fichier introuvable:", fichier, "->", err)

    # print ('fichier', fichier, statinfo)
    return list(zip(ajout_attributs, definition + infos))


def h_infofich(regle):
    """prepare la structure d'info de fichier"""
    infos = (
        "nom_complet",
        "chemin",
        "nom",
        "ext",
        "taille",
        "domaine",
        "proprietaire",
        "creation",
        "modif",
        "acces",
    )
    regle.infofich = dict()
    prefix = regle.params.att_sortie.val if regle.params.att_sortie.val else "#"
    regle.ajout_attributs = [prefix + i for i in infos]
    regle.nomexiste = regle.params.att_entree.val or regle.params.val_entree.val

    # print ('infofich: champs generes',regle.ajout_attributs)
    return True


def f_infofich(regle, obj):
    """#aide||ajoute les informations du fichier sur les objets
    #aide_spec||usage prefix;defaut;attribut;infofich;;;
              ||prefixe par defaut:#, si pas d'entree s'applique au fichier courant
              ||cree les attributs: #chemin, #nom, #ext,
              ||#domaine, #proprietaire, #creation, #modif, #acces
       #schema||ajout_attribut
      #pattern||?A;?C;?A;infofich;;
         #test||obj||^;%testrep%/refdata/liste.csv;;infofich||atv:#ext:.csv
    """
    # print ('infofich',obj)
    if regle.nomexiste:
        fichier = regle.get_entree(obj)
        # print ('infofich avec entree', fichier)

    else:
        fichier = os.path.join(
            obj.attributs.get("#chemin", ""), obj.attributs.get("#fichier", "")
        ) + obj.attributs.get("#ext", "")
        # print("infofich sans entree", fichier)
    if fichier:
        if fichier not in regle.infofich:
            regle.infofich[fichier] = fileinfo(fichier, regle)
        obj.attributs.update(regle.infofich[fichier])
        return True
    return False


def h_abspath(regle):
    """ prepare le chemin absolu"""
    regle.dynref = regle.params.cmp1.val.startswith("[")
    regle.ref = regle.params.cmp1.val[1:-1] if regle.dynref else regle.params.cmp1.val
    if not regle.ref:
        regle.ref = os.path.curdir


def f_abspath(regle, obj):
    """#aide||change un chemin relatif en chemin absolu
    #aide_spec||le point de depart est le chemin ou cmp1
      #pattern||S;C?;A?;abspath;C?;
         #test||obj||^;%_progdir%;;namesplit;||^absp;;#s_nom;abspath;[#s_chemin]||
              ||^absp2;toto;;set;||^absp2;%_progdir%;;abspath||ata:absp:absp2
         #test2||obj||^X;toto;;set;||^absp;;X;abspath;A:/titi;||atv2|absp|A:\\titi\\toto|
    """
    candidat = regle.get_entree(obj)
    if os.path.isabs(candidat):
        final = candidat
    else:
        ref = (
            os.path.abspath(obj.attributs.get(regle.ref, ""))
            if regle.dynref
            else regle.ref
        )
        final = os.path.normpath(os.path.join(ref, candidat))
    try:
        final = os.path.realpath(final)
    except FileNotFoundError:
        regle.stock_param.logger.error("fichier introuvable %s", final)
    # print("chemin final", candidat, os.path.isabs(candidat), "->", final)
    regle.setval_sortie(obj, final)
    return True


def h_namesplit(regle):
    """prepare la structure d'info de fichier"""
    prefix = regle.params.att_sortie.val if regle.params.att_sortie.val else "#s_"
    regle.ajout_attributs = [prefix + "chemin", prefix + "nom", prefix + "ext"]
    return True


def f_namesplit(regle, obj):
    """#aide||decoupe un nom de fichier en chemin,nom,extention
     #aide_spec||genere les attributs prefix_chemin,prefix_nom,prefix_ext avec un prefixe
    #parametres||prefixe;defaut;attr contenant le nom;namesplit
        #schema||ajout_attribut
       #pattern||?A;C?;A?;namesplit;;
          #test||obj||^;/aaa/bbb/ccc.tst;;namesplit||atv:#s_nom:ccc
    """
    fichier = Path(regle.get_entree(obj))
    # print ('namesplit ',fichier,list(zip(regle.ajout_attributs,(str(fichier.parent),fichier.stem,fichier.suffix))))
    obj.attributs.update(
        zip(regle.ajout_attributs, (str(fichier.parent), fichier.stem, fichier.suffix))
    )
    return True


def f_namejoin(regle, obj):
    """#aide||combine des element en nom de fichier en chemin,nom,extention
       #pattern||S;C?;L?;namejoin;;
    #parametres||sortie;defaut;liste d'attributs;namesjoin
       #test||obj||^n1,n2;toto,titi;;set||^X;;n1,n2;namejoin||^;;X;namesplit||atv:#s_nom:titi
    """
    regle.setval_sortie(obj, os.path.join(*regle.getlist_entree(obj)))
    return True


def dict_decode(attdict, encoding="utf-8"):
    """decode un dictionnaide byte vers str"""
    for i in attdict:
        if isinstance(attdict[i], list):
            attdict[i] = ",".join(
                (
                    (j.decode(encoding) if isinstance(j, bytes) else j)
                    for j in attdict[i]
                )
            )
        elif isinstance(attdict[i], bytes):
            attdict[i] = attdict[i].decode(encoding)


def h_adquery(regle):
    """initialise l'acces active_directory"""

    # print("acces LDAP", ACD.root(), regle)
    regle.a_recuperer = regle.params.cmp2.liste if regle.params.cmp2.liste else ["cn"]
    adcode = regle.getvar("ADserver")
    if adcode:
        # connection specifique a un autre serveur AD
        # on charge le groupe de parametres
        import ldap

        regle.stock_param.load_paramgroup(adcode, nom=adcode)

        server = regle.getvar("server_" + adcode)
        user = regle.getvar("user_" + adcode)
        passwd = regle.getvar("passwd_" + adcode)
        base_dn = regle.getvar("base_dn_" + adcode)
        # print("adconnect ", user, passwd, server)
        try:
            connect = ldap.initialize("ldap://" + server)
            connect.bind_s(user, passwd, ldap.AUTH_SIMPLE)
        except Exception as err:
            print("erreur connection LDAP", adcode, "->", server, err)
            regle.valide = False
            return False
        # print("connecteur LDAP sur ", server)
        # print("champs", ["clef"] + regle.a_recuperer)
        sortie = namedtuple("ldapreturn", ["clef"] + [i for i in regle.a_recuperer])

        def find_user(nom):
            filter = "(|(CN=%s)(sAMAccountName=%s))" % (nom, nom)
            attrs = regle.a_recuperer
            retour = connect.search_s(base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
            if regle.debug:
                print("adquery", base_dn, filter, attrs)
                print("retour adquery", retour)
            result = list()
            if retour:
                for ligne in retour:
                    ref, attdict = ligne
                    dict_decode(attdict)
                    attdict["clef"] = ref
                    # print("stockage attdict", attdict)
                    item = sortie(**attdict)
                result.append(item)
            return result

        if regle.params.pattern == "1" or regle.params.pattern == "4":
            regle.queryfonc = find_user

    else:
        # connection serveur par defaut
        from . import active_directory as ACD

        try:
            regle.AD = ACD
        except ACD.pywintypes.com_error:
            regle.stock_param.logger.error("connection LDAP impossible")
            regle.valide = False
            return False
        # regle.a_recuperer = regle.params.cmp2.val if regle.params.cmp2.val else "CN"
        # print("----AD", regle.params.pattern, regle)
        if regle.params.pattern == "1" or regle.params.pattern == "4":
            regle.queryfonc = regle.AD.find_user
        elif regle.params.pattern == "2":
            regle.queryfonc = regle.AD.find_computer
        elif regle.params.pattern == "3":
            regle.queryfonc = regle.AD.find_group

    if regle.params.pattern == "4":  # variable

        items = regle.queryfonc(regle.params.val_entree.val)
        if items is None:
            regle.stock_param.logger.error(
                "element introuvable: %s", regle.params.val_entree.val
            )
            regle.valide = "done"
            return True
        item = items[0] if isinstance(items, list) else items
        val = getattr(item, regle.a_recuperer[0])
        regle.setvar(regle.params.att_sortie.val, val)
        if regle.debug:
            print(
                "AD setvar",
                regle.params.att_sortie.val,
                regle.params.val_entree.val,
                item,
            )
        regle.valide = "done"


def f_adquery(regle, obj):
    """#aide||extait des information de active_directory
    #pattern1||S;?C;?A;adquery;=user;?C;
    #pattern2||S;?C;?A;adquery;=machine;?C;
    #pattern3||S;?C;?A;adquery;=groupe;?C;
    #pattern4||P;C;;adquery;=user;;||sortie||1
    #req_test||adserver
    #test||obj||X;89965;adquery;user;||atv;X;UNGER Claude;
    #"""
    if regle.get_entree(obj):
        try:
            items = regle.queryfonc(regle.get_entree(obj))
        except TypeError as err:
            print("erreur adquery", err, regle.get_entree(obj))
            items = []
        item = None
        if items:
            if isinstance(items, list):
                if len(items) == 1:
                    item = items[0]
                elif len(items) > 1:
                    for item in items:
                        obj2 = obj.dupplique()
                        val = getattr(item, regle.a_recuperer[0])
                        regle.setval_sortie(obj2, val)
                        regle.stock_param.moteur.traite_objet(obj2, regle.ok)
                    return True
                else:
                    return False  # liste vide
            else:
                item = items
        if regle.a_recuperer == ["*"]:
            print("infos:", item)
            item.dump()
            regle.setval_sortie(obj, "")
        else:
            # print("recup adquery", regle.a_recuperer[0])
            val = getattr(item, regle.a_recuperer[0]) if item else ""
            regle.setval_sortie(obj, val)
        return True
    # print("pas d'entree adquery", regle.get_entree(obj))
    return False


def h_listefich(regle):
    """rends la regle executable"""
    regle.chargeur = True
    if regle.params.pattern == "2":
        regle.setlocal("fileselect", regle.params.val_entree.val)
    regle.setlocal("F_entree", "*")
    regle.extfilter = regle.params.cmp2.liste


def f_listefich(regle, obj):
    """#aide||genere un objet par fichier repondant aux criteres d'entree
    #pattern1||S;?C;A;listefich;?C;?C
    #pattern2||S;?C;;listefich;?C;?C
    #parametres1||attribut de sortie;defaut;selecteur de fichiers;;repertoire;extension;
    #variables||dirselect:selecteur de repertoires
              ||filtre_entree:filtrage noms par expression reguliere
    """
    if regle.params.pattern == "1":
        regle.setlocal("fileselect", regle.get_entree(obj))
    classe = regle.params.cmp1.val or obj.attributs.get("#classe")
    traite_objet = regle.stock_param.moteur.traite_objet
    trouve = False
    for fich in getfichs(regle, obj):
        nom, defs = fich
        racine, chemin, nom_f, ext = defs
        if regle.extfilter and ext not in regle.extfilter:
            continue
        nouveau = obj.dupplique()
        nouveau.attributs["#classe"] = classe
        regle.setval_sortie(nouveau, nom)
        nouveau.attributs["#f_racine"] = racine
        nouveau.attributs["#f_chemin"] = chemin
        nouveau.attributs["#f_base"] = nom_f
        nouveau.attributs["#f_ext"] = ext
        nouveau.attributs["#f_nom"] = nom_f + "." + ext
        traite_objet(nouveau, regle.branchements.brch["gen"])
        trouve = True
    return trouve
