# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de structurelles diverses
"""
import os
import locale
import sys
import re
import logging
import subprocess
from collections import defaultdict
from pathlib import Path
import shutil
import time
import win32api
# import win32con
import win32security

from pyetl.formats.mdbaccess import dbaccess
from pyetl.formats.generic_io import Writer
from .outils import getfichs


LOGGER = logging.getLogger("pyetl")


def commandrunner(regle, chaine):
    """execute une commande et renvoie eventuellement le resultat"""
    # print ("commandrunner",regle.params)
    # print ("commandrunner",regle.params.cmp1.val,regle.params.cmp2.val)
    chaine = regle.params.cmp1.val+" "+ chaine
    if regle.params.att_sortie.val:
        fini = subprocess.run(chaine, capture_output=True, shell=True, encoding=regle.consoleencoding)
        retour = fini.stdout+fini.stderr
        if retour.endswith("\n"):
            retour = retour[:-1]
        return retour
    else:
        fini = subprocess.run(chaine, stderr=subprocess.STDOUT, shell=True, encoding=regle.consoleencoding)
        return None


def h_run(regle):
    """execution unique si pas d'objet dans la definition"""
    regle.consoleencoding=regle.getvar('console_encoding','CP850')
    # print('---------hrun', regle.runscope(),regle,regle.params.pattern)
    # print('valeurs parametres', regle.getvar('import'))
    if regle.params.pattern=="1":
        return
    if regle.runscope():  # on voit si on doit l'executer
        retour=commandrunner(regle, regle.params.cmp2.val)
        if regle.params.att_sortie.val:
            regle.setvar(regle.params.att_sortie.val, retour)
    # print ('retour run : done',retour)
    regle.valide = "done"


def f_run(regle, obj):
    """#aide||execute une commande externe
   #pattern1||?A;?C;?A;run;C
   #pattern3||P;;;run;C;?C
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
    if regle.runscope():  # on voit si on doit l'executer
        retour=commandrunner(regle, regle.getval_entree(obj))
        if regle.params.att_sortie.val:
            obj.attributs[regle.params.att_sortie.val] = retour
        return True
    return False


def h_filerename(regle):
    """renomme un fichier execution unique si pas d'objet dans la definition"""
    if regle.params.att_sortie.val:
        regle.chemin_orig = regle.params.cmp2.val if regle.params.cmp2.val else regle.params.cmp1.val
        regle.chemin_final = regle.params.cmp1.val
        regle.valide = True
    else:
        regle.valide = "done"
        if regle.runscope():  # on voit si on doit l'executer
            try:
                os.rename(regle.params.cmp2.val, regle.params.cmp1.val)
                print ('retour run : done')
            except (FileNotFoundError,FileExistsError):
                regle.valide = False



def f_filerename(regle, obj):
    """#aide||renomme un fichier
   #pattern1||;;;os_ren;C;C
   #pattern2||A;;A;os_ren;?C;?C
 #aide_spec1||execution unique au demarrage
#parametres1||nom destination;nom d origine
 #variables1||process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
            ||\t\t en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
 #aide_spec2||execution pour chaque objet
#parametres2||nom destination,nom d origine;chemin destination;chemin origine
   #req_test||testwriterep
       #test||obj||^;;;os_copy;%testrep%/refdata/liste.csv;%testwriterep%||
            ||^;;;os_ren;%testwriterep%/liste2.csv;%testwriterep%/liste.csv||
            ||is:file;%testwriterep%/liste2.csv;;X;1;;set||atv:X:1

   """
    try:
        os.rename(os.path.join(regle.chemin_orig,regle.params.att_entree.val),
                    os.path.join(regle.chemin_final,regle.params.att_sortie.val))
        return True
    except (FileNotFoundError,FileExistsError):
        return False

