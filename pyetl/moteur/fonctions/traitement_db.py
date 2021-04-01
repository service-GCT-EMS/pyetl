# -*- coding: utf-8 -*-
"""
#titre||accés aux bases de données
fonctions de manipulation d'attributs
"""
import os
import logging
import glob

# from pyetl.formats.db.database import DbConnect
import re
import datetime

from itertools import zip_longest
import pyetl.formats.mdbaccess as DB
from pyetl.formats.interne.objet import Objet

from .outils import prepare_mode_in
from .tableselector import getselector, select_in, adapt_qgs_datasource

LOGGER = logging.getLogger(__name__)


def getbase(regle):
    """recuper le code base our les ecritures"""
    regle.base = regle.code_classe[3:]
    return regle.base


def param_base(regle, nom="", geo=False, req=False, mods=True):
    """ extrait les parametres d acces a la base"""
    # TODO gerer les modes in dynamiques
    base = regle.code_classe[3:]
    if not base:
        base = "*"
    if base.startswith("#"):  # c'est un selecteur nomme
        nom = base[1:]
        selecteur = regle.stock_param.namedselectors.get(nom)
        if not selecteur:
            raise KeyError("selecteur inconnu ", nom)
        regle.cible_base = selecteur
        return True
    niveau, classe, att = "", "", ""
    niv = regle.v_nommees["val_sel1"]
    cla = regle.v_nommees["sel2"]
    att = regle.v_nommees["val_sel2"]
    vals = (regle.v_nommees["entree"], regle.v_nommees["defaut"])
    if mods:
        regle.mods = regle.params.cmp1.val
    else:
        regle.mods = regle.context.getlocal("mods")
    fonction = "=" if "=" in regle.mods else ""
    if geo:
        fonction = att
        att = ""
        vals = regle.params.att_entree.liste
    if req:
        vals = ""
    LOGGER.debug("info base %s ", repr(regle))
    # print("param_base", regle, "-", nom, base, niv, cla, att, vals)

    if niv.lower().startswith("in:"):  # mode in
        selecteur = select_in(regle, niv[3:], base, nom=nom)
        # print("recup selecteur", selecteur)
    else:
        selecteur = getselector(regle, base, nom=nom)
        selecteur.metainfos = ("niveau=" + niv if niv else "") + (
            " classe=" + cla if cla else ""
        )
        if cla.lower().startswith("in:"):  # mode in
            clef = 1 if "#schema" in cla else 0
            mode_select, classes = prepare_mode_in(cla[3:], regle, taille=1, clef=clef)
        else:
            classes = cla.split(",")
        if niv:
            for niveau in niv.split(","):
                if "." in niveau:
                    tmp = niveau.split(".")
                    if len(tmp) == 2:
                        n, c = niveau.split(".")
                        b = base
                    else:
                        b, n, c = niveau.split(".")
                    selecteur.add_descripteur(b, n, c, att, vals, fonction)
                else:
                    selecteur.add_descripteur(
                        base, niveau, classes, att, vals, fonction
                    )
        else:
            selecteur.add_descripteur(base, niveau, classes, att, vals, fonction)

    regle.cible_base = selecteur

    return True


def setdb(regle, obj):
    """positionne des parametres d'acces aux bases de donnees"""
    # print("acces base", regle.cible_base.keys())
    selecteur = regle.cible_base
    if selecteur:
        selecteur.resolve(obj)
    return selecteur
    # return (base, niveau, classe, attrs, valeur, chemin, type_base)


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
            regle.setlocal("noauto", regle.getvar("noauto"))  # on confine en local
            regle.chargeur = False
        #        regle.stock_param.gestion_parallel_load(regle)
        if valide_dbmods(regle.params.cmp1.liste):
            regle.mods = regle.params.cmp1.liste
            return True
        regle.erreurs.append(
            "dbalpha: modificateurs non autorises seulement:"
            + str(regle.params.cmp1.liste)
            + ":"
            + str(DB.DBMODS)
        )
        return False
    print("erreur regle", regle)
    regle.erreurs.append("dbalpha: erreur base non definie")
    return False


