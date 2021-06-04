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

# ------------selecteurs sur valeurs d'attributs---------------------


def sel_attexiste(selecteur, obj):
    """#aide||teste si un attribut existe
    #pattern||A;||50
       #test||obj||^?Z;0;;set||Z;!;;;res;1;;set||atv;res;1
    """
    return selecteur.params.attr.val in obj.attributs


def selh_attexiste_re(selecteur):
    """ compile les expressions regulieres"""
    #    print (" dans helper regex",selecteur.params.vals.val)
    selecteur.fselect = re.compile(selecteur.params.attr.val).search


def sel_attexiste_re(selecteur, obj):
    """#aide||teste si un attribut existe
    #pattern||re:re;||50
       #test||obj||^?Z;0;;set||Z;!;;;res;1;;set||atv;res;1
    """
    result = sorted([i for i in obj.attributs if selecteur.fselect(i)])
    selecteur.regle.match = result[0] if result else ""
    selecteur.regle.matchlist = result if result else []
    return selecteur.regle.match


def selh_regex(selecteur):
    """ compile lesexpressions regulieres"""
    # print (" dans helper regex",selecteur.params.vals.val,re.compile(selecteur.params.vals.val))
    try:
        selecteur.fselect = re.compile(selecteur.params.vals.val).search
    except re.error:
        selecteur.regle.stock_param.logger.error(
            "expression regulière erronée %s %s", repr(selecteur), repr(selecteur.regle)
        )
        # print("expression selecteur erronee", selecteur, selecteur.regle)


def sel_egal(selecteur, obj):
    """#aide||selection sur la valeur d un attribut egalite stricte
    #pattern||A;=:||1
    #test||obj||^A;1;;set||^?A;0;;set||A;=:1;;;res;1;;set||atv;res;1
    """
    # print ("selecteur egal",selecteur.params.vals.val)
    return selecteur.params.vals.val == obj.attributs.get(selecteur.params.attr.val)


def sel_regex(selecteur, obj):
    """#aide||selection sur la valeur d un attribut
    #pattern||A;re||99
    #pattern2||A;re:re||1
    #test||obj||^A;1;;set||^?A;0;;set||A;1;;;res;1;;set||atv;res;1
    #test2||obj||^A;uv:xy;;set||^?A;0;;set||A;re:uv;;;res;1;;set||atv;res;1
    """
    # print ("------------------- test variable",obj.attributs.get(selecteur.params.attr.val, ""))
    result = selecteur.fselect(obj.attributs.get(selecteur.params.attr.val, ""))
    selecteur.regle.match = result.group(0) if result else ""
    selecteur.regle.matchlist = result.groups() if result else []
    return result


def selh_calc(selecteur):
    """prepare les expressions pour le calcul """

    attribut = selecteur.params.attr.val
    valeurs = selecteur.params.vals.val

    exp_final = re.sub("^ *N:(?!#?[A-Za-z])", "N:" + attribut, valeurs)
    exp_final = re.sub("^ *C:(?!#?[A-Za-z])", "C:" + attribut, exp_final)

    # print("exp test final", exp_final, attribut, valeurs)
    selecteur.fselect = selecteur.params.compilefonc(
        exp_final, "obj", debug=selecteur.regle.debug
    )


def sel_calc(selecteur, obj):
    """#aide||evaluation d une expression avec un attribut
    #pattern||A;NC2:||50
    #test||obj||^A;5;;set||^?A;0;;set||A;N: >2;;;res;1;;set||atv;res;1
    #test2||obj||^A;5;;set||^?A;0;;set||A;C: in "3456";;;res;1;;set||atv;res;1
    """
    result = selecteur.fselect(obj)
    selecteur.regle.match = result if result else ""
    return selecteur.fselect(obj)


def selh_calc2(selecteur):
    """prepare les expressions pour le calcul """
    valeurs = selecteur.params.vals.val
    selecteur.fselect = selecteur.params.compilefonc(
        valeurs, "obj", debug=selecteur.regle.debug
    )


