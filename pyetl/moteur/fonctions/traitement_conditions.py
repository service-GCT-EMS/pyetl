# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions s de selections : determine si une regle est eligible ou pas
"""
import re
import itertools
import time
import os
from .outils import prepare_mode_in

# ------------conditions sur valeurs d'attributs---------------------


def sel_attexiste(condition, obj):
    """#aide||teste si un attribut existe
    #pattern||A;||50
       #test||obj||^?Z;0;;set||Z;!;;;res;1;;set||atv;res;1
    """
    return condition.params.attr.val in obj.attributs


def selh_attexiste_re(condition):
    """ compile les expressions regulieres"""
    #    print (" dans helper regex",condition.params.vals.val)
    condition.fselect = re.compile(condition.params.attr.val).search


def sel_attexiste_re(condition, obj):
    """#aide||teste si un attribut existe
    #pattern||re:re;||50
       #test||obj||^?Z;0;;set||Z;!;;;res;1;;set||atv;res;1
    """
    result = sorted([i for i in obj.attributs if condition.fselect(i)])
    condition.regle.match = result[0] if result else ""
    condition.regle.matchlist = result if result else []
    return condition.regle.match


def selh_regex(condition):
    """ compile lesexpressions regulieres"""
    # print (" dans helper regex",condition.params.vals.val,re.compile(condition.params.vals.val))
    try:
        condition.fselect = re.compile(condition.params.vals.val).search
    except re.error:
        condition.regle.stock_param.logger.error(
            "expression regulière erronée %s %s", repr(condition), repr(condition.regle)
        )
        # print("expression condition erronee", condition, condition.regle)


def sel_egal(condition, obj):
    """#aide||selection sur la valeur d un attribut egalite stricte
    #pattern||A;=:||1
    #test||obj||^A;1;;set||^?A;0;;set||A;=:1;;;res;1;;set||atv;res;1
    """
    # print ("condition egal",condition.params.vals.val)
    return condition.params.vals.val == obj.attributs.get(condition.params.attr.val)


def sel_regex(condition, obj):
    """#aide||selection sur la valeur d un attribut
    #pattern||A;re||99
    #pattern2||A;re:re||1
    #test||obj||^A;1;;set||^?A;0;;set||A;1;;;res;1;;set||atv;res;1
    #test2||obj||^A;uv:xy;;set||^?A;0;;set||A;re:uv;;;res;1;;set||atv;res;1
    """
    # print ("------------------- test variable",obj.attributs.get(condition.params.attr.val, ""))
    result = condition.fselect(obj.attributs.get(condition.params.attr.val, ""))
    condition.regle.match = result.group(0) if result else ""
    condition.regle.matchlist = result.groups() if result else []
    return result


def selh_calc(condition):
    """prepare les expressions pour le calcul """

    attribut = condition.params.attr.val
    valeurs = condition.params.vals.val

    exp_final = re.sub("^ *N:(?!#?[A-Za-z])", "N:" + attribut, valeurs)
    exp_final = re.sub("^ *C:(?!#?[A-Za-z])", "C:" + attribut, exp_final)

    # print("exp test final", exp_final, attribut, valeurs)
    condition.fselect = condition.params.compilefonc(
        exp_final, "obj", debug=condition.regle.debug
    )


def sel_calc(condition, obj):
    """#aide||evaluation d une expression avec un attribut
    #pattern||A;NC2:||50
    #test||obj||^A;5;;set||^?A;0;;set||A;N: >2;;;res;1;;set||atv;res;1
    #test2||obj||^A;5;;set||^?A;0;;set||A;C: in "3456";;;res;1;;set||atv;res;1
    """
    result = condition.fselect(obj)
    condition.regle.match = result if result else ""
    return condition.fselect(obj)


def selh_calc2(condition):
    """prepare les expressions pour le calcul """
    valeurs = condition.params.vals.val
    condition.fselect = condition.params.compilefonc(
        valeurs, "obj", debug=condition.regle.debug
    )


def sel_calc2(condition, obj):
    """#aide||evaluation d une expression libre
    #pattern||;NC:||50
    #test||obj||^A,B;5,2;;set||^?A;0;;set||;N:A>N:B;;;res;1;;set||atv;res;1

    """
    result = condition.fselect(obj)
    condition.regle.match = result if result else ""
    return condition.fselect(obj)


def selh_infich(condition):
    """precharge le fichier"""
    # ("infich", condition.regle, len(condition.params.attr.liste), condition.params)
    mode, valeurs = prepare_mode_in(
        condition.params.vals.val,
        condition.regle,
        taille=len(condition.params.attr.liste),
    )
    # print("recup_condition", mode, valeurs)
    if mode == "in_s":
        condition.dyn = False
        if valeurs:
            taille_id = max([len(i[0].split(".")) for i in valeurs])
            condition.info = set(i[0] for i in valeurs)
            condition.taille = taille_id
        else:
            condition.info = {}
            condition.taille = 0
    else:
        condition.dyn = True


#    print ('condition liste fich charge ',condition.info)


def sel_vinfich(condition, obj):
    """#aide||valeur dans un fichier
    #aide_spec||il est possible de preciser des positions a lire dans le ficher
             +||en mettant les positions entre a,b;in:nom,1,3
       #helper||infich
      #pattern||A;in:fich||20
         #test||obj;||^A;B;;set||^?A;xxx;;set||
             +||A;in:%testrep%/refdata/liste.csv;;;res;1;;set||atv;res;1
    """
    if condition.dyn:  # mode dynamique
        pass
    else:
        condition.regle.match = obj.attributs.get(condition.params.attr.val, "")
        if condition.regle.match in condition.info:
            return True
        condition.regle.match = ""
        return False


def selh_infich_re(condition):
    """precharge le fichier"""
    #    print ('infich', len(condition.params.attr.liste),condition.params)
    _, valeurs = prepare_mode_in(
        condition.params.vals.val,
        condition.regle,
        taille=len(condition.params.attr.liste),
    )
    # on recupere les complements s'il y en a

    pref, suf = condition.params.vals.definition[0].split(":F:")
    # print(
    #     "-------------------------------in fich_re",
    #     condition.params.vals.definition,
    #     pref,
    #     suf,
    #     valeurs,
    # )

    if isinstance(valeurs, list):
        valeurs = set(valeurs)
    condition.info = [re.compile(pref + i[0] + suf) for i in valeurs]
    # TODO gerer correctement les listes


#    print ('condition infichre fich charge ',condition.info)


def sel_infich_re(condition, obj):
    """#aide||valeur dans un fichier sous forme d'expressions regulieres
    #aide_spec||il est possible de preciser des positions a lire dans le ficher
             +||en mettant les positions separees par des ,ex : a,b;in:nom,1,3
             +||il est possible d'ajouter des prefixes et des suffies aux expressions du fichier
             +||en mettant (pref:F:suff) à la fin de l'expression
             +||ex: ^:F:.* permet de matcher tout ce qui commence par une ligne du fichier
      #pattern||L;in:fich(re)||20
         #test||obj||^A;AA;;set||^?A;xxx;;set||A;in:%testrep%/refdata/liste.csv(^:F:.);;;res;1;;set
              ||atv;res;1
    """
    if len(condition.params.attr.liste) > 1:
        vals = ";".join(obj.attributs.get(i, "") for i in condition.params.attr.liste)
    else:
        vals = obj.attributs.get(condition.params.attr.val, "")
    for i in itertools.dropwhile(lambda i: not i.search(vals), condition.info):
        condition.regle.match = i.search(vals).group(0)
        condition.regle.matchlist = i.search(vals).groups()

        return True
    print("infich_re: no match", vals)
    condition.regle.match = ""
    return False
    # return any((i.search(vals) for i in condition.info))


def selh_inlist(condition):
    """stocke la liste"""
    condition.info = set(condition.params.vals.liste)


#    print ("inlist", condition.regle.numero, condition.comparaison)


def sel_inlist(condition, obj):
    """#aide||valeur dans une liste
    #pattern||A;in:list||10
    #test||obj||^A;3;;set||^?A;0;;set||A;in:{1,2,3,4};;;res;1;;set;;;||atv;res;1
    """
    val = obj.attributs.get(condition.params.attr.val, "")
    if val in condition.info:
        condition.regle.match = val
        return True
    condition.regle.match = ""
    return False


def selh_inlist_re(condition):
    """precharge le fichier"""
    #    print ('infich', len(condition.params.attr.liste),condition.params)
    valeurs = set(condition.params.vals.liste)
    pref, suf = condition.params.vals.definition[0].split(":F:")
    #    print ('-------------------------------in fich_re',condition.params.vals.definition, pref,suf)
    condition.info = [re.compile(pref + i + suf) for i in valeurs]


#    print ('condition infichre fich charge ',condition.info)


def sel_inlist_re(condition, obj):
    """#aide||valeur dans une liste sous forme d'expressions regulieres
    #aide_spec||il est possible d'ajouter des prefixes et des suffies aux expressions de la liste
             +||en mettant (pref:F:suff) à la fin de l'expression
             +||ex: ^:F:.* permet de matcher tout ce qui commence par un element de la liste
      #pattern||L;in:list(re)||20
         #test||obj||^A;AA;;set||^?A;xxx;;set||A;in:{A,y,z}(^:F:.);;;res;1;;set||atv;res;1
    """
    if len(condition.params.attr.liste) > 1:
        vals = ";".join(obj.attributs.get(i, "") for i in condition.params.attr.liste)
    else:
        vals = obj.attributs.get(condition.params.attr.val, "")
    #    print ('sel _inlist_re ', vals, condition.info)
    # return any((i.search(vals) for i in condition.info))
    for i in itertools.dropwhile(lambda i: not i.search(vals), condition.info):
        condition.regle.match = i.search(vals).group(0)
        condition.regle.matchlist = i.search(vals).groups()

        return True
    condition.regle.match = ""
    return False


def selh_inmem(condition):
    """stocke la liste"""
    condition.info = None
    condition.precedent = None
    condition.geom = "#geom" in condition.params.attr.liste
    if condition.geom:
        condition.params.attr.liste.remove("#geom")


#    print ("inlist", condition.regle.numero, condition.comparaison)


def sel_inmem(condition, obj):
    """#aide||valeur dans une liste en memoire (chargee par preload)
    #pattern||L;in:mem||10
    #!test||obj||^A;3;;set||^?A;0;;set||A;in:{1,2,3,4};;;res;1;;set;;;||atv;res;1
    """
    if condition.precedent != obj.ident:  # on vient de changer de classe
        condition.info = condition.regle.stock_param.store[condition.params.vals.val]
        condition.precedent = obj.ident
        # print("comparaison ", condition.params.vals.val, len(condition.info))
    if condition.info is None:
        condition.regle.match = ""
        return False

    clef = str(tuple(tuple(i) for i in obj.geom_v.coords)) if condition.geom else ""
    clef = clef + "|".join(
        obj.attributs.get(i, "") for i in condition.params.attr.liste
    )

    if clef in condition.info:
        condition.regle.match = clef
        return True
    condition.regle.match = ""
    return False


def sel_changed(condition, obj):
    """#aide||vrai si l'attribut a change d'un objet au suivant
    #pattern||A;=<>:||1
       #test||obj;;2||^A;;;cnt;1;0||^?A;0;;set||A;<>:;;;res;1;;set||V0;0;;;;;;supp||atv;res;1
    """
    if condition.info != obj.attributs.get(condition.params.attr.val, ""):
        condition.info = obj.attributs.get(condition.params.attr.val, "")
        condition.regle.match = condition.info
        return True
    return False


def sel_ispk(condition, obj):
    """#aide||vrai si l'attribut est une clef primaire
     #pattern||A;=is:pk||1
    #pattern2||A;=is:PK||1
        #test||obj||^Z(E,PK);1;;set||^?pk;;;set_schema||Z;is:pk;;;res;1;;set||atv;res;1
    """

    #        le test est fait sur le premier objet de  la classe qui arrive
    #        et on stocke le resultat : pur eviter que des modifs ulterieures de
    #        schema ne faussent les tests'''
    if not obj.schema:
        return False
    clef = obj.ident + (condition.params.attr.val,)
    if clef not in condition.info:
        condition.info[clef] = obj.schema.getpkey == condition.params.attr.val
    return condition.info[clef]


def sel_isnull(condition, obj):
    """#aide||vrai si l'attribut existe et est null
    #pattern||A;=is:null||1
    #pattern2||A;=is:NULL||1
    #test||obj||^A;;;set||^?A;1;;set||A;is:null;;;res;1;;set||atv;res;1
    """
    return not obj.attributs.get(condition.params.attr.val, "1")


def sel_isnotnull(condition, obj):
    """#aide||vrai si l'attribut existe et n est pas nul
    #pattern||A;=is:not_null||1
    #pattern2||A;=is:NOT_NULL||1
    #test||obj||^A;1;;set||^?A;;;set||A;is:not_null;;;res;1;;set||atv;res;1
    """
    return obj.attributs.get(condition.params.attr.val, "")


# fonctions de selections dans un hstore


def sel_hselk(condition, obj):
    """#aide||selection si une clef de hstore existe
    #pattern||H:A;haskey:A||3
    #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;haskey:V0;;;res;1;;set||atv;res;1
    """
    att = condition.params.attr.val
    hdic = obj.gethdict(att)
    #    print (" test hstore",hdic,condition.params.vals.val)
    return condition.params.vals.val in hdic


def sel_hselv(condition, obj):
    """#aide||selection si une clef de hstore n'est pas vide
    #pattern||H:A;hasval:C||3
       #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;hasval:0;;;res;1;;set||atv;res;1

    """
    att = condition.params.attr.val
    hdic = obj.gethdict(att)
    return condition.params.vals.val in hdic.values()


def sel_hselvk(condition, obj):
    """#aide||selection sur une valeur d'un hstore
    #pattern||H:A;A:C||10
    #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;V0:0;;;res;1;;set||atv;res;1
    #!test||rien||H:AA;V0:0;;;res;1;;set||rien

    """
    att = condition.params.attr.val
    clef = condition.params.vals.val
    vals = condition.params.vals.definition[0]
    hdic = obj.gethdict(att)
    #    print ("test clef ",hdic,clef,vals)
    return hdic.get(clef) == vals


# -------------------conditions proprietes objet
# --------------------conditions sur identifiant-----------------------------


def sel_idregex(condition, obj):
    """#aide||vrai si l identifiant de classe verifie une expression
        #pattern||=ident:;re||10
        #helper||regex
    #test1||obj||^#groupe,#classe;e1,tt;;set||^?#groupe;e2;;set||ident:;e1;;;res;1;;set||atv;res;1
    """
    return condition.fselect(".".join(obj.ident))


def sel_idinfich(condition, obj):
    """#aide||vrai si l identifiant de classe est dans un fichier
        #pattern||=ident:;in:fich||1
        #helper||infich
    !test1||obj||^#groupe,#classe;e1,tt;;set||^?#groupe;e2;;set||ident:;e1;;;res;1;;set||atv;res;1
    """
    if condition.taille == 3 and "#codebase" in obj.attributs:  # on a ajoute la base
        return (
            obj.attributs.get("#codebase") + "." + ".".join(obj.ident) in condition.info
        )
    return ".".join(obj.ident) in condition.info


def sel_haspk(condition, obj):
    """#aide||vrai si on a defini un des attributs comme clef primaire
    #pattern||;=has:pk||1
    #pattern2||;=has:PK||1
    #test||obj||^A(E,PK);1;;set||^?pk;;;set_schema||;has:pk;;;res;1;;set||atv;res;1
    """
    #     le test est fait sur le premier objet de  la classe qui arrive
    #     et on stocke le resultat : pur eviter que des modifas ulterieures de
    #     schema ne faussent les tests'''
    clef = obj.ident
    if clef in condition.info:
        return condition.info[clef]

    condition.info[clef] = obj.schema and obj.schema.haspkey
    #    print ("pk ",obj.schema.haspkey, obj.schema.indexes)
    return condition.info[clef]


# ------------------------conditions sur parametres--------------------------


def sel_pexiste(condition, _):
    """#aide||teste si un parametre est non vide
    #pattern||P;||50
      #test1||obj||^?P:AA;1;;set||P:AA;!;;;res;1;;set||atv;res;1
    """
    # print ('---------------------------test Pexiste',
    #         condition.params.attr.val,'->',
    #         condition.regle.getvar(condition.params.attr.val),'<-',
    #         bool(condition.regle.getvar(condition.params.attr.val)))

    var = str(condition.regle.getvar(condition.params.attr.val))
    return var and var.lower() not in {"", "0", "f", "false"}


def sel_pregex(condition, _):
    """#aide||teste la valeur d un parametre
     #helper||regex
    #pattern||P;re||100
      #test1||obj||^P:AA;1;;set||^?P:AA;0;;set||P:AA;1;;;res;1;;set||atv;res;1
    """
    # print ('------------------------------pregex',condition.params.attr.val,'->',condition.regle.getvar(condition.params.attr.val))
    return condition.fselect(condition.regle.getvar(condition.params.attr.val))


def selh_constante(condition):
    """ mets en place le condition de constante """
    condition.static = True
    if condition.neg:
        condition.initval = condition.params.attr.val != condition.params.vals.val[1:]
    else:
        condition.initval = condition.params.attr.val == condition.params.vals.val


def sel_constante(condition, *_):
    """#aide||egalite de constantes sert a customiser des scripts
    #pattern||C:C;C||50
    #test||obj||C:1;1;;;res;1;;set||?C:1;!2;;;res;0;;set||atv;res;1
    """
    return condition.initval


def selh_cexiste(condition):
    """ mets en place le condition de constante """
    condition.static = True
    if condition.neg:
        condition.initval = not bool(condition.params.attr.val)
    else:
        condition.initval = bool(condition.params.attr.val)


def sel_cexiste(condition, *_):
    """#aide|| existance de constantes sert a customiser des scripts
    #pattern||C:C;||50
    #test||obj||C:1;;;;res;1;;set||?C:;!;;;res;0;;set||atv;res;1
    """
    return condition.initval


# -----------conditions sur schema-------------------------


def sel_hasschema(_, obj):
    """#aide||objet possedant un schema
    #pattern||;=has:schema||1
    #pattern1||=has:schema||1
    #test||obj||^?#schema;;;supp;;;||;has:schema;;;res;1;;set||atv;res;1
    """
    return obj.schema


def selh_ininfoschema(condition):
    """test sur un parametre de schema : recupere le nom du parametre"""
    condition.info = condition.params.attr.val.split(":")[-1]


def sel_ininfoschema(condition, obj):
    """#aide||test sur un parametre de schema
    #pattern||=schema:(.*);||1
    #test||obj||;?schema:dim;;;res;1;;set||;schema:dom;;;res;0;;set||atv;res;1
    """
    return obj.schema and condition.info in obj.schema.info


def sel_inschema(condition, obj):
    """#aide||vrai si un attribut est defini dans le schema
    #pattern||A;=in:schema||1
    #pattern2||A;=in_schema||1
       #test||obj||^?C1;;;supp;;;||C1;in_schema;;;res;1;;set||atv;res;1
    """
    # print("sel inschema",obj.schema.attributs)
    return obj.schema and condition.params.attr.val in obj.schema.attributs


def sel_infoschema(condition, obj):
    """#aide||teste la valeur d un parametre de schema
     #helper||regex
    #pattern||schema:A;re||50
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom;3;;;X;1;;set;||atv;X;1;
    """
    return (
        condition.fselect(obj.schema.info.get(condition.params.attr.val, ""))
        if obj.schema
        else False
    )


def selh_infoschema_type(condition):
    """#initialise les caches"""
    condition.lastschema = None  # on mets en cache
    condition.lastvaleur = None


