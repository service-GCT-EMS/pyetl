# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces aux bases de donnees
"""
import re
import time
import os
import logging
from .db import DATABASES
from .interne.objet import Objet


DEBUG = False
LOGGER = logging.getLogger("pyetl")
# modificateurs de comportement reconnus
DBACMODS = {"A", "T", "V", "=", "NOCASE"}
DBDATAMODS = {"S", "L"}
DBMODS = DBACMODS | DBDATAMODS


def dbaccess(regle, codebase, type_base=None):
    """ouvre l'acces a la base de donnees et lit le schema"""
    base = codebase
    serveur = ""
    stock_param = regle.stock_param
    print("dbaccess", codebase, regle)
    systables = regle.getvar("tables_systeme")
    # serveur = regle.getvar("server_" + codebase, "")
    prefix = ""
    if not type_base:  # on pioche dans les variables
        base = regle.getvar("base_" + codebase, "")
        if not base:
            if stock_param.load_paramgroup(codebase, nom=codebase, fin=False):
                base = regle.getvar("base_" + codebase, "")
            else:
                print("mdba: base non definie", codebase)
                return None
        serveur = regle.getvar("server_" + codebase, "")
        type_base = regle.getvar("db_" + codebase, "")
        prefix = regle.getvar("prefix_" + codebase, "")
        print("mdba:acces base", codebase, base, serveur, type_base, prefix)

    if type_base not in DATABASES:
        print("type_base inconnu", type_base)
        return None
    # print(
    #     "--------acces base de donnees",
    #     codebase,
    #     "->",
    #     type_base,
    #     "en memoire:",
    #     codebase in stock_param.dbconnect,
    # )
    dbdef = DATABASES[type_base]
    if dbdef.svtyp == "file":
        # c'est une base fichier elle porte le nom du fichier et le serveur c'est le chemin
        # serveur = ""
        #        servertyp = type_base
        base = codebase
        print("filedb", type_base, "-->", codebase)
        serveur = regle.getvar("server_" + codebase, "")

    user = regle.getvar("user_" + codebase, "")
    passwd = regle.getvar("passwd_" + codebase, "")

    dbdef = DATABASES[type_base]
    connection = dbdef.acces(
        serveur, base, user, passwd, system=systables, params=regle, code=codebase
    )

    if connection.valide:
        # print("connection valide", serveur, base)
        connection.gensql = dbdef.gensql(connection=connection)
        connection.prefix = prefix
        connection.type_serveur = dbdef.svtyp
        connection.geom_from_natif = dbdef.converter
        connection.geom_to_natif = dbdef.geomwriter
        connection.format_natif = dbdef.geom
        connection.schemabase.dbsql = connection.gensql
        connection.get_schemabase()
        connection.commit()  # on referme toutes les transactions
        return connection

    print("connection invalide", base, type_base)
    return None


def dbclose(stock_param, base):
    """referme une connection"""
    print("mdba: fermeture base de donnees", base)
    if base in stock_param.dbconnect:
        stock_param.dbconnect[base].dbclose()
        del stock_param.dbconnect[base]


def get_helper(base, files, loadext, helpername, stock_param):
    """affiche les messages d erreur du loader"""
    for file in files:
        if not file.endswith(loadext):
            print(
                "seul des fichiers", loadext, "peuvent etre lances par cette commande"
            )
            print("!!!!!!!!!!fichier incompatible", file, files)
            return False
    if helpername is None:
        print("pas de loader defini sur la base ", base)
        return False
    helper = stock_param.getvar(helpername)
    if not helper:
        print("pas de programme externe defini", helpername)
        return False
    return helper


def setpath(regle, nom):
    """prepare les fichiers de log pour les programmes externes"""
    if nom:
        nom = os.path.join(regle.getvar("_sortie"), nom)
        rep = os.path.dirname(nom)
        if rep:
            os.makedirs(rep, exist_ok=True)
    return nom


