# -*- coding: utf-8 -*-
"""format geojson en lecture et ecriture"""

import os
import json

from .fileio import FileWriter


def init_json(writer):
    writer.writerclass = JsonWriter


class JsonWriter(FileWriter):
    """gestionnaire d ecriture au format json"""

    start = True

    def header(self, init=None):
        """positionne l'entete"""
        nom = os.path.splitext(os.path.basename(self.nom))[0]
        self.ttext = "]}\n"  # queue
        return (
            '{\n"type": "FeatureCollection","name": "'
            + nom
            + '",\n'
            + '"crs": { "type": "name", "properties": '
            + '{ "name": "urn:ogc:def:crs:EPSG::'
            + self.srid
            + '" } },\n'
            + '"features": [\n'
        )

    def changeclasse(self, schemaclasse, attributs=None):
        """ ecriture multiclasse on change de schema"""
        #        print ("changeclasse schema:", schemaclasse, schemaclasse.schema)
        self.liste_att = (
            schemaclasse.get_liste_attributs(liste=attributs)
            if schemaclasse
            else attributs
        )

    def write(self, obj):
        """ecrit un objet"""
        if obj.virtuel:
            return True
        chaine = obj.__json_if__(self.liste_att)
        if self.start:
            self.start = False
        else:
            self.fichier.write(",")
        try:
            self.fichier.write(chaine)
        except UnicodeEncodeError:
            chaine = ascii(obj.__json_if__(self.liste_att))
            self.fichier.write(chaine)
            print("chaine illisible", chaine)
            if "source" in obj.attributs:
                print("js : ", obj.attributs["source"])
            print("att:", obj.attributs)
        if chaine[-1] != "\n":
            self.fichier.write("\n")
        return True


def lire_objets(self, rep, chemin, fichier):
    """ lecture d'un fichier json et stockage des objets en memoire"""
    regle_ref = self.regle if self.regle else self.regle_start
    stock_param = regle_ref.stock_param
    # ouv = None
    obj = None
    codec = regle_ref.getvar("codec_entree", "utf-8")
    entree = os.path.join(rep, chemin, fichier)
    stock_param.fichier_courant = os.path.splitext(fichier)[0]
    self.setidententree(chemin, stock_param.fichier_courant)
    with open(entree, "r", 65536, encoding=codec) as ouvert:
        return self.objreader(ouvert)


def readobjs(reader, jsonlist):

    n_obj = 0
    for i in jsonlist:
        # print("jsonlist", i)
        if reader.maxobj and n_obj > reader.maxobj:
            break
        if not i:
            continue  # ligne vide
        n_obj += 1
        obj = reader.getobj()
        if n_obj % 100000 == 0:
            print("formats :", reader.fichier, "lecture_objets_json ", n_obj)
        # print("traitement json", [(nom, str(val)) for nom, val in i.items()])
        obj.attributs.update([(nom, str(val)) for nom, val in i.items()])
        obj.setorig(n_obj)
        # print("lu objet", obj)
        # print("traitement objet, ", reader.regle_start)
        # reader.traite_objet(obj, reader.regle_start)
        reader.regle_start.traite_push.send(obj)


def objreader(self, ouvert):
    n_obj = 0
    obj = None
    contenu = json.load(ouvert)
    # print("lu json", type(contenu), contenu)
    if isinstance(contenu, list):
        readobjs(self, contenu)

    elif isinstance(contenu, dict):
        if contenu.get("type") == "FeatureCollection":
            # c'est des objets
            for i in contenu["features"]:
                if self.maxobj and n_obj > self.maxobj:
                    break
                if not i:
                    continue  # ligne vide
                n_obj += 1
                obj = self.getobj()
                if n_obj % 100000 == 0:
                    print("formats :", self.fichier, "lecture_objets_json ", n_obj)
                # print("traitement json", i)
                obj.from_geo_interface(i)
                obj.setorig(n_obj)
                # self.traite_objet(obj, self.regle_start)
                self.regle_start.traite_push.send(obj)


READERS = {
    "json": (lire_objets, None, True, (), None, objreader),
    "geojson": (lire_objets, None, True, (), None, objreader),
}
WRITERS = {
    "json": ("", "", False, "", 0, "", "classe", None, "#tmp", init_json),
    "geojson": ("", "", False, "", 0, "", "classe", None, "#tmp", init_json),
}


#########################################################################
