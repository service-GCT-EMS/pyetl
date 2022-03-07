# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:20:44 2015

@author: Claude unger

traducteur de commandes pour la definition de regles

"""
import os
import re

# import sys
import logging
from pyetl.schema.schema_interne import get_attribut
from pyetl.formats.mdbaccess import recup_table_parametres
from .fonctions.outils import charge_fichier

LOGGER = logging.getLogger(__name__)
PARAM_EXP = re.compile("(%#?[a-zA-Z0-9_]+(?:#[a-zA-Z0-9_]+)?%)")

# quelques fonction générales
def fdebug(regle, obj):
    """gestion des affichages de debug"""
    #    print('dans debug', regle, obj)
    regle.debugvalid = regle.debug and obj
    if regle.debugvalid:
        cond = regle.getvar("debug_cond")
        if "=" in cond:
            att, val = cond.split("=", 1)
            regle.debugvalid = obj.attributs.get(att) == val

        regle.stock_param.gestion_log.setdebug()
        wid = regle.getvar("_wid")
        debugmode = regle.v_nommees["debug"]

        if debugmode == "print":
            regle.affiche_debug(wid + "------affiche------>")
            obj.debug("", attlist=regle.champsdebug)
            regle.debugvalid = False
            return regle.f_init(regle, obj)
        if debugmode == "step":
            regle.affiche_debug(wid + "------step------>")
            succes = regle.f_init(regle, obj)
            redirect = obj.redirect if obj.redirect else "ok"
            suite = redirect if succes else "fail"
            regle2 = regle.branchements.brch[suite]
            if regle2.v_nommees["debug"] != "end":
                regle2.v_nommees["debug"] = "step"
            regle2.debug = 1
        else:
            regle.affiche_debug(wid + "------debug------>")
            obj.debug("avant", attlist=regle.champsdebug)

        succes = regle.f_init(regle, obj)
        regle.debug = regle.debug - 1
        liens_num = regle.branchements.liens_num()
        redirect = obj.redirect if obj.redirect else "ok"
        #        if obj.redirect and obj.redirect not in regle.branchements.brch:
        #            redirect = 'ok'
        #            print ('branchement orphelin', obj.redirect, '(',regle.branchements.brch.keys())
        print(
            "retour fonction ",
            succes,
            "->",
            redirect if succes else "fail",
            liens_num[redirect] if succes else liens_num["fail"],
            regle.branchements.brch[redirect]
            if succes
            else regle.branchements.brch["fail"],
        )
        if regle.copy:
            print("copy :  ->", liens_num["copy"], regle.branchements.brch["copy"])

    else:
        #        print('debug: non affichage ', regle, obj)
        succes = regle.f_init(regle, obj)
    return succes


def regles_liees(regle, liaison, prec, refs):
    """ decode le systeme de regles liees """
    nivprec = prec.niveau if prec else 0
    nivref = refs[-1].niveau if refs else 0
    if liaison and liaison[0] in "|+-":  # mode de regles liees
        regle.niveau = 0

        while regle.niveau < len(liaison) and liaison[regle.niveau] in "|+-":
            regle.niveau += 1
        if liaison[regle.niveau - 1] == "-":
            regle.nonext = True
        for i in regle.branchements.enchainements:
            if isinstance(i, str):
                cmp = i
                if liaison[regle.niveau : regle.niveau + len(cmp)] == cmp:
                    regle.enchainement = i
                    regle.code_classe = liaison[regle.niveau + len(cmp) + 1 :]
        if regle.enchainement == "":
            regle.enchainement = "ok"
            # petite magouille pour coller aux branchements sans alourdir la syntaxe
        if not regle.enchainement:
            err = "erreur de syntaxe " + regle.ligne[:-1]
            print("liaison:", err)
            print("autorises", regle.branchements.enchainements)
            print("trouve", liaison)
            raise SyntaxError("liaison non valide")
        debug = 0
        if regle.getvar("debug") == "1" or regle.debug:
            debug = 1
            print(
                "     regle liee",
                regle.enchainement,
                liaison[regle.niveau :],
                regle.niveau,
            )
        # la on determine si la regle est statiquement selectable
        prec = None
        if refs:
            if len(refs) < regle.niveau:
                print("erreur d imbrication", regle)
                return
            prec = refs[regle.niveau - 1]
        if prec:
            if debug:
                print(
                    "    etat prec",
                    prec.valide,
                    prec.selstd,
                    regle.enchainement,
                    "valide avant:",
                    regle.valide,
                )
            if prec.valide == "unselected":
                if regle.enchainement == "ok":
                    regle.valide = "skip"
                    return
                if regle.enchainement == "sinon":
                    regle.valide = "selected"
                    return
            if prec.selstd == None or prec.valide == "selected":  # toujours valide
                if regle.enchainement == "sinon":
                    regle.valide = "skip"
                    return
                if regle.enchainement == "ok":
                    regle.valide = "selected"
                    return
        return None


# ---------------------------fonctions standard--------------------------------


def description_schema(regle):
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
    type_att_sortie = regle.params.att_sortie.typedef
    position = -1
    valeur_defaut = ""
    def_index = ""
    desc_schema = regle.params.att_sortie.definition
    # print("desc schema1", type(regle.params.att_sortie), desc_schema, type_att_sortie)
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
    modele = get_attribut("modele", 30)
    modele.nom_court = ""
    modele.type_att = type_att_sortie.upper()
    modele.type_att_base = modele.type_att
    modele.defaut = valeur_defaut
    modele.ordre = position
    modele.def_index = def_index
    regle.params.def_sortie = modele


def extraction_operation(regle, fonction):
    """ isole le code operation de tous les modificateurs """
    # fonction avec les modificateurs de comportement
    # + : dupplique l'objet  un passe la regle l'autre pas
    # - : mange les objets qui ne passent pas la regle
    # > : sortie des objets passant la regle
    regle.copy = "+" in fonction
    regle.filter = "-" in fonction
    regle.final = ">" in fonction
    regle.supobj = regle.final
    mode = fonction.strip('+-> "')
    regle.mode = mode
    if regle.copy:
        regle.branchements.addsortie("copy")  # on gagne une sortie


def printpattern(commande):
    """affiche la descriprion de la commande (debug)"""
    print("commande ", commande.nom)
    for variante in commande.subfonctions:
        print(
            "sf:   %-10s->%s<- %s,(%s)"
            % (
                variante.nom,
                variante.pattern,
                variante.description.get("#aide"),
                variante.clef_sec,
            )
        )


def printelements(elements):
    """affiche les elements detectes par les expressions regulieres (debug)"""
    print("int: parametres detectes")
    #    print (elements)
    for i in elements:
        #        print(i,elements[i])
        print("->", i, elements[i].groups(), elements[i].re)


def setvloc(regle):
    """positionne les variables locales declarees dans la regle"""
    valeurs = regle.context.SPLITTER_PV.split(regle.ligne)
    if len(valeurs) > 11:
        listevlocs = regle.context.SPLITTER_V.split(valeurs[11])
        regle.context.affecte(listevlocs)

    # print("decodage v nommees", valeurs)
    for n, v in enumerate(valeurs):
        valeurs[n], _ = regle.context.resolve(v)
    # print("apres resolve v nommees", valeurs)

    if len(valeurs) <= 11:
        valeurs.extend([""] * (12 - len(valeurs)))
    if not any(valeurs):
        regle.valide = "vide"
    regle.v_nommees = dict(zip(regle.NOMS_CHAMPS, valeurs))
    # print("apres decodage v nommees", regle.v_nommees)


def ajuste_contexte(regle, prec):
    """ grer les contextes entre les regles liees"""
    return
    ajuste = regle.niveau != prec.niveau
    if ajuste:
        print("avant ajuste_context", regle.niveau, prec.niveau, regle, prec)

    if regle.niveau > prec.niveau:
        cprec = regle.stock_param.pushcontext(prec.context)
        regle.context.setparent(cprec, ref=False)
    if regle.niveau < prec.niveau:
        context = None
        for i in range(prec.niveau - regle.niveau):
            context = regle.stock_param.popcontext()
        regle.context.setparent(context, ref=False)

    if ajuste:
        print("apres ajuste_context", regle.context)


def prepare_regle(regle, prec=None, refs=None):
    """positionne les elements standard de la regle
    decodage des liens entre regles (structure de blocs)
    premier parametre : contient les elements de structure
            de la forme [|+-][sinon|fail]:[element de condition]
    """
    # print("vnommees1", regle.v_nommees)
    setvloc(regle)
    v_nommees = regle.v_nommees
    # print("vnommees2", regle.v_nommees)
    ndebug = 10

    if any(i in v_nommees["debug"] for i in ("debug", "print", "step")):
        vdebug = v_nommees["debug"].split(",")
        if vdebug[-1].strip().isnumeric():
            ndebug = vdebug.pop()
        regle.debug = int(ndebug)
        if len(vdebug) > 1:
            regle.champsdebug = vdebug[1:]
        print("debug regle ::::", regle.ligne)

    if not regle.runscope():
        regle.valide = "out_of_scope"
        regle.selected = False
        if regle.debug:
            print("regle non eligible ->", regle.getvar("process"))
        return regle.valide

    regle.code_classe = v_nommees["sel1"]
    # print ('interpreteur: ',regle,'->',regle.v_nommees)

    fonction = v_nommees["commande"]
    if fonction:
        regles_liees(regle, v_nommees["sel1"], prec, refs)
        # print ("avant ajuste",prec.niveau if prec else None,regle.niveau,regle)
        # refs[regle.niveau] = regle
        if regle.valide == "skip":
            if regle.debug:
                print("     mode statique : skip", regle)
                print("     refs", refs)
            return regle.valide
        prec = refs[regle.niveau - 1] if len(refs) > regle.niveau else None
        if prec:
            ajuste_contexte(regle, prec)
        if len(refs) > regle.niveau:
            refs[regle.niveau] = regle
        else:
            refs.append(regle)
        if regle.code_classe[:3] == "db:":  # mode d'acces a la base de donnees
            regle.selstd = None
            regle.valide = True
        #        print ("interp: acces base de donnees",regle.code_classe,regle.mode,regle)
        else:
            # print("appelle prepare")
            regle.prepare_condition(v_nommees)
            regle.selected = True
            if regle.valide == "unselected":
                # regle non selectionnable en mode statique
                if regle.debug:
                    print("     mode statique : unselected", regle)
                regle.selected = False
                return regle.valide

            regle.code_classe = regle.code_classe.split(":")[-1]
            # on nettoie d'eventuels tests
        #    regle.valide = "vide"
        extraction_operation(regle, fonction)
        regle.identifie_operation()
        if regle.valide:
            description_schema(
                regle
            )  # mets en place le schema pour l'attribut de sortie

    else:
        #            if re.match('^( *;*)*$',regle.ligne):
        if regle.valide != "vide":
            print(
                regle.stock_param.nompyetl,
                regle.stock_param.idpyetl,
                regle.valide,
                "------>regle sans fonction",
                regle.numero,
            )
            morceaux = regle.context.SPLITTER_PV.split(regle.ligne.replace("\n", ""))
            if len(morceaux) < 8:
                morceaux = morceaux + [""] * 8
            morceaux[7] = "???"
            print(regle)
            print("                ------>", ";".join(morceaux))
            #            print('decodage champs', ' '.join([i+'->'+j for i, j in regle.v_nommees.items()]))
            raise SyntaxError("regle sans fonction")
    return regle.valide


def reinterprete_regle(regle, mapper, context=None):
    """ reinterprete les variables d'une regle pour la mise a jour"""
    # TODO gerer correctement ce truc
    prepare_regle(regle)


