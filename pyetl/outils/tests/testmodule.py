# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 17:06:28 2017

@author: 89965
testmodule : automatisation des tests
"""
import os
import re
import io
from contextlib import redirect_stdout
from pyetl.moteur.fonctions.outils import printexception


RETESTOK = {
    "A": ["A", "#A", "a", "#a_1", "#aa_C_2", "#aa_C_2(1:E,P,C)"],
    "+A": ["+A", "+#A", "+a", "+#a_1", "+#aa_C_2", "+#aa_C_2(1:E,P,C)"],
}


RETESTFAIL = {
    "A": ["1A", "#1", "11", "1_1", "=)", "#aa_C_2(1:E,P,C", "A-A", ""],
    "+A": ["+1A", "+#1", "+11", "1_1", "=)", "#aa_C_2(1:E,P,C", "A", "+"],
}


def retest(mapper):
    """verifie la description des expressions regulieres"""
    # test expressions regulieres
    #    commande_test = next(iter(mapper.commandes.values()))
    erreurs = 0
    commande_test = None
    for commande_test in mapper.commandes:
        if mapper.getcommande(commande_test):
            break
    # print("retest commande a tester", commande_test)
    commande_test = mapper.getcommande(commande_test)
    relist = commande_test.subfonctions[0].definition["entree"].relist
    nbtests = 0
    for i in relist:
        if i in RETESTOK:
            for j in RETESTOK[i]:
                #                print ('test',relist[i][0],j)
                match = re.match(relist[i][0], j)
                nbtests += 1
                if not match:
                    erreurs += 1
                    print("retest", i, j, "ko----> devrait matcher")
        #
        if i in RETESTFAIL:
            for j in RETESTFAIL[i]:
                #                print ('test',relist[i][0],j)
                match = re.match(relist[i][0], j)
                nbtests += 1
                if match:
                    erreurs += 1
                    print("retest", i, j, "ko----> ne devrait pas matcher")
    # print("test regex achevé avec", erreurs, "erreurs")
    return nbtests, erreurs


def testrunner(mapper, idtest, liste_regles, debug, redirect=False):
    """execute un test standardise"""
    nom_fonc, nom_subfonc, nom_test = idtest
    try:
        map2 = mapper.getpyetl(liste_regles, nom=nom_fonc)
        #        print ("creation",map2.nompyetl)
        if map2 is None:
            print(
                "unittest: erreur creation environnement ",
                nom_fonc,
                nom_subfonc,
                nom_test,
            )
            return ""
        if debug and int(debug):
            map2.setvar("debug", "1")
        if redirect:
            capture = io.StringIO()
            with redirect_stdout(capture):
                map2.process()
            retour = capture.getvalue()
            # print("mode redirect actif ->", retour, "<-")
        else:
            map2.process()
            retour = map2.retour
            retour = retour[0] if retour else ""
    #            print ("mode redirect inactif ->",retour,"<-")

    #    except:
    except Exception as exc:
        print("test:============== erreur fonction", nom_fonc, nom_subfonc, nom_test)
        print("test:", exc)
        printexception()
        retour = ""
        if mapper.getvar("autotest") == "raise":
            raise
    #    print("testrunner",retour)
    return retour


def eval_test(mapper, idtest, liste_regles, liste_controle, debug=0, redirect=False):
    """realise les tests et evalue le resultat"""
    nom_fonc, nom_subfonc, nom_test = idtest
    err = 0
    mapper.setvar("testrep", os.path.join(os.path.dirname(__file__), "fichiers"))

    retour = testrunner(mapper, idtest, liste_regles, debug, redirect)
    retour_controle = testrunner(mapper, idtest, liste_controle, debug, redirect)
    #    print("eval:retour tests",retour,retour_controle)
    if (
        "ok" in retour_controle
        or "ok" not in retour
        or mapper.getvar("testmode") == "all"
    ):
        if "ok" in retour_controle or "ok" not in retour:
            print("! test invalide", nom_fonc)
            err = 1
        print(
            "controle %15s %6s %-80s"
            % (nom_fonc + ":" + nom_subfonc, nom_test[1:], liste_controle),
            "--->",
            retour_controle,
        )
        print(
            "regle    %15s %6s %-80s"
            % (nom_fonc + ":" + nom_subfonc, nom_test[1:], liste_regles),
            "--->",
            retour,
        )
    #                    print ('testmode',mapper.getvar('testmode'))
    #                        raise
    return err


def controle(mapper, idtest, descript_test, debug=0):
    """realise une paire de tests fonctionnels standardises"""
    desctest = descript_test[:]

    init = desctest[0]
    if init == "notest":
        # fonction non testable par ce moyen
        return 0
    nom_fonc = idtest[0]
    redirect = False
    if init == "redirect":  # cas particulier de capture de stdout
        redirect = True
        desctest.pop(0)
        init = desctest[0]

    regles = [re.sub(r"^\^\?", "?;;;;", i) for i in desctest[1:-1]]
    regles = [re.sub(r"^\^", ";;;;", i) for i in regles]
    # gere le raccourci ^ pour 4 ;;;;
    regles_s = [re.sub(";~", ";", i) for i in regles if not i.startswith("?")]
    # ~ devant une instruction indique qu elle est liee a l'instruction a tester
    regles_c = [re.sub(r"^\?", "", i) for i in regles if ";~" not in i]
    f_controle = desctest[-1]
    liste_regles = list(
        enumerate(
            [";;;;;;;start;;", "<#" + init + ";"] + regles_s + ["<#" + f_controle + ";"]
        )
    )
    #    if "debug" in nom_test:
    #        debug = 1
    #    if debug:
    #        for i, regle in enumerate(liste_regles):
    #            num, ligne = regle
    ##            print ("preparation debug",ligne,fonc.nom in ligne)
    #            if nom_fonc in ligne: # on modifie en debug
    #                dec = ligne.split(";")+[";"]*10
    #                dec[10] = "debug"
    #                liste_regles[i] = (num, ";".join(dec))
    ##                print ("modif",liste_regles[i])
    #        print("mode debug", nom_fonc, liste_regles)

    #    print ('unittest: ',liste_regles)
    liste_controle = list(
        enumerate(
            [";;;;;;;start;;", "<#" + init + ";"]
            + [i for i in regles_c if ";" + nom_fonc not in i + ";"]
            + ["<#" + f_controle + ";"]
        )
    )
    if liste_controle == liste_regles:
        # print("attention controle inoperant")
        return None
    #   variable contenant le nom du repertoire local de fichiers pour les tests
    return eval_test(mapper, idtest, liste_regles, liste_controle, debug, redirect)


#    print ("controle ",liste_regles)
def untestable(mapper, fonc):
    if "#req_test" in fonc.description:
        conditions = fonc.description["#req_test"][0].split(",")
        for i in conditions:
            if not mapper.getvar(i):
                # print ("non defini",i, conditions)
                return i
    return ""


def fonctest(mapper, nom=None, debug=0):
    """execute les tests unitaires des fonctions"""
    nbtests = 0
    nberrs = 0
    invalides = set()
    realises = set()
    for fonc_a_tester in sorted(mapper.commandes):
        fonc = mapper.getcommande(fonc_a_tester)
        if not fonc:
            print("fonction indisponible", fonc_a_tester)
            continue
        # print("test: ", fonc_a_tester, fonc.nom, nom)
        if nom and fonc_a_tester != nom:
            continue
        if nom:
            print("test: ", fonc_a_tester, "(", fonc.nom, ")")
            print(
                "variantes:",
                [(subfonc.nom, subfonc.description) for subfonc in fonc.subfonctions],
            )
        mapper.setvar("test_courant", fonc_a_tester)

        # teslist = dict()
        # for subfonc in fonc.subfonctions:
        #     if not untestable(mapper,subfonc):
        #         for j in subfonc.description:
        #             if "#test" in j:
        #                 desctest = subfonc.description[j]
        #                 teslist[(subfonc.nom,j)] = desctest

        for subfonc in fonc.subfonctions:
            testee = False
            raison = untestable(mapper, subfonc)
            notest = False
            if not raison:
                notest = True
                for j in subfonc.description:
                    if "#test" in j:
                        notest = False
                        desctest = subfonc.description[j]

                        idtest = (fonc.nom, subfonc.nom, j)
                        # print("test unitaire,", idtest)
                        testee = True
                        if idtest not in realises:
                            errs = controle(mapper, idtest, desctest, debug=debug)
                            if errs is None:
                                # controle invalide : on ignore
                                continue
                            realises.add(idtest)
                            if errs:
                                nberrs += 1
                                invalides.add(idtest)
                            nbtests += 1
            if not testee:
                print(
                    "fonction non testee",
                    fonc.nom,
                    ":",
                    subfonc.nom,
                    (raison + " non definie") if raison else "",
                    "pas de tests definis" if notest else "",
                )
    if nom:
        print("tests realises", sorted(realises))
    return nbtests, nberrs, invalides


def seltest(mapper, nom=None, debug=0):
    """execute les tests unitaires des conditions"""
    nbtests = 0
    nberrs = 0
    invalides = set()
    for sel_a_tester in sorted(mapper.conditions):
        fonc = mapper.conditions[sel_a_tester]
        testee = False
        if nom and fonc.nom != nom:
            continue
        for j in fonc.description:
            if "#test" in j:
                #                print ("condition teste",fonc.nom,j)
                desctest = fonc.description[j]
                testee = True
                idtest = (fonc.nom, "", j)
                errs = controle(mapper, idtest, desctest, debug=debug)
                if errs:
                    nberrs += errs
                    invalides.add(idtest)
                nbtests += 2
        if not testee:
            print("condition non testee", fonc.nom)
    return nbtests, nberrs, invalides


def set_test_config(mapper):
    """enregistre la localisation des fichier de test"""
    rep = os.path.join(os.path.dirname(__file__), "fichiers/testscripts")
    # print("--------------repertoire de tests", rep)
    mapper.setvar("_test_path", rep)
    mapper.setvar("log_print", mapper.getvar("force_log", "WARNING"))

    mapper.charge_cmd_internes(test="unittest")  # on charge les ressources
    try:
        mapper.load_paramgroup("testconfig")  # on charge les configs de test
        # print("-------------------chargement params de test")
        testdb = mapper.getvar("testbd")
        testrep = mapper.getvar("testrep")
        testconfig = True
    except KeyError:
        print("config de test non definie certains tests ne seront pas effectues")
        testconfig = False
        testdb = False
        testrep = False
    return testconfig, testdb, testrep


def formattests(mapper, nom=None, debug=0):
    """execute les tests d'entree sortie"""
    if nom:
        print("---------------------test format " + nom + " -----------------------")
    else:
        print("---------------------test formats-----------------------")
    set_test_config(mapper)
    return []


