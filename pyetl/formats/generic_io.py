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
import re
import logging
from types import MethodType

# from functools import partial
from .db import DATABASES
from .fichiers import READERS, WRITERS
from .geometrie import GEOMDEF
from .interne.objet import Objet

LOGGER = logging.getLogger("pyetl")
#
# geomdef = namedtuple("geomdef", ("writer", "converter"))
#
# rdef = namedtuple("reader", ("reader", "geom", "has_schema", "auxfiles", "converter", initer))
# wdef = namedtuple("writer", ("writer", "streamer",  "force_schema", "casse",
#                                 "attlen", "driver", "fanout", "geom", "tmp_geom",
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


class Reader(object):
    """wrappers d'entree génériques"""

    databases = DATABASES
    lecteurs = READERS
    geomdef = GEOMDEF

    @staticmethod
    def get_formats():
        """retourne la liste des formats connus"""
        return Reader.lecteurs

    #    auxiliaires = AUXILIAIRES
    #    auxiliaires = {a:AUXILIAIRES.get(a) for a in LECTEURS}

    def __init__(self, nom, regle, regle_start, debug=0):
        self.nom_format = nom
        self.filters = {'in': self.listfilter, '=': self.valuefilter, 're': self.regexfilter}
        self.filter=None
        self.debug = debug
        self.regle = regle  # on separe la regle de lecture de la regle de demarrage
        self.regle_start = regle_start
        self.regle_ref = self.regle if regle is not None else self.regle_start
        stock_param = self.regle_ref.stock_param
        self.maxobj = int(self.regle_ref.getvar("lire_maxi", 0))
        self.traite_objets = stock_param.moteur.traite_objet
        self.schema = None
        self.schema_entree = None
        self.newschema=True
        self.set_format_entree(nom)
        self.nb_lus = 0
        self.lus_fich = 0
        self.groupe = ""
        self.classe = ""
        self.fixe=()
        self.orig = None
        self.affich = 1000
        self.nextaff = self.affich
        self.aff = stock_param.aff
        if self.debug:
            print("debug:format: instance de reader ", nom, self.schema)

    def set_format_entree(self, nom):
        """#positionne un format d'entree"""
        nom = nom.replace(".", "").lower()
        if nom in self.lecteurs:
            #            lire, converter, cree_schema, auxiliaires = self.lecteurs[nom]
            description = self.lecteurs[nom]
            # print ('initialisation reader',description)
            self.description = description
            self.format_natif = description.geom
            self.lire_objets = MethodType(description.reader, self)
            self.nom_format = nom
            self.cree_schema = description.has_schema
            self.auxiliaires = description.auxfiles
            self.converter = description.converter
            self.initer = description.initer
            self.formatters = dict()
            if self.initer:
                self.initer(self)
            self.initfilter()
            stock_param = self.regle_ref.stock_param
            self.schema_entree = stock_param.schemas.get(
                self.regle_ref.getvar("schema_entree")
            )
            self.nomschema = ""
            nom_schema_entree = self.regle_ref.getvar("schema_entree")
            if nom_schema_entree:
                if nom_schema_entree.startswith("#"):
                    self.schema_entree = stock_param.schemas.get(nom_schema_entree)
                    nom_schema_entree = nom_schema_entree[1:]
                elif "#" + nom_schema_entree in stock_param.schemas:
                    self.schema_entree = stock_param.schemas["#" + nom_schema_entree]
                else:
                    cod_csv = self.regle_ref.getvar("codec_csv")
                    self.schema_entree = stock_param.lire_schemas_multiples(
                        nom_schema_entree, nom_schema_entree, cod_csv=cod_csv
                    )
                    if self.schema_entree:
                        self.schema_entree.nom = "#" + nom_schema_entree
                        stock_param.schemas[
                            "#" + nom_schema_entree
                        ] = self.schema_entree

                if self.schema_entree:  # on cree un schema stable
                    self.nomschema = nom_schema_entree
                    self.schema = stock_param.init_schema(
                        self.nomschema, "L"
                    )  # et un schema pour les objets
            else:
                nomschema = self.regle_ref.getvar("autoschema")
                if nomschema:
                    self.nomschema = nomschema
                    self.schema = stock_param.init_schema(
                        nomschema, origine="B", stable=False
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
                        stock_param.schemas,
                    )

                    print(
                        "debug:format: lecture format " + nom,
                        self.converter,
                        self.schema,
                    )
        else:
            print("error:format: format entree inconnu", nom)
            raise KeyError

    def setvirtuel(self):
        """positionne un format d'entree virtuel"""
        self.format_natif = "interne"

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

    def prepare_lecture_fichier(self, rep, chemin, fichier, schema=True):
        """prepare les parametres de lecture"""
        regle = self.regle_ref
        self.lus_fich = 0
        self.chemin = chemin
        chem = chemin
        niveaux = []
        while chem:
            chem, nom = os.path.split(chem)
            niveaux.append(nom)
        self.fixe={'#chemin': os.path.abspath(os.path.join(rep,chemin)), '#fichier':fichier}
        groupe = "_".join(niveaux) if niveaux else os.path.basename(rep)
        # print ('prepare lecture',self.fixe)
        if (
            not self.nomschema and self.cree_schema
        ):  # les objets ont un schema issu du fichier
            self.nomschema = os.path.basename(rep) if rep and rep != "." else "schema"
            # self.schema = stock_param.init_schema(self.nomschema, "L")
        # self.aff.send(("initfich", 0, 0))
        classe, regle.ext = os.path.splitext(fichier)
        # print ('prepare_lecture: initfich', groupe,classe)
        # self.setidententree(groupe,classe)
        defchain = [
            "encoding",
            "codec_" + self.nom_format + "_in",
            "codec_" + self.nom_format,
            "codec_entree",
            "defcodec",
        ]
        self.encoding = regle.getchain(defchain, "utf-8-sig")
        sep_chain = [
            "sep",
            "separ" + self.nom_format + "_in",
            "separ" + self.nom_format,
        ]
        self.separ = regle.getchain(sep_chain, ";")

        # self.setidententree(groupe, classe)
        # print('apres setidenttnetree', self.schemaclasse._id)
        self.fichier = os.path.join(rep, chemin, fichier)
        if open(self.fichier, "rb").read(10).startswith(codecs.BOM_UTF8):
            self.encoding = "utf-8-sig"

        self.setidententree(groupe, classe)
        return groupe,classe

    def process(self, obj):
        """renvoie au moteur de traitement"""
        self.traite_objets(obj, self.regle_start)

    def alphaprocess(self,attributs,hdict=None):
        # print ('alphaprocess', self, self.filter)
        obj = self.getobj(attributs=attributs)
        if obj:
            if hdict:
                for nom,dico in hdict.items():
                    obj.sethtext(nom,dico)
            obj.attributs["#type_geom"] = '0'
            self.traite_objets(obj, self.regle_start)
        # else:
        #     print ('rejet')



    def get_info(self):
        """ affichage du format courant : debug """
        print("info :format: format courant :", self.nom_format)

    def get_converter(self, format_natif=None):
        """retourne la fonction de conversion geometrique"""
        if format_natif is None:
            return self.converter
        fgeom = Reader.lecteurs.get(format_natif, Reader.lecteurs["interne"]).geom
        return Reader.geomdef[fgeom].converter

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
        if self.orig==(groupe,classe):
            # print ('retour', (groupe,classe),self.orig,self.groupe,self.classe)
            return # on a rien touche
        if self.schema is None:
            self.schemaclasse = None
        if self.schema_entree:
            # print ('mapping entree', self.schema_entree, self.schema_entree.classes.keys())
            groupe2, classe2 = self.schema_entree.map_dest((groupe, classe))
            # print ('mapping entree',(groupe, classe),'->', (groupe2, classe2))
        else:
            groupe2, classe2 = groupe, classe
            if not self.schema and self.nomschema:
                self.schema = self.regle_ref.stock_param.init_schema(self.nomschema, "L")
        self.groupe = groupe2
        self.classe = classe2
        self.orig = (groupe, classe)
        self.newschema = False
        self.ident = groupe2, classe2
        self.attformatters = None
        # print ('setidententree ', groupe,classe, '->', self.ident, self.schema)
        if self.schema and self.ident in self.schema.classes:  # il existe deja
            self.schemaclasse = self.schema.get_classe(self.ident)
            self.setattformatter()
            # print ('------classe_existe ',self.schemaclasse._id,self.schemaclasse.identclasse)
            return
        if self.schema_entree and self.ident in self.schema_entree.classes:
            modele = self.schema_entree.get_classe(self.ident)
            self.schemaclasse = modele.copy(self.ident, self.schema)
            self.setattformatter()
            # print ('------nouvelle classe ',self.schemaclasse._id, self.schemaclasse.attmap)
            # print ('------controle', self.schema.get_classe(self.ident)._id)
            return
        if self.schema_entree:
            print ('mapping schema_entree impossible',self.ident,'->',self.schema_entree.nom)
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
        else:
            self.attlist = attlist

    def attremap(self, attributs):
        """mappe les attributs par un dictionnaire"""
        return [(self.schemaclasse.attmap.get(i, i), v) for i, v in attributs]

    def initfilter(self):
        readfilter = self.regle_ref.getvar('readfilter')
        if readfilter:
            filterdef = readfilter.split(':',3)
            field,type,vals = filterdef
            if type == 're':
                vals=re.compile(vals)
            elif type == 'in':
                vals = set(i.strip() for i in vals[1:-1].split(','))
            self.filter = self.filters.get(type)
            self.filterfield = field
            self.filtervalue = vals
            # print ('filtrage entree active', readfilter,self, self.filter)

    def valuefilter(self, attributs):
        try:
            return attributs[self.filterfield]==self.filtervalue
        except KeyError:
            return False

    def regexfilter(self, attributs):
        try:
            return self.filtervalue.match(attributs[self.filterfield])
        except KeyError:
            return False

    def listfilter(self, attributs):
        # print ('appel listfilter', attributs[self.filterfield] in self.filtervalue)
        try:
            return attributs[self.filterfield] in self.filtervalue
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
        self.nb_lus += 1
        self.lus_fich += 1
        errs = []
        if self.maxobj and self.lus_fich > self.maxobj:
            self.nb_lus -= 1
            self.lus_fich -= 1
            raise GeneratorExit
        if self.nb_lus >= self.nextaff:
            self.nextaff += self.affich
            self.aff.send(("interm", 0, self.lus_fich))
        # print ('getobj', self.filter, attributs)
        if self.filter and attributs:
            # print ('filter ',self.filter(dict(attributs)))
            if isinstance(attributs, dict):
                if not self.filter(attributs):
                    return None
            else:
                if not self.filter(dict(attributs)):
                # if not self.filter(attributs):
                    return None
        if attributs and self.schemaclasse and self.schemaclasse.attmap:
            # print ('on remappe', self.schemaclasse.attmap)
            attributs = self.attremap(attributs)
        elif valeurs:
            attributs = zip(self.attlist, valeurs)
        if self.attformatters and attributs is not None:
            attributs = dict(attributs)
            for nom in self.attformatters:
                if nom in attributs:
                    try:
                        attributs[nom] = self.attformatters[nom](attributs[nom])
                    except TypeError:
                        errs.append('formattage attribut'+ str(self.ident) +' '+nom+' '+attributs[nom])
                        # print ('erreur de formattage attribut', self.ident, nom, attributs[nom])
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
        # print ('creation obj',obj)
        if errs:
            obj.attributs["#erreurs"]=','.join(errs)
        if self.fixe:
            # print ('fixe', self.fixe)
            obj.attributs.update(self.fixe)
        return obj


