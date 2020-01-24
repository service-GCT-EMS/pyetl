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
from .outils import prepare_mode_in, objloader

LOGGER = logging.getLogger("pyetl")


def _mode_niv_in(regle, niv, autobase=False):
    """gere les requetes de type niveau in..."""
    mode_select, valeurs = prepare_mode_in(niv, regle, taille=2)
    niveau = []
    classe = []
    attrs = []
    cmp = []
    base= []
    print("mode_niv in:lecture_fichier",valeurs)
    for i in valeurs:
        liste_defs = valeurs[i]
        # print("mode_niv in:liste_defs",liste_defs)

        def1 = liste_defs.pop(0).split(".")
        if len(def1) == 1 and liste_defs and liste_defs[0]: # c'est de la forme niveau;classe
            defs2 = liste_defs.pop(0).split(".")
            def1.extend(defs2)
        # print("mode_niv in:def1",def1)

        niveau.append(def1[0])
        if len(def1) == 1:
            classe.append("")
            attrs.append("")
            cmp.append("")
        elif len(def1) == 2:
            classe.append(def1[1])
            attrs.append("")
            cmp.append("")
            if autobase and len(liste_defs)>2: # on a rajoute la base
                base.append(liste_defs[2:])
        elif len(def1) == 3:
            #                print("detection attribut")
            classe.append(def1[1])
            attrs.append(def1[2])
            vals = ""
            if liste_defs:
                if liste_defs[0].startswith("in:"):
                    txt = liste_defs[0][3:]
                    vals = txt[1:-1].split(",") if txt.startswith("{") else []
                else:
                    vals = liste_defs[0]
            cmp.append(vals)
    # print ('mode_niv in:lu ','\n'.join(str(i) for i in zip(niveau, classe, attrs, cmp)))
    return base, niveau, classe, attrs, cmp


def param_base(regle):
    """ extrait les parametres d acces a la base"""
    # TODO gerer les modes in dynamiques
    base = regle.code_classe[3:]
    if base=='*':
        base=''

    niveau, classe, att = "", "", ""
    niv = regle.v_nommees["val_sel1"]
    cla = regle.v_nommees["sel2"]
    att = regle.v_nommees["val_sel2"]
    attrs = []
    cmp = []

    if niv.lower().startswith("s:"):  # selection directe du style niveau,classe.attribut
        if len(niv.split(".")) != 3:
            print("dbselect: il faut une description complete s:niveau.classe.attribut", niv)
        else:
            att = niv.split(".")[2]
            niveau = [niv]
    #    elif re.match("\[.*\]", niv) and

    elif niv.lower().startswith("in:"):  # mode in
        if base:
            _ ,niveau, classe, attrs, cmp = _mode_niv_in(regle, niv[3:])
        else: # mode mutibase (projets qgis ou csv multibase)
            base, niveau, classe, attrs, cmp = _mode_niv_in(regle, niv[3:], autobase=True)
    elif cla.lower().startswith("in:"):  # mode in
        clef = 1 if "#schema" in cla else 0
        mode_select, valeurs = prepare_mode_in(cla[3:], regle, taille=1, clef=clef)
        classe = list(valeurs.keys())
        niveau = [niv] * len(classe)
    elif "," in niv:
        niveau = niv.split(",")
        if "." in niv:
            classe = [(i.split(".") + [""])[1] for i in niveau]
            niveau = [i.split(".")[0] for i in niveau]
        else:
            classe = [cla] * len(niveau)
    elif "," in cla:
        classe = cla.split(",")
        niveau = [niv] * len(classe)

    else:
        niveau = [niv]
        classe = [cla]
    if attrs:
        att = (attrs, cmp)

    regle.dyn = "#" in niv or "#" in cla
    #    print('parametres dbaccess', base, niveau, classe, att, regle)

    regle.cible_base = (base, niveau, classe, att)
    return True


def valide_dbmods(modlist):
    """ valide les modificateur sur les requetes """

    modlist = [i.upper() for i in modlist]
    valide = all([i in DB.DBMODS for i in modlist])
    return valide


