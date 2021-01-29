# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 10:14:31 2019

@author: 89965

gestionaire de formats de traitements
les formats sont enregistres en les mettant dans des fichiers python qui
commencent par format_

"""
import os
import codecs
from pyetl.pyetl import LOGGER
import re
import io
from types import MethodType

# from functools import partial
from .db import DATABASES
from .fichiers import READERS, WRITERS
from .geometrie import GEOMDEF
from .interne.objet import Objet

#
# geomdef = namedtuple("geomdef", ("writer", "converter"))
#
# rdef = namedtuple("reader", ("reader", "geom", "has_schema", "auxfiles", "converter", initer))
# wdef = namedtuple("writer", ("writer", "streamer",  "force_schema", "casse",
#                                 "attlen", "driver", "fanoutmin", "geom", "tmp_geom",
#                                 "geomwriter", tmpgeowriter))
# "database", ("acces", "gensql", "svtyp", "fileext", 'description', "geom", 'converter',
#             "geomwriter"))
#
# assemblage avec les geometries
for nom in WRITERS:
    tmp = WRITERS[nom]
    if tmp.geom:
        WRITERS[nom] = tmp._replace(
            geomwriter=GEOMDEF[tmp.geom].writer,
            tmpgeomwriter=GEOMDEF[tmp.tmp_geom].writer,
        )
#    print ('writer', nom , 'geom', WRITERS[nom].geom, WRITERS[nom].geomwriter)

for nom in READERS:
    tmp = READERS[nom]
    if tmp.geom:
        READERS[nom] = tmp._replace(converter=GEOMDEF[tmp.geom].converter)

for nom in DATABASES:
    tmp = DATABASES[nom]
    if tmp.geom:
        DATABASES[nom] = tmp._replace(
            converter=GEOMDEF[tmp.geom].converter, geomwriter=GEOMDEF[tmp.geom].writer
        )


def get_read_encoding(regle, nom_format):
    defchain = [
        "encoding",
        "codec_" + nom_format + "_in",
        "codec_" + nom_format,
        "codec_entree",
        "defcodec",
    ]
    return regle.getchain(defchain, "utf-8-sig")


def get_read_separ(regle, nom_format):

    sep_chain = ["sep", "separ_" + nom_format + "_in", "separ_" + nom_format]
    return regle.getchain(sep_chain, ";")


class Reader(object):
    """wrappers d'entree génériques"""

    @classmethod
    def get_formats(cls, nature):
        """retourne la liste des formats connus"""
        if nature == "r":
            return READERS
        elif nature == "w":
            return WRITERS
        elif nature == "d":
            return DATABASES

    #    auxiliaires = AUXILIAIRES
    #    auxiliaires = {a:AUXILIAIRES.get(a) for a in LECTEURS}

    def __init__(self, nom, regle, regle_start, debug=0):
        self.nom_format = nom
        self.filters = {
            "in": self.listfilter,
            "=": self.valuefilter,
            "re": self.regexfilter,
        }
        self.filter = None
        self.debug = debug
        self.regle = regle  # on separe la regle de lecture de la regle de demarrage
        self.regle_start = regle_start
        self.regle_ref = self.regle if regle is not None else self.regle_start
        self.stock_param = self.regle_ref.stock_param
        self.maxobj = int(self.regle_ref.getvar("lire_maxi", 0))
        self.traite_objet = self.stock_param.moteur.traite_objet
        self.schema = None
        self.schemaclasse = None
        self.schema_entree = None
        self.newschema = True
        self.set_format_entree(nom)
        self.nb_lus = 0
        self.lus_fich = 0
        self.obj_crees = 0
        self.groupe = ""
        self.classe = ""
        self.fixe = dict()
        self.orig = None
        self.affich = 1000
        self.nextaff = self.affich
        self.aff = self.stock_param.aff
        self.srid = "3948"
        if self.debug:
            print("debug:format: instance de reader ", nom, self.schema)

    def set_format_entree(self, nom):
        """#positionne un format d'entree"""
        nom = nom.replace(".", "").lower()
        if nom in READERS:
            #            lire, converter, cree_schema, auxiliaires = self.lecteurs[nom]
            description = READERS[nom]
            # print ('---initialisation reader',nom ,self.regle_ref)
            self.description = description
            self.format_natif = description.geom
            self.lire_objets = MethodType(description.reader, self)
            # print("objreader", description)
            self.objreader = (
                MethodType(description.objreader, self)
                if description.objreader
                else None
            )
            self.nom_format = nom
            self.cree_schema = description.has_schema
            self.auxiliaires = description.auxfiles
            self.converter = description.converter
            self.initer = description.initer
            self.formatters = dict()
            if self.initer:
                self.initer(self)
            self.initfilter()
            self.nomschema = ""
            schemas = self.stock_param.schemas
            nom_schema_entree = self.regle_ref.getvar("schema_entree")
            # print ('schema_entree', nom_schema_entree, self.regle_ref.context.vlocales)
            if nom_schema_entree:
                if nom_schema_entree.startswith("#"):
                    self.schema_entree = schemas.get(nom_schema_entree)
                    nom_schema_entree = nom_schema_entree[1:]
                elif "#" + nom_schema_entree in schemas:
                    self.schema_entree = schemas["#" + nom_schema_entree]
                else:
                    cod_csv = get_read_encoding(self.regle_ref, "csv")
                    self.schema_entree = self.stock_param.lire_schemas_multiples(
                        nom_schema_entree, nom_schema_entree, cod_csv=cod_csv
                    )
                    if self.schema_entree:
                        self.schema_entree.nom = "#" + nom_schema_entree
                        self.stock_param.schemas[
                            "#" + nom_schema_entree
                        ] = self.schema_entree

                if self.schema_entree:  # on cree un schema stable
                    self.nomschema = nom_schema_entree
                    self.schema = self.stock_param.init_schema(
                        self.nomschema, "L"
                    )  # et un schema pour les objets
                self.stock_param.logger.info(
                    "definition schema_entree %s -> %s",
                    nom_schema_entree,
                    repr(self.schema),
                )
                # print(
                #     "----------------------------definition schema_entree ",
                #     nom_schema_entree,
                #     "->",
                #     self.nomschema,
                #     self.schema,
                # )
            elif self.regle_ref.getvar("autoschema"):
                self.nomschema = self.regle_ref.getvar("autoschema")
                self.schema = self.stock_param.init_schema(
                    self.nomschema, origine="B", stable=False
                )

            if self.debug:
                print(
                    "set format entree: schema entree", self.schema_entree, self.schema
                )
                if self.schema_entree:
                    print(
                        "reader:schema_entree", self.schema_entree.nom, self.nomschema
                    )
                else:
                    print(
                        "reader:pas de schema d'entree",
                        nom,
                        self.regle_ref.getvar("schema_entree"),
                        self.stock_param.schemas,
                    )

                    print(
                        "debug:format: lecture format " + nom,
                        self.converter,
                        self.schema,
                    )
        else:
            print("error:format: format entree inconnu", nom)
            raise KeyError

    def __repr__(self):
        return (
            "Reader "
            + self.nom_format
            + " conv: "
            + repr(self.converter)
            + " sc: "
            + repr(self.schema)
        )

    def getobjvirtuel(
        self, attributs=None, niveau=None, classe=None, geom=None, valeurs=None
    ):

        self.nb_lus += 1
        obj = Objet(
            niveau or self.groupe,
            classe or self.classe,
            format_natif=self.format_natif,
            conversion=self.converter,
            attributs=attributs,
            schema=self.schemaclasse,
            numero=self.nb_lus,
        )
        obj.virtuel = True
        return obj

    def prepare_lecture(self):
        """prepare les parametres de lecture"""
        regle = self.regle_ref
        if self.regle_start is None:
            self.regle_start = self.regle_ref.getgen
        self.lus_fich = 0
        self.obj_crees = 0
        self.chemin = ""
        # possibilite de declencher une macro a l'ouverture d'un fichier
        macro_ouverture = regle.getvar("macro_ouverture")
        variables = regle.getvar("variables_ouverture").split(",")
        if macro_ouverture:
            retour = regle.stock_param.macrorunner(macro_ouverture, retour=variables)
            if retour:
                self.fixe.update(retour)
        if not self.nomschema and self.cree_schema:
            # les objets ont un schema issu du fichier (le format a un schema)
            self.nomschema = "schema"
        self.encoding = get_read_encoding(regle, self.nom_format)
        self.separ = get_read_separ(regle, self.nom_format)
        self.fichier = ""

    def prepare_lecture_fichier(self, rep, chemin, fichier, schema=True, classe=None):
        """prepare les parametres de lecture"""
        regle = self.regle_ref
        self.chemin = chemin
        chem = chemin
        niveaux = []
        while chem:
            chem, nom = os.path.split(chem)
            niveaux.append(nom)
        fich, ext = os.path.splitext(fichier)
        self.fixe = {
            "#chemin": os.path.abspath(os.path.join(rep, chemin)),
            "#fichier": fich,
            "#ext": ext,
        }
        self.prepare_lecture()
        groupe = "_".join(niveaux) if niveaux else os.path.basename(rep)
        # print ('prepare lecture',self.nomschema,self.cree_schema)
        if not self.nomschema and self.cree_schema:
            # les objets ont un schema issu du fichier (le format a un schema)
            self.nomschema = os.path.basename(rep) if rep and rep != "." else "schema"
        # self.aff.send(("initfich", 0, 0))
        regle.ext = ext
        classe = fich if classe is None else classe
        self.fichier = os.path.join(rep, chemin, fichier)
        if open(self.fichier, "rb").read(10).startswith(codecs.BOM_UTF8):
            self.encoding = "utf-8-sig"
        self.setidententree(groupe, classe)
        return groupe, classe

    def transfert_attribut(self, obj):
        "recupere les attributs de l objet initial"
        if self.regle.params.att_sortie.val == "*":
            liste_att = {
                i: j for i, j in obj.attributs.items() if not i.startswith("#")
            }
        else:
            liste_att = {
                i: j
                for i, j in obj.attributs.items()
                if i in self.regle.params.att_sortie.liste
            }
        return liste_att

    def prepare_lecture_att(self, obj, format, schema=True):
        """prepare les parametres de lecture"""
        self.chemin = ""
        self.fixe = {"#format": format}
        self.prepare_lecture()
        if self.regle.params.att_sortie.val:
            self.fixe.update(self.transfert_attribut(obj))
        groupe = None
        classe = None
        oclasse = ""
        cdef = self.regle.params.cmp2.liste
        if len(cdef) == 1:
            classe = cdef[0]
        elif len(cdef) == 2:
            groupe, classe = cdef[:2]
        if groupe is None:
            groupe, oclasse = obj.ident
        if classe is None:
            nat = self.regle.nom_att
            if nat.startswith("#"):
                nat = nat[1:]
            classe = oclasse + "_" + nat
        if not self.nomschema and self.cree_schema:
            # les objets ont un schema issu du fichier (le format a un schema)
            self.nomschema = "schema" + format
        self.fichier = ""
        self.setidententree(groupe, classe)

    def attaccess(self, obj):
        """lance le reader sur un attribut en le traitant comme un buffer texte"""
        self.prepare_lecture_att(obj, self.regle.format)
        with io.StringIO(obj.attributs[self.regle.nom_att]) as ouvert:
            self.objreader(ouvert)

    def process(self, obj):
        """renvoie au moteur de traitement"""
        self.traite_objet(obj, self.regle_start)

    def alphaprocess(self, attributs, hdict=None):
        # print ('alphaprocess', self, self.filter)
        obj = self.getobj(attributs=attributs)
        if obj:
            if hdict:
                for nom, dico in hdict.items():
                    obj.sethtext(nom, dico)
            obj.attributs["#type_geom"] = "0"
            self.traite_objet(obj, self.regle_start)
        # else:
        #     print ('rejet')

    def setvar(self, nom, val):
        """positionne une variable ( en general variables de format par defaut)"""
        self.stock_param.setvar(nom, val)

    def get_info(self):
        """ affichage du format courant : debug """
        # print("info :format: format courant :", self.nom_format)

    def get_converter(self, format_natif=None):
        """retourne la fonction de conversion geometrique"""
        if format_natif is None:
            return self.converter
        fgeom = READERS.get(format_natif, READERS["interne"]).geom
        return GEOMDEF[fgeom].converter

    def setattformatter(self):
        """ gere les formatterurs de type"""
        # print ('setattformatter', self.schemaclasse)
        if self.formatters and any(
            [
                att.type_att in self.formatters
                for att in self.schemaclasse.attributs.values()
            ]
        ):
            self.attformatters = {
                att.nom: self.formatters[att.type_att]
                for att in self.schemaclasse.attributs.values()
                if att.type_att in self.formatters
            }
        # print ('attformatters -> ', self.attformatters)

    def setidententree(self, groupe, classe):
        """positionne les identifiants"""
        if self.orig == (groupe, classe):
            # print ('retour', (groupe,classe),self.orig,self.groupe,self.classe)
            return  # on a rien touche
        if self.schema is None:
            self.schemaclasse = None
        if self.schema_entree:
            # print ('mapping entree', self.schema_entree, self.schema_entree.classes.keys())
            groupe2, classe2 = self.schema_entree.map_dest((groupe, classe))
            # print ('mapping entree',(groupe, classe),'->', (groupe2, classe2))
        else:
            groupe2, classe2 = groupe, classe
            if not self.schema and self.nomschema:
                self.schema = self.regle_ref.stock_param.init_schema(
                    self.nomschema, "L"
                )
        self.groupe = groupe2
        self.classe = classe2
        self.orig = (groupe, classe)
        self.newschema = False
        self.ident = groupe2, classe2
        self.attformatters = None
        # print ('setidententree ', groupe,classe, '->', self.ident, self.nomschema, self.schema)
        if self.schema and self.ident in self.schema.classes:  # il existe deja
            self.schemaclasse = self.schema.get_classe(self.ident)
            self.setattformatter()
            # print ('------classe_existe ',self.schemaclasse._id,self.schemaclasse.identclasse)
            return
        if self.schema_entree:
            modele = self.schema_entree.get_classe(self.ident, guess=1)
            if modele:
                self.schemaclasse = modele.copy(self.ident, self.schema)
                self.setattformatter()
                # print ('------nouvelle classe ',self.schemaclasse._id, self.schemaclasse.attmap)
                # print ('------controle', self.schema.get_classe(self.ident)._id)
                return
            self.stock_param.logger.warning(
                "mapping schema_entree  %s impossible %s",
                self.schema_entree.nom,
                str(self.ident),
            )
            # print(
            #     "mapping schema_entree impossible",
            #     self.ident,
            #     "->",
            #     self.schema_entree.nom,
            # )
        self.newschema = True
        if self.schema:
            self.schemaclasse = self.schema.setdefault_classe(self.ident)
            self.setattformatter()

    def prepare_attlist(self, attlist):
        """prepare une liste de mapping"""
        if self.schemaclasse.attmap:
            self.attlist = [
                self.schemaclasse.attmap.get(i, i if i.startswith("#") else "#" + i)
                for i in attlist
            ]
            unmapped = [i for i in attlist if i.startswith("#")]
            if unmapped:
                self.stock_param.logger.warn("champs non mappés:" + ",".join(unmapped))
                print("-----warning----- champs non mappés:" + ",".join(unmapped))
        else:
            self.attlist = attlist

    def attremap(self, attributs):
        """mappe les attributs par un dictionnaire"""
        return [(self.schemaclasse.attmap.get(i, i), v) for i, v in attributs]

    def initfilter(self):
        """definit un filtre de lecture sur un champs"""
        readfilter = self.regle_ref.getvar("readfilter")
        if readfilter:
            filterdef = readfilter.split(":", 3)
            field, filtertype, vals = filterdef
            if filtertype == "re":
                self.matchfilter = re.compile(vals)
            elif filtertype == "in":
                self.inlist = set(i.strip() for i in vals[1:-1].split(","))
            elif filtertype == "=":
                self.filtervalue = vals
            else:
                raise SyntaxError("definition de filtre inconnue: " + filtertype)
            self.filter = self.filters.get(filtertype)
            self.filterfield = field
            self.stock_param.logger.info("filtrage entree: %s ", readfilter)
            # print("filtrage entree:", readfilter, "->", filtertype)

    def valuefilter(self, attributs):
        try:
            return attributs.get(self.filterfield, "#vide") == self.filtervalue
        except KeyError:
            return False

    def regexfilter(self, attributs):
        try:
            return self.matchfilter.match(attributs.get(self.filterfield, "#vide"))
        except KeyError:
            return False

    def listfilter(self, attributs):
        # print ('appel listfilter', attributs[self.filterfield] in self.filtervalue)
        try:
            return attributs.get(self.filterfield, "#vide") in self.inlist
        except KeyError:
            return False

    def getobj(
        self,
        attributs=None,
        niveau=None,
        classe=None,
        geom=None,
        valeurs=None,
        orig=None,
    ):
        """retourne un objet neuf a envoyer dans le circuit
        cree un objet si on a pas depasse la limite de lecture"""

        errs = []
        if self.maxobj > 0 and self.lus_fich >= self.maxobj:
            raise GeneratorExit
        self.nb_lus += 1
        self.lus_fich += 1
        if self.nb_lus >= self.nextaff:
            self.nextaff += self.affich
            # print(
            #     "envoi",
            #     self.nb_lus,
            #     "(",
            #     self.nextaff,
            #     ")",
            #     self.regle_ref.getvar("_wid"),
            # )
            self.aff.send(("interm", 0, self.nb_lus))

        if attributs and self.schemaclasse and self.schemaclasse.attmap:
            # print ('on remappe', self.schemaclasse.attmap)
            attributs = self.attremap(attributs)
        elif valeurs:
            attributs = zip(self.attlist, valeurs)

        if self.attformatters and attributs is not None:
            attributs = dict(attributs)
            # print ('getobj1b', list(attributs),self.attformatters)
            for nom in self.attformatters:
                if nom in attributs:
                    try:
                        attributs[nom] = self.attformatters[nom](attributs[nom])
                    except TypeError:
                        errs.append(
                            "formattage attribut"
                            + str(self.ident)
                            + " "
                            + nom
                            + " "
                            + attributs[nom]
                        )
                        # print ('erreur de formattage attribut', self.ident, nom, attributs[nom])
        if self.filter and attributs:
            # print ('filter ',self.filter(dict(attributs)))
            if isinstance(attributs, dict):
                if not self.filter(attributs):
                    return None
            else:
                attributs = dict(attributs)
                if not self.filter(dict(attributs)):
                    # if not self.filter(attributs):
                    return None
        # if self.filter:
        #     if not self.filter(attributs):
        #         return None

        obj = Objet(
            niveau or self.groupe,
            classe or self.classe,
            format_natif=self.format_natif,
            conversion=self.converter,
            attributs=attributs,
            schema=self.schemaclasse,
            numero=self.nb_lus,
            orig=self.orig if orig is None else orig,
        )
        if geom:
            # print ('getobj:affectation geometrie',geom)
            obj.attributs["#geom"] = geom
        if errs:
            obj.attributs["#erreurs"] = ",".join(errs)
        if self.fixe:
            # print ('fixe', self.fixe)
            obj.attributs.update(self.fixe)
        if self.maxobj and self.obj_crees == -self.maxobj:
            raise GeneratorExit
        self.obj_crees += 1
        return obj