def sel_calc2(selecteur, obj):
    """#aide||evaluation d une expression libre
    #pattern||;NC:||50
    #test||obj||^A,B;5,2;;set||^?A;0;;set||;N:A>N:B;;;res;1;;set||atv;res;1

    """
    result = selecteur.fselect(obj)
    selecteur.regle.match = result if result else ""
    return selecteur.fselect(obj)


def selh_infich(selecteur):
    """precharge le fichier"""
    # ("infich", selecteur.regle, len(selecteur.params.attr.liste), selecteur.params)
    mode, valeurs = prepare_mode_in(
        selecteur.params.vals.val,
        selecteur.regle,
        taille=len(selecteur.params.attr.liste),
    )
    # print("recup_selecteur", mode, valeurs)
    if mode == "in_s":
        selecteur.dyn = False
        if valeurs:
            taille_id = max([len(i[0].split(".")) for i in valeurs])
            selecteur.info = set(i[0] for i in valeurs)
            selecteur.taille = taille_id
        else:
            selecteur.info = {}
            selecteur.taille = 0
    else:
        selecteur.dyn = True


#    print ('selecteur liste fich charge ',selecteur.info)


def sel_vinfich(selecteur, obj):
    """#aide||valeur dans un fichier
    #aide_spec||il est possible de preciser des positions a lire dans le ficher
             +||en mettant les positions entre a,b;in:nom,1,3
       #helper||infich
      #pattern||A;in:fich||20
         #test||obj;||^A;B;;set||^?A;xxx;;set||
             +||A;in:%testrep%/refdata/liste.csv;;;res;1;;set||atv;res;1
    """
    if selecteur.dyn:  # mode dynamique
        pass
    else:
        selecteur.regle.match = obj.attributs.get(selecteur.params.attr.val, "")
        if selecteur.regle.match in selecteur.info:
            return True
        selecteur.regle.match = ""
        return False


def selh_infich_re(selecteur):
    """precharge le fichier"""
    #    print ('infich', len(selecteur.params.attr.liste),selecteur.params)
    _, valeurs = prepare_mode_in(
        selecteur.params.vals.val,
        selecteur.regle,
        taille=len(selecteur.params.attr.liste),
    )
    # on recupere les complements s'il y en a

    pref, suf = selecteur.params.vals.definition[0].split(":F:")
    # print(
    #     "-------------------------------in fich_re",
    #     selecteur.params.vals.definition,
    #     pref,
    #     suf,
    #     valeurs,
    # )

    if isinstance(valeurs, list):
        valeurs = set(valeurs)
    selecteur.info = [re.compile(pref + i[0] + suf) for i in valeurs]
    # TODO gerer correctement les listes


#    print ('selecteur infichre fich charge ',selecteur.info)


def sel_infich_re(selecteur, obj):
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
    if len(selecteur.params.attr.liste) > 1:
        vals = ";".join(obj.attributs.get(i, "") for i in selecteur.params.attr.liste)
    else:
        vals = obj.attributs.get(selecteur.params.attr.val, "")
    for i in itertools.dropwhile(lambda i: not i.search(vals), selecteur.info):
        selecteur.regle.match = i.search(vals).group(0)
        selecteur.regle.matchlist = i.search(vals).groups()

        return True
    selecteur.regle.match = ""
    return False
    # return any((i.search(vals) for i in selecteur.info))


def selh_inlist(selecteur):
    """stocke la liste"""
    selecteur.info = set(selecteur.params.vals.liste)


#    print ("inlist", selecteur.regle.numero, selecteur.comparaison)


def sel_inlist(selecteur, obj):
    """#aide||valeur dans une liste
    #pattern||A;in:list||10
    #test||obj||^A;3;;set||^?A;0;;set||A;in:{1,2,3,4};;;res;1;;set;;;||atv;res;1
    """
    val = obj.attributs.get(selecteur.params.attr.val, "")
    if val in selecteur.info:
        selecteur.regle.match = val
        return True
    selecteur.regle.match = ""
    return False


