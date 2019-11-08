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
import io
import re
import time
#import itertools
import requests

# import pycurl
from .outils import compilefonc, charge_mapping


def f_setliste(regle, obj):
    """#aide||affectation d'un ensemble d'attributs
       #aide_spec||remplacement d'une liste de valeurs d'attribut avec defaut
       #parametres||liste de sortie;liste de defauts;liste d'entree
       #pattern||M;?LC;?L;set;;||sortie
       #test1||obj||^V4,V5;;C1,C2;set||atv;V4;AB
       #test2||obj||^V4,V5;;C1,C2;set||atv;V5;BCD
    """
    #    print ("dans setliste", regle.ligne,regle.params.att_sortie, regle.params.att_entree)
    regle.setval_sortie(obj, regle.getlist_entree(obj))
    return True

def f_setmatch_liste(regle, obj):
    """#aide||affectation d un attribut
       #aide_spec||remplacement d'une valeur d'attribut par les valeurs retenues dans la selection
       ||par expression regulieres (recupere les groupes de selections)
       #pattern||M;;;set;=match;||sortie
    #parametres||liste de sortie
       #test1||obj||^X;BCD;;set;||X;re:(.)C(.);;;V4,V5;;;set;match||atv;V4;B
       #test1||obj||^X;BCD;;set;||X;re:(.)C(.);;;V4,V5;;;set;match||atv;V5;D
    """
    # print ('regle.match',regle.match )
    regle.setval_sortie(obj, regle.matchlist)
    return True

def h_setval(regle):
    """helper de fonctiond'entree"""
    if not regle.params.att_entree.val:
        regle.get_entree = regle.get_defaut

def f_setval(regle, obj):
    """#aide||affectation d un attribut
       #aide_spec||remplacement d'une valeur d'attribut avec defaut
       #pattern||S;?;?A;set;;||sortie
    #parametres||attribut de sortie;defaut;attribut d'entree
       #test1||obj||^V4;;C1;set||atv;V4;AB
       #test2||obj||^V4;1;X;set||atv;V4;1
    """
    regle.setval_sortie(obj, regle.get_entree(obj))
    return True

def f_setmatch(regle, obj):
    """#aide||affectation d un attribut
       #aide_spec||remplacement d'une valeur d'attribut par les valeurs retenues dans la selection
       ||par expression regulieres (recupere toute la selection)
       #pattern||S;;;set;=match;||sortie
    #parametres||attribut de sortie
       #test1||obj||^X;BCDXX;;set;||X;re:(.)C(.);;;V4;;;set;match||atv;V4;BCD
    """
    regle.setval_sortie(obj, regle.match)
    return True


def h_setschema(regle):
    """helper : positionne le nocase"""
    regle.changeschema = True
    if regle.params.cmp1.val:
        regle.context.setvar("schema_nocase", regle.params.cmp1.val)


def f_setschema(regle, obj):
    """#aide||affectation d un schema en adaptant la casse des attributs du schema a l'objet
  #aide_spec||change le schema de reference d'un objet
 #parametres||#schema (mot clef);valeur par defaut;attribut d'entree;;
     #helper||setval
   #pattern1||=#schema;?;?A;set;?=maj;||sortie
 #aide_spec1||passe en majuscule
   #pattern2||=#schema;?;?A;set;?=min;||sortie
 #aide_spec2||passe en minuscule

    """
    obj.attributs["#schema"] = regle.get_entree(obj)
    return True


def f_setgeom(regle, obj):
    """#aide||affectation d un attribut
  #aide_spec||cree une geometrie texte
     #helper||setval
    #pattern||=#geom;?;?A;set;C;N||sortie
 #parametres||#geom (mot clef);valeur par defaut;attribut d'entree;;format;dimension
      #test1||obj||^#geom;1SEC 1,2,|1,0,|0,0,1,0;;set;asc;2;
            ||^;;;geom||atv;#type_geom;2
      #test2||obj||^#gg;1SEC 1,2,|1,0,|0,0,1,0;;set||^#geom;;#gg;set;asc;2;\
            ||^;;;geom||atv;#type_geom;2
    """
    geom = regle.get_entree(obj)
    # print ("recup geom:",geom)
    obj.attributs["#geom"] = geom.split("|")
    obj.format_natif = regle.params.cmp1.val
    obj.geompending(dimension=regle.params.cmp2.num if regle.params.cmp2.num else 2)
    converter = regle.stock_param.get_converter(obj.format_natif)
    if converter:
        obj.attributs_geom = converter
    return True


def h_setnonvide(regle):
    """ pour repl_c il faut mettre en forme la liste """
    regle.params.att_entree.liste.pop()  # on vide la liste pour la recreer
    regle.params.att_entree.liste.extend(regle.params.att_entree.val.split("|"))


