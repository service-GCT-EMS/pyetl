# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 13:33:58 2015

@author: 89965
"""
#from . import csv as E
from collections import namedtuple
from . import asc as A
from .interne.objet import Objet


# format interne pour le stockage en fichier temporaire
def _extendlist(liste):
    '''utilitaire d'applatissement d'une liste de liste
    c est une syntaxe qui ne s'invente pas alors quand on l'a on la garde'''
    return [x for slist in liste for x in slist]
    #l=liste[0]
    #print 'liste a applatir',l
    #for j in liste[1:]: l.extend(j)
    #return l

def _ecrire_section_tmp(section):
    '''ecrit une section en format temporaire'''
#    print     ("S,"+str(section.couleur) + "," + str(section.courbe) + ',' + section.__list_if__)

    return "S,"+str(section.couleur) + "," + str(section.courbe) + ',' + section.__list_if__
#def ecrire_ligne_tmp(ligne):
#    return (["L"].extend([ecrire_section_tmp(j) for j in ligne.sections])).append("M")
def _ecrire_ligne_tmp(ligne):
    '''ecrit une ligne en format temporaire'''
#    print("ligne", len(ligne.sections))
#    print('ecrire_ligne',['L']+[_ecrire_section_tmp(j) for j in ligne.sections])
#    print('fin_ligne')
    return ['L']+[_ecrire_section_tmp(j) for j in ligne.sections]

def _ecrire_lignes_tmp(lignes):
    '''ecrit un ensemble de  lignes en format temporaire'''
    return _extendlist([_ecrire_ligne_tmp(j) for j in lignes])

def _ecrire_polygone_tmp(poly):
    '''ecrit un polygone en format temporaire'''
#    print("polygone", len(poly.lignes))
#    print('longueur lignes',[len(j.sections) for j in poly.lignes])
#    print('liste')
    return ["P"]+(_extendlist([_ecrire_ligne_tmp(j) for j in poly.lignes]))+['Q']

def _ecrire_polygones_tmp(polygones):
    '''ecrit un ensemble de  polygones en format temporaire'''
    return _extendlist([_ecrire_polygone_tmp(j) for j in polygones])

def ecrire_geometrie_tmp(geom):
    '''ecrit une geometrie en format temporaire'''
    if   geom.type == '1':
        return ['O']+geom.point.__list_if__
    elif geom.type == '2':
#        print("geom_tmp",geom,geom.type,len(geom.lignes) )
        if len(geom.lignes) > 1:
            return _ecrire_lignes_tmp(geom.lignes)
        return _ecrire_ligne_tmp(geom.lignes[0])
    elif geom.type == '3':
#        print("geom_tmp",geom,geom.type,len(geom.polygones) )

        if len(geom.polygones) > 1:
            return _ecrire_polygones_tmp(geom.polygones)
        return _ecrire_polygone_tmp(geom.polygones[0])
    else:
        raise TypeError('geometrie inconnue: '+ geom.type)

def geom_from_tmp(obj):
    '''convertit une geometrie en format temporaire en geometrie interne'''
    geom_v = obj.geom_v
    geom_v.type = '2'
    poly = None
    nouvelle_ligne = False
    for i in obj.geom:
        code = i[0]
        if code == "P":
            poly = geom_v.polygones
            geom_v.type = '3'
        elif code == "L":
            nouvelle_ligne = True
        elif code == "S":
            sect_parts = i.split(",")
            couleur, arc = sect_parts[1:2]
            coords = [list(map(float, j.split(' '))) for j in sect_parts[3:]]
            if nouvelle_ligne:
                lig = geom_v.nouvelle_ligne_s()
            lig.ajout_section(couleur, arc, len(coords[0]), coords)
        elif code == "M": # fin ligne
            geom_v.ajout_ligne(lig)
            if poly:
                poly.ajout_contour(lig)
        elif code == "Q": # fin polygone
            geom_v.ajout_polygone(poly)
            poly = None
        elif code == "O":
            pnt = [float(j) for j in i[1:].split(' ')]
            geom_v.setpoint(pnt, 0, len(pnt))
    return geom_v



def tmp_entetes(obj, form):
    ''' retourne un entete en format interne
        form permet de connaitre le format de stockage de la geometrie
        en general de l'ewkt
    '''
    niveau, classe = obj.ident
    if not form:
        form = ''
    entete = '1' + niveau + "," + classe + "," + form + "," + obj.attributs['#type_geom']+'\n'
    return entete

def tmp_attributs(obj):
    '''stockage des attributs.
        c'est de l'asc
    '''
    attlist = "\n".join(("2"+i+",NG"+str(len(str(obj.attributs[i])))+","
                         +str(obj.attributs[i])+";" for i in obj.attributs
                         if i not in obj.text_graph and i not in obj.etats))
    if obj.text_graph:
        tglist = "\n".join(("2"+i+",TL"+str(len(str(obj.attributs[i])))+","+
                            ",".join(obj.text_graph[i])+","+str(obj.attributs[i])+";"
                            for i in obj.text_graph))
        attlist = attlist+"\n"+tglist
    if obj.etats:
        elist = "\n".join(("4"+i+",NG"+str(len(str(obj.attributs[i])))+","+
                           str(obj.attributs[i])+";" for i in obj.etats))
        attlist = attlist+"\n"+elist
    return attlist


def tmp_geom(obj, convertisseur):
    '''serialise les geometries'''
    if obj.attributs['#type_geom'] == '0':
        return ""
    #print 'tmp-geom',self.nogeom,self.atg,ecrire_geom_ewkt(self.geom_v,False,False,err)
    #if obj.atg : return '3'+ecrire_geom_ewkt(obj.geom_v,False,False,err)+'\n'
    if obj.geom_v.valide:
        if convertisseur is None:
            convertisseur = ecrire_geometrie_tmp
        geom = convertisseur(obj.geom_v)
    else:
        geom = obj.geom
    if isinstance(geom, list):
        return "3" + "\n3".join(geom)+ '\n'
    return '3'+ geom + '\n'
#

# =================== format temporaire ==============================
def lire_objets(fichier, stock_param):
    """relit les objets du stockage temporaire"""
    for ligne in open(fichier, 'r', encoding='utf-8'):
        if ligne:
            code = ligne[0]
            if code == "1":
                niveau, classe, form, type_geom = ligne[1:-1].split(',')
                obj = Objet(niveau, classe, format_natif=form,
                            conversion=stock_param.get_converter(form))
                obj.attributs['#type_geom'] = type_geom
#                if form: print ('format natif ',form,stock_param.get_converter(form))
            elif code == "2" or code == "4":
                A.ajout_attribut_asc(obj, ligne)
            elif code == "3":
                obj.nogeom = False
                obj.geom.append(ligne[1:-1])
                if not ligne:
                    print('lecture objet sans geom')
            elif code == "5":
                if obj.geom and not obj.attributs_geom:
                    print('geom_lue sans convertisseur', form, ':', obj.attributs_geom)
#                print (obj.geom)
                obj.geomnatif = True
                yield obj

def ecrire_objets(nom, mode, groupe, geomwriter, nom_format):
    """stocke les objets en format temporaire"""
    fichier = open(nom, mode, encoding='utf-8')

    for classe in groupe:
        liste_obj = groupe[classe]
        for i in liste_obj:
            if i.geom_v.valide:
                fichier.write(tmp_entetes(i, nom_format))
            else:
                fichier.write(tmp_entetes(i, i.format_natif))
            fichier.write(tmp_attributs(i))
            fichier.write('\n')
            geom = tmp_geom(i, geomwriter)
            if geom:
                fichier.write(geom)
                fichier.write('\n')
            fichier.write("5fin_objet\n")
    fichier.close()


#============================= interne pour comparaison ====================


class ObjStore(object):
    '''structure de stockage d'objets en memoire'''
    def __init__(self, nom, schemaclasse, clef):
        self.nom = nom
        self.schemaclasse = schemaclasse
        self.data = dict()
        self.strlist = schemaclasse.liste_attributs()
        struct = self.strlist[:]
        struct.append('geometrie')
        self.structure = namedtuple(nom, struct)
        self.key = clef
        self.nbval = 0

    def write(self, obj):
        ''' stocke un objet '''
        clef = obj.attributs.get(self.key)
        if clef in self.data:
            print('interne:clef duppliqueee', self.nom, self.key, clef)
            return False
        liste = [obj.attributs[i] for i in self.strlist]
        liste.append(obj.geom_v)
        tmp = self.structure(liste)
        self.data[clef] = tmp
        self.nbval += 1
        return True

    def get(self, clef):
        '''recuper un objet'''
        return self.data.get(clef)



def intstreamer(obj, regle): #ecritures non bufferisees
    ''' ecrit des objets tmp en streaming'''
    store = regle.stock_param.store

    if obj.ident != regle.dident:
        groupe, classe = obj.ident
#        if obj.schema:
        schema_courant = obj.schema
        nom = '.'.join(obj.ident)

        ressource = store.get(nom)
        if ressource is None:
            ressource = ObjStore(nom, schema_courant, regle.params.cmp2.val)
            store[nom] = ressource

        regle.ressource = ressource
        regle.dident = (groupe, classe)
    else:
        schema_courant = obj.schema
    ressource = regle.ressource
    ressource.write(obj)


def ecrire_objets_int(regle, _):
    ''' ecrit des objets dans le stockage interne'''
    nb_obj, nb_fich = 0, 0
    dident = None
    store = regle.stock_param.store
#    print("csv:ecrire csv", regle.stockage.keys())
    ressource = None
    for groupe in list(regle.stockage.keys()):
        # on determine le schema
        nom = ''
        for obj in regle.recupobjets(groupe):
            groupe, classe = obj.ident
            if obj.ident != dident:
                schema_courant = obj.schema
                nom = '.'.join(obj.ident)
                ressource = store.get(nom)
                if ressource is None:
                    nb_fich += 1
                    ressource = ObjStore(nom, schema_courant, regle.params.cmp2.val)
                    store[nom] = ressource
                dident = (groupe, classe)
            retour = ressource.write(obj)
            if retour:
                nb_obj += 1
    return nb_obj, nb_fich