def selh_inlist_re(selecteur):
    """precharge le fichier"""
    #    print ('infich', len(selecteur.params.attr.liste),selecteur.params)
    valeurs = set(selecteur.params.vals.liste)
    pref, suf = selecteur.params.vals.definition[0].split(":F:")
    #    print ('-------------------------------in fich_re',selecteur.params.vals.definition, pref,suf)
    selecteur.info = [re.compile(pref + i + suf) for i in valeurs]


#    print ('selecteur infichre fich charge ',selecteur.info)


def sel_inlist_re(selecteur, obj):
    """#aide||valeur dans une liste sous forme d'expressions regulieres
    #aide_spec||il est possible d'ajouter des prefixes et des suffies aux expressions de la liste
             +||en mettant (pref:F:suff) à la fin de l'expression
             +||ex: ^:F:.* permet de matcher tout ce qui commence par un element de la liste
      #pattern||L;in:list(re)||20
         #test||obj||^A;AA;;set||^?A;xxx;;set||A;in:{A,y,z}(^:F:.);;;res;1;;set||atv;res;1
    """
    if len(selecteur.params.attr.liste) > 1:
        vals = ";".join(obj.attributs.get(i, "") for i in selecteur.params.attr.liste)
    else:
        vals = obj.attributs.get(selecteur.params.attr.val, "")
    #    print ('sel _inlist_re ', vals, selecteur.info)
    # return any((i.search(vals) for i in selecteur.info))
    for i in itertools.dropwhile(lambda i: not i.search(vals), selecteur.info):
        selecteur.regle.match = i.search(vals).group(0)
        selecteur.regle.matchlist = i.search(vals).groups()

        return True
    selecteur.regle.match = ""
    return False


def selh_inmem(selecteur):
    """stocke la liste"""
    selecteur.info = None
    selecteur.precedent = None
    selecteur.geom = "#geom" in selecteur.params.attr.liste
    if selecteur.geom:
        selecteur.params.attr.liste.remove("#geom")


#    print ("inlist", selecteur.regle.numero, selecteur.comparaison)


def sel_inmem(selecteur, obj):
    """#aide||valeur dans une liste en memoire (chargee par preload)
    #pattern||A;in:mem||10
    #!test||obj||^A;3;;set||^?A;0;;set||A;in:{1,2,3,4};;;res;1;;set;;;||atv;res;1
    """
    if selecteur.precedent != obj.ident:  # on vient de changer de classe
        selecteur.info = selecteur.regle.stock_param.store[selecteur.params.vals.val]
        selecteur.precedent = obj.ident
    #    print ('comparaison ', len(regle.comp), regle.comp)
    if selecteur.info is None:
        selecteur.regle.match = ""
        return False

    clef = str(tuple(tuple(i) for i in obj.geom_v.coords)) if selecteur.geom else ""
    clef = clef + "|".join(
        obj.attributs.get(i, "") for i in selecteur.params.attr.liste
    )

    if clef in selecteur.info:
        selecteur.regle.match = clef
        return True
    selecteur.regle.match = ""
    return False


def sel_changed(selecteur, obj):
    """#aide||vrai si l'attribut a change d'un objet au suivant
    #pattern||A;=<>:||1
       #test||obj;;2||^A;;;cnt;1;0||^?A;0;;set||A;<>:;;;res;1;;set||V0;0;;;;;;supp||atv;res;1
    """
    if selecteur.info != obj.attributs.get(selecteur.params.attr.val, ""):
        selecteur.info = obj.attributs.get(selecteur.params.attr.val, "")
        selecteur.regle.match = selecteur.info
        return True
    return False