def f_setnonvide(regle, obj):
    """#aide||remplacement d une valeur
        #aide_spec||remplacement d'une valeur d'attribut par le premier non vide  avec defaut
        #pattern||S;?;|L;set;;||entree
        #test3||obj||^V4;1;A|C1|C2;set||atv;V4;AB
        #test4||obj||^V4;1;A|B;set||atv;V4;1
    """
    regle.fstore(
        regle.params.att_sortie,
        obj,
        next(
            (obj.attributs.get(i) for i in regle.params.att_entree.liste if obj.attributs.get(i)),
            regle.params.val_entree.val,
        ),
    )
    return True


def h_sub(regle):
    """helper pour sub : compile les expressions regulieres"""
    try:
        regle.exp_entree = re.compile(regle.params.cmp1.val)  # expression sur l'attribut d'entree
    except re.error as err:
        print("expression reguliere invalide", regle.params.cmp1.val, err)
        regle.valide = False
        regle.erreurs.append("erreur compilation des expressions" + repr(err))
        return
    regle.exp_sortie = regle.params.cmp2.val

    if regle.params.cmp2.val.startswith("f:"):
        if '__' in regle.params.cmp2.val:
            raise SyntaxError('fonction non autorisee:'+regle.params.cmp2.val)
        try:
            regle.exp_sortie = eval("lambda " + regle.params.cmp2.val,{})
            regle.valide = True
        except SyntaxError as err:
            regle.valide = False
            regle.erreurs.append("erreur compilation des expressions" + err.msg)


# fonctions de traitement alpha
def f_sub(regle, obj):  # fonction de substution
    """#aide||remplacement d une valeur
        #aide_spec||application d'une fonction de transformation par expression reguliere
        #pattern||S;?;A;sub;re;?re||sortie
        #test1||obj||^V4;;C1;sub;A;B;||atv;V4;BB
        #test2||obj||^V4;;C1;sub;.*;f:f.group(0).lower();||atv;V4;ab
    """
    # substitution
    regle.setval_sortie(obj, regle.exp_entree.sub(regle.exp_sortie, regle.getval_entree(obj)))
    return True


def h_setcalc(regle):
    """ preparation de l'expression du calculateur de champs"""
    #    print ('dans hcalc',regle.params)
    try:
        regle.calcul = compilefonc(regle.params.att_entree.val, "obj")
    except SyntaxError:
        print("erreur sur l'expression de calcul->" + regle.params.att_entree.val + "<-")
        compilefonc(regle.params.att_entree.val, "obj", debug=True)
        regle.valide = False


def f_setcalc(regle, obj):
    """#aide||remplacement d une valeur
        #aide_spec||fonction de calcul libre (attention injection de code)
        || les attributs doivent etre précédes de N: pour un traitement numerique
        || ou C: pour un traitement alpha
        #pattern||S;;NC:;set;;
        #test1||obj||^V4;;N:V1+1;set||atn;V4;13
    """
    regle.setval_sortie(obj, str(regle.calcul(obj)))
    return True


def h_setself(regle):
    """helper generique permettant de gerer les cas ou entree = sortie"""
    #    print("helper self",regle)
    regle.selset = set(regle.params.att_ref.liste)
#    print ('selset',regle.selset)


def f_upper(regle, obj):
    """#aide||remplacement d une valeur
        #aide_spec||remplacement d'une valeur d'attribut avec defaut passage en majuscule
        #pattern||S;?;A;upper;;
        #test1||obj||^V4;a;;set||^V4;;V4;upper||atv;V4;A

    """
    regle.setval_sortie(obj, regle.getval_entree(obj).upper())
    return True


def f_upper2(regle, obj):
    """#aide||remplacement d une valeur
        #aide_spec||passage en majuscule d'un attribut ( avec defaut eventuel)
        #pattern||A;?;;upper||sortie||50
        #pattern2||;?;A;upper||sortie||50
        #schema||ajout_attribut
        #helper||setself
        #test2||obj||^V4;a;;set||^V4;;;upper||atv;V4;A
        #test3||obj||^V4;a;;set||^;;V4;upper||atv;V4;A
    """
    obj.attributs[regle.params.att_ref.val] = regle.getval_ref(obj).upper()
    return True


def f_upper_liste(regle, obj):
    """#aide||passage en majuscule d'une liste de valeurs
        #aide_spec||remplacement d'une valeur d'attribut avec defaut passage en minuscule
        #pattern||M;?;L;upper;;||sortie
        #test1||obj||^V4,V5;a,b;;set||^V4,V5;;V4,V5;upper||atv;V5;B
        #test2||obj||^V4,V5;a,b;;set||^V4,V5;;V4,V5;upper||atv;V4;A
    """
    #    regle.fstore(regle.params.att_sortie, obj,
    #                 [obj.attributs.get(i, regle.params.val_entree.val).upper()
    #                  for i in regle.params.att_entree.liste])
    #    regle.setval_sortie(obj, regle.getlist_entree(obj).upper())
    regle.process_liste(obj, str.upper)
    return True