def h_dbalpha(regle):
    """preparation lecture"""
    if param_base(regle):
        #        print (" preparation lecture ",regle.cible_base)
        #    raise
        defaut = regle.v_nommees.get("defaut", "") # on utilise in comme selecteur attributaire
        if defaut[:3].lower() == "in:":
            mode_multi, valeurs = prepare_mode_in(
                regle.v_nommees["defaut"][3:], regle, taille=1
            )
            regle.params.val_entree = regle.params.st_val(
                defaut, None, list(valeurs.keys()), False, ""
            )
        regle.chargeur = True  # c est une regle qui cree des objets
        if regle.getvar('noauto'): # mais on veut pas qu'elle se declenche seule
            regle.chargeur = False
        #        regle.stock_param.gestion_parallel_load(regle)
        if valide_dbmods(regle.params.cmp1.liste):
            return True
        regle.erreurs.append("dbalpha: modificateurs non autorises seulement:", DB.DBMODS)
        return False
    print("erreur regle", regle)
    regle.erreurs.append("dbalpha: erreur base non definie")
    return False


def setdb(regle, obj, att=True):
    """positionne des parametres d'acces aux bases de donnees"""
    base, niveau, classe, attribut = regle.cible_base
    attrs = []
    cmp = []
    type_base = None
    chemin = ""
    if att: #(tri sur attribut si necessaire)
        if attribut:  # attention il y a des definitions d'attributs
            if isinstance(attribut, tuple):
                attrs, cmp = attribut
            else:
                attrs = attribut
    else: # traitement sans gestion des attributs (geometrique ou dump)
        attrs = attribut
    #    print ('f_alpha :',attrs, cmp)
    if obj.attributs["#groupe"] == "__filedb":  # acces a une base fichier

        chemin = obj.attributs["#chemin"]
        if not base:
            base = obj.attributs["#base"]
        type_base = obj.attributs["#type_base"]
        regle.setvar("db", type_base)
        regle.setvar("server", chemin)
    #    print ('regles alpha: acces base ', base, niveau, classe, attribut)

    if niveau and niveau[0].startswith("["):  # nom de classe contenu dans un attribut
        niveau = [obj.attributs.get(niveau[0][1:-1], "niveau non defini " + niveau[0])]
    if classe and classe[0].startswith("["):  # nom de classe contenu dans un attribut
        classe = [obj.attributs.get(classe[0][1:-1], "attribut non defini " +'.'.join(obj.ident)+' '+classe[0][1:-1])]
    if regle.params.att_entree.liste:
        #        print('on a mis un attribut', regle.params.att_entree.liste)
        valeur = [
            obj.attributs.get(a, d)
            for a, d in zip_longest(regle.params.att_entree.liste, regle.params.val_entree.liste)
        ]
    elif regle.params.val_entree.liste:
        valeur = regle.params.val_entree.liste
    else:
        valeur = cmp
    return (base, niveau, classe, attrs, valeur, chemin, type_base)


