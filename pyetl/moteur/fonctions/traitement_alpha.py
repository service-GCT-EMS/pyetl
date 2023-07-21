# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
#titre||manipulation d'attributs

# description des patterns pour les attributs :
# chaque pattern comprend 5 champs sous la forme:
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
from collections import namedtuple
from itertools import zip_longest
from datetime import datetime
import re
import copy
import logging
import json

LOGGER = logging.getLogger(__name__)


def f_setliste(regle, obj):
    """#aide||affectation d'un ensemble d'attributs
    #aide_spec||remplacement d'une liste de valeurs d'attribut avec defaut
    #parametres||liste de sortie;liste de defauts;liste d'entree
    #pattern||M;?LC;?L;set;;||sortie
    #test1||obj||^V4,V5;;C1,C2;set||atv;V4;AB
    #test2||obj||^V4,V5;;C1,C2;set||atv;V5;BCD
    #test3||obj||^V4,V5;;C1,C2;set||ats;V5

    """
    #    print ("dans setliste", regle.ligne,regle.params.att_sortie, regle.params.att_entree)
    regle.setval_sortie(obj, regle.getlist_entree(obj))
    return True


def f_setmatch_liste(regle, obj):
    """#aide||affectation d un attribut
    #aide_spec1||remplacement d'une liste de valeurs d'attribut par les valeurs retenues dans la selection
               ||par expression regulieres (recupere les groupes de selections)
      #pattern1||M;;;set;=match;||sortie
    #parametres||liste de sortie;=match;
          #test1||obj||^X;BCD;;set;||X;re:(.)C(.);;;V4,V5;;;set;match||atv;V4;B
          #test2||obj||^X;BCD;;set;||X;re:(.)C(.);;;V4,V5;;;set;match||atv;V5;D
    """
    # print ('regle.match',regle.match )
    regle.setval_sortie(obj, regle.matchlist)
    return True


# def h_setval(regle):
#     """helper de fonctiond'entree"""
#     if not regle.params.att_entree.val:
#         regle.get_entree = regle.get_defaut


def f_setval(regle, obj):
    """#aide||affectation d un attribut
       #aide_spec||remplacement d'une valeur d'attribut avec defaut
       #pattern||S;?;?A;set;;||sortie
    #parametres||attribut de sortie;defaut;attribut d'entree
       #test1||obj||^V4;;C1;set||atv;V4;AB
       #test2||obj||^V4;1;X;set||atv;V4;1
       #test3||obj||^V4;1;X;set||ats;V4

    """
    regle.setval_sortie(obj, regle.get_entree(obj))
    return True

def h_setuuid(regle):
    """ importe la bibliotheque"""
    import uuid
    regle.uuid=uuid
    return True

def f_setuuid(regle, obj):
    """#aide||affectation d un attribut
       #aide_spec||cree un uuid
       #pattern||S;;;set;=UUID;||sortie
    #parametres||attribut de sortie;defaut;attribut d'entree
    """
    regle.setval_sortie(obj, str(regle.uuid.uuid1()))
    return True

def f_setmatch(regle, obj):
    """#aide||affectation d un attribut
       #aide_spec||remplacement d'une valeur d'attribut par les valeurs retenues dans la selection
       ||par expression regulieres (recupere toute la selection)
       #pattern||S;;;set;=match;||sortie
    #parametres||attribut de sortie
       #test1||obj||^X;BCDXX;;set;||X;re:(.)C(.);;;V4;;;set;match||atv;V4;BCD
       #test2||obj||^X;BCDXX;;set;||X;re:(.)C(.);;;V4;;;set;match||ats;V4
    """
    regle.setval_sortie(obj, regle.match)
    return True


def h_setschema(regle):
    """helper : positionne le nocase"""
    regle.changeschema = True
    if regle.params.cmp1.val:
        regle.setvar("schema_nocase", regle.params.cmp1.val)


def f_setschema(regle, obj):
    """#aide||affectation d un schema en adaptant la casse des attributs du schema a l'objet
    #parametres||;valeur par defaut;attribut d'entree;;
        #helper||setval
      #pattern1||=#schema;?;?A;set;=maj;||sortie
    #aide_spec1||change le schema de reference d'un objet et passe en majuscule
      #pattern2||=#schema;?;?A;set;=min;||sortie
    #aide_spec2||change le schema de reference d'un objet et passe en minuscule
      #pattern3||=#schema;?;?A;set;||sortie
    #aide_spec3||change le schema de reference d'un objet
    """
    obj.attributs["#schema"] = regle.get_entree(obj)
    return True


def f_setgeom(regle, obj):
    """#aide||affectation d un attribut
  #aide_spec||cree une geometrie texte
     #helper||setval
    #pattern||=#geom;?;?A;set;C;N||sortie
 #parametres||#geom (mot clef);valeur par defaut;attribut d'entree;;format;dimension
      #test1||obj||^#geom;1SEC 1,2,|1,0,|0,0,1,0;;set;#asc;2;
            ||^;;;geom||atv;#type_geom;2
      #test2||obj||^#gg;1SEC 1,2,|1,0,|0,0,1,0;;set||^#geom;;#gg;set;#asc;2;\
            ||^;;;geom||atv;#type_geom;2
    """
    geom = regle.get_entree(obj)
    # print("recup geom:", geom, obj)

    obj.format_natif = regle.params.cmp1.val

    obj.geompending(dimension=regle.params.cmp2.num if regle.params.cmp2.num else 2)
    converter = regle.stock_param.get_converter(obj.format_natif, debug=regle.debug)
    structure = regle.stock_param.get_geomstructure(obj.format_natif, debug=regle.debug)
    if converter:
        obj.attributs_geom = converter
        if structure == list and not isinstance(obj.attributs["#geom"], list):
            obj.attributs["#geom"] = geom.split("|")
        else:
            obj.attributs["#geom"] = geom
    return True