def sel_ispk(selecteur, obj):
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
    clef = obj.ident + (selecteur.params.attr.val,)
    if clef not in selecteur.info:
        selecteur.info[clef] = obj.schema.getpkey == selecteur.params.attr.val
    return selecteur.info[clef]


def sel_isnull(selecteur, obj):
    """#aide||vrai si l'attribut existe et est null
    #pattern||A;=is:null||1
    #pattern2||A;=is:NULL||1
    #test||obj||^A;;;set||^?A;1;;set||A;is:null;;;res;1;;set||atv;res;1
    """
    return not obj.attributs.get(selecteur.params.attr.val, "1")


def sel_isnotnull(selecteur, obj):
    """#aide||vrai si l'attribut existe et n est pas nul
    #pattern||A;=is:not_null||1
    #pattern2||A;=is:NOT_NULL||1
    #test||obj||^A;1;;set||^?A;;;set||A;is:not_null;;;res;1;;set||atv;res;1
    """
    return obj.attributs.get(selecteur.params.attr.val, "")


# fonctions de selections dans un hstore


def sel_hselk(selecteur, obj):
    """#aide||selection si une clef de hstore existe
    #pattern||H:A;haskey:A||3
    #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;haskey:V0;;;res;1;;set||atv;res;1
    """
    att = selecteur.params.attr.val
    hdic = obj.gethdict(att)
    #    print (" test hstore",hdic,selecteur.params.vals.val)
    return selecteur.params.vals.val in hdic


def sel_hselv(selecteur, obj):
    """#aide||selection si une clef de hstore n'est pas vide
    #pattern||H:A;hasval:C||3
       #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;hasval:0;;;res;1;;set||atv;res;1

    """
    att = selecteur.params.attr.val
    hdic = obj.gethdict(att)
    return selecteur.params.vals.val in hdic.values()


def sel_hselvk(selecteur, obj):
    """#aide||selection sur une valeur d'un hstore
    #pattern||H:A;A:C||10
    #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;V0:0;;;res;1;;set||atv;res;1
    #!test||rien||H:AA;V0:0;;;res;1;;set||rien

    """
    att = selecteur.params.attr.val
    clef = selecteur.params.vals.val
    vals = selecteur.params.vals.definition[0]
    hdic = obj.gethdict(att)
    #    print ("test clef ",hdic,clef,vals)
    return hdic.get(clef) == vals


# -------------------selecteurs proprietes objet
# --------------------selecteurs sur identifiant-----------------------------


def sel_idregex(selecteur, obj):
    """#aide||vrai si l identifiant de classe verifie une expression
        #pattern||=ident:;re||10
        #helper||regex
    #test1||obj||^#groupe,#classe;e1,tt;;set||^?#groupe;e2;;set||ident:;e1;;;res;1;;set||atv;res;1
    """
    return selecteur.fselect(".".join(obj.ident))


def sel_idinfich(selecteur, obj):
    """#aide||vrai si l identifiant de classe est dans un fichier
        #pattern||=ident:;in:fich||1
        #helper||infich
    !test1||obj||^#groupe,#classe;e1,tt;;set||^?#groupe;e2;;set||ident:;e1;;;res;1;;set||atv;res;1
    """
    if selecteur.taille == 3:  # on a ajoute la base
        return (
            obj.attributs.get("#codebase") + "." + ".".join(obj.ident) in selecteur.info
        )
    return ".".join(obj.ident) in selecteur.info


def sel_haspk(selecteur, obj):
    """#aide||vrai si on a defini un des attributs comme clef primaire
    #pattern||;=has:pk||1
    #pattern2||;=has:PK||1
    #test||obj||^A(E,PK);1;;set||^?pk;;;set_schema||;has:pk;;;res;1;;set||atv;res;1
    """
    #     le test est fait sur le premier objet de  la classe qui arrive
    #     et on stocke le resultat : pur eviter que des modifas ulterieures de
    #     schema ne faussent les tests'''
    clef = obj.ident
    if clef in selecteur.info:
        return selecteur.info[clef]

    selecteur.info[clef] = obj.schema and obj.schema.haspkey
    #    print ("pk ",obj.schema.haspkey, obj.schema.indexes)
    return selecteur.info[clef]


