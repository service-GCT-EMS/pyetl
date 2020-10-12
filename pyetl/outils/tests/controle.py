# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 14:30:42 2016

@author: 89965
"""

# comparaison de fichiers dans 2 repertoires :

import difflib as D

import os
import sys
import platform
from pyetl.moteur.fonctions.outils import scandirs


def getdefcodec():
    """recupere l'encodage systeme"""
    system = platform.system()
    release = platform.release()
    defcodec = "utf-8"
    if system == "Windows" and release == "XP":
        defcodec = "cp1252"
    #    print('codec ES positionne par defaut a ', defcodec)
    return defcodec


def main():
    """comparaison de fichiers"""

    origine = sys.argv[1]
    ref = sys.argv[2]

    codec = sys.argv[3] if len(sys.argv) > 3 else getdefcodec()

    liste_ref = {i for i in scandirs(ref, "", True)}
    liste_comp = {i for i in scandirs(origine, "", True)}

    #    for i in scandirs(origine, '', True):
    #        liste_comp[i] = 1
    #
    #    for i in scandirs(ref, '', True):
    #        liste_ref[i] = 1

    print("nombre de fichiers lus ", origine, len(liste_comp), ref, len(liste_ref))

    # controle 1 presence
    for i in liste_comp:
        if i not in liste_ref:
            print("fichier en trop dans ", origine, i)

    for i in liste_ref:
        if i not in liste_comp:
            print("fichier manquant dans ", origine, i)
    nb_err = 0
    # controle 2 egalite des fichiers
    for i in sorted(liste_comp.keys()):
        if i in liste_ref:
            fich1 = os.path.join(ref, i[1], i[0])
            f_a = open(fich1, "r", encoding=codec).readlines()
            fich2 = os.path.join(origine, i[1], i[0])
            f_b = open(fich2, "r", encoding=codec).readlines()
            erreurs = []
            for ligne in D.unified_diff(f_a, f_b, n=0):
                erreurs.append(ligne)
            if erreurs:
                print("------------------comparaison ", i, fich1, fich2, "------>", len(erreurs))
                n_e = 0
                for j in erreurs:
                    n_e = n_e + 1
                    if n_e < 20:
                        print(j.encode("cp850", "ignore"))
                # print (erreurs[:5])
                nb_err += 1
        # raise
    print("nombre total d'erreurs ", nb_err, "sur ", len(liste_comp))


main()