def sel_infoschema_has_type(condition, obj):
    """#aide||vrai si un attribut de type donne existe dans le schema de l'objet
     #helper||infoschema_type
    #pattern||schema:T:;||50
    #pattern2||;schema:T:;||50
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom;3;;;X;1;;set;||atv;X;1;
    """
    #    print ('dans sel_infoschema_has_type')
    if not obj.schema:
        return False
    if obj.schema.identclasse == condition.lastschema:
        return condition.lastvaleur
    atts = obj.schema.attributs
    val = (
        condition.params.attr.val
        if condition.params.attr.val
        else condition.params.vals.val
    )
    condition.lastschema = obj.schema.identclasse  # on mets en cache
    condition.lastvaleur = any([atts[i].type_att == val for i in atts])
    #    print ('sel info type',condition.lastschema, condition.lastvaleur, val,
    #           [atts[i].type_att for i in atts])
    return condition.lastvaleur


def sel_infoschema_is_type(condition, obj):
    """#aide||vrai si des attributs nommes sont de type dmand
    #pattern||L;schema:T:||50
     #helper||infoschema_type
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom;3;;;X;1;;set;||atv;X;1;
    """
    if not obj.schema:
        return False
    idschema = obj.schema.identclasse
    if idschema == condition.lastschema:
        return condition.lastvaleur
    atts = [i for i in obj.schema.attributs if i in condition.params.attr.liste]
    val = condition.params.val.val
    condition.lastschema = idschema  # on mets en cache
    condition.lastvaleur = any([atts[i].type_att == val for i in atts])
    return condition.lastvaleur