def dbextload(regle_courante, base, files, log=None):
    """charge un fichier a travers un loader"""
    print("extload chargement ", base, files)
    stock_param = regle_courante.stock_param
    connect = stock_param.getdbaccess(regle_courante, base)
    if connect is None:
        return False
    connect = stock_param.dbconnect[base]
    helpername = connect.load_helper
    loadext = connect.load_ext
    helper = get_helper(base, files, loadext, helpername, stock_param)
    reinit = regle_courante.getvar("reinit", "0")
    vgeom = regle_courante.getvar("valide_geom", "1")
    if helper:
        logfile = setpath(regle_courante, log)
        return connect.extload(
            helper, files, logfile=logfile, reinit=reinit, vgeom=vgeom
        )
    return False


def dbextdump(regle_courante, base, niveau, classe, dest="", log=None):
    """extrait un fichier a travers un loader"""

    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante, base, niveau, classe
    )
    if connect is None:
        return False
    if not liste_tables:
        print("pas de tables a sortir", base, niveau, classe)
        return False
    helpername = connect.dump_helper
    helper = get_helper(base, [], "", helpername, regle_courante.stock_param)
    if helper:
        workers, extworkers = regle_courante.get_max_workers()
        fanout = regle_courante.getvar("fanout", "classe")
        print("extdump", regle_courante.context.vlocales, extworkers)
        logfile = setpath(regle_courante, log)
        resultats = connect.extdump(
            helper, liste_tables, dest, logfile, workers=extworkers, fanout=fanout
        )
        #        print(' extdump' , resultats)
        if resultats:
            for idclasse in resultats:
                schema_travail.classes[idclasse].objcnt = resultats[idclasse]
            regle_courante.setvar("schema_entree", schema_travail.nom, loc=0)
    return False


def dbextalpha(regle_courante, baseselector, dest="", log=""):
    """extrait un fichier a travers un loader et lance les traitements"""

    connect = baseselector.connect
    if connect is None:
        return False
    schema_travail = baseselector.schema_travail
    base = baseselector.base
    # if not liste_tables:
    #     print("pas de tables a sortir", base, niveau, classe)
    #     return False
    liste_tables = [desc[0] for ident, desc in baseselector.classlist()]
    regle_courante.setvar("schema_entree", schema_travail.nom)
    helpername = connect.dump_helper
    helper = get_helper(base, [], "", helpername, regle_courante.stock_param)
    if helper:
        #        workers, extworkers = regle_courante.get_max_workers()
        print(
            "extalpha",
            regle_courante,
            regle_courante.get_max_workers(),
            regle_courante.getvar("_wid"),
        )
        logfile = setpath(regle_courante, log)
        resultats = connect.extalpha(
            regle_courante,
            helper,
            liste_tables,
            dest,
            logfile,
            nbworkers=regle_courante.get_max_workers(),
        )
        #        print(' extdump' , resultats)
        if resultats:
            for idclasse in resultats:
                schema_travail.classes[idclasse].objcnt = resultats[idclasse]

    return False


def dbrunproc(regle, base, commande, data):
    """execute une procedure stockeee en base """
    # print("mdba execution directe commande", base, file)
    connect = regle.stock_param.getdbaccess(regle, base)
    if connect is None:
        return False
    # connect = regle.stock_param.dbconnect[base]
    return connect.request(commande, data)


def dbextsql(regle, base, file, log=None, out=None):
    """charge un fichier sql a travers un client sql externe"""
    # print("mdba execution sql via un programme externe", base, file)
    connect = regle.stock_param.getdbaccess(regle, base)
    if connect is None:
        return False
    connect = regle.stock_param.dbconnect[base]
    helpername = connect.sql_helper
    helper = get_helper(base, [file], ".sql", helpername, regle.stock_param)
    if helper:
        logfile = setpath(regle, log)
        outfile = setpath(regle, out)
        # print("mdba:extsql: demarrage", helpername, helper, "user:", connect.user)
        return connect.extsql(helper, file, logfile, outfile)
    return False