# ------------------------selecteurs sur parametres--------------------------


def sel_pexiste(selecteur, _):
    """#aide||teste si un parametre est non vide
    #pattern||P;||50
      #test1||obj||^?P:AA;0;;set||P:AA;!;;;res;1;;set||atv;res;1
    """
    # print ('---------------------------test Pexiste',
    #         selecteur.params.attr.val,'->',
    #         selecteur.regle.getvar(selecteur.params.attr.val),'<-',
    #         bool(selecteur.regle.getvar(selecteur.params.attr.val)))
    return selecteur.regle.getvar(selecteur.params.attr.val)


def sel_pregex(selecteur, _):
    """#aide||teste la valeur d un parametre
     #helper||regex
    #pattern||P;re||100
      #test1||obj||^P:AA;1;;set||^?P:AA;0;;set||P:AA;1;;;res;1;;set||atv;res;1
    """
    # print ('------------------------------pregex',selecteur.params.attr.val,'->',selecteur.regle.getvar(selecteur.params.attr.val))
    return selecteur.fselect(selecteur.regle.getvar(selecteur.params.attr.val))


def selh_constante(selecteur):
    """ mets en place le selecteur de constante """
    if selecteur.params.attr.val == selecteur.params.vals.val:
        selecteur.fselect = selecteur.true
    else:
        selecteur.fselect = selecteur.false


def sel_constante(selecteur, *_):
    """#aide||egalite de constantes sert a customiser des scripts
    #pattern||C:C;C||50
    #test||obj||C:1;1;;;res;1;;set||?C:1;!2;;;res;0;;set||atv;res;1
    """
    return selecteur.fselect()


def selh_cexiste(selecteur):
    """ mets en place le selecteur de constante """
    if selecteur.params.attr.val:
        selecteur.fselect = selecteur.true
    else:
        selecteur.fselect = selecteur.false


def sel_cexiste(selecteur, *_):
    """#aide|| existance de constantes sert a customiser des scripts
    #pattern||C:C;||50
    #test||obj||C:1;;;;res;1;;set||?C:;!;;;res;0;;set||atv;res;1
    """
    return selecteur.fselect()


# -----------selecteurs sur schema-------------------------


def sel_hasschema(_, obj):
    """#aide||objet possedant un schema
    #pattern||;=has:schema||1
    #pattern1||=has:schema||1
    #test||obj||^?#schema;;;supp;;;||;has:schema;;;res;1;;set||atv;res;1
    """
    return obj.schema


def selh_ininfoschema(selecteur):
    """test sur un parametre de schema : recupere le nom du parametre"""
    selecteur.info = selecteur.params.attr.val.split(":")[-1]


def sel_ininfoschema(selecteur, obj):
    """#aide||test sur un parametre de schema
    #pattern||=schema:(.*);||1
    """
    return obj.schema and selecteur.info in obj.schema.info


def sel_inschema(selecteur, obj):
    """#aide||vrai si un attribut est defini dans le schema
    #pattern||A;=in:schema||1
    #pattern2||A;=in_schema||1
       #test||obj||^?C1;;;supp;;;||C1;in_schema;;;res;1;;set||atv;res;1
    """
    # print("sel inschema",obj.schema.attributs)
    return obj.schema and selecteur.params.attr.val in obj.schema.attributs


def sel_infoschema(selecteur, obj):
    """#aide||teste la valeur d un parametre de schema
     #helper||regex
    #pattern||schema:A;re||50
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom;3;;;X;1;;set;||atv;X;1;
    """
    return (
        selecteur.fselect(obj.schema.info.get(selecteur.params.attr.val, ""))
        if obj.schema
        else False
    )


def selh_infoschema_type(selecteur):
    """#initialise les caches"""
    selecteur.lastschema = None  # on mets en cache
    selecteur.lastvaleur = None