def h_setnonvide(regle):
    """pour repl_c il faut mettre en forme la liste"""
    regle.params.att_entree.liste = []  # on vide la liste pour la recreer
    regle.params.att_entree.liste.extend(regle.params.att_entree.val.split("|"))


def f_setnonvide(regle, obj):
    """#aide||remplacement d une valeur
    #aide_spec||remplacement d'une valeur d'attribut par le premier non vide
    ||d'une liste avec defaut
    #parametres||attribut resultat;defaut;liste d'attributs d'entree separes par |
    #pattern||S;?;|L;set;;||entree
    #test3||obj||^V4;1;A|C1|C2;set||atv;V4;AB
    #test4||obj||^V4;1;A|B;set||atv;V4;1
    #test2||obj||^V4;1;A|B;set||ats;V4
    """
    regle.setval_sortie(
        obj,
        next(
            (
                obj.attributs.get(i)
                for i in regle.params.att_entree.liste
                if obj.attributs.get(i)
            ),
            regle.params.val_entree.val,
        ),
    )
    return True


def h_setjoin(regle):
    """preparation separateur"""
    regle.separ = regle.params.cmp1.val if regle.params.cmp1.val != "#b" else " "


def f_setjoin(regle, obj):
    """#aide||remplacement d une valeur
    #aide_spec||remplacement d'une valeur d'attribut par la concatenation de champs
    ||d'une liste avec defaut
    #parametres||attribut resultat;defaut;liste d'attributs d'entree separes par ,;;separateur;format resultat
    #pattern1||S;?;L;set;?C;=text
    #pattern2||S;?;L;set;;=list
    #pattern3||S;?;L;set;;=set
    #test3||obj||^V4;1;A|C1|C2;set||atv;V4;AB
    #test4||obj||^V4;1;A|B;set||atv;V4;1
    #test2||obj||^V4;1;A|B;set||ats;V4
    """
    liste = [obj.attributs.get(i, "") for i in regle.params.att_entree.liste]
    if regle.params.pattern == "1":
        regle.setval_sortie(
            obj,
            regle.separ.join(liste) or regle.params.val_entree.val,
        ),
    elif regle.params.pattern == "2":
        obj.attributs[regle.params.att_sortie.val] = (
            liste or regle.params.val_entree.liste
        )
    elif regle.params.pattern == "3":
        obj.attributs[regle.params.att_sortie.val] = set(
            liste or regle.params.val_entree.liste
        )
    return True


def h_sub(regle):
    """helper pour sub : compile les expressions regulieres"""
    try:
        regle.exp_entree = re.compile(
            regle.params.cmp1.val
        )  # expression sur l'attribut d'entree
    except re.error as err:
        LOGGER.exception(
            "expression reguliere invalide %s", regle.params.cmp1.val, exc_info=err
        )
        # print("expression reguliere invalide", regle.params.cmp1.val, err)
        regle.valide = False
        regle.erreurs.append("erreur compilation des expressions" + repr(err))
        return
    regle.exp_sortie = regle.params.cmp2.val

    if regle.params.cmp2.val.startswith("f:"):
        if "__" in regle.params.cmp2.val:
            raise SyntaxError("fonction non autorisee:" + regle.params.cmp2.val)
        try:
            regle.exp_sortie = eval("lambda " + regle.params.cmp2.val, {})
            regle.valide = True
        except SyntaxError as err:
            regle.valide = False
            regle.erreurs.append("erreur compilation des expressions" + err.msg)
            return
    regle.statique = not regle.params.cmp2.origine
    # # remplacement dynamique
    # print("dynval", regle.statique)
    if not regle.statique:
        regle.exp_sortie = regle.params.cmp2.val[1:-1]
    try:
        regle.maxsub = int(regle.getvar("maxsub", 0))
    except ValueError:
        regle.maxsub = 0
        regle.setlocal("maxsub", str(regle.maxsub))  # on force la variable en local
    if regle.params.pattern == "2":
        regle.setvar(
            regle.params.att_sortie.val,
            regle.exp_entree.sub(
                regle.exp_sortie, regle.params.val_entree.val, count=regle.maxsub
            ),
        )
        regle.valide = "done"


# fonctions de traitement alpha
def f_sub(regle, obj):  # fonction de substution
    """#aide||remplacement d une valeur
        #aide_spec||application d'une fonction de transformation par expression reguliere
        #pattern||S;?;A;sub;re;?re||sortie
        #pattern2||P;C;;sub;re;?re||sortie||10
    #parametres||resultat;defaut;entree;;expression de selection;expression de substitution
    #variables||maxsub: nombre maxi de substitutions (variable locale)
        #test1||obj||^V4;;C1;sub;A;B;||atv;V4;BB
        #test2||obj||^V4;;C1;sub;.*;f:f.group(0).lower();||atv;V4;ab
        #test3||obj||^V4;;C1;sub;A;B;||ats;V4
        #test4||obj||^XX;AAA;;set||^V4;;XX;sub;A;B;;maxsub=2||atv;V4;BBA

    """
    # substitution

    exp_sortie = (
        regle.exp_sortie if regle.statique else obj.attributs.get(regle.exp_sortie, "")
    )

    regle.setval_sortie(
        obj,
        regle.exp_entree.sub(exp_sortie, regle.getval_entree(obj), count=regle.maxsub),
    )
    return True