def f_dbalpha(regle, obj):
    """#aide||recuperation d'objets depuis la base de donnees
     #groupe||database
    #pattern||?A;?;?;dbalpha;?;?
    #parametres||;defaut;entree;dbalpha;precisions;ordre
    #dbparams||base;schema;table;attribut;valeur
    #variables||traitement_virtuel;se declenche pour un objet virtuel
            ||dest;repertoire temporaire si extracteur externe
    #req_test||testdb
    """
    if not regle.getvar("traitement_virtuel"):
        if obj.virtuel and obj.attributs.get("#categorie") == "traitement_virtuel":
            # print ('detection traitement virtuel : on ignore', obj, regle.getvar('traitement_virtuel'), regle.context.vlocales)
            return False

    # bases, niveau, classe, attrs, valeur, chemin, type_base = setdb(regle, obj)
    selecteur = setdb(regle, obj)
    if not selecteur:
        return False
    if selecteur.nobase:  # on ne fait rien pour le test
        return True
    ordre = regle.params.cmp2.liste
    # print("dbalpha: acces base ", selecteur)
    retour = 0
    # print("dbalpha", basedict.keys())
    # selecteur.resolve(regle, obj)
    regle.liste_sortie = [obj.attributs.get(i) for i in regle.params.att_entree.liste]
    for base, basesel in selecteur.baseselectors.items():

        LOGGER.debug(
            "regles alpha:ligne " + repr(regle) + basesel.type_base + repr(regle.mods)
        )
        # connect = regle.stock_param.getdbaccess(regle, base, type_base=type_base)
        connect = basesel.connect

        if connect.accept_sql == "non":
            # pas de requetes directes on essaye le mode dump
            dest = regle.getvar("dest")
            if not dest:
                dest = os.path.join(regle.getvar("_sortie"), "tmp")
            os.makedirs(dest, exist_ok=True)
            regle.setvar("_entree", dest)
            log = regle.getvar("log", os.path.join(dest, "log_extraction.log"))
            os.makedirs(os.path.dirname(log), exist_ok=True)
            LOGGER.info("dump donnees de %s vers %s", base, dest)
            # print("traitement db: dump donnees de", base, "vers", dest)
            retour = DB.dbextalpha(regle, basesel, dest=dest, log=log)
        else:
            retour += DB.recup_donnees_req_alpha(regle, basesel)
            # print("regles alpha: valeur retour", retour, obj)
    return retour

    # recup_donnees(stock_param,niveau,classe,attribut,valeur):


def h_dbtmp(regle):
    """creation de structures temporaires"""
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
        if not valide_dbmods(regle.params.cmp1.liste):

            regle.erreurs.append(
                "dbtmp: modificateurs non autorises seulement:"
                + str(regle.params.cmp1.liste)
                + ":"
                + str(DB.DBMODS)
            )
            return False
        destbase = regle.params.cmp2.val
        if not destbase:
            print("erreur pas de base destination")
        regle.valide = 'done"'

    print("erreur regle", regle)
    regle.erreurs.append("dbtmp: erreur base non definie")
    return False
    pass


def f_dbtmp(regle, obj):
    """#aide||creation de structures temporaires dans la base de donnees permets de preparer les requetes
     #groupe||database
    #pattern||?A;?;?;dbtmp;?;?
    #req_test||testdb

    """
    pass


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
    param_base(regle, geo=True)
    regle.chargeur = True  # c est une regle qui cree des objets
    fonctions = [
        "intersect",
        "dans",
        "dans_emprise",
        "!intersect",
        "!dans",
        "!dans_emprise",
    ]
    regle.fonction_geom = regle.v_nommees.get("val_sel2", "")
    valide = True
    if regle.fonction_geom not in fonctions:
        regle.erreurs.append(
            "dbgeo: fonction geometrique inconnue " + regle.fonction_geom
        )
        valide = False

    if not valide_dbmods(regle.params.cmp1.liste):
        valide = False
        regle.erreurs.append(
            "dbalpha: modificateurs non autorises seulement:" + ",".join(DB.DBMODS)
        )
    if not regle.params.att_sortie.val:
        regle.params.att_sortie.liste = regle.params.att_entree.liste
    return valide


