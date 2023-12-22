# -*- coding: utf-8 -*-
"""modification d'attributs en fonction d'un fichier de parametrage avec
prise en charge des expressions regulieres"""
import time

STARTTIME = time.time()
import sys
from pyetl.pyetl import runpyetl
from pyetl.vglobales import VERSION


# print ('mapper: fin import modules',int(time.time()-t1))
# import cProfile as profile
# ---------------debut programme ---------------


def message_help():
    """message d aide de demarrage"""
    print("mapper version", VERSION)
    print("parametres insuffisants")
    print("usage:", sys.argv[0], "commande [entree] [sortie] [parametres]")
    print("      ", sys.argv[0], "#help pour l aide des commandes")


#    exit(1)


def main():
    """appel de pyetl
    traitement des parametres d'entree
    instanciation du moteur
    et traitement des fichiers"""
    if len(sys.argv) == 1:
        message_help()
    else:
        args = sys.argv

        # print("args", list((n, i) for n, i in enumerate(args)))
        runpyetl(args[1], args[2:])
    print(
        "=========== temps d'execution total %.2f secondes" % (time.time() - STARTTIME)
    )


# profile.run('main()','schemamapper.profile')
# import pstats
# pstats.Stats('schemamapper.profile').sort_stats('time').print_stats()

if __name__ == "__main__":
    # execute only if run as a script
    main()