def get_connect(
    regle,
    base,
    niveau,
    classe,
    tables="A",
    multi=True,
    nocase=False,
    nomschema="",
    type_base=None,
    chemin="",
    description=None,
):
    """ recupere la connection a la base et les schemas qui vont bien"""
    # print("get_connect", regle, base, type_base)
    stock_param = regle.stock_param
    nombase = base

    connect = stock_param.getdbaccess(regle, nombase, type_base=type_base)

    if connect is None:
        LOGGER.error("connection base invalide " + str(nombase))
        return None

    nomschema = nomschema if nomschema else connect.schemabase.nom.replace("#", "")
    schema_travail, liste2 = connect.getschematravail(
        regle,
        niveau,
        classe,
        tables=tables,
        multi=multi,
        nocase=nocase,
        nomschema=nomschema,
    )
    return connect, schema_travail, liste2


def get_dbtype(connect, typecode):
    """recupere le type du retour par defaut texte"""
    return "text"
    connection.request()


def schema_from_curs(schema, curs, nomclasse):
    """ cree un schema de classe a partir d'une requete generique"""
    attlist = curs.infoschema
    curs.connecteur.cree_schema_classe(nomclasse, curs.infoschema, schema=schema)


def sortie_resultats(
    regle_courante,
    curs,
    niveau,
    classe,
    connect,
    sortie,
    v_sortie,
    type_geom,
    schema_classe_travail,
    treq=0,
    cond="",
):
    """ recupere les resultats et génére les objets"""
    regle_debut = regle_courante.branchements.brch["gen"]
    stock_param = regle_courante.stock_param
    traite_objet = stock_param.moteur.traite_objet

    # print ('mdba:sortie_resultat ',type_geom,type(curs),niveau,classe)
    # valeurs = curs.fetchone()
    # print ('mdba:recuperation valeurs ',valeurs)
    schema_init = None
    if not curs.cursor:
        return 0
    if not niveau:
        niveau = schema_classe_travail.fichier
    if regle_courante.getvar("schema_entree"):
        schema_init = stock_param.schemas[regle_courante.getvar("schema_entree")]
        if schema_init:
            niveau, classe = schema_init.map_dest((niveau, classe))
        schema_classe_travail = schema_init.setdefault_classe((niveau, classe))
    if regle_courante.getvar("printpending"):
        print()
    print(
        "...%-50s" % ("%s : %s.%s" % (connect.base, niveau, classe)), end="", flush=True
    )

    regle_courante.setvar("printpending", 1)
    nbvals = 0
    namelist = curs.namelist
    # print(" attributs recuperes avant", namelist)
    if type_geom == "indef":
        type_geom = schema_classe_travail.info["type_geom"]
    if type_geom != "0":
        namelist.append(("#geom"))
    # print (' attributs recuperes ', attlist)
    # namelist = [i[0] for i in attlist]
    geom_from_natif = connect.geom_from_natif
    format_natif = connect.format_natif
    maxobj = regle_courante.getvar("lire_maxi", 0)
    nb_pts = 0
    sys_cre, sys_mod = None, None
    if connect.sys_cre in namelist:
        sys_cre = connect.sys_cre
    if connect.sys_mod in namelist:
        sys_mod = connect.sys_mod
    tget = time.time()
    decile = curs.decile
    for valeurs in curs.cursor:
        #        print ("geometrie valide",obj.geom_v.valide)
        # print("mdba: creation objet", niveau, classe, namelist, valeurs)
        obj = Objet(
            niveau,
            classe,
            format_natif=format_natif,
            conversion=geom_from_natif,
            attributs=zip(namelist, [str(i) if i is not None else "" for i in valeurs]),
        )
        # if '#geom' in attlist:
        #     print ('attlist', attlist)
        #     print (valeurs,valeurs)
        #     print ('zip ',zip(attlist, [str(i) if i is not None else "" for i in valeurs]))
        #     raise
        if type_geom == "1":  # on prepare les angles s'il y en a
            obj.attributs["#angle"] = obj.attributs.get("angle_g", "0")

        obj.attributs["#type_geom"] = type_geom
        obj.setschema(schema_classe_travail)
        #        print ('type_geom',obj.attributs['#type_geom'], obj.schema.info["type_geom"])
        nbvals += 1
        obj.attributs["#gid"] = obj.attributs.get("gid", str(nbvals))
        if sys_cre:
            obj.attributs["#_sys_date_cre"] = obj.attributs[sys_cre]
        if sys_mod:
            obj.attributs["#_sys_date_mod"] = obj.attributs[sys_mod]
        #        print ('lu sys',obj.attributs,sys_cre,connect.sys_cre,connect.idconnect)
        if sortie:
            #            print ('mdba: renseignement attributs',sortie,v_sortie)
            for nom, val in zip(sortie, v_sortie):
                obj.attributs[nom] = val
        #                print ('renseigne',obj.attributs)
        # print ("mdba sortie_resultats vers regle:",regle_courante.ligne,regle_debut.ligne)
        obj.setorig(nbvals)
        # print("sortie_res", obj)
        traite_objet(obj, regle_debut)
        if nbvals == maxobj:
            break
        # deco avec petits points por faire patienter
        if nbvals > decile:
            decile += curs.decile
            nb_pts += 1
            print(".", end="", flush=True)
    tget = time.time() - tget
    if nb_pts < 10:
        print("." * (10 - nb_pts), end="")

    print("%8d en %8d ms (%8d) %s" % (nbvals, (tget + treq) * 1000, treq * 1000, ""))
    regle_courante.setvar("printpending", 0)
    curs.close()
    return nbvals