def f_filecopy(regle, obj):
    """#aide||copie un fichier
  #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
    #pattern||;;;os_copy;C;C
    #pattern2||A;;A;os_copy;?C;?C
 #aide_spec1||execution unique au demarrage
#parametres1||nom destination;nom d origine
 #variables1||process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
            ||\t\t en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
 #aide_spec2||execution pour chaque objet
#parametres2||nom destination,nom d origine;chemin destination;chemin origine
    #helper||filerename
    #req_test||testwriterep
    """
    try:
        shutil.copy2(os.path.join(regle.chemin_orig,regle.params.att_entree.val),
                    os.path.join(regle.chemin_final,regle.params.att_sortie.val))
        return True
    except (FileNotFoundError,FileExistsError):
        return False

def f_filemove(regle, obj):
    """#aide||deplace un fichier
  #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
    #pattern||;;;os_move;C;C
   #pattern2||A;;A;os_move;?C;?C
 #aide_spec1||execution unique au demarrage
#parametres1||nom destination;nom d origine
 #variables1||process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
            ||\t\t en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
 #aide_spec2||execution pour chaque objet
#parametres2||nom destination,nom d origine;chemin destination;chemin origine
     #helper||filerename
   #req_test||testwriterep

    """
    try:
        shutil.move(os.path.join(regle.chemin_orig,regle.params.att_entree.val),
                    os.path.join(regle.chemin_final,regle.params.att_sortie.val))
        return True
    except (FileNotFoundError,FileExistsError):
        return False

def f_filedel(regle, obj):
    """#aide||supprime un fichier
    #pattern||;;;os_del;C;
    #pattern2||;?C;A;os_del;?C;
    #helper||filerename
    """
    try:
        os.remove(os.path.join(regle.chemin_orig,regle.params.att_entree.val))
        return True
    except (FileNotFoundError):
        return False



def fileinfo(fichier, ajout_attributs):
    '''recupere les infos detaillees d'un fichier'''
    # print ('infos', fichier)
    tmp = Path(fichier)
    definition = [str(tmp),str(tmp.parent),tmp.stem,tmp.suffix]
    infos = [0,'inexistant','inexistant']
    try:
        sd = win32security.GetFileSecurity (fichier, win32security.OWNER_SECURITY_INFORMATION)
        owner_sid = sd.GetSecurityDescriptorOwner ()
        uname, domain, typef = win32security.LookupAccountSid (None, owner_sid)
        statinfo = os.stat(fichier)
        taille = statinfo.st_size
        creation = statinfo.st_ctime
        modif = statinfo.st_mtime
        acces = statinfo.st_atime
        infos = [taille,domain,uname,time.ctime(creation),time.ctime(modif),time.ctime(acces)]
    except NameError:
        uname,domain = '',''
    except Exception as err:
        print ('fichier introuvable', fichier, err)


    # print ('fichier', fichier, statinfo)
    return list(zip(ajout_attributs,definition+infos))

def h_infofich(regle):
    """prepare la structure d'info de fichier"""
    infos= ("nom_complet","chemin","nom","ext","taille",'domaine','proprietaire','creation','modif','acces')
    regle.infofich = dict()
    prefix = regle.params.att_sortie.val if regle.params.att_sortie.val else "#"
    regle.ajout_attributs = [prefix+i for i in infos]
    regle.nomexiste = regle.params.att_entree.val or regle.params.val_entree.val

    # print ('infofich: champs generes',regle.ajout_attributs)
    return True

def f_infofich(regle,obj):
    """#aide||ajoute les informations du fichier sur les objets
  #aide_spec||usage prefix;defaut;attribut;infofich;;;
            ||prefixe par defaut:#, si pas d'entree s'applique au fichier courant
            ||cree les attributs: #chemin_fich, #nom_fich, #ext_fich,
            ||     #domaine_fich, #proprietaire_fich, #creation_fich, #modif_fich, #acces_fich
     #schema||ajout_attribut
    #pattern||?A;?C;?A;infofich;;
    """
    # print ('infofich',obj)
    if regle.nomexiste:
        fichier = regle.get_entree(obj)
        # print ('infofich avec entree', fichier)

    else:
        fichier = os.path.join(obj.attributs.get('#chemin',''),obj.attributs.get('#fichier',''))
        # print ('infofich sans entree', fichier)
    if fichier:
        if fichier not in regle.infofich:
            regle.infofich[fichier] = fileinfo(fichier, regle.ajout_attributs)
        obj.attributs.update(regle.infofich[fichier])
        return True
    return False

