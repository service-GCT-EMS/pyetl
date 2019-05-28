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
from collections import defaultdict

from .db import DATABASES
from .interne.objet import Objet


DEBUG = False
LOGGER = logging.getLogger("pyetl")
# modificateurs de comportement reconnus
DBACMODS = {"A", "T", "V", "=", "NOCASE"}
DBDATAMODS = {"S", "L"}
DBMODS = DBACMODS | DBDATAMODS


def coroutine(func):
    """ decorateur de coroutine"""

    def wrapper(*arg, **kwargs):
        """decorateur de coroutine"""
        generator = func(*arg, **kwargs)
        next(generator)
        return generator

    return wrapper


def fkref(liste, niveau, niv_ref, schema):
    """identifie les tables referenceees par des fk"""
    trouve = 0
    for ident in liste:
        if niveau[ident] == niv_ref:
            cibles = schema.is_cible(ident)
            #            print(ident,":tables  visant la classe",cibles)
            for j in cibles:
                if j not in niveau:
                    print("fkref: erreur cible", j)
                    continue
                if niveau[j] >= niv_ref and j != ident:
                    if ident in schema.is_cible(j):
                        print("attention references croisees", ident, j)
                    else:
                        niveau[ident] += 1
                        #                        print(" trouve",ident,niveau[ident],j)
                        trouve = 1
                    break
    return trouve


def tablesorter(liste, schema):
    """ trie les tables en fonction des cibles de clef etrangeres """
    schema.calcule_cibles()
    niveau = dict()
    niveau = {i: 0 for i in liste}
    trouve = 1
    niv_ref = 0
    while trouve:
        trouve = fkref(liste, niveau, niv_ref, schema)
        niv_ref += 1
    #    print("niveau maxi", niv_ref)
    niv2 = {i: "%5.5d_%s.%s" % (99999 - niveau[i], *i) for i in niveau}
    liste.sort(key=niv2.get)
    return niveau


def invalide(schemaclasse, tables):
    """ determine si une table est eligible """
    if schemaclasse.type_table in tables:
        return False
    print("table non retenue", schemaclasse.nom, schemaclasse.type_table, "->", tables)
    return True


def choix_multi(schemaclasse, ren, rec, negniv, negclass, nocase):
    """ determine si une table est a retenir """
    if nocase:
        return (
            bool(ren.search(schemaclasse.groupe.lower())) != negniv
            and bool(rec.search(schemaclasse.nom.lower())) != negclass
        )
    return (
        bool(ren.search(schemaclasse.groupe)) != negniv
        and bool(rec.search(schemaclasse.nom)) != negclass
    )


def choix_simple(schemaclasse, exp_niv, exp_class, negniv, negclass, nocase):
    """ determine si une table est a retenir """
    groupe = schemaclasse.groupe.lower() if nocase else schemaclasse.groupe
    vniv = groupe == exp_niv if exp_niv else True
    vniv = vniv and not negniv
    nom = schemaclasse.nom.lower() if nocase else schemaclasse.nom
    vclass = nom == exp_class if exp_class else True
    vclass = vclass and not negclass
    #    if vniv and vclass:
    #        print ('choix simple ',groupe,nom,exp_niv,'.',exp_class)
    return vniv and vclass


def selection_directe(schema, niveau):
    """ selection directe d une table """
    tables_a_sortir = set()
    niv = niveau[0][2:]
    if len(niv.split(".")) != 3:
        print("dbselect: il faut une description complete s:niveau.classe.attribut", niveau)
    niv, clas = niv.split(".")[:2]
    #    print("mdba select: recherche ", niv, clas)
    for i in schema.classes:
        #            print (schema.classes[i].groupe,schema.classes[i].nom)
        if schema.classes[i].groupe == niv and schema.classes[i].nom == clas:
            tables_a_sortir.add(i)
            return tables_a_sortir