def f_dbalpha(regle, obj):
    """#aide||recuperation d'objets depuis la base de donnees
     #groupe||database
    #pattern||?A;?;?;dbalpha;?;?
    #req_test||testdb

    """
    if not regle.getvar('traitement_virtuel'):
        if obj.virtuel and obj.attributs.get("#categorie") == "traitement_virtuel" :
            # print ('detection traitement virtuel : on ignore', obj, regle.getvar('traitement_virtuel'), regle.context.vlocales)
            return False

    base, niveau, classe, attrs, valeur, chemin, type_base = setdb(regle, obj)
    mods = regle.params.cmp1.liste
    ordre = regle.params.cmp2.liste
    # print ('regles alpha: acces base apres ', base, niveau, classe, attrs)

    LOGGER.debug("regles alpha:ligne  " + repr(regle) + repr(type_base) + repr(mods))
    #    print('regles alpha:ligne  ', regle, type_base, mods)
    #    print('regles alpha:parms:', base, niveau, classe, attribut, 'entree:',regle.params.val_entree,
    #          valeur, 'cmp1:', regle.params.cmp1, 'sortie:', regle.params.att_sortie)

    #    print ('regles alpha: ','\n'.join(str(i) for i in (zip(niveau,classe,attrs,cmp))), valeur)

    if base:
        connect = DB.dbaccess(regle, base, type_base=type_base, chemin=chemin)
        if connect is None:
            return False
        if connect.accept_sql == "non":  # pas de requetes directes on essaye le mode dump
            dest = regle.getvar("dest")
            if not dest:
                dest = os.path.join(regle.getvar("_sortie"), "tmp")
            os.makedirs(dest, exist_ok=True)
            regle.setvar("_entree", dest)
            log = regle.getvar("log", os.path.join(dest, "log_extraction.log"))
            os.makedirs(os.path.dirname(log), exist_ok=True)
            print("traitement db: dump donnees de", base, "vers", dest)
            retour = DB.dbextalpha(regle, base, niveau, classe, dest=dest, log=log)

        #            if regle.store:
        ##        print( 'mode parallele', os.getpid(), regle.stock_param.worker)
        ##        print ('regles', regle.stock_param.regles)
        #                regle.tmpstore.append(obj)
        #                regle.nbstock += 1
        #                return True
        #            return objloader(regle, obj)
        else:
            retour = DB.recup_donnees_req_alpha(
                regle,
                base,
                niveau,
                classe,
                attrs,
                valeur,
                mods=mods,
                sortie=regle.params.att_sortie.liste,
                v_sortie=valeur,
                ordre=ordre,
                type_base=type_base,
                chemin=chemin,
            )
        #    print ('regles alpha: valeur retour',retour,obj)
        return retour
    print("fdbalpha: base non definie ", base, regle.context, regle)
    return False
    # recup_donnees(stock_param,niveau,classe,attribut,valeur):


def f_dblast(regle, obj):
    """#aide||recupere les derniers enregistrements d 'une couche (superieur a une valeur min)
    #groupe||database
    #pattern||;;;dblast;C
    #pattern2||A;;;dblast
    #req_test||testdb

    """
    pass


def h_dbgeo(regle):
    """gestion des fonctions geographiques"""
    param_base(regle)
    regle.chargeur = True  # c est une regle qui cree des objets

    fonctions = ["intersect", "dans", "dans_emprise", "!intersect", "!dans", "!dans_emprise"]
    attribut = regle.v_nommees.get("val_sel2", "")
    valide = True
    if attribut not in fonctions:
        regle.erreurs.append("dbgeo: fonction inconnue seulement:" + ",".join(fonctions))
        valide = False
    if not valide_dbmods(regle.params.cmp1.liste):
        valide = False
        regle.erreurs.append(
            "dbalpha: modificateurs non autorises seulement:" + ",".join(DB.DBMODS)
        )
    return valide


def f_dbgeo(regle, obj):
    """#aide||recuperation d'objets depuis la base de donnees
    #aide_spec||db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;buffer
     #groupe||database
    #pattern||?A;?;?L;dbgeo;?C;?N
    #req_test||testdb
    """
    # regle.stock_param.regle_courante=regle
    base, niveau, classe, fonction, valeur, chemin, type_base = setdb(regle, obj, att=False)
    if not fonction:
        print("regle:dbgeo !!!!! pas de fonction geometrique", regle)
        return False
    else:
        retour = DB.recup_donnees_req_geo(
            regle,
            base,
            niveau,
            classe,
            fonction,
            obj,
            regle.params.cmp1.val,
            regle.params.att_sortie.liste,
            valeur,
            type_base=type_base,
            chemin=chemin,
        )
    return retour
    # recup_donnees(stock_param,niveau,classe,attribut,valeur):

