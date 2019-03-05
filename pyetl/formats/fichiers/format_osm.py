# -*- coding: utf-8 -*-
# formats d'entree sortie
''' format osm '''

import os
import time
import xml.etree.cElementTree as ET

from pyetl.schema.fonctions_schema import copyschema
from .interne.objet import Objet
#from .formats import Reader

#print ('osm start')
#import pyetl.schema as SC

# ewkt ##################################################################
#def parse_ewkb(geometrie,texte):


# lecture de la configuration osm
class DecodeConfigOsm(object):
    '''stocke une config de classe'''
    def __init__(self, vals):
        self.atts = []
        self.static = []
        self.schema = None
        self.geom = vals[2]
        if vals[0] == '*':
            self.getident = self.decode_defaut
            self.liste_classes = None
            self.force_geom = None
            self.niveau, self.classe = vals[4].split('.')
        else:
            self.getident = self.decode_classe
            self.clef = vals[0]
            self.sous_clef = vals[1]
#            self.geom=[int(j) for j in vals[2].split(',')] if vals[2] else None
            self.liste_classes = vals[3]
            self.niveau, self.classe = vals[4].split('.')
            self.force_geom = vals[5] if vals[5] else None

            for j in range(6, len(vals)):
                if vals[j]:
                    vl2 = vals[j].split(':')
                    if len(vl2) == 1:
                        self.atts.append((vl2[0], self.clef))
                    elif len(vl2) == 2:
                        if vl2[1][0] == '#':
                            self.static.append((vl2[0], vl2[1][1:]))
                        else:
                            self.atts.append((vl2[0], vl2[1]))

    def setliste(self, groupes):
        '''stocke les listes associees'''
        if self.liste_classes:
            liste_classes = groupes.get(self.liste_classes, None)
#            print (' affectation groupes',liste_classes)
            self.liste_classes = [(i[0], i[1]) for i in liste_classes
                                  if i[2] == self.geom] if liste_classes else None

    def init_schema(self, schema_travail):
        '''genere le schema des donnees'''
        self.schema = schema_travail


    def decode_defaut(self, tagdict):
        ''' range les objets residuela dans les classes par defaut '''
        if len(tagdict) == 1:
            if 'source' in tagdict or 'created_by' in tagdict:
                return (self.niveau, 'a_jeter_'+str(self.geom))
            if 'type' in tagdict and tagdict['type'] == "multipolygon":
                return (self.niveau, 'a_jeter'+str(self.geom))
        return (self.niveau, self.classe)


    def decode_classe(self, tagdict):
        '''determine la classe d un objet osm'''
#        print ('recherche clef',self.clef,tagdict)
#        if self.geom and type_geom not in self.geom : return False

        if self.clef not in tagdict:
            return None
        if self.sous_clef:
            if self.sous_clef not in tagdict:
                return None
            elif self.liste_classes:
                clef = tagdict[self.clef]+'::'+tagdict[self.sous_clef]
                if clef in self.liste_classes:
                    return self.liste_classes[clef]
                return (self.niveau, self.classe)
        if self.liste_classes:
            if tagdict[self.clef] in self.liste_classes:
                return self.liste_classes[tagdict[self.clef]]
        return (self.niveau, self.classe)


    def get_schema_classe(self, ident, idref):
        ''' retourne le schema et le cree si necessaire '''
        schem = self.schema.get_classe(ident)
        if schem:
            return schem

        schemaclasse = self.schema.def_classe(idref)
        schemaclasse.stocke_attribut('gid', 'EL', index='P:')
        for nom, _ in self.atts:
            schemaclasse.stocke_attribut(nom, 'T')
        for nom, _ in self.static:
            schemaclasse.stocke_attribut(nom, 'T')
        schemaclasse.stocke_attribut('tags', 'H')
#        schemaclasse.stocke_attribut('#all_tags', 'H')
        schemaclasse.info["type_geom"] = self.force_geom if self.force_geom else self.geom
        incomplet = copyschema(schemaclasse, idref, None, filiation=False)
        incomplet.groupe = "osm_incomplet"
        self.schema.ajout_classe(incomplet)
        if incomplet.info["type_geom"] == '3':
            incomplet.info["type_geom"] = '2'
            # si l'objet est incomplet on ne peut pas toujours creer un contour
#            incomplet.attributs['#type_geom'] = '2'
        return self.schema.get_classe(ident)


    def decode_objet(self, tagdict, geom, type_geom, manquants):
        '''range l objet dans la bonne classe'''