def f_dbgeo(regle, obj):
    """#aide||recuperation d'objets depuis la base de donnees
    #aide_spec||db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;buffer
     #groupe||database
    #pattern||?L;?;?L;dbgeo;?C;?N
    #req_test||testdb
    """

    selecteur = setdb(regle, obj)
    retour = 0
    for base, basesel in selecteur.baseselectors.items():
        connect = basesel.connect
        # niveau, classe, fonction, valeur, chemin, type_base = description
        if not regle.fonction_geom:
            print("regle:dbgeo !!!!! pas de fonction geometrique", regle)
        else:
            retour += DB.recup_donnees_req_geo(
                regle,
                basesel,
                obj,
            )
    return retour
    # recup_donnees(stock_param,niveau,classe,attribut,valeur):


def getrequest(regle):
    "lit une requete sql et l analyse"
    requete = regle.params.cmp1.val
    regle.fich = "tmp"
    regle.grp = "tmp"
    if requete.startswith("F:"):  # lecture requete en fichier
        nom_fich = requete[2:]
        regle.fich = os.path.basename(os.path.splitext(nom_fich)[0])
        regle.grp = os.path.basename(os.path.dirname(nom_fich))
        try:
            with open(requete[2:], "r", encoding="utf-8-sig") as fich:
                requete = "".join(fich.readlines())
        except FileNotFoundError:
            # LOGGER.error("fichier de requetes introuvable %s",requete[2:])
            regle.valide = False
            regle.erreurs = "fichier introuvable ->" + requete[2:]
            return False
    maxi = regle.getvar("lire_maxi")
    if maxi and maxi != "0":
        try:
            vmax = int(maxi)
            limit = " LIMIT " + str(maxi)
            requete = requete + limit
        except ValueError:
            pass
    regle.requete = requete
    regle.dynrequete = "%#" in requete
    # la requete depends de elements du selecteur
    return True


def h_dbrequest(regle):
    """passage direct de requetes"""
    param_base(regle, mods=False, req=True)
    regle.chargeur = regle.params.pattern not in "34"
    # c est une regle qui cree des objets si on est pas en mode completement
    attribut = regle.v_nommees.get("val_sel2", "")
    requete = regle.params.cmp1.val
    regle.fich = "tmp"
    regle.grp = "tmp"
    valide = getrequest(regle)
    if regle.params.cmp2.val:
        regle.identclasse = (
            (regle.params.cmp2.val, regle.params.cmp2.definition[0])
            if regle.params.cmp2.definition
            else (None, regle.params.cmp2.val)
        )
    else:
        regle.identclasse = None
    LOGGER.debug("req:%s --> %s", requete, str(regle.identclasse))

    regle.prefixe = regle.params.att_sortie.val
    return valide


def printexception(regle, err):
    """ affiche ou pas une erreur"""
    fail_silent = regle.getvar("Fail_silent", False)
    if not fail_silent or fail_silent == "0" or fail_silent.lower() == "false":
        print("erreur requete", err)