def recup_schema(
    regle_courante,
    base,
    niveau,
    classe,
    nom_schema="",
    type_base=None,
    chemin="",
    mods=None,
    description=None,
):
    """ recupere juste les schemas de la base sans donnees """
    cmp1 = (
        mods
        if mods is not None
        else [i.upper() for i in regle_courante.params.cmp1.liste]
    )
    #    cmp2 = [i.upper for i in regle_courante.params.cmp2.liste]

    multi = not "=" in cmp1
    nocase = "NOCASE" in cmp1
    tables = "".join([i for i in cmp1 if i not in {"=", "NOCASE", "S", "L"}])
    #    tables = [i for i in cmp1 if i in DBACMODS]
    if not tables:
        tables = "A"
    print("mdba:recup_schema", nom_schema, tables)
    retour = get_connect(
        regle_courante,
        base,
        niveau,
        classe,
        tables,
        multi,
        nocase=nocase,
        nomschema=nom_schema,
        type_base=type_base,
        chemin=chemin,
        description=description,
    )

    if retour:
        connect, schema_travail, liste_tables = retour
        print(
            "recup_schema",
            chemin,
            schema_travail.nom,
            len(schema_travail.classes),
            "classes",
        )
        if not liste_tables or DEBUG:
            print(
                "dbschema :",
                "regex" if multi else "strict",
                list(cmp1),
                tables,
                nocase,
                "->",
                len(liste_tables),
                "tables a sortir",
            )
        schema_base = connect.schemabase
        # print("recup_schema", schema_base, schema_travail, stock_param.schemas.keys())
        # print(
        #     "mdba:recup_schema",
        #     schema_travail.nom,
        #     len(schema_travail.elements_specifiques["roles"][1]),
        # )

        return (connect, schema_base, schema_travail, liste_tables)
    else:
        print("erreur de connection a la base", base, niveau, classe)
    return (None, None, None, None)