def sel_infoschema_egal(condition, obj):
    """#aide||test sur un parametre de schema
    #pattern||schema:A:;C||1
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom=;3;;;X;1;;set;||atv;X;1;
    """
    #    print('test ',condition.params.attr.val,'->',obj.schema.info.get(condition.params.attr.val),
    #          condition.params.vals.val)
    return obj.schema and (
        obj.schema.info.get(condition.params.attr.val) == condition.params.vals.val
    )


# --------------------conditions sur workflow------------------------------


def sel_isko(_, obj):
    """#aide||operation precedente en echec
    #pattern||;=is:ko||1
    #pattern2||;=is:KO||1
    #test||obj||^;;;fail||^?;;;pass||;is:ko;;;res;1;;set||atv;res;1
    """
    #    print (" attributs",condition,obj)
    return not obj.is_ok


def sel_isok(_, obj):
    """#aide||operation precedente correcte
    #pattern||;=is:ok||1
    #pattern2||;=is:OK||1
    #test||obj||^;;;pass||^?;;;fail||;is:ok;;;res;1;;set||atv;res;1
    """
    #    print (" attributs",condition,obj)
    return obj.is_ok


def sel_isvirtuel(_, obj):
    """#aide||objet virtuel
    #pattern||;=is:virtuel||1
    #pattern2||=is:virtuel;||1
    #test||obj||^;;;virtuel||^?;;;reel||;is:virtuel;;;C1;1;;set||^;;;reel||atv;C1;1

    """
    return obj.virtuel