def interprete_ligne_csv(
    mapper, ligne, fichier, numero, prec=None, regle_ref=None, macrodef=None
):
    """decode une ligne du fichier cs v de regles
    et la stocke en structure interne"""
    refs = regle_ref.refs if regle_ref else mapper.refs
    # print('traitement_ligne', ligne, mapper.context)
    # regle = RegleTraitement(ligne, mapper, fichier, numero)
    # print ('context creation1',regle.context)
    regle = mapper.regleref.getregle(ligne, fichier, numero)
    if macrodef:
        regle.setlocal("_commande", macrodef)
    # print("creation regle", regle, ligne)
    prepare_regle(regle, prec, refs)
    # print("retour prepare", regle.valide, regle)

    if not regle.valide:
        return None

    if regle.debug or regle.istrue("debug"):
        msg = regle.v_nommees["debug"]
        if "print" in regle.v_nommees["debug"]:
            print("---------" + msg + " ligne--->", regle.numero, regle.ligne)
        regle.f_init = regle.fonc
        regle.fonc = fdebug

    if regle.valide == "done":
        # print ('done', regle)
        # c'est une regle qui n'a pas de consequences sur les objets
        mapper.done = True  # on a fait qque chose
        return None
    if regle.valide != True:
        #        print('regle vide ',regle)
        return None
    return regle