def h_abspath(regle):
    """ prepare le chemin absolu"""
    regle.dynref = regle.params.cmp1.val.startswith('[')
    regle.ref = regle.params.cmp1.val[1:-1] if regle.dynref else regle.params.cmp1.val
    if not regle.ref:
        regle.ref = os.path.curdir


def f_abspath(regle,obj):
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
        ref = os.path.abspath(obj.attributs.get(regle.ref,"")) if regle.dynref else regle.ref
        final = os.path.normpath(os.path.join(ref, candidat))
    final = os.path.realpath(final)
    # print ('chemin final',candidat,os.path.isabs(candidat), '->', final)
    regle.setval_sortie(obj, final)
    return True

def h_namesplit(regle):
    """prepare la structure d'info de fichier"""
    prefix = regle.params.att_sortie.val if regle.params.att_sortie.val else "#s_"
    regle.ajout_attributs = [prefix+"chemin",prefix+"nom",prefix+"ext"]
    return True

def f_namesplit(regle,obj):
    """#aide||decoupe un nom de fichier en chemin,nom,extention
  #aide_spec||genere les attributs prefix_chemin,prefix_nom,prefix_ext avec un prefixe
 #parametres||prefixe;defaut;attr contenant le nom;namesplit
     #schema||ajout_attribut
    #pattern||?A;C?;A?;namesplit;;
       #test||obj||^;/aaa/bbb/ccc.tst;;namesplit||atv:#s_nom:ccc
    """
    fichier = Path(regle.get_entree(obj))
    # print ('namesplit ',fichier,list(zip(regle.ajout_attributs,(str(fichier.parent),fichier.stem,fichier.suffix))))
    obj.attributs.update(zip(regle.ajout_attributs,(str(fichier.parent),fichier.stem,fichier.suffix)))
    return True

def f_namejoin(regle,obj):
    """#aide||combine des element en nom de fichier en chemin,nom,extention
    #pattern||S;C?;L?;namejoin;;
 #parametres||sortie;defaut;liste d'attributs;namesjoin
    #test||obj||^n1,n2;toto,titi;;set||^X;;n1,n2;namejoin||^;;X;namesplit||atv:#s_nom:titi
    """
    regle.setval_sortie(obj, os.path.join(*regle.getlist_entree(obj)))
    return True

def h_adquery(regle):
    """initialise l'acces active_directory"""
    from . import active_directory as ACD
    print("acces LDAP", ACD.root())
    regle.AD = ACD
    regle.a_recuperer = regle.params.cmp2.val if regle.params.cmp2.val else 'CN'


def f_adquery(regle,obj):
    """#aide extait des information de active_directory
    #pattern||S;?C;?A;adquery;=user;?C;
    # """
    if regle.get_entree(obj):
        user = regle.AD.find_user(regle.get_entree(obj))
        if user:
            val = getattr(user,regle.a_recuperer)
            regle.setval_sortie(obj,val)
            return True
    # print("pas d'entree adquery",regle.get_entree(obj) )
    return False

def f_listefich(regle,obj):
    """#aide genere un objet par fichier repondant aux criteres d'entree
    #pattern||S;?C;?A;listefich;?C;
    """
    if regle.get_entree(obj):
        classe = regle.params.cmp1.val or obj.attributs.get('#classe')
        traite_objet = regle.stock_param.traite_objets
        for fich in getfichs(regle,obj):
            nouveau = obj.dupplique()
            nouveau.attributs['#classe'] = classe
            regle.setval_sortie(nouveau,fich)
            traite_objets(nouveau)
        return True
    return False

def sel_isfile(selecteur, obj):
    """#aide||tesste si un fichier existe
       #pattern||=is:file;[A]||1
       #pattern2||=is:file;C||1
       #test||obj||^;;;virtuel||^?;;;reel||;is:virtuel;;;C1;1;;set||^;;;reel||atv;C1;1

    """
    return os.path.isfile(obj.attributs[selecteur.params.val.val])