def lire_requete(
    regle_courante, base, niveau, classe, attribut=None, requete="", parms=None
):
    """lecture directe"""
    if classe is None:
        return 0
    ident = (niveau, classe)

    print("requete", ident, "->", base, requete)
    nom_schema = regle_courante.getvar("#schema", "tmp")
    v_sortie = parms
    sortie = attribut
    retour = get_connect(regle_courante, base, None, None, nomschema=nom_schema)
    if retour:
        connect, schema, liste = retour
    else:
        return 0
    treq = time.time()
    curs = connect.iterreq(requete, data=parms)

    #            print ('mdba : ',ident,schema_base.nom,schema_classe_base.info["type_geom"])
    #        print ('mdba : ',ident)
    # print("-----------------------traitement curseur ", curs, type(curs))
    treq = time.time() - treq
    connect.commit()
    if curs and classe:
        schema_classe_travail = curs.connecteur.cree_schema_classe(
            ident, curs.infoschema, schema=schema
        )
        # print(
        #     "creation schema",
        #     schema.nom,
        #     ident,
        #     sorted(curs.infoschema, key=lambda x: x.num_attribut),
        # )
        if schema_classe_travail:
            res = sortie_resultats(
                regle_courante,
                curs,
                *ident,
                connect,
                sortie,
                v_sortie,
                schema_classe_travail.info["type_geom"],
                schema_classe_travail,
                treq=treq,
            )

            if sortie:
                for nom in sortie:
                    if nom and nom[0] != "#":
                        schema_classe_travail.stocke_attribut(nom, "T")
            return res
    return 0


def recup_donnees_req_alpha(regle_courante, baseselector):
    """ recupere les objets de la base de donnees et les passe dans le moteur de regles"""
    #    debut = time.time()
    # print('mdb: recup_donnees alpha', regle_courante, base, mods, sortie, classe)
    connect = baseselector.connect
    # print ('recup liste tables', liste_tables)
    if connect is None:
        return 0

    schema_travail = baseselector.schema_travail
    print("recup schema_travail ", schema_travail.nom)

    schema_base = connect.schemabase
    reqdict = dict()
    # if isinstance(attribut, list):
    #     reqdict = {
    #         (niv, cla): (att, val)
    #         for niv, cla, att, val in zip(niveau, classe, attribut, valeur)
    #     }

    stock_param = regle_courante.stock_param
    maxobj = int(regle_courante.getvar("lire_maxi", 0))
    mods = regle_courante.params.cmp1.liste
    ordre = regle_courante.params.cmp2.liste
    sortie = regle_courante.params.att_sortie.liste
    res = 0
    print("dbacces: recup_donnees_req_alpha", connect.idconnect, mods)
    curs = None  #
    n = 0
    for ident2, description in baseselector.classlist():
        ident, attr, val, fonction = description
        treq = time.time()
        n += 1
        if ident is not None:
            niveau, classe = ident2
            schema_classe_base = schema_base.get_classe(ident)
            #            print('mdba: ', ident, schema_base.nom, schema_classe_base.info["type_geom"])
            # print("mdba: ", ident, ident2)
            schema_classe_travail = schema_travail.get_classe(ident)
            schema_classe_travail.info["type_geom"] = schema_classe_base.info[
                "type_geom"
            ]
            if (
                attr
                and attr not in schema_classe_travail.attributs
                and attr not in connect.sys_fields
            ):
                # print ('la on fait rien',type(attribut), attr)
                continue  # on a fait une requete sur un attribut inexistant: on passe

            curs = connect.req_alpha(
                ident, schema_classe_base, attr, val, mods, maxi=maxobj, ordre=ordre
            )
            connect.commit()
            # print ('-----------------------traitement curseur ', ident, curs,type(curs) )
            treq = time.time() - treq
            if curs:
                res += sortie_resultats(
                    regle_courante,
                    curs,
                    niveau,
                    classe,
                    connect,
                    sortie,
                    val,
                    schema_classe_base.info["type_geom"],
                    schema_classe_travail,
                    treq=treq,
                    cond=(attr, val),
                )

            if sortie:
                for nom in sortie:
                    if nom and nom[0] != "#":
                        schema_classe_travail.stocke_attribut(nom, "T")

    if stock_param is not None:
        stock_param.padd("_st_lu_objs", res)
        stock_param.padd("_st_lu_tables", n)
    return res


def cre_script_reset(liste_tables, gensql):
    # print ('reinit tables a traiter', travail)
    script_clean = [
        gensql.prefix_charge(niveau, classe, "TDGS")
        + gensql.tail_charge(niveau, classe, "TDGS")
        for niveau, classe in reversed(liste_tables)
    ]
    return script_clean