def decoupe_liste_commandes(fichier_regles):
    """ gere les cas ou la liste de commandes est un assemblage complexe de macros"""
    fichier_regles = fichier_regles.strip()
    if fichier_regles.startswith("[") and fichier_regles.endswith("]"):
        fichier_regles = fichier_regles[1:-1]
    if fichier_regles.startswith("'") and fichier_regles.endswith("'"):
        fichier_regles = fichier_regles[1:-1]
    fichier_regles = fichier_regles.strip()
    if "'," in fichier_regles or ",'" in fichier_regles:
        liste_commandes = re.split("' *, *'", fichier_regles)
    elif fichier_regles.startswith("#"):
        liste_commandes = fichier_regles.split(",#")
        for i in range(1, len(liste_commandes)):
            liste_commandes[i] = "#" + liste_commandes[i]
    elif fichier_regles.startswith("-"):
        liste_commandes = fichier_regles.split(",-")
        for i in range(1, len(liste_commandes)):
            liste_commandes[i] = (
                liste_commandes[i]
                if liste_commandes[i].startswith("#")
                else "#" + liste_commandes[i]
            )
    else:
        liste_commandes = fichier_regles.split(",")
    # print(
    #     "decoupage_macros",
    #     fichier_regles,
    #     "->",
    #     [(n, "<" + i) for n, i in enumerate(liste_commandes)],
    # )

    return [(n, "##" + i) for n, i in enumerate(liste_commandes)]


