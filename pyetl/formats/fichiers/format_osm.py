# -*- coding: utf-8 -*-
# formats d'entree sortie
""" format osm """

import os
import time
import xml.etree.cElementTree as ET
from collections import defaultdict
# print ('osm start')
# import pyetl.schema as SC

# ewkt ##################################################################
# def parse_ewkb(geometrie,texte):


# lecture de la configuration osm
class DecodeConfigOsm(object):
    """stocke une config de classe
        vals est la ligne de definition dans le fichier de config
        setups est un dictionnaire contenent des config globales"""

    def __init__(self, vals, setups):
        self.atts = []
        self.static = []
        self.tgs = dict()
        self.schema = None
        self.valeur = vals[2]
        self.description = vals
        self.geom = vals[3]
        self.multiobj = '+' in self.geom
        self.geom = self.geom.strip('+')
        self.reader = None
        self.setups = setups
        self.minimal= setups.get("minimal")
        self.niveau = vals[4]
        self.classe = vals[5]
        self.def_classes = self.niveau if self.niveau.startswith('groupes') else ''
        self.conds = dict()
        self.force_geom = vals[6]
        self.multigeom = (vals[7] == '1')
        self.geomrest = None
        self.geomrole = None
        if vals[0] == "*":
            self.getident = self.decode_defaut
            self.liste_classes = None
        else:
            self.getident = self.decode_classe
            self.clef = vals[0]
            self.sous_clef = vals[1]
            self.geom={int(j) for j in self.geom.split(',')}
            self.liste_classes=None
            for j in range(8, len(vals)):
                if vals[j].startswith('G:ref:'):
                    vl2 = vals[j].split(":")
                    self.geomrest, self.geomrole = self.getrefcond(vl2[2])
                    print ('detecte geometrie relation', self.classe, self.geomrest, self.geomrole, self.description)
                elif vals[j].startswith('TG:ref:'):
                    vl2 = vals[j].split(":")
                    self.tgdef(vl2[2],vl2[3],vl2[4])
                elif vals[j]:
                    vl2 = vals[j].split(":")
                    if len(vl2) == 1:
                        self.storeatt(vl2[0], self.clef)
                    elif len(vl2) == 2:
                        self.storeatt(vl2[0], vl2[1])
                    elif len(vl2) == 3: # definition de conditions supplementaires
                        conditions = vl2[2].strip()[1:-1].split(',')
                        self.storeatt(vl2[0], vl2[1])
                        for cond in conditions:
                            tag,val = cond.split('=')
                            self.conds[vl2[0]]=(tag,val)

    def getrefcond(self,geomcond):
        role = None
        geomtype = None
        geomcond = geomcond[1:-1].strip() if geomcond.startswith('{') else geomcond.strip()
        for i in geomcond.split(','):
            if 'role=' in i:
                role = i.split('=')[1]
            if 'type=' in i:
                geomtype = i.split('=')[1]
        return geomtype,role


    def storeatt(self, att, val):
        if val.startswith("#"):
            self.static.append((att, val[1:]))
        else:
            self.atts.append((att, val))

    def tgdef(self,geomcond,att,val):
        self.storeatt(att,val)
        geomtype, self.tgs[att] = self.getrefcond(geomcond)



    def setliste(self, groupes):
        """stocke les listes associees"""
        if self.def_classes:
            liste_classes = groupes.get(self.def_classes, None)
            # print (' choix groupes', self.clef, liste_classes, self.geom)
            self.liste_classes = ({i:(j[0], j[1]) for i, j in liste_classes.items() if j[2] in self.geom }
                if liste_classes
                else None
            )
            # print (' affectation groupes',self.geom, self.liste_classes)


    def init_schema(self, schema_travail):
        """genere le schema des donnees"""
        self.schema = schema_travail

    def decode_defaut(self, tagdict):
        """ range les objets residuels dans les classes par defaut """
        if len(tagdict) == 1:
            if "source" in tagdict or "created_by" in tagdict:
                return ('tmp')
            if "type" in tagdict and tagdict["type"] == "multipolygon":
                return ('tmp')
        return (self.niveau, self.classe)

    def decode_classe(self, tagdict):
        """determine la classe d un objet osm"""
        #        print ('recherche clef',self.clef,tagdict)
        #        if self.geom and type_geom not in self.geom : return False

        if self.clef not in tagdict:
            return None
        if self.sous_clef:
            if self.sous_clef not in tagdict:
                return None
            elif self.liste_classes:
                clef = tagdict[self.clef] + "::" + tagdict[self.sous_clef]
                if clef in self.liste_classes:
                    return self.liste_classes[clef]
                return (self.niveau, self.classe)
        if self.liste_classes:
            if tagdict[self.clef] in self.liste_classes:
                return self.liste_classes[tagdict[self.clef]]
        return (self.niveau, self.classe)

    def get_schema_classe(self, ident, idref):
        """ retourne le schema et le cree si necessaire """
        schem = self.schema.get_classe(ident)
        if schem:
            return schem

        schemaclasse = self.schema.def_classe(idref)
        if self.reader.gestion_doublons:
            schemaclasse.stocke_attribut("id_osm", "EL", index="P:")
        else:
            schemaclasse.stocke_attribut("id_osm", "EL")
            schemaclasse.stocke_attribut("gid", "EL", index="P:")

        for nom, _ in self.atts:
            schemaclasse.stocke_attribut(nom, "T")
        for nom, _ in self.static:
            schemaclasse.stocke_attribut(nom, "T")
        schemaclasse.stocke_attribut("tags", "H")
        #        schemaclasse.stocke_attribut('#all_tags', 'H')
        schemaclasse.info["type_geom"] = self.force_geom if self.force_geom else self.geom
        schemaclasse.multigeom = self.multigeom
        incomplet = schemaclasse.copy(idref, None, filiation=False)
        incomplet.groupe = "osm_incomplet"
        self.schema.ajout_classe(incomplet)
        if incomplet.info["type_geom"] == "3":
            incomplet.info["type_geom"] = "2"
            # si l'objet est incomplet on ne peut pas toujours creer un contour
        #            incomplet.attributs['#type_geom'] = '2'
        return self.schema.get_classe(ident)

    def decode_objet(self, tagdict, geoms, type_geom, manquants, ido, parties, multi):
        """range l objet dans la bonne classe"""
        #        if len(tagdict)==0:
        #            ident=('non_classe','a_jeter')
        #        else:
        #        if self.geom and type_geom != self.geom:
        #            return None
        # print ('recu geom',geoms)
        ident = self.getident(tagdict)
        if ident is None:
            return None
        if multi and not self.multigeom:
            return None
        if ident == 'tmp':
            parties[ido] = tagdict.copy()
            return 0
        idref = ident

        if manquants:  # on separe les objets incomplets
            ident = ("osm_incomplet", ident[1])
        self.reader.setidententree(*ident)
        obj = self.reader.getobj()
        if obj.ident==('osm','om_comm_restriction'):
            print ('obj', obj.ident)
        if self.geomrest: #declaration de geometrie
            # print('geometrie relation', self.geomrest, self.geomrole,self.description, geoms)
            geoms2=[]
            if self.geomrest in geoms:
                for geomdef in geoms[self.geomrest]:
                    geometrie,role = geomdef
                    if self.geomrole != role:
                        continue
                    geoms2.append(geomdef)
            obj.attributs["#geom"] = geoms2
        else:
            obj.attributs["#geom"] = next(iter(geoms.values())) if geoms else []

        obj.attributs["#type_geom"] = self.force_geom if self.force_geom is not None else type_geom  # on force
        # print ('decodage tags mode minimal:',self.minimal, obj.attributs["#type_geom"], self.force_geom)
        for att, tag in self.atts:
            if tag in tagdict:
                obj.attributs[att] = tagdict[tag]
                if self.minimal:
                    del tagdict[tag]

        for att, val in self.static:
            obj.attributs[att] = val

        obj.setschema(self.get_schema_classe(ident, idref))
        # print ('objet osm', obj)
        return obj