def reset_liste_tables(
    regle_courante, base, niveau, classe, type_base=None, chemin="", mods=None
):
    """ genere un script de reset de tables"""
    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante,
        base,
        niveau,
        classe,
        type_base=type_base,
        chemin=chemin,
        mods=mods,
    )
    script_clean = (
        cre_script_reset(liste_tables, connect.gensql) if liste_tables else []
    )
    return script_clean


def recupval(
    regle_courante,
    base,
    niveau,
    classe,
    attribut,
    valeur,
    mods=None,
    type_base=None,
    chemin="",
    requete="",
):
    """ recupere des valeurs en base (une par table)"""
    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante,
        base,
        niveau,
        classe,
        type_base=type_base,
        chemin=chemin,
        mods=mods,
    )
    if connect is None:
        return 0
    reqdict = dict()
    if isinstance(attribut, list):
        for niv, cla, att, val in zip(niveau, classe, attribut, valeur):
            reqdict[(niv, cla)] = (att, val)

    total = 0
    reponse = dict()
    for ident in liste_tables:
        attr, val = attribut, valeur
        if ident is not None:

            niveau, classe = ident

            schema_classe_travail = schema_travail.get_classe(ident)
            if isinstance(attribut, list):
                if ident in reqdict:
                    attr, val = reqdict[ident]
                else:
                    attr, val = "", ""
            if (
                attr
                and attr not in schema_classe_travail.attributs
                and attr not in connect.sys_fields
            ):
                continue  # on a fait une requete sur un attribut inexistant: on passe
            reponse[ident] = connect.requete_simple(
                requete, ident, schema_classe_travail, attr, val, mods
            )
            connect.commit()

            #        print ('retour ',nb)
    return reponse


def recup_count(
    regle_courante,
    base,
    niveau,
    classe,
    attribut,
    valeur,
    mods=None,
    type_base=None,
    chemin="",
):
    """ recupere des comptages en base"""

    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante,
        base,
        niveau,
        classe,
        type_base=type_base,
        chemin=chemin,
        mods=mods,
    )
    if connect is None:
        return 0
    reqdict = dict()
    if isinstance(attribut, list):
        for niv, cla, att, val in zip(niveau, classe, attribut, valeur):
            reqdict[(niv, cla)] = (att, val)

    total = 0
    for ident in liste_tables:
        attr, val = attribut, valeur
        if ident is not None:

            niveau, classe = ident

            schema_classe_travail = schema_travail.get_classe(ident)
            if isinstance(attribut, list):
                if ident in reqdict:
                    attr, val = reqdict[ident]
                else:
                    attr, val = "", ""
            if (
                attr
                and attr not in schema_classe_travail.attributs
                and attr not in connect.sys_fields
            ):
                continue  # on a fait une requete sur un attribut inexistant: on passe
            reponse = connect.req_count(ident, schema_classe_travail, attr, val, mods)
            connect.commit()

            #        print ('retour ',nb)
            if reponse and reponse[0]:
                total += reponse[0][0]
    return total


def recup_table_parametres(
    regle, nombase, niveau, classe, clef=None, valeur=None, ordre=None, type_base=None
):
    """lit une table en base de donnees et retourne le tableau de valeurs """
    print("recup_table", nombase, niveau, classe)
    LOGGER.info("recup table en base " + nombase + ":" + niveau + "." + classe)
    retour = get_connect(
        regle, nombase, [niveau], [classe], tables="A", multi=0, type_base=type_base
    )
    if retour:
        connect, schema_travail, _ = retour
    else:
        return []

    ident = (niveau, classe)
    print("recup_table schema:", schema_travail)
    curs = connect.req_alpha(
        ident, schema_travail.get_classe(ident), clef, valeur, "", 0, ordre=ordre
    )
    connect.commit()
    resultat = [valeurs for valeurs in curs.cursor] if curs else []
    return resultat