def unittests(mapper, nom=None, debug=0):
    """execute les tests unitaires"""
    debug = mapper.getvar("debug")
    if nom:
        print("---------------------test unitaire " + nom + " -----------------------")
        # debug = 1
    else:
        print("---------------------test unitaires commandes-----------------------")
    set_test_config(mapper)
    mapper.initlog(force=True)
    if not nom:
        nbtests, erreurs = retest(mapper)
        print("------", nbtests, "tests regex effectues", erreurs, "erreurs -----")

    nb1, err1, finvalides = fonctest(mapper, nom, debug)
    nb2, err2, sinvalides = seltest(mapper, nom, debug)
    if nb1 + nb2 == 0:
        print("!!!!!!!!!!!!!!!!!!!!! erreur fonction inconnue", nom)
        return []
    nbtests = nb1 + nb2
    erreurs = err1 + err2
    print("------", nbtests, "tests unitaires effectues", erreurs, "erreurs -----")
    if sinvalides:
        print("conditions en erreur:", sinvalides)
    if finvalides:
        print("fonctions en erreur:", finvalides)
    return []


def autotest_partiel(mapper, nom):
    """execute un fichier d autotest"""
    if nom == "unittest":  # tests unitaires de commandes
        unittests(mapper)
        return []

    print("part:-------------------test ", nom, "-------------------")
    #       charge_cmd_internes(mapper,test=liste_commandes[1])
    liste_regles = []
    testconfig, testdb, testrep = set_test_config(mapper)
    mapper.charge_cmd_internes(test="test_" + nom)
    test = mapper.getmacro("#start_test")
    if test:
        liste_regles.extend(test.get_commands())
        print("lu regles de test", liste_regles)
    return liste_regles


def full_autotest(mapper, nom):
    """realise un autotest complet"""

    if not nom:
        unittests(mapper)
        print("----------------autotest complet--------------")
        rep = mapper.getvar("_test_path")
        liste_tests = [
            i.replace("test_", "").replace(".csv", "")
            for i in os.listdir(rep)
            if "test_" in i and ".csv" in i
        ]
        print("tests a passer", liste_tests)
        for i in liste_tests:
            map2 = mapper.getpyetl("#autotest:" + i)
            print("--------------------debut test " + i)
            if map2 is None:
                print("autotest: erreur creation environnement", i)
                continue
            map2.process()
            wstats = map2.get_work_stats()
            print(
                "---------------------%d objets lus dans %d fichiers"
                % (wstats["obj_lus"], wstats["fich_lus"])
            )
            print("--------------------fin test " + i)
        return []
    return autotest_partiel(mapper, nom)