class Output(object):
    """wrappers de sortie génériques"""

    @classmethod
    def get_formats(cls, nature):
        """retourne la liste des formats connus"""
        if nature == "r":
            return READERS
        elif nature == "w":
            return WRITERS
        elif nature == "d":
            return DATABASES

    def __init__(self, nom, regle, debug=0):
        #        print ('dans writer', nom)

        self.dialecte = None
        destination = ""
        dialecte = ""
        fich = ""
        if ":" in nom:
            defs = nom.split(":")
            #            print ('decoupage writer', nom, defs,nom.split(':'))
            nom = defs[0]
            dialecte = defs[1]
            destination = defs[2] if len(defs) > 2 else ""
            fich = defs[3] if len(defs) > 3 else ""
        self.nom_format = nom
        #        self.destination = destination
        self.regle = regle
        self.debug = debug
        self.liste_att = None
        # positionne un format de sortie
        nom = nom.replace(".", "").lower()
        if nom not in WRITERS:
            if nom:
                LOGGER.error("format sortie inconnu '%s'", nom)
                LOGGER.info("formats existants :")
                LOGGER.info("formats existants : %s", ",".join(WRITERS.keys()))
            # print("format sortie inconnu '" + nom + "'", WRITERS.keys())
            nom = "#poubelle"
        # writer, streamer, force_schema, casse, attlen, driver, fanoutmin, geom, tmp_geom)
        self.writerparms = WRITERS[nom]._asdict()  # parametres specifique au format
        # print("definition output", nom, self.writerparms)
        if nom == "sql":

            if dialecte == "":
                dialecte = "natif"
            else:
                dialecte = dialecte if dialecte in DATABASES else "sql"
                self.writerparms["dialecte"] = DATABASES[dialecte]
                self.writerparms["base_dest"] = destination
                self.writerparms["destination"] = fich
        else:
            self.writerparms["destination"] = destination

        initer = self.writerparms.get("initer")
        if initer:
            initer(self)
        self.writerparms.update(self.regle.writerparms)
        self.dialecte = dialecte
        self.encoding = self.writerparms.get("encoding", "utf-8")
        self.ecrire_objets = (
            MethodType(self.writerparms["writer"], self)
            if self.writerparms["writer"]
            else self.blocwriter
        )
        self.ecrire_objets_stream = (
            MethodType(self.writerparms["streamer"], self)
            if self.writerparms["streamer"]
            else self.streamer
        )
        self.nom = nom
        self.ext = "." + self.writerparms.get("extension",nom)
        self.fanoutmin = self.writerparms["fanoutmin"]
        fanout = self.writerparms.get("fanout", self.fanoutmin)
        if fanout == "no" or fanout == "all":
            self.fanout = self.fanoutmin
        elif fanout == "groupe":
            self.fanout = "classe" if self.fanoutmin == "classe" else "groupe"
        else:
            self.fanout = "classe"
        self.multiclasse = self.fanout != "classe"
        self.schema_sortie = self.regle.getvar("schema_sortie", None)
        self.sorties = self.regle.stock_param.sorties
        # print("fin definition output", nom, self.writerparms)

    def get_info(self):
        """ affichage du format courant : debug """
        print("error:format: format courant :", self.nom_format)

    def get_geomwriter(self, format_natif=None):
        """retourne la fonction de conversion geometrique"""
        if format_natif is None:
            return GEOMDEF[self.nom].writer
        fgeom = WRITERS.get(format_natif, WRITERS["interne"]).geom
        return GEOMDEF[fgeom].writer

    def setvar(self, nom, val):
        """positionne une variable ( en general variables de format par defaut)"""
        self.regle.stock_param.setvar(nom, val)

    def __repr__(self):
        return "writer " + self.nom_format + " nom: " + self.nom

    def getfanout(self, ident, initial=False):
        """determine le mode de fanout"""
        dest = self.writerparms.get("destination")
        if dest == "#print":
            nom = "#print"
            ressource = self.sorties.get_res(self.regle, nom)
            return ressource, nom
        rep_sortie = self.regle.getvar("_sortie")
        groupe, classe = ident

        if self.fanout == "all":
            bfich = dest or "all"
            nom = self.sorties.get_id(rep_sortie, bfich, "", self.ext, nom=dest)
        #            print('nom de fichier sans fanout ', rep_sortie, nfich, nom)
        elif self.fanout == "groupe":
            #            print('csv:recherche fichier',obj.ident,groupe,classe,obj.schema.nom,
            nom = self.sorties.get_id(rep_sortie, groupe, "", self.ext)
        else:
            nom = self.sorties.get_id(rep_sortie, groupe, classe, self.ext)
        # print("getfanout", rep_sortie, self.fanout, groupe, classe, dest, "->", nom)
        ressource = self.sorties.get_res(self.regle, nom)
        return ressource, nom

    def change_ressource(self, obj, initial=False):
        """ change la definition de la ressource utilisee si necessaire"""
        # separ, extension, entete, null, initial=False, geomwriter=None
        ressource, nom = self.getfanout(obj.ident)
        self.srid = obj.geom_v.srid
        if ressource is None:
            if not nom.startswith("#"):
                #            print('creation ',nom,'rep',os.path.abspath(os.path.dirname(nom)))
                os.makedirs(os.path.dirname(nom), exist_ok=True)
            str_w = self.writerclass(nom, schema=obj.schema, regle=self.regle)
            ressource = self.sorties.creres(nom, str_w)
        else:
            ressource.handler.changeclasse(obj.schema)

        #    print ('recup_ressource ressource stream csv' , ressource, nom, ident, ressource.etat, entete)
        self.regle.context.setroot("derniere_sortie", nom)
        return ressource

    def streamer(self, obj, regle, _, attributs=None):
        """ecrit des objets au fil de l'eau.
        dans ce cas les objets ne sont pas stockes,  l'ecriture est effetuee
        a la sortie du pipeline (mode streaming)
        """
        if obj.virtuel:  # on ne traite pas les virtuels
            return
        if regle.dident != obj.ident:
            regle.ressource = self.change_ressource(obj)
            regle.dident = obj.ident
        regle.ressource.write(obj, regle.idregle)
        if obj.geom_v.courbe and obj.schema:
            obj.schema.info["courbe"] = "1"

    def blocwriter(self, regle, _, attributs=None):
        """ecrit un ensemble de fichiers a partir d'un stockage memoire ou temporaire"""

        dident = None
        for groupe in list(regle.stockage.keys()):
            for obj in regle.recupobjets(groupe):  # on parcourt les objets
                if obj.virtuel:  # on ne traite pas les virtuels
                    continue
                if obj.ident != dident:
                    ressource = self.change_ressource(obj)
                    dident = obj.ident
                    regle.ressource = ressource
                ressource.write(obj, regle.idregle)
                # if obj.geom_v.courbe and obj.schema:
                #     obj.schema.info["courbe"] = "1"