def recup_maxval(regle, nombase, niveau, classe, clef, type_base=None):
    """ recupere la valeur maxi d'un champ en base """
    #    print('recup_table', nombase, niveau, classe, type_base)
    retour = get_connect(
        regle, nombase, niveau, classe, "A", False, type_base=type_base
    )
    if retour:
        connect, schema_travail, _ = retour
    else:
        return None
    if connect is None:
        return None
    retour = dict()
    for ident in schema_travail.classes:
        niveau, classe = ident
        champ = clef if clef else schema_travail.classes[ident].getpkey
        mval = (
            connect.recup_maxval(niveau, classe, champ)
            if champ in schema_travail.classes[ident].attributs
            else ""
        )
        if mval:
            retour[ident] = str(mval)
        #            print('maxval:', ident, retour[ident], champ)
        connect.commit()
    return retour


def recup_donnees_req_geo(
    regle_courante,
    base,
    niveau,
    classe,
    fonction,
    obj,
    mods,
    sortie,
    v_sortie,
    type_base=None,
    chemin="",
):
    """ recupere les objets de la base de donnees et les passe dans le moteur de regles"""
    #    debut = time.time()
    maxobj = regle_courante.getvar("lire_maxi", 0)
    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante,
        base,
        niveau,
        classe,
        type_base=type_base,
        chemin=chemin,
        mods=mods,
    )
    if connect is None:
        return 0
    buffer = regle_courante.params.cmp1.num

    if obj.format_natif == connect.format_natif:
        geometrie = obj.attributs["#geom"]
    else:
        if obj.initgeom():
            geometrie = connect.geom_to_natif(obj.geom_v, 0, 0, None)
        else:
            print("objet non geometrique comme filtre de requete geometrique")
            return False
    res = 0
    #    interm = time.time()
    #    print('recup_req geom ', fonction, ': initialisation ', int(interm-debut), 's')
    if not liste_tables:
        return None
    for ident in sorted(liste_tables):

        niveau, classe = ident
        schema_classe_postgis = schema_base.get_classe(ident)

        schema_classe_travail = schema_travail.get_classe(ident)
        treq = time.time()
        curs = connect.req_geom(
            ident, schema_classe_travail, mods, fonction, geometrie, maxobj, buffer
        )
        connect.commit()
        treq = time.time() - treq
        if curs.cursor is None:
            continue
        for nom_att, orig in (
            (i, j)
            for i, j in zip(sortie, regle_courante.params.att_entree.liste)
            if i and i[0] != "#"
        ):
            #            print ('creation attribut',nom_att,orig)
            if obj.schema and obj.schema.attributs.get(orig):
                def_att_sortie = obj.schema.attributs.get(orig)
                schema_classe_travail.ajout_attribut_modele(def_att_sortie, nom=nom_att)
            else:
                schema_classe_travail.stocke_attribut(nom_att, "T")
        schema_classe_travail.info["type_geom"] = schema_classe_postgis.info[
            "type_geom"
        ]
        res += sortie_resultats(
            regle_courante,
            curs,
            niveau,
            classe,
            connect,
            sortie,
            v_sortie,
            schema_classe_postgis.info["type_geom"],
            schema_classe_travail,
            treq=treq,
            cond=("geom", fonction),
        )

    #    stock_param.dbread += res
    return res


class DbWriter(object):
    """ ressource d'ecriture en base de donnees"""

    def __init__(self, nom, liste_att=None, encoding="utf-8", regle=None):

        self.nom = nom
        self.liste_att = liste_att
        self.fichier = None
        self.encoding = encoding
        self.schema_base = None
        retour = get_connect(
            regle,
            nom,
            None,
            None,
            tables="A",
            multi=True,
            nomschema="",
            type_base=None,
            chemin="",
        )
        if retour:
            connect, schema_travail, liste_tables = retour
            self.connect = connect
            self.schema_base = connect.schemabase

    def dbtable(self, idtable):
        """ cree une table """
        schematable = self.schema_base.get_classe(idtable)
        return self.connect.valide_table(schematable)

    def open(self, idtable):
        """ teste l existance de la table et la cree si necessaire"""
        self.dbtable(idtable)

    def reopen(self, _):
        """ reouverture d'une table ferme (non utilise)"""
        return

    def close(self, _):
        """fermeture d'une table (non utilise)"""
        return

    def finalise(self, _):
        """fermeture definitive d'un fichier (non utilise)"""
        return

    def set_liste_att(self, liste_att):
        """positionne la liste d'attributs"""
        self.liste_att = liste_att

    def write(self, obj):
        """ecrit un objet complet"""
        return True