def init_osm(reader, config_osm, schema, setups=None):
    """initialisation de la config osm"""
    #    config_osm_def = os.path.join(os.path.dirname(__file__), 'config_osm2.csv')
    #    config_osm = mapper.get_var('config_osm',
    #                                config_osm_def)if mapper is not None else config_osm_def
    #    print('fichier osm ', config_osm)

    #    CONFIGFILE = os.path.join(os.path.dirname(__file__), config_osm)
    grouplist = dict()
    decodage = {"1": [], "2": [], "3": [],'4': []}
    if setups is None:
        setups=dict()
    # print ('setups decodage',setups)
    reader.parties = dict()
    for conf in open(config_osm, "r").readlines():
        chaine = conf.strip()
        if chaine and chaine[0] != "!":
            valeurs = [j.strip() for j in chaine.split(";")]
            if valeurs[0][0] == "{":  # c'est une definton de groupe
                nom_groupe = valeurs[0].replace("{", "").replace("}", "")
                if nom_groupe not in grouplist:
                    grouplist[nom_groupe] = dict()
                groupe = grouplist[nom_groupe]
                groupe[valeurs[1]] = (valeurs[4], valeurs[5], int(valeurs[3]))
            else:  # c'est une definition standard
                geomdefs = [j for j in valeurs[3].strip('+').split(",")] if valeurs[3] else None
                if geomdefs:
                    for i in geomdefs:
                        valeurs[3] = i
                        decodage[i].append(DecodeConfigOsm(valeurs,setups))
                else:
                    for i in decodage:
                        valeurs[3] = str(i).strip('+')
                        decodage[i].append(DecodeConfigOsm(valeurs,setups))
    for i in decodage:
        #    DECODAGE[ii].append(Decodeconfig(['*', '', str(ii)]))
        for conf in decodage[i]:
            conf.setliste(grouplist)
            conf.init_schema(schema)
            conf.reader = reader

    return decodage


