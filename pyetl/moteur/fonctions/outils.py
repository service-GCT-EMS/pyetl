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

from pyetl.formats.generic_io import Reader
from pyetl.formats.interne.objet import Objet
from pyetl.vglobales import DEFCODEC

MODIFFONC1 = re.compile(r"([nc]):(#?[a-zA-Z_][a-zA-Z0-9_]*)")
MODIFFONC2 = re.compile(r"P:([a-zA-Z_][a-zA-Z0-9_]*)")
LOGGER = logging.getLogger("pyetl")




def compilefonc(descripteur, variable, debug=False):
    """compile une expression de champs"""
    desc1 = descripteur.replace("N:", "n:")
    desc2 = desc1.replace("C:", "c:")
    desc3 = MODIFFONC1.sub(r"obj.atget_\1('\2')", desc2)
    desc4 = MODIFFONC2.sub(r"regle.getvar('\1')", desc3)
    if '__' in desc4:
        raise SyntaxError('fonction non autorisee:'+desc4)
    if debug:
        print("fonction a evaluer", "lambda " + variable + ": " + desc4)
    retour = eval("lambda " + variable + ": " + desc4,{})
    return retour


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



def scandirs(rep_depart, chemin, rec, pattern=None, dirpattern=None):
    """parcours recursif d'un repertoire."""
    path = os.path.join(rep_depart, chemin)
    if os.path.exists(path):
        for element in os.listdir(path):
#        for element in glob.glob(path):
            if os.path.isdir(os.path.join(path, element)) and (not dirpattern or re.search(dirpattern, os.path.join(chemin, element))):
                if rec:
                    yield from scandirs(rep_depart, os.path.join(chemin, element), rec, pattern, dirpattern)
            else:
                if pattern is None or re.search(pattern, os.path.join(chemin, element)):
                    # print ('match',pattern, chemin, element)
                    yield (os.path.basename(element), chemin)
                # else:
                #     pass


                    # print ('not match',pattern, chemin, element)


def getfichs(regle, obj):
    """recupere une liste de fichiers"""

    #    mapper = regle.stock_param
    racine = obj.attributs.get(regle.params.cmp1.val) if regle.dyn else regle.params.cmp1.val
    if not racine:
        racine = regle.getvar("_entree", ".")
    vobj = regle.getval_entree(obj)
    rep = os.path.join(racine, vobj) if vobj else racine
    fichs, parametres_fichiers = scan_entree(
        rep=rep,
        force_format=regle.getvar("F_entree"),
        fileselect=regle.getvar("fileselect"),
        dirselect=regle.getvar("dirselect"),
        filtre_entree=regle.getvar("filtre_entree"),
    )
    # fichs, parametres_fichiers = scan_entree(rep=rep)
    fparm = [(i, parametres_fichiers[i]) for i in fichs]
    return fparm


def printexception():
    """affichage d exception avec traceback"""
    err, exc_obj, infodebug = sys.exc_info()
    frame = infodebug.tb_frame
    lineno = infodebug.tb_lineno
    fname = frame.f_code.co_filename
    linecache.checkcache(fname)
    line = linecache.getline(fname, lineno, frame.f_globals)
    nom = err.__name__
    print("""{}:{}\nIN      :{}\nLINE {} {}:""".format(nom, exc_obj, fname, lineno, line.strip()))
    traceback.print_tb(infodebug)


def renseigne_attributs_batch(regle, obj, retour):
    """stocke les infos du traitement dans les objets"""
    #    print ('recu ', parametres)
    mapper = regle.stock_param
    obj.attributs["#objets_lus"] = mapper.get_param("_st_lu_objs", "0")
    obj.attributs["#fichiers_lus"] = mapper.get_param("_st_lu_fichs", "0")
    obj.attributs["#objets_ecrits"] = mapper.get_param("_st_wr_objs", "0")
    obj.attributs["#fichiers_ecrits"] = mapper.get_param("_st_wr_fichs", "0")
    obj.attributs[regle.params.att_sortie.val] = str(retour)