def dbload(regle, base, niveau, classe, obj):
    pass


def dbupdate(regle, base, niveau, classe, attribut, obj):

    requete = "UPDATE "
    pass


def ecrire_objets_db(regle, _, attributs=None, rep_sortie=None):
    """ecrit un ensemble d'objets en base"""
    # ng, nf = 0, 0
    # memoire = defs.stockage
    sorties = regle.stock_param.sorties
    rep_sortie = regle.getvar("_sortie") if rep_sortie is None else rep_sortie
    dident = None
    ressource = None
    for groupe in list(regle.stockage.keys()):
        nb_obj = 0
        for obj in regle.recupobjets(groupe):  # on parcourt les objets
            if obj.virtuel:  # on ne traite pas les virtuels
                continue
            if obj.ident != dident:
                if ressource:
                    ressource.compte(nb_obj)
                    nb_obj = 0
                groupe, classe = obj.ident
                print("dbw : regle.fanout", regle.fanout)

                if regle.fanout == "no":
                    nom = sorties.get_id(rep_sortie, "all", "", ".sql")
                elif regle.fanout == "groupe":
                    nom = sorties.get_id(rep_sortie, groupe, "", ".sql")
                else:
                    nom = sorties.get_id(rep_sortie, classe, "", ".sql")

                ressource = sorties.get_res(regle, nom)
                if ressource is None:
                    os.makedirs(os.path.dirname(nom), exist_ok=True)
                    #                    liste_att = _set_liste_attributs(obj, attributs)
                    liste_att = obj.schema.get_liste_attributs(liste=attributs)
                    dbwr = DbWriter(
                        nom, liste_att, encoding=regle.getvar("codec_sortie", "utf-8")
                    )
                    sorties.creres(regle, nom, dbwr)
                    ressource = sorties.get_res(regle, nom)
                else:
                    #                    liste_att = _set_liste_attributs(obj, attributs)
                    liste_att = obj.schema.get_liste_attributs(liste=attributs)
                    dbwr = ressource.handler
                    dbwr.set_liste_att(liste_att)
                dident = (groupe, classe)
            dbwr.write(obj)
            nb_obj += 1


def db_streamer(obj, regle, _, attributs=None, rep_sortie=None):
    """ecrit des objets sql au fil de l'eau.
        dans ce cas les objets ne sont pas stockes,  l'ecriture est effetuee
        a la sortie du pipeline (mode streaming) on groupe quand meme pour les perfs
    """
    if obj.virtuel:
        return
    rep_sortie = regle.getvar("_sortie") if rep_sortie is None else rep_sortie
    sorties = regle.stock_param.sorties
    if obj.ident != regle.dident:
        if obj.virtuel:  # on ne traite pas les virtuels
            return
        dest = obj.ident
        ressource = sorties.get_res(regle, dest)
        if ressource is None:
            liste_att = obj.schema.get_liste_attributs(liste=attributs)
            #            liste_att = _set_liste_attributs(obj, attributs)
            swr = DbWriter(
                dest,
                liste_att,
                encoding=regle.getvar("codec_sortie", "utf-8"),
                regle=regle,
            )
            sorties.creres(regle, dest, swr)
            ressource = sorties.get_res(regle, dest)
            regle.dident = dest
            regle.ressource = ressource
        else:
            if dest != regle.dident:
                #                liste_att = _set_liste_attributs(obj, attributs)
                liste_att = obj.schema.get_liste_attributs(liste=attributs)
                ressource.handler.set_liste_att(liste_att)
                regle.dident = dest
                regle.ressource = ressource
    regle.ressource.handler.write(obj)