def f_dbrequest(regle, obj):
    """#aide||recuperation d'objets depuis une requete sur la base de donnees
    #parametres||att_sortie;valeurs;champ a integrer;dbreq;requete;destination
     #dbparams||db:base;niveau;classe;attr
    #aide_spec||si la requete contient %#niveau ou %#classe la requete est passee sur chaque
              ||classe du selecteur en substituant les variables par la classe courante
              ||sinon elle est passee une fois pour chaque base du selecteur
              ||les variables %#base et %#attr sont egalement substituees
       #groupe||database
      #pattern1||?A;?;?L;dbreq;C;?A.C
      #pattern2||?A;?;?L;dbreq;C;?A
      #pattern3||;;=#;dbreq;C;?A
      #pattern4||;;=#;dbreq;C;?A.C
     #req_test||testdb
    """

    selecteur = setdb(regle, obj)
    retour = 0
    parms = None
    if regle.params.att_entree.liste:
        parms = [obj.attributs.get(i, "") for i in regle.params.att_entree.liste]
    refobj = obj if regle.params.pattern in "34" else None
    for base, basesel in selecteur.baseselectors.items():
        requete_ref = regle.requete.replace("%#base", base)
        # print("requete dynamique", regle.dynrequete, len(list(basesel.classlist())))
        if regle.dynrequete:
            for resultat, definition in basesel.classlist():
                identclasse, att, *_ = definition
                niveau, classe = identclasse
                # parms = [regle.getv]
                # print("execution requete", niveau, classe, definition)
                # print("metas", basesel.schemabase.metas)

                requete = requete_ref.replace("%#niveau", niveau)
                requete = requete.replace("%#classe", classe)
                requete = requete.replace("%#attr", att)
                schemaclasse = basesel.schemabase.get_classe(identclasse)
                while "%#info" in requete:
                    # acces a des infos schema
                    match = re.search("%#info\[(.*)\]", requete)
                    if match:
                        nom_info = match.group(1)
                        val_info = schemaclasse.getinfo(nom_info).replace("'", "''")
                        requete = requete.replace(match.group(), val_info)
                    else:
                        LOGGER.error("chaine mal formee %s", requete)
                        raise StopIteration(2)
                metas = basesel.schemabase.metas
                while "%#meta" in requete and metas:
                    # acces a des infos schema
                    match = re.search("%#meta\[(.*)\]", requete)
                    if match:
                        nom_info = match.group(1)
                        val_info = metas.get(nom_info).replace("'", "''")
                        requete = requete.replace(match.group(), val_info)
                    else:
                        LOGGER.error("chaine mal formee %s", requete)
                        raise StopIteration(2)
                if regle.identclasse is not None:
                    idsortie = regle.identclasse
                    if idsortie[0] is None:
                        idsortie = (niveau, regle.identclasse[1])
                elif refobj:
                    idsortie = refobj.ident
                else:
                    idsortie = identclasse
                # print("execution requete", niveau, classe, requete, "->", idsortie)
                try:
                    retour += DB.lire_requete(
                        regle,
                        base,
                        idsortie,
                        requete=requete,
                        parms=parms,
                        obj=refobj,
                    )
                except Exception as err:
                    printexception(regle, err)
                    continue
        else:
            try:
                retour += DB.lire_requete(
                    regle,
                    base,
                    regle.ident if regle.ident is not None else ("tmp", "tmp"),
                    requete=requete_ref,
                    parms=parms,
                    obj=refobj,
                )
            except Exception as err:
                printexception(regle, err)
                continue
    obj.attributs["#nb_results"] = str(retour)
    return retour


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
            regle.setvar("server", obj.attributs.get("#racine"))
        DB.dbclose(regle.stock_param, base)
    return True


def h_dbrunsql(regle):
    """execution de commandes"""
    regle.chargeur = True  # c est une regle qui cree des objets
    param_base(regle)


def f_dbrunsql(regle, obj):
    """#aide||lancement d'un script sql via un loader externe
    #aide_spec||parametres:base;;;;?nom;?variable contenant le nom;runsql;?log;?sortie
       #groupe||database
      #pattern||;?C;?A;runsql;?C;?C
      #req_test||testdb

    """
    selecteur = setdb(regle, obj)
    for base in selecteur.baseselectors:
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
    selecteur = setdb(regle, obj)
    for base in selecteur.baseselectors:
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
    base = regle.cible_base.base
    datas = regle.getval_entree(obj)
    #    print('traitement db: chargement donnees ', base, '->', datas, regle.params.cmp1.val)
    fichs = sorted(glob.glob(datas))
    retour = DB.dbextload(regle, base, fichs, log=regle.params.cmp1.val)
    print("retour chargement:", retour)


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
    selecteur = setdb(regle, obj)
    dest = regle.params.cmp1.val or regle.getvar("_sortie")
    os.makedirs(dest, exist_ok=True)
    log = regle.params.cmp2.val or "log"
    LOGGER.info("extraction donnees de vers %s", dest)
    # print("traitement db: extraction donnees de vers", dest)
    for base, baseselector in selecteur.baseselectors.items():
        DB.dbextdump(regle, base, baseselector, dest=dest, log=log)
    return True


