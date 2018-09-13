# -*- coding: utf-8 -*-
"""
remapping des sichgiers projets sur siglc

@author: 89965
"""
import os
import sys
import xml.etree.ElementTree as ET

# project_converter conversion de projets qgis

ogrpath=r'set path=S:\Commun\SIGLI\outils\cree_projets_standalone\programmes\ogr;%path'

sous_projets=set()

def lire_mapping(fichier,entree_s,entree_c,sortie_s,sortie_c):
    mapping=dict()
    with open(fichier,'r') as mapp:
        for i in mapp:
            l=i.split(';')
            vin=(l[entree_s],l[entree_c])
            vout=(l[sortie_s],l[sortie_c])
            mapping[vin]=vout
#            print ('mapping',vin,vout)
    return mapping




def convert_projet(nom,entree,sortie,mapp,connect):  #fonction de conversion principale:
    db,host,port=connect.split(':')
    racine=os.path.splitext(os.path.basename(entree))[0]
    #entree=os.path.dirname(nom)
    projet = ET.parse(entree)
    print ('-------------lecture_xml-------- ',nom,racine)
   
    for layer in projet.iter('maplayer'):
        provider=layer.find('provider')
#        print ('couches',layer.find('layername').text, ' type : ',layer.find('provider').text, layer.find('datasource').text)
#        print ('valeur de provider',provider)
        trouve=False
        if provider is not None:
#            print ('-------------------------valeur de provider',provider)
            sourcetype=provider.text
            source=layer.find('datasource')
            ligne_source=source.text
            if sourcetype=='postgres': # traitement base postgres : on passe en base locale et on modifie les elements
                l=ligne_source.split(' ')
                trouve=False
                for k in range(len(l)):
                    v=l[k].split('=')
                    if 'dbname' in v[0]:
                        l[k]="dbname='"+db+"'"
                    if 'host' in v[0]:
                        l[k]="host="+host
                    if 'port' in v[0]:
                        l[k]="port="+port
                    if v[0] == 'table':
                        table=v[1].replace('"','')
                        clef=tuple(table.split('.'))
                        if clef in mapp:
                            result=mapp[clef]
                            trouve=True
#                            print ('remplacement',l,k,clef,'--->',result)
                            l[k]='table="%s"."%s"' % result
                        else:
                            pass
#                            print ('clef non trouvee',clef,mapp.keys())
                if trouve:
    #                print ('avant  ',source.text)
                    source.text=' '.join(l)
    #                print ('apres  ',source.text)
    projet.write(os.path.join(sortie,racine+'.qgs'))        
    
def decode_entree(valeur):
    p=valeur.split(':')
    v0=int(p[0])
    v1=int(p[1]) if len(p)==2 else v0+1
    return v0,v1


    
 
def main():

    project='160106_maquette_ass'
    fsortie='resultat'
    #print ('arguments',sys.argv)
    if len(sys.argv)<6:
        print ('parametres: projet fichier_mapping,entree,sortie,param_serveur')
        print ('     projet : nom du projet')
        print ("     mapping : fichier csv contenant la table de correspondance")
        print ("     entree : position des parametres d'entree dans la table de correspondance")
        print ("     sortie : position des parametres de remplacement dans la table de correspondance")
        print ("     param_serveur : chaine de connection  base:host:port")
        exit(0)

    project=sys.argv[1]
    fich_map=sys.argv[2]
    entree=sys.argv[3]
    sortie=sys.argv[4]
    connect=sys.argv[5]
    entree_s,entree_c=decode_entree(entree)
    sortie_s,sortie_c=decode_entree(sortie)
    if len(sys.argv)>6:
           fsortie=sys.argv[6]



    print ('repertoite projet',project,os.path.isdir(project))
    
    if os.path.isdir(project):
        print ('repertoire ',os.path.isdir(project))
        plist=[i for i in os.listdir(project) if '.qgs' in i]
        prefix=project
    else:
        plist=[project]
        prefix=''
    
    print ('projets a traiter ',plist  ) 
    
    mapp=lire_mapping(fich_map,entree_s,entree_c,sortie_s,sortie_c)

    for i in plist:
        fentree=os.path.join(prefix,i)
        convert_projet(i,fentree,fsortie,mapp,connect)
main()
