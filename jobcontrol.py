# -*- coding: utf-8 -*-
"""
Created on Tue Jan 06 09:46:00 2015

@author: 89965
"""
import sys,os
import time

if len(sys.argv)>3:
    racine=sys.argv[1]
    njobs=int(sys.argv[2])
    timeout=int(sys.argv[3])
else:
    print("usage jobcontrol racine nb jobs timeout")
    exit(1)
suite=True
total=0
fini=False
nfini=0
while not fini:
    if total%100==0:print("job control ", racine, njobs-nfini,'/',njobs, total)
    time.sleep(1)
    total+=1
    fini=True
    nfini=0
    for i in range(njobs):
        nom_fich=racine+str(i)
#        print ('test '+ nom_fich,os.path.isfile(nom_fich))
        if os.path.isfile(nom_fich):
            nfini+=1
        
    fini= nfini >= njobs or total > timeout
if total > timeout : 
    print("erreur: sortie en timeout")
    exit(1)     

print("temps de traitement total" , total, 'secondes')   
exit(0)
        