def prepare_batch_from_object(regle, obj):
    """extrait les parametres pertinents de l'objet decrivant le batch"""

    comm = regle.getval_entree(obj)
    commande = comm if comm else obj.attributs.get("commandes",'')
    #    print("commande batch", commande)

    mapper = regle.stock_param
    entree = obj.attributs.get("entree", mapper.get_param("_entree"))
    sortie = obj.attributs.get("sortie", mapper.get_param("_sortie"))
    numero = obj.attributs.get("#_batchnum", "0")
    #    chaine_comm = ':'.join([i.strip(" '") for i in commande.strip('[] ').split(',')])
    parametres = obj.attributs.get("parametres")  # parametres en format hstore
    params = None
    if parametres:
        params = ["=".join(re.split('"=>"', i)) for i in re.split('" *, *"', parametres[1:-1])]

    return (numero, commande, entree, sortie, params)


def execbatch(regle, obj):
    """execute un batch"""
    if obj is None:  # pas d'objet on en fabrique un sur mesure
        obj = Objet("_batch", "_batch", format_natif="interne")
    _, commande, entree, sortie, params = prepare_batch_from_object(regle, obj)
    processor = regle.stock_param.getpyetl(
        commande, liste_params=params, entree=entree, rep_sortie=sortie
    )
    if processor is None:
        return False

    processor.process(debug=1)
    renseigne_attributs_batch(regle, obj, processor.retour)
    return True


def objloader(regle, obj):
    """charge des objets depuis des fichiers"""
    nb_lu = 0
    mapper = regle.stock_param
    fichs = getfichs(regle, obj)
    if fichs:
        for i, parms in fichs:
            # print ('lecture', i)
            try:
                nb_lu += mapper.lecture(i, regle=regle, parms=parms)
            except StopIteration as abort:
                if abort.args[0] == "2":
                    continue
    #    print("lecture",nb_lu)
    else:
        print ("chargeur: pas de fichiers d'entree" )
    if regle.params.att_sortie.val:
        obj.attributs[regle.params.att_sortie.val] = str(nb_lu)
    return fichs


def expandfilename(nom, rdef, racine="", chemin="", fichier=""):
    """prepare un nom de fichier en fonction de modifieurs"""
    rplaces = {"D": rdef, "R": racine, "C": chemin, "F": fichier}
    return re.sub(r"\[([DRCF])\]", lambda x: rplaces.get(x.group(1), ""), nom)

def hasbom(fichier, encoding):
    if open(os.path.join(fichier), "rb").read(10).startswith(codecs.BOM_UTF8):
        return 'utf-8-sig'
    return encoding




def charge_fichier(fichier, rdef, codec=None, debug=False, defext=""):
    """chargement en memoire d'un fichier"""
    f_interm = expandfilename(fichier, rdef)  # fichier de jointure dans le repertoire de regles
    stock = []
    if not os.path.isfile(f_interm):
        if defext and not os.path.splitext(f_interm)[1]:
            f_interm = f_interm + defext
    try:
        if codec is None:
            codec = DEFCODEC
        codec = hasbom(f_interm, codec)
        with open(f_interm, "r", encoding=codec) as cmdfile:
            nlin = 0
            for ligne in cmdfile:
                nlin += 1
                stock.append((nlin, ligne))
        if debug:
            print("chargement", fichier)
    except FileNotFoundError:
        print("fichier introuvable ", fichier)
    return stock


def _charge_liste_csv(fichier, codec=DEFCODEC, debug=False, taille=1, positions=None):
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
                    if taille == -1:
                        stock[ligne] = liste
                    else:
                        if len(liste) < taille:
                            liste = list(itertools.islice(itertools.cycle(liste), taille))
                        stock[";".join([liste[i] for i in positions])] = liste
        if debug:
            print("chargement liste", fichier)
    except FileNotFoundError:
        print("fichier liste introuvable ", fichier)
    #    print('prechargement csv', stock)
    return stock


