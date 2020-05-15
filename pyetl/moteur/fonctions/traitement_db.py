# -*- coding: utf-8 -*-
"""
#titre||accés aux bases de données
fonctions de manipulation d'attributs
"""
import os
import logging
import glob

from itertools import zip_longest
import pyetl.formats.mdbaccess as DB
from .outils import prepare_mode_in
from .tableselector import TableSelector

LOGGER = logging.getLogger("pyetl")


def _mode_niv_in(regle, niv, autobase=False):
    """gere les requetes de type niveau in..."""
    print("mode_niv in:", niv, autobase)

    mode_in = "b" if autobase else "n"
    taille = 3 if autobase else 2
    mode_select, valeurs = prepare_mode_in(niv, regle, taille=taille, type_cle=mode_in)
    niveau = []
    classe = []
    attrs = []
    cmp = []
    base = []
    # selecteur = DB.TableSelector(regle)
    # for i in valeurs:
    #     selecteur.add_selector(*i)
    #     print("add_selector", i)
    for i in valeurs:
        liste_defs = list(i)
        # print("mode_niv in:liste_defs", liste_defs)
        bdef = liste_defs[0]
        if bdef in regle.stock_param.dbref:
            # c est une definition de base
            bdef = regle.stock_param.dbref.get(bdef)
        if autobase:
            base.append(bdef)
            liste_defs.pop(0)
        else:
            base.append("")

        niveau.append(liste_defs.pop(0) if liste_defs else "")
        classe.append(liste_defs.pop(0) if liste_defs else "")
        attrs.append(liste_defs.pop(0) if liste_defs else "")
        cmp.append(liste_defs.pop(0) if liste_defs else "")

    # print(
    #     "mode_niv in:lu ",
    #     "\n".join(str(i) for i in zip(base, niveau, classe, attrs, cmp)),
    # )
    return base, niveau, classe, attrs, cmp


def param_base(regle):
    """ extrait les parametres d acces a la base"""
    # TODO gerer les modes in dynamiques
    base = regle.code_classe[3:]
    autobase = False
    if base == "*" or base == "":
        base = ""
        autobase = True

    niveau, classe, att = "", "", ""
    niv = regle.v_nommees["val_sel1"]
    cla = regle.v_nommees["sel2"]
    att = regle.v_nommees["val_sel2"]
    attrs = []
    cmp = []
    print("param_base", base, niv, cla, "autobase:", autobase)

    if niv.lower().startswith("in:"):  # mode in
        b_lue, niveau, classe, attrs, cmp = _mode_niv_in(
            regle, niv[3:], autobase=autobase
        )
        if autobase:
            base = b_lue
        else:
            base = [base] * len(niveau)
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
        att = [(i, j) for i, j in zip(attrs, cmp)]

    regle.dyn = "#" in niv or "#" in cla
    print("parametres acces base", base, niveau, classe, att, regle)

    # gestion multibase
    if isinstance(base, list):
        multibase = {i: ([], [], []) for i in set(base)}
        for b, n, c, a in zip(base, niveau, classe, att):
            # print("traitement", b, n, c, a)
            nl, cl, al = multibase[b]
            nl.append(n)
            cl.append(c)
            al.append(a)
        regle.cible_base = multibase
        # print("retour multibase", multibase)
    else:
        regle.cible_base = {base: (niveau, classe, att)}
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
        defaut = regle.v_nommees.get(
            "defaut", ""
        )  # on utilise in comme selecteur attributaire
        if defaut[:3].lower() == "in:":
            mode_multi, valeurs = prepare_mode_in(
                regle.v_nommees["defaut"][3:], regle, taille=1
            )
            regle.params.val_entree = regle.params.st_val(
                defaut, None, list(valeurs.keys()), False, ""
            )
        regle.chargeur = True  # c est une regle qui cree des objets
        if regle.getvar("noauto"):  # mais on veut pas qu'elle se declenche seule
            regle.chargeur = False
        #        regle.stock_param.gestion_parallel_load(regle)
        if valide_dbmods(regle.params.cmp1.liste):
            return True
        regle.erreurs.append(
            "dbalpha: modificateurs non autorises seulement:", DB.DBMODS
        )
        return False
    print("erreur regle", regle)
    regle.erreurs.append("dbalpha: erreur base non definie")
    return False