class Writer(object):
    """wrappers de sortie génériques"""

    databases = DATABASES
    sorties = WRITERS
    geomdef = GEOMDEF

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
        self.writerparms = dict()  # parametres specifique au format
        # positionne un format de sortie
        nom = nom.replace(".", "").lower()
        if nom in self.sorties:
            self.def_sortie = self.sorties[nom]
        #            ecrire, stream, tmpgeo, schema, casse, taille, driver, fanoutmax,\
        #            nom_format = self.sorties[nom]
        else:
            if nom:
                print("format sortie inconnu '" + nom + "'", self.sorties.keys())
            self.def_sortie = self.sorties["#poubelle"]

        #            ecrire, stream, tmpgeo, schema, casse, taille, driver, fanoutmax, nom_format =\
        #                    self.sorties['#poubelle']
        if nom == "sql":

            if dialecte == "":
                dialecte = "natif"
            else:
                dialecte = dialecte if dialecte in self.databases else "sql"
                self.writerparms["dialecte"] = self.databases[dialecte]
                self.writerparms["base_dest"] = destination
                self.writerparms["destination"] = fich
        else:
            self.writerparms["destination"] = destination
        self.dialecte = dialecte
        self.ecrire_objets = MethodType(self.def_sortie.writer, self)
        self.ecrire_objets_stream = MethodType(self.def_sortie.streamer, self)
        self.geomwriter = self.def_sortie.geomwriter
        self.tmpgeomwriter = self.def_sortie.tmpgeomwriter
        self.calcule_schema = self.def_sortie.force_schema
        self.minmaj = (
            self.def_sortie.casse
        )  # determine si les attributs passent en min ou en maj
        self.driver = self.def_sortie.driver
        self.nom = nom
        self.l_max = self.def_sortie.attlen
        self.ext = "." + nom
        self.multiclasse = self.def_sortie.fanout != "classe"
        self.fanoutmax = self.def_sortie.fanout
        self.schema_sortie = self.regle.getvar("schema_sortie", None)
        self.initer = self.def_sortie.initer
        if self.initer:
            self.initer(self)
            # print('writer : initialisation',nom, self.nom_format, self.def_sortie, self.__dict__)

    def get_info(self):
        """ affichage du format courant : debug """
        print("error:format: format courant :", self.nom_format)

    def get_geomwriter(self, format_natif=None):
        """retourne la fonction de conversion geometrique"""
        if format_natif is None:
            return self.geomdef[self.nom].writer
        fgeom = self.sorties.get(format_natif, Writer.sorties["interne"]).geom
        return self.geomdef[fgeom].writer