def sel_isreel(_, obj):
    """#aide||objet virtuel
    #pattern||;=is:reel||1
    #pattern2||=is:reel;||1
    #test||obj||^?;;;virtuel||;is:reel;;;C1;1;;set||^;;;reel||atv;C1;1

    """
    return not obj.virtuel


# --------------------conditions geometriques-------------------------------


def sel_hasgeomv(_, obj):
    """#aide||vrai si l'objet a une geometrique en format interne
    #pattern||;=has:geomV||1
    #pattern1||=has:geomV||1
    #test||obj;point;1||^;;;geom||^?;;;resetgeom||;has:geomV;;;res;1;;set||atv;res;1
    """
    #    print ("hasgeomv",condition,obj.geom_v)
    return obj.geom_v.valide or obj.geom_v.sgeom


def sel_hasgeom(_, obj):
    """#aide||vrai si l'objet a un attribut geometrique natif
    #pattern||;=has:geom||1
    #pattern1||=has:geom||1
    #test||obj;asc;1||^;;;geom||^?#geom;;;supp||;has:geom;;;res;1;;set||atv;res;1
    """
    return bool(obj.attributs.get("#geom"))


def sel_hascouleur(condition, obj):
    """#aide||objet possedant un schema
    #pattern||=has:couleur;C||1
    #test||obj;asc_c;1||^;;;geom;||^?#geom;;;supp||has:couleur;2;;;res;1;;set;;||atv;res;1
    #test2||obj;asc_c;1||^;;;geom;||^res;0;;set||?has:couleur;!3;;;res;1;;set;;||atv;res;0
    """
    return obj.geom_v.has_couleur(condition.params.vals.val)