def f_dbrequest(regle, obj):
    """#aide||recuperation d'objets depuis une requtere sur la base de donnees
    #aide_spec||db:base;niveau;classe;;att_sortie;valeurs;champ a integrer;dbreq;requete
    #groupe||database
    #pattern||?A;?;?L;dbgeo;C;?N
    #req_test||testdb
    """
    # regle.stock_param.regle_courante=regle
    base, niveau, classe, fonction, valeur, chemin, type_base = setdb(regle, obj, att=False)
    if not fonction:
        print("regle:dbgeo !!!!! pas de fonction geometrique", regle)
        return False
    else:
        retour = DB.lire_requete(regle, base, niveau, classe, requete='', parms=None)
    return retour
    # recup_donnees(stock_param,niveau,classe,attribut,valeur):


def f_dbclose(regle, obj):
    """#aide||recuperation d'objets depuis la base de donnees
     #groupe||database
    #pattern||;;;dbclose;;
    #req_test||testfiledb
    """
    base, _, _, _ = regle.cible_base
    if obj.attributs["#groupe"] == "__filedb":  # acces a une base fichier
        base = obj.attributs.get("#base", base)
        regle.setvar("db", obj.attributs.get("#type_base"))
        regle.setvar("server", obj.attributs.get("#chemin"))
    DB.dbclose(regle.stock_param, base)
    return True


def h_dbrunsql(regle):
    """execution de commandes"""
    regle.chargeur = True  # c est une regle qui cree des objets
    param_base(regle)


def f_dbrunsql(regle, obj):
    """#aide||lancement d'un script sql
  #aide_spec||parametres:base;;;;?nom;?variable contenant le nom;runsql;?log;?sortie
     #groupe||database
    #pattern||;?C;?A;runsql;?C;?C
    #req_test||testdb

    """
    base, _, _, _ = regle.cible_base
    script = regle.getval_entree(obj)
    print(
        "traitement db: execution sql ",
        base,
        "->",
        script,
        regle.params.cmp1.val,
        regle.params.cmp2.val,
    )
    if '*' in script or '?' in script:
        scripts = sorted(glob.glob(script))
    else:
        scripts = [script]
    if not scripts:
        print("pas de scripts a executer: ", script)
    for nom in scripts:
        if nom.startswith('#'): # c'est une commande sql interne
            nom = os.path.join(regle.getvar("_progdir"),'formats/db/sql',nom[1:])
        if not nom.endswith(".sql"):
            nom = nom + ".sql"
        # print("traitement sql ", nom)
        DB.dbextsql(
            regle, base, nom, log=regle.params.cmp1.val, out=regle.params.cmp2.val
        )

def h_dbrunproc(regle):
    """execution de commandes"""
    regle.chargeur = True  # c est une regle qui cree des objets
    param_base(regle)
    regle.procedure = 'select '+regle.params.cmp1.val+'()'

def f_dbrunproc(regle,obj):
    """#aide||lancement d'un procedure stockeee
  #aide_spec||parametres:base;;;;?arguments;?variable contenant les arguments;runsql;?log;?sortie
     #groupe||database
    #pattern||;?LC;?L;runproc;C;
    #req_test||testdb
    """
    base, _, _, _ = regle.cible_base
    params = regle.getval_entree(obj)
    print ('runproc',regle.procedure, params)
    DB.dbrunproc(regle, base, regle.procedure, params)

def h_dbextload(regle):
    """execution de commandes de chargement externe"""
    #    regle.chargeur = True # c est une regle qui cree des objets
    param_base(regle)


def f_dbextload(regle, obj):
    """#aide||lancement d'un chargement de base par un loader externe
  #aide_spec||parametres:base;;;;?nom;?variable contenant le nom;dbextload;log;
     #groupe||database
    #pattern||;?C;?A;dbextload;C;;
    #req_test||testdb
    """
    base, _, _, _ = regle.cible_base
    datas = regle.getval_entree(obj)
    #    print('traitement db: chargement donnees ', base, '->', datas, regle.params.cmp1.val)
    fichs = sorted(glob.glob(datas))
    retour = DB.dbextload(regle, base, fichs, log=regle.params.cmp1.val)
    print ('retour chargement:', retour)


#    for nom in fichs:
##        print('chargement donnees', nom)
#        DB.dbextload(regle, base, nom, log=regle.params.cmp1.val)


