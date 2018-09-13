# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de manipulation d'attributs
"""
import os
import logging
import glob

from itertools import zip_longest
import pyetl.formats.mdbaccess as DB
from .outils import prepare_mode_in

LOGGER = logging.getLogger('pyetl')


def _mode_niv_in(mapper, niv):
    """gere les requetes de type niveau in..."""
    mode_select, valeurs = prepare_mode_in(niv, mapper, 2)
    niveau = []
    classe = []
    attrs = []
    cmp = []
#    print("mode_niv in:lecture_fichier",valeurs)
    for i in valeurs:
        liste_defs = valeurs[i]
#        print("mode_niv in:liste_defs",liste_defs)

        def1 = liste_defs.pop(0).split('.')
        if len(def1) == 1 and liste_defs and liste_defs[0]:
            defs2 = liste_defs.pop(0).split('.')
            def1.extend(defs2)
#            print("mode_niv in:def1",def1)

        niveau.append(def1[0])
        if len(def1) == 1:
            classe.append('')
            attrs.append('')
            cmp.append('')
        elif len(def1) == 2:
            classe.append(def1[1])
            attrs.append('')
            cmp.append('')
        elif len(def1) == 3:
#                print("detection attribut")
            classe.append(def1[1])
            attrs.append(def1[2])
            vals = ""
            if liste_defs:
                if liste_defs[0].startswith('in:'):
                    txt = liste_defs[0][3:]
                    vals = txt[1:-1].split(",") if txt.startswith('{') else []
                else:
                    vals = liste_defs[0]
            cmp.append(vals)
#    print ('mode_niv in:lu ','\n'.join(str(i) for i in zip(niveau, classe, attrs, cmp)))
    return niveau, classe, attrs, cmp



def param_base(regle):
    """ extrait les parametres d acces a la base"""
    base = regle.code_classe[3:]

    niveau, classe, att = '', '', ""
    niv = regle.v_nommees["val_sel1"]
    cla = regle.v_nommees["sel2"]
    att = regle.v_nommees["val_sel2"]
    attrs = []
    cmp = []

    if niv.lower().startswith('s:'): # selection directe du style niveau,classe.attribut
        if len(niv.split('.')) != 3:
            print('dbselect: il faut une description complete s:niveau.classe.attribut', niv)
        else:
            att = niv.split('.')[2]
            niveau = [niv]
#    elif re.match("\[.*\]", niv) and

    elif niv.lower().startswith('in:'):# mode in
        niveau, classe, attrs, cmp = _mode_niv_in(regle.stock_param, niv[3:])
    elif cla.lower().startswith('in:'):# mode in
        clef = 1 if '#schema' in cla else 0
        mode_select, valeurs = prepare_mode_in(cla[3:], regle.stock_param, 1, clef=clef)
        classe = list(valeurs.keys())
        niveau = [niv]*len(classe)
    elif ',' in niv:
        niveau = niv.split(',')
        if '.' in niv:
            classe = [(i.split('.')+[''])[1] for i in niveau]
            niveau = [i.split('.')[0] for i in niveau]
        else:
            classe = [cla]*len(niveau)
    elif ',' in cla:
        classe = cla.split(',')
        niveau = [niv]*len(classe)

    else:
        niveau = [niv]
        classe = [cla]
    if attrs:
        att = (attrs, cmp)

    regle.dyn = '#' in niv or '#' in cla
#    print('parametres dbaccess', base, niveau, classe, att, regle)

    regle.cible_base = (base, niveau, classe, att)
    return True

def valide_dbmods(modlist):
    ''' valide les modificateur sur les requetes '''

    modlist = [i.upper() for i in modlist]
    valide = all([i in DB.DBMODS for i in modlist])
    return valide


def h_dbalpha(regle):
    """preparation lecture"""
    if param_base(regle):
#        print (" preparation lecture ",regle.cible_base)
    #    raise
        defaut = regle.v_nommees.get("defaut", "")
        if defaut[:3].lower() == 'in:':
            mode_multi, valeurs = prepare_mode_in(regle.v_nommees["defaut"][3:],
                                                  regle.stock_param, 1)
            regle.params.val_entree = regle.params.st_val(defaut, None, list(valeurs.keys()),
                                                          False, "")
        regle.chargeur = True # c est une regle qui cree des objets
        if valide_dbmods(regle.params.cmp1.liste):
            return True
        regle.erreurs.append("dbalpha: modificateurs non autorises seulement:", DB.DBMODS)
        return False
    print("erreur regle", regle)
    regle.erreurs.append("dbalpha: erreur base non definie")
    return False

def f_dbalpha(regle, obj):
    '''#aide||recuperation d'objets depuis la base de donnees
     #groupe||database
    #pattern||?A;?;?;dbalpha;?;?

    '''
    #regle.stock_param.regle_courante=regle
    type_base = None
    chemin = ''
    attrs = []
    cmp = []
    valeur = []
    base, niveau, classe, attribut = regle.cible_base
    if attribut: #attention on traite des attributs
        if isinstance(attribut, tuple):
            attrs, cmp = attribut
        else:
            attrs = attribut
#    print ('f_alpha :',attrs, cmp)
    if obj.attributs["#groupe"] == '__filedb': # acces a une base fichier

        chemin = obj.attributs["#chemin"]
        if not base:
            base = obj.attributs["#base"]
        type_base = obj.attributs["#type_base"]
        regle.setvar("db", type_base, loc=1)
        regle.setvar("server", chemin, loc=1)
#    print ('regles alpha: acces base ', base, niveau, classe, attribut)

    if niveau and niveau[0].startswith('['): # nom de classe contenu dans un attribut
        niveau = [obj.attributs.get(niveau[0][1:-1], 'xx')]
    if classe and classe[0].startswith('['): # nom de classe contenu dans un attribut
        classe = [obj.attributs.get(classe[0][1:-1], 'xx')]
    if regle.params.att_entree.liste:
#        print('on a mis un attribut', regle.params.att_entree.liste)
        valeur = [obj.attributs.get(a, d) for a, d
                  in zip_longest(regle.params.att_entree.liste, regle.params.val_entree.liste)]
    elif regle.params.val_entree.liste:
        valeur = regle.params.val_entree.liste
    else:
        valeur = cmp

    mods = regle.params.cmp1.liste


#    vue = 0
#    ordre = None
#    if regle.params.cmp2.val == '#v':
#        vue = 1
#    elif regle.params.cmp2.val == '#+v':
#        vue = 2
#    elif regle.params.cmp2.val == '!#v':
#        vue = -1
#    elif regle.params.cmp2.liste:
    ordre = regle.params.cmp2.liste
#    print ('regles alpha: acces base apres ', base, niveau, classe, attribut)


    LOGGER.debug('regles alpha:ligne  '+ repr(regle)+ repr(type_base)+ repr(mods))
#    print('regles alpha:ligne  ', regle, type_base, mods)
#    print('regles alpha:parms:', base, niveau, classe, attribut, 'entree:',regle.params.val_entree,
#          valeur, 'cmp1:', regle.params.cmp1, 'sortie:', regle.params.att_sortie)

#    print ('regles alpha: ','\n'.join(str(i) for i in (zip(niveau,classe,attrs,cmp))), valeur)
    if base:
        retour = DB.recup_donnees_req_alpha(regle, base, niveau, classe, attrs,
                                            valeur, mods=mods, sortie=regle.params.att_sortie.liste,
                                            v_sortie=valeur, ordre=ordre,
                                            type_base=type_base, chemin=chemin)
#    print ('regles alpha: valeur retour',retour,obj)
        return retour
    print('fdbalpha: base non definie ', base)
    return False
    #recup_donnees(stock_param,niveau,classe,attribut,valeur):

def f_dblast(regle, obj):
    '''#aide||recupere les derniers enregistrements d 'une couche (superieur a une valeur min)
    #groupe||database
    #pattern||;;;dblast;C
    #pattern2||A;;;dblast
    '''


def h_dbgeo(regle):
    """gestion des fonctions geographiques"""
    param_base(regle)
    regle.chargeur = True # c est une regle qui cree des objets

    fonctions = ['intersect', 'dans', 'dans_emprise', '!intersect', '!dans', '!dans_emprise']
    attribut = regle.v_nommees.get("val_sel2", '')
    valide = True
    if attribut not in fonctions:
        regle.erreurs.append("dbgeo: fonction inconnue seulement:"+','.join(fonctions))
        valide = False
    if not valide_dbmods(regle.params.cmp1.liste):
        valide = False
        regle.erreurs.append("dbalpha: modificateurs non autorises seulement:"+','.join(DB.DBMODS))
    return valide

def f_dbgeo(regle, obj):
    '''#aide||recuperation d'objets depuis la base de donnees
     #groupe||database
    #pattern||?A;?;?L;dbgeo;?C;

    '''
    #regle.stock_param.regle_courante=regle
    base, niveau, classe, fonction = regle.cible_base
    type_base = None
    chemin = ''
    if obj.attributs["#groupe"] == '__filedb': # acces a une base fichier
        chemin = obj.attributs["#chemin"]
        if not base:
            base = obj.attributs["#base"]
        type_base = obj.attributs["#type_base"]
        regle.setvar("db", type_base, loc=1)
        regle.setvar("server", chemin, loc=1)
    if niveau and niveau[0] == '[': # nom de classe contenu dans un attribut
        niveau = obj.attributs.get(niveau[1:-1], 'xx')
    if classe and classe[0] == '[': # nom de classe contenu dans un attribut
        classe = obj.attributs.get(classe[1:-1], 'xx')
    if regle.params.att_entree.liste:
        if regle.params.val_entree.liste and regle.params.att_entree.liste:
            valeur = [obj.attributs.get(a, d) for a, d
                      in zip(regle.params.att_entree.liste,
                             regle.params.val_entree.liste)]
        else:
            valeur = [obj.attributs.get(a, '') for a in regle.params.att_entree.liste]
    else:
        valeur = regle.params.val_entree.liste
#    print('preparation attribut', valeur, regle.params.att_entree)
    if not fonction:
        print("regle:dbgeo !!!!! pas de fonction geometrique", regle)
        return False
    else:
        retour = DB.recup_donnees_req_geo(regle, base, niveau, classe, fonction, obj,
                                          regle.params.cmp1.val, regle.params.att_sortie.liste,
                                          valeur, type_base=type_base, chemin=chemin)
    return retour
    #recup_donnees(stock_param,niveau,classe,attribut,valeur):

def f_dbclose(regle, obj):
    '''#aide||recuperation d'objets depuis la base de donnees
     #groupe||database
    #pattern||;;;dbclose;;
    '''
    base, _, _, _ = regle.cible_base
    if obj.attributs["#groupe"] == '__filedb': # acces a une base fichier
        base = obj.attributs.get("#base", base)
        regle.setvar("db", obj.attributs.get("#type_base",))
        regle.setvar("server", obj.attributs.get("#chemin"))
    DB.dbclose(regle.stock_param, base)
    return True

def h_dbrunsql(regle):
    """execution de commandes"""
    regle.chargeur = True # c est une regle qui cree des objets
    param_base(regle)

def f_dbrunsql(regle, obj):
    '''#aide||lancement d'un script sql
  #aide_spec||parametres:base;;;;?nom;?variable contenant le nom;runsql;?log;?sortie
     #groupe||database
    #pattern||;?C;?A;runsql;?C;?C
    '''
    base, _, _, _ = regle.cible_base
    script = obj.attributs.get(regle.params.att_entree.val, regle.params.val_entree.val)
    print('traitement db: execution sql ', base, '->', script, regle.params.cmp1.val,
          regle.params.cmp2.val)
    scripts = sorted(glob.glob(script))
    for nom in scripts:
        print('traitement sql ', nom)
        DB.dbrunsql(regle.stock_param, base, nom, log=regle.params.cmp1.val,
                    out=regle.params.cmp2.val)

def h_dbextload(regle):
    """execution de commandes de chargement externe"""
#    regle.chargeur = True # c est une regle qui cree des objets
    param_base(regle)

def f_dbextload(regle, obj):
    '''#aide||lancement d'un script sql
  #aide_spec||parametres:base;;;;?nom;?variable contenant le nom;runsql;?log;?sortie
     #groupe||database
    #pattern||;?C;?A;dbextload;?C
    '''
    base, _, _, _ = regle.cible_base
    datas = obj.attributs.get(regle.params.att_entree.val, regle.params.val_entree.val)
    print('traitement db: chargement donnees ', base, '->', datas, regle.params.cmp1.val)
    fichs = sorted(glob.glob(datas))
    for nom in fichs:
        print('chargement donnees', nom)
        DB.dbextload(regle.stock_param, base, nom, log=regle.params.cmp1.val)




def f_dbwrite(regle, obj):
    '''#aide||chargement en base de donnees
     #groupe||database
    #pattern||;;;dbwrite;;
    '''
    base, niveau, classe, _ = regle.cible_base
    DB.dbload(regle, base, niveau, classe, obj)


def f_dbupdate(regle, obj):
    '''#aide||chargement en base de donnees
     #groupe||database
    #pattern||;;;dbupdate;;
    '''
    base, niveau, classe, attribut = regle.cible_base
    DB.dbupdate(regle, base, niveau, classe, attribut, obj)


def h_dbmaxval(regle):
    ''' stocke la valeur maxi '''
    param_base(regle)
    base, niveau, classe, attribut = regle.cible_base
    retour = DB.recup_maxval(regle.stock_param, base, niveau, classe, attribut)
    if len(retour) == 1 and regle.params.att_sortie.val:
        # cas simple on stocke l' attribut dans le parametre
        valeur = list(retour.values())[0]
        regle.stock_param.set_param(regle.params.att_sortie.val, str(valeur))
        print('maxval stockage', regle.params.att_sortie.val, str(valeur))
    nom = regle.params.cmp1.val if regle.params.cmp1.val else '#maxvals'
    regle.stock_param.store[nom] = retour
    regle.valide = 'done'
    return True

def f_dbmaxval(regle, obj):
    '''#aide||valeur maxi d une claef en base de donnees
     #groupe||database
    #pattern||?P;;;dbmaxval;?C;
    #test||rien||$#sigli;sigli;;||db:sigli;admin_sigli;description_fonctions;;P:toto;;;dbmaxval
    -||ptv;toto;1
    '''
    pass




def h_dbcount(regle):
    ''' stocke la valeur maxi '''
    param_base(regle)
    base, niveau, classe, attribut = regle.cible_base
    retour = DB.count(regle.stock_param, base, niveau, classe)
    if len(retour) == 1 and regle.params.att_sortie.val:
        # cas simple on stocke l' attribut dans le parametre
        valeur = list(retour.values())[0]
        regle.stock_param.set_param(regle.params.att_sortie.val, str(valeur))
        print('comptage', regle.params.att_sortie.val, str(valeur))
    nom = regle.params.cmp1.val if regle.params.cmp1.val else '#nbvals'
    regle.stock_param.store[nom] = retour
    regle.valide = 'done'
    return True

def f_dbcount(regle, obj):
    '''#aide||valeur maxi d une claef en base de donnees
     #groupe||database
    #pattern||?P;;;dbcount;?C;
       #test||rien||$#sigli;sigli;;||db:sigli;admin_sigli;description_fonctions;;P:toto;;;dbcount
           -||ptv;toto;1
    '''
    pass






def h_recup_schema(regle):
    """ lecture de schemas """
    if not param_base(regle):
        regle.valide = False
        return False
    regle.chargeur = True # c est une regle a declencher

    nombase, niveau, classe, _ = regle.cible_base

    regle.type_base = regle.stock_param.get_param('db_'+nombase)
#    print ('interp schema_base','db_'+nombase,regle.type_base,nombase,regle.stock_param.parms)
#    base = regle.v_nommees["sel1"][3:]
    base = nombase
    if base:
        nomschema = regle.params.val_entree.val if regle.params.val_entree.val else base
        if regle.params.att_sortie.val: # c'est une definition de mapping

            regle.schema_entree = regle.params.att_sortie.val == "schema_entree"
            regle.schema_sortie = regle.params.att_sortie.val == "schema_sortie"
            if regle.schema_entree or regle.schema_sortie:

                if regle.schema_entree:
                    regle.setvar("schema_entree", nomschema)
                if regle.schema_sortie:
                    regle.setvar("schema_sortie", nomschema)
            regle.valide = 'done'
            DB.recup_schema(regle, base, niveau, classe, nomschema)

def f_recup_schema(regle, obj):
    '''#aide||recupere les schemas des base de donnees
     #groupe||database
    #pattern1||=schema_entree;C?;A?;dbschema;?;||sortie
    #pattern2||=schema_sortie;C?;A?;dbschema;?;||sortie
    #pattern3||=#schema;C?;A?;dbschema;?;||sortie
    #pattern4||;C?;A?;dbschema;?;
    '''
    chemin = ''

    base, niveau, classe, att = regle.cible_base

    if obj.attributs["#groupe"] == "__filedb":
        chemin = obj.attributs["#chemin"]
        type_base = obj.attributs["#type_base"]
        if base != obj.attributs["#base"]:
            base = obj.attributs["#base"]
            regle.cible_base = (base, niveau, classe, att)
            DB.recup_schema(regle, base, niveau, classe, regle.params.val_entree.val,
                            type_base=type_base, chemin=chemin)
            regle.stock_param.parms["db"] = type_base
            regle.stock_param.parms["server"] = chemin
#        print ("regles",regle.numero," :dans recupschema ",chemin,base,type_base)
#        print ("regles",regle.numero," :dans recupschema ",obj.virtuel,obj.attributs)
    else:
        type_base = regle.type_base
#        print('tdb: acces schema base', type_base, base, niveau, classe)
#          regle.ligne,
#          regle.params.val_entree.val,
#          regle.params)
    if type_base and base:
        DB.recup_schema(regle, base, niveau, classe, regle.params.val_entree.val,
                        type_base=type_base, chemin=chemin)
        return True
    print('recup_schema: base non definie ', type_base, base)
    return False




def h_dbclean(regle):
    '''prepare un script de reinitialisation d'une ensemble de tables '''

    regle.chargeur = True # c est une regle a declencher
    if not param_base(regle):
        regle.valide = False
        return False
    nombase, niveau, classe, _ = regle.cible_base

    regle.type_base = regle.stock_param.get_param('db_'+nombase)
#    print ('interp schema_base','db_'+nombase,regle.type_base,nombase,regle.stock_param.parms)
#    base = regle.v_nommees["sel1"][3:]
    base = nombase
    nom = regle.params.cmp2.val + '.sql'
    if base:
        nomschema = regle.params.val_entree.val if regle.params.val_entree.val else base
        script = DB.reset_liste_tables(regle, base, niveau, classe, nomschema)
        if os.path.dirname(nom):
            os.makedirs(os.path.dirname(nom), exist_ok=True)
        print('ecriture script ', nom)
        with open(nom, 'w') as sortie:
            sortie.write(''.join(script))
        regle.valide = 'done'


def f_dbclean(regle, obj):
    '''#aide||vide un ensemble de tables
     #groupe||database
   #pattern1||;;;dbclean;?C;?C'''
    pass