def sel_infoschema_has_type(selecteur, obj):
    """#aide||vrai si un attribut de type donne existe dans le schema de l'objet
     #helper||infoschema_type
    #pattern||schema:T:;||50
    #pattern2||;schema:T:;||50
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom;3;;;X;1;;set;||atv;X;1;
    """
    #    print ('dans sel_infoschema_has_type')
    if not obj.schema:
        return False
    if obj.schema.identclasse == selecteur.lastschema:
        return selecteur.lastvaleur
    atts = obj.schema.attributs
    val = (
        selecteur.params.attr.val
        if selecteur.params.attr.val
        else selecteur.params.vals.val
    )
    selecteur.lastschema = obj.schema.identclasse  # on mets en cache
    selecteur.lastvaleur = any([atts[i].type_att == val for i in atts])
    #    print ('sel info type',selecteur.lastschema, selecteur.lastvaleur, val,
    #           [atts[i].type_att for i in atts])
    return selecteur.lastvaleur


def sel_infoschema_is_type(selecteur, obj):
    """#aide||vrai si des attributs nommes sont de type dmand
    #pattern||L;schema:T:||50
     #helper||infoschema_type
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom;3;;;X;1;;set;||atv;X;1;
    """
    if not obj.schema:
        return False
    idschema = obj.schema.identclasse
    if idschema == selecteur.lastschema:
        return selecteur.lastvaleur
    atts = [i for i in obj.schema.attributs if i in selecteur.params.attr.liste]
    val = selecteur.params.val.val
    selecteur.lastschema = idschema  # on mets en cache
    selecteur.lastvaleur = any([atts[i].type_att == val for i in atts])
    return selecteur.lastvaleur


def sel_infoschema_egal(selecteur, obj):
    """#aide||test sur un parametre de schema
    #pattern||schema:A:;C||1
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom=;3;;;X;1;;set;||atv;X;1;
    """
    #    print('test ',selecteur.params.attr.val,'->',obj.schema.info.get(selecteur.params.attr.val),
    #          selecteur.params.vals.val)
    return obj.schema and (
        obj.schema.info.get(selecteur.params.attr.val) == selecteur.params.vals.val
    )


# --------------------selecteurs sur workflow------------------------------


def sel_isko(_, obj):
    """#aide||operation precedente en echec
    #pattern||;=is:ko||1
    #pattern2||;=is:KO||1
    #test||obj||^;;;fail||^?;;;pass||;is:ko;;;res;1;;set||atv;res;1
    """
    #    print (" attributs",selecteur,obj)
    return not obj.is_ok


def sel_isok(_, obj):
    """#aide||operation precedente correcte
    #pattern||;=is:ok||1
    #pattern2||;=is:OK||1
    #test||obj||^;;;pass||^?;;;fail||;is:ok;;;res;1;;set||atv;res;1
    """
    #    print (" attributs",selecteur,obj)
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


# --------------------selecteurs geometriques-------------------------------


def sel_hasgeomv(_, obj):
    """#aide||vrai si l'objet a une geometrique en format interne
    #pattern||;=has:geomV||1
    #pattern1||=has:geomV||1
    #test||obj;point;1||^;;;geom||^?;;;resetgeom||;has:geomV;;;res;1;;set||atv;res;1
    """
    #    print ("hasgeomv",selecteur,obj.geom_v)
    return obj.geom_v.valide or obj.geom_v.sgeom


def sel_hasgeom(_, obj):
    """#aide||vrai si l'objet a un attribut geometrique natif
    #pattern||;=has:geom||1
    #pattern1||=has:geom||1
    #test||obj;asc;1||^;;;geom||^?#geom;;;supp||;has:geom;;;res;1;;set||atv;res;1
    """
    return bool(obj.attributs.get("#geom"))