def h_dbextdump(regle):
    """execution de commandes de lecture externe"""
    #    regle.chargeur = True # c est une regle qui cree des objets
    param_base(regle)
    regle.chargeur = True  # c est une regle qui cree des objets


def f_dbextdump(regle, obj):
    """#aide||lancement d'une extraction par une extracteur externe
  #aide_spec||parametres:base;;;;;;dbextdump;dest;?log
     #groupe||database
    #pattern||;;;dbextdump;?C;?C
    #req_test||testdb
    """
    base, niveau, classe, _, _, chemin, type_base = setdb(regle, obj, att=False)
    dest = regle.params.cmp1.val
    if not dest:
        dest = regle.getvar("_sortie")
    os.makedirs(dest, exist_ok=True)
    log = regle.params.cmp2.val
    if not log:
        log = os.path.join(dest, "log")
    os.makedirs(log, exist_ok=True)

    print("traitement db: extraction donnees de", base, "vers", dest)

    return DB.dbextdump(regle, base, niveau, classe, dest=dest, log=log)


def f_dbwrite(regle, obj):
    """#aide||chargement en base de donnees
     #groupe||database
    #pattern||;;;dbwrite;;
   #req_test||testdb

    """
    base, niveau, classe, _ = regle.cible_base
    DB.dbload(regle, base, niveau, classe, obj)


def f_dbupdate(regle, obj):
    """#aide||chargement en base de donnees
     #groupe||database
    #pattern||;;;dbupdate;;
   #req_test||testdb
    """
    base, niveau, classe, attribut = regle.cible_base
    DB.dbupdate(regle, base, niveau, classe, attribut, obj)


def h_dbmaxval(regle):
    """ stocke la valeur maxi """
    param_base(regle)
    base, niveau, classe, attribut = regle.cible_base
    retour = DB.recup_maxval(regle, base, niveau, classe, attribut)
    if retour and len(retour) == 1 and regle.params.att_sortie.val:
        # cas simple on stocke l' attribut dans le parametre
        valeur = list(retour.values())[0]
        regle.stock_param.set_param(regle.params.att_sortie.val, str(valeur))
        print("maxval stockage", regle.params.att_sortie.val, str(valeur))
    nom = regle.params.cmp1.val if regle.params.cmp1.val else "#maxvals"
    regle.stock_param.store[nom] = retour
    regle.valide = "done"
    return True


def f_dbmaxval(regle, obj):
    """#aide||valeur maxi d une clef en base de donnees
     #groupe||database
    #pattern||?P;;;dbmaxval;?C;
    #req_test||testdb
    #test||rien||$#sigli;sigli;;||db:sigli;admin_sigli;description_fonctions;;P:toto;;;dbmaxval
            ||ptv;toto;71
    """
    pass


def h_dbcount(regle):
    """ recupere le nombre d'objets """
    retour = h_dbalpha(regle)
    regle.chargeur = False
    return retour


def f_dbcount(regle, obj):
    """#aide||nombre d'objets dans un groupe de tables
     #groupe||database
    #pattern||S;;;dbcount;?C;
   #req_test||testdb
       #test||obj||$#sigli;sigli;;||db:sigli;admin_sigli;description_fonctions;;toto;;;dbcount;
            ||atv;toto;64
    """
    base, niveau, classe, attrs, valeur, chemin, type_base = setdb(regle, obj)
    #    print ('regles cnt: setdb',base, niveau, classe, attrs, valeur, chemin, type_base)

    mods = regle.params.cmp1.liste

    LOGGER.debug("regles count:ligne  " + repr(regle) + repr(type_base) + repr(mods))

    if base:
        retour = DB.recup_count(
            regle,
            base,
            niveau,
            classe,
            attrs,
            valeur,
            mods=mods,
            type_base=type_base,
            chemin=chemin,
        )
        #        print ('regles cnt: valeur retour',retour,obj)
        obj.attributs[regle.params.att_sortie.val] = str(retour)
        return True
    print("dbcount: base non definie ", base)
    return False


# TODO meilleure gestion des schemas