def select_tables(schema, niveau, classe, tables="A", multi=True, nocase=False):
    """produit la liste des tables a partir du schema utile pour id_in:"""
    tables_a_sortir = set()
    #    print('select ', niveau, classe, tables, multi)
    if len(niveau) == 1 and niveau[0][:2] == "s:":  # selection directe
        return selection_directe(schema, niveau)
    convert = {"a": "rtmfv", "v": "vm", "t": "r"}
    tables = convert.get(tables.lower(), tables.lower())
    # print('db:sortie liste', len(niveau), len(classe))
    # print('db:sortie liste', tables,niveau,classe)
    for exp_niv, exp_clas in zip(niveau, classe):
        #            trouve = False
        exp_niv = exp_niv.strip()
        exp_clas = exp_clas.strip()

        if nocase:
            exp_niv = exp_niv.lower()
            exp_clas = exp_clas.lower()
        negniv = False
        negclass = False
        if exp_niv and exp_niv[0] == "!":
            negniv = True
            exp_niv = exp_niv[1:]
        if exp_clas and exp_clas[0] == "!":
            negclass = True
            exp_clas = exp_clas[1:]
        if exp_clas == '*':
            exp_clas = '.*'
        ren = re.compile(exp_niv)
        try:
            rec = re.compile(exp_clas)
        except: # on essaye de remplacesr les *
            exp_clas.replace('*','.*')
            try:
                rec = re.compile(exp_clas)
            except re.error as identifier:
                print('erreur de description de classe ', exp_clas)
                raise SyntaxError

        #        print ('selection boucle', ren,rec,len(schema.classes))
        for i in schema.classes:
            if schema.classes[i].type_table not in tables:
                continue
            if multi:
                if choix_multi(schema.classes[i], ren, rec, negniv, negclass, nocase):
                    tables_a_sortir.add(i)
                #                    print ('sortir multi')
                continue
            if choix_simple(schema.classes[i], exp_niv, exp_clas, negniv, negclass, nocase):
                tables_a_sortir.add(i)
    #    print('db: Nombre de tables a sortir:', len(tables_a_sortir))
    if not tables_a_sortir:
        print("pas de tables a sortir")
        print("select tables: requete", tables, niveau, classe, multi)
        print("taille schema", schema.nom, len(schema.classes))

    return tables_a_sortir


def ihmtablelist(liste):
    """retourne une liste hierarchique de niveaux classe"""
    schemas = dict()
    for i in liste:
        nomschema, nomtable, commentaire, nb_enreg = i
        if nomschema not in schemas:
            schemas[nomschema] = dict()
        schemas[nomschema][nomtable] = (commentaire, nb_enreg)
    liste = []
    for i in sorted(schemas):
        valeur = (
            i + ":<" + ",".join([j + ":" + str(schemas[i][j]) for j in sorted(schemas[i])]) + ">"
        )
        liste.append(valeur)
    return "<" + ",".join(liste) + ">"


def _get_tables(connect):
    """recupere la structure des tables"""
    schema_base = connect.schemabase
    for i in connect.get_tables():
        nom_groupe, nom_classe, alias_classe, type_geometrique, dimension, nb_obj, type_table = ('','','','0','2','0','r')
        if len(i) == 12:
            _, nom_groupe, nom_classe, alias_classe, type_geometrique, dimension, nb_obj, type_table, _, _, _, _ = (
                i
            )
        elif len(i) == 11:
            nom_groupe, nom_classe, alias_classe, type_geometrique, dimension, nb_obj, type_table, _, _, _, _ = (
                i
            )
        else:
            print("mdba:table mal formee ", connect.type_base, len(i), i)
            continue

        #        nom_groupe, nom_classe, alias_classe, type_geometrique, dimension, nb_obj, type_table,\
        #        index_geometrique, clef_primaire, index, clef_etrangere = i
        #        print ('mdba:select tables' ,i)
        ident = (nom_groupe, nom_classe)
        schemaclasse = schema_base.get_classe(ident)
        if not schemaclasse:
            #            print ("schema incoherent",ident,sorted(schema_base.classes.keys()))
            if type_table == "r":
                LOGGER.info("table sans attributs" + ".".join(ident))
            #                print("table sans attributs", ident)
            elif type_table == "v" or type_table == "m":
                LOGGER.info("vue sans attributs" + ".".join(ident))
            #                print("vue sans attributs", ident)

            schemaclasse = schema_base.setdefault_classe(ident)
        schemaclasse.alias = alias_classe if alias_classe else ""
        schemaclasse.setinfo("objcnt_init", str(nb_obj) if nb_obj is not None else "0")
        schemaclasse.setinfo("dimension", str(dimension))
        schemaclasse.fichier = connect.nombase
        #        print ('_get_tables: type_geometrique',type_geometrique,schemaclasse.info["type_geom"])
        if schemaclasse.info["type_geom"] == "indef":
            schemaclasse.stocke_geometrie(type_geometrique, dimension=dimension)
            #            print('stockage type geometrique', ident, type_geometrique,
            #                  schemaclasse.info["type_geom"])
            if schemaclasse.info["type_geom"] != "0":
                schemaclasse.info["nom_geometrie"] = "geometrie"
        if schemaclasse.info["type_geom"] == "indef":
           print(ident, "apres _get_tables: type_geometrique", schemaclasse.info["type_geom"])

        schemaclasse.type_table = type_table


