# -*- coding: utf-8 -*-
# formats d'entree sortie
""" format xml en sortie """
import os
from pyetl.vglobales import DEFCODEC, DEBUG
from .fileio import FileWriter

# raise ImportError
# print ('osm start')
# import pyetl.schema as SC


def ecrire_geom_xml(geomtemplate, geom_v, type_geom, multi, erreurs):
    """ecrit une geometrie en xml (gml)"""
    return ""


class XmlWriter(FileWriter):
    """ gestionnaire des fichiers xml en sortie """

    def __init__(
        self,
        nom,
        schema=None,
        entete="",
        encoding="utf-8",
        liste_fich=None,
        null="",
        writerparms=None,
        liste_att=None,
    ):
        super().__init__(nom, encoding=encoding, liste_fich=liste_fich, schema=schema)

        self.nom = nom
        self.schema = schema
        self.null = null
        self.writerparms = writerparms
        self.entete = entete
        self.liste_atts = liste_att
        template = self.writerparms.get("template") if self.writerparms else None
        self.templates = dict()
        if template:
            self.readtemplate(template)
        self.classes = set()

        self.stats = liste_fich if liste_fich is not None else dict()
        self.encoding = encoding
        self.curtemp = None
        self.curclasse = None

    def header(self, init=1):
        """ preparation de l'entete du fichiersr xml"""
        if not self.entete:
            return ""
        geom = self.separ + "geometrie" + "\n" if self.schema.info["type_geom"] != "0" else "\n"
        return self.separ.join(self.liste_att) + geom

    def readtemplate(self, templatefile, codec=DEFCODEC):
        """lit un fichier de description de template xml"""
        niveau_courant = 0
        blocs = []
        classe = ""
        key = False
        try:
            with open(templatefile, "r", encoding=codec) as fich:
                for i in fich:
                    if i.startswith("!"):
                        if i.startswith("!!"):
                            i = i[1:]
                        else:
                            continue
                    args = i.split(";") + ["", ""]

                    if i.statrswith("xmltemplate"):
                        while blocs:  # on ferme les blocs
                            self.templates[classe].append("</" + blocs.pop() + ">")

                        classe = args[1] if args[1] else "#generique"
                        self.template[classe] = []
                        niveau_courant = 0
                        continue
                    liste = i[:-1].split(";")
                    niveau = 0
                    for element in liste:
                        if not element:
                            niveau += 1
                            continue
                        while niveau < niveau_courant:
                            self.templates[classe].append("</" + blocs.pop() + ">\n")
                            niveau_courant -= 1
                        if niveau > niveau_courant:
                            niveau_courant = niveau
                            if liste[niveau + 1] == "":
                                self.blocs.append(element)
                                self.template[classe].append("<" + element + ">\n")
                                continue
                            self.templates[classe].append("<" + element + " ")
                            key = True
                            continue
                        if key:
                            if element == "#":
                                continue
                            self.templates[classe].append(element + "=")
                            key = False
                        else:
                            key = True
                            if "[" in element:
                                arg = element[1:-1]
                                self.templates[classe].append("=" + arg)
                            else:
                                self.templates[classe].append('"' + element + '"')
                    if not self.templates[classe][-1].endswith("\n"):
                        self.templates[classe].append("/>\n")

            if DEBUG:
                print("chargement template", templatefile)
                print("resultat ", self.templates)
        except FileNotFoundError:
            print("fichier template  introuvable ", templatefile)

    #    print('prechargement csv', stock)

    def changeclasse(self, schemaclasse, attributs=None):
        """ initialise un fichier """
        clef = ".".join(schemaclasse.identclasse)
        self.liste_atts = attributs
        self.schema = schemaclasse
        self.curtemp = self.templates.get(clef, self.templates.get("#generique", []))

    def write(self, obj):
        """ecrit un objet"""
        if obj.virtuel:
            return False  #  les objets virtuels ne sont pas sortis
        template = self.curtemp

        for i in template:
            if i.startswith("="):
                val = obj.attributs.get(i[1], "")
                self.fichier.write('"' + val + '" ')
            else:
                self.fichier.write(i)

        if obj.initgeom():
            if self.type_geom:
                geom = ecrire_geom_xml(
                    self.tempates, obj.geom_v, self.type_geom, self.multi, obj.erreurs
                )
        else:
            print(
                "xml: geometrie invalide : erreur geometrique",
                obj.ident,
                obj.numobj,
                obj.geom_v.erreurs.errs,
                obj.attributs["#type_geom"],
                self.schema.info["type_geom"],
                obj.geom,
            )
            geom = ""
        if not geom:
            geom = self.null
        obj.format_natif = "xml"
        obj.geom = geom
        obj.geomnatif = True
        if obj.erreurs and obj.erreurs.actif == 2:
            print(
                "error: writer xml :",
                obj.ident,
                obj.ido,
                "erreur geometrique",
                obj.attributs["#type_geom"],
                self.schema.identclasse,
                obj.schema.info["type_geom"],
                obj.erreurs.errs,
            )
            return False
        self.stats[self.nom] += 1
        return True


