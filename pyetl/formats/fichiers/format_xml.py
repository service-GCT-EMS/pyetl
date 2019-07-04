# -*- coding: utf-8 -*-
# formats d'entree sortie
""" format xml en sortie """
import os
import re
import xml.etree.cElementTree as ET
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
        null="",
        writerparms=None,
        liste_att=None,
    ):
        super().__init__(nom, encoding=encoding, schema=schema)

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
                obj.attributs["#geom"],
            )
            geom = ""
        if not geom:
            geom = self.null
        obj.format_natif = "xml"
        obj.attributs["#geom"] = geom
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

def decode_att(nom,type_att,valeur):
    if nom == '[*]':
        typeval = 'dyn'
        type_att = 'T'
        valeur = ''
    elif nom.startswith('['):
        typeval = 'var'
        nom = nom[1:-1]
        valeur = valeur[1:-1]
    else:
        if valeur=='#props':
            typeval='hst'
            type_att='H'
        elif valeur.startswith('#'):
            typeval = 'fixe'
        elif valeur.startswith('['):
            typeval = 'prop'
            valeur = valeur[1:-1]
        else:
            typeval = 'const'
    return nom,type_att,valeur,typeval


def decode_config_xml(config_xml):
    config = dict()
    for conf in open(config_xml, "r").readlines():
        chaine = conf.strip()
        if chaine and chaine[0] != "!":
            defs = [j.strip() for j in chaine.split(";")]
            if len(defs)<9:
                print ('erreur description', defs)
                continue
            parent,groupe,classe, item, selecteur, vselect,nom_att,type_att,valeur = defs[:9]
            nom_att,type_att,valeur,typeval=decode_att(nom_att,type_att,valeur)
            valeurs = (nom_att,type_att,valeur,typeval)
            ident=(groupe,classe)
            if parent in config:
                if item in config[parent]:
                    config[parent][item]['attributs'].append(valeurs)
                else:
                    config[parent][item]={'classe':classe,'groupe':groupe,'select':selecteur,'vselect':vselect,'attributs':[valeurs] }
            else:
                config[parent]={item:{'classe':classe,'groupe':groupe,'select':selecteur,'vselect':vselect,'attributs':[valeurs]}}
    # print ('lecture config',config)
    return config
def qgs_datasourceparser(text):
    vals=re.split(' *\+?[a-z]+=',text)
    keys=re.findall('[a-z]+(?==)',text)
    return zip(keys,vals[1:])

def decode_elem(elem, attributs, hdict, config, fixe):
    # print ('decodage element ', elem.tag, elem.text, elem.items())
    for attr,type_attribut, val,typeval in config:
        if typeval == 'fixe':
            if val == '#text':
                txt = '' if elem.text is None else elem.text
                if type_attribut=="H":
                    tmp=txt.split(" ")
                    hdict[attr] = dict([tuple((i.split("=")+[""])[:2]) for i in tmp if i])
                    # print ("creation hdict",hdict)
                else:
                    attributs[attr]=txt
            else:
                attributs[attr]=fixe[val]
        elif typeval == 'prop':
            attributs[attr]=elem.get(val)
        elif typeval == 'var':
            attributs[elem.get(attr)]=elem.get(val)
        elif typeval == 'hst':
            hdict[attr] = dict(elem.items())
            # print ("creation hdict",hdict,elem.items(),elem.tag,elem.attrib,elem.text)
        elif typeval == 'dyn':
            attributs.update(elem.items())
        elif typeval == 'const':
            attributs[attr]=val

def initschema(schema,config):
    '''cree le schema des donnees'''
    for definition in config.values():
        for subdef in definition.values():
            ident = (subdef['groupe'],subdef['classe'])
            schemaclasse = schema.setdefault_classe(ident)
            for att in subdef['attributs']:
                nom_att,type_att,valeur,typeval = att
                if typeval == 'var' or typeval == 'dyn': #schema dynamique
                    schemaclasse.stable=False
                else:
                    schemaclasse.stocke_attribut(nom_att,type_att)
                    # print ('stockage attribut',schemaclasse.identclasse, nom_att, type_att)
                    # print (schema)


def lire_objets_xml_simple(self, rep, chemin, fichier):
    """ lit les datasources des fichiers qgis"""
    stock_param = self.regle_ref.stock_param
    self.prepare_lecture_fichier(rep, chemin, fichier)
    # nomschema = os.path.splitext(fichier)[0]
    # schema = stock_param.init_schema(nomschema, "F")
    fixe={'#chemin': os.path.join(rep,chemin), '#fichier':fichier}
    if self.nb_lus == 0: # initialisation lecteur
        self.config = decode_config_xml(self.configfile)
        schema = stock_param.init_schema('initial', "F")
        initschema(schema, self.config)
        self.schema = schema
        # print ('decodage_config',schema)
        if not self.regle_ref.getvar("fanout"): # on positionne un fanout approprie par defaut
            self.regle_ref.stock_param.set_param("fanout","classe")
    base = ET.parse(os.path.join(rep, chemin, fichier))
    for elem in base.iter():
        if elem.tag in self.config: #parent
            fixe['#parent'] = elem.tag
            # print ('parsing',elem.tag,elem.text)
            config = self.config[elem.tag]
            # print ('detecte parent',elem.tag)
            attributs = dict()
            hdict=dict()
            for tag, conf in config.items():
                # groupe,classe,select,vselect,config_att = conf
                # print ('recherche', tag)
                select = conf['select']
                vselect = conf['vselect']
                config_att = conf['attributs']
                for el2 in elem.iter(tag=tag):
                    # print ('traitement',el2.tag,el2.text)
                    if select and el2.get(select)!=vselect:
                        continue
                    decode_elem(el2, attributs, hdict, config_att, fixe)
            if attributs or hdict:
                self.setidententree(conf['groupe'], conf['classe'])
                self.alphaprocess(attributs,hdict=hdict)
    return

def init_qgs(reader):
    config_qgs_def = os.path.join(os.path.dirname(__file__), "config_qgs.csv")
    config_qgs = reader.regle_ref.getvar("config_qgs", config_qgs_def)
    reader.configfile = config_qgs




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

# extension : (fonction de lecture, format graphique, schema, fichiers aux, initialiseur)
READERS = {"xml": (lire_objets_xml, "#gml", False, (), None),
            "qgs": (lire_objets_xml_simple, None, False, (), init_qgs),
            }
# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {"xml": (ecrire_objets_xml, xml_streamer, False, "", 0, "", "groupe", "#gml", "#gml",None)}
