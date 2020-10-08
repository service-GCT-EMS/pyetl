# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 19:34:45 2018

@author: claude
outils generiques de manipulation de listes
"""
import sys
import re
import os
import itertools
import linecache
import traceback
import logging
import glob
import codecs
import zipfile
import typing as T

from pyetl.formats.generic_io import READERS
from pyetl.vglobales import DEFCODEC

LOGGER = logging.getLogger("pyetl")


def description_schema(regle, nom, schema):
    """gere les definitions de schema associees a l'attribut resultat
    la description d'uun attribut prend la forme suivante ([p:]type,[D:defaut],[index])
    p: position du champ : par defaut dernier champ -1 = premier
    type : T E/EL S/BS F D

    description des index :
    PK: : clef primaire
    X: index
    U:  : unique
    FK: : clef etrangere doit etre suivi de la ref schema.table.attribut"""
    # TODO: gerer les enums
    type_att_sortie = "T"
    position = -1
    valeur_defaut = ""
    def_index = ""
    for att in regle.params.att_sortie.liste:
        desc_schema = regle.params.att_sortie.definition
        if desc_schema:
            if ":" in desc_schema[0]:  # ( indicateur de position)
                position = int(desc_schema[0][: desc_schema[0].index(":")])
                type_att_sortie = desc_schema[0][desc_schema[0].index(":") + 1 :]
            else:
                type_att_sortie = desc_schema[0]
            if not type_att_sortie:
                type_att_sortie = "A"
            if len(desc_schema) > 1:
                if desc_schema[1][:2] == "D:":
                    valeur_defaut = desc_schema[1][2:]
                else:
                    def_index = desc_schema[1]
            if len(desc_schema) > 2:
                def_index = desc_schema[2]
        # on cree un attribut modele pour la sortie
        modele = schema.get_attribut(nom, 30)
        modele.nom_court = ""
        modele.type_att = type_att_sortie
        modele.type_att_base = modele.type_att
        modele.defaut = valeur_defaut
        modele.ordre = position
        modele.def_index = def_index
        regle.params.def_sortie[nom] = modele


def scandirs(
    rep_depart, chemin, rec, pattern=None, dirpattern=None
) -> T.Iterator[T.Tuple[str, str]]:
    """parcours recursif d'un repertoire."""
    path = os.path.join(rep_depart, chemin)
    if os.path.isfile(path):
        chemin = os.path.dirname(chemin)
        yield (str(os.path.basename(path)), str(chemin))
        return
    if "*" in path:
        for element in glob.glob(path):
            fichier = os.path.basename(element)
            place = os.path.dirname(element)
            chemin = place.replace(rep_depart, "")
            if pattern is None or re.search(pattern, fichier):
                yield (str(fichier), str(chemin))
        return
    if os.path.exists(path):
        for element in os.listdir(path):
            #        for element in glob.glob(path):
            if os.path.isdir(os.path.join(path, element)) and (
                not dirpattern or re.search(dirpattern, os.path.join(chemin, element))
            ):
                if rec:
                    yield from scandirs(
                        rep_depart,
                        os.path.join(chemin, element),
                        rec,
                        pattern,
                        dirpattern,
                    )
            else:
                if pattern is None or re.search(pattern, os.path.join(chemin, element)):
                    # print ('match',pattern, chemin, element)
                    yield (str(os.path.basename(element)), str(chemin))
                # else:
                #     pass
                # print ('not match',pattern, chemin, element)


def getfichs(regle, obj):
    """recupere une liste de fichiers"""

    #    mapper = regle.stock_param
    racine = regle.params.cmp1.getval(obj)
    if not racine:
        racine = regle.getvar("_entree", ".")
    nom = regle.getval_entree(obj)
    # print("getfichs:", os.path.join(racine, nom) if nom else racine)
    yield from scan_entree(
        rep=os.path.join(racine, nom) if nom else racine,
        force_format=regle.getvar("F_entree"),
        fileselect=regle.getvar("fileselect"),
        dirselect=regle.getvar("dirselect"),
        filtre_entree=regle.getvar("filtre_entree"),
    )