def _charge_liste_projet_qgs(fichier, codec=DEFCODEC, debug=False):
    """prechargement d un fichier projet qgis"""

    stock = dict()
    try:
        codec = hasbom(fichier, codec)
        with open(fichier, "r", encoding=codec) as fich:
            for i in fich:

                if "datasource" in i:
                    #                        dbname=''
                    #                        l_tmp = i.split('dbname=')
                    #                        if len(l_tmp) > 1:
                    #                            dbname = l_tmp[1].split(" ")
                    l_tmp = i.split("table=")
                    if len(l_tmp) > 1:

                        liste = l_tmp[1].split(" ")
                        valeur = liste[0].replace('"', "")
                        stock[valeur] = [valeur]
        if debug:
            print("chargement liste", fichier)
    except FileNotFoundError:
        print("fichier liste introuvable ", fichier)
    # print ('lus fichier qgis ',fichier,list(stock))
    return stock


def charge_liste(fichier, codec=DEFCODEC, debug=False, taille=1, positions=None):
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
        if os.path.isdir(f_interm):  # on charge toutes les listes d'un repertoire (csv et qgs)
            for i in os.listdir(f_interm):
                if clef in i:
                    LOGGER.debug("chargement liste " + i + " repertoire " + f_interm)

                    #                    print("chargement liste ", i, 'repertoire:', f_interm)
                    if os.path.splitext(i)[-1] == ".qgs":
                        stock.update(
                            _charge_liste_projet_qgs(
                                os.path.join(f_interm, i), codec=codec, debug=debug
                            )
                        )
                    elif os.path.splitext(i)[-1] == ".csv":
                        stock.update(
                            _charge_liste_csv(
                                os.path.join(f_interm, i), taille=taille, codec=codec, debug=debug
                            )
                        )
                else:
                    #                    print ('non retenu',i,clef)
                    pass
        else:
            if os.path.splitext(f_interm)[-1] == ".qgs":
                stock.update(_charge_liste_projet_qgs(f_interm, codec=codec, debug=debug))
            elif os.path.splitext(f_interm)[-1] == ".csv":
                stock.update(
                    _charge_liste_csv(
                        f_interm, taille=taille, codec=codec, debug=debug, positions=positions
                    )
                )
    #    print ('charge liste',sorted(stock))
    if not stock:  # on a rien trouve
        print("---------attention aucune liste disponible sous ", fichier)
    return stock


# def get_listeval(txt):
#    """decode une liste sous la forme {v,v,v,v}"""
#    # c est une liste directement dans le champ
#    return txt[1:-1].split(",") if txt.startswith('{') else []


def prepare_mode_in(fichier, stock_param, taille=1, clef=0):
    """precharge les fichiers utilises pour les jointures ou les listes d'appartenance
    formats acceptes:
        in:{a,b,c}                  -> liste de valeurs dans la commande
        in:#schema:nom_du_schema    -> liste des tables d'un schema
        in:nom_de_fichier           -> contenu d'un fichier
        in:[att1,att2,att3...]      -> attributs de l'objet courant
        in:(attributs)              -> noms des attributs de l'objet courant
        in:st:nom_du_stockage       -> valeurs des objets en memoire (la clef donne l'attribut)
        in:db:nom_de_la_table       -> valeur des attributs de l'objet en base (la clef donne le nom du champs)
    """
    fichier = fichier.strip()
    #    valeurs = get_listeval(fichier)
    liste_valeurs = fichier[1:-1].split(",") if fichier.startswith("{") else []
    valeurs = {i:i for i in liste_valeurs}
    #    print ('fichier a lire ',fichier,valeurs)
    if fichier.startswith("#schema"):  # liste de classes d'un schema
        mode = "in_s"
        decoupage = fichier.split(":")
        nom = ''
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
            valeurs = charge_liste(fichier, taille=taille, positions=positions)
            # on precharge le fichier de jointure
            # print ('outils: chargement liste ',fichier,'------>',
            #         '\n'.join((str(i)+':'+str(valeurs[i]) for i in valeurs)))
    return mode, valeurs


def prepare_elmap(mapping):
    """precalcule les dictionaires pour le mapping"""
    mapping_special = dict()  # mapping simplifie pour modifier les scripts de base de donnees
    for i in mapping:
        schema1, table1 = i
        schema2, table2 = mapping[i]
        mapping_special[schema1] = schema2
        mapping_special[table1] = table2
    items = sorted(mapping_special, key=lambda i: len(mapping_special[i]), reverse=True)
    intmap1 = {j: "**<<" + str(i) + ">>**" for i, j in enumerate(items)}
    intmap2 = {"**<<" + str(i) + ">>**": mapping_special[j] for i, j in enumerate(items)}
    elmap = (items, intmap1, intmap2)
    #    print ('definition intmap2', intmap2)
    return elmap