def dbwritebloc(regle):
    """ecrit un bloc en base"""
    connect = regle.connect
    if not connect:
        connect = regle.stock_param.getdbaccess(regle, regle.base)
        if connect is None:
            LOGGER.error("connection impossible a la base %s", regle.base)
            raise StopIteration(2)
    schema = regle.schema
    connect.dbload(schema, regle.dident, regle.tmpstore)
    regle.nbstock = 0
    regle.traite += len(regle.tmpstore)
    regle.tmpstore = []


def h_dbwrite(regle):
    """ preparation ecriture en base """
    regle.blocksize = int(regle.getvar("transaction_size", 1000))
    regle.store = True
    regle.nbstock = 0
    regle.traite = 0
    regle.traite_stock = dbwritebloc
    regle.tmpstore = []
    regle.connect = None
    regle.colonnes = None
    regle.dident = None
    if not getbase(regle):
        LOGGER.error("base non definie")
        return False
    return True


def f_dbwrite(regle, obj):
    """#aide||chargement en base de donnees en bloc
      #groupe||database
     #pattern||;;;dbwrite;;
    #req_test||testdb
    """
    ident = obj.ident
    if regle.dident != ident:
        regle.traite_stock()
        regle.dident = ident
        regle.liste_att = tuple((i for i in obj.schema.get_liste_attributs()))
        regle.colonnes = (
            regle.liste_att + ("geometrie",)
            if obj.schema.type_geom != "0"
            else regle.liste_att
        )
        regle.has_geom = obj.schema.type_geom != "0"
    if regle.nbstock >= regle.blocksize:
        regle.traite_stock()
    ligne = tuple((obj.attributs[i]) for i in regle.liste_att)
    if regle.has_geom:
        ligne = ligne + obj.geometrie
    regle.tmpstore.append(ligne)


def f_dbupdate(regle, obj):
    """#aide||chargement en base de donnees
      #groupe||database
     #pattern||;;;dbupdate;;
    #req_test||testdb
    """
    for base, (niveau, classe, attributs) in regle.cible_base.items():
        DB.dbupdate(regle, base, niveau, classe, attributs, obj)


def h_dbmaxval(regle):
    """ stocke la valeur maxi """
    param_base(regle)
    selecteur = regle.cible_base
    regle.dyndescriptors = False
    for base, basesel in selecteur.baseselectors.items():
        if basesel.dyndescr:
            regle.dyndescriptors = True

        retour = DB.recup_maxval(regle, base, basesel)
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
    #pattern1||P;;;dbmaxval;?C;
    #pattern2||A;;;dbmaxval;?C;
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

    selecteur = setdb(regle, obj)
    retour = 0
    for base, ident in selecteur.get_classes():
        niveau, classe = ident
        LOGGER.debug("regles count:ligne  " + repr(regle) + repr(base) + repr(mods))

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
    selecteur = regle.cible_base
    # print("h_recup_schema:selecteur", selecteur)
    LOGGER.debug("selecteur %s", repr(selecteur))
    try:
        complet = selecteur.resolve()
        LOGGER.debug("retour selecteur %s complet: %s", repr(selecteur), complet)

        # print("retour selecteur", complet, selecteur)
        if complet:
            regle.valide = "done"
        return True
    except ConnectionError:
        regle.valide = False
        return False


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
    # print("recup_schema---------------", obj)
    if obj.attributs.get("#categorie") == "traitement_virtuel":
        return True
    valide = True
    selecteur = setdb(regle, obj)
    for base, baseselecteur in selecteur.baseselectors.items():
        schema_travail = baseselecteur.getschematravail(regle)

    if valide:
        return True
    print("recup_schema: base non definie ", regle, selecteur, obj)
    return False


def h_dbclean(regle):
    """prepare un script de reinitialisation d'une ensemble de tables """

    regle.chargeur = True  # c est une regle a declencher
    if not param_base(regle):
        regle.valide = False
        return False
    for base, (niveau, classe, _) in regle.cible_base.items():

        regle.type_base = regle.getvar("db_" + base)

        nom = str(regle.params.cmp2.val) + ".sql"
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