def _get_attributs(connect):
    """recupere les attributs"""
    types_base = connect.types_base
    schema_base = connect.schemabase
    fields = connect.attdef._fields
    fdebug = None
    if DEBUG:
        print("ecriture debug:", "lecture_base_attr_" + connect.type_base + ".csv")
        fdebug = open("lecture_base_attr_" + connect.type_base + ".csv", "w")
        fdebug.write("\n".join(fields) + "\n")

    for atd in connect.get_attributs():
        # atd = connect.attdef(*i)
        # print ('schema attributs', atd)
        if DEBUG:
            fdebug.write(";".join([str(v) if v is not None else "" for v in atd]))
            fdebug.write("\n")
        num_attribut = float(atd.num_attribut)
        classe = schema_base.setdefault_classe((atd.nom_groupe, atd.nom_classe))
        #        if 'G' in nom_attr:print ('type avant',nom_attr,type_attr)
        if not atd.type_attr:
            print(
                "attribut sans type", "g:", atd.nom_groupe, "c:", atd.nom_classe, "a:", atd.nom_attr
            )
        type_ref = atd.type_attr
        taille_att = atd.taille
        if "(" in atd.type_attr:  # il y a une taille
            tmp = atd.type_attr.split("(")
            if tmp[1][-1].isnumeric():
                type_ref = tmp[0]
                taille_att = tmp[1][-1]
        if type_ref.upper() in types_base:
            type_attr = types_base[type_ref.upper()]
        else:
            type_attr = connect.get_type(type_ref)

        if atd.enum:
            #            print ('detection enums ',atd.enum)
            #            if enum in schema_base.conformites:
            type_attr_base = "T"
            type_attr = atd.enum
        else:
            type_attr_base = type_attr

        clef_etr = ""
        if atd.clef_etrangere:
            cible_clef = atd.cible_clef if atd.cible_clef is not None else ""
            #            if atd.cible_clef is None:
            #                cible_clef = ''
            if not cible_clef:
                print(
                    "mdbaccess: erreur schema : cible clef etrangere non definie",
                    atd.nom_groupe,
                    atd.nom_classe,
                    atd.nom_attr,
                    atd.clef_etrangere,
                )
            #            print ('trouve clef etrangere',clef_etrangere)
            clef_etr = atd.clef_etrangere + "." + cible_clef
        #        if clef:  print (clef)
        index = atd.index if atd.index is not None else ""
        #        if index is None:
        #            index = ''
        if atd.clef_primaire:
            code = "P:" + str(atd.clef_primaire)
            if code not in index:
                index = index + " " + code if index else code

        obligatoire = atd.obligatoire == "oui"
        parametres_clef = atd.parametres_clef if "parametres_clef" in fields else ""
        #        if type_attr == 'geometry':
        #            print ('attribut',atd)
        classe.stocke_attribut(
            atd.nom_attr,
            type_attr,
            defaut=atd.defaut,
            type_attr_base=type_attr_base,
            taille=taille_att,
            dec=atd.decimales,
            force=True,
            alias=atd.alias,
            dimension=atd.dimension,
            clef_etr=clef_etr,
            ordre=num_attribut,
            mode_ordre="a",
            parametres_clef=parametres_clef,
            index=index,
            unique=atd.unique,
            obligatoire=obligatoire,
            multiple=atd.multiple,
        )

    if DEBUG:
        fdebug.close()


def get_schemabase(connect, mode_force_enums=1):
    """ recupere le schema complet de la base """
    debut = time.time()
    schema_base = connect.schemabase
    #    types_base = connect.types_base
    metas = {
        "type_base": connect.idconnect,
        "date_extraction": time.asctime(),
        "serveur": connect.serveur,
        "base": connect.base,
        "origine": "B",
        "user": connect.user,
    }
    schema_base.metas = metas
    for i in connect.get_enums():
        nom_enum, ordre, valeur, alias = i[:4]
        conf = schema_base.get_conf(nom_enum)
        conf.stocke_valeur(valeur, alias, ordre=ordre, mode_force=mode_force_enums)

    _get_attributs(connect)
    _get_tables(connect)

    for i in connect.db_get_schemas():
        nom, alias = i
        schema_base.alias_groupes[nom] = alias if alias else ""
    #        print ('recuperation alias',nom,alias)
    connect.get_elements_specifiques(schema_base)
    schema_base.dialecte = connect.dialecte
    LOGGER.info(
        "lecture schema base "
        + schema_base.nom
        + ":"
        + str(len(schema_base.classes))
        + " tables en "
        + str(int(time.time() - debut))
        + "s ("
        + schema_base.dialecte
        + ")"
    )


