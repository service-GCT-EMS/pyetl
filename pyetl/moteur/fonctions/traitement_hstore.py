# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de manipulation d'attributs

# description des patterns pour les attributs :
# chaque pattern cmprend 5 champs sous la forme:
# C1,C2,C3,C4,C5,C6
# C1) sortie A : attribut
#           L : liste
#           [A] : indirect
#           =nom : nom impose
# modifieurs +  : composition autorisee
#            ?  : facultatif
#
# C2 defaut  C : chaine caractere
#           [A] : indirect
#            N : numerique
# C3 entree  A: attribut
#           L liste
#          / obligatoire si pas defaut
#          :NC expression de calcul
# C4 commande
# C5 parametre 1
# C6 parametre 2
#
# description des tests:
#

"""
# from pyetl.formats.formats import Stat
import re


## ===================================== hstore ===============================

# ============================= creation d un hstore =========================


def f_hset1(regle, obj):
    """#aide||transforme des attributs en hstore
    #aide_spec||liste d attributs en entree
    #pattern||A;?;L;hset;;
    #schema||ajout_attribut
    #test||obj||^X;;C1,C2;hset;||^Z;;X;hget;C1;||atv;Z;AB
    """
    #    print("hcre! ", obj.ido, "->", regle.params.att_entree.liste)
    obj.attributs[regle.params.att_sortie.val] = ", ".join(
        [
            '"'
            + i
            + '" => "'
            + obj.attributs.get(i, regle.params.val_entree.val)
            .replace("\\", "\\\\")
            .replace('"', r"\"")
            + '"'
            for i in regle.params.att_entree.liste
        ]
    )
    #    print("creation hstore", regle.params.att_sortie.val,
    #          obj.attributs[regle.params.att_sortie.val])
    return True


def h_hset2(regle):
    """compile les expression pour les champs"""
    #    print("compilation de la regex", regle.params.att_entree.val)
    regle.re1 = re.compile(regle.params.att_entree.val)


def f_hset2(regle, obj):
    """#aide||transforme des attributs en hstore
    #aide_spec||expression reguliere
    #pattern||A;?;re;hset;;
    #schema||ajout_attribut
    #test||obj||^X;;C*;hset;||^Z;;X;hget;C1;||atv;Z;AB
    """
    #    print("hcre2 ", obj.ido, "->", regle.params.att_entree.val)
    obj.attributs[regle.params.att_sortie.val] = ", ".join(
        [
            '"'
            + i
            + '" => "'
            + obj.attributs.get(i, regle.params.val_entree.val)
            .replace("\\", "\\\\")
            .replace('"', r"\"")
            + '"'
            for i in obj.attributs
            if not i.startswith("#") and regle.re1.search(i)
        ]
    )
    return True


def f_hset3(regle, obj):
    """#aide||transforme des attributs en hstore
    #aide_spec||tous les attributs visibles
    #pattern||A;;;hset;;
    #schema||ajout_attribut
    #test||obj||^X;;;hset;||^Z;;X;hget;C1;||atv;Z;AB
    """
    obj.attributs[regle.params.att_sortie.val] = ", ".join(
        [
            '"'
            + i
            + '" => "'
            + obj.attributs[i].replace("\\", "\\\\").replace('"', r"\"")
            + '"'
            for i in obj.attributs
            if not i.startswith("#")
        ]
    )
    #    print("hcre3 ", obj.ido, "->", obj.attributs[regle.params.att_sortie.val])
    return True


def f_hset4(regle, obj):
    """#aide||transforme des attributs en hstore
    #aide_spec||tous les attributs visibles passe les noma en minuscule
    #pattern||A;;;hset;=lower;
    #schema||ajout_attribut
    #test||obj||^X;;;hset;||^Z;;X;hget;C1;||atv;Z;AB
    """
    obj.attributs[regle.params.att_sortie.val] = ", ".join(
        [
            '"'
            + i.lower()
            + '" => "'
            + obj.attributs[i].replace("\\", "\\\\").replace('"', r"\"")
            + '"'
            for i in obj.attributs
            if not i.startswith("#")
        ]
    )
    #    print("hcre3 ", obj.ido, "->", obj.attributs[regle.params.att_sortie.val])
    return True


def f_hset5(regle, obj):
    """#aide||transforme des attributs en hstore
    #aide_spec||tous les attributs visibles passe les noma en majuscule
    #pattern||A;;;hset;=upper;
    #schema||ajout_attribut
    #test||obj||^X;;;hset;||^Z;;X;hget;C1;||atv;Z;AB
    """
    obj.attributs[regle.params.att_sortie.val] = ", ".join(
        [
            '"'
            + i.upper()
            + '" => "'
            + obj.attributs[i].replace("\\", "\\\\").replace('"', r"\"")
            + '"'
            for i in obj.attributs
            if not i.startswith("#")
        ]
    )
    #    print("hcre3 ", obj.ido, "->", obj.attributs[regle.params.att_sortie.val])
    return True


def f_hget1(regle, obj):
    """#aide||eclatement d un hstore
    #aide_spec||destination;defaut;hstore;hget;clef;
    #pattern||S;?;A;hget;A;
    #schema||ajout_attribut
    #test||obj||^X;;;hset||^Z;;X;hget;C1;||atv;Z;AB
    """
    if regle.params.att_entree.val not in obj.attributs:
        regle.setval_sortie(obj, regle.params.val_entree.val)
    try:
        hdic = obj.gethdict(regle.params.att_entree.val)
    #        print("recupere hdict ", hdict)
    except ValueError:
        return False
    regle.setval_sortie(
        obj, hdic.get(regle.params.cmp1.val, regle.params.val_entree.val)
    )
    return True


def f_hget2(regle, obj):
    """#aide||eclatement d un hstore
    #aide_spec||destination;defaut;hstore;hget;liste clefs;
    #pattern||M;?;A;hget;L;
    #schema||ajout_attribut
    #test||obj||^X;;;hset||^Z1,Z2;;X;hget;C1,C2;||atv;Z2;BCD
    """
    if regle.params.att_entree.val not in obj.attributs:
        regle.setval_sortie(
            obj, [regle.params.val_entree.val for i in regle.params.att_entree.liste]
        )
    try:
        hdic = obj.gethdict(regle.params.att_entree.val)
    except ValueError:
        return False
    regle.setval_sortie(
        obj, [hdic.get(i, regle.params.val_entree.val) for i in regle.params.cmp1.liste]
    )
    return True


def f_hget3(regle, obj):
    """#aide||eclatement d un hstore
    #aide_spec||destination;defaut;clef;hget;hstore;
    #pattern||D;?;A;hget;?L;
    #test||obj||^X;;;hset||^Z_*;;X;hget;;||atv;Z_C2;BCD
    #schema||ajout_attribut
    """
    if regle.params.att_entree.val not in obj.attributs:
        return False
    try:
        hdic = obj.gethdict(regle.params.att_entree.val)
    except ValueError:
        return False
    regle.setval_sortie(obj, hdic)
    return True


def f_hsplit(regle, obj):
    """#aide||decoupage d'un attribut hstore
    #parametres||
    #pattern||M;?;A;hsplit;?L
     #schema||ajout_attribut
       #test1||obj||^X;;;hset||^k,v;;X;hsplit>;C1,C2,C3;||cnt;3
    """
    try:
        hdic = obj.gethdict(regle.params.att_entree.val)
    except ValueError:
        return False
    klist = regle.params.cmp1.liste or hdic.keys()
    nom_clef, nom_val = regle.params.att_sortie.liste
    for k in klist:
        if k in hdic:
            val = hdic[k]
        else:
            continue
        obj2 = obj.dupplique()
        obj2.attributs[nom_clef] = k
        obj2.attributs[nom_val] = val
        # regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
        regle.branchements.brch["gen"].traite_push.send(obj2)
    return True


def f_hdel(regle, obj):
    """#aide||supprime une valeur d un hstore
    #pattern||A;;A;hdel;L;?
    #test||obj||^X;;;hset||^X;;X;hdel;C2;||^Z_*;;X;hget;;||atne;Z_C2;
    """
    hdic = obj.gethdict(regle.params.att_entree.val)
    for i in regle.params.cmp1.liste:
        try:
            del hdic[i]
        except KeyError:
            pass
    obj.sethtext(regle.params.att_entree.val)
    return True