def get_ressource(obj, regle, attributs=None):
    """ recupere une ressource en fonction du fanout"""
    groupe, classe = obj.ident
    sorties = regle.stock_param.sorties
    rep_sortie = regle.getvar("_sortie")
    if not rep_sortie:
        raise NotADirectoryError("repertoire de sortie non défini")
    if regle.fanout == "no":
        nom = sorties.get_id(rep_sortie, "all", "", ".xml")
    if regle.fanout == "groupe":
        nom = sorties.get_id(rep_sortie, groupe, "", ".xml")
    else:
        nom = sorties.get_id(rep_sortie, groupe, classe, ".xml")

    ressource = sorties.get_res(regle.numero, nom)
    if ressource is None:
        if os.path.dirname(nom):
            os.makedirs(os.path.dirname(nom), exist_ok=True)
        #            print ('ascstr:creation liste',attributs)
        streamwriter = XmlWriter(
            nom,
            encoding=regle.getvar("codec_sortie", "utf-8"),
            liste_att=attributs,
            liste_fich=regle.stock_param.liste_fich,
            schema=obj.schema,
        )
        ressource = sorties.creres(regle.numero, nom, streamwriter)
        ressource.handler.changeclasse(obj.schema, attributs)
    else:
        ressource.handler.changeclasse(obj.schema, attributs)
    regle.ressource = ressource
    regle.dident = obj.ident

    return ressource


def lire_objets_xml(self, rep, chemin, fichier):
    """lecture xml non implemente"""
    return


def xml_streamer(self, obj, regle, _, attributs=None):
    """ecrit des objets en xml au fil de l'eau.
        dans ce cas les objets ne sont pas stockes,  l'ecriture est effetuee
        a la sortie du pipeline (mode streaming)
    """
    if obj.virtuel:  # on ne traite pas les virtuels
        return
    # raise
    if obj.ident == regle.dident:
        ressource = regle.ressource
    else:
        ressource = get_ressource(obj, regle, attributs=None)
    ressource.write(obj, regle.numero)


def ecrire_objets_xml(self, regle, _, attributs=None):
    """ecrit un ensemble de fichiers xml a partir d'un stockage memoire ou temporaire"""
    # ng, nf = 0, 0
    # memoire = defs.stockage
    #    print( "ecrire_objets asc")
    numero = regle.numero
    dident = None
    ressource = None
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):  # on parcourt les objets
            if obj.virtuel:  # on ne stocke pas les virtuels
                continue
            ident = obj.ident
            if ident != dident:
                ressource = get_ressource(obj, regle, attributs=None)
                dident = ident
            ressource.write(obj, numero)


READERS = {"xml": (lire_objets_xml, "#gml", False, ())}
# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {"xml": (ecrire_objets_xml, xml_streamer, False, "", 0, "", "groupe", "#gml", "#gml")}