def dbaccess(stock_param, nombase, type_base=None, chemin=""):
    """ouvre l'acces a la base de donnees et lit le schema"""
    codebase = nombase
    base = nombase
    serveur = ''
#    print('--------acces base de donnees', codebase, "->", type_base, 'exist:',
#          codebase in stock_param.dbconnect)
    #    print('bases connues', stock_param.dbconnect.keys())
    if codebase in stock_param.dbconnect:
        return stock_param.dbconnect[codebase]
    defmodeconf = 1
    systables = stock_param.get_param("tables_systeme")
    if not type_base:  # on pioche dans les variables
        base = stock_param.get_param("base_" + codebase, "")
        serveur = stock_param.get_param("server_" + codebase, "")
        type_base = stock_param.get_param("db_" + codebase, "")
        if not base:
            print("dbaccess: base non definie", nombase, codebase, sorted(stock_param.context.vlocales) )
            return None

    if type_base not in DATABASES:
        print("type_base inconnu", type_base)
        return None

    dbdef = DATABASES[type_base]
    if dbdef.svtyp == "file":
        # c'est une base fichier elle porte le nom du fichier et le serveur c'est le chemin
        #       if stock_param.get_param("racine",''):
        #       serveur = os.path.join(stock_param.get_param("racine"), chemin)
        serveur = ""
        #        servertyp = type_base
        base = nombase
        print("filedb", type_base, "-->", nombase)

    defmodeconf = stock_param.get_param("mode_enums_" + codebase, 1)
    user = stock_param.get_param("user_" + codebase, "")
    passwd = stock_param.get_param("passwd_" + codebase, "")

    dbdef = DATABASES[type_base]
    connection = dbdef.acces(
        serveur, base, user, passwd, system=systables, params=stock_param, code=codebase
    )

    if connection.valide:
        #        print('connection valide', serveur)
        connection.gensql = dbdef.gensql(connection=connection)
        connection.type_serveur = dbdef.svtyp
        connection.geom_from_natif = dbdef.converter
        connection.geom_to_natif = dbdef.geomwriter
        connection.format_natif = dbdef.geom

        schema_base = stock_param.init_schema("#" + codebase, "B", defmodeconf=defmodeconf)
        connection.schemabase = schema_base

        schema_base.dbsql = connection.gensql
        get_schemabase(connection)
        stock_param.dbconnect[codebase] = connection
        connection.connection.commit() # on referme toutes les ressources
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
            print("seul des fichiers", loadext, "peuvent etre lances par cette commande")
            print("!!!!!!!!!!fichier incompatible", file, files)
            return False
    if helpername is None:
        print("pas de loader defini sur la base ", base)
        return False
    helper = stock_param.get_param(helpername)
    if not helper:
        print("pas de programme externe defini", helpername)
        return False
    return helper


def setpath(stock_param, nom):
    """prepare les fichiers de log pour les programmes externes"""
    if nom:
        nom = os.path.join(stock_param.get_param("_sortie"), nom)
        rep = os.path.dirname(nom)
        if rep:
            os.makedirs(rep, exist_ok=True)
    return nom


def dbextload(regle_courante, base, files, log=None):
    """charge un fichier a travers un loader"""
    print("extload chargement ", base, files)
    stock_param = regle_courante.stock_param
    connect = dbaccess(stock_param, base)
    if connect is None:
        return False
    connect = stock_param.dbconnect[base]
    helpername = connect.load_helper
    loadext = connect.load_ext
    helper = get_helper(base, files, loadext, helpername, stock_param)
    reinit = regle_courante.getvar("reinit", "0")
    vgeom = regle_courante.getvar("valide_geom", "1")
    if helper:
        return connect.extload(helper, files, logfile=log, reinit=reinit, vgeom=vgeom)
    return False


def dbextdump(regle_courante, base, niveau, classe, dest="", log=""):
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
        print("extdump", regle_courante.context.vlocales, extworkers)
        resultats = connect.extdump(helper, liste_tables, dest, log, workers=extworkers)
        #        print(' extdump' , resultats)
        if resultats:
            for idclasse in resultats:
                schema_travail.classes[idclasse].objcnt = resultats[idclasse]
            regle_courante.setvar("schema_entree", schema_travail.nom, loc=0)
    return False