def f_upper_liste2(regle, obj):
    """#aide||passage en majuscule d'une lister de valeurs
        #aide_spec||passage en majuscule d une liste d'attribut avec defaut
        #pattern1||L;?;;upper;;||sortie||99
        #pattern2||;?;L;upper;;||sortie||99
        #helper||setself
        #schema||ajout_attribut
        #test1||obj||^V4,V5;a,b;;set||^;;V4,V5;upper||atv;V5;B
        #test2||obj||^V4,V5;a,b;;set||^V4,V5;;;upper||atv;V4;A
    """
    #    for i, j in zip(regle.params.att_ref.liste, regle.params.val_entree.liste):
    #        obj.attributs[i] = obj.attributs.get(i, j).upper()
    #    regle.process_list_inplace(obj, str.upper)
    obj.attributs.update(zip(regle.params.att_ref.liste, map(str.upper, regle.getlist_ref(obj))))
    return True


def f_lower(regle, obj):
    """#aide|| passage en minuscule
        #aide_spec||remplacement d'une valeur d'attribut avec defaut passage en minuscule
        #pattern||S;?;A;lower;;||sortie
        #test1||obj||^V4;A;;set||^V4;;V4;lower||atv;V4;a

    """
    #    regle.fstore(regle.params.att_sortie, obj,
    #                 obj.attributs.get(regle.params.att_entree.val,
    #                                   regle.params.val_entree.val).lower())
    regle.setval_sortie(obj, regle.getval_entree(obj).lower())
    return True


def f_lower2(regle, obj):
    """#aide|| passage en minuscule
        #aide_spec||remplacement d'une valeur d'attribut avec defaut passage en majuscule
        #patternC||A;?;;lower;;
        #pattern||A;?;;lower;;
        #pattern2||;?;A;lower;;
        #helper||setself
        #test2||obj||^V4;A;;set||^V4;;;lower||atv;V4;a
        #test3||obj||^V4;A;;set||^;;V4;lower||atv;V4;a
    """
    obj.attributs[regle.params.att_ref.val] = regle.getval_ref(obj).lower()
    return True


def f_lower_liste(regle, obj):
    """#aide||passage en minuscule d'une lister de valeurs
        #aide_spec||remplacement d'une valeur d'attribut avec defaut passage en minuscule
        #pattern||M;?;L;lower;;||sortie
        #schema||ajout_attribut
        #testl1||obj||^V4,V5;A,B;;set||^V4,V5;;V4,V5;lower||atv;V5;b
        #testl2||obj||^V4,V5;A,B;;set||^V4,V5;;V4,V5;lower||atv;V4;a

    """
    regle.process_liste(obj, str.lower)
    return True


def f_lower_liste2(regle, obj):
    """#aide||passage en minuscule d'une lister de valeurs
        #aide_spec||passage enmajuscule d une liste d'attribut avec defaut
         #pattern1||L;?;;lower;;||sortie
        #patternC1||L;?;;lower;;||sortie
         #pattern2||;?;L;lower;;||sortie
           #helper||setself
           #schema||ajout_attribut
            #test1||obj||^V4,V5;A,B;;set||^;;V4,V5;lower||atv;V5;b
            #test2||obj||^V4,V5;A,B;;set||^V4,V5;;;lower||atv;V4;a
    """
    obj.attributs.update(zip(regle.params.att_ref.liste, map(str.lower, regle.getlist_ref(obj))))
    return True


def h_asplit(regle):
    """ preparation decoupage attributs"""
    f_debut = None
    f_fin = None
    tmp = []
    nbres = len(regle.params.att_sortie.liste) - 1
    regle.multi = nbres == -1
    if nbres == 0:
        nbres = 1
    sep = regle.params.cmp1.val
    if regle.params.cmp1.val == "\\s":
        sep = ";"
    if regle.elements["cmp2"].group(0):
        tmp = regle.elements["cmp2"].group(0).split(":")
        f_debut = tmp[0]
    if tmp and len(tmp) > 1:
        f_fin = tmp[1]
    regle.defcible = slice(int(f_debut) if f_debut else None, int(f_fin) if f_fin else None)
    nbdecoup = nbres + (int(f_debut) if f_debut else 0)
    #    print ('cible decoupage',regle.defcible, nbdecoup,regle.params.att_sortie.liste, regle.multi)
    regle.sep = sep
    regle.nbdecoup = nbdecoup