#        if len(tagdict)==0:
#            ident=('non_classe','a_jeter')
#        else:
#        if self.geom and type_geom != self.geom:
#            return None
        ident = self.getident(tagdict)
        if ident is None:
            return None
        idref = ident
        if manquants: # on separe les objets incomplets
            ident = ("osm_incomplet", ident[1])
        obj = Objet(*ident, format_natif='osm', conversion=geom_from_osm)
        obj.geom = geom
        obj.attributs['#type_geom'] = type_geom

        if self.force_geom is not None:
            obj.attributs['#type_geom'] = self.force_geom # on force

        for att, tag in self.atts:
            if tag in tagdict:
                obj.attributs[att] = tagdict[tag]
                del tagdict[tag]

        for att, val in self.static:
            obj.attributs[att] = val

        obj.setschema(self.get_schema_classe(ident, idref))
        return obj


def init_osm(mapper=None):
    """initialisation de la config osm"""
    config_osm_def = os.path.join(os.path.dirname(__file__), 'config_osm2.csv')
    config_osm = mapper.get_var('config_osm',
                                config_osm_def)if mapper is not None else config_osm_def
#    print('fichier osm ', config_osm)

#    CONFIGFILE = os.path.join(os.path.dirname(__file__), config_osm)
    for conf in open(config_osm, 'r').readlines():
        chaine = conf.strip()
        if chaine and chaine[0] != '!':
            valeurs = [j.strip() for j in chaine.split(';')]
            if valeurs[0][0] == '{': # c'est une definton de groupe
                nom_groupe = valeurs[0].replace('{', '').replace('}', '')
                if nom_groupe not in GROUPLIST:
                    GROUPLIST[nom_groupe] = dict()
                groupe = GROUPLIST[nom_groupe]
                groupe[valeurs[1]] = (valeurs[2], valeurs[3], valeurs[4])
            else: # c'est une definition standard
                geoms = [j for j in valeurs[2].split(',')] if valeurs[2] else None
                if geoms:
                    for i in geoms:
                        valeurs[2] = i
                        DECODAGE[i].append(DecodeConfigOsm(valeurs))
                else:
                    for i in DECODAGE:
                        valeurs[2] = str(i)
                        DECODAGE[i].append(DecodeConfigOsm(valeurs))
    for i in DECODAGE:
    #    DECODAGE[ii].append(Decodeconfig(['*', '', str(ii)]))
        for conf in DECODAGE[i]:
            conf.setliste(GROUPLIST)

GROUPLIST = dict()
DECODAGE = {'1':[], '2':[], '3':[]}
init_osm()


#########################################################################
# format osm
#########################################################################

#def _gettags(elem):
#    '''renvoie les tags d un objet sous forme d un dictionnaire '''
#    return {i.get('k', 'undefined'):i.get('v') for i in elem.iter(tag='tag')}

#def _creeliste(points, liste):
#    ''' transforme une list d identifiants en ligne '''
#    geom = list([points[i] for i in liste if i in points])
#    ninc = len(liste)-len(geom)
#    ppt = liste[0]
#    dpt = liste[-1]
#    contour = ppt == dpt
#    return (geom, ninc, contour, ppt, dpt)



def _getpoints(points, elem):
    '''decodage des structures de type  way
    recupere les points d une ligne et renvoie une liste de points
    retour: geom : liste de points
    ninc : nbre de points perdus
    contour : booleen si la liste est fermee
    pp dp indice des premiers et derniers points de la liste'''
    liste = list([i.get('ref') for i in elem.iter(tag='nd')])
    geom = list([points[i] for i in liste if i in points])
    ninc = len(liste)-len(geom)
    ppt = liste[0]
    dpt = liste[-1]
    contour = ppt == dpt
    return (geom, ninc, contour, ppt, dpt)
#    return _creeliste(points, liste)