def dbextalpha(regle_courante, base: str, niveau, classe, dest="", log=""):
    """extrait un fichier a travers un loader et lance les traitements"""

    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante, base, niveau, classe
    )
    if connect is None:
        return False
    if not liste_tables:
        print("pas de tables a sortir", base, niveau, classe)
        return False
    print ('----------------------------------------extalpha schema:', schema_travail.nom, len(schema_travail.classes))
    regle_courante.setvar("schema_entree", schema_travail.nom)
    helpername = connect.dump_helper
    helper = get_helper(base, [], "", helpername, regle_courante.stock_param)
    if helper:
        #        workers, extworkers = regle_courante.get_max_workers()
        print("extalpha",regle_courante, regle_courante.context, regle_courante.get_max_workers(), regle_courante.getvar('_wid'))
        resultats = connect.extalpha(
            regle_courante,
            helper,
            liste_tables,
            dest,
            log,
            nbworkers=regle_courante.get_max_workers(),
        )
        #        print(' extdump' , resultats)
        if resultats:
            for idclasse in resultats:
                schema_travail.classes[idclasse].objcnt = resultats[idclasse]

    return False


def dbrunsql(stock_param, base, file, log=None, out=None):
    """charge un fichier sql a travers un client sql externe"""
    print("mdba execution sql via un programme externe", base, file)
    connect = dbaccess(stock_param, base)
    if connect is None:
        return False
    connect = stock_param.dbconnect[base]
    helpername = connect.sql_helper
    helper = get_helper(base, [file], ".sql", helpername, stock_param)
    if helper:
        logfile = setpath(stock_param, log)
        outfile = setpath(stock_param, out)
        print("runsql: demarrage", helpername, helper, "user:", connect.user)
        return connect.runsql(helper, file, logfile, outfile)
    return False


def get_connect(
    stock_param,
    base,
    niveau,
    classe,
    tables="A",
    multi=True,
    nocase=False,
    nomschema="",
    type_base=None,
    chemin="",
):
    """ recupere la connection a la base et les schemas qui vont bien"""
    connect = dbaccess(stock_param, base, type_base=type_base, chemin=chemin)

    if connect is None:
        LOGGER.error("connection base invalide" + str(base))
        return None

    nomschema = nomschema if nomschema else connect.schemabase.nom.replace("#", "")
    schema_travail = stock_param.init_schema(nomschema, "B", modele=connect.schemabase)
    schema_travail.metas = dict(connect.schemabase.metas)
    schema_travail.metas["tables"] = tables
    liste2 = []
    #    print ( 'schema base ',schema_base.classes.keys())
    for ident in select_tables(connect.schemabase, niveau, classe, tables, multi, nocase):
        classe = connect.schemabase.get_classe(ident)
        #        print ('classe a copier ',classe.identclasse,classe.attributs)
        clas2 = classe.copy(ident, schema_travail)
        clas2.setinfo("objcnt_init", classe.getinfo("objcnt_init", "0"))
        # on renseigne le nombre d'objets de la table
        clas2.type_table = classe.type_table  # pour eviter qu elle soit marqueee interne

        liste2.append(ident)
    niveau = tablesorter(liste2, connect.schemabase)
    #        print('tri des tables ,niveau max', {i:niveau[i] for i in niveau if niveau[i] > 0})
    if schema_travail.elements_specifiques:
        connect.select_elements_specifiques(schema_travail, liste2)

    LOGGER.info(
        "get_connect schema_travail "
        + str(len(connect.schemabase.classes))
        + "-->"
        + str(len(schema_travail.classes))
        + str(len(schema_travail.conformites))
    )
    connect.connection.commit()
    return connect, schema_travail, liste2


def get_typecode(curs, typecode):
    """recupere le type du retour par defaut texte"""
    return "text"
    connection = curs.connect
    connection.request()


