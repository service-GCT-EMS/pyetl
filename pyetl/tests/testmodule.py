
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


RETESTOK = {'A':['A', '#A', 'a', '#a_1', '#aa_C_2', '#aa_C_2(1:E,P,C)'],
            '+A':['+A', '+#A', '+a', '+#a_1', '+#aa_C_2', '+#aa_C_2(1:E,P,C)']

           }



RETESTFAIL = {'A':['1A', '#1', '11', '1_1', '=)', '#aa_C_2(1:E,P,C', 'A-A', ''],
              '+A':['+1A', '+#1', '+11', '1_1', '=)', '#aa_C_2(1:E,P,C', 'A', '+']
             }


def retest(mapper):
    ''' verifie la description des expressions regulieres '''
    # test expressions regulieres
#    commande_test = next(iter(mapper.commandes.values()))
    erreurs = 0
    commande_test = None
    for commande_test in mapper.commandes.values():
        break
    relist = commande_test.definition['entree'].relist
    nbtests = 0
    for i in relist:
        if i in RETESTOK:
            for j in RETESTOK[i]:
#                print ('test',relist[i][0],j)
                match = re.match(relist[i][0], j)
                nbtests += 1
                if not match:
                    erreurs += 1
                    print('retest', i, j, 'ko----> devrait matcher')
#
        if i in RETESTFAIL:
            for j in RETESTFAIL[i]:
#                print ('test',relist[i][0],j)
                match = re.match(relist[i][0], j)
                nbtests += 1
                if match:
                    erreurs += 1
                    print('retest', i, j, 'ko----> ne devrait pas matcher')
    print('test regex achevé avec', erreurs, 'erreurs')
    return nbtests, erreurs


def testrunner(mapper, idtest, liste_regles, debug, redirect=False):
    """execute un test standardise"""
    nom_fonc, nom_subfonc, nom_test = idtest
    try:
        map2 = mapper.getpyetl(liste_regles, nom=nom_fonc)
#        print ("creation",map2.nompyetl)
        if map2 is None:
            print('unittest: erreur creation environnement ', nom_fonc, nom_subfonc, nom_test)
            return ""
        if debug and int(debug):
            map2.set_param("debug", 1)
        if redirect:
            capture = io.StringIO()
            with redirect_stdout(capture):
                map2.process()
            retour = capture.getvalue()
#            print ("mode redirect actif ->",retour,"<-")
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
        if mapper.get_param("autotest") == "raise":
            raise
#    print("testrunner",retour)
    return retour

def eval_test(mapper, idtest, liste_regles, liste_controle, debug=0, redirect=False):
    """realise les tests et evalue le resultat"""
    nom_fonc, nom_subfonc, nom_test = idtest
    err = 0
    mapper.set_param("testrep", os.path.join(os.path.dirname(__file__), "fichiers"))

    retour = testrunner(mapper, idtest, liste_regles, debug, redirect)
    retour_controle = testrunner(mapper, idtest, liste_controle, debug, redirect)
#    print("eval:retour tests",retour,retour_controle)
    if 'ok' in retour_controle or 'ok' not in retour or mapper.get_param('testmode') == 'all':
        if 'ok' in retour_controle or 'ok' not in retour:
            print('! test invalide', nom_fonc)
            err = 1
        print("controle %15s %6s %-80s"
              %(nom_fonc+":"+nom_subfonc, nom_test[1:], liste_controle), '--->',
              retour_controle)
        print("regle    %15s %6s %-80s"
              %(nom_fonc+":"+nom_subfonc, nom_test[1:], liste_regles), '--->', retour)
#                    print ('testmode',mapper.get_param('testmode'))
#                        raise
    return err

def controle(mapper, idtest, descript_test, debug=0):
    ''' realise une paire de tests fonctionnels standardises'''
    desctest = descript_test[:]

    init = desctest[0]
    if init == "notest":
        #fonction non testable par ce moyen
        return 0
    nom_fonc = idtest[0]
    redirect = False
    if init == "redirect": # cas particulier de capture de stdout
        redirect = True
        desctest.pop(0)
        init = desctest[0]

    regles = [re.sub(r'^\^\?', '?;;;;', i) for i in desctest[1:-1]]
    regles = [re.sub(r'^\^', ';;;;', i) for i in regles]
    # gere le raccourci ^ pour 4 ;;;;
    regles_s = [re.sub(';~', ';', i) for i in regles if not i.startswith('?')]
    # ~ devant une instruction indique qu elle est liee a l'instruction a tester
    regles_c = [re.sub(r'^\?', '', i) for i in regles if ';~' not in i]
    f_controle = desctest[-1]
    liste_regles = list(enumerate(['<#'+init+';']+regles_s+['<#'+f_controle+';']))
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
    liste_controle = list(enumerate(['<#'+init+';']+
                                    [i for i in regles_c if ';'+nom_fonc not in i+";"]+
                                    ['<#'+f_controle+';']))
