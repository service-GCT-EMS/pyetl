# -*- coding: utf-8 -*-
"""

@author: 89965
fonctions s de selections : determine si une regle est eligible ou pas
"""
import os
import sys
import re
import glob
import zipfile
import gzip
import time
import logging
import hashlib


def listefichs(regle, nom):
    """gere la compression"""
    racine = regle.params.cmp2.val
    stock = dict()
    mode = 0
    if regle.params.att_entree.val:
        fich = os.path.join(racine, nom)
        if fich:
            stock[fich] = fich
            mode = "a"
    else:
        mode = "w"
        regle.stock_param.logger.info(
            "archive : ecriture zip:" + (racine + ":")
            if racine
            else "" + ",".join(regle.params.val_entree.liste) + " -> " + dest
        )
        for f_1 in regle.params.val_entree.liste:
            clefs = []
            f_interm = os.path.join(racine, f_1)
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


def h_archive(regle):
    """definit la regle comme declenchable"""
    racine = regle.params.cmp2.val
    dest = os.path.join(racine, regle.params.cmp1.val + ".zip")
    if regle.params.pattern == "2" or regle.params.pattern == "2b":
        mode = "w"
        regle.stock_param.logger.info(
            "archive : ecriture zip:" + (racine + ":")
            if racine
            else "" + ",".join(regle.params.val_entree.liste) + " -> " + dest
        )
        stock = dict()
        for f_1 in regle.params.val_entree.liste:
            clefs = []
            f_interm = os.path.join(racine, f_1)
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
        regle.valide = "done"
    else:
        if os.path.isfile(dest):
            if regle.istrue("ajout_zip"):
                pass
            else:
                os.remove(dest)
        regle.chargeur = True


def f_archive(regle, obj):
    """#aide||zippe les fichiers ou les repertoires de sortie
    #parametres||liste de noms de fichiers(avec \*...);attribut contenant le nom;;nom du fichier zip
      #pattern1||;?C;A;archive;C;?C
      #pattern1b||;?C;A;zip;C;?C
      #pattern2||;C;;archive;C;?C
      #pattern2b||;C;;zip;C;?C
         #test||notest
    """
    #    if not obj.virtuel:
    #        return False
    racine = regle.params.cmp2.val
    dest = os.path.join(racine, regle.params.cmp1.val + ".zip")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(
        "archive",
        time.ctime(),
        regle.entree,
        dest,
        regle.getvar("_sortie"),
    )
    fich = os.path.join(racine, regle.entree)
    mode = "a"

    with zipfile.ZipFile(dest, compression=zipfile.ZIP_BZIP2, mode=mode) as file:
        file.write(i, arcname=fich)
    print("fin_archive", dest, time.ctime())
    regle.stock_param.logger.info("fin_archive " + dest)
    return True


def f_zipdir(regle, obj):
    """#aide||liste les fichiers d un zip
    #parametres||attribut de sortie;nom du fichier;attribut contenant le nom;;
    #aide_spec1||cree la liste de contenus dans l'attribut de sortie
      #pattern1||?A;?C;?A;zipdir;
    #aide_spec2||cree un objet par element du fichier zip
      #pattern2||?A;?C;?A;zipdir;=split;
          #test||notest
    """
    name = regle.entree
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
    #parametres||destination;fichier a extraire;attribut contenant le nom;zipextract;nom du zip;
     #pattern1||?C;?C;?A;zipextract;C;?=all
         #test||notest
    """

    name = regle.params.cmp1.val
    # print("preparation zipextract", name)
    if not os.path.isabs(name) and not name.startswith("."):
        name = os.path.join(regle.getvar("_entree", "."), name)

    namelist = glob.glob(name) if "*" in name else [name]
    found = False
    sortie = regle.params.att_sortie.val
    if not os.path.isabs(sortie) and not sortie.startswith("."):
        sortie = os.path.join(regle.getvar("_sortie", "."), sortie)
    for name in namelist:
        if not zipfile.is_zipfile(name):
            regle.stock_param.logger.warning(
                "le fichier %s n est pas un fichier zip", name
            )
            regle.stock_param.logger.info("tentative d'extreaction en gzip")
            destfich = os.path.splitext(os.path.basename(name))[0]
            dest = os.path.join(sortie, destfich)
            try:
                with gzip.open(name) as archive:
                    with open(dest, "wb") as f:
                        f.write(archive.read())
                found = True
            except:
                raise
        else:
            found = True

            # print("zipextract", name, regle.params.cmp2.val, "vers", sortie)

            with zipfile.ZipFile(name, "r") as archive:
                if regle.params.cmp2.val == "all":
                    archive.extractall(path=sortie)
                else:
                    files = regle.getlist_entree(obj)
                    archive.extractall(path=sortie, members=files)
    return found


def get_checksum(regle, name, write=False):
    """calcul checksum"""
    if not os.path.isabs(name) and not name.startswith("."):
        name = os.path.join(regle.getvar("_entree", "."), name)
    hash = hashlib.md5()
    print("md5: ouverture ", name)
    file = open(name, "br")
    while i := file.read(1048576):
        hash.update(i)
    checksum = hash.hexdigest()
    if write:
        sortie = os.path.splitext(name)[0] + ".md5"
        open(sortie, "w").write(checksum)
    return checksum


def verify_checksum(regle, name, checksum):
    """compare une checksum"""
    calcul = get_checksum(regle, name)
    return calcul == checksum


def h_checksum(regle):
    """calcule le hash d un fichier"""
    regle.result = regle.params.att_sortie.val
    if regle.params.pattern == "2":
        name = regle.params.val_entree.val
        result = regle.params.att_sortie.val
        cksum = get_checksum(regle, name, write=not result)
        if result:
            regle.setvar(result, cksum)
        regle.valide = "done"


def f_checksum(regle, obj):
    """#aide||cree un hash md5 ou sha64
    #parametres||destination;fichier a extraire;attribut contenant le nom;zipextract;nom du zip;
     #pattern1||?A;?C;A;checksum;=md5;
     #pattern2||?P;C;;checksum;=md5;
         #test||notest
    """
    name = regle.entree
    cksum = get_checksum(regle, name, write=not regle.result)
    if regle.result:
        regle.seval_sortie(obj, cksum)
    return True