def schema_from_curs(curs):
    """ cree un schema de classe a partir d'une requete generique"""
    nom, typecode, _, _, taille, dec, _ = curs.description


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
    base="",
    treq=0,
    cond="",
):
    """ recupere les resultats et génére les objets"""
    regle_debut = regle_courante.branchements.brch["next"]
    traite_objet = regle_courante.stock_param.moteur.traite_objet

    # print ('dbaccess:sortie_resultat ',type_geom,type(curs))
    # valeurs = curs.fetchone()
    # print ('dbaccess:recuperation valeurs ',valeurs)
    schema_init = None
    stock_param = regle_courante.stock_param
    if not niveau:
        niveau = schema_classe_travail.fichier
    if stock_param.get_param("schema_entree"):
        schema_init = stock_param.schemas[stock_param.get_param("schema_entree")]
        if schema_init:
            newid = schema_init.map_dest((niveau, classe))
            print("mdba: mapping:", (niveau, classe), "->", newid)
            niveau, classe = newid
        schema_classe_travail = schema_init.setdefault_classe((niveau, classe))
    if stock_param.get_param("printpending"):
        print()
    print("...%-50s" % ("%s : %s.%s" % (connect.base, niveau, classe)), end="", flush=True)
    stock_param.set_param('printpending', 1)
    nbvals = 0
    attlist = curs.attlist
    # print (' attributs recuperes avant', attlist)

    if type_geom != "0":
        attlist.append("#geom")
    # print (' attributs recuperes ', attlist)
    geom_from_natif = connect.geom_from_natif
    format_natif = connect.format_natif
    stock_param = regle_courante.stock_param
    maxobj = stock_param.get_param("lire_maxi", 0)
    nb_pts = 0
    sys_cre, sys_mod = None, None
    if connect.sys_cre in attlist:
        sys_cre = connect.sys_cre
    if connect.sys_mod in attlist:
        sys_mod = connect.sys_mod
    tget = time.time()
    decile =curs.decile
    for valeurs in curs.cursor:
        #        print ("geometrie valide",obj.geom_v.valide)
        #        print ('dbaccess: creation objet',niveau,classe,obj.ident,type_geom)
        obj = Objet(niveau, classe, format_natif=format_natif,
                        conversion=geom_from_natif,
                        attributs = zip(attlist, [str(i) if i is not None else "" for i in valeurs]))
        # if '#geom' in attlist:
        #     print ('attlist', attlist)
        #     print (valeurs,valeurs)
        #     print ('zip ',zip(attlist, [str(i) if i is not None else "" for i in valeurs]))
        #     print ('objet lu',obj)
        #     raise
        if type_geom == "1":  # on prepare les angles s'il y en a
            obj.attributs["#angle"] = obj.attributs.get("angle", "0")

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
        # print ("dbaccess sortie_resultats vers regle:",regle_courante.ligne,regle_debut.ligne)
        obj.setorig(nbvals)
        traite_objet(obj, regle_debut)
        if nbvals == maxobj:
            break
        # deco avec petits points por faire patienter
        if nbvals >decile:
            decile +=curs.decile
            nb_pts += 1
            print(".", end="", flush=True)
    tget = time.time() - tget
    if nb_pts < 10:
        print("." * (10 - nb_pts), end="")
    attrs, vals = cond
    cdef = repr(cond) if attrs else ""

    print("%8d en %8d ms (%8d) %s" % (nbvals, (tget + treq) * 1000, treq * 1000, cdef))
    stock_param.set_param('printpending', 0)
    curs.close()
    return nbvals


def recup_schema(
    regle_courante, base, niveau, classe, nom_schema="", type_base=None, chemin="", mods=None
):
    """ recupere juste les schemas de la base sans donnees """
    stock_param = regle_courante.stock_param
    cmp1 = mods if mods is not None else [i.upper() for i in regle_courante.params.cmp1.liste]
    #    cmp2 = [i.upper for i in regle_courante.params.cmp2.liste]

    multi = not "=" in cmp1
    nocase = "NOCASE" in cmp1
    tables = "".join([i for i in cmp1 if i not in {"=", "NOCASE", "S", "L"}])
    #    tables = [i for i in cmp1 if i in DBACMODS]
    if not tables:
        tables = "A"
    #    print ('mdba:recup_schema',nom_schema)
    retour = get_connect(
        stock_param,
        base,
        niveau,
        classe,
        tables,
        multi,
        nocase=nocase,
        nomschema=nom_schema,
        type_base=type_base,
        chemin=chemin,
    )

    if retour:
        connect, schema_travail, liste_tables = retour

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
#        print("recup_schema", schema_base, schema_travail, stock_param.schemas.keys())
        return (connect, schema_base, schema_travail, liste_tables)
    else:
        print("erreur de connection a la base", base, niveau, classe)
    return (None, None, None, None)