#   variable contenant le nom du repertoire local de fichiers pour les tests
    return eval_test(mapper, idtest, liste_regles, liste_controle, debug, redirect)
#    print ("controle ",liste_regles)




def fonctest(mapper, nom=None, debug=0):
    ''' execute les tests unitaires des fonctions '''
    nbtests = 0
    nberrs = 0
    for fonc_a_tester in sorted(mapper.commandes):
        fonc = mapper.commandes[fonc_a_tester]
        if nom and fonc.nom != nom:
            continue
        for subfonc in fonc.subfonctions:
            testee = False
            for j in subfonc.description:
                if '#test' in j:
                    desctest = subfonc.description[j]
                    testee = True
                    idtest = (fonc.nom, subfonc.nom, j)
                    nberrs += controle(mapper, idtest, desctest, debug=debug)
                    nbtests += 2
            if not testee:
                if subfonc.nom != fonc.nom:
                    print('fonction non testee', fonc.nom, subfonc.nom)
                else:
                    print('fonction non testee', fonc.nom)
    return nbtests, nberrs


def seltest(mapper, nom=None, debug=0):
    ''' execute les tests unitaires des selecteurs'''
    nbtests = 0
    nberrs = 0
    for sel_a_tester in sorted(mapper.selecteurs):
        fonc = mapper.selecteurs[sel_a_tester]
        testee = False
        if nom and fonc.nom != nom:
            continue
        for j in fonc.description:
            if '#test' in j:
#                print ("selecteur teste",fonc.nom,j)
                desctest = fonc.description[j]
                testee = True
                idtest = (fonc.nom, "", j)
                nberrs += controle(mapper, idtest, desctest, debug=debug)
                nbtests += 2
        if not testee:
            print('selecteur non testee', fonc.nom)
    return nbtests, nberrs

def set_test_path(mapper):
    """enregistre la localisation des fichier de test"""
    rep = os.path.join(os.path.dirname(__file__), "fichiers/testscripts")
    print('------------------------------------repertoire de tests', rep)
    mapper.set_param("_test_path", rep)
    mapper.charge_cmd_internes(test='unittest') # on charge les ressources
    mapper.load_paramgroup('testconfig') # on charge les configs de test






def unittests(mapper, nom=None, debug=0):
    ''' execute les tests unitaires '''
    if nom:
        print('---------------------test unitaire '+nom+' -----------------------')
    else:
        print('---------------------test unitaires commandes-----------------------')
    set_test_path(mapper)
    nbtests, erreurs = retest(mapper)
    print('------', nbtests, "tests regex effectues", erreurs, "erreurs -----")

    nb1, err1 = fonctest(mapper, nom, debug)
    nb2, err2 = seltest(mapper, nom, debug)
    if nb1+nb2 == 0:
        print("!!!!!!!!!!!!!!!!!!!!! erreur fonction inconnue")
        return []
    nbtests = nb1 + nb2
    erreurs = err1 + err2
    print('------', nbtests, "tests unitaires effectues", erreurs, "erreurs -----")
    return []



def autotest_partiel(mapper, nom):
    """ execute un fichier d autotest"""
    if nom == 'unittest':# tests unitaires de commandes
        unittests(mapper)
        return []

    print('part:-------------------test ', nom, "-------------------")
#       charge_cmd_internes(mapper,test=liste_commandes[1])
    liste_regles = []
    set_test_path(mapper)
    mapper.charge_cmd_internes(test="test_"+nom)
    test = mapper.macros.get('#start_test')
    if test:
        liste_regles.extend(test.get_commands())
#    print ("lu regles de test",liste_regles)
    return liste_regles




def full_autotest(mapper, nom):
    ''' realise un autotest complet'''

    if not nom:
        unittests(mapper)
        print("----------------autotest complet--------------")
        rep = mapper.get_param("_test_path")
        liste_tests = [i.replace('test_', '').replace('.csv', '')
                       for i in os.listdir(rep) if 'test_' in i and '.csv' in i]
        print("tests a passer", liste_tests)
        for i in liste_tests:
            print("-------------------debut test", i, "-------------------")
            map2 = mapper.getpyetl('#autotest:'+i)
            if map2 is None:
                print('autotest: erreur creation environnement', i)
                continue
            nl2, nfl2, _, _ = map2.process()
            print('-------------------fin test', i, ':', nl2, 'objets dans', nfl2, 'fichiers')
            print("----------------------------------------------------------------")
        return []
    return autotest_partiel(mapper, nom)