def setdb(regle, obj, att=True):
    """positionne des parametres d'acces aux bases de donnees"""
    # print("acces base", regle.cible_base.keys())
    basedict = dict()
    for base, (niveau, classe, attribut) in regle.cible_base.items():
        attrs = []
        cmp = []
        type_base = None
        chemin = ""
        if att:  # (tri sur attribut si necessaire)
            if attribut:  # attention il y a des definitions d'attributs
                if isinstance(attribut, tuple):
                    attrs, cmp = attribut
                else:
                    attrs = attribut
        else:  # traitement sans gestion des attributs (geometrique ou dump)
            attrs = attribut
        #    print ('f_alpha :',attrs, cmp)
        if obj.attributs["#groupe"] == "__filedb":  # acces a une base fichier

            chemin = obj.attributs["#chemin"]
            if not base:
                base = obj.attributs["#base"]
            type_base = obj.attributs["#type_base"]
            regle.setvar("db", type_base)
            regle.setvar("server", chemin)
        # print("regles alpha: acces base ", base, niveau, classe, attribut, type_base)

        if niveau and niveau[0].startswith(
            "["
        ):  # nom de classe contenu dans un attribut
            niveau = [
                obj.attributs.get(niveau[0][1:-1], "niveau non defini " + niveau[0])
            ]
        if classe and classe[0].startswith(
            "["
        ):  # nom de classe contenu dans un attribut
            classe = [
                obj.attributs.get(
                    classe[0][1:-1],
                    "attribut non defini "
                    + ".".join(obj.ident)
                    + " "
                    + classe[0][1:-1],
                )
            ]
        if regle.params.att_entree.liste:
            #        print('on a mis un attribut', regle.params.att_entree.liste)
            valeur = [
                obj.attributs.get(a, d)
                for a, d in zip_longest(
                    regle.params.att_entree.liste, regle.params.val_entree.liste
                )
            ]
        elif regle.params.val_entree.liste:
            valeur = regle.params.val_entree.liste
        else:
            valeur = cmp
        # bd2 = DB.TableSelector(regle.stock_param)
        if isinstance(base, list):
            for numero, idbase in enumerate(base):
                # bd2.add_selector(idbase, basedict[idbase])
                if idbase in basedict:
                    niv, cla, attr, val, chm, typ = basedict[idbase]
                    niv.extend(niveau[numero])
                    cla.extend(classe[numero])
                    attr.extend(attrs[numero])
                    val.extend(valeur[numero])
                    basedict[idbase] = (niv, cla, attr, val, chm, typ)
                else:
                    basedict[idbase] = (
                        niveau,
                        classe,
                        attrs,
                        valeur,
                        chemin,
                        type_base,
                    )
        else:
            basedict[base] = (niveau, classe, attrs, valeur, chemin, type_base)
    return basedict
    # return (base, niveau, classe, attrs, valeur, chemin, type_base)