def lire_table(ident, regle_courante, parms=None):
    """lecture directe"""
    if ident is None:
        return 0
    niveau, classe = ident
    base, attribut, valeur, mods, sortie, v_sortie, ordre, type_base, chemin, reqdict, maxobj = (
        parms
    )
    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante, base, niveau, classe, type_base=type_base, chemin=chemin, mods=mods
    )

    schema_classe_base = schema_base.get_classe(ident)
    #            print ('dbaccess : ',ident,schema_base.nom,schema_classe_base.info["type_geom"])
    #        print ('dbaccess : ',ident)
    schema_classe_travail = schema_travail.get_classe(ident)
    if isinstance(attribut, list):
        if ident in reqdict:
            attr, val = reqdict[ident]
        else:
            attr, val = "", ""
    else:
        attr, val = attribut, valeur
    #        print("id attr,val", ident, attr, val)
    #        print('%-60s'%('%s : %s.%s'% (connect.type_base, niveau,
    #    classe)), end='', flush=True)
    if attr and attr not in schema_classe_travail.attributs and attr not in connect.sys_fields:
        return 0  # on a fait une requete sur un attribut inexistant: on passe
    treq = time.time()

    curs = connect.req_alpha(ident, schema_classe_travail, attr, val, mods, maxobj, ordre=ordre)
    #        print ('-----------------------traitement curseur ', curs,type(curs) )
    treq = time.time() - treq
    connect.connection.commit()

    if curs:
        res = sortie_resultats(
            regle_courante,
            curs,
            niveau,
            classe,
            connect,
            sortie,
            v_sortie,
            schema_classe_base.info["type_geom"],
            schema_classe_travail,
            base=base,
            treq=treq,
            cond=(attr, val),
        )

        if sortie:
            for nom in sortie:
                if nom and nom[0] != "#":
                    schema_classe_travail.stocke_attribut(nom, "T")
        return res
    return 0


def recup_donnees_req_alpha(
    regle_courante,
    base,
    niveau,
    classe,
    attribut,
    valeur,
    mods=None,
    sortie=None,
    v_sortie=None,
    ordre=None,
    type_base=None,
    chemin="",
):
    """ recupere les objets de la base de donnees et les passe dans le moteur de regles"""
    #    debut = time.time()
    #    print('mdb: recup_donnees alpha', regle_courante, base, mods, sortie, v_sortie)
    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante, base, niveau, classe, type_base=type_base, chemin=chemin, mods=mods
    )
    if connect is None:
        return 0
    reqdict = dict()
    if isinstance(attribut, list):
        for niv, cla, att, val in zip(niveau, classe, attribut, valeur):
            reqdict[(niv, cla)] = (att, val)
    #    print ("reqdict",reqdict)

    stock_param = regle_courante.stock_param
    maxobj = int(stock_param.get_param("lire_maxi", 0))

    res = 0
    #    print ('dbacces: recup_donnees_req_alpha',connect.idconnect,type_base)
    curs = None
    for ident in liste_tables:
        attr, val = attribut, valeur
        treq = time.time()
        if ident is not None:

            niveau, classe = ident
            schema_classe_base = schema_base.get_classe(ident)
            #            print('dbaccess : ', ident, schema_base.nom, schema_classe_base.info["type_geom"])
            #        print ('dbaccess : ',ident)
            schema_classe_travail = schema_travail.get_classe(ident)
            schema_classe_travail.info["type_geom"] = schema_classe_base.info["type_geom"]
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

            curs = connect.req_alpha(ident, schema_classe_base, attr, val, mods, maxi=maxobj, ordre=ordre)
            connect.connection.commit()
        #        print ('-----------------------traitement curseur ', curs,type(curs) )
            treq = time.time() - treq
            if curs:
                res += sortie_resultats(
                    regle_courante,
                    curs,
                    niveau,
                    classe,
                    connect,
                    sortie,
                    v_sortie,
                    schema_classe_base.info["type_geom"],
                    schema_classe_travail,
                    base=base,
                    treq=treq,
                    cond=(attr, val),
                )

            if sortie:
                for nom in sortie:
                    if nom and nom[0] != "#":
                        schema_classe_travail.stocke_attribut(nom, "T")

    if stock_param is not None:
        stock_param.padd("_st_lu_objs", res)
        stock_param.padd("_st_lu_tables", len(liste_tables) if liste_tables is not None else 0)
    return res


def reset_liste_tables(regle_courante, base, niveau, classe, type_base=None, chemin="", mods=None):
    """ genere un script de reset de tables"""
    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante, base, niveau, classe, type_base=type_base, chemin=chemin, mods=mods
    )
    if liste_tables:
        travail = reversed(liste_tables)  # on inverse l'ordre c est de la destruction
        gensql = connect.gensql

        script2 = [gensql.prefix_charge(niveau, classe, "TDS") for niveau, classe in travail]

        script1 = [gensql.prefix_charge(niveau, classe, "G") for niveau, classe in travail]
        script3 = [gensql.tail_charge(niveau, classe, "G") for niveau, classe in travail]
        print("reset:script a sortir ", len(script1), len(script2), len(script3))
        return script1 + script2 + script3
    return []