def h_setcalc(regle):
    """preparation de l'expression du calculateur de champs"""
    # print("dans hcalc", regle.params)
    try:
        if regle.params.pattern == "1":
            regle.calcul = regle.params.compilefonc(
                regle.params.att_entree.val, "obj", debug=regle.debug
            )
        elif regle.params.pattern == "2":
            regle.calcul = regle.params.compilefonc(
                regle.params.val_entree.val, "obj", debug=regle.debug
            )
            regle.setvar(regle.params.att_sortie, str(regle.calcul(None)))
    except SyntaxError as err:
        LOGGER.exception(
            "erreur sur l'expression de calcul->%s<-",
            regle.params.att_entree.val,
            exc_info=err,
        )
        # print(
        #     "erreur sur l'expression de calcul->" + regle.params.att_entree.val + "<-"
        # )
        regle.params.compilefonc(regle.params.att_entree.val, "obj", debug=True)
        regle.valide = False


def f_setcalc(regle, obj):
    """#aide||remplacement d une valeur
        #aide_spec||fonction de calcul libre (attention injection de code)
        || les attributs doivent etre précédes de N: pour un traitement numerique
        || ou C: pour un traitement alpha
    #parametres||attribut resultat;formule de calcul
        #pattern1||S;;NC:;set;;
        #pattern2||P;NC2:;;set;;||defaut||10
        #test1||obj||^V4;;N:V1+1;set||atn;V4;13
        #test2||obj||^V4;;N:V1+1;set||ats;V4
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
        #!pattern||S;?;A;upper;;||sortie
        #pattern||A;?;A;upper;;||sortie
    #parametres||attribut resultat;defaut;attribut d'entree
        #test1||obj||^V4;a;;set||^V4;;V4;upper||atv;V4;A
        #test2||obj||^V4;a;;set||^V5;;V4;upper||ats;V5

    """
    # print("-----------upper", regle.params.att_sortie, regle.fstore)
    regle.setval_sortie(obj, regle.getval_entree(obj).upper())
    return True


def f_upper2(regle, obj):
    """#aide||remplacement d une valeur
        #aide_spec||passage en majuscule d'un attribut ( avec defaut eventuel)
        #pattern1||A;?;;upper||sortie||50
    #parametres1||attribut;defaut
        #pattern2||;?;A;upper||sortie||50
    #parametres2||defaut,attribut
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
    #parametres||liste attributs sortie;defaut;liste attributs entree
        #test1||obj||^V4,V5;a,b;;set||^V4,V5;;V4,V5;upper||atv;V5;B
        #test2||obj||^V4,V5;a,b;;set||^V4,V5;;V4,V5;upper||atv;V4;A
        #test3||obj||^V4,V5;a,b;;set||^V4,V6;;V4,V5;upper||ats;V6
    """
    regle.process_liste(obj, str.upper)
    return True


def f_upper_liste2(regle, obj):
    """#aide||passage en majuscule d'une lister de valeurs
        #aide_spec||passage en majuscule d une liste d'attribut avec defaut
        #pattern1||L;?;;upper;;||sortie||99
    #parametres1||liste attributs;defaut
        #pattern2||;?;L;upper;;||sortie||99
    #parametres2||defaut;liste attributs
        #helper||setself
        #schema||ajout_attribut
        #test1||obj||^V4,V5;a,b;;set||^;;V4,V5;upper||atv;V5;B
        #test2||obj||^V4,V5;a,b;;set||^V4,V5;;;upper||atv;V4;A
    """
    obj.attributs.update(
        zip(regle.params.att_ref.liste, map(str.upper, regle.getlist_ref(obj)))
    )
    return True


def f_lower(regle, obj):
    """#aide|| passage en minuscule
     #aide_spec|| passage en minuscule d'une valeur d'attribut avec defaut
       #pattern||S;?;A;lower;;||sortie
    #parametres||attribut resultat;defaut;attribut d'entree
         #test1||obj||^V4;A;;set||^V4;;V4;lower||atv;V4;a

    """
    regle.setval_sortie(obj, regle.getval_entree(obj).lower())
    return True


def f_lower2(regle, obj):
    """#aide|| passage en minuscule
      #aide_spec||remplacement d'une valeur d'attribut avec defaut passage en majuscule
       #pattern1||A;?;;lower;;
    #parametres1||attribut;defaut
       #pattern2||;?;A;lower;;
    #parametres2||attribut resultat;defaut;attribut d'entree
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
    #parametres||liste attributs sortie;defaut;liste attributs entree
        #schema||ajout_attribut
           #testl1||obj||^V4,V5;A,B;;set||^V4,V5;;V4,V5;lower||atv;V5;b
           #testl2||obj||^V4,V5;A,B;;set||^V4,V5;;V4,V5;lower||atv;V4;a
    """
    regle.process_liste(obj, str.lower)
    return True


def f_lower_liste2(regle, obj):
    """#aide||passage en minuscule d'une lister de valeurs avec defaut
      #aide_spec||passage en minuscule d une liste d'attribut
       #pattern1||L;?;;lower;;||sortie
    #parametres1||liste attributs;defaut
       #pattern2||;?;L;lower;;||sortie
    #parametres2||defaut;liste attributs
         #helper||setself
         #schema||ajout_attribut
          #test1||obj||^V4,V5;A,B;;set||^;;V4,V5;lower||atv;V5;b
          #test2||obj||^V4,V5;A,B;;set||^V4,V5;;;lower||atv;V4;a
    """
    obj.attributs.update(
        zip(regle.params.att_ref.liste, map(str.lower, regle.getlist_ref(obj)))
    )
    return True