def printexception():
    """affichage d exception avec traceback"""
    err, exc_obj, infodebug = sys.exc_info()
    frame = infodebug.tb_frame
    lineno = infodebug.tb_lineno
    fname = frame.f_code.co_filename
    linecache.checkcache(fname)
    line = linecache.getline(fname, lineno, frame.f_globals)
    nom = err.__name__
    print(
        """{}:{}\nIN      :{}\nLINE {} {}:""".format(
            nom, exc_obj, fname, lineno, line.strip()
        )
    )
    traceback.print_tb(infodebug)


def renseigne_attributs_batch(regle, obj, retour):
    """stocke les infos du traitement dans les objets"""
    #    print ('recu ', parametres)
    obj.attributs["#objets_lus"] = regle.getvar("_st_lu_objs", "0")
    obj.attributs["#fichiers_lus"] = regle.getvar("_st_lu_fichs", "0")
    obj.attributs["#objets_ecrits"] = regle.getvar("_st_wr_objs", "0")
    obj.attributs["#fichiers_ecrits"] = regle.getvar("_st_wr_fichs", "0")
    obj.attributs[regle.params.att_sortie.val] = str(retour)


def objloader(regle, obj):
    """charge des objets depuis des fichiers"""
    nb_lu = 0
    lecture = regle.stock_param.lecture
    retour = False
    for i, parms in getfichs(regle, obj):
        # print ('lecture', i, parms)
        try:
            nb_lu += lecture(i, regle=regle, parms=parms)
            retour = True
        except StopIteration as abort:
            if abort.args[0] == "2":
                continue
    #    print("lecture",nb_lu)
    if not retour:
        print("chargeur: pas de fichiers d'entree")
    if regle.params.att_sortie.val:
        obj.attributs[regle.params.att_sortie.val] = str(nb_lu)
    return retour


def expandfilename(nom, rdef, racine="", chemin="", fichier=""):
    """prepare un nom de fichier en fonction de modifieurs"""
    rplaces = {"D": rdef, "R": racine, "C": chemin, "F": fichier}
    return re.sub(r"\[([DRCF])\]", lambda x: rplaces.get(x.group(1), ""), nom)


def hasbom(fichier, encoding):
    if open(fichier, "rb").read(10).startswith(codecs.BOM_UTF8):
        return "utf-8-sig"
    return encoding


def charge_fichier(fichier, rdef, codec=None, debug=False, defext=""):
    """chargement en memoire d'un fichier"""
    f_interm = expandfilename(
        fichier, rdef
    )  # fichier de jointure dans le repertoire de regles
    stock = []
    if not os.path.isfile(f_interm):
        if defext and not os.path.splitext(f_interm)[1]:
            f_interm = f_interm + defext
    try:
        if not codec:
            codec = DEFCODEC
        codec = hasbom(f_interm, codec)
        # print("codec lecture commandes:",codec, DEFCODEC)
        with open(f_interm, "r", encoding=codec) as cmdfile:
            nlin = 0
            for ligne in cmdfile:
                nlin += 1
                stock.append((nlin, ligne))
        if debug:
            print("chargement", fichier)
    except FileNotFoundError:
        print("chargement:fichier introuvable", fichier)
    return stock


def charge_liste_classes(fichier, codec=DEFCODEC, debug=False, taille=1):
    codec = hasbom(fichier, codec)
    retour = dict()
    with open(fichier, "r", encoding=codec) as fich:
        for i in fich:
            ligne = i.replace("\n", "")  # on degage le retour chariot
            if ligne.startswith("!"):
                if ligne.startswith("!!"):
                    ligne = ligne[1:]
                else:
                    continue
            liste = ligne.split(";")
            if not liste:
                continue
            if "." in liste[0]:
                liste = liste[0].split(".") + ["", ""]
            if liste[0].startswith("B:"):
                ident = (liste[0], ".".join(liste[1:3]))
            else:
                ident = ("", ".".join(liste[:2]))
            retour[ident] = ligne
    return retour