def f_asplit(regle, obj):
    """#aide||decoupage d'un attribut en fonction d'un separateur
    #aide_spec||s'il n'y a pas d'attributs de sortie on cree un objet pour chaque element
       #pattern||M;?;A;split;.;?N:N||sortie
       #pattern2||;?;A;split;.;?N:N||sortie
       #test1||obj||^V4;a:b:cc:d;;set||^r1,r2,r3,r4;;V4;split;:;||atv;r3;cc
       #test2||obj||^V4;a:b:c:d;;set||^;;V4;split;:;||cnt;4
       """
    if regle.multi:
        #        elems = obj.attributs.get(regle.params.att_entree.val,
        #                                   regle.params.val_entree.val).split(regle.sep)[regle.defcible]
        elems = regle.getval_entree(obj).split(regle.sep)[regle.defcible]
        obj.attributs[regle.params.att_entree.val] = elems[0]
        for i in elems[1:]:
            obj2 = obj.dupplique()
            obj2.attributs[regle.params.att_entree.val] = i
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["next"])

    else:
        #        regle.fstore(regle.params.att_sortie, obj,
        #                     obj.attributs.get(regle.params.att_entree.val,
        #                                       regle.params.val_entree.val).split
        #                     (regle.sep, regle.nbdecoup)[regle.defcible])
        regle.setval_sortie(
            obj, regle.getval_entree(obj).split(regle.sep, regle.nbdecoup)[regle.defcible]
        )
    return True


def f_strip(regle, obj):
    """#aide||supprime des caracteres aux extremites
       #pattern||S;?;A;strip;?C;||sortie
       #test||obj||^V4;abbcaa;;set||^r1;;V4;strip;a||atv;r1;bbc
    """
    #    print("strip",regle.getval_entree(obj),regle.getval_entree(obj).strip(regle.params.cmp1.val))
    if regle.params.cmp1.val:
        regle.setval_sortie(obj, regle.getval_entree(obj).strip(regle.params.cmp1.val))
    else:
        regle.setval_sortie(obj, regle.getval_entree(obj).strip())
    return True


def f_strip2(regle, obj):
    """#aide||supprime des caracteres aux estremites
     #helper||setself
    #pattern||;?;A;strip;?C;||sortie
    #pattern2||A;?;;strip;?C;||entree
    #test||obj||^V4;abbaa;;set||^;;V4;strip;a;||atv;V4;bb
    #test2||obj||^V4;abbaa;;set||^V4;;;strip;a;||atv;V4;bb
    """
    if regle.params.cmp1.val:
        obj.attributs[regle.params.att_ref.val] = regle.getval_ref(obj).strip(regle.params.cmp1.val)
    else:
        obj.attributs[regle.params.att_ref.val] = regle.getval_ref(obj).strip()
    return True


def f_len(regle, obj):
    """#aide||calcule la longueur d un attribut
    #pattern||S;?;A;len;;
    #test||obj||^X;toto;;set;||^Y;;X;len;;||atv;Y;4
    """
    regle.setval_sortie(obj, str(len(regle.getval_entree(obj))))
    return True


def f_crypt(regle, obj):
    """#aide||crypte des valeurs dans un fichier en utilisant une clef
    #pattern||A;?;A;crypt;C?;
    #schema||ajout_attribut
    #test||obj||^X;toto;;set;||^Y;;X;crypt;ffff;||^Z;;Y;decrypt;ffff||atv;Z;toto
    """
    crypte = regle.stock_param.crypter(regle.getval_entree(obj), regle.params.cmp1.getval(obj))
    obj.attributs[regle.params.att_sortie.val] = crypte
    return True


def f_decrypt(regle, obj):
    """#aide||crypte des valeurs dans un fichier en utilisant une clef
    #pattern||A;?;A;decrypt;C?;
    #schema||ajout_attribut
    #test||obj||^X;toto;;set;||^Y;;X;crypt;ffff;||^Z;;Y;decrypt;ffff||atv;Z;toto

    """
    clef = regle.params.cmp1.getval(obj)
    val = regle.getval_entree(obj)

    decrypte = regle.stock_param.decrypt(val, clef)
    obj.attributs[regle.params.att_sortie.val] = decrypte if decrypte else val
    return True


def f_vset(regle, obj):
    """#aide||remplacement d une valeur
        #aide_spec||positionne une variable globale
        #pattern||P;?;?A;set;;||sortie
        #test1||obj||^P:AA;1;;set||ptv;AA;1
    """
    valeur = obj.attributs.get(regle.params.att_entree.val) or regle.params.val_entree.val
    #    print ('dans vset',regle.params.att_sortie.val,valeur)
    if valeur != regle.getvar(regle.params.att_sortie.val):
        regle.setvar(regle.params.att_sortie.val, valeur)
        for i in regle.stock_param.bindings.get(regle.params.att_sortie.val, ()):
            print("reinterpretation regle", i)
            regle.stock_param.reconfig(regle.stock_param.regles[i], regle.stock_param)
        # print ('stocke ', regle.params.att_sortie.val,
            #    regle.getvar(regle.params.att_sortie.val), regle.context.ref, regle.context)
    return True


