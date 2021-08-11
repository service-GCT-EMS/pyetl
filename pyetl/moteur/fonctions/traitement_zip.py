# -*- coding: utf-8 -*-
"""

@author: 89965
fonctions s de selections : determine si une regle est eligible ou pas
"""
import os
import sys
import re

import zipfile
import time
import logging


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
    print(
        "archive",
        time.ctime(),
        regle.params.val_entree.liste,
        dest,
        regle.getvar("_sortie"),
    )
    if regle.params.att_entree.val:
        fich = obj.attributs.get(regle.params.att_entree.val)
        if fich:
            stock[fich] = fich
        mode = "a"
    else:
        mode = "w"
        regle.stock_param.logger.info(
            "archive : ecriture zip:"
            + ",".join(regle.params.val_entree.liste)
            + " -> "
            + dest
        )
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
    print("fin_archive", dest, time.ctime())
    regle.stock_param.logger.info("fin_archive " + dest)
    return True


def f_zipdir(regle, obj):
    """#aide||liste les fichiers d un zip
    #aide_spec|| parametres:liste de noms de fichiers(avec *...);attribut contenant le nom;archive;nom
      #pattern1||?A;?C;?A;zipdir;;
      #pattern2||?A;?C;?A;zipdir;=split;
          #test||notest
    """
    name = regle.get_entree(obj)
    if not os.path.isabs(name) and not name.startswith("."):
        name = os.path.join(regle.getvar("_entree", "."), name)
    if not zipfile.is_zipfile(name):
        return False
    with zipfile.ZipFile(name, "r") as archive:
        filelist = archive.namelist()
    if regle.params.pattern == "1":
        obj.attributs[regle.params.att_sortie.val] = filelist
        return True
    for i in filelist:
        obj2 = obj.dupplique()
        obj2.attributs[regle.params.att_sortie.val] = i
        regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])


def f_zipextract(regle, obj):
    """#aide||extrait des fichiers d'un zip
    #aide_spec|| parametres:liste de noms de fichiers(avec *...);attribut contenant le nom;archive;nom
      #pattern1||?C;?C;?A;zipextract;C;?=all
          #test||notest
    """
    name = regle.params.cmp1.getval(obj)
    if not os.path.isabs(name) and not name.startswith("."):
        name = os.path.join(regle.getvar("_entree", "."), name)
    if not zipfile.is_zipfile(name):
        return False
    sortie = regle.params.att_sortie.getval(obj)
    if not os.path.isabs(sortie) and not sortie.startswith("."):
        sortie = os.path.join(regle.getvar("_sortie", "."), sortie)
    if not zipfile.is_zipfile(name):
        return False
    with zipfile.ZipFile(name, "r") as archive:
        if regle.params.cmp2.val == "all":
            archive.extractall(path=sortie)
            return True
        files = regle.getlist_entree(obj)
        archive.extractall(path=sortie, members=files)
        return True