def _charge_liste_csv(
    fichier, codec="", debug=False, taille=1, positions=None, type_cle="txt"
):
    if not codec:
        codec = DEFCODEC
    """prechargement d un fichier de liste csv"""
    stock = dict()
    if taille > 0:  # taille = 0 veut dire illimite
        if not positions:
            positions = range(taille)
        if len(positions) > taille:
            positions = positions[:taille]
    try:
        codec = hasbom(fichier, codec)
        with open(fichier, "r", encoding=codec) as fich:
            for i in fich:
                ligne = i.replace("\n", "")  # on degage le retour chariot
                if ligne.startswith("!"):
                    if ligne.startswith("!!"):
                        ligne = ligne[1:]
                    else:
                        continue
                liste = ligne.split(";")
                if any([i.strip() for i in liste]):
                    if taille <= 0:
                        stock[ligne] = liste
                    else:
                        if type_cle != "txt":
                            bdef = liste.pop(0)
                            tmp = bdef.split(".", taille)
                            tmp.extend(liste)
                            liste = tmp
                        if len(liste) < taille:
                            liste = list(
                                itertools.islice(itertools.cycle(liste), taille)
                            )
                        stock[tuple([liste[i] for i in positions])] = liste
        if debug:
            print("chargement liste", fichier)
    except FileNotFoundError:
        # print("fichier liste introuvable ", fichier)
        LOGGER.warning("fichier liste introuvable " + fichier)
    # print("prechargement csv", stock)
    return stock


def _extract(ligne, clef):
    """ extrait un element de la ligne"""
    l_tmp = ligne.split(clef)
    if len(l_tmp) > 1:
        liste = l_tmp[1].split(" ")
        valeur = liste[0].replace('"', "")
        valeur = valeur.replace("'", "")
        return valeur
    return ""


def _charge_liste_projet_qgs(fichier, codec="", debug=False, taille=1, type_cle="txt"):
    """prechargement d un fichier projet qgis"""
    if not codec:
        codec = DEFCODEC
    stock = dict()
    try:
        codec = hasbom(fichier, codec)
        with open(fichier, "r", encoding=codec) as fich:
            print("lecture projet qgs", taille, fichier, type_cle)
            for i in fich:

                if "datasource" in i:
                    table = _extract(i, "table=")
                    database = _extract(i, "dbname=")
                    host = _extract(i, "host=")
                    port = _extract(i, "port=")
                    # l_tmp = i.split("table=")
                    # if len(l_tmp) > 1:

                    #     liste = l_tmp[1].split(" ")
                    #     valeur = liste[0].replace('"', "")
                    if table:
                        dbdef = (database, "host=" + host.lower(), "port=" + port)
                        if taille == 1:
                            clef = table
                        elif taille == 2:
                            clef = tuple(table.split(".", 1))
                        else:

                            niv, cla = table.split(".", 1)
                            if type_cle == "txt":
                                txt = ",".join(dbdef)
                                clef = (txt, niv, cla)
                            else:
                                clef = (dbdef, niv, cla)
                        stock[clef] = (table, dbdef)

        if debug:
            print("chargement liste", fichier)
    except FileNotFoundError:
        # print("fichier liste introuvable ", fichier)
        LOGGER.warning("fichier liste introuvable " + fichier)
    # print ('lus fichier qgis ',fichier,list(stock))
    return stock