def f_renamelist(regle, obj):  # fonction de substution
    """#aide||renommage d'un attribut
       #pattern||L;;L;ren;;||sortie
       #schema||rename_attribut
       #test1||obj||^V4,V5;;C1,C2;ren||atv;V4;AB
    """
    ok=True
    for dest, orig in zip(regle.params.att_sortie.liste, regle.params.att_entree.liste):
        if dest in obj.attributs:
            ok=False
        elif orig in obj.attributs:
            obj.attributs[dest] = obj.attributs[orig]
            del obj.attributs[orig]
    return ok


def f_rename(regle, obj):  # fonction de substution
    """#aide||renommage d'un attribut
       #pattern||A;;A;ren;;||sortie
       #schema||rename_attribut
       #test1||obj||^V4;;C1;ren||atv;V4;AB
    """
    if regle.params.att_sortie.val in obj.attributs:
        return False  # on ecrase pas d'attribut
    if regle.params.att_entree.val in obj.attributs:
        obj.attributs[regle.params.att_sortie.val] = obj.attributs[regle.params.att_entree.val]
        del obj.attributs[regle.params.att_entree.val]
        return True
    return False  # l attribut n' existe pas on ne fait rien


def _suppatt(obj, nom):
    """ #aide||suppression d'un element """
    del obj.attributs[nom]  # suppression d'attribut
    if obj.text_graph and nom in obj.text_graph:
        del obj.text_graph[nom]
    if obj.etats and nom in obj.etats:
        del obj.etats[nom]
    if obj.hdict and nom in obj.hdict:
        del obj.hdict[nom]
    return True


def f_suppl(regle, obj):
    """#aide||suppression d'elements
       #aide_spec||liste d'attributs
       #pattern||;;L;supp;;||entree
       #pattern2||L;;;supp;;||sortie
       #schema||supprime_attribut
       #test1||obj||^;;C1,C2,C3;supp||atne;C2
       #test2||obj||^C1,C2,C3;;;supp||atne;C2
    """
    #    print ("=========================dans supatt")

    for i in regle.params.att_entree.liste or regle.params.att_sortie.liste:
        if i in obj.attributs:
            _suppatt(obj, i)
    #    print ("=========================fin supatt",regle.ligne)
    return True


def f_suppg(_, obj):
    """#aide||suppression d'elements
       #aide_spec||geometrie
       #pattern||;;=#geom;supp;;||entree
       #pattern2||=#geom;;;supp;;||sortie
       #schema||set_geom
       #testg1||obj;point||^;;#geom;supp||atv;#type_geom;0
       #testg2||obj;point||^#geom;;;supp||atv;#type_geom;0
    """
    #    print ('suppg',obj)
    obj.setnogeom()
    return True


def f_suppschema(_, obj):
    """#aide||suppression d'elements
       #aide_spec||geometrie
       #pattern||;;=#schema;supp;;||entree
       #pattern2||=#schema;;;supp;;||sortie
       #schema||
       #tests1||obj||^;;#schema;supp||;!has:schema;;;V4;1;;set||atv;V4;1
       #tests2||obj||^#schema;;;supp||;!has:schema;;;V4;1;;set||atv;V4;1
    """
    obj.resetschema()
    return True


def h_suppobj(regle):
    """evite la transmission d'un objet"""
    regle.final = True
    regle.supobj = True


def f_suppobj(_, __):
    """#aide||suppression d'elements
       #aide_spec||objet
       #pattern||;;;supp;;
       #test3||obj;;2||V0;1;;;;;;supp||#classe;;;;nb;;C1;stat;cnt||anstat;atv:nb:1;

    """
    return True


def f_keep2(regle, obj):
    """#aide||suppression de tous les attributs sauf ceux de la liste
       #pattern||;;L;garder;;
       #pattern2||L;;;garder;;
       #schema||garder_attributs
       #helper||setself
       #test||obj||^;;C1;garder||^X;2;C2;set||atv;X;2
       #test2||obj||^C1;;;garder||^X;2;C2;set||atv;X;2
    """
    asupprimer = [i for i in obj.attributs if not i.startswith("#") and i not in regle.selset]
    #    agarder = [i for i in obj.attributs if i[0] != '#' and i in regle.params.att_entree.liste ]
    #    print ('garder sauf ' , asupprimer)
    regle.asupprimer = asupprimer
    for nom in asupprimer:
        _suppatt(obj, nom)


    return True


