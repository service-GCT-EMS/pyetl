# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de structurelles diverses
"""
import os
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
from .outils import charge_mapping, remap, prepare_elmap, renseigne_attributs_batch


LOGGER = logging.getLogger("pyetl")

def h_run(regle):
    """execution unique si pas d'objet dans la definition"""
    if regle.params.att_entree.val or regle.params.val_entree.val:
        print ('retour run ', regle)
        return
    if regle.runscope():  # on voit si on doit l'executer
        chaine = " ".join((regle.params.cmp1.val, regle.params.cmp2.val))
        print("lancement ", chaine)
        fini = ''
        fini = subprocess.run(chaine, stderr=subprocess.STDOUT, shell=True)
        if regle.params.att_sortie.val:
            regle.stock_param.set_param(regle.params.att_sortie.val, fini)
    print ('retour run : done')
    regle.valide = "done"


def f_run(regle, obj):
    """#aide||execute un programme exterieur
  #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
    #pattern||?A;?C;?A;run;C;?C
   #pattern2||P;;;run;C;?C
     #schema||ajout_attribut
    """
    if regle.runscope():  # on voit si on doit l'executer
        chaine = " ".join((regle.params.cmp1.val, regle.params.cmp2.val, regle.getval_entree(obj)))
        raise
        fini = subprocess.run(chaine, stderr=subprocess.STDOUT, shell=True)
        if regle.params.att_sortie.val:
            obj.attributs[regle.params.att_sortie.val] = str(fini)
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
  #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
    #pattern||;;;os_ren;C;C
    #pattern2||A;;A;os_ren;?C;?C
    """
    try:
        os.rename(os.path.join(regle.chemin_orig,regle.params.att_entree.val),
                    os.path.join(regle.chemin_final,regle.params.att_sortie.val))
        return True
    except (FileNotFoundError,FileExistsError):
        return False

def f_filecopy(regle, obj):
    """#aide||renomme un fichier
  #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
    #pattern||;;;os_copy;C;C
    #pattern2||A;;A;os_copy;?C;?C
    #helper||filerename
    """
    try:
        shutil.copy2(os.path.join(regle.chemin_orig,regle.params.att_entree.val),
                    os.path.join(regle.chemin_final,regle.params.att_sortie.val))
        return True
    except (FileNotFoundError,FileExistsError):
        return False

def f_filemove(regle, obj):
    """#aide||renomme un fichier
  #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
    #pattern||;;;os_move;C;C
    #pattern2||A;;A;os_move;?C;?C
    #helper||filerename
    """
    try:
        shutil.move(os.path.join(regle.chemin_orig,regle.params.att_entree.val),
                    os.path.join(regle.chemin_final,regle.params.att_sortie.val))
        return True
    except (FileNotFoundError,FileExistsError):
        return False

def f_filedel(regle, obj):
    """#aide||renomme un fichier
  #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
    #pattern||;;;os_del;C;
    #pattern2||;;A;os_del;?C;
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
    #pattern||;?C;?A;listefich;;
    """
    if regle.get_entree(obj):
        fichs = getfichs(regle,obj)