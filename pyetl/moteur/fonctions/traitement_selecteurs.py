# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions s de selections : determine si une regle est eligible ou pas
"""
import re
from .outils import compilefonc, prepare_mode_in
DEBUG = 0

def selh_calc(selecteur):
    """prepare les expressions pour le calcul """

    attribut = selecteur.params.attr.val
    valeurs = selecteur.params.vals.val

    exp_final = re.sub("^ *N:(?!#?[A-Za-z])", "N:"+attribut, valeurs)
    exp_final = re.sub("^ *C:(?!#?[A-Za-z])", "C:"+attribut, exp_final)

#    print('exp test final', exp_final, attribut, valeurs)
    selecteur.fselect = compilefonc(exp_final, 'obj', debug=DEBUG)

def sel_calc(selecteur, obj):
    '''#aide||evaluation d une expression avec un attribut
       #pattern||A;NC2:||50
       #test||obj||^A;5;;set||^?A;0;;set||A;N: >2;;;res;1;;set||atv;res;1
       #test2||obj||^A;5;;set||^?A;0;;set||A;C: in "3456";;;res;1;;set||atv;res;1
    '''
    return selecteur.fselect(obj)

def selh_calc2(selecteur):
    """prepare les expressions pour le calcul """
    valeurs = selecteur.params.vals.val
    selecteur.fselect = compilefonc(valeurs, 'obj', debug=DEBUG)

def sel_calc2(selecteur, obj):
    '''#aide||evaluation d une experssion libre
       #pattern||;NC:||50
       #test||obj||^A,B;5,2;;set||^?A;0;;set||;N:A>N:B;;;res;1;;set||atv;res;1

    '''
    return selecteur.fselect(obj)

def sel_attexiste(selecteur, obj):
    '''#aide||teste si un attribut existe
       #pattern||A;||50
       #test||obj||^?Z;0;;set||Z;!;;;res;1;;set||atv;res;1
    '''
    return selecteur.params.attr.val in obj.attributs

def sel_pexiste(selecteur, _):
    '''#aide||teste si un parametre existe
       #pattern||P;||50
       #test1||obj||^?P:AA;0;;set||P:AA;!;;;res;1;;set||atv;res;1
    '''
##    print("test pexiste", selecteur.params.attr.val,
#          selecteur.regle.getvar(selecteur.params.attr.val,"rien"),
#          selecteur.regle.stock_param.get_param(selecteur.params.attr.val,"rien2"))
    return selecteur.regle.getvar(selecteur.params.attr.val)


def selh_regex(selecteur):
    """ compile lesexpressions regulieres"""
#    print (" dans helper regex",selecteur.params.vals.val)
    selecteur.fselect = re.compile(selecteur.params.vals.val).search


def sel_infoschema(selecteur, obj):
    '''#aide||teste la valeur d un parametre de schema
     #helper||regex
    #pattern||schema:A;re||50
      #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom;3;;;X;1;;set;||atv;X;1;
    '''
    return selecteur.fselect(obj.schema.info.get(selecteur.params.attr.val, "")) \
            if  obj.schema else False

def sel_infoschema_egal(selecteur, obj):
    ''' #aide||test sur un parametre de schema
     #pattern||schema:A:;C||1
       #test1||obj;poly||^X;0;;set;||^?;;;force_ligne;;||schema:type_geom=;3;;;X;1;;set;||atv;X;1;
        '''
#    print('test ',selecteur.params.attr.val,'->',obj.schema.info.get(selecteur.params.attr.val),
#          selecteur.params.vals.val)
    return obj.schema and (obj.schema.info.get(selecteur.params.attr.val)
                           == selecteur.params.vals.val)


def sel_regex(selecteur, obj):
    '''#aide||selection sur la valeur d un attribut
       #pattern||A;re||99
       #pattern2||A;re:re||1
       #test||obj||^A;1;;set||^?A;0;;set||A;1;;;res;1;;set||atv;res;1
       #test2||obj||^A;is:pk;;set||^?A;0;;set||A;re:is;;;res;1;;set||atv;res;1
    '''
#    print (" attributs",selecteur,obj)
    return selecteur.fselect(obj.attributs.get(selecteur.params.attr.val, ""))


def sel_pregex(selecteur, _):
    '''#aide||teste la valeur d un parametre
    #helper||regex
       #pattern||P;re||100
       #test1||obj||^P:AA;1;;set||^?P:AA;0;;set||P:AA;1;;;res;1;;set||atv;res;1
    '''
    return selecteur.fselect(selecteur.regle.getvar(selecteur.params.attr.val))

def sel_idregex(selecteur, obj):
    '''selection sur l identifiant de classe
        #pattern||=ident:;re||10
        #helper||regex
    #test1||obj||^#groupe,#classe;e1,tt;;set||^?#groupe;e2;;set||ident:;e1;;;res;1;;set||atv;res;1
    '''
    return selecteur.fselect(".".join(obj.ident))

def sel_idinfich(selecteur, obj):
    '''selection sur l identifiant de classe
        #pattern||=ident:;in:fich||1
        #helper||infich
    !test1||obj||^#groupe,#classe;e1,tt;;set||^?#groupe;e2;;set||ident:;e1;;;res;1;;set||atv;res;1
    '''
    return '.'.join(obj.ident) in selecteur.info


def sel_isko(_, obj):
    '''#aide||operation precedente en echec
       #pattern||;=is:ko||1
       #pattern2||;=is:KO||1
       #test||obj||^;;;fail||^?;;;pass||;is:ko;;;res;1;;set||atv;res;1
    '''
#    print (" attributs",selecteur,obj)
    return not obj.is_ok

def sel_isok(_, obj):
    '''#aide||operation precedente correcte
       #pattern||;=is:ok||1
       #pattern2||;=is:OK||1
       #test||obj||^;;;pass||^?;;;fail||;is:ok;;;res;1;;set||atv;res;1
    '''
#    print (" attributs",selecteur,obj)
    return obj.is_ok


def sel_isvirtuel(_, obj):
    '''#aide||objet virtuel
       #pattern||;=is:virtuel||1
       #pattern2||=is:virtuel;||1
       #test||obj||^;;;virtuel||^?;;;reel||;is:virtuel;;;C1;1;;set||^;;;reel||atv;C1;1

    '''
    return obj.virtuel


def sel_hasgeomv(_, obj):
    '''#aide||vrai si l'objet a une geometrique en format interne
       #pattern||;=has:geomV||1
       #pattern1||=has:geomV||1
       #test||obj;point;1||^;;;geom||^?;;;resetgeom||;has:geomV;;;res;1;;set||atv;res;1
    '''
#    print ("hasgeomv",selecteur,obj.geom_v)
    return obj.geom_v.valide

def sel_hasgeom(_, obj):
    '''#aide||vrai si l'objet a un attribut geometrique natif
       #pattern||;=has:geom||1
       #pattern1||=has:geom||1
       #test||obj;asc;1||^;;;geom||^?#geom;;;supp||;has:geom;;;res;1;;set||atv;res;1
    '''
    return bool(obj.geom)

def sel_hasschema(_, obj):
    '''#aide||objet possedant un schema
       #pattern||;=has:schema||1
       #pattern1||=has:schema||1
       #test||obj||^?#schema;;;supp;;;||;has:schema;;;res;1;;set||atv;res;1
    '''
    return obj.schema

def sel_hascouleur(selecteur, obj):
    '''#aide||objet possedant un schema
       #pattern||=has:couleur;N||1
       #test||obj;asc_c;1||^;;;geom;||^?#geom;;;supp||has:couleur;2;;;res;1;;set;;||atv;res;1
       #test2||obj;asc_c;1||^;;;geom;||^res;0;;set||?has:couleur;!3;;;res;1;;set;;||atv;res;0
    '''
    return obj.geom_v.has_couleur(selecteur.params.vals.num)




def selh_ininfoschema(selecteur):
    '''recupere le nom de l'attribut'''
    selecteur.info = selecteur.params.attr.val.split(':')[-1]


def sel_ininfoschema(selecteur, obj):
    ''' #aide||test sur un parametre de schema
        #pattern||=schema:(.*);||1
        '''
    return obj.schema and selecteur.info in obj.schema.info

def sel_inschema(selecteur, obj):
    '''#aide vrai si un attribut est defini dans le schema
    #pattern||A;=in_schema||1
       #test||obj||^?C1;;;supp;;;||C1;in_schema;;;res;1;;set||atv;res;1
    '''
    return obj.schema and selecteur.params.attr.val in obj.schema.attributs


def selh_infich(selecteur):
    '''precharge le fichier
    '''
#    print ('infich', len(selecteur.params.attr.liste),selecteur.params)
    _, valeurs = prepare_mode_in(selecteur.params.vals.val, selecteur.regle.stock_param,
                                 len(selecteur.params.attr.liste))
    if isinstance(valeurs, list):
        valeurs = set(valeurs)
    selecteur.info = set(valeurs)
#    print ('selecteur liste fich charge ',selecteur.info)

def sel_vinfich(selecteur, obj):
    '''#aide||valeur dans un fichier
    #aide_spec||il est possible de preciser des positions a lire dans le ficher
    +||en mettant les positions entre a,b;in:nom,1,3
     #helper||infich
       #pattern||A;in:fich||20
       #test||obj;||^?A;xxx;;set||A;in:%testrep%/refdata/liste.csv;;;res;1;;set||atv;res;1
    '''
    return obj.attributs.get(selecteur.params.attr.val, "") in selecteur.info

def sel_infich(selecteur, obj):
    '''#aide||valeur dans un fichier
  #aide_spec||il est possible de preciser des positions a lire dans le ficher
           +||en mettant les positions entre a,b;in:nom,1,3
     #helper||infich
    #pattern||L;in:fich||20
       #test||obj||^?A;xxx;;set||A;in:%testrep%/refdata/liste.csv;;;res;1;;set||atv;res;1
    '''
    return ';'.join(obj.attributs.get(i, "") for i in selecteur.params.attr.liste) in selecteur.info


def selh_inlist(selecteur):
    '''stocke la liste'''
    selecteur.info = set(selecteur.params.vals.liste)
#    print ("inlist", selecteur.regle.numero, selecteur.comparaison)

def sel_inlist(selecteur, obj):
    '''#aide||valeur dans une liste
       #pattern||A;in:list||10
       #test||obj||^A;3;;set||^?A;0;;set||A;in:{1,2,3,4};;;res;1;;set;;;||atv;res;1
    '''
    return obj.attributs.get(selecteur.params.attr.val, "") in selecteur.info

def selh_inmem(selecteur):
    '''stocke la liste'''
    selecteur.info = None
    selecteur.precedent = None
    selecteur.geom = '#geom' in selecteur.params.attr.liste
    if selecteur.geom:
        selecteur.params.attr.liste.remove('#geom')
#    print ("inlist", selecteur.regle.numero, selecteur.comparaison)

def sel_inmem(selecteur, obj):
    '''#aide||valeur dans une liste en memoire (chargee par preload)
       #pattern||A;in:mem||10
       #!test||obj||^A;3;;set||^?A;0;;set||A;in:{1,2,3,4};;;res;1;;set;;;||atv;res;1
    '''
    if selecteur.precedent != obj.ident: # on vient de changer de classe
        selecteur.info = selecteur.regle.stock_param.store[selecteur.params.vals.val]
        selecteur.precedent = obj.ident
#    print ('comparaison ', len(regle.comp), regle.comp)
    if selecteur.info is None:
        return False

    clef = str(tuple(tuple(i) for i in obj.geom_v.coords)) if selecteur.geom else ''
    clef = clef + "|".join(obj.attributs.get(i, '') for i in selecteur.params.attr.liste)

    return clef in selecteur.info


def sel_changed(selecteur, obj):
    '''#aide||detection de changement d un attribut
    #pattern||A;=<>:||1
    #test||obj;;2||^A;;;cnt;1;0||^?A;0;;set||A;<>:;;;res;1;;set||V0;0;;;;;;supp||atv;res;1
    '''
    if selecteur.info != obj.attributs.get(selecteur.params.attr.val, ""):
        selecteur.info = obj.attributs.get(selecteur.params.attr.val, "")
        return True
    return False


def sel_haspk(selecteur, obj):
    '''#aide || vrai si on a defini un des attributs comme clef primaire
    #pattern||;=has:pk||1
    #pattern2||;=has:PK||1
    #test||obj||^A(E,PK);1;;set||^?pk;;;set_schema||;has:pk;;;res;1;;set||atv;res;1
    '''
#     le test est fait sur le premier objet de  la classe qui arrive
#     et on stocke le resultat : pur eviter que des modifas ulterieures de
#     schema ne faussent les tests'''
    clef = obj.ident
    if clef in selecteur.info:
        return selecteur.info[clef]

    selecteur.info[clef] = obj.schema and obj.schema.haspkey
#    print ("pk ",obj.schema.haspkey, obj.schema.indexes)
    return selecteur.info[clef]


def sel_ispk(selecteur, obj):
    '''#aide ||vrai si l'attribut est une clef primaire
    #pattern||A;=is:pk||1
    #pattern2||A;=is:PK||1
    #test||obj||^A(E,PK);1;;set||^?pk;;;set_schema||A;is:pk;;;res;1;;set||atv;res;1
    '''

#        le test est fait sur le premier objet de  la classe qui arrive
#        et on stocke le resultat : pur eviter que des modifas ulterieures de
#        schema ne faussent les tests'''

    clef = obj.ident+(selecteur.params.attr.val,)
    if clef in selecteur.info:
        return selecteur.info[clef]
#        if obj.schema:
    selecteur.info[clef] = obj.schema.indexes.get("P:1") == selecteur.params.attr.val
    return selecteur.info[clef]


def sel_is2d(_, obj):
    '''#aide||vrai si l'objet est de dimension 2
    #pattern||;=is:2d||1
    #pattern2||;=is:2D||1
    #test||obj;point;1||^?;1;;geom3D||;is:2d;;;res;1;;set||atv;res;1
    '''
    return obj.dimension == 2

def sel_is3d(_, obj):
    '''#aide||vrai si l'objet est de dimension 3
    #pattern||;=is:3d||1
    #pattern2||;=is:3D||1
    #test||obj;point;1||^;1;;geom3D||^?;;;geom2D||;is:3d;;;res;1;;set||atv;res;1
    '''
#        print ('selecteurs: dans virtuel :', obj.ident,obj.virtuel)
    return obj.dimension == 3


def sel_isnull(selecteur, obj):
    '''#aide||vrai si l'attribut existe et est null
    #pattern||A;=is:null||1
    #pattern2||A;=is:NULL||1
    #test||obj||^A;;;set||^?A;1;;set||A;is:null;;;res;1;;set||atv;res;1
    '''
    return not obj.attributs.get(selecteur.params.attr.val, "1")

def sel_isnotnull(selecteur, obj):
    '''#aide||vrai si l'attribut existe et n est pas nul
    #pattern||A;=is:not_null||1
    #pattern2||A;=is:NOT_NULL||1
    #test||obj||^A;1;;set||^?A;;;set||A;is:not_null;;;res;1;;set||atv;res;1
    '''
    return obj.attributs.get(selecteur.params.attr.val, "")

#def sel_hascouleur(selecteur, obj):
#    '''#aide||vrai si une couleur est presente dans la geometrie
#    #pattern||N;=has:couleur||1
#    #pattern2||N;=has:color||1
#    #test||obj;asc_c;1||^;;;geom||^?;1;;force_pt||2;has:couleur;;;res;1;;set||atv;res;1
#    '''
#    return obj.geom_v.has_couleur(selecteur.params.attr.num)


def selh_constante(selecteur):
    """ mets en place le selecteur de constante """
    if selecteur.params.attr.val == selecteur.params.vals.val:
        selecteur.fselect = selecteur.true
    else:
        selecteur.fselect = selecteur.false


def sel_constante(selecteur, *_):
    '''#aide egalite de constantes sert a customiser des scripts
    #pattern||C:C;C||50
    #test||obj||C:1;1;;;res;1;;set||?C:1;!2;;;res;0;;set||atv;res;1
    '''
    return selecteur.fselect()


def selh_cexiste(selecteur):
    """ mets en place le selecteur de constante """
    if selecteur.params.attr.val:
        selecteur.fselect = selecteur.true
    else:
        selecteur.fselect = selecteur.false


def sel_cexiste(selecteur, *_):
    '''#aide existance de constantes sert a customiser des scripts
    #pattern||C:C;||50
    #test||obj||C:1;;;;res;1;;set||?C:;!;;;res;0;;set||atv;res;1
    '''
    return selecteur.fselect()

# fonctions de selections dans un hstore


def sel_hselk(selecteur, obj):
    '''#aide||selection si une clef de hstore existe
    #pattern||H:A;haskey:A||3
    #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;haskey:V0;;;res;1;;set||atv;res;1
    '''
    att = selecteur.params.attr.val
    hdic = obj.gethdict(att)
#    print (" test hstore",hdic,selecteur.params.vals.val)
    return selecteur.params.vals.val in hdic

def sel_hselv(selecteur, obj):
    '''#aide||selection sur une valeur dans une valeur d'un hstore
    #pattern||H:A;hasval:C||3
    #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;hasval:0;;;res;1;;set||atv;res;1

    '''
    att = selecteur.params.attr.val
    hdic = obj.gethdict(att)
    return selecteur.params.vals.val in hdic.values()

def sel_hselvk(selecteur, obj):
    '''#aide||selection sur une valeur dans une valeur d'un hstore
    #pattern||H:A;A:C||10
    #test||obj||^AA;;;hset||^?AA;;AA;hdel;V0||H:AA;V0:0;;;res;1;;set||atv;res;1
    #!test||rien||H:AA;V0:0;;;res;1;;set||rien

    '''
    att = selecteur.params.attr.val
    clef = selecteur.params.vals.val
    vals = selecteur.params.vals.definition[0]
    hdic = obj.gethdict(att)
#    print ("test clef ",hdic,clef,vals)
    return hdic.get(clef) == vals