def f_dbalpha(regle, obj):
    """#aide||recuperation d'objets depuis la base de donnees
     #groupe||database
    #pattern||?A;?;?;dbalpha;?;?
    #req_test||testdb

    """
    if not regle.getvar("traitement_virtuel"):
        if obj.virtuel and obj.attributs.get("#categorie") == "traitement_virtuel":
            # print ('detection traitement virtuel : on ignore', obj, regle.getvar('traitement_virtuel'), regle.context.vlocales)
            return False

    # bases, niveau, classe, attrs, valeur, chemin, type_base = setdb(regle, obj)
    basedict = setdb(regle, obj)
    mods = regle.params.cmp1.liste
    ordre = regle.params.cmp2.liste
    # print("regles alpha: acces base apres ", basedict)

    #    print('regles alpha:ligne  ', regle, type_base, mods)
    #    print('regles alpha:parms:', base, niveau, classe, attribut, 'entree:',regle.params.val_entree,
    #          valeur, 'cmp1:', regle.params.cmp1, 'sortie:', regle.params.att_sortie)

    #    print ('regles alpha: ','\n'.join(str(i) for i in (zip(niveau,classe,attrs,cmp))), valeur)

    if not basedict:
        print("fdbalpha: base non definie ", regle.context, regle)
        return False
    retour = 0
    print("dbalpha", basedict.keys())
    for base, description in basedict.items():
        print("lecture base", base)
        niveau, classe, attrs, valeur, chemin, type_base = description
        LOGGER.debug("regles alpha:ligne " + repr(regle) + repr(type_base) + repr(mods))
        connect = regle.stock_param.getdbaccess(regle, base, type_base=type_base)
        if connect is None:
            print("erreur connection:", base)
            continue
        if connect.accept_sql == "non":
            # pas de requetes directes on essaye le mode dump
            dest = regle.getvar("dest")
            if not dest:
                dest = os.path.join(regle.getvar("_sortie"), "tmp")
            os.makedirs(dest, exist_ok=True)
            regle.setvar("_entree", dest)
            log = regle.getvar("log", os.path.join(dest, "log_extraction.log"))
            os.makedirs(os.path.dirname(log), exist_ok=True)
            print("traitement db: dump donnees de", base, "vers", dest)
            retour = DB.dbextalpha(regle, base, niveau, classe, dest=dest, log=log)
        else:
            retour += DB.recup_donnees_req_alpha(
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
            # print("regles alpha: valeur retour", retour, obj)
    return retour

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

    fonctions = [
        "intersect",
        "dans",
        "dans_emprise",
        "!intersect",
        "!dans",
        "!dans_emprise",
    ]
    attribut = regle.v_nommees.get("val_sel2", "")
    valide = True
    if attribut not in fonctions:
        regle.erreurs.append(
            "dbgeo: fonction inconnue seulement:" + ",".join(fonctions)
        )
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
    # base, niveau, classe, fonction, valeur, chemin, type_base = setdb(
    #     regle, obj, att=False
    # )
    basedict = setdb(regle, obj, att=False)
    retour = 0
    for base, description in basedict.items():
        niveau, classe, fonction, valeur, chemin, type_base = description
        if not fonction:
            print("regle:dbgeo !!!!! pas de fonction geometrique", regle)
        else:
            retour += DB.recup_donnees_req_geo(
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


def h_dbrequest(regle):
    """passage direct de requetes"""
    param_base(regle)
    regle.chargeur = True  # c est une regle qui cree des objets
    attribut = regle.v_nommees.get("val_sel2", "")
    requete = regle.params.cmp1.val
    regle.fich = "tmp"
    regle.grp = "tmp"
    if requete.startswith("F:"):  # lecture requete en fichier
        nom_fich = requete[2:]
        regle.fich = os.path.basename(os.path.splitext(nom_fich)[0])
        regle.grp = os.path.basename(os.path.dirname(nom_fich))
        with open(requete[2:], "r") as fich:
            requete = "".join(fich.readlines())
    maxi = regle.getvar("lire_maxi")
    if maxi and maxi != "0":
        try:
            vmax = int(maxi)
            limit = " LIMIT " + str(maxi)
            requete = requete + limit
        except ValueError:
            pass
    regle.requete = requete

    valide = True
    return valide


def f_dbrequest(regle, obj):
    """#aide||recuperation d'objets depuis une requete sur la base de donnees
    #aide_spec||db:base;niveau;classe;;att_sortie;valeurs;champ a integrer;dbreq;requete
    #groupe||database
    #pattern||?A;?;?L;dbreq;C
    #req_test||testdb
    #
    """
    # regle.stock_param.regle_courante=regle
    # base, niveau, classe, attribut, valeur, chemin, type_base = setdb(
    #     regle, obj, att=False
    # )
    basedict = setdb(regle, obj, att=False)
    retour = 0
    for base, description in basedict.items():
        niveau, classe, fonction, valeur, chemin, type_base = description
        # parms = [regle.getv]
        # print("execution requete", regle.params.cmp1.val, niveau, classe)
        parms = None
        if regle.params.att_entree.liste:
            parms = [obj.attributs.get(i, "") for i in regle.params.att_entree.liste]
        retour = DB.lire_requete(
            regle, base, niveau, classe, requete=regle.requete, parms=parms
        )
    return retour
    # recup_donnees(stock_param,niveau,classe,attribut,valeur):


def f_dbclose(regle, obj):
    """#aide||recuperation d'objets depuis la base de donnees
     #groupe||database
    #pattern||;;;dbclose;;
    #req_test||testfiledb
    """
    for base in regle.cible_base:
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
    for base in regle.cible_base:
        script = regle.getval_entree(obj)
        print(
            "traitement db: execution sql ",
            base,
            "->",
            script,
            regle.params.cmp1.val,
            regle.params.cmp2.val,
        )
        if "*" in script or "?" in script:
            scripts = sorted(glob.glob(script))
        else:
            scripts = [script]
        if not scripts:
            print("pas de scripts a executer: ", script)
        for nom in scripts:
            if nom.startswith("#"):  # c'est une commande sql interne
                nom = os.path.join(regle.getvar("_progdir"), "formats/db/sql", nom[1:])
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
    regle.procedure = "select " + regle.params.cmp1.val + "()"


def f_dbrunproc(regle, obj):
    """#aide||lancement d'un procedure stockeee
  #aide_spec||parametres:base;;;;?arguments;?variable contenant les arguments;runsql;?log;?sortie
     #groupe||database
    #pattern||;?LC;?L;runproc;C;
    #req_test||testdb
    """
    for base in regle.cible_base:
        params = regle.getval_entree(obj)
        print("runproc", regle.procedure, params)
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
    for base in regle.cible_base:
        datas = regle.getval_entree(obj)
        #    print('traitement db: chargement donnees ', base, '->', datas, regle.params.cmp1.val)
        fichs = sorted(glob.glob(datas))
        retour = DB.dbextload(regle, base, fichs, log=regle.params.cmp1.val)
        print("retour chargement:", retour)


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
    # base, niveau, classe, _, _, chemin, type_base = setdb(regle, obj, att=False)
    basedict = setdb(regle, obj, att=False)
    retour = 0
    for base, description in basedict.items():
        niveau, classe, fonction, valeur, chemin, type_base = description
        dest = regle.params.cmp1.val
        if not dest:
            dest = regle.getvar("_sortie")
        os.makedirs(dest, exist_ok=True)
        log = regle.params.cmp2.val
        if not log:
            log = os.path.join(dest, "log")
        os.makedirs(log, exist_ok=True)

        print("traitement db: extraction donnees de", base, "vers", dest)

        DB.dbextdump(regle, base, niveau, classe, dest=dest, log=log)
    return True


def f_dbwrite(regle, obj):
    """#aide||chargement en base de donnees
     #groupe||database
    #pattern||;;;dbwrite;;
   #req_test||testdb

    """
    for base, (niveau, classe, _) in regle.cible_base.items():
        DB.dbload(regle, base, niveau, classe, obj)


def f_dbupdate(regle, obj):
    """#aide||chargement en base de donnees
     #groupe||database
    #pattern||;;;dbupdate;;
   #req_test||testdb
    """
    for base, (niveau, classe, attribut) in regle.cible_base.items():
        DB.dbupdate(regle, base, niveau, classe, attribut, obj)


def h_dbmaxval(regle):
    """ stocke la valeur maxi """
    param_base(regle)
    for base, (niveau, classe, attribut) in regle.cible_base.items():
        retour = DB.recup_maxval(regle, base, niveau, classe, attribut)
        print("retour maxval", retour)
        if retour and len(retour) == 1 and regle.params.att_sortie.val:
            # cas simple on stocke l' attribut dans le parametre
            valeur = list(retour.values())[0]
            regle.setvar(regle.params.att_sortie.val, str(valeur))
            print(
                "maxval stockage",
                regle.params.att_sortie.val,
                str(valeur),
                regle.getvar,
            )
        nom = regle.params.cmp1.val if regle.params.cmp1.val else "#maxvals"
        regle.stock_param.store[nom] = retour
        regle.valide = "done"
    return True


def f_dbmaxval(regle, obj):
    """#aide||valeur maxi d une clef en base de donnees
     #groupe||database
    #pattern||?P;;;dbmaxval;?C;
    #req_test||testdb
    #test||rien||$#testdb;;||$toto=1||db:testdb;testschema;tablealpha;col3;P:toto;;;dbmaxval
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
       #test||obj||$#testdb;;||db:testdb;testschema;tablealpha;;toto;;;dbcount;
            ||atv;toto;3
    """
    # base, niveau, classe, attrs, valeur, chemin, type_base = setdb(regle, obj)
    #    print ('regles cnt: setdb',base, niveau, classe, attrs, valeur, chemin, type_base)

    mods = regle.params.cmp1.liste

    basedict = setdb(regle, obj, att=False)
    retour = 0
    for base, description in basedict.items():
        niveau, classe, attrs, valeur, chemin, type_base = description
        LOGGER.debug(
            "regles count:ligne  " + repr(regle) + repr(type_base) + repr(mods)
        )

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


# TODO meilleure gestion des schemas


def h_recup_schema(regle):
    """ lecture de schemas """
    if not param_base(regle):
        print("erreur definition selecteur de base", regle.v_nommees)
        regle.valide = False
        return False
    regle.chargeur = True  # c est une regle a declencher

    regle.setlocal("mode_schema", "dbschema")
    for nombase, (niveau, classe, _) in regle.cible_base.items():
        regle.type_base = regle.getvar("db_" + nombase)
        nomschema = (
            regle.params.val_entree.val if regle.params.val_entree.val else nombase
        )
        if regle.params.att_sortie.val == "schema_entree":
            regle.setvar("schema_entree", nomschema)
        if regle.params.att_sortie.val == "schema_sortie":
            regle.setvar("schema_sortie", nomschema)
        regle.valide = "done"
        print("h_recup_schema", nomschema, "->", nombase, regle.valide)
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
    valide = True
    for base, (niveau, classe, _) in regle.cible_base.items():
        if obj.attributs["#groupe"] == "__filedb":
            chemin = obj.attributs["#chemin"]
            type_base = obj.attributs["#type_base"]
            if base != obj.attributs["#base"]:
                base = obj.attributs["#base"]
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
    if valide:
        return True
    print("recup_schema: base non definie ", regle, type_base, base, obj)
    return False


def h_dbclean(regle):
    """prepare un script de reinitialisation d'une ensemble de tables """

    regle.chargeur = True  # c est une regle a declencher
    if not param_base(regle):
        regle.valide = False
        return False
    for base, (niveau, classe, _) in regle.cible_base.items():

        regle.type_base = regle.getvar("db_" + base)

        nom = regle.params.cmp2.val + ".sql"
        if len(regle.cible_base) > 1:
            nom = os.path.join(os.path.dirname(nom), base + "_" + os.path.basename(nom))
        script = DB.reset_liste_tables(regle, base, niveau, classe)
        if not os.path.isabs(nom):
            nom = os.path.join(regle.getvar("_sortie"), nom)
        if os.path.dirname(nom):
            os.makedirs(os.path.dirname(nom), exist_ok=True)
        print("ecriture script ", nom)
        with open(nom, "w") as sortie:
            sortie.write("".join(script))
        regle.valide = "done"
    return True


def f_dbclean(regle, obj):
    """#aide||vide un ensemble de tables
     #groupe||database
   #pattern1||;;;dbclean;?C;?C
      #req_test||testdb

   """

    pass