def _getmembers(points, lignes, objets, elem):
    ''' decodage des structures de type relation  '''
    geom = []
    nodelist = []
    rellist = []
    perdus = 0
    ppt = None
    ferme = False
    for i in elem.iter(tag='member'):
        type_membre = i.get('type')
        identifiant = i.get('ref')
        role = i.get('role')
        if type_membre == 'node':
            if identifiant in points:
                nodelist.append((identifiant, role))
            else:
                perdus += 1
            return (geom, perdus, ferme)
        if type_membre == 'way': # c est une multiligne ou un polygone
            ligne, manquants, lferm, ppl, dpl = lignes.get(i.get('ref'),
                                                           ('', 0, False, None, None))
            ferme = lferm or ferme
            ppt = ppt or ppl
            if ligne:
                geom.append((ligne, role))
                ferme = ferme or ppt == dpl
                perdus += manquants
            else:
                perdus += 10000
            return (geom, perdus, ferme)
        if type_membre == 'relation':
            if identifiant in objets:
                rellist.append(identifiant, role)
            else:
                perdus += 100000
        return (geom, perdus, ferme)


def geom_from_osm(obj):
    ''' convertit une geometrie osm'''
    geomv = obj.geom_v
    if geomv.valide:
        return True
    if not obj.geom:
        obj.attributs['#type_geom'] = '0'
        return True
    if obj.attributs['#type_geom'] == '1':
        geomv.setpoint(obj.geom[0], None, 2)

    else:
#        ext = 999998
#        trou = 999999
#        geom = obj.geom
#        for i in range(len(geom)):
#            lg, role = geom[i]
#            if role == 'inner':
#                ext = min(i, ext)
#            if role == 'outer':
#                trou = min(i, trou)
#        if trou < ext:
#            if ext < 999998:
#                geom[ext], geom[trou] = geom[trou], geom[ext]
#            else:
#                lg, role = geom[trou]
#                geom[trou] = (lg,'outer')


#        print('geom_from osm', obj.geom)
        for sect, role in obj.geom:

            geomv.cree_section(sect, 2, 1, 0, interieur=role == 'inner')
            #print ('osm:creation section ',lg)

    obj.finalise_geom(type_geom=obj.attributs['#type_geom'])
    return True


def _classif_osm(tagdict, geom, type_geom, manquants, ido):
    ''' applique les regles de classification a l'objet '''
#    print (' dans classif osm ')
    for decodeur in DECODAGE[type_geom]:
        obj = decodeur.decode_objet(tagdict, geom, type_geom, manquants)
        if obj:
            tags = ", ".join(['"'+i+'" => "'+tagdict[i].replace('"', r'\"')+'"'
                              for i in sorted(tagdict)])
            obj.hdict = {'tags':tagdict}
            obj.attributs['tags'] = tags
            obj.attributs['gid'] = ido
            obj.geom_v.srid = '4326'
            return obj
    print('classif osm : pas de categorie', str(tagdict).encode('ascii', 'ignore'))
    return None

def init_schema_osm(schema):
    '''enregistre le nom du schema'''
    for i in DECODAGE:
        for decodeur in DECODAGE[i]:
            decodeur.init_schema(schema)

def classif_elem(elem, points, lignes, objets):
    ''' classifie un element '''
    ignore = {'tag', 'nd', 'member'}
    type_geom = '0'
    manquants = 0
    geom = []
    if elem.tag in ignore:
        return -1, None, None, None, None
#        print ('osm:',event,elem.tag,elem.get('id'))
#    attributs = _gettags(elem)
    attributs = {i.get('k', 'undefined'):i.get('v') for i in elem.iter(tag='tag')}
    ido = elem.get('id')
    if elem.tag == 'node':
        points[ido] = [float(elem.get('lon')), float(elem.get('lat')), 0]
        if attributs:
            type_geom = '1'
            geom = [points[ido]]
    elif elem.tag == 'way': # lignes
        lignes[ido] = _getpoints(points, elem)
        if attributs:
            ligne, manquants, ferme, _, _ = lignes[ido]
            if ligne:
                geom = [(ligne, 'outer')] if ferme else [(ligne, 'way')]
                type_geom = '3' if ferme else '2'
    elif elem.tag == 'relation':
        if attributs:
            geom, manquants, ferme = _getmembers(points, lignes, objets, elem)
            if geom:
                type_geom = '3' if ferme else '2'
        else:
            print('element perdu', elem.get('id'))
    else:
        print('tag inconnu', elem.tag)
    return ido, attributs, geom, type_geom, manquants






def lire_objets_osm(self, rep, chemin, fichier):
    '''lit des objets a partir d'un fichier xml osm'''
    regle_ref = self.regle if self.regle else self.regle_start
    stock_param = regle_ref.stock_param
    dd0 = time.time()
    nlignes = 0
    nobj = 0