def prepare_acces_base_scripts(regle):
    """ initialise les acces a la base de scripts"""
    mapper = regle.stock_param
    if mapper.load_paramgroup("dbscriptmode"):
        serv = mapper.getvar("scriptserver")
        LOGGER.info("lecture commande en base " + serv)
        #    print('lire_db: chargement ', serv)
        mapper.load_paramgroup(serv, nom=serv)
        #        print ('parametres',mapper.parms)
        #        base = mapper.getvar('base_'+serv)
        nomschema = regle.getvar("scriptschema")
        return (serv, nomschema)
    else:
        LOGGER.error("base de script non definie ")
        raise SyntaxError("base de script non definie ")


def get_macro_from_db(regle, nom_inclus):
    """ lit une macro en base """
    acces = prepare_acces_base_scripts(regle)
    if acces:
        serv, nomschema = acces
        nomtable = regle.getvar("commandtable")
        description = recup_table_parametres(
            regle, serv, nomschema, nomtable, clef="nom", valeur=nom_inclus
        )
        regles = recup_table_parametres(
            regle, serv, nomschema, nomtable, clef="nom", valeur=nom_inclus
        )
        regle.stock_param.stocke_macro(description, "database")


def lire_commandes_en_base(mapper, fichier_regles):
    """ lit les commandes en base de donnees"""
    defs = mapper.context.SPLITTER_2P.split(fichier_regles)
    if len(defs) != 2:
        print(
            "erreur commande en base de donnees la commande doit"
            "avoir le format suivant  #db:nom"
        )
        raise SyntaxError("erreur script en base: " + fichier_regles)
    nom = defs[1]
    acces = prepare_acces_base_scripts(mapper.regleref)
    if not acces:
        raise SyntaxError("base scripts non accessible")
    serv, nomschema = acces
    mapper.load_paramgroup("dbscriptmode")
    serv = mapper.getvar("scriptserver")
    if not serv:
        raise SyntaxError("base de scripts non definie")
    nomschema = mapper.getvar("scriptschema")
    LOGGER.info("lecture commande en base " + serv)
    #    print('lire_db: chargement ', serv)
    mapper.load_paramgroup(serv, nom=serv)
    #        print ('parametres',mapper.parms)
    # type_base = mapper.getvar("db_" + serv)
    #        base = mapper.getvar('base_'+serv)
    type_base = None
    commandtable = mapper.getvar("commandtable")
    print(
        "lecture de regles en base",
        serv,
        type_base,
        nomschema + "." + commandtable,
        "->",
        nom,
    )
    regle = mapper.regleref

    regles = recup_table_parametres(
        regle,
        serv,
        nomschema,
        commandtable,
        clef="nom",
        valeur=nom,
        ordre="ordre",
        type_base=type_base,
    )

    liste_regles = [
        (v[3], ";".join([str(i) if i is not None else "" for i in v[4:]]))
        for v in regles
    ]

    print("regles lues en base:", serv, nom, "\n".join([str(i) for i in liste_regles]))

    return liste_regles


def _lire_commandes(mapper, fichier_regles, niveau):
    """lit les commandes quelle que soit l'origine base de donnees fichier ou macro"""
    #    print(" lecture",fichier_regles)
    if fichier_regles.startswith("#db:"):  # acces a des commandes en base de donnees
        liste_regles = lire_commandes_en_base(mapper, fichier_regles)

    elif (
        fichier_regles.startswith("#")
        or fichier_regles.startswith("['")
        or fichier_regles.startswith("-")
    ):
        #       assemblage complexe de macros
        #        print ('a lire', fichier_regles)
        liste_regles = decoupe_liste_commandes(fichier_regles)
    #        print ('lu', '\n   '.join([str(i) for i in liste_regles]))
    else:
        liste_regles = charge_fichier(
            fichier_regles, "", defext=".csv", codec=mapper.getvar("codec_csv")
        )

    #    print ('lu:',liste_regles)
    return liste_regles