# init_osm()


#########################################################################
# format osm
#########################################################################




def _getpoints(points, elem):
    """decodage des structures de type  way
    recupere les points d une ligne et renvoie une liste de points
    retour: geom : liste de points
    ninc : nbre de points perdus
    contour : booleen si la liste est fermee
    pp dp indice des premiers et derniers points de la liste"""
    liste = list([i.get("ref") for i in elem.iter(tag="nd")])
    geom = list([points[i] for i in liste if i in points])
    ninc = len(liste) - len(geom)
    ppt = liste[0]
    dpt = liste[-1]
    contour = ppt == dpt
    return (geom, ninc, contour, ppt, dpt)

def _getplist(elem):
    liste = tuple(int(i.get("ref")) for i in elem.iter(tag="nd"))
    return liste

def _getgeom(points, liste):
    geom = list([points[i] for i in liste if i in points])
    return (geom, len(liste) - len(geom), liste[0] == liste[-1] if liste else False)
#    return _creeliste(points, liste)


def _getmembers(reader, attributs, points, lignes, objets, elem, used):
    """ decodage des structures de type relation  """
    geoms = defaultdict(list)
    membres = defaultdict(list)
    # nodelist = []
    rellist = []
    perdus = 0
    ppt = None
    ferme = False
    type_geom = '0'
    decodeurs = reader.decodage['4']
    # print ('getmembers: decodeurs',decodeurs)
    for i in elem.iter(tag="member"):
        type_membre = i.get("type")
        identifiant = int(i.get("ref"))
        role = i.get("role")
        if type_membre == "relation":
            if identifiant in objets:
                rellist.append((identifiant, role))
            else:
                perdus += 100000
        else:
            membres[type_membre].append((identifiant,role))

    # if len(membres)==1: # objet monotype
    for type_membre in membres:
        geomlist = membres[type_membre]
        if type_membre == 'node':
            if type_geom == '0':
                type_geom='1'
            if type_geom !='1':
                type_geom = '4'
            for identifiant, role in geomlist:
                if identifiant in points:
                # nodelist.append((identifiant, role))
                    used.add(identifiant)
                    geoms[type_membre].append((points[identifiant], role if role else 'node'))
                else:
                    perdus += 1
        elif type_membre == 'way':
            if type_geom == '0':
                type_geom='2'
            if type_geom !='2':
                type_geom = '4'
            for identifiant, role in geomlist:
                ligne = lignes.get(identifiant)
                if ligne:
                    used.add(identifiant)
                    gligne,manquants,lferm = _getgeom(points,ligne)
                    ferme = lferm or ferme
                    ppt = ppt or ligne[0]
                    used.update(ligne)
                    geoms[type_membre].append((gligne, role if role else 'outer'))
                    ferme = ferme or ppt == ligne[-1]
                    perdus += manquants
                else:
                    perdus += 10000
        elif type_membre == "relation":
            type_geom=4
            for identifiant, role in geomlist:
                if identifiant in objets:
                    rellist.append((identifiant, role, type_membre))
                else:
                    perdus += 100000
        else:
            print ('type_membre inconnu', type_membre)
            # return ([],0,False,[],0)
    return (geoms, perdus, ferme, rellist, type_geom)
    # else: # objet multi_type
    #     pass
    #     print ('objet non decode',membres.items(), attributs)
    #     return ([],0,False,[])