def traite_mapping(elements):
    '''decode une definition de mapping
        elements est une liste de definitions de mapping
        a ce stade une definition  se presente sous la forme suivante:
        (groupe.classe, groupe.classe,[(attribut => attribut,...)])
        ou
        (groupe,classe, groupe,classe,[(attribut => attribut,...)])
        '''
    mapping = dict()
    mapping_attributs =  dict()
    for els in elements:
        # print ("traitement els", els)
        if not els or els[0].startswith("!") or not els[0]:
            continue
        attrmap = ""
        if len(els) == 2 or len(els) == 3:
            id1 = tuple(els[0].split("."))
            id2 = tuple(els[1].split("."))
            if len(els) == 3:
                attrmap = els[2]
        #            print ('mapping',i,id1,id2)
        elif len(els) == 4 or len(els) == 5:
            id1 = (els[0], els[1])
            id2 = (els[2], els[3])
            if len(els) == 5:
                attrmap = els[4]
        else:
            print("charge_mapping :description incorrecte", len(els), els, elements[els])
            continue

        if attrmap:
            attrmap = attrmap.replace('"', "")
            attrmap = attrmap.replace("'", "")
            map_attributs = dict([re.split(" *=> *", i) for i in re.split(" *, *", attrmap)])
            mapping_attributs[id1] = map_attributs
            mapping_attributs[id2] = dict((b, a) for a, b in map_attributs.items()) #mapping inverse

        mapping[id1] = id2
        mapping[id2] = id1
    return mapping, mapping_attributs


def charge_mapping(regle, mapping=None):
    """ precharge un mapping"""

    if regle.params.cmp1.val.startswith("{"):  # c'est une definition in line
        # {groupe.classe,groupe.classe,att=>att,att=>att...:groupe.classe,groupe.classe,att=>att,...:...}
        vtmp = regle.params.cmp1.val[1:-1].split(":")
        elements = [i.split(',',2) for i in vtmp]

    elif regle.params.cmp1.val:
        regle.fichier = regle.params.cmp1.val  # nom du fichier
        fichier = expandfilename(
            regle.fichier,
            regle.stock_param.rdef,
            regle.stock_param.racine,
            regle.stock_param.chemin_courant,
            regle.stock_param.fichier_courant,
        )
        elements = charge_liste(fichier, taille=-1).values()
        # on precharge le fichier de mapping
    else:
        elements =[]

    regle.mapping, regle.mapping_attributs = traite_mapping(elements)

    if regle.params.att_sortie.val == "#schema":
        regle.schema_dest = regle.getschema(regle.params.val_entree.val)
    #        mapping_attributs
    regle.elmap = prepare_elmap(regle.mapping)
    # print ('definition mapping', '\n'.join([str(i)+':\t\t'+str(regle.mapping[i])
    #     for i in sorted(regle.mapping)]))
    # print (regle.mapping_attributs)
    #

    if not regle.mapping:
        print("h_map:mapping introuvable", regle.fichier)


def valide_auxiliaires(identifies, non_identifies):
    """ valide que les fichiers trouves sont connus"""
    auxiliaires = {a: defin[3] for a, defin in Reader.lecteurs.items()}
    for chemin, nom, extinc in non_identifies:
        if (chemin, nom) in identifies:
            extref = identifies[(chemin, nom)]
            if auxiliaires.get(extref) and extinc in auxiliaires.get(extref):
                #                    print ('connu ',chemin,nom,extinc,'->',extref)
                pass
            else:
                print("extention inconnue ", extref, "->", chemin, nom, extinc)