def affecte_variable(mapper, commande, context, regle_ref):
    """ affecte une variable avec gestion des valeurs par defaut"""
    niveau, texte, rvirt = getlevel(mapper, commande, regle_ref)
    commande_orig = texte[1:]

    liste_vals = context.SPLITTER_PV.split(commande)
    commande = liste_vals[0][1:].strip()
    if not "=" in commande:
        commande = commande + "=True"
    nom, valeur, binding, nolocal = context.traite_egalite(commande)
    if not valeur:
        for i in liste_vals[1:]:
            if not i:
                break
            valeur, binding = context.resolve(i)
            if valeur:
                break

    if not nom:
        raise SyntaxError(
            "affectation impossible " + commande_orig + "->" + repr(commande)
        )
    setter = context.setvar
    if nom.startswith("$"):  # $$X variable globale
        nom = nom[1:]
        setter = context.setroot
    elif nom.startswith("-"):  # $-X variable locale
        nom = nom[1:]
        setter = context.setlocal
    elif nom.startswith("*"):  # $*X variable retour
        nom = nom[1:]
        setter = context.setretour
    elif nom.startswith("!"):  # $!X variable retour environnement
        nom = nom[1:]
        setter = context.setretour_env

    setter(nom, valeur)
    if nom in mapper.variables_speciales:
        setter = context.setroot
        setter(nom, valeur)
        mapper.traite_variables_speciales(nom)
    # print("affectation variable", commande, setter, nom, "=", valeur)


def prepare_texte(defligne, niveau):
    """ prepare le texte pour l 'interpretation et verifie s 'il y a des choses a faire """
    numero, texte_brut = defligne
    #        texte_brut = texte
    texte = texte_brut.strip()
    if not texte or texte.startswith("!") or texte.startswith('"!'):
        return None, None, texte_brut
    if texte.startswith('"'):
        # on a mis des cotes dans les champs : petite touille pour nettoyer
        tmp = texte.replace('""', "&&trucmuch&&")  # on sauve les doubles cotes
        tmp = tmp.replace('"', "")
        texte = tmp.replace("&&trucmuch&&", '"')
    if not niveau:
        return numero, texte, texte_brut
    if re.match(r"^[\+\-\|]", texte):
        return numero, niveau + texte, texte_brut
    return numero, niveau + ":" + texte, texte_brut


def traite_regle_std(
    mapper,
    numero,
    texte,
    texte_brut,
    fichier_regles,
    bloc,
    regle_ref=None,
    macrodef=None,
):
    """ traite une regle classique """
    #    texte = texte_brut.strip()
    erreurs = 0
    regles = mapper.regles if regle_ref is None else regle_ref.liste_regles
    precedent = regles[-1] if regles else None
    try:
        r_cour = interprete_ligne_csv(
            mapper,
            texte,
            fichier_regles,
            numero,
            prec=precedent,
            regle_ref=regle_ref,
            macrodef=macrodef,
        )
    except SyntaxError:
        # print("syntaxerror ", texte_brut)
        return bloc, 1
    #        raise
    #            print ('icsv:traitement ligne ',i[:-1], r_cour)
    #            print ('retour',r_cour)
    # print("interp regle", texte, erreurs, r_cour)
    if r_cour is None:
        return bloc, 0
    if r_cour.valide:
        r_cour.texte_brut = texte_brut
        r_cour.bloc = bloc
        bloc += r_cour.ebloc  # gestion des blocs
        if bloc < 0:
            print("erreur structure de blocs", bloc, numero, texte)
            erreurs = 1
            return 0, bloc
        position = len(regles)
        r_cour.bloc = bloc
        if regles:  # contextes dans le systeme de blocs
            prec = regles[-1]
            if r_cour.ebloc == 1:
                mapper.pushcontext(
                    r_cour.context, type_c="B"
                )  # devient le contexte de reference
                # print ("bloc",r_cour.ebloc,r_cour.context)
            elif r_cour.ebloc == -1:
                mapper.popcontext(typecheck="B", orig="traite_regle_std")  # on depile
            if prec.bloc:
                # print ("bloc",r_cour.ebloc,r_cour.context)
                r_cour.context.setref(mapper.cur_context)

        regles.append(r_cour)
        # for i in binding:  # enregistre les regles dynamiques
        #     mapper.bindings.setdefault(texte, []).append(r_cour)
        if position:
            regles[position - 1].branchements.suivante = r_cour
        r_cour.suivante = None
        r_cour.index = position
        # print("regle:", r_cour)
    #                print ('regle valide ', r_cour.ligne, r_cour.val_entree, r_cour.valide)
    else:
        # print("interp: regle invalide -------------->", r_cour)
        LOGGER.error("regle invalide :%s", str(r_cour.erreurs))
        if not r_cour.erreurs:
            # print("\t", r_cour.erreurs)
            print(
                "decodage champs",
                " ".join([i + "->" + j for i, j in r_cour.v_nommees.items()]),
            )
        erreurs = 1
    return bloc, erreurs