def h_asplit(regle):
    """preparation decoupage attributs"""
    f_debut = None
    f_fin = None
    tmp = []
    nbres = len(regle.params.att_sortie.liste)
    regle.multi = not regle.params.att_sortie.val
    if regle.multi:
        nbres = 0
    sep = regle.params.cmp1.val
    if regle.params.cmp1.val == "\\s":
        sep = ";"
    if regle.elements["cmp2"].group(0):
        tmp = regle.elements["cmp2"].group(0).split(":")
        f_debut = tmp[0]
    if tmp and len(tmp) > 1:
        f_fin = tmp[1]
    try:
        regle.defcible = slice(
            int(f_debut) if f_debut else None, int(f_fin) if f_fin else None
        )
    except ValueError as err:
        regle.stock_param.logger.exception(
            "erreur definition decoupage->%s<-", regle.params.cmp2.val, exc_info=err
        )
        regle.valide = False
        return
    nbdecoup = nbres - 1 + (int(f_debut) if f_debut else 0)
    regle.modestruct = regle.params.pattern == "3"

    if regle.debug:
        print(
            "cible decoupage",
            regle.defcible,
            nbdecoup,
            regle.params.att_sortie.liste,
            regle.multi,
        )
    regle.sep = sep
    regle.nbdecoup = nbdecoup if not regle.multi else -1
    if regle.params.pattern=="4":
        print ("decoupage parametres",regle.params.att_sortie.liste)
        vals=str(regle.params.val_entree.val).split(regle.sep, regle.nbdecoup)
        for p,v in zip(regle.params.att_sortie.liste,vals):
            regle.setvar(p,v)
        regle.valide='done'



def f_asplit(regle, obj):
    """#aide||decoupage d'un attribut en fonction d'un separateur
      #aide_spec||s'il n'y a pas d'attributs de sortie on cree un objet pour chaque element
       #pattern1||M;?;A;split;.;?N:N||sortie
    #parametres1||liste attributs sortie;defaut;attribut;;caractere decoupage;nombre de morceaux:debut
       #pattern2||;?;A;split;.;?N:N||sortie
    #parametres2||defaut;attribut;;caractere decoupage;nombre de morceaux:debut
       #pattern3||;?;A;split;;?N:N||cmp1
    #parametres3||defaut;attribut;;;nombre de morceaux:debut
       #pattern4||LP;C;;split;.;?N:N||sortie
    #traitement de variables
          #test1||obj||^V4;a:b:cc:d;;set||^r1,r2,r3,r4;;V4;split;:;||atv;r3;cc
          #test2||obj||^V4;a:b:c:d;;set||^;;V4;split>;:;||cnt;4
          #test3||obj||^V4;a:b:c:d;;set||^X,Y;;V4;split;:;;||atv;Y;b:c:d
    """
    att = regle.getval_entree(obj)
    keys = None

    if regle.sep:
        elems = att.split(regle.sep, regle.nbdecoup)[regle.defcible]
        # print("decoupage", elems)
    elif isinstance(att, (list, tuple)):
        if hasattr(att, "_fields"):  # c est un namedtuple
            atd = att._asdict()
            elems = list(atd.values())[regle.defcible]
            keys = list(atd.keys)[regle.defcible]
        else:
            elems = att[regle.defcible]
    elif isinstance(att, dict):
        elems = [att.values()][regle.defcible]
        keys = [att.keys][regle.defcible]

    else:
        elems = [regle.getval_entree(obj)]

        # regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["gen"])
    if regle.multi:
        # obj.attributs[regle.params.att_entree.val] = elems[0] if elems else ""
        for i in elems:
            obj2 = obj.dupplique()
            obj2.attributs[regle.params.att_entree.val] = i
            if keys:
                obj2.attributs["#clef"] = keys.pop(0)
            obj2.redirect = "gen"
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
    else:
        regle.setval_sortie(obj, elems)
    return True


def f_strip(regle, obj):
    """#aide||supprime des caracteres aux extremites
       #pattern||S;?;A;strip;?C;||sortie
    #parametres||sortie;defaut;attribut;;caractere a supprimer blanc par defaut
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
       #pattern1||;?;A;strip;?C;||sortie
    #parametres1||;defaut;attribut;caractere a supprimer blanc par defaut
       #pattern2||A;?;;strip;?C;||entree
    #parametres2||attribut;defaut;caractere a supprimer blanc par defaut
        #test||obj||^V4;abbaa;;set||^;;V4;strip;a;||atv;V4;bb
        #test2||obj||^V4;abbaa;;set||^V4;;;strip;a;||atv;V4;bb
    """
    if regle.params.cmp1.val:
        obj.attributs[regle.params.att_ref.val] = regle.getval_ref(obj).strip(
            regle.params.cmp1.val
        )
    else:
        obj.attributs[regle.params.att_ref.val] = regle.getval_ref(obj).strip()
    return True


def f_len(regle, obj):
    """#aide||calcule la longueur d un attribut
       #pattern||S;?;A;len;;
    #parametres||attribut resultat;defaut;attribut d'entree
        #test||obj||^X;toto;;set;||^Y;;X;len;;||atv;Y;4
    """
    regle.setval_sortie(obj, str(len(regle.getval_entree(obj))))
    return True