#    regle = stock_param.regles[0]
    nomschema = os.path.splitext(fichier)[0]
    init_schema_osm(stock_param.init_schema(nomschema, 'F'))
#    ignore = {'tag':1, 'nd':1, 'member':1}
    points = dict()
    lignes = dict()
    objets = dict()
    prn = 1000000
    aff = prn
    for _, elem in ET.iterparse(os.path.join(rep, chemin, fichier)):
        nlignes += 1
        if nlignes == aff:
            print('osm: lignes lues', nlignes, 'objets:', nobj, 'en', int(time.time()-dd0),
                  's (', int(nobj/(time.time()-dd0)), ')o/s')
            aff += prn

        ido, attributs, geom, type_geom, manquants = classif_elem(elem, points, lignes, objets)
        if ido == -1:
            continue
        if type_geom != '0': # analyse des objets et mise en categorie
            obj = _classif_osm(attributs, geom, type_geom, manquants, ido)
            if obj:
                nobj += 1
                obj.setorig(nobj)
                obj.attributs["#chemin"] = chemin
                stock_param.moteur.traite_objet(obj, self.regle_start) # on traite le dernier objet
        elem.clear()

    return nobj




class OsmReader(object):
    '''classe de lecture du format osm'''
    def __init__(self, stock_param):
        config_osm_def = os.path.join(os.path.dirname(__file__), 'config_osm.csv')
        config_osm = stock_param.get_var('config_osm', config_osm_def)
        self.grouplist = dict()
        self.decodage = {'1':[], '2':[], '3':[]}
        self.stock_param = stock_param
        self.chargeconfig(config_osm)


    def chargeconfig(self, config_osm):
        '''charge un fichier de config osm'''
        for conf in open(config_osm, 'r').readlines():
            chaine = conf.strip()
            if chaine and chaine[0] != '!':
                valeurs = [j.strip() for j in chaine.split(';')]
                if valeurs[0][0] == '{': # c'est une definton de groupe
                    nom_groupe = valeurs[0].replace('{', '').replace('}', '')
                    if nom_groupe not in self.grouplist:
                        self.grouplist[nom_groupe] = dict()
                    groupe = self.grouplist[nom_groupe]
                    groupe[valeurs[1]] = (valeurs[2], valeurs[3], valeurs[4])
                else: # c'est une definition standard
                    geoms = [j for j in valeurs[2].split(',')] if valeurs[2] else None
                    if geoms:
                        for i in geoms:
                            valeurs[2] = i
                            self.decodage[i].append(DecodeConfigOsm(valeurs))
                    else:
                        for i in self.decodage:
                            valeurs[2] = str(i)
                            self.decodage[i].append(DecodeConfigOsm(valeurs))
        for i in self.decodage:
        #    DECODAGE[ii].append(Decodeconfig(['*', '', str(ii)]))
            for conf in self.decodage[i]:
                conf.setliste(self.grouplist)

    def read(self, rep, chemin, fichier, regle):
        '''lit des objets a partir d'un fichier xml osm'''
        dd0 = time.time()
        nlignes = 0
        nobj = 0
    #    regle = stock_param.regles[0]
        nomschema = os.path.splitext(fichier)[0]
        init_schema_osm(self.stock_param.init_schema(nomschema, 'F'))
    #    ignore = {'tag':1, 'nd':1, 'member':1}
        points = dict()
        lignes = dict()
        objets = dict()
        prn = 1000000
        aff = prn
        for _, elem in ET.iterparse(os.path.join(rep, chemin, fichier)):
            nlignes += 1
            if nlignes == aff:
                print('osm: lignes lues', nlignes, 'objets:', nobj, 'en', int(time.time()-dd0),
                      's (', int(nobj/(time.time()-dd0)), ')o/s')
                aff += prn

            ido, attributs, geom, type_geom, manquants = classif_elem(elem, points, lignes, objets)
            if ido == -1:
                continue
            if type_geom != '0': # analyse des objets et mise en categorie
                obj = _classif_osm(attributs, geom, type_geom, manquants, ido)
                if obj:
                    nobj += 1
                    obj.setorig(nobj)
                    obj.attributs["#chemin"] = chemin
                    self.stock_param.moteur.traite_objet(obj, regle) # on traite le dernier objet
            elem.clear()

        return nobj

READERS = {'osm':(lire_objets_osm, geom_from_osm, True, ())}
WRITERS = {}
