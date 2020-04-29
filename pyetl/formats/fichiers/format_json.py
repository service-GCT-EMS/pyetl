# -*- coding: utf-8 -*-
"""format geojson en lecture et ecriture"""

import os
import json

from .fileio import FileWriter


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
        self.liste_att = schemaclasse.get_liste_attributs(liste=attributs)

    def write(self, obj):
        """ecrit un objet"""
        if obj.virtuel:
            return False
        chaine = obj.__json_if__
        if self.start:
            self.start = False
        else:
            self.fichier.write(",")
        try:
            self.fichier.write(chaine)
        except UnicodeEncodeError:
            chaine = _convertir_objet(obj, ensure_ascii=True)
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


def objreader(self, ouvert):
    n_obj = 0
    obj = None
    contenu = json.load(ouvert)
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
            self.traite_objet(obj, self.regle_start)


def _convertir_objet(obj, ensure_ascii=False):
    """sort un objet json en chaine """

    return ascii(obj.__json_if__) if ensure_ascii else obj.__json_if__


# def _set_liste_attributs(obj, attributs):
#    '''positionne la liste d'attributs a sortir'''
#    obj.liste_attributs = obj.schema.get_liste_attributs(liste=attributs)


def ecrire_objets(self, regle, _, attributs=None, rep_sortie=None):
    """ecrit un ensemble de fichiers json a partir d'un stockage memoire ou temporaire"""

    dident = None
    sorties = regle.stock_param.sorties
    extention = ".json"
    rep_sortie = regle.getvar("_sortie") if rep_sortie is None else rep_sortie
    #    print("csv:ecrire csv", regle.stockage.keys())
    ressource = None
    for groupe in list(regle.stockage.keys()):
        #        nb_cour = 0
        setclasse = regle.fanout != "classe"  # en cas de fanout on precise la classe
        for obj in regle.recupobjets(groupe):
            if obj.ident != dident:

                groupe, classe = obj.ident
                #                if ressource:
                #                    ressource.compte(nb_cour)
                #                    nb_cour = 0
                #                if obj.schema:
                schema_courant = obj.schema
                #                print('schema_courant ', obj.ido, obj.copie, obj.ident, '->',
                #                      obj.schema, obj.virtuel)

                if regle.fanout == "groupe":
                    nom = sorties.get_id(rep_sortie, groupe, "", extention)
                else:
                    nom = sorties.get_id(rep_sortie, groupe, classe, extention)

                #                nom = sorties.get_id(rep_sortie, groupe, classe, extention)
                ressource = sorties.get_res(regle, nom)
                if ressource is None:
                    #                    print ('creation ressource csv' , nom)
                    encoding = regle.getvar("codec_sortie", "utf-8")
                    os.makedirs(os.path.dirname(nom), exist_ok=True)
                    str_w = JsonWriter(
                        nom,
                        schema=schema_courant,
                        encoding=encoding,
                        liste_att=attributs,
                    )
                    sorties.creres(regle, nom, str_w)
                    ressource = sorties.get_res(regle, nom)
                dident = (groupe, classe)
            #                fich = ressource.handler
            obj.classe_is_att = setclasse
            obj.liste_attributs = ressource.handler.liste_att

            ressource.handler.write(obj)
    #            nb_cour += 1
    #        if ressource and nb_cour:
    #            ressource.compte(nb_cour)
    return


def jsonstreamer(self, obj, regle, _, rep_sortie=None):  # ecritures non bufferisees
    """ ecrit des objets json en streaming"""
    sorties = regle.stock_param.sorties
    rep_sortie = regle.getvar("_sortie") if rep_sortie is None else rep_sortie
    extention = "." + self.nom_format
    groupe, classe = obj.ident
    #    print ('json: ecriture ',groupe,classe,obj.schema)
    setclasse = regle.fanout != "classe"  # en cas de fanout on precise la classe

    if obj.ident != regle.dident:
        groupe, classe = obj.ident
        schema_courant = obj.schema
        if regle.fanout == "groupe":
            nom = sorties.get_id(rep_sortie, groupe, "", extention)
        else:
            nom = sorties.get_id(rep_sortie, groupe, classe, extention)
        if not nom:
            print("jsonio erreur sortie", groupe, classe)
            return
        ressource = sorties.get_res(regle, nom)
        if ressource is None:
            #            print ('creation ressource stream csv' , nom,groupe,classe)
            try:
                os.makedirs(os.path.dirname(nom), exist_ok=True)
            except FileNotFoundError:
                print("jsonio erreur sortie", nom)
                return

            str_w = JsonWriter(
                nom,
                schema_courant,
                extention,
                encoding=regle.getvar("codec_sortie", "utf-8"),
            )
            sorties.creres(regle, nom, str_w)
            ressource = sorties.get_res(regle, nom)
        else:
            print("json:changeschema", obj, obj.schema)

            ressource.handler.changeclasse(obj.schema)
        regle.ressource = ressource
        regle.dident = (groupe, classe)
    else:
        schema_courant = obj.schema
    ressource = regle.ressource
    obj.classe_is_att = setclasse

    retour = ressource.handler.write(obj)

    if retour and schema_courant:
        if not schema_courant.info["courbe"] and obj.geom_v.courbe:
            schema_courant.info["courbe"] = "1"


#        ressource.compte(1)
# geomdef = namedtuple("geomdef", ("writer", "converter"))
#
# reader: (reader, geom, has_schema, auxfiles, converter, initer)
# writer: (writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom,
#          geomwriter, tmpgeowriter))
READERS = {
    "json": (lire_objets, None, True, (), None, objreader),
    "geojson": (lire_objets, None, True, (), None, objreader),
}
WRITERS = {
    "json": (
        ecrire_objets,
        jsonstreamer,
        False,
        "",
        0,
        "",
        "classe",
        None,
        "#tmp",
        None,
    ),
    "geojson": (
        ecrire_objets,
        jsonstreamer,
        False,
        "",
        0,
        "",
        "classe",
        None,
        "#tmp",
        None,
    ),
}


#########################################################################
