# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 22:15:26 2015

@author: claude
"""
import os
import time
#import pyetl.formats.shapefile_access as SH
from . import shapefile_access as SH
from .interne.objet import Objet
#-----------------------------------------------------------------------------
# format shape base sur shapefile.py de jlawhead<at>geospatialpython.com
#-----------------------------------------------------------------------------

def __schema_from_shp(ident, sh_reader, schema_courant):
    '''extrait le schema du fichier shape '''
    schema_cref = None
    liste_att = []
    if ident in schema_courant.classes: # il existe deja donc c'est un forcage
        schema_cref = schema_courant.classes[ident]
    else:
        schema_c = schema_courant.def_classe(ident)
    code_geom = sh_reader.shapeType
    if code_geom == 0:
        type_geom = '0'
    elif code_geom in (1, 11, 21):
        type_geom = '1'
    elif code_geom in (3, 13, 23):
        type_geom = '2'
    elif code_geom in (5, 15, 25):
        type_geom = '3'
    schema_courant.info["type_geom"] = type_geom
#    schema_courant.is_3d = type_geom > 10
    schema_courant.info["dimension"] = "3" if code_geom > 10 else "2"
    attributs = sh_reader.fields
    for i in attributs[1:]:
        nom, type_att, long_att, dec = i
        if schema_cref:
#            print ('shp:essai mapping attribut ',nom,schema_cref.attmap)
            if nom in schema_cref.attmap:
#                print ('shp:mapping attribut ',nom,schema_cref.attmap[nom].nom)
                nom = schema_cref.attmap[nom].nom
        if type_att == 'N':
            #type numerique
            if dec == 0:
                #pas de decimales: entier ou entier long
                typ_interne = 'E' if long_att < 8 else 'EL'
            else:
                #flottant
                typ_interne = 'F'
        elif type_att == 'D':
            #date
            typ_interne = 'D'
        elif type_att == 'L':
            #text
            typ_interne = 'T'
        elif type_att == 'C':
            typ_interne = 'T'
        else:
            print("erreur de type shape ", type_att)
            typ_interne = 'T'
        liste_att.append(nom.lower())
        if not schema_cref:
            schema_c.stocke_attribut(nom.lower(), typ_interne, '', typ_interne, True,
                                     long_att, dec,
                                     alias=nom[:], nom_court=nom[:], nb_conf=30)
##TODO:                                 # pas satisfaisant a mettre en parametre nb_conf
    if schema_cref:
        return schema_cref, liste_att

    schema_c.info["type_geom"] = type_geom

    return schema_c, liste_att

#def ajuste_valeurs_entree(ajustables,attributs): # cas particuliers de mappings en entree
#    ''' remplace des valeurs d 'enum en entree a la volee'''
#    for i in ajustables:
#        v=attributs[i]
#        if v in ajustables[i]:
#            print ('shp:ajustement',i,attributs[i],'->',ajustables[i][v])
#            attributs[i]=ajustables[i][v]

#def controle_conformites(confs,attributs,err):
#    ''' valide les conformites à la lecture'''
##    print ('conformites a controler',confs)
#
#    for i in confs.items():
#        nom,vals=i
#        if attributs[nom] in vals:
#            continue
#        err.append('erreur conformite ' + nom +':->'+attributs[nom]+'<-')
#
#def controle_pk(stock,pk,err):
#    ''' valide l'unicite de la clef primaire'''
#    if pk in stock:
#        err.append('clef duppliquee :'+ pk)
#    else:
#        stock.add(pk)





def lire_objets_shp(rep, chemin, fichier, stock_param, regle, debut=0):
    '''lit des objets a partir d'un fichier shape.'''
    if debut == 0:
        debut = int(time.time())
    n_obj = 0
    #geom=False
    racine = os.path.basename(rep)
    verif = False
    if stock_param.get_param("schema_entree"):
        schema_courant = stock_param.schemas[stock_param.get_param("schema_entree")]
        verif = True
    else:
        schema_courant = stock_param.init_schema(racine, origine='B', fich=racine)
    entree = os.path.join(rep, chemin, fichier)
    classe = os.path.splitext(fichier)[0]
    stock_param.fichier_courant = classe
    maxobj = int(stock_param.get_param('lire_maxi', 0))
    sh_reader = SH.Reader(entree)
    idclasse_orig = (chemin, classe)
#    print ('lecture shape ',idclasse_orig,schema_courant,stock_param.get_param("schema_entree"))
    idclasse = schema_courant.map_dest(idclasse_orig)
#    print ('mapping entree ',(chemin,classe),'->',idclasse)
    schemaclasse, liste_attrib = __schema_from_shp(idclasse, sh_reader, schema_courant)

    nomgr, nomcl = idclasse
#    attributs = sh_reader.fields
#    liste_attrib = [i[0].lower() for i in attributs[1:]]
#    print("info: formats lecture classe shape ", chemin,stock_param.fichier_courant,
#          idclasse,schema.info["type_geom"],verif)
    pkey = schemaclasse.getpkey
    if pkey:
#        print ('controle schema identification clef primaire',schema.getpkey())
        attclef = schemaclasse.getpkey
    confs = bool(schemaclasse.confs)
    ajust = bool(schemaclasse.ajust_enums)

    for shp in sh_reader.iterShapeRecords():
        n_obj = n_obj + 1
        obj = Objet(nomgr, nomcl, format_natif='shp', conversion=geom_from_shp)
        obj.attributs.update(list(zip(liste_attrib,
                                      (str(j) if j is not None else '' for j in shp.record))))
        #print 'lecture_shape', obj.attributs
        #print('lecture_shape', shp.record)
        obj.setorig(n_obj)
        obj.geom = shp.shape
        obj.setschema(schemaclasse)
        obj.forceorig(idclasse_orig)
        if verif:
            err = list()
            if ajust:
    #            print ('shp: ajustement_enum',schema.nom,schema.ajust_enums)
                schemaclasse.ajuste_valeurs(obj)
            if pkey:
                schemaclasse.controle_pk(obj.attributs[attclef], err)
            if confs:
                schemaclasse.controle_conformites(obj, err)
            if err:
#                print ('detection erreur schema entree ',err)
                obj.attributs['#erreurs'] = ';'.join(err)

        type_geometrie = shp.shape.shapeType
#        obj.is_3d = type_geometrie > 10
        obj.geom_v.dimension = 3 if type_geometrie > 10 else 2
        nature = type_geometrie % 10
        if nature == 1:
            obj.attributs['#type_geom'] = '1'
        elif nature == 3:
            obj.attributs['#type_geom'] = '2'
        elif nature == 5:
            obj.attributs['#type_geom'] = '3'

        obj.attributs["#schema"] = schema_courant.nom

        #bj.schema=schema
        stock_param.moteur.traite_objet(obj, regle)

        if maxobj: # nombre maxi d'objets a lire par fichier
            if n_obj >= maxobj:
                obj = None
                break
        if n_obj % 100000 == 0:
            print("lire_objets_shp ", n_obj, int(time.time()-debut), obj.attributs['#type_geom'])
    return n_obj

def geom_from_shp(obj):
    '''cree la geometrie interne'''
    geom = obj.geom
    geom_v = obj.geom_v
    type_geometrie = geom.shapeType
    if obj.schema: # s'il y a un schema : on force le type de geometrie demandees
        type_geom_demande = obj.schema.info["type_geom"]
    #print ("formats :  shp type_geometrie", type_geometrie, type_geometrie/10)
    dim = 2 if int(type_geometrie/10) == 0 else 3
    nature = type_geometrie % 10
    if nature == 0:
        geom_v.type = '0'
    elif nature == 1:
        geom_v.type = '1'
        if dim == 3:
            geom.points[0].append(geom.z[0])
        geom_v.setpoint(geom.points[0], 0, int(dim))
#        print ("creation geometrie", geom.points[0])
    elif nature == 3 or nature == 5:
        type_geom = '2' if nature == 3 else '3'
        liste_parties = list(geom.parts)
        liste_parties.append(len(geom.points)) # on ajoute la position du dernier point
        for i in range(len(liste_parties)-1):
            #print "shp_part", i, l[i], l[i+1], l, l[0:], range(*l[i:i+2])
            for j in range(*liste_parties[i:i+2]):
                if dim == 3:
                    geom.points[j].append(geom.z[j])
                geom_v.addpoint(geom.points[j], dim)
            geom_v.fin_section(1, 0)
        if type_geom >= '2' and type_geom_demande >= '2':
            type_geom = type_geom_demande

        #print ("format:shp : ", geom_v.np, geom_v.type, geom_v.erreur )
    obj.finalise_geom(type_geom=type_geom, orientation='R')

    if obj.attributs['#type_geom'] != '0':
        obj.nogeom = False
    geom_v.valide = True
    return True

def get_shapewriter(regle, groupe, classe, rep_sortie, schema):
    ''' initialise une sortie shape '''
    sorties = regle.stock_param.sorties
    id_demand = regle.numero
    rep_sortie = regle.getvar('_sortie', loc=2) if rep_sortie is None else rep_sortie
    nom = sorties.get_id(rep_sortie, groupe, classe, ".shp")
    sortie = sorties.get_res(id_demand, nom)
    if sortie is None:
        os.makedirs(os.path.dirname(nom), exist_ok=True)
        type_geom = schema.info["type_geom"]
        if type_geom == '0':
            shapetype = 0
        elif type_geom == '1': # point
#            shapetype = 11 if schema.is_3d else 1
            shapetype = 11 if schema.info["dimension"] == '3' else '1'
        elif type_geom == '2': # ligne
#            shapetype = 13 if schema.is_3d else 3
            shapetype = 13 if schema.info["dimension"] == '3' else '3'
        elif type_geom == '3': # ligne
#            shapetype = 15 if schema.is_3d else 5
            shapetype = 15 if schema.info["dimension"] == '3' else '5'
        writer = SH.streamWriter(fich=nom, shapeType=shapetype)
        sorties.creres(id_demand, nom, writer)
        for i in schema.get_liste_attributs():
            type_att = schema.attributs[i].type_att_base
            taille = schema.attributs[i].taille
            dec = schema.attributs[i].dec
            dec = 3
            writer.field(i, fieldType=type_att, size=taille, decimal=dec)

#        sw.openfiles()
        sortie = sorties.get_res(id_demand, nom)
#        print ("get fich:schema",schema)
    return sortie

def shapestreamer(obj, regle, final, attributs=None, rep_sortie=None):
    '''shape ecritures non bufferisees'''
    if obj.virtuel:
        return False
    liste_fich = regle.stock_param.liste_fich
    groupe, classe = obj.ident
    if regle.dident != obj.ident:
#        if obj.schema:
        schema_courant = obj.schema
#        else:
#            nom_schema = obj.attributs.get('#schema', groupe)
#            print('objet sans schema', classe, obj.attributs.get('#schema'), groupe)
#            schema_courant = regle.stock_param.getschema(nom_schema, obj.ident)
        regle.ressource = get_shapewriter(regle, groupe, classe, rep_sortie,
                                          schema=schema_courant)
        regle.dident = (groupe, classe)
        regle.schema_courant = schema_courant
#        regle.liste_att = schema_courant.get_liste_attributs()

    shpwriter = regle.ressource.handler # on reste sur la meme classe et on utilise le meme writer
    schema_courant = regle.schema_courant
    nom = regle.ressource.nom
    obj.initgeom()

#    if not obj.geom_v.valide:
#        obj.attributs_geom(obj)
#    print ('shapestreamer schema',schema_courant.nom,schema_courant.info["type_geom"],
#    obj.geom_v.npt,obj.geom_v.valide,obj.geom)
#    try:
    if schema_courant.info["type_geom"] == '0':
        shpwriter.null()
    elif schema_courant.info["type_geom"] == '1':
        shpwriter.point(*obj.geom_v.point.coords)
    elif schema_courant.info["type_geom"] == '2':
        parts = [[j for j in i.coords] for i in obj.geom_v.lignes]
#        shapetyp = 13 if schema_courant.is_3d else 3
        shapetyp = 13 if schema_courant.info["dimension"] == '3' else '3'
#        print ('shapestreamer',shapetyp,parts)
        shpwriter.poly(parts, shapetyp)

    elif schema_courant.info["type_geom"] == '3':
        parts = [[j for j in i.coords] for i in obj.geom_v.lignes]
#        shapetyp = 15 if schema_courant.is_3d else 5
        shapetyp = 15 if schema_courant.info["dimension"] == '3' else '5'
#        print ('shapestreamer',shapetyp,len(obj.geom_v.lignes))

        shpwriter.poly(parts, shapetyp)
#    print ('shp attributs',obj.attdict)
    shpwriter.record(**obj.attdict)
#    except:
#        print ('erreur ecriture shape ',schema_courant.nom,schema_courant.info["type_geom"],
#               obj.geom_v.npt,obj.geom_v.valide,obj.geom,obj.attributs.get("gid"),obj.geom_v.point)

    liste_fich[nom] += 1
    regle.ressource.compte(1)
    return True

#def ecrire_objet_shp(fichier, obj, liste_att, type_geom, multiple):
#    ''' a finaliser '''
##TODO fonction a ecrire
#    return True


def ecrire_objets_shp(regle, final, rep_sortie=None, entete=''):
    '''writer shape non finalise'''
#    ng, nf = 0, 0
    dident = None
    ressource = None
    for groupe_courant in list(regle.stockage.keys()):
        # on determine le schema
        n_obj = 0
        for obj in regle.recupobjets(groupe_courant):
            if obj.virtuel:
                continue
            if obj.ident != dident:
                classe, groupe = obj.ident
                if ressource:
                    ressource.compte(n_obj)
                    n_obj = 0
#                if obj.schema:
                schema_courant = obj.schema
#                else:
#                    nom_schema = obj.attributs.get('#schema', groupe)
#                    print('objet sans schema', groupe,classe, obj.attributs.get('#schema'))
#                    schema_courant = regle.stock_param.getschema(nom_schema, obj.ident)
                ressource = get_shapewriter(regle, groupe, classe, rep_sortie,
                                            schema=schema_courant)
                shpwriter = ressource.handler
                dident = groupe, classe
                type_geom = schema_courant.info["type_geom"]
                shapetyp = type_geom
                if type_geom == '2':
                    shapetyp = 3
                elif type_geom == '3':
                    shapetyp = 5
#                if schema_courant.is_3d:
                if schema_courant.info["dimension"] == '3':
                    shapetyp = shapetyp+10
# on ecrit les objets

            obj.initgeom()

#            if not obj.geom_v.valide:
#                obj.attributs_geom(obj)
            if type_geom == 0:
                shpwriter.null()
            elif type_geom == 1:
                shpwriter.point(*obj.geom_v.point.coords)
            else:
                parts = [[j for j in i.coords] for i in obj.geom_v.lignes]
                shpwriter.poly(parts, shapetyp)
            shpwriter.record(**obj.attdict)
            n_obj += 1

    return 0, 0