def h_vset(regle):
    """positionnement variable"""
    if not regle.params.att_entree.val:
        regle.setvar(regle.params.att_sortie.val, regle.params.val_entree.val)
        regle.valide = "done"


def f_vset(regle, obj):
    """#aide||remplacement d une valeur
       #aide_spec||positionne une variable
       #pattern||P;?;?A;set;;||sortie
    #parametres||variable (sans les %);defaut;attribut d'entree
       #test1||obj||^P:AA;1;;set||ptv;AA;1
    """
    valeur = (
        obj.attributs.get(regle.params.att_entree.val) or regle.params.val_entree.val
    )
    # print("dans vset", regle.params.att_sortie.val, valeur)
    # raise
    if valeur != regle.getvar(regle.params.att_sortie.val):
        regle.setvar(regle.params.att_sortie.val, valeur)
        for i in regle.stock_param.bindings.get(regle.params.att_sortie.val, ()):
            LOGGER.info("reinterpretation regle %s", repr(i))
            # print("reinterpretation regle", i)
            regle.stock_param.reconfig(regle.stock_param.regles[i], regle.stock_param)
        # print ('stocke ', regle.params.att_sortie.val,
    return True


def f_renamelist(regle, obj):  # fonction de substution
    """#aide||renommage d'une liste d attributs
       #pattern||L;;L;ren;;||
    #parametres||liste nouveaux noms;liste ancien noms
        #schema||rename_attribut
         #test1||obj||^V4,V5;;C1,C2;ren||atv;V4;AB
    """
    ok = True
    for dest, orig in zip(regle.params.att_sortie.liste, regle.params.att_entree.liste):
        if dest in obj.attributs:
            ok = False
        elif orig in obj.attributs:
            obj.attributs[dest] = obj.attributs[orig]
            del obj.attributs[orig]
    return ok


def f_rename(regle, obj):  # fonction de substution
    """#aide||renommage d'un attribut
       #pattern||A;;A;ren;;||sortie
    #parametres||nouveau nom;ancien nom
        #schema||rename_attribut
         #test1||obj||^V4;;C1;ren||atv;V4;AB
    """
    if regle.params.att_sortie.val in obj.attributs:
        return False  # on ecrase pas d'attribut
    if regle.params.att_entree.val in obj.attributs:
        obj.attributs[regle.params.att_sortie.val] = obj.attributs[
            regle.params.att_entree.val
        ]
        del obj.attributs[regle.params.att_entree.val]
        return True
    return False  # l attribut n' existe pas on ne fait rien


def _suppatt(obj, nom):
    """#aide||suppression d'un element"""
    del obj.attributs[nom]  # suppression d'attribut
    if nom in obj.attributs_speciaux:
        del obj.attributs_speciaux[nom]
    if obj.hdict and nom in obj.hdict:
        del obj.hdict[nom]
    return True


def f_suppl(regle, obj):
    """#aide||suppression d'elements
     #aide_spec||suppression d une liste d'attributs
       #pattern||;;L;supp;;||entree
    #parametres||liste attributs
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
          #aide_spec||suppression de la geometrie
    #parametres||#geom (mot clef)
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
           #aide_spec||suppression du schema
    #parametres||#schema (mot clef)
           #pattern1||;;=#schema;supp;;||entree
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
    #aide_spec||suppression d l objet complet
      #pattern||;;;supp;;
        #test3||obj;;2||V0;1;;;;;;supp||#classe;;;;nb;;C1;stat;cnt||anstat;atv:nb:1;
    """
    return True


def h_suppclasse(regle):
    """evite la transmission d'un objet et supprime la classe du schema"""
    h_suppobj(regle)
    regle.supp_classe = True


def f_suppclasse(_, obj):
    """#aide||suppression d'elements
    #aide_spec||suppression de la classe d objets avec tous ses objets et son schema
      #pattern||;;;supp_classe;;
    """
    if obj.schema:
        obj.schema.deleted = True
        return True
    return False


def f_keep2(regle, obj):
    """#aide||suppression de tous les attributs sauf ceux de la liste
      #pattern1||;;L;garder;;
      #pattern2||L;;;garder;;
    #parametres||liste des attributs a garder
        #schema||garder_attributs
        #helper||setself
          #test||obj||^;;C1;garder||^X;2;C2;set||atv;X;2
         #test2||obj||^C1;;;garder||^X;2;C2;set||atv;X;2
    """
    asupprimer = [
        i for i in obj.attributs if not i.startswith("#") and i not in regle.selset
    ]
    #    print ('garder sauf ' , asupprimer)
    regle.asupprimer = asupprimer
    for nom in asupprimer:
        _suppatt(obj, nom)
    return True


def h_keep(regle):
    """cree un ensemble a partir de la liste de sortie"""
    regle.selset = set(regle.params.att_sortie.liste)
    if regle.istrue("verbose"):
        regle.stock_param.logger.info('keep %s -> %s (%s)',repr(regle.params.att_entree.liste),
            repr(regle.params.att_sortie.liste),
            repr(regle.params.val_entree.liste))
    return True