def f_keep(regle, obj):
    """#aide||suppression de tous les attributs sauf ceux de la liste
       #pattern||L;?C;?L;garder;;
       #schema||garder_attributs
       #helper||setself
       #test||obj||^C1;;;garder||^X;2;C2;set||atv;X;2
    """
    if regle.params.att_entree.liste:  # on renomme les attributs
        for source, dest, defaut in zip(
            regle.params.att_entree.liste,
            regle.params.att_sortie.liste,
            regle.params.val_entree.liste,
        ):
            obj.attributs[dest] = obj.attributs.get(source, defaut)
    else:
        for dest, defaut in zip(regle.params.att_sortie.liste, regle.params.val_entree.liste):
            if dest not in obj.attributs:
                obj.attributs[dest] = defaut

    return f_keep2(regle, obj)


## ===================================== hstore ===============================

# ============================= creation d un hstore =========================


def f_hset1(regle, obj):
    """ #aide||transforme des attributs en hstore
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
    """ #aide||transforme des attributs en hstore
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
    """ #aide||transforme des attributs en hstore
    #aide_spec||tous les attributs visibles
    #pattern||A;;;hset;;
    #schema||ajout_attribut
    #test||obj||^X;;;hset;||^Z;;X;hget;C1;||atv;Z;AB
    """
    obj.attributs[regle.params.att_sortie.val] = ", ".join(
        [
            '"' + i + '" => "' + obj.attributs[i].replace("\\", "\\\\").replace('"', r"\"") + '"'
            for i in obj.attributs
            if not i.startswith("#")
        ]
    )
    #    print("hcre3 ", obj.ido, "->", obj.attributs[regle.params.att_sortie.val])
    return True


def f_hset4(regle, obj):
    """ #aide||transforme des attributs en hstore
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
    """ #aide||transforme des attributs en hstore
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
    """ #aide||eclatement d un hstore
        #aide_spec||destination;defaut;hstore;hget;clef;
        #pattern||S;?;A;hget;A;
        #schema||ajout_attribut
        #test||obj||^X;;;hset||^Z;;X;hget;C1;||atv;Z;AB
    """
    if regle.params.att_entree.val not in obj.attributs:
        regle.fstore(regle.params.att_sortie, obj, regle.params.val_entree.val)
    try:
        hdic = obj.gethdict(regle.params.att_entree.val)
    #        print("recupere hdict ", hdict)
    except ValueError:
        return False
    regle.fstore(
        regle.params.att_sortie, obj, hdic.get(regle.params.cmp1.val, regle.params.val_entree.val)
    )
    return True


def f_hget2(regle, obj):
    """ #aide||eclatement d un hstore
        #aide_spec||destination;defaut;hstore;hget;liste clefs;
        #pattern||M;?;A;hget;L;
        #schema||ajout_attribut
        #test||obj||^X;;;hset||^Z1,Z2;;X;hget;C1,C2;||atv;Z2;BCD
    """
    if regle.params.att_entree.val not in obj.attributs:
        regle.fstore(
            regle.params.att_sortie,
            obj,
            [regle.params.val_entree.val for i in regle.params.att_entree.liste],
        )
    try:
        hdic = obj.gethdict(regle.params.att_entree.val)
    except ValueError:
        return False
    regle.fstore(
        regle.params.att_sortie,
        obj,
        [hdic.get(i, regle.params.val_entree.val) for i in regle.params.cmp1.liste],
    )
    return True