def charge_liste(
    fichier, codec="", debug=False, taille=1, positions=None, type_cle="txt"
):
    """prechargement des fichiers de comparaison """
    # fichier de jointure dans le repertoire de regles
    clef = ""
    if "*." in os.path.basename(fichier):
        clef = os.path.basename(fichier)
        clef = os.path.splitext(clef)[-1]
        fichier = os.path.dirname(fichier)
    #        print(' clef ',clef,fichier)
    stock = dict()
    LOGGER.info("charge_liste: chargement " + str(fichier))

    #    print ('-------------------------------------------------------chargement',fichier)
    for f_interm in str(fichier).split(","):
        if os.path.isdir(
            f_interm
        ):  # on charge toutes les listes d'un repertoire (csv et qgs)
            for i in os.listdir(f_interm):
                if clef in i:
                    LOGGER.debug("chargement liste " + i + " repertoire " + f_interm)

                    #                    print("chargement liste ", i, 'repertoire:', f_interm)
                    if os.path.splitext(i)[-1] == ".qgs":
                        stock.update(
                            _charge_liste_projet_qgs(
                                os.path.join(f_interm, i),
                                codec=codec,
                                debug=debug,
                                taille=taille,
                                type_cle=type_cle,
                            )
                        )
                    elif os.path.splitext(i)[-1] == ".csv":
                        stock.update(
                            _charge_liste_csv(
                                os.path.join(f_interm, i),
                                taille=taille,
                                codec=codec,
                                debug=debug,
                                type_cle=type_cle,
                            )
                        )
                else:
                    #                    print ('non retenu',i,clef)
                    pass
        else:
            if os.path.splitext(f_interm)[-1] == ".qgs":
                stock.update(
                    _charge_liste_projet_qgs(
                        f_interm, codec=codec, debug=debug, taille=taille
                    )
                )
            elif os.path.splitext(f_interm)[-1] == ".csv":
                stock.update(
                    _charge_liste_csv(
                        f_interm,
                        taille=taille,
                        codec=codec,
                        debug=debug,
                        positions=positions,
                    )
                )
    #    print ('charge liste',sorted(stock))
    if not stock:  # on a rien trouve
        pass
        # print("---------attention aucune liste disponible sous ", fichier)
    return stock


def conditionne_liste_classes(valeurs):
    """ transforme une liste en liste de classes """
    result = dict()
    for val in valeurs:
        if "." in val[0]:
            pass


# def get_listeval(txt):
#    """decode une liste sous la forme {v,v,v,v}"""
#    # c est une liste directement dans le champ
#    return txt[1:-1].split(",") if txt.startswith('{') else []


def prepare_mode_in(fichier, regle, taille=1, clef=0, type_cle="txt"):
    """precharge les fichiers utilises pour les jointures ou les listes d'appartenance
    formats acceptes:
        mode txt: clef simple (pour des selecteurs attributaires)
        mode n: (niveau,classe) ( pour des selections de schema)
        mode b: (base,niveau,classe)
        in:{a,b,c}                  -> liste de valeurs dans la commande
        in:#schema:nom_du_schema    -> liste des tables d'un schema
        in:nom_de_fichier           -> contenu d'un fichier
        in:[att1,att2,att3...]      -> attributs de l'objet courant
        in:(attributs)              -> noms des attributs de l'objet courant
        in:st:nom_du_stockage       -> valeurs des objets en memoire (la clef donne l'attribut)
        in:db:nom_de_la_table       -> valeur des attributs de l'objet en base (la clef donne le nom du champs)
    """
    stock_param = regle.stock_param
    fichier = fichier.strip()
    #    valeurs = get_listeval(fichier)
    liste_valeurs = fichier[1:-1].split(",") if fichier.startswith("{") else []
    valeurs = {i: i for i in liste_valeurs}
    #    print ('fichier a lire ',fichier,valeurs)
    if fichier.startswith("#schema"):  # liste de classes d'un schema
        mode = "in_s"
        decoupage = fichier.split(":")
        nom = ""
        if len(decoupage) > 1:
            nom = decoupage[1]
        if nom:
            print("lecture schema", nom, stock_param.schemas.keys())
            classes = stock_param.schemas.get(nom).classes.keys()
            if clef:
                valeurs = {i[clef]: i for i in classes}
            else:
                valeurs = {".".join(i): i for i in classes}
            print("classes a lire", valeurs)
    if valeurs:
        mode = "in_s"
    elif fichier == "(attributs)":  # liste d'attributs
        mode = "in_a"
    elif fichier.startswith("st:"):
        mode = "in_store"
        fichier = fichier[3:]
    elif fichier.startswith("db:"):
        mode = "in_db"
        fichier = fichier[3:]
    else:
        if re.search(r"\[[CF]\]", fichier):
            mode = "in_d"  # dynamique en fonction du repertoire de lecture
        else:
            mode = "in_s"  # jointure statique
            positions = []
            if clef:
                positions = [clef]
            #            print ('lecture disque ',fichier,':' in fichier)

            if "," in fichier:  # on a precise des positions a lire
                fi2 = fichier.split(",")
                fichier = fi2[0]
                positions = [int(i) for i in fi2[1:]]
            valeurs = charge_liste(
                fichier, taille=taille, positions=positions, type_cle=type_cle
            )
            # on precharge le fichier de jointure
            # print(
            #     "outils: chargement liste ",
            #     fichier,
            #     "------>",
            #     "\n".join((str(i) + ":" + str(valeurs[i]) for i in valeurs)),
            # )
    return mode, valeurs