def h_dbselect(regle):
    """preparation selecteur"""
    nom_selecteur = regle.params.att_sortie.val
    if nom_selecteur.startswith("#"):
        nom_selecteur = nom_selecteur[1:]
    param_base(regle, nom=nom_selecteur)
    selecteur = regle.cible_base
    # selecteur = regle.cible_base
    regle.valide = "done"
    return True


def f_dbselect(regle, obj):
    """#aide||creation d un selecteur: ce selecteur peut etre reutilise pour des operations
             ||sur les bases de donnees
      #groupe||database
     #pattern||A;?;?;dbselect;?;?
    #req_test||testdb
    """
    pass


def h_liste_selecteur(regle):
    """prepare la liste"""
    regle.chargeur = True
    param_base(regle)
    regle.metas = "#meta" in regle.params.cmp1.val
    regle.infos = "#infos" in regle.params.cmp1.val
    regle.schema = (
        regle.stock_param.init_schema(regle.params.cmp2.val)
        if regle.params.cmp2.val
        else None
    )
    regle.idclasse = (
        tuple(regle.params.att_sortie.texte.split("."))
        if regle.params.pattern == "1"
        else None
    )
    if regle.idclasse and regle.schema:
        classe = regle.schema.setdefault_classe(regle.idclasse)
        classe.info["type_geom"] = "0"
    if regle.cible_base:
        # print ("creation selecteur", regle.cible_base)
        return True
    regle.valide = False
    regle.erreurs = "selecteur invalide -"


def f_liste_selecteur(regle, obj):
    """#aide||cree des objets virtuels ou reels a partir d un selecteur (1 objet par classe)
    #parametres_c||#meta et/ou #infos pour inclure les elements dans l objet;nom du schema
    #parametres1||idclasse resultante;;#1;#2
    #parametres2||;;#1;#2
    #parametres3||;#1;#2
    #aide_spec||cree des objets reels par defaut sauf si on mets la variable virtuel a 1
    #aide_spec3||cree un objet par classe
    #schema||change_schema
    #pattern1||A.C;;;dblist;?C;?C
    #pattern2||=#obj;;;dblist;?C;?C
    #pattern3||;;;dblist;?C;?C
    """
    selecteur = setdb(regle, obj)
    virtuel = regle.getvar("virtuel") == "1"
    if regle.idclasse:
        niveau, classe = regle.idclasse
        schemaclasse = regle.schema.get_classe(regle.idclasse) if regle.schema else None
    # print("traitement liste selecteur", selecteur)
    for i in selecteur.get_classes():
        idbase, selinfo = i
        idsel, description = selinfo
        # print(" lecture selecteur", i, "->", idbase, idsel, description)
        nsel, csel = idsel
        server = ""
        infos = {
            "#sel_codebase": idbase,
            "#sel_niveau": nsel,
            "#sel_classe": csel,
            "#sel_host": regle.getvar("server_" + idbase),
            "#sel_user": regle.getvar("user_" + idbase),
            "#sel_user": regle.getvar("user_" + idbase),
            "#sel_base": regle.getvar("base_" + idbase),
            "#sel_type_base": regle.getvar("db_" + idbase),
        }
        # print("infos selecteur", infos)
        if regle.metas:
            infos.update(selecteur.baseselectors[idbase].schemabase.metas)
        if regle.infos:
            infos.update(selecteur.baseselectors[idbase].schemabase.infos)

        if regle.params.pattern == "2":
            obj2 = obj.dupplique()
            obj2.attributs.update(infos)
            if regle.idclasse:
                obj2.setschema(schemaclasse)
        else:
            if not regle.idclasse:
                niveau, classe = idsel
                if regle.schema:
                    schemaclasse = selecteur.schemabase.get_classe(idsel)
                else:
                    schemaclasse = None

            obj2 = Objet(
                niveau,
                classe,
                format_natif="interne",
                conversion="virtuel" if virtuel else None,
                attributs=infos,
                schema=schemaclasse,
            )
            obj2.initattr()
        if regle.debug:
            obj2.debug("cree", attlist=regle.champsdebug)
            regle.debug -= 1
        try:
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
        except StopIteration as abort:
            #            print("intercepte abort",abort.args[0])
            if abort.args[0] == 2:
                break
            raise
    return True