def f_hget3(regle, obj):
    """ #aide||eclatement d un hstore
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
    regle.fstore(regle.params.att_sortie, obj, hdic)
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
        regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["next"])
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


def h_cnt(regle):
    """init compteur"""
    regle.orig = regle.params.cmp2.num if regle.params.cmp2.num else 0
    regle.pas = regle.params.cmp1.num if regle.params.cmp1.num else 1
    regle.local = not (regle.params.att_entree.val or regle.params.val_entree.val)
    return True


def f_cnt(regle, obj):
    """#aide||compteur
  #aide_spec||attribut de sortie;nom fixe ou;nom du compteur en attibut;cnt;pas;origine
 #aide_spec2||le comteur est global s'il a un nom, local s'il n'en a pas
    #pattern||S;?;?A;cnt;?N;?N
     #schema||ajout_attribut
      #test1||obj||^V4;t1;;cnt;3;4||atv;V4;4
      #test2||obj;;2||^V4;t1;;cnt;3;4||V4;4;;;;;;supp||atv;V4;7
    """
    if regle.local:
        obj.attributs[regle.params.att_sortie.val] = "%d" % (regle.orig)
        regle.orig += regle.pas
        return True
    nom = regle.getval_entree(obj)
    val = regle.stock_param.cntr.get(nom, regle.orig)
    obj.attributs[regle.params.att_sortie.val] = "%d" % (val)
    regle.stock_param.cntr[nom] = val + regle.pas
    #    print ('compteur',nom,val)
    return True


def h_join(regle):
    """preparation jointure"""
    regle.fichier = regle.params.cmp1.val  # nom du fichier
    definition_jointure = regle.params.cmp2.liste
    regle.clef = definition_jointure.index(regle.params.att_entree.val)
    regle.champ = definition_jointure.index(regle.params.att_sortie.val)
    regle.stock_param.jointdef[regle.fichier] = regle.clef
    regle.stock_param.joint_fich[regle.fichier] = ""
    if re.search(r"\[[CDF]\]", regle.fichier):
        regle.joint_statique = False
    else:
        #        regle.mode = "sjoin" # jointure statique)
        regle.joint_statique = True
        regle.stock_param.charge(
            regle.fichier, regle.fichier
        )  # on precharge le fichier de jointure
    #    print(" prechargement",regle.fichier)
    return True


def f_join(regle, obj):
    """#aide||jointures
    #pattern||A;?;?A;join;?C[];?C||cmp1
    #aide_spec||sur un fichier dans le repertoire des donnees
    #schema||ajout_attribut
    #test||obj||^X;C;;set||^val;;X;join;%testrep%/refdata/join.csv;X,nom,val||atv;val;3
    """
    obj.attributs[regle.params.att_sortie.val] = regle.stock_param.jointure(
        regle.fichier,
        obj.attributs.get("#repertoire", ""),
        obj.attributs.get(regle.params.att_entree.val, regle.params.val_entree.val),
        regle.champ,
    )
    return True


def f_sjoin(regle, obj):
    """#aide||jointures
    #aide_spec||jointure statique
    #pattern||A;?;A;join;?C;?C||cmp1
    #schema||ajout_attribut
    #helper||join
    #test||obj||^X;C;;set||^nom;;X;join;%testrep%/refdata/join.csv;X,nom,val||atv;nom;tata
    """
    #    print ('jointure ', obj.attributs.get(regle.params.att_entree.val,
    #           regle.params.val_entree.val), regle.champ)
    obj.attributs[regle.params.att_sortie.val] = regle.stock_param.jointure_s(
        regle.fichier,
        obj.attributs.get(regle.params.att_entree.val, regle.params.val_entree.val),
        regle.champ,
    )
    return True


def h_round(regle):
    """helper round : stocke le nombre de decimales"""
    regle.ndec = int(regle.params.cmp1.num if regle.params.cmp1.num else 0)


def f_round(regle, obj):
    """#aide|| arrondit une valeur a n decimales
    #pattern||S;?N;A;round;?N;||sortie
    #schema||ajout_attribut
    #test||obj||^X;1.534;;set||^X;;X;round;2||atn;X;1.53
    """
    regle.setval_sortie(obj, str(round(float(regle.getval_entree(obj)), regle.ndec)))
    return True

def f_vround(regle, obj):
    """#aide|| arrondit une variable a n decimales
    #pattern||P;?N;A;round;?N;||sortie
    #schema||ajout_attribut
    #helper||round
    #test||obj||^X;1.534;;set||^P:W;;X;round;2||ptv;W;1.53
    """
    valeur= str(round(float(regle.getval_entree(obj)), regle.ndec))
    regle.setvar(regle.params.att_sortie.val, valeur)
    return True


def geocode_traite_stock(regle, final=True):
    """libere les objets geocodes """
    if regle.nbstock == 0:
        return
    flist = list(regle.filtres.values())
    adlist = regle.params.att_entree.liste
    prefix = regle.params.cmp1.val
    outcols = 2 + len(flist)
    header = []
    suite = regle.branchements.brch["end"]
    fail = regle.branchements.brch["fail"]
    traite = regle.stock_param.moteur.traite_objet
    geocodeur = regle.getvar("url_geocodeur")
    data = {"columns": "_adresse"}.update(regle.filtres)
    buffer = (
        ";".join(["ident","_adresse"]+flist)+'\n'
        + "\n".join(
            [
                str(n) + ";" + " ".join([obj.attributs.get(i, "") for i in adlist])
                +((';'+ ";".join([obj.attributs.get(i, "") for i in flist ])) if flist else '')
                for n, obj in enumerate(regle.tmpstore)
            ]
        )
    ).encode("utf-8")

    # print('geocodage', regle.nbstock, adlist,flist, data)


    files = {"data": io.BytesIO(buffer)}
    res = requests.post(geocodeur, files=files, data=data)
    # print ('retour', res.text)

    #        print ('retour ',buf)
    for ligne in res.text.split("\n"):
        # print ('traitement sortie',ligne)
        if not ligne:
            continue
        attributs = ligne[:-1].split(";")
        # attributs = ligne.split(";")
        if attributs[0].isnumeric():
            numero = int(attributs[0])
            obj = regle.tmpstore[numero]
            obj.attributs.update(
                [(nom, contenu) for nom, contenu in zip(header, attributs[outcols:])]
            )
            # print ('retour',obj)
            score = obj.attributs.get("result_score", "")
            if not score:
                print ('erreur geocodage', attributs)
            traite(obj, suite if score else fail)
        elif not header:
            header = [prefix + i for i in attributs[outcols:]]
            # print ('calcul header', header)
            obj = regle.tmpstore[0]
            if obj.schema:
                # print ('geocodage action schema',regle.action_schema, header)
                obj.schema.force_modif(regle)
                regle.action_schema(regle, obj, liste=header)
                # print ('schema :', obj.schema)
        else:
            if not final:
                print("geocodeur: recu truc etrange ", ligne)
                # print("retry")
                # geocode_traite_stock(regle, final=True)
                return

    # and regle in obj.schema.regles_modif
    regle.traite += regle.nbstock
    regle.nbstock = 0
    print(
        "geocodage %d objets en %d secondes (%d obj/sec)"
        % (regle.traite, int(time.time() - regle.tinit), regle.traite / (time.time() - regle.tinit))
    )
    regle.tmpstore = []


def h_geocode(regle):
    """ prepare les espaces de stockage et charge le geocodeur addok choisi"""

    print("geocodeur utilise ", regle.getvar("url_geocodeur"))
    regle.blocksize = int(regle.getvar("geocodeur_blocks", 1000))
    regle.store = True
    regle.nbstock = 0
    regle.traite = 0
    regle.traite_stock = geocode_traite_stock
    regle.tmpstore = []
    regle.scoremin = 0
    print("liste_filtres demandes", regle.params.cmp2.liste)
    regle.filtres = dict(i.split(":") for i in regle.params.cmp2.liste)
    #    regle.ageocoder = dict()
    regle.tinit = time.time()
    return True


def f_geocode(regle, obj):
    """#aide||geocode des objets en les envoyant au gecocodeur addict
    #aide_spec||en entree clef et liste des champs adresse a geocoder score min pour un succes
    #pattern||;;L;geocode;?C;?LC
    #schema||ajout_att_from_liste
    """
    #    clef = obj.attributs.get(regle.params.cmp1.val)
    #    print("avant geocodeur", regle.nbstock)
    regle.tmpstore.append(obj)
    #    regle.ageocoder[clef] = ";".join([obj.attributs.get(i,"")
    #                                      for i in regle.params.att_entree.liste])
    #    print("geocodeur", regle.nbstock)
    regle.nbstock += 1
    if regle.nbstock >= regle.blocksize:
        regle.traite_stock(regle, final=False)
    return True


def h_map_data(regle):
    """ precharge le fichier de mapping et prepare les dictionnaires"""
    regle.dynlevel = 0  # les noms de mapping dependent ils des donnees d entree
    regle.mapping = None
    regle.identclasse = None
    regle.liste_att = None
    #    if regle.params.att_sortie.val == '#schema': # mapping d un schema existant
    #        schema2 =
    regle.lastfich = None
    fich = regle.params.cmp1.val
    if "[F]" in fich:
        regle.dynlevel = 2
    elif "[C]" in fich:
        regle.dynlevel = 1
    if regle.dynlevel:
        regle.clefdyn = ""
    else:
        charge_mapping(regle)


def f_map_data(regle, obj):
    """#aide||applique un mapping complexe aux donnees
    #aide_spec||C: fichier de mapping
    #pattern||A;?C;A;map_data;C
    #schema||ajout_attribut
    """
    val = regle.getval_entree(obj)
    obj.attributs[regle.params.att_sortie.val] = regle.elmap.get(val, val)
    return val in regle.elmap


def f_map_data_liste(regle, obj):
    """#aide||applique un mapping complexe aux donnees
    #aide_spec||C: fichier de mapping
    #pattern||L;?C;L;map_data;C
    #helper||map_data
    #schema||ajout_attribut
    """
    defaut = regle.params.val_entree.val
    for entree, sortie in zip(regle.params.att_entree.liste, regle.params.att_sortie.liste):
        val = obj.attributs.get(entree, defaut)
        obj.attributs[sortie] = regle.elmap.get(val, val)
    return True


def f_map_data_type(regle, obj):
    """#aide||applique un mapping complexe aux donnees
    #aide_spec||C: fichier de mapping
    #aide_spec||T: definition de type de donnees (T:)
    #pattern||*;?C;T:;map_data;C
    #helper||map_data
    #schema||ajout_attribut
    """
    if obj.schema is None:
        return False
    ident = obj.schema.identclasse
    if ident != regle.identclasse:
        regle.identclasse = ident
        regle.liste_att = [
            i
            for i in obj.schema.attributs
            if obj.schema.attributs[i].type_att == regle.params.att_entree.val
        ]
    defaut = regle.params.val_entree.val
    if not regle.liste_att:
        return False
    for att in regle.liste_att:
        val = obj.attributs.get(att, defaut)
        obj.attributs[att] = regle.elmap.get(val, val)
    return True