def get_macro(mapper, nom_inclus, parametres):
    """inclut une macro en la lisant en base si necessaire"""
    if nom_inclus.startswith("-"):
        nom_inclus = nom_inclus[1:]
        if not nom_inclus.startswith("#"):
            nom_inclus = "#" + nom_inclus
    while nom_inclus.startswith("##"):
        nom_inclus = nom_inclus[1:]

    if nom_inclus.startswith("#db:"):
        get_macro_from_db(mapper.regle_ref, nom_inclus)  # on mets en cache
        nom_inclus = nom_inclus[4:]
    macro = mapper.getmacro(nom_inclus)
    # macro = mapper.macros.get(nom_inclus)
    context = mapper.cur_context
    if macro:
        context = mapper.pushcontext(macro.bind(parametres, context))
    return macro, context


def prepare_env(mapper, texte: str, fichier_regles):
    """prepare une macro ou un chargement de fichier et son environnement (positionne les variables)"""
    # print ('mapping parametres macro', texte)
    context = mapper.cur_context
    champs = context.SPLITTER_PV.split(texte)
    nom_inclus = champs[0].strip()
    parametres = champs[1:]
    # print("prepare_env", nom_inclus, parametres)
    listevlocs = []
    if len(parametres) > 10:
        parametres = parametres[:10]
        listevlocs = context.SPLITTER_V.split(champs[11])

    cmd, *pars = (
        context.SPLITTER_B.split(nom_inclus)
        if context.SPLITTER_B.search(nom_inclus)
        else context.SPLITTER_2P.split(nom_inclus)
    )
    nom_inclus = cmd
    if pars:
        parametres = pars + parametres
    nom_inclus, _ = context.resolve(nom_inclus)
    macro = None
    if nom_inclus.startswith("#") or nom_inclus.startswith("-"):
        # print("getmacro", nom_inclus, parametres)
        macro, context = get_macro(mapper, nom_inclus, parametres)
    else:
        context.affecte(parametres)
        if not (nom_inclus.startswith(".") or os.path.abspath(nom_inclus)):
            nom_inclus = os.path.join(os.path.dirname(fichier_regles), nom_inclus)
    #            print("lecture de regles incluses", inclus,pps)
    context.affecte(listevlocs)
    # print(
    #     "prepare_env",
    #     macro.nom,
    #     nom_inclus,
    #     context,
    #     context.vlocales,
    #     parametres,
    #     listevlocs,
    # )
    return nom_inclus, context, macro


def getlevel(mapper, texte_brut, regle_ref):
    """recupere le niveau d une commande et gere les contextes"""
    match = re.match(r"(([\|\+\-]+)([a-z]*):)?((<?)(.*))", texte_brut)
    niveau = (match.group(2) if match.group(2) else "") + (
        "+" if match.group(3) else ""
    )
    texte = match.group(4)
    if match.group(5) and match.group(3):
        # appel de macro dans un sinon ou autre_branchement
        rvirt = (niveau[:-1] + match.group(3) + ":") + ";;;;;;;pass;;;;;rv"
        # print("on ajoute une regle virtuelle pour ajuster les niveaux", rvirt)
        traite_regle_std(mapper, 0, rvirt, rvirt, "", 0, regle_ref=regle_ref)
    if regle_ref:
        prec = regle_ref.liste_regles[-1] if regle_ref.liste_regles else None
    else:
        prec = mapper.regles[-1] if mapper.regles else None
    nivelem = len(niveau)
    rvirt = ""
    if prec:
        if nivelem != prec.niveau:
            rvirt = (niveau + ":" if niveau else "") + ";;;;;;;pass;;;;;rv"
            # print("on ajoute une regle virtuelle pour ajuster les niveaux", rvirt)
            traite_regle_std(mapper, 0, rvirt, rvirt, "", 0, regle_ref=regle_ref)
    # print(
    #     "getlevel:",
    #     niveau,
    #     texte_brut,
    #     match.group(1),
    #     match.group(2),
    #     match.group(3),
    #     match.group(4),
    #     match.group(5),
    # )
    return niveau, texte, rvirt


