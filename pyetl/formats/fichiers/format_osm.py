# -*- coding: utf-8 -*-
# formats d'entree sortie
""" format osm """

import os
import time
import xml.etree.cElementTree as ET

# print ('osm start')
# import pyetl.schema as SC

# ewkt ##################################################################
# def parse_ewkb(geometrie,texte):


# lecture de la configuration osm
class DecodeConfigOsm(object):
    """stocke une config de classe"""

    def __init__(self, vals, setups):
        self.atts = []
        self.static = []
        self.schema = None
        self.geom = vals[2]
        self.reader = None
        self.setups = setups
        self.minimal= setups.get("minimal")
        self.niveau = vals[4]
        self.classe = vals[5]
        self.def_classes = vals[3]

        if vals[0] == "*":
            self.getident = self.decode_defaut
            self.liste_classes = None
            self.force_geom = None
        else:
            self.getident = self.decode_classe
            self.clef = vals[0]
            self.sous_clef = vals[1]
            self.geom={int(j) for j in vals[2].split(',')}

            self.liste_classes=None
            self.force_geom = vals[6] if vals[6] else None

            for j in range(7, len(vals)):
                if vals[j]:
                    vl2 = vals[j].split(":")
                    if len(vl2) == 1:
                        self.atts.append((vl2[0], self.clef))
                    elif len(vl2) == 2:
                        if vl2[1][0] == "#":
                            self.static.append((vl2[0], vl2[1][1:]))
                        else:
                            self.atts.append((vl2[0], vl2[1]))

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
                return (self.niveau, "non_classe_" + str(self.geom))
            if "type" in tagdict and tagdict["type"] == "multipolygon":
                return (self.niveau, "non_classe_" + str(self.geom))
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
        incomplet = schemaclasse.copy(idref, None, filiation=False)
        incomplet.groupe = "osm_incomplet"
        self.schema.ajout_classe(incomplet)
        if incomplet.info["type_geom"] == "3":
            incomplet.info["type_geom"] = "2"
            # si l'objet est incomplet on ne peut pas toujours creer un contour
        #            incomplet.attributs['#type_geom'] = '2'
        return self.schema.get_classe(ident)

    def decode_objet(self, tagdict, geom, type_geom, manquants):
        """range l objet dans la bonne classe"""
        #        if len(tagdict)==0:
        #            ident=('non_classe','a_jeter')
        #        else:
        #        if self.geom and type_geom != self.geom:
        #            return None
        ident = self.getident(tagdict)
        if ident is None:
            return None
        idref = ident
        if manquants:  # on separe les objets incomplets
            ident = ("osm_incomplet", ident[1])
        self.reader.setidententree(*ident)
        obj = self.reader.getobj()
        obj.attributs["#geom"] = geom
        obj.attributs["#type_geom"] = type_geom

        if self.force_geom is not None:
            obj.attributs["#type_geom"] = self.force_geom  # on force
        # print ('decodage tags mode minimal:',self.minimal)
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
    decodage = {"1": [], "2": [], "3": []}
    if setups is None:
        setups=dict()
    # print ('setups decodage',setups)
    for conf in open(config_osm, "r").readlines():
        chaine = conf.strip()
        if chaine and chaine[0] != "!":
            valeurs = [j.strip() for j in chaine.split(";")]
            if valeurs[0][0] == "{":  # c'est une definton de groupe
                nom_groupe = valeurs[0].replace("{", "").replace("}", "")
                if nom_groupe not in grouplist:
                    grouplist[nom_groupe] = dict()
                groupe = grouplist[nom_groupe]
                groupe[valeurs[1]] = (valeurs[4], valeurs[5], int(valeurs[2]))
            else:  # c'est une definition standard
                geoms = [j for j in valeurs[2].split(",")] if valeurs[2] else None
                if geoms:
                    for i in geoms:
                        valeurs[2] = i
                        decodage[i].append(DecodeConfigOsm(valeurs,setups))
                else:
                    for i in decodage:
                        valeurs[2] = str(i)
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


