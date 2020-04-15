# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:44:21 2016

@author: 89965
"""
import os
import sys
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import shutil
import glob
# project_converter conversion de projets qgis

ogrpath=r'set path=S:\Commun\SIGLI\outils\cree_projets_standalone\programmes\ogr;%path'

sous_projets=set()

def decode_conf_csv(entree):
    """decode un tableau de conformites
    se presente sous la forme:  nom;ordre,valeur;alias;mode
    hierarchie :
        force / fichier / demande / 1
    """
    lin = 0
    enumerations=dict()
    for i in entree:
        if lin == 0 and "!" in i[:4]:
            #                print (" schema conf io:detecte commentaire utf8")
            lin = 1
            continue
        if i[0] == "!":
            #                print (" schema conf io:detecte commentaire")
            continue
        val_conf = i.replace("\n", "").split(";")
        if not val_conf:
            continue
        nom = val_conf[0].lower().strip()
        if not nom:
            continue
        if len(val_conf) < 2:
            print("enumeration incomplete ", val_conf)
            continue
        ordre = int(val_conf[1]) if val_conf[1].isnumeric() else 0
        valeur = val_conf[2].strip()
        conf = enumerations.get(nom,[])
        conf.append(valeur)
    return enumerations    # on ignore


def lire_conf_csv(fichier, mode_alias, cod):
    """lit un fichier de conformites au format csv"""
    enumerations=dict()
    if not os.path.isfile(fichier):
        print("schema: ::: warning fichier conformites introuvable ", fichier)
        return enumerations
    with open(fichier, "r", encoding=cod) as entree:
        lin = 0
        for i in entree:
            if lin == 0 and "!" in i[:4]:
                #                print (" schema conf io:detecte commentaire utf8")
                lin = 1
                continue
            if i[0] == "!":
                #                print (" schema conf io:detecte commentaire")
                continue
            val_conf = i.replace("\n", "").split(";")
            if not val_conf:
                continue
            nom = val_conf[0].lower().strip()
            if not nom:
                continue
            if len(val_conf) < 2:
                print("enumeration incomplete ", val_conf)
                continue
            ordre = int(val_conf[1]) if val_conf[1].isnumeric() else 0
            valeur = val_conf[2].strip()
            conf = enumerations.get(nom,[])
            conf.append(valeur)
    return enumerations    # on ignore








def makeabs(fichier,entree):
    nom=fichier
    if '$' in nom: # chemin relatif mocca en changeant les lettres de lecteur BEURK
        v=nom.split('$')
        nom =v[0][-1]+':'+v[1]
    if os.path.isabs(nom):
        return nom
    else:
        origine=os.path.join(entree,nom)
    if not os.path.exists(origine):
        print ('erreur fichier introuvable ',origine)

    print ('conversion absolue ',fichier,entree,'->',origine)
    return origine


def setlocal(fichier,entree,sortie,copieur,multi=False): # convertit un chemin en local et prepare le script de copie
    if not fichier:
        raise FileNotFoundError

    nom=fichier.split('?')[0]
    if '$' in nom: # chemin relatif mocca en changeant les lettres de lecteur BEURK
        v=nom.split('$')
        nom =v[0][-1]+':'+v[1]
    if os.path.isabs(nom):
        origine=nom
    else:
        origine=os.path.join(entree,nom)
    if not os.path.exists(origine):
        print ('erreur fichier introuvable ',origine)
    #if '?' in fichier: # c'est une URL
     #url=true

    nomlocal=os.path.join('.',str(os.path.basename(fichier)))
    destination=os.path.join(sortie,str(os.path.basename(nom)))
    origine=origine.replace('/','\\')
    if multi:
        destination=sortie
        origine=os.path.splitext(origine)[0]+'.*'
    copieur[origine]=destination
    return nomlocal.replace('\\','/')

def convert_projet(nom,entree,sortie,converters,copieur,schemas, limit=False, extend = None, retours=dict(), enumerations=dict(),attributs=dict()):
    #fonction de conversion principale:

    racine=str(os.path.splitext(os.path.basename(nom))[0])
    racine=racine.replace('ô','o')
    racine=racine.replace('ê','e')
    racine=racine.replace('é','e')
    racine=racine.replace('é','e')
    #entree=os.path.dirname(nom)
    projet = ET.parse(nom)
    print ('-------------lecture_xml-------- ',nom,racine)
    carte= projet.find('mapcanvas')
    print ('extend',extend, 'limit',limit)
    xmin,xmax,ymin,ymax=('','','','')
    if limit:
        ext=carte.find('extent')
        xmin=ext.find('xmin').text.split('.')[0]
        print ('xmin',xmin)
        xmax=ext.find('xmax').text.split('.')[0]
        ymin=ext.find('ymin').text.split('.')[0]
        ymax=ext.find('ymax').text.split('.')[0]
        spatial= '-spat ' +' '.join((xmin,ymin,xmax,ymax))
    elif extend:
        spatial= '-spat ' +' '.join(extend)

    else:
        spatial =''



    serveurs ={'sigli': 'host=bpsigli.cus.fr port=34000',
               'siglc': 'host=bpsiglc.cus.fr port=34000'}

    converter1 = 'ogr2ogr '+spatial+' -f SQLite -dsco SPATIALITE=yes -lco SPATIAL_INDEX=yes -gt 65536 -forceNullable "%s.sqlite" PG:"dbname='+'%s %s" %s'
    converter2 = 'ogr2ogr '+spatial+' -f SQLite -update -lco SPATIAL_INDEX=yes -gt 65536 -forceNullable "%s.sqlite" PG:"dbname='+'%s %s" %s'
    sqlitegeosource="dbname='%s.sqlite' table=\"%s\" (geometry) sql="
    sqlitealphasource="dbname='%s.sqlite' table=\"%s\" sql="

    for layer in projet.iter('maplayer'):
        provider=layer.find('provider')
#        print ('couches',layer.find('layername').text, ' type : ',layer.find('provider').text, layer.find('datasource').text)
#        print ('valeur de provider',provider)
        if provider is not None:
#            print ('-------------------------valeur de provider',provider)

            sourcetype=provider.text
            source=layer.find('datasource')
            ligne_source=source.text
            if sourcetype=='postgres': # traitement base postgres : on passe en base locale et on modifie les elements
                l=ligne_source.split(' ')
                table,dbname,svname,port=('','','','')
                for k in l:
                    v=k.split('=')
                    if 'dbname' in v[0]:
                        dbname=v[1].replace("'",'')
                    if v[0] == 'table':
                        table=v[1].replace('"','')
                        if table in schemas:
                            table=schemas[table]+'.'+table
                    if v[0] == 'host':
                        svname = v[1]
                    if v[0] == 'port':
                        port =  v[1]
                svdef = 'host='+svname+' port='+port
                # print ('detecte base', dbname,svdef)
                nomschema,nomtable = table.split('.')
                nomschema=nomschema.replace('"','')
                nomtable=nomtable.replace('"','')
                if table not in retours:
                    localname=os.path.join('.',racine+'_data')
                else:
                    localname=os.path.join('.',racine+'_retour')
                if '(' in ligne_source:
                    ligne_source= sqlitegeosource % (localname.replace('\\','/'),table)
                else:
                    ligne_source= sqlitealphasource % (localname.replace('\\','/'),table)
                provider.text='spatialite'
                if localname in converters:
                    if table not in converters[localname]:
                        converters[localname][table]=converter2 % (localname, dbname, svdef, table)
                else:
                    converters[localname]=dict()
                    converters[localname][table]=converter1 % (localname, dbname, svdef, table)
                source.text=ligne_source
                # === analyse et modification des editeurs
                for editeur in layer.iter('edittype'):
                    widgettype=editeur.get('widgetv2type')
                    if editeur.get('widgetv2type')=="Enumeration": # c'est une enum : on modifie
                        nom_att_enum=editeur.get('name')
                        if nom_att_enum:
                            print("detection enum",dbname,'->',nom_att_enum)
                        if dbname in attributs and  (nomschema,nomtable,nom_att_enum) in attributs[dbname]:
                            nom_enum = attributs[dbname][(nomschema,nomtable,nom_att_enum)]
                            if dbname in enumerations and nom_enum in enumerations[dbname]:
                                print ('enum traitable:',nom_enum)
                                editeur.set('widgetv2type',"ValueMap")
                                config = editeur.find('widgetv2config')
                                for item in enumerations[dbname][nom_enum]:
                                    newvalue=ET.Element('value', attrib={'key':item,'value':item})
                                    config.append(newvalue)

                #print ('transformation',source.text)
            elif sourcetype=='spatialite': # traitement base sqlite : on  copie et on mets le path en relatif
                l=ligne_source.split(' ')
                for k in l:
                    v=k.split('=')
                    if 'dbname' in v[0]:
                        dbname=v[1].replace("'",'')
                        ndbname=setlocal(dbname,entree,sortie,copieur)
                        source.text=ligne_source.replace(dbname,ndbname)
            elif sourcetype=='ogr':
                dbname=source.text
                nsourcename=setlocal(dbname,entree,sortie,copieur,multi=True)
                source.text=nsourcename
#            elif sourcetype=='gdal':
#                dbname=source.text
#                nsourcename=setlocal(dbname,entree,sortie,copieur,multi=True)
#                source.text=nsourcename
            elif sourcetype=='delimitedtext':
                dbname=source.text
                nom=dbname.split('?')[0]
                if  'file:' in nom: #('c est une url)
                    nomdistant= urllib.parse.parse_qs('nom='+nom.replace('file:','').replace('///','')).get('nom')[0]
                    print ('detecte url ',nom,nomdistant)
                    nomlocal=setlocal(nomdistant,entree,sortie,copieur)
                    #print ('copie',nomlocal)
                    #local,headers=urllib.request.urlretrieve(nom,filename=os.path.join(sortie,os.path.basename(nomlocal)))
                    nsourcename='file:./'+urllib.parse.quote(nomlocal)+'?'+dbname.split('?')[1]
                else:
                    nsourcename=setlocal(dbname,entree,sortie,copieur)
                source.text=nsourcename
        else:
            embed=layer.get('embedded',"0")
            if embed=='1':
                projet_interne=layer.get('project')
                proj_int=makeabs(projet_interne,entree)
                e2=os.path.dirname(proj_int)
                convert_projet(proj_int,e2,sortie,converters,copieur,schemas,
                               extend=(xmin,ymin,xmax,ymax) if limit else extend, retours=retours,enumerations=enumerations,attributs=attributs)
                sous_projets.add(proj_int)
                projet_interne_local=os.path.join('.',os.path.splitext(os.path.basename(projet_interne))[0]+
                                                  '_local.qgs').replace('\\','/')
                layer.set('project',projet_interne_local)

    for p in projet.iter('annotationform'):
        if p.text and '.ui' in p.text:
            p.text=setlocal(p.text,entree,sortie,copieur)
    for p in projet.iter('previewexpression'):
        p.clear()
    for p in projet.iter('editform'):
        if p.text and '.ui' in p.text:
            p.text=setlocal(p.text,entree,sortie,copieur)
    for p in projet.iter('property'):
        clef=p.get('key')
        if clef=='embedded_project':
            projet_interne=p.get('value')
            if projet_interne:
                proj_int=makeabs(projet_interne,entree)

                e2=os.path.dirname(proj_int)
                convert_projet(proj_int,e2,sortie,converters,copieur,schemas,
                               extend=(xmin,ymin,xmax,ymax) if limit else extend,retours=retours,enumerations=enumerations,attributs=attributs)
                sous_projets.add(proj_int)
                projet_interne_local=os.path.join('.',os.path.splitext(os.path.basename(projet_interne))[0]+
                                                  '_local.qgs').replace('\\','/')
                p.set('value',projet_interne_local)

    # on passe les path en relatifs
    for p in projet.iter('Paths'):
        for q in p.iter('Absolute'):
            q.text='false'



    projet.write(os.path.join(sortie,racine+'_local.qgs'),encoding='UTF-8')



def main():

    project='160106_maquette_ass'
    sortie='resultat'
    description='parametres/schemas'
    csvcodec='cp1252'
    #print ('arguments',sys.argv)
    if len(sys.argv)<2:
        print ('parametres: chemin_du_projet [limit/nolimit],[rep sortie]')
        print ('     chemin du projet : nom complet du projet avec son chemin absolu')
        print ("     limit : limite l'export a l'emprise de la fenetre enregistree dans le projet")
        exit(0)

    project=sys.argv[1]

    limit = sys.argv[2] == 'limit' if len(sys.argv)>2 else False
    print ('repertoire projet',project,os.path.isdir(project))

    if len(sys.argv)>3:
        sortie = sys.argv[3]
        os.makedirs(sortie, exist_ok=True)
        print ('repertoire sortie',sortie, os.path.dirname(sortie))
        description = os.path.join(os.path.dirname(sortie),description)


    if os.path.isdir(project):
        print ('repertoire ',os.path.isdir(project))
        plist=[i for i in os.listdir(project) if '.qgs' in i]
        prefix=project
    else:
        plist=[project]
        prefix=''

    print ('projets a traiter ',plist  )


    #data = r'.\data.sqlite'
    #dataqg = r'./data.sqlite'
    #qgis=r'D:\donnees\programmes\qgis_2.12.0'
    #ogr2ogr=os.path.join(qgis,'bin\\ogr2ogr.exe')

    #provider='<provider encoding="System">spatialite</provider>\n'
    preview='<previewExpression></previewExpression>\n'


    converters=dict()
    enumerations=dict()
    attrdef=dict()
    dbname=''
    schemas=dict()
    try:
        with open('correspondance_schemas.csv','r') as mapping:
            for i in mapping:
                v=i.split(';')
                schemas[v[1]]=v[0]
    except FileNotFoundError:
        pass
    convert=os.path.join(sortie,'crebase_local.bat')
    # on lit les descriptions de schema
    for fich in os.listdir(description):
        if fich.endswith('enumerations.csv'):
            base=fich.replace('_enumerations.csv','')
            enumbase=enumerations.setdefault(base,dict())
            with open(os.path.join(description,fich),'r',encoding=csvcodec) as enums:
                for ligne in enums:
                    if ligne.startswith('!'):
                        continue
                    tmp = ligne.split(';')
                    enumlist = enumbase.setdefault(tmp[0],[])
                    enumlist.append(tmp[2])
        if fich.endswith('classes.csv'):
            base=fich.replace('_classes.csv','')
            attbase=attrdef.setdefault(base,dict())
            with open(os.path.join(description,fich),'r',encoding=csvcodec) as attrs:
                for ligne in attrs:
                    if ligne.startswith('!'):
                        continue
                    tmp = ligne.split(';')
                    attbase[tmp[0],tmp[1],tmp[2]]=tmp[9]
    copieur={}
    for i in plist:
        retours=set()
        liste_retours = os.path.splitext(i)[0]+'_retours.csv'
        if os.path.isfile(os.path.join(prefix,liste_retours)):
            with open(os.path.join(prefix,liste_retours)) as info_retours:
                for ligne in info_retours:
                    tmp = ligne.split(';')
                    if not ligne.startswith('!'):
                        retours.add(tmp[0])
        entree=os.path.join(os.path.dirname(i),prefix)
        convert_projet(i,entree,sortie,converters,copieur,schemas,limit=limit,retours=retours,enumerations=enumerations,attributs=attrdef)

    for i in copieur:
        print( 'copy ',i,'->',copieur[i])
        if '*' in i:
            for f in glob.glob(i):
                shutil.copy(f, copieur[i])
        else:
            if os.path.isfile(i):
                shutil.copy(i, copieur[i])
            else:
                print ("******************************fichier introuvable ",i )
    print ('ecriture fichiers chargement')
    for i in converters:
        convert=os.path.join(sortie,i+'_charge.bat').replace(' ','_')
#        print (i,converters[i])
        print (i+'_charge.bat')

        open(convert,'w').write('\n'.join([ogrpath]+sorted(converters[i].values())))

main()