def sel_hascouleur(selecteur, obj):
    """#aide||objet possedant un schema
    #pattern||=has:couleur;C||1
    #test||obj;asc_c;1||^;;;geom;||^?#geom;;;supp||has:couleur;2;;;res;1;;set;;||atv;res;1
    #test2||obj;asc_c;1||^;;;geom;||^res;0;;set||?has:couleur;!3;;;res;1;;set;;||atv;res;0
    """
    return obj.geom_v.has_couleur(selecteur.params.vals.val)


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
    #        print ('selecteurs: dans virtuel :', obj.ident,obj.virtuel)
    return obj.dimension == 3


def sel_is_type_geom(selecteur, obj):
    """#aide||vrai si l'objet est de dimension 3
    #pattern||=type_geom:;N||1
    #test||obj;point;1||^;1;;geom3D||^?;;;geom2D||;is:3d;;;res;1;;set||atv;res;1
    """
    #        print ('selecteurs: dans virtuel :', obj.ident,obj.virtuel)
    return obj.geom_v.type == selecteur.params.vals.val


def sel_isfile(selecteur, obj):
    """#aide||teste si un fichier existe
    #pattern1||=is:file;[A]||1
    #pattern2||=is:file;C||1
    #test||obj||is:file;%testrep%/refdata/liste.csv;;;C1;1;;set||?is:file;!%testrep%/refdata;;;C1;0;;set||atv;C1;1
    """
    if selecteur.params.pattern == "2":
        # print ('isfile',selecteur.params.vals.val,os.path.isfile(selecteur.params.vals.val))
        return os.path.isfile(selecteur.params.vals.val)
    else:
        return (
            os.path.isfile(obj.attributs.get(selecteur.params.vals.val))
            if obj is not None
            else None
        )


def sel_isdir(selecteur, obj):
    """#aide||tesste si un fichier existe
    #pattern1||=is:dir;[A]||1
    #pattern2||=is:dir;C||1
    #test||obj||is:dir;%testrep%/refdata;;;C1;1;;set||?is:dir;!%testrep%/dudule;;;C1;0;;set||atv;C1;1
    """
    if selecteur.params.pattern == "2":
        return os.path.isdir(selecteur.params.vals.val)
    else:
        return (
            os.path.isdir(obj.attributs.get(selecteur.params.vals.val))
            if obj is not None
            else None
        )


def selh_is_date(selecteur):
    """prepare les selecteurs"""
    selecteur.vref = "O" if selecteur.params.pattern in "23" else "T"


def sel_is_date(selecteur, obj):
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
    # print ("comparaison temps", selecteur.params.pattern)
    if selecteur.params.pattern == "1" or selecteur.params.pattern == "3":
        dateref = obj.attributs.get(selecteur.params.vals.val, "X")
    else:
        dateref = selecteur.params.vals.val
    if selecteur.vref == "O":  # temps de reference pris dans l objet: faux si invalide
        datedesc = obj.attributs.get(selecteur.params.attr.val)
        try:
            date = time.strptime(datedesc, "%Y-%m-%d")
        except ValueError:
            return False
    else:
        date = time.localtime()  # temps de reference = jour courant
    # print ("comparaison temps", date, dateref,selecteur.params.pattern)

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


def selh_is_time(selecteur):
    """prepare les selecteurs"""
    selecteur.vref = "O" if selecteur.params.pattern in "23" else "T"
    if not selecteur.params.pattern or selecteur.params.pattern == "2":
        pass


def sel_is_time(selecteur, obj):
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
    # print ("================================patern ref",selecteur.pattern)
    if selecteur.params.pattern == "1" or selecteur.params.pattern == "3":
        timeref = obj.attributs.get(selecteur.params.vals.val, "X")
    else:
        timeref = selecteur.params.vals.val
    if selecteur.vref == "O":  # temps pris dans l objet
        temps = obj.attributs.get(selecteur.params.attr.val)
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
    #     selecteur.params.vals.val,
    #     selecteur.params.pattern,
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