def f_keep(regle, obj):
    """#aide||suppression de tous les attributs sauf ceux de la liste
     #aide_spec||avec renommage de la liste et eventuellemnt valeur par defaut
       #pattern3||L;?LC;L;garder;;
    #parametres||nouveaux noms;liste val defauts;attributs a garder
        #schema||garder_attributs
          #test||obj||^C1;;;garder||^X;2;C2;set||atv;X;2
         #test2||obj||^ZZ;;C1;garder||atv;ZZ;AB
    """
    if regle.params.att_entree.liste:  # on renomme les attributs
        for source, dest, defaut in zip(
            regle.params.att_entree.liste,
            regle.params.att_sortie.liste,
            regle.params.val_entree.liste,
        ):
            obj.attributs[dest] = obj.attributs.get(source, defaut)
    else:
        for dest, defaut in zip(
            regle.params.att_sortie.liste, regle.params.val_entree.liste
        ):
            if dest not in obj.attributs:
                obj.attributs[dest] = defaut

    return f_keep2(regle, obj)


def h_cnt(regle):
    """init compteur"""
    regle.orig = regle.params.cmp2.num if regle.params.cmp2.num else 0
    regle.pas = regle.params.cmp1.num if regle.params.cmp1.num else 1
    regle.local = not (regle.params.att_entree.val or regle.params.val_entree.val)
    return True


def f_cnt(regle, obj):
    """#aide||creation des compteurs
     #parametres||attribut de sortie;nom fixe;attribut contenant le nom du compteur;;pas;origine
    #aide_spec||le comteur est global s'il a un nom, local s'il n'en a pas
       #pattern||S;?;?A;cnt;?N;?N
        #schema||ajout_attribut
         #test1||obj||^V4;t1;;cnt;3;4||atv;V4;4
         #test2||obj;;2||^V4;t1;;cnt;3;4||V4;4;;;;;;supp||atv;V4;7
    """
    if obj.virtuel:
        return True
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
    # print(" jointure", regle.params)
    regle.fichier = regle.params.cmp1.val  # nom du fichier
    if regle.fichier.startswith("#"):  # jointure objets sur tmpstore
        regle.jointtype = "obj"
        regle.champs = list((i for i in regle.params.cmp2.liste))
        regle.recup_geom = "#geom" in regle.params.cmp2.liste
        regle.ajuste_geom = regle.recup_geom
        regle.jstore = regle.stock_param.store.get(regle.params.cmp1.val)
        if regle.jstore is None:
            # print("element de comparaison non defini " + regle.params.cmp1.val)
            raise SyntaxError(
                "join: element de comparaison non defini " + regle.params.cmp1.val
            )
    else:
        regle.jointtype = "fich"
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
       #pattern||L;?;?A;join;C[];?C||cmp1
       #pattern2||M?;?;?L;join;#C;?C||cmp1
    #parametres||sortie;defaut;entree;;fichier (dynamique)
               ||position des champs dans le fichier (ordre)
     #attributs||#repertoire (optionnel) repertoire du fichier
     #aide_spec||sur un fichier dans le repertoire des donnees
        #schema||ajout_attribut
          #test||obj||^X;C;;set||^val;;X;join;%testrep%/refdata/join.csv;X,nom,val||atv;val;3
    """
    if regle.jointtype == "obj":
        clef_jointure = '|'.join(regle.getlist_entree(obj))
        # print("clef jointure", clef_jointure)
        obj_joint = regle.jstore.get(clef_jointure)
        # print("obj joint",clef_jointure, obj_joint)

        if obj_joint:
            if regle.recup_geom:
                if obj_joint.geom_v.valide:
                    # print(" detecte geom_v", obj_joint.geom_v)
                    obj.geom_v = copy.deepcopy(obj_joint.geom_v)
                    if regle.ajuste_geom:
                        regle.ajuste_geom = False
                        if obj.schema and obj_joint.schema:
                            obj.schema.info["type_geom"] = obj_joint.schema.info[
                                "type_geom"
                            ]
                else:
                    geom = obj_joint.attributs.get("#geom")
                    # obj.attributs_geom = obj_joint.attributs_geom
                    if regle.ajuste_geom:
                        regle.ajuste_geom = False
                        if obj.schema:
                            obj.schema.info["type_geom"] = "-1"
                    # print("recup #geom")
                    obj.attributs["#geom"] = geom
                    # (geom if isinstance(geom, str) else list(geom))

                    obj.format_natif = obj_joint.format_natif
                    obj.geompending()
                    obj.attributs_geom = obj_joint.attributs_geom

            if regle.champs and regle.champs != "*":
                vnlist = [(i, obj_joint.attributs.get(i, "")) for i in regle.champs]
            else:
                vnlist = [
                    (i, j)
                    for i, j in obj_joint.attributs.items()
                    if not i.startswith("#")
                ]
        else:
            if regle.istrue("debug"):
                print ('non trouve', clef_jointure)
            return False
        # print("list", vnlist)
        if regle.params.att_sortie.liste:
            regle.setval_sortie(obj, [i[1] for i in vnlist])
        else:
            obj.attributs.update(vnlist)

    else:
        obj.attributs[regle.params.att_sortie.val] = regle.stock_param.jointure(
            regle.fichier,
            obj.attributs.get("#repertoire", ""),
            obj.attributs.get(regle.params.att_entree.val, regle.params.val_entree.val),
            regle.champ,
        )
    # print("jointure", obj, obj.schema)
    return True


def f_sjoin(regle, obj):
    """#aide||jointures
     #aide_spec||jointure statique
       #pattern||A;?;A;join;?C;?C||cmp1
    #parametres||sortie;defaut;entree;;fichier
               ||position des champs dans le fichier (ordre)
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
    """#aide||arrondit une valeur d attribut à n decimales
    #pattern||S;?N;A;round;?N;||sortie
    #parametres||sortie;defaut;entree;;decimales
    #schema||ajout_attribut
    #test||obj||^X;1.534;;set||^X;;X;round;2||atn;X;1.53
    """
    try:
        regle.setval_sortie(
            obj, str(
                round(float(regle.getval_entree(obj)), regle.ndec) if regle.ndec else
                int(round(float(regle.getval_entree(obj)), regle.ndec))
                     )
        )
        return True
    except ValueError:
        regle.stock_param.logger.debug(
            "attention valeur %s non numerique", regle.getval_entree(obj)
        )
        return False