def _classif_osm(reader, tagdict, geoms, type_geom, manquants, ido, parties):
    """ applique les regles de classification a l'objet """
    #    print (' dans classif osm ')
    # print ('avant decodage', tagdict, reader.decodage.keys())
    objs = []
    valide = False
    multi = len(geoms)>1
    for decodeur in reader.decodage[type_geom]:
        obj = decodeur.decode_objet(tagdict, geoms, type_geom, manquants, ido, parties, multi)
        valide = valide or obj is not None
        if obj:
            tags = ", ".join(
                ['"' + i + '" => "' + tagdict[i].replace('"', r'\"') + '"' for i in sorted(tagdict)]
            )
            # print ('apres decodage', tags)

            obj.hdict = {"tags": tagdict}
            obj.attributs["tags"] = tags
            obj.attributs["id_osm"] = ido
            if not reader.gestion_doublons: # dans ce cas on a besoin d'une clef primaire
                obj.attributs["gid"] = str(obj.ido)
            obj.geom_v.srid = "4326"
            objs.append(obj)
            if not decodeur.multiobj:
                break
    if not valide:
        print("classif osm : pas de categorie", str(tagdict).encode("ascii", "ignore"))
    return objs


def classif_elem(reader, elem, points, lignes, objets, used):
    """ classifie un element """
    ignore = {"tag", "nd", "member", "bounds","osm"}
    type_geom = "0"
    manquants = 0
    geoms = defaultdict(list)
    if elem.tag in ignore:
        return -1, None, None, None, None
    #        print ('osm:',event,elem.tag,elem.get('id'))
    #    attributs = _gettags(elem)
    attributs = {i.get("k", "undefined"): i.get("v") for i in elem.iter(tag="tag")}
    ido = elem.get("id")
    if ido is None:
        print ('element non identifié', elem)
        return -1, None, None, None, None
    ido = int(ido)
    if elem.tag == "node":
        points[ido] = (float(elem.get("lon")), float(elem.get("lat")))
        if attributs:
            type_geom = "1"
            geoms["node"] = [(points[ido],'node')]
            used.add(ido)
    elif elem.tag == "way":  # lignes
        ldef = tuple(int(i.get("ref")) for i in elem.iter(tag="nd"))

        if attributs:
            used.add(ido)
            used.update(ldef)
            ligne, manquants, ferme = _getgeom(points, ldef)

            if manquants:
                ferme = False
            if ligne:
                geoms["way"] = [(ligne, "outer")] if ferme else [(ligne, "way")]
                type_geom = "3" if ferme else "2"
            lignes[ido] = ldef
    elif elem.tag == "relation":
        geoms, manquants, ferme, rellist, type_geom = _getmembers(reader, attributs, points, lignes, objets, elem,used)
        if type_geom==2 and ferme:
            type_geom=3
        if rellist:
            print('detecte relation',rellist)


    else:
        print("tag inconnu", elem.tag)
    return ido, attributs, geoms, type_geom, manquants