def h_recup_schema(regle):
    """ lecture de schemas """
    if not param_base(regle):
        regle.valide = False
        return False
    regle.chargeur = True  # c est une regle a declencher

    nombase, niveau, classe, _ = regle.cible_base
    regle.setlocal('mode_schema','dbschema')

    if isinstance(nombase,list): # cas particulier des extractions multibases
        print ('detection extraction multibase',nombase)
        # raise
        regle.setlocal('autobase','1')

        for nom in nombase: # description schemas multibases
            nombase,val,host,port=nom

            print ('multibase:recup base',nombase,val,host,port)
            DB.recup_schema(regle, nombase, niveau, classe, nombase, description=nom)

        regle.valide = "done"
    else:
        regle.type_base = regle.getvar("db_" + nombase)
        if nombase:
            nomschema = regle.params.val_entree.val if regle.params.val_entree.val else nombase
            if regle.params.att_sortie.val == "schema_entree":
                regle.setvar("schema_entree", nomschema)
            if regle.params.att_sortie.val == "schema_sortie":
                regle.setvar("schema_sortie", nomschema)
            regle.valide = "done"
            print("h_recup_schema", nomschema, '->', nombase)
            DB.recup_schema(regle, nombase, niveau, classe, nomschema)
        return True


def f_recup_schema(regle, obj):
    """#aide||recupere les schemas des base de donnees
  #aide_spec||db:base;niveau;classe;;destination;nom_schema;;dbschema;select_tables;
     #groupe||database
   #pattern1||=schema_entree;C?;;dbschema;?;||sortie
   #pattern2||=schema_sortie;C?;;dbschema;?;||sortie
   #pattern3||=#schema;C?;A?;dbschema;?;||sortie
   #pattern4||;C?;A?;dbschema;?;
   #req_test||testdb
    """
    chemin = ""
    # print ('recup_schema---------------', obj)
    if obj.attributs.get("#categorie") == "traitement_virtuel":
        return True
    base, niveau, classe, att = regle.cible_base
    if obj.attributs["#groupe"] == "__filedb":
        chemin = obj.attributs["#chemin"]
        type_base = obj.attributs["#type_base"]
        if base != obj.attributs["#base"]:
            base = obj.attributs["#base"]
            regle.cible_base = (base, niveau, classe, att)
            DB.recup_schema(
                regle,
                base,
                niveau,
                classe,
                regle.get_entree(obj),
                type_base=type_base,
                chemin=chemin,
            )
            regle.setlocal("db", type_base)
            regle.setlocal("server", chemin)
            return True
    else:
        type_base = regle.type_base
    #        print('tdb: acces schema base', type_base, base, niveau, classe)
    #          regle.ligne,
    #          regle.params.val_entree.val,
    #          regle.params)
        if type_base and base:
            DB.recup_schema(
                regle,
                base,
                niveau,
                classe,
                regle.params.val_entree.val,
                type_base=type_base,
                chemin=chemin,
            )
            return True
    print("recup_schema: base non definie ",regle, type_base, base, obj)
    return False


def h_dbclean(regle):
    """prepare un script de reinitialisation d'une ensemble de tables """

    regle.chargeur = True  # c est une regle a declencher
    if not param_base(regle):
        regle.valide = False
        return False
    nombase, niveau, classe, _ = regle.cible_base

    regle.type_base = regle.getvar("db_" + nombase)

    base = nombase
    nom = regle.params.cmp2.val + ".sql"
    if base:
        script = DB.reset_liste_tables(regle, base, niveau, classe)
        if not os.path.isabs(nom):
            nom = os.path.join(regle.getvar('_sortie'),nom)
        if os.path.dirname(nom):
            os.makedirs(os.path.dirname(nom), exist_ok=True)
        print("ecriture script ", nom)
        with open(nom, "w") as sortie:
            sortie.write("".join(script))
        regle.valide = "done"
    else:
        print ('cible inconnue',regle.cible_base)


def f_dbclean(regle, obj):
    """#aide||vide un ensemble de tables
     #groupe||database
   #pattern1||;;;dbclean;?C;?C
      #req_test||testdb

   """

    pass