def f_vround(regle, obj):
    """#aide|| arrondit une variable a n decimales
    #pattern||P;?N;A;round;?N;||sortie
    #parametres||variable de sortie;defaut;entree;;decimales
    #schema||ajout_attribut
    #helper||round
    #test||obj||^X;1.534;;set||^P:W;;X;round;2||ptv;W;1.53
    """
    try:
        valeur = str(round(float(regle.getval_entree(obj)), regle.ndec))
        regle.setvar(regle.params.att_sortie.val, valeur)
        return True
    except ValueError:
        return False


def h_format(regle):
    """prepare le formattage"""
    holder = regle.params.cmp2.val if regle.params.cmp2.val else "µ"
    regle.espace = regle.getvar("espace")
    regle.params.att_entree.liste = regle.params.att_entree.val.split(",")
    regle.params.val_entree.liste = regle.params.val_entree.val.split(",")
    vlist = regle.params.att_entree.liste
    # on gere le fait que le % est reserve pour les variable donc on peut mettre autre chose
    
    regle.format = regle.params.cmp1.val.replace(holder, "%")
    # print("remplacement", holder, regle.params.cmp1.val)
    regle.espace = regle.getvar("espace", " ")
    flist = [None] * len(vlist)
    for n, v in enumerate(vlist):
        if v.startswith("N:"):
            flist[n] = float
        elif v.startswith("I:"):
            flist[n] = int
        elif v.startswith("C:"):
            flist[n] = str
        if flist[n]:
            vlist[n] = v[2:]
        elif v.startswith("#"):
            flist[n] = str
    regle.flist = flist
    regle.incomplet = None in flist
    return True


def f_format(regle, obj):
    """#aide||formatte un attribut utilise les formatages python standard
    #aide_spec||en cas de conflit (motif de type variable %xxx%) 
            ||il est possible de remplacer le % par un autre caractere (par defaut µ)
            ||si on souhaite des espaces avant ou apres le format il est possible de definir
            ||la variable espace pour remplacer les espaces
            ||exemple: °°µs%d°° avec espace=° devient '  %s%d  '
    #pattern1||S;?LC;?LC;format;C;?C
    #parametre||attribut de sortie;defaut;liste_entree;;format;remplacement du %
    #test1||obj||^X;1.534;;set||^Y;;N:X;format;%3.1f;||atv;Y;1.5
    #test2||obj||^X,A;1.534,B;;set||^Y;;N:X,A;format;%3.1f %s;||atv;Y;1.5 B
    """
    if len(regle.params.val_entree.liste)==1 and  isinstance(regle.getval_entree(obj),datetime):
        #formattage de dates
        try:
            regle.setval_sortie(obj,datetime.strftime(regle.getval_entree(obj),regle.format))
            return True
        except ValueError as err:
            print( "erreur formattage", err)
        return False

    if regle.incomplet:
        for n, v in enumerate(regle.params.att_entree.liste):
            if not regle.flist[n]:
                if obj.schema and v in obj.schema.attributs:
                    schematype = obj.schema.attributs[v].type_att
                    if schematype in "E,EL,S,BS":
                        regle.flist[n] = int
                    elif schematype in "F,N":
                        regle.flist[n] = float
                if not regle.flist[n]:
                    regle.flist[n] = str
        regle.incomplet = False

    vlist = regle.getlist_entree(obj)
    try:
        vlist2 = tuple((i(j)) for i, j in zip(regle.flist, vlist))
    except ValueError:
        regle.setval_sortie(obj, "")
        return False
    # print(
    #     " formattage",
    #     regle.params.cmp1.val,
    #     vlist,
    #     regle.flist,
    #     vlist2,
    #     regle.params.att_entree.liste,
    #     regle.params.val_entree.liste,
    # )
    if regle.espace:
        result = (regle.format % tuple(vlist2)).replace(" ", regle.espace)
        regle.setval_sortie(obj, result)
    else:
        regle.setval_sortie(obj, regle.format % tuple(vlist2))
    return True

def h_todate(regle):
    """prepare le format de dates"""
    holder = regle.params.cmp2.val if regle.params.cmp2.val else "µ"
    regle.espace = regle.getvar("espace")
    regle.format = regle.params.cmp1.val.replace(holder, "%")
    return True


def f_todate(regle,obj):
    """#aide||convertit un texte en date en utilisant un formattage prdefini
    #aide_spec||en cas de conflit (motif de type variable %xxx%) 
            ||il est possible de remplacer le % par un autre caractere (par defaut µ)
            ||si on souhaite des espaces avant ou apres le format il est possible de definir
            ||la variable espace pour remplacer les espaces
            ||exemple: °°µs%d°° avec espace=° devient '  %s%d  '
    #pattern1||S;?C;?A;to_date;C;?C
    #parametre||attribut de sortie;defaut;liste_entree;;format;remplacement du %
    ##test1||obj||^X;1.534;;set||^Y;;N:X;format;%3.1f;||atv;Y;1.5
    ##test2||obj||^X,A;1.534,B;;set||^Y;;N:X,A;format;%3.1f %s;||atv;Y;1.5 B
    """
    try:
        regle.setval_sortie(obj,datetime.strptime(regle.getval_entree(obj),regle.format))
        return True
    except ValueError as err:
        print( "erreur formattage", err)
        return False