def _getmembers(points, lignes, objets, elem):
    """ decodage des structures de type relation  """
    geom = []
    # nodelist = []
    rellist = []
    perdus = 0
    ppt = None
    ferme = False
    membres = None
    for i in elem.iter(tag="member"):
        type_membre = i.get("type")
        if membres and type_membre != membres:
            print ('attention melange de types', membres , '->', type_membre)
        membres = type_membre
        identifiant = i.get("ref")
        if identifiant:
            identifiant =  int(identifiant)
        role = i.get("role")
        if type_membre == "node":
            if identifiant in points:
                # nodelist.append((identifiant, role))
                geom.append((points[identifiant], role))
            else:
                perdus += 1

            # return (geom, perdus, ferme)
        if type_membre == "way":  # c est une multiligne ou un polygone
            ligne, manquants, lferm = lignes.get(i.get("ref"), ("", 0, False))
            ferme = lferm or ferme
            if ligne:
                ppt = ppt or ligne[0]
                geom.append((ligne, role))
                ferme = ferme or ppt == ligne[-1]
                perdus += manquants
            else:
                perdus += 10000
            # return (geom, perdus, ferme)
        if type_membre == "relation":
            if identifiant in objets:
                rellist.append((identifiant, role))
            else:
                perdus += 100000

    return (geom, perdus, ferme)



def _classif_osm(reader, tagdict, geom, type_geom, manquants, ido):
    """ applique les regles de classification a l'objet """
    #    print (' dans classif osm ')
    # print ('avant decodage', tagdict)
    for decodeur in reader.decodage[type_geom]:
        obj = decodeur.decode_objet(tagdict, geom, type_geom, manquants)
        if obj:
            tags = ", ".join(
                ['"' + i + '" => "' + tagdict[i].replace('"', r"\"") + '"' for i in sorted(tagdict)]
            )
            # print ('apres decodage', tags)

            obj.hdict = {"tags": tagdict}
            obj.attributs["tags"] = tags
            obj.attributs["id_osm"] = ido
            if not reader.gestion_doublons: # dans ce cas on a besoin d'une clef primaire
                obj.attributs["gid"] = str(obj.ido)
            obj.geom_v.srid = "4326"
            return obj
    print("classif osm : pas de categorie", str(tagdict).encode("ascii", "ignore"))
    return None


def classif_elem(elem, points, lignes, objets):
    """ classifie un element """
    ignore = {"tag", "nd", "member", "bounds","osm"}
    type_geom = "0"
    manquants = 0
    geom = []
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
        points[int(ido)] = (float(elem.get("lon")), float(elem.get("lat")), 0)
        if attributs:
            type_geom = "1"
            geom = [(points[ido],'node')]
    elif elem.tag == "way":  # lignes
        # lignes[ido] = _getpoints(points, elem)
        lignes[ido] = tuple(int(i.get("ref")) for i in elem.iter(tag="nd"))

        if attributs:
            # ligne, manquants, ferme, _, _ = lignes[ido]
            ligne, manquants, ferme = _getgeom(points, lignes[ido])
            if manquants:
                ferme = False
            if ligne:
                geom = [(ligne, "outer")] if ferme else [(ligne, "way")]
                type_geom = "3" if ferme else "2"
    elif elem.tag == "relation":
        if attributs:
            geom, manquants, ferme = _getmembers(points, lignes, objets, elem)
            if geom:
                type_geom = "3" if ferme else "2"
            else:
                type_geom = "0"
        else:
            print("element perdu", ido)
    else:
        print("tag inconnu", elem.tag)
    return ido, attributs, geom, type_geom, manquants


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
        config_osm_def = os.path.join(os.path.dirname(__file__), "config_osm.csv")
        config_osm = self.regle_ref.getvar("config_osm", config_osm_def)
        self.gestion_doublons = self.regle_ref.getvar("doublons_osm", '1') == '1'
        minitaglist = self.regle_ref.getvar("tags_osm_minimal", '1') == '1'
        setups = {"minimal":minitaglist}
        if not self.regle_ref.getvar("fanout"): # on positionne un fanout approprie par defaut
            self.regle_ref.stock_param.set_param("fanout","classe")
        self.decodage = init_osm(self, config_osm, schema, setups)
        self.id_osm=set() # on initialise une structure de stockage des identifiants
    points = dict()
    lignes = dict()
    objets = dict()
    for _, elem in ET.iterparse(os.path.join(rep, chemin, fichier)):
        ido, attributs, geom, type_geom, manquants = classif_elem(elem, points, lignes, objets)
        if ido == -1:
            continue
        if self.gestion_doublons:
            if int(ido) in self.id_osm:
                continue
            self.id_osm.add(int(ido))
        if type_geom != "0":  # analyse des objets et mise en categorie
            try:
                obj = _classif_osm(self, attributs, geom, type_geom, manquants, ido)
            except StopIteration:
                # print ('osm :stopIteration')
                return
            if obj:
                nobj += 1
                obj.setorig(nobj)
                obj.attributs["#chemin"] = chemin
                stock_param.moteur.traite_objet(obj, self.regle_start)  # on traite le dernier objet
        elem.clear()
    return

READERS = {"osm": (lire_objets_osm, "#osm", True, (), None)}
WRITERS = {}