def scan_entree(rep=None, force_format=None, fileselect=None, filtre_entree=None, dirselect = None, debug=0):
    " etablit la liste des fichiers a lire"
    entree = rep
    parametres_fichiers = {}
    retour = []
    if debug:
        print ('scan_entree repertoire a scanner',rep)
    if not entree:
        return retour, parametres_fichiers
    #    force_format = ''
    #    liste_formats = F.LECTEURS.keys()
    liste_formats = Reader.lecteurs.keys()
    #        auxiliaires = {a:F.AUXILIAIRES.get(a) for a in F.LECTEURS}
    if debug:
        print("format entree forcee ", force_format)
    # print ('scan_entree', rep, os.path.isfile(entree))
    if os.path.isfile(entree):  # traitement un seul fichier

        fichs = [(os.path.basename(entree), "")]
        entree = os.path.dirname(entree)  # on extrait le repertoire
    elif '*' in entree:
        rep = str(os.path.dirname(entree))
        while '*' in rep:
            rep=str(os.path.dirname(rep))
        print ('repertoire de reference', rep)
        fichs = [(os.path.basename(i),str(os.path.dirname(i)).replace(rep,'')) for i in  glob.glob(entree, recursive=True)]
        entree = rep

        # print ( 'fichiers lus', fichs)
    else:
        fichs = [i for i in scandirs(entree, "", True, pattern=fileselect, dirpattern=dirselect)]

    identifies = dict()
    non_identifies = []

    if filtre_entree:
        print("filtrage entrees ", filtre_entree)
    # print ('fichs',fichs, filtre_entree)
    for fichier, chemin in fichs:
        if filtre_entree:
            if not re.search(filtre_entree, fichier):
                #                    print ('ignore ',filtre_entree,fichier)
                continue

        nom = os.path.splitext(fichier)[0].lower()
        ext = (
            force_format if force_format else str(os.path.splitext(fichier)[1]).lower().replace(".", "")
        )
        # print ('ici', nom,ext, ext in liste_formats, liste_formats)
        if ext in liste_formats:
            aux = Reader.lecteurs[ext][3]
            if '!' in aux: # attention il y a des incompatibilites
                racine = os.path.splitext(fichier)[0]
                valide = True
                for ex2 in aux:
                    if os.path.isfile(os.path.join(str(entree), str(chemin), str(racine+'.'+ex2))):
                        non_identifies.append((chemin, nom, ext))
                        valide = False
                        continue
                if not valide:
                    continue
            f_courant = os.path.join(str(entree), str(chemin), str(fichier))
            identifies[chemin, nom] = ext
            if debug:
                print("fichier a traiter", f_courant, ext)
            retour.append(f_courant)
            parametres_fichiers[f_courant] = (entree, chemin, fichier, ext)
        #                print('fichier a traiter', f_courant, fichier, ext)
        else:
            non_identifies.append((chemin, nom, ext))
    valide_auxiliaires(identifies, non_identifies)

    if debug:
        print("fichiers a traiter", fichs, retour, parametres_fichiers)
    return retour, parametres_fichiers


def remap_noms(items, intmap1, intmap2, elt):
    """ remappe un nom """
    elt2 = elt
    for tbl in items:
        elt2 = elt2.replace(tbl, intmap1[tbl])
    #        if intmap1[tbl] in elt2:
    #            print ('remplacement', elt2, tbl, intmap1[tbl])
    for code in intmap2:
        elt2 = elt2.replace(code, intmap2[code])
    #        if intmap2[code] in elt2:
    #            print ('remplacement', elt2, code, intmap2[code])
    #    print ('remap_noms',elt,'->',elt2)
    return elt2


def remap_ident(elmap, ident):
    """ remappe un identifiant """
    if isinstance(ident, tuple):
        schema, table = ident
        schema2 = remap_noms(*elmap, schema)
        table2 = remap_noms(*elmap, table)
        return (schema2, table2)
    elif isinstance(ident, str):
        return remap_noms(*elmap, ident)
    return ident


def remap(element, elmap):
    """remappe des noms de tables et de schema dans des structures"""
    #    print ('valeur elmap',elmap)
    #    raise
    if isinstance(element, dict):
        return {remap_ident(elmap, ident): remap(val, elmap) for ident, val in element.items()}
    elif isinstance(element, (list, tuple)):
        return [remap(val, elmap) for val in element]
    elif isinstance(element, str):
        return remap_noms(*elmap, element)
    return element