def sel_is2d(_, obj):
    """#aide||vrai si l'objet est de dimension 2
    #pattern||;=is:2d||1
    #pattern2||;=is:2D||1
    #test||obj;point;1||^?;1;;geom3D||;is:2d;;;res;1;;set||atv;res;1
    """
    return obj.dimension == 2


def sel_is3d(_, obj):
    """#aide||vrai si l'objet est de dimension 3
    #pattern||;=is:3d||1
    #pattern2||;=is:3D||1
    #test||obj;point;1||^;1;;geom3D||^?;;;geom2D||;is:3d;;;res;1;;set||atv;res;1
    """
    #        print ('conditions: dans virtuel :', obj.ident,obj.virtuel)
    return obj.dimension == 3


def sel_is_type_geom(condition, obj):
    """#aide||vrai si l'objet est de dimension 3
    #pattern||=type_geom:;N||1
    #test||obj;point;1||^;1;;geom3D||^?;;;geom2D||;is:3d;;;res;1;;set||atv;res;1
    """
    #        print ('conditions: dans virtuel :', obj.ident,obj.virtuel)
    return obj.geom_v.type == condition.params.vals.val


def sel_isfile(condition, obj):
    """#aide||teste si un fichier existe
    #pattern1||=is:file;[A]||1
    #pattern2||=is:file;C||1
    #test||obj||is:file;%testrep%/refdata/liste.csv;;;C1;1;;set||?is:file;!%testrep%/refdata;;;C1;0;;set||atv;C1;1
    """
    if condition.params.pattern == "2":
        # print(
        #     "isfile",
        #     condition.params.vals.val,
        #     os.path.isfile(condition.params.vals.val),
        # )
        return os.path.isfile(condition.params.vals.val)
    else:
        return (
            os.path.isfile(obj.attributs.get(condition.params.vals.val))
            if obj is not None
            else None
        )