def importe_macro(mapper, texte, context, fichier_regles, regle_ref=None):
    """ importe une macro et l 'interprete"""
    # niveau, texte, rvirt = getlevel(mapper, texte_brut, regle_ref)
    # on cree un contexte avec ses propres valeurs locales
    inclus, macroenv, macro = prepare_env(mapper, texte, fichier_regles)
    debug = macroenv.istrue("debug")
    if debug:
        print("importe_macro", texte, "contexte", mapper.cur_context)
        print(
            "debug macro:",
            macroenv,
            texte,
            "->",
            inclus,
            sorted(macroenv.vlocales.items()),
        )
    if macro:
        # mapper.pushcontext(type_c="M")
        # print("contexte macros :", mapper.cur_context)
        liste_regles = macro.get_commands(add_return=bool(regle_ref))
        erreurs = lire_regles_csv(
            mapper,
            "",
            liste_regles=liste_regles,
            regle_ref=regle_ref,
        )
        if erreurs:
            LOGGER.error("erreur initialisation macro %s : %s", macro.nom, str(erreurs))
            erreurs = -999
            # print("=======================erreurs initialisation macro", macro.nom)
        # if debug:
        #     texte_fin = ";;;;;;;return;;;debug;;retour macro"
        # else:
        #     texte_fin = ";;;;;;;return;;;;;retour macro"
        # traite_regle_std(mapper, 0, texte_fin, texte_fin, "", 0, regle_ref=regle_ref)
        if debug:
            print("contexte macros apres:", mapper.cur_context)
        mapper.popcontext(
            typecheck="M", orig="importe_macro", context=macroenv
        )  # on depile un contexte
        # print("contexte macros apres pop:", mapper.cur_context)

    else:
        LOGGER.error("macro introuvable %s", texte)
        # print("================================macro introuvable", texte)
        erreurs = 1
    return erreurs

    # fichier inclus


def initmacro(mapper, texte, fichier_regles):
    """ initialise le stockage """
    champs_macro = mapper.context.SPLITTER_PV.split(texte)
    nom = champs_macro[1]
    vposmacro = [i for i in champs_macro[2:] if i]
    macro = mapper.macrostore.regmacro(nom, file=fichier_regles, vpos=vposmacro)
    # print('enregistrement macro',mapper.idpyetl,nom)
    return macro