def valide_auxiliaires(identifies, non_identifies):
    """ valide que les fichiers trouves sont connus"""
    auxiliaires = {a: defin[3] for a, defin in READERS.items()}
    for chemin, nom, extinc in non_identifies:
        if (chemin, nom) in identifies:
            extref = identifies[(chemin, nom)]
            if auxiliaires.get(extref) and extinc in auxiliaires.get(extref):
                #                    print ('connu ',chemin,nom,extinc,'->',extref)
                pass
            else:
                print("extention inconnue ", extref, "->", chemin, nom, extinc)


def getfilelist(
    rep=None, fileselect=None, dirselect=None
) -> T.Iterator[T.Tuple[str, str, str]]:
    " etablit la liste de fichiers sous forme d'iterateur"
    liste_entree = rep.split(",")
    for entree in liste_entree:
        if entree:
            # print ("filelist", entree)
            if os.path.isfile(entree):  # traitement un seul fichier
                yield (
                    str(os.path.basename(entree)),
                    str(""),
                    str(os.path.dirname(entree)),
                )
            elif "*" in entree:
                racine = str(os.path.dirname(entree))
                while "*" in racine:
                    racine = str(os.path.dirname(rep))
                yield from (
                    (
                        str(os.path.basename(i)),
                        str(os.path.dirname(i)).replace(rep, ""),
                        racine,
                    )
                    for i in glob.glob(entree, recursive=True)
                )
            else:
                yield from (
                    i + (entree,)
                    for i in scandirs(
                        entree, "", True, pattern=fileselect, dirpattern=dirselect
                    )
                )


def scan_entree(
    rep=None,
    force_format=None,
    fileselect=None,
    filtre_entree=None,
    dirselect=None,
    debug=0,
):

    identifies = dict()
    non_identifies = set()
    select = re.compile(filtre_entree if filtre_entree else ".*")
    for fichier, chemin, racine in getfilelist(
        rep=rep, fileselect=fileselect, dirselect=dirselect
    ):
        # print("scan2",fichier,chemin,racine)
        if not select.search(fichier):
            continue
        f_courant = str(os.path.join(racine, chemin, fichier))
        nom, ext = os.path.splitext(fichier.lower())
        ext = ext.replace(".", "")
        if force_format == "*":
            yield f_courant, (racine, chemin, nom, ext)
        else:
            nom = os.path.splitext(fichier)[0].lower()
            if force_format:
                ext = str(force_format)
            try:
                aux = READERS[ext][3]
                if "!" in aux:  # attention il y a des incompatibilites
                    nom = os.path.splitext(fichier)[0]
                    for ex2 in aux:
                        if os.path.isfile(
                            os.path.join(str(racine), str(chemin), str(nom + "." + ex2))
                        ):
                            raise KeyError
                identifies[racine, chemin, nom] = ext
                yield f_courant, (racine, chemin, fichier, ext)
            except KeyError:
                non_identifies.add((chemin, nom, ext))
        valide_auxiliaires(identifies, non_identifies)
