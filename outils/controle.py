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


system = platform.system()
release = platform.release()
DEFCODEC = "utf-8"
if system == 'Windows' and release =='XP':
    DEFCODEC = "cp1252"
print ('codec ES positionne par defaut a ',DEFCODEC)

origine=sys.argv[1]
ref=sys.argv[2]
codec=DEFCODEC
if len(sys.argv)>3:
    codec=sys.argv[3]

liste_ref=dict()
liste_comp=dict()

def scandirs(rac, chemin, rec):
    '''parcours recursif d'un repertoire.'''
    path=os.path.join(rac,chemin)
    if os.path.exists(path):
        for element in os.listdir(path):
            #print path,element
            if os.path.isdir(os.path.join(path,element)):
                #print 'trouve directory: ' + element
                if rec :
                    for f in scandirs(rac,os.path.join(chemin,element),rec): yield f
            else : yield (os.path.basename(element),chemin)


for i in scandirs(origine,'',True):
    liste_comp[i]=1
    
for i in scandirs(ref,'',True):
    liste_ref[i]=1
 
print ('nombre de fichiers lus ',origine,len(liste_comp),ref,len(liste_ref))

# controle 1 presence 
for i in liste_comp:
    if i not in liste_ref :
        print ("fichier en trop dans ",origine, i)
        
for i in liste_ref:
    if i not in liste_comp :
        print ("fichier manquant dans ",origine, i)
nb_err=0        
# controle 2 egalite des fichiers 
for i in sorted(liste_comp.keys()):
    if i in liste_ref:
        fich1=os.path.join(ref,i[1],i[0])
        a=open(fich1,'r',encoding=codec,errors="backslashreplace").readlines()
        fich2=os.path.join(origine,i[1],i[0])
        b=open(fich2,'r',encoding=codec,errors="backslashreplace").readlines()
        erreurs=[]
        a.sort()
        b.sort()
        for l in D.unified_diff(a, b,n=0):
            erreurs.append(l)
        if len(erreurs) >0 : 
            print ("comparaison %-50s ----> %10d / %10d %10d"%(i, len(erreurs),len(a),len(a)-len(b)))
            n=0
            for j in erreurs:
                n=n+1
                if n<20:
                    print (j.encode('cp850','ignore'))
            #print (erreurs[:5])
            nb_err+=1
    #raise
print("nombre total d'erreurs ", nb_err, "sur ",len(liste_comp))
    