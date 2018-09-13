# -*- coding: cp1252 -*-
'''modification d'attributs en fonction d'un fichier de parametrage avec
prise en charge des expressions regulieres'''
import time
import sys
starttime = time.time()
from pyetl.pyetl import runpyetl, VERSION
#print ('mapper: fin import modules',int(time.time()-t1))
#import cProfile as profile
#---------------debut programme ---------------


def message_help():
    ''' message d aide de demarrage'''
    print("mapper version", VERSION)
    print("parametres insuffisants")
    print("usage:", sys.argv[0], "commande [entree] [sortie] [parametres]")
    print("      ", sys.argv[0], "#help pour l aide des commandes")
#    exit(1)


def main():
    ''' appel de pyetl
    traitement des parametres d'entree
    instanciation du moteur
    et traitement des fichiers  '''
    if len(sys.argv) == 1:
        message_help()
    else:
        mapping = sys.argv[1]
        runpyetl(mapping, sys.argv[2:])

#profile.run('main()','schemamapper.profile')
#import pstats
#pstats.Stats('schemamapper.profile').sort_stats('time').print_stats()

main()
print ('temps total %.2f secondes' % (time.time()-starttime))