def recup_count(
    regle_courante, base, niveau, classe, attribut, valeur, mods=None, type_base=None, chemin=""
):
    """ recupere des comptages en base"""
    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante, base, niveau, classe, type_base=type_base, chemin=chemin, mods=mods
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
            connect.connection.commit()

        #        print ('retour ',nb)
            if reponse and reponse[0]:
                total += reponse[0][0]
    return total


def recup_table_parametres(
    stock_param, nombase, niveau, classe, clef=None, valeur=None, ordre=None, type_base=None
):
    """lit une table en base de donnees et retourne le tableau de valeurs """
    #    print('recup_table', nombase, niveau, classe, "type_base", type_base)
    LOGGER.info(
        "recup table en base " + nombase + ":" + niveau + "." + classe + " type_base" + type_base
    )
    retour = get_connect(
        stock_param, nombase, [niveau], [classe], tables="A", multi=0, type_base=type_base
    )
    if retour:
        connect, schema_travail, _ = retour
    else:
        return None

    ident = (niveau, classe)
    curs = connect.req_alpha(
        ident, schema_travail.get_classe(ident), clef, valeur, "", 0, ordre=ordre
    )
    connect.connection.commit()
    resultat = [valeurs for valeurs in curs.cursor]
    return resultat


def recup_maxval(stock_param, nombase, niveau, classe, clef, type_base=None):
    """ recupere la valeur maxi d'un champ en base """
    #    print('recup_table', nombase, niveau, classe, type_base)
    retour = get_connect(stock_param, nombase, niveau, classe, "A", False, type_base=type_base)
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
        connect.connection.commit()
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
    stock_param = regle_courante.stock_param
    maxobj = stock_param.get_param("lire_maxi", 0)

    connect, schema_base, schema_travail, liste_tables = recup_schema(
        regle_courante, base, niveau, classe, type_base=type_base, chemin=chemin, mods=mods
    )
    if connect is None:
        return 0
    maxobj = stock_param.get_param("lire_maxi", 0)
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
        connect.connection.commit()
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
        schema_classe_travail.info["type_geom"] = schema_classe_postgis.info["type_geom"]
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

    def __init__(self, nom, liste_att=None, encoding="utf-8", stock_param=None):

        self.nom = nom
        self.liste_att = liste_att
        self.fichier = None
        self.encoding = encoding
        self.schema_base = None
        retour = get_connect(
            stock_param,
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
            self.schema_base = connect.schema_base

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


# def _set_liste_attributs(obj, attributs):
#    '''positionne la liste d'attributs a sortir'''
#    if attributs:
#        return attributs
#    return obj.schema.get_liste_attributs()
def dbload(regle, base, niveau, classe, obj):
    pass


def dbupdate(regle, base, niveau, classe, attribut, obj):
    pass


def ecrire_objets_db(regle, _, attributs=None, rep_sortie=None):
    """ecrit un ensemble d'objets en base"""
    # ng, nf = 0, 0
    # memoire = defs.stockage
    sorties = regle.stock_param.sorties
    rep_sortie = regle.getvar("_sortie") if rep_sortie is None else rep_sortie
    numero = regle.numero
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

                ressource = sorties.get_res(numero, nom)
                if ressource is None:
                    os.makedirs(os.path.dirname(nom), exist_ok=True)
                    #                    liste_att = _set_liste_attributs(obj, attributs)
                    liste_att = obj.schema.get_liste_attributs(liste=attributs)
                    dbwr = DbWriter(
                        nom,
                        liste_att,
                        encoding=regle.getvar("codec_sortie", "utf-8"),
                    )
                    sorties.creres(numero, nom, dbwr)
                    ressource = sorties.get_res(numero, nom)
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
        ressource = sorties.get_res(regle.numero, dest)
        if ressource is None:
            liste_att = obj.schema.get_liste_attributs(liste=attributs)
            #            liste_att = _set_liste_attributs(obj, attributs)
            swr = DbWriter(
                dest,
                liste_att,
                encoding=regle.getvar("codec_sortie", "utf-8"),
                stock_param=regle.stock_param,
            )
            sorties.creres(regle.numero, dest, swr)
            ressource = sorties.get_res(regle.numero, dest)
            #            print ('nouv ressource', regle.numero,nom,ressource.handler.nom)
            regle.dident = dest
            regle.ressource = ressource
        else:
            #            print ('ressource', regle.numero,nom,ressource.handler.nom)
            if dest != regle.dident:
                #                liste_att = _set_liste_attributs(obj, attributs)
                liste_att = obj.schema.get_liste_attributs(liste=attributs)
                ressource.handler.set_liste_att(liste_att)
                regle.dident =  dest
                regle.ressource = ressource
    regle.ressource.handler.write(obj)