def sel_isdir(condition, obj):
    """#aide||teste si un repertoire existe
    #pattern1||=is:dir;[A]||1
    #pattern2||=is:dir;C||1
    #test||obj||is:dir;%testrep%/refdata;;;C1;1;;set||?is:dir;!%testrep%/dudule;;;C1;0;;set||atv;C1;1
    """
    if condition.params.pattern == "2":
        return os.path.isdir(condition.params.vals.val)
    else:
        return (
            os.path.isdir(obj.attributs.get(condition.params.vals.val))
            if obj is not None
            else None
        )


def selh_is_date(condition):
    """prepare les conditions"""
    condition.vref = "O" if condition.params.pattern in "23" else "T"


def sel_is_date(condition, obj):
    """#aide||vrai si la date est compatible avec la description ( sert dans les declecnheurs de batch)
    #aide_spec||format de date: (liste de jours)/intervalle
              ||ex:  rien : tous les jour
              ||      /2J :  tous les 2 jours
              ||   1,3/S  :  lundi et mercredi toutes les semaines
              ||   1-5/S  :  lundi au vendredi toutes les semaines
              ||     7/2S :  dimanche toutes les 2 semaines
              ||     7/M  :  premier dimanche du mois
              ||    07/M  :  jour 7 du mois
      #pattern0||=is:valid_date;C||2
      #pattern1||=is:valid_date;[A]||1
      #pattern2||(is:valid_date:)A;C||2
      #pattern3||(is:valid_date:)A;[A]||1
      #test||obj;point;1||^X;2005-11-10;;set||^?X;2005-11-11;;set||^Y;2;;set;
           ||is:valid_date:X;/2J;;;Y;1;;set||atv;Y;1
    """
    # print ("comparaison temps", condition.params.pattern)
    if condition.params.pattern == "1" or condition.params.pattern == "3":
        dateref = obj.attributs.get(condition.params.vals.val, "X")
    else:
        dateref = condition.params.vals.val
    if condition.vref == "O":  # temps de reference pris dans l objet: faux si invalide
        datedesc = obj.attributs.get(condition.params.attr.val)
        try:
            date = time.strptime(datedesc, "%Y-%m-%d")
        except ValueError:
            return False
    else:
        date = time.localtime()  # temps de reference = jour courant
    # print ("comparaison temps", date, dateref,condition.params.pattern)

    if dateref == "X":
        return False
    if dateref == "":
        # print ('toujours')
        return True
    tmp = dateref.split("/")
    if len(tmp) != 2:
        return False
    jours, intervalle = tmp
    if "," in jours:
        lj = jours.split(",")
    elif "-" in jours:
        debut, fin = jours.split("-")
        lj = list(range(int(debut), int(fin) + 1))
    else:
        lj = [jours]
    wn = int(time.strftime("%W", date))
    if "J" in intervalle:
        intdef = int(intervalle.replace("J", ""))
        vdef = int(jours) if jours else 0

        return date.tm_yday % intdef == vdef
    if intervalle == "S":  # toutes les semaines
        return str(date.tm_wday + 1) in lj
    if "S" in intervalle:
        intdef = int(intervalle.replace("S", ""))
        if wn % intdef:
            return False
        return str(date.tm_wday + 1) in lj
    if intervalle == "M":  # tous les mois
        if "%2.2d" % (date.tm_mday) in lj:
            return True
        if date.tm_mday < 8 and str(date.tm_wday) in lj:
            return True
        return False
    if "M" in intervalle:
        intdef = int(intervalle.replace("M"))
        if date.tm_mon % intdef != 1:
            return False
        if "%2.2d" % (date.tm_mday) in lj:
            return True
        if date.tm_mday < 8 and str(date.tm_wday) in lj:
            return True
        return False