def h_dbset(regle):
    """prepare la liste"""
    getrequest(regle)
    base = regle.code_classe[3:]
    # print(" dbset ", base, regle.code_classe)
    regle.connect = regle.stock_param.getdbaccess(regle, base)
    regle.multiple = regle.params.cmp2.val
    regle.valide = bool(regle.connect)


def dataconverter(liste):
    """formatage de donnees"""
    result = []
    for i in liste:
        if isinstance(i, datetime.datetime):
            val = i.isoformat()
        elif i:
            val = str(i)
        else:
            val = ""
        result.append(val)
    return result


def f_dbset(regle, obj):
    """#aide||renseigne des champs par requete en base
    #aide_spec||cree des objets si multiple est specifie
        ||renseigne le champ #nb_lignes avec le nombre d'objets crees
        ||les champs d'entree sont fournis a la requete et remplacent les %s
        ||si les tables de la requete ou le nom des attributs dependent de l objet
        ||il faut les ecrire sous la forme %#[nom_attribut]
    #pattern1||M;?;?L;dbset;C;?=multiple
    #parametres||sortie;defauts;entrees;dbset;requete;multiple
    """
    requete = regle.requete
    if obj.virtuel:
        return True
    if regle.dynrequete:
        niveau, classe = obj.ident
        # print ("dbset:requetes dynamiques ", niveau,classe)
        requete = requete.replace("%#niveau", niveau)
        requete = requete.replace("%#classe", classe)
        if "%#[" in requete:
            findlist = re.findall(r"%#\[(.*?)\]", requete)
            # print ("findlist", findlist, obj)
            if findlist:
                for i in findlist:
                    valeur = obj.attributs.get(i.strip(), "")
                    # print ("traitement",i,"->",valeur)
                    requete = requete.replace("%#[" + i + "]", valeur)
            else:
                LOGGER.warning(" no match %s", requete)

    data = regle.getlist_entree(obj)
    # print("dbset", requete, data)
    try:
        liste = regle.connect.request(requete, data, regle=regle)
    except regle.connect.DBError as errs:
        if regle.debug:
            print("dbset: erreur requete", errs)
        return False
    if regle.multiple:
        for i in liste:
            obj2 = obj.dupplique()
            result = dataconverter(i)
            regle.setval_sortie(obj2, result)
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
        obj.attributs["#nb_lignes"] = len(liste)
        return len(liste)
    if liste:
        result = dataconverter(liste[0] if liste else [])
        regle.setval_sortie(obj, result)
        # print("recup_requete", result)
        return True
    return False


def h_dbmap_qgs(regle):
    """mapping statique de fichier qgis"""
    regle.base = regle.code_classe[3:]
    regle.nom_selecteur = regle.params.val_entree.val
    if regle.nom_selecteur.startswith("#"):
        regle.nom_selecteur = regle.nom_selecteur[1:]
    regle.entree = regle.params.cmp1.val
    regle.sortie = regle.params.cmp2.val
    selecteur = regle.stock_param.namedselectors.get(regle.nom_selecteur)
    # print ("mapping statique",selecteur,selecteur.resolve())
    if selecteur and selecteur.resolve():
        LOGGER.info("mapping qgis statique %s -> %s", selecteur.nom, regle.sortie)
        adapt_qgs_datasource(regle, None, regle.entree, selecteur, regle.sortie)
        regle.valide = "done"
    return True


def f_dbmap_qgs(regle, obj):
    """#aide||remappe des fichiers qgis pour un usage en local en prenant en comte un selecteur
    #aide spec|| la base de destination est indiquee par db:defbasse en premiere colonne
    #parametres||selecteur;;rep entree;rep sortie
    #pattern||;C;;dbmap_qgs;C;C
    """
    LOGGER.debug("dbmapqgs")
    print("====================dbmapqgs")
    selecteur = regle.stock_param.namedselectors.get(regle.nom_selecteur)
    if selecteur:
        adapt_qgs_datasource(regle, obj, regle.entree, selecteur, regle.sortie)
        return True
    else:
        return False