def lire_objets_osm(self, rep, chemin, fichier):
    """lit des objets a partir d'un fichier xml osm"""
    stock_param = self.regle_ref.stock_param
    dd0 = time.time()
    nlignes = 0
    nobj = 0

    self.lus_fich = 0
    nomschema = os.path.splitext(fichier)[0]
    schema = stock_param.init_schema(nomschema, "F")
    if self.nb_lus == 0: # initialisation lecteur
        refrep = os.path.dirname(__file__)
        config_osm_defaut = os.path.join(refrep, "config_osm.csv")
        config_osm_spe = self.regle_ref.getvar("config_osm")
        if config_osm_spe:
            if config_osm_spe.endswith('.csv'): # c'est un fichier absolu
                config_osm = config_osm_spe
            else:
                config_osm = os.path.join(refrep,config_osm_spe+'.csv')
        else:
            config_osm = config_osm_defaut
        self.gestion_doublons = self.regle_ref.getvar("doublons_osm", '1') == '1'
        print ('gestion des doublons osm','activee' if self.gestion_doublons else 'desactivee')
        minitaglist = self.regle_ref.getvar("tags_osm_minimal", '1') == '1' # si 1 on ne stocke que les tags non traites
        setups = {"minimal":minitaglist}
        if not self.regle_ref.getvar("fanout"): # on positionne un fanout approprie par defaut
            self.regle_ref.stock_param.setvar("fanout","classe")
        self.decodage = init_osm(self, config_osm, schema, setups)
    self.id_osm=set() # on initialise une structure de stockage des identifiants
    points = dict()
    lignes = dict()
    objets = dict()
    parties = dict()
    used = set()
    for _, elem in ET.iterparse(os.path.join(rep, chemin, fichier)):
        ido, attributs, geoms, type_geom, manquants = classif_elem(self, elem, points, lignes, objets, used)
        if ido == -1:
            continue
        if self.gestion_doublons:
            if ido in self.id_osm:
                continue
            self.id_osm.add(ido)
        if type_geom != "0":  # analyse des objets et mise en categorie
            try:
                objs = _classif_osm(self, attributs, geoms, type_geom, manquants, ido, parties)
            except StopIteration:
                # print ('osm :stopIteration')
                return
            for obj in objs:
                nobj += 1
                obj.setorig(nobj)
                obj.attributs["#chemin"] = chemin
                if obj.ident==('osm','om_comm_restriction'):
                    print ('obj', obj )
                stock_param.moteur.traite_objet(obj, self.regle_start)  # on traite le dernier objet
        elem.clear()
    print ('parties', len(parties))
    for ideelem in parties:
        if ideelem not in used:
            print ('element non  utilise', idelem, parties(idelem))

    lostpt = set(points.keys()).difference(used)
    print ('points_perdus', len(lostpt))
    lostl = set(lignes.keys()).difference(used)
    print ('lignes_perdues', len(lostl))

    return

READERS = {"osm": (lire_objets_osm, "#osm", True, (), None, None)}
WRITERS = {}
