# -*- coding: utf-8 -*-
"""format geojson en lecture et ecriture"""

import os
import json
import codecs

# from this import d

from .fileio import FileWriter


def hasbom(fichier, encoding):
    if open(fichier, "rb").read(10).startswith(codecs.BOM_UTF8):
        return "utf-8-sig"
    return encoding


def init_json(writer):
    """json liste"""
    writer.writerclass = JsonWriter
    writer.writerclass.header = writer.writerclass.listheader


def init_sjson(writer):
    """json mono objet"""
    writer.writerclass = JsonWriter
    writer.writerparms["extension"] = "json"
    writer.writerclass.header = writer.writerclass.singleheader


def init_geojson(writer):
    writer.writerclass = GeoJsonWriter


class JsonWriter(FileWriter):
    """gestionnaire d ecriture au format json"""

    start = True

    def listheader(self, init=None):
        """positionne l'entete"""
        self.ttext = "]\n"  # queue
        return "[\n"

    def singleheader(self, init=None):
        """positionne l'entete"""
        self.ttext = ""  # queue
        return ""

    def changeclasse(self, schemaclasse, attributs=None):
        """ecriture multiclasse on change de schema"""
        self.currentlayer = self.schemaclasse.identclasse
        verbose = (
            self.regle_ref.istrue("verbose")
            if self.regle_ref
            else self.regle.istrue("verbose")
        )
        if verbose:
            logger = (
                self.regle_ref.stock_param.logger
                if self.regle_ref
                else self.regle.stock_param.logger
            )
            logger.info("json schema: %s,%s", repr(schemaclasse), schemaclasse.schema)
        self.liste_att = (
            schemaclasse.get_liste_attributs(liste=attributs)
            if schemaclasse
            else attributs
        )
        if not self.liste_att:
            self.liste_att = schemaclasse.attributs.keys()
        self.hconvert = [
            i
            for i in self.liste_att
            if schemaclasse.attributs.get(i)
            and schemaclasse.attributs.get(i).type_att == "H"
        ]
        if self.hconvert and verbose:
            logger.info(
                "json:trouve hconvert %s %s", repr(self.liste_att), repr(self.hconvert)
            )

    def convert(self, obj):
        """ecriture d objets"""
        liste_att = (
            self.liste_att
            if self.liste_att
            else [i for i in obj.attributs if not i.startswith("#")]
        )
        # raise
        return json.dumps(
            {i: obj.attributs.get(i, "") for i in liste_att},
            ensure_ascii=False,
            indent=4 if self.pp else None,
        )

    def write(self, obj):
        """ecrit un objet"""
        if obj.virtuel:
            return False

        if self.start:
            self.start = False
            self.pp = self.regle.istrue("indent")
        else:
            self.fichier.write(",")
        chaine = self.convert(obj)
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


class GeoJsonWriter(JsonWriter):
    """gestionnaire d ecriture au format geojson"""

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

    def convert(self, obj):
        print("conversion geojson", self.liste_att)

        return obj.__json_if__(self.liste_att)


def lire_objets(self, rep, chemin, fichier):
    """lecture d'un fichier json et stockage des objets en memoire"""
    regle_ref = self.regle if self.regle else self.regle_start
    stock_param = regle_ref.stock_param
    # ouv = None
    obj = None
    codec = regle_ref.getchain(("codec_json", "codec_entree", "codec"), "utf-8-sig")
    entree = os.path.join(rep, chemin, fichier)
    print("lecture objets json", entree, codec)
    stock_param.fichier_courant = os.path.splitext(fichier)[0]
    self.setidententree(chemin, stock_param.fichier_courant)
    codec_lecture = hasbom(entree, codec)
    with open(entree, "r", 65536, encoding=codec_lecture) as ouvert:
        # print(ouvert.read())
        # ouvert.seek(0)
        if codec_lecture == codec:
            return self.objreader(ouvert)
        else:
            contenu = ouvert.read()
            # contenu = contenu.encode("UTF-8").decode(encoding=codec)
            # print("recup contenu", contenu[-100:])
            return self.objreader(contenu)


def readobjs(reader, jsonlist, niveau=None, classe=None, geoif=False):
    n_obj = 0
    for i in jsonlist:
        # print("jsonlist", i)
        if reader.maxobj and n_obj > reader.maxobj:
            break
        if not i:
            continue  # ligne vide
        n_obj += 1
        if n_obj % 100000 == 0:
            print("formats :", reader.fichier, "lecture_objets_json ", n_obj)
        # print("traitement json", niveau, classe, i)
        try:
            obj = reader.getobj(niveau=niveau, classe=classe)
            if geoif:
                obj.from_geo_interface(i)
            else:
                obj.attributs.update([(nom, val) for nom, val in i.items()])
            obj.setorig(n_obj)
            # print("lu objet", obj)
            # print("traitement objet, ", obj.ident, reader.regle_start)
            reader.traite_objet(obj, reader.regle_start)
        except AttributeError:
            n_obj -= 1
            reader.objfail()
            print("json non parsable", niveau, classe, i)
            # raise
            pass


def objreader(self, ouvert):
    n_obj = 0
    obj = None
    try:
        if isinstance(ouvert, str):
            contenu = json.loads(ouvert) if ouvert else []
        elif hasattr(ouvert, "read"):
            contenu = json.load(ouvert)
        else:
            contenu = ouvert
            # print("recup directe", contenu)
    except json.JSONDecodeError as err:
        print(
            "objreader:json non parsable",
            err,
            self.encoding,
            type(ouvert),
            ouvert.read() if hasattr(ouvert, "read") else ouvert,
        )
        raise
        return -1
    # print("lu json", type(contenu), contenu)
    if isinstance(contenu, list):
        # print("lecture liste")
        readobjs(self, contenu)
    elif isinstance(contenu, dict):
        if contenu.get("type") == "FeatureCollection":
            # c'est des objets
            for i in contenu["features"]:
                if self.maxobj and n_obj > self.maxobj:
                    break
                if not i:
                    continue  # ligne vide
                readobjs(self, i, geoif=True)
                # n_obj += 1
                # obj = self.getobj()
                # if n_obj % 100000 == 0:
                #     print("formats :", self.fichier, "lecture_objets_json ", n_obj)
                # # print("traitement json", i)
                # obj.from_geo_interface(i)
                # obj.setorig(n_obj)
                # self.traite_objet(obj, self.regle_start)
        else:  # c est n importe quoi on va essayer d en faire qque chose:
            for ident, value in contenu.items():
                if isinstance(value, dict):  # c est des objets ou des classes
                    for elem, val2 in value.items():
                        if isinstance(val2, list):  # c'est une liste d objets
                            readobjs(self, val2, niveau=ident, classe=elem)
                elif isinstance(value, list):  # c est des objets
                    readobjs(self, value, classe=ident)
                else:
                    print("element non exploitable", ident, type(value), value)


READERS = {
    "json": (lire_objets, None, True, (), None, objreader),
    "geojson": (lire_objets, None, True, (), None, objreader),
}
WRITERS = {
    "json": ("", "", False, "", 0, "", "classe", None, "#tmp", init_json),  # liste json
    "sjson": (
        "",
        "",
        False,
        "",
        0,
        "",
        "classe",
        None,
        "#tmp",
        init_sjson,
    ),  # objet json
    "geojson": ("", "", False, "", 0, "", "classe", None, "#tmp", init_geojson),
}


#########################################################################