def selh_is_time(condition):
    """prepare les conditions"""
    condition.vref = "O" if condition.params.pattern in "23" else "T"
    if not condition.params.pattern or condition.params.pattern == "2":
        pass


def sel_is_time(condition, obj):
    """#aide||vrai si l'heure est compatible avec la description ( sert dans les declencheurs de batch)
    #aide_spec||format de temps: (liste de jours)/intervalle
              ||ex:  rien : tout le temps
              ||      /2m :  tous les 2 minutes
              ||   1,15/1H  :  minutes 1 et 15 toutes les heures
              ||     7/2H :  minute 7 toutes les 2 heures
              ||     7/2H[8-18] :  minute 7 toutes les 2 heures de 8h a 18h
      #pattern0||=is:valid_time;C||2
      #pattern1||=is:valid_time;[A]||1
      #pattern2||(is:valid_time:)A;C||1
      #pattern3||(is:valid_time:)A;[A]||2
      #test||obj;point;1||^X;12:32:10;;set||^?X;12:31:10;;set||^Y;2;;set;
           ||is:valid_time:X;/2m;;;Y;1;;set||atv;Y;1
    """
    # print ("================================patern ref",condition.pattern)
    if condition.params.pattern == "1" or condition.params.pattern == "3":
        timeref = obj.attributs.get(condition.params.vals.val, "X")
    else:
        timeref = condition.params.vals.val
    if condition.vref == "O":  # temps pris dans l objet
        temps = obj.attributs.get(condition.params.attr.val)
        heures, minutes, *_ = temps.split(":")
        heures = int(heures)
        minutes = int(minutes)
    else:
        temps = time.localtime()
        heures = temps.tm_hour
        minutes = temps.tm_min

    # print(
    #     "comparaison temps",
    #     heures,
    #     minutes,
    #     timeref,
    #     condition.params.vals.val,
    #     condition.params.pattern,
    # )

    if timeref == "X":
        return False
    if timeref == "":
        return True
    tmp = timeref.split("/")
    if len(tmp) != 2:
        return False
    decalage, intervalle = tmp
    if not decalage:
        decalage = "0"
    lastsel = obj.attributs.get("#_lastsel")
    if lastsel and lastsel.isnumeric():
        lastseln = int(lastsel)
    else:
        lastseln = -1
    if "[" in intervalle:
        debut, fin = intervalle.split("[")[1][:-1].split("-")
        intervalle = intervalle.split("[")[0]
    else:
        debut, fin = (-1, 25)

    if debut > heures or fin < heures:
        return False
    if "m" in intervalle:
        mdef = intervalle.replace("m", "")
        intdef = int(mdef) if mdef.isnumeric() else 1
        min_interv = minutes % intdef
    elif "H" in intervalle:
        hdef = intervalle.replace("H", "")
        intdef = int(hdef) if hdef.isnumeric() else 1
        min_interv = minutes + (heures % intdef) * 60
    else:
        return False
    # print("intervalle minutes", minutes, lastseln, decalage)
    if minutes == lastseln:  # on a deja selectionne
        return False
    if str(min_interv) in decalage.split(","):
        obj.attributs["#_lastsel"] = str(minutes)
        return True