def lire_regles_csv(
    mapper, fichier_regles, numero_ext=0, liste_regles=None, niveau="", regle_ref=None
):
    """ lecture des fichiers de regles """
    erreurs = 0
    #    mstore = False
    autonum = 0
    macro = None
    if liste_regles is None:
        liste_regles = []
    else:
        liste_regles = liste_regles
    numero = numero_ext
    # if regle_ref:
    #     print('regle_ref:',regle_ref)
    # print("dans lire_regles", fichier_regles, liste_regles)
    if fichier_regles:
        liste_regles = _lire_commandes(mapper, fichier_regles, niveau)
    #    if niveau:
    # print("regles lues:\n" + "\n".join((str(i) for i in liste_regles)))
    # if regle_ref:
    #     raise
    bloc = 0
    for defligne in liste_regles[:]:
        #        numero, texte = defligne
        numero, texte, texte_brut = prepare_texte(defligne, niveau)
        context = mapper.cur_context
        # print("context lecture", context)
        if texte is None:
            continue
        # lignes conditionelles (lignes incluses dans le code seulement si la condition est vraie)
        # sous la forme K:variable:valeur ou K:variable
        start = 0
        while re.match(r"(([\|\+-]+)[a-z_]*:)?(K:)", texte) and not macro:
            # while texte.startswith("K:") and not macro:
            pmatch = re.match(r"(([\|\+-]+)[a-z_]*:)?(K:.*)", texte)
            t2 = pmatch.group(3)
            texte = t2
            liste_val = t2.split(";", 1)
            cond, _ = context.resolve(liste_val[0])
            condmatch = re.match("K:(.*?)=(.*)", cond) or re.match("K:(.*)", cond)
            # print("lire: condmatch", condmatch, cond, liste_val[0])
            if condmatch:  # interpretation conditionelle
                #                print( "lire: trouve condmatch",condmatch.groups(), liste_val[0])
                texte = liste_val[1]
                if condmatch.group(1) == "":
                    texte = ""
                if condmatch.lastindex == 2 and condmatch.group(1) != condmatch.group(
                    2
                ):
                    texte = ""

            start += 1

        if texte and start:
            defligne = (
                defligne[0],
                mapper.context.SPLITTER_PV.split(texte_brut, start)[1],
            )
            #        liste_val[0] = ''
            #        liste_val[1] = ''
            numero, texte, texte_brut = prepare_texte(defligne, niveau)
        #            print('traitement_ligne', texte)
        if not texte:
            continue
        # enregistrement d'une macro
        # print ('traitement regle', texte_brut)

        if texte.startswith("&&#define"):
            macro = initmacro(mapper, texte, fichier_regles)
            continue

        elif texte.startswith("&&#end"):
            if not macro:  # cas particulier on est dans un schema de
                #                           scripts multiples enchaines: on transforme les autres en macros locales
                autonum += 1
                nom = "#autochain_" + str(autonum)
                texte = ";;;;;" + nom + ";;;batch;;"
                macro = mapper.macrostore.regmacro(nom, file=fichier_regles)
            else:
                macro.close()
                macro = None
                continue
        elif macro:
            # print("stockage macro", macro.nom, texte, numero)
            macro.add_command(texte, numero)
            continue

        #        print ('icsv: regle ',i)

        elif texte.startswith("$#"):
            ligne, _ = context.resolve(texte)
            # print('$# resolve ',context ,texte,'->', ligne, context.getvar('acces'))
            champs_var = ligne.split(";") + [""] * 3
            vgroup = champs_var[0][2:].strip()
            ngroup = champs_var[1].strip() if champs_var[1].strip() else vgroup
            check = champs_var[2].strip()
            # verif si le groupe n'a pas ete defini d'une autre facon
            #            print ("avt chargement groupe", vgroup, champs_var)
            if vgroup.startswith("#"):
                pass  # c est un selecteur on ne le traite pas
            else:
                try:
                    mapper.load_paramgroup(vgroup, nom=ngroup, check=check)
                except KeyError:
                    print("====groupe de parametres inconnu", vgroup)
                    erreurs += 1
                    return erreurs
            # genere des variables internes de la forme 'nomDefiniDansLeFichier_nomDuGroupe
            # print("apres chargement groupe", vgroup, ngroup)
            # print("variables", mapper.context.vlocales)

        # elif texte.startswith("$"):
        elif re.match(r"(([\|\+-]+)[a-z_]*:)?\$", texte):
            affecte_variable(mapper, texte, context, regle_ref=regle_ref)
        elif texte.startswith("<<"):  # execution immediate d'une macro
            print("=============interp:avant execution, contexte:", context)
            entree = None if context.istrue("entree") else ""
            mapper.macrorunner(texte[2:], entree=entree)
            print("=============interp:retour macro")
        elif re.match(r"(([\|\+-]+)[a-z_]*:)?<(.*)", texte):
            # print("avant macro", texte, context, context.getvar("atts"))
            # on transforme ca en appel call
            # ligne,_ = context.resolve(texte)
            match = re.match(r"(([\|\+-]+)[a-z_]*:)?<(.*)", texte)
            macrodef = match.group(3)
            level = match.group(1)
            if level is None:
                level = ""
            rtext = level + ";;;;;;;call;;"
            traite_regle_std(
                mapper,
                numero,
                rtext,
                rtext,
                fichier_regles,
                bloc,
                regle_ref=regle_ref,
                macrodef=macrodef,
            )
        elif re.match(r"^##(.*)", texte):
            errs = importe_macro(
                mapper, texte[2:], context, fichier_regles, regle_ref=regle_ref
            )
            if errs:
                LOGGER.error("erreur chargement macro %s", texte)
                # print("====erreur chargement macro", texte, errs)
                erreurs += errs
                return erreurs
        else:
            #            print('regles std', defligne)
            bloc, errs = traite_regle_std(
                mapper,
                numero,
                texte,
                texte_brut,
                fichier_regles,
                bloc,
                regle_ref=regle_ref,
            )
            if errs:
                # LOGGER.error("erreur interpretation des regles : arret du traitement")
                # print("====erreur traite_regles_std")
                LOGGER.error("erreur traite_regles_std %s", texte)
                erreurs += errs
    #            print('apres,regles std', defligne, errs)

    if bloc != 0:
        erreurs += 1
        print("erreur structure de blocs", bloc)
    mapper.debug = int(mapper.getvar("debug", 0))
    if mapper.debug:
        print("niveau debug :", mapper.getvar("debug"))
        # on initialise les parametres pour finir #print 'parametres ', i
        print("fin lecture regles", erreurs, "erreurs")
    return erreurs