def blocfilter(text, identifiant, keypair, escape):
    "analyse un bloc de texte et extrait des identifiants et des blocs enter paires de clefs"
    startbloc, endbloc = keypair
    foundblocs = dict()
    print("debut recherche")
    for match in identifiant.finditer(text):
        print("trouve match")
        clef = match.groups(1)
        recherche = match.end()
        level = 0
        start = 0
        long = 0
        for i in text[recherche:]:
            if level == 0:
                start += 1
            else:
                long += 1
            if i == startbloc:
                level += 1
            elif i == endbloc:
                level -= 1
                if level <= 0:
                    break
        if long:
            foundblocs[clef] = text[recherche + start - 1 : recherche + start + long]
        else:
            foundblocs[clef] = ""
    return foundblocs


def h_extractbloc(regle):
    """prepare les extractions"""
    try:
        regle.regex = re.compile(regle.params.cmp1.val, re.MULTILINE)
    except re.error as err:
        regle.stock_param.loger.error("erreur expression reguliere %s", err)
        return False
    keypair = regle.params.cmp2.val
    regle.keypair = (keypair[0], keypair[1])
    regle.escape = regle.getvar("escape")
    return True


def f_extractbloc(regle, obj):
    """#aide||extrait des blocs d un attribut texte
    #aide_spec||chaque bloc est identifie par une clef (regex avec un groupe de capture)
              ||et une paire de caracteres debut/fin ex <> ou () {}...
    #pattern1||A;?C;?A;extractbloc;re;C
    #pattern2||;?C;?A;extractbloc;re;C
    #parametre||attribut de sortie;defaut;liste_entree;;format
    #test1||obj||^X;1.534;;set||^Y;;N:X;format;%3.1f;||atv;Y;1.5
    #test2||obj||^X,A;1.534,B;;set||^Y;;N:X,A;format;%3.1f %s;||atv;Y;1.5 B
    """
    texte = regle.getval_entree(obj)
    # print("recherche blocs", regle.params.cmp1.val, regle.keypair)
    foundblocs = blocfilter(texte, regle.regex, regle.keypair, regle.escape)
    # print("trouve blocs", foundblocs)
    if regle.params.pattern == "1":
        obj.attributs[regle.params.att_sortie.val] = foundblocs
    elif regle.params.pattern == "2":
        tmp = obj.attributs[regle.params.val_entree.val] = ""
        if tmp:
            obj.attributs[regle.params.val_entree.val] = ""
        for clef, bloc in foundblocs.items():
            obj2 = obj.dupplique()
            obj2.attributs["#bloc"] = bloc
            obj2.attributs["#clef"] = clef
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
        obj.attributs[regle.params.val_entree.val] = tmp
    return bool(foundblocs)


def affiche_iterable(elem, n, clef=""):
    """affiche recursivement un iterable"""
    print("--" * n, " element", clef, ":", type(elem), elem)
    if isinstance(elem, dict):
        for nom, val in elem.items():
            affiche_iterable(val, n + 1, clef=nom)
    else:
        try:
            for i in elem:
                if isinstance(i, str):
                    print("--" * (n + 1), "str", i)
                else:
                    affiche_iterable(i, n + 1)
        except TypeError:
            return


def f_infoatt(regle, obj):
    """#aide||affiche des infos sur un attribut
    #aide_spec||donne recursivement les types d un attribut compexe
    #pattern1||;;A;infoatt;;"""
    att = obj.attributs[regle.params.att_entree.val]
    print("analyse attribut", regle.params.att_entree.val)
    print("type brut ", type(att))
    if isinstance(att, str):
        return True
    affiche_iterable(att, 0)
    return True


def txtstruct(elem):
    """convertit recursivement un iterable en texte"""
    if isinstance(elem, dict):
        return {nom: txtstruct(val) for nom, val in elem.items()}
    if isinstance(elem, tuple):
        return tuple(txtstruct(val) for val in elem)
    else:
        try:
            return [txtstruct(val) for val in elem]
        except:
            return repr(elem)


def f_txtstruct(regle, obj):
    """#aide||transforme un objet complexe contenu dans un attribut en structures de texte
    #aide_spec||attention mode rantanplan : fait ce qu il peut basé sur la fonction repr
    #aide_spec||gere les dictionnaires et les iterables imbriques
    #pattern1||A;;A;txtstruct;;
    #"""
    att = obj.attributs.get(regle.params.att_entree.val)
    print(" restructuration de l objet", type(att))
    if isinstance(att, str):
        return True
    sortie = txtstruct(att)
    print(" restructuration de l objet", type(att), "->", type(sortie))
    obj.attributs[regle.params.att_sortie.val] = sortie
    return True


def f_json(regle, obj):
    """#aide||transforme un objet complexe contenu dans un attribut en texte json
    #aide_spec||attention mode rantanplan : fait ce qu il peut basé sur la fonction repr
    #aide_spec||gere les dictionnaires et les iterables imbriques
    #pattern1||A;;A;json;;
    #"""
    obj.attributs[regle.params.att_sortie.val] = json.dumps(regle.getval_entree(obj))
