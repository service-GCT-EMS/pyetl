# -*- coding: utf-8 -*-
""" format asc en lecture et ectiture"""

import os

# import time
# from numba import jit
import logging

from .fileio import FileWriter

# import pyetl.schema as SC


# formats geometriques ######
FC = 1000.0  # ajoute les elements d'entete a un objet
FA = 10.0
LOGGER = logging.getLogger("pyetl")


# formats complets
####################################################################################
#### traitement  format asc
####################################################################################


def _decode_dates_apic(chaine):
    """ decode une date au format apic"""
    dates = chaine.split(",")

    if len(dates) == 4:
        dat_cre = " ".join(dates[:2]).strip()
        dat_mod = " ".join(dates[2:4]).strip()
    elif len(dates) == 3:  # une seule date
        if dates[0] == "":
            dat_cre = ""
            dat_mod = " ".join(dates[1:2]).strip()
        else:
            dat_cre = " ".join(dates[:2]).strip()
            dat_mod = ""
    elif len(dates) == 2:  # une seule date partielle
        if dates[0] == "":
            dat_cre = ""
            dat_mod = dates[1].strip()
        else:
            if ":" in dates[1]:
                dat_cre = " ".join(dates[:2]).strip()
                dat_mod = ""
            else:
                dat_cre = dates[0].strip()
                dat_mod = dates[1].strip()
    else:
        dat_cre = ""
        dat_mod = ""

    return dat_cre, dat_mod


def _point_apic(liste_elt, log_erreurs):
    """positionne une geometrie de point et des parties d'entete """
    types_geom = {"3": "1", "5": "0", "6": "1", "9": "2"}
    type_geom = "0"
    dim = "2"
    angle = "0"
    erreurs = ''

    type_geom_asc = liste_elt[0][0]
    classe = liste_elt[1].strip()
    index = liste_elt[2].strip()

    coords = []
    try:
        type_geom = types_geom[type_geom_asc]
        # obj.geomnatif = False
        if type_geom_asc == "3":
            coords = [float(liste_elt[3]) / FC, float(liste_elt[4]) / FC, 0]
            angle = 90 - round(float(liste_elt[5]) / FA, 1)
            # obj.geom_v.setpoint([cd_x, cd_y, 0], angle, 2)

        elif type_geom_asc == "6":
            coords = [
                float(liste_elt[3]) / FC,
                float(liste_elt[4]) / FC,
                float(liste_elt[5]) / FC,
            ]
            angle = 90 - round(float(liste_elt[6]) / FA, 1)  # point 3D
            # obj.geom_v.setpoint([cd_x, cd_y, cd_z], angle, 3)
            dim = "3"
    except ValueError:
        # obj.attributs["#erreurs"] = "erreur lecture entete"
        # log_erreurs.send(obj.ident)
        erreurs = "erreur lecture entete"
    return index, type_geom, dim, angle, coords, erreurs


def _decode_entete_asc(entete, log_erreurs):
    """decode l'entete apic"""
    types_geom = {"3": "1", "5": "0", "6": "1", "9": "2"}
    type_geom = "0"
    dim = 2
    angle = "0"
    erreurs = ""
    liste1 = entete.split(";")
    liste_elt = liste1[1].split(",")
    gid = liste_elt[0][2:].strip()  # gid
    if len(liste_elt) < 3:
        print("asc:erreur point ", liste1[0])
    type_geom_asc = liste_elt[0][0]
    classe = liste_elt[1].strip()
    index = liste_elt[2].strip()
    coords = []
    try:
        type_geom = types_geom[type_geom_asc]
        # obj.geomnatif = False
        if type_geom_asc == "3":
            coords = [float(liste_elt[3]) / FC, float(liste_elt[4]) / FC, 0]
            angle = 90 - round(float(liste_elt[5]) / FA, 1)
            # obj.geom_v.setpoint([cd_x, cd_y, 0], angle, 2)

        elif type_geom_asc == "6":
            coords = [
                float(liste_elt[3]) / FC,
                float(liste_elt[4]) / FC,
                float(liste_elt[5]) / FC,
            ]
            angle = 90 - round(float(liste_elt[6]) / FA, 1)  # point 3D
            # obj.geom_v.setpoint([cd_x, cd_y, cd_z], angle, 3)
            dim = 3
    except ValueError:
        # obj.attributs["#erreurs"] = "erreur lecture entete"
        log_erreurs.send(classe)
        erreurs = "erreur lecture entete"

    # index, type_geom, dim, angle = _point_apic(obj, liste_elt, log_erreurs)
    dat_cre, dat_mod = _decode_dates_apic(liste1[2])

    attributs = {
        "#gid": gid,
        "#clef": index,
        "#type_geom": type_geom,
        "#dimension": str(dim),
        "#_sys_date_cre": dat_cre,
        "#_sys_date_mod": dat_mod,
        "#complement": ";".join(liste1[3:-1]),
        "#angle": str(angle),
        "#erreurs": erreurs,
    }
    return classe, attributs, coords, angle, dim


def _erreurs_entete():
    """cumul des erreurs d'entete et affichage"""
    classe_courante = ""
    #    classe='1'
    nb_err = 0
    while True:
        classe = yield
        if classe_courante and classe_courante != classe:
            LOGGER.error(
                "asc  : erreurs entetes : "
                + str(nb_err)
                + " sur la classe "
                + classe_courante
            )
            #            print('error: asc  : erreurs entetes :', nb_err, 'sur la classe ', classe_courante)
            nb_err = 0
            classe_courante = classe
        nb_err += 1
    return

    # print obj.attributs
def traite_booleen(vatt):
    ''' traitement des booleens '''
    bcode = {"-1": "t", "0": "f", "t": "t", "f": "f"}
    # print("asc: traitement booleen")
    try:
        vatt = bcode[vatt]
    except KeyError:
        # print("erreur booleen ", vatt)
        raise TypeError
    return vatt

# entree sortie en asc
# @jit
def ajout_attribut_asc(attributs, attr):
    """decodage d'un attribut asc et stockage"""
    code = attr[0]
    suite = False
    liste_elts = attr.split(",", 2)  # les 2 premiers suffisent en general
    nom = liste_elts[0][1:]
    vatt =''
    type_att = "A"
    # if obj.schema:
    #     if nom in obj.schema.attmap:
    #         nom = obj.schema.attmap[nom].nom
    #     elif nom not in obj.schema.attributs:
    #         if obj.schema.schema.origine == "B":  # c'est un schema autogenere
    #             obj.schema.stocke_attribut(nom, "A")
    #         else:
    #             nom = "#" + nom
    #     type_att = obj.schema.attributs[nom].type_att
    if code == "2":
        code_att = liste_elts[1][0:2]
        long_attrib = int(liste_elts[1][2:])
        if code_att == "NG":
            # vl = ', '.join(l[2:])
            vatt = liste_elts[2][0:long_attrib]
            suite = len(vatt) < long_attrib

        elif code_att == "TL":
            # obj.text_graph[liste_elts[0][1:]] = liste_elts[2:-1]  # texte_graphique
            nom_x = nom + "_X"
            nom_y = nom + "_Y"
            # obj.tg_coords[nom_x] = 1
            # obj.tg_coords[nom_y] = 1
            liste_elts = attr.split(",")  # d on decode plus loin
            #            try:
            attributs[nom_x] = str(float(liste_elts[2]) / FC)
            attributs[nom_y] = str(float(liste_elts[3]) / FC)
            #            except ValueError:
            #                print("error: asc  : texte graphique incorrect", liste_elts)
            texte_candidat = ",".join(liste_elts[7:])
            vatt = texte_candidat[0:long_attrib]
        elif code_att == "CT":  # texte symbolique (recupere en texte)
            liste_elts = attr.split(",")  # d on decode plus loin
            vatt = liste_elts[6]
        else:
            print("error: asc  : lecture_asc code inconnu ", code_att, attr)
    elif code == "4":
        #        print('detection code etat ', obj.ident, liste_elts)
        # if obj.etats is None:
        #     obj.etats = dict()
        # obj.etats[liste_elts[0][1:]] = liste_elts[1][:-1]  # code etat
        vatt = liste_elts[1][:-1]
        nom = "#_sys_E_" + liste_elts[0][1:]
    else:
        print("error: asc  : code inconnu", liste_elts)

    attributs[nom] = vatt
    return nom, suite
    # print l, l[-1].strip()
    # print 1/0


def init_format_asc(reader):
    '''positionnne des elements de lecture (traitement des booleens)'''
    reader.formatters['B'] = traite_booleen
    reader.setvar('codec_asc','cp1252')
    # print ('initialisation reader', reader.formatters)
    # raise

# def _get_schemas(regle, rep, fichier):
#     """definit le schemas de reference et les elementt immuables """
#     schema = None
#     schema_init = None
#     stock_param = regle.stock_param
#     stock_param.fichier_courant = os.path.splitext(fichier)[0]
#     if regle.getvar("schema_entree"):
#         schema = regle.getschema(regle.getvar("schema_entree"))
#         schema_init = schema
#     else:
#         if regle.getvar("autoschema"):
#             schema = stock_param.init_schema(
#                 rep, origine="B", fich=fichier, stable=False
#             )
#     return schema, schema_init

def finalise_obj(reader, attributs, coords, geom, angle, dim):
    '''finalise un objet et le traite'''
    obj = reader.getobj(attributs=attributs, geom=geom) if attributs or geom else None
    if obj is None: # filtrage en entree
        return
    if coords:
        obj.geom_v.setpoint(coords, angle, dim)
    if geom:
        obj.attributs["#dimension"] = "3" if geom[0].find("3D") else "2"
    if obj.dimension == 0:
        print ('asc: erreur finalisation ', obj, coords, geom, dim)
    reader.process(obj)



def lire_objets_asc(self, rep, chemin, fichier):
    """ lecture d'un fichier asc et stockage des objets en memoire"""
    obj = None
    nom = ''
    attributs = dict()
    geom = []
    coords = []
    angle = 0
    dim = 2
    groupe,dclasse = self.prepare_lecture_fichier(rep, chemin, fichier)
    #    print ('lire_asc ', schema, schema_init)
    #    print('asc:entree', fichier)
    log_erreurs = _erreurs_entete()
    next(log_erreurs)
    # dclasse = classe
    with open(
        self.fichier, "r", 65536, encoding=self.encoding, errors="backslashreplace"
    ) as ouvert:
        suite = False
        if not chemin:
            chemin = os.path.basename(rep)
        for i in ouvert:
            if suite:
                # suite, nom = complete_attribut(attributs, nom, i)
                attributs[nom] += i
                suite = False
                continue
            if len(i) <= 2 or i.startswith("*") or i.startswith(';4'):
                continue
            code_0, code_1 = i[0], i[1]
            if code_0 == ";" and code_1.isnumeric():
                # print ('asc lecture', i)
                finalise_obj(self, attributs, coords, geom, angle, dim)
                geom=[]

                if code_1 in "9356":
                    classe, attributs, coords, angle, dim = _decode_entete_asc(i, log_erreurs)
                    if classe != dclasse:
                        self.setidententree(groupe,classe)
                        dclasse = classe

            elif (code_0 == "2" or code_0 == "4") and (
                code_1.isalpha() or code_1 == "_"
            ):
                nom, suite = ajout_attribut_asc(attributs, i)
            elif i.startswith("FIN"):
                continue
            else:
                geom.append(i)
        finalise_obj(self, attributs, coords, geom, angle, dim)
        log_erreurs.send("")
    return


def _ecrire_point_asc(geom):
    """retourne un point pour l'entete"""

    dim = geom.dimension
    angle = (90 - geom.angle) % 360 if geom.angle is not None else 0
    angle = round(angle*FA)
    try:
        if dim == 2:
            ccx, ccy = list(geom.coords)[0][:2]
            code = ";3 "
            chaine = ",".join(
                ("", "%d" % (ccx * FC), "%d" % (ccy * FC), "%d" % (angle))
            )
        else:
            ccx, ccy, ccz = list(geom.coords)[0][:3]
            code = ";6 "
            chaine = ",".join(
                (
                    "",
                    "%d" % (ccx * FC),
                    "%d" % (ccy * FC),
                    "%d" % (ccz * FC),
                    "%d" % (angle),
                )
            )
        return code, chaine
    except ValueError:
        print("erreur ecriture point", geom.coords, dim)
        return ';0 ',""


def format_date(date):
    """ genere une date en format entete elyx"""
    return (
        date.replace("/", "-").replace(" ", ",").split(".")[0]
        if date
        else ""
    )


def _ecrire_entete_asc(obj) ->str:
    """ genere le texte d'entete asc a partir d'un objet en memoire"""
    types_geom_asc = {"0": ";5 ", "1": "3", "2": ";9 ", "3": ";9 "}
    type_geom_sortie = ";5 "
    attr = obj.attributs
    try:
        id_num = attr["#gid"]
    except KeyError:
        id_num = str(obj.ido)

    classe = attr["#classe"].upper()
    if "#clef" in classe:
        index = attr.get("#clef")
    else:
        index = " "
    #    print ("entete asc ",obj.attributs)
    type_geom = obj.attributs["#type_geom"]
    if type_geom != "0":
        if obj.initgeom():
            type_geom_sortie = types_geom_asc.get(type_geom, ";5 ")
        else:
            print("geometrie asc invalide ", id_num, obj.attributs["#geom"], obj.geom_v.erreurs, obj)
            type_geom_sortie = ";5 "

    dcre = format_date(attr.get("#_sys_date_cre"))
    dmod = format_date(attr.get("#_sys_date_mod"))
    fin_ent = ";" + dcre + "," + dmod + ";" + attr.get("#complement", "")
    idobj = id_num + "," + classe + "," + index
    if fin_ent[-1] == "\n":
        fin_ent = fin_ent[:-1]

    if type_geom_sortie == "3":

        code, chaine = _ecrire_point_asc(obj.geom_v)
        entete = code + idobj + chaine + fin_ent + ";\n"
    else:
        entete = type_geom_sortie + idobj + fin_ent + ";\n"
    return entete


class AscWriter(FileWriter):
    """ gestionnaire d'ecriture pour fichiers asc"""

    def __init__(
        self, nom, liste_att=None, encoding="cp1252", schema=None, geomwriter=None
    ):
        super().__init__(
            nom,
            liste_att=liste_att,
            converter=self._convertir_objet_asc,
            encoding=encoding,
            schema=schema,
            geomwriter=geomwriter,
        )
        self.htext = "*****\n** sortie_mapper\n*****\n"
        self.ttext = "FIN\n"
        self.transtable = str.maketrans({"\n": "\\" + "n", "\r": ""})
        self.liste_graphique = None
        self.liste_ordinaire = None

    def changeclasse(self, schemaclasse, attributs=None):
        """ ecriture multiclasse on change de schema"""
        #        print ("changeclasse schema:", schemaclasse, schemaclasse.schema)
        if attributs:
            self.liste_att = set(attributs)
        elif schemaclasse:
            self.liste_att = schemaclasse.get_liste_attributs(liste=attributs)
            self.liste_graphique = {
                i for i in self.liste_att if schemaclasse.attributs[i].graphique
            }
            if self.liste_graphique:
                self.liste_ordinaire = {
                    i for i in self.liste_att if i not in self.liste_graphique
                }
            else:
                self.liste_ordinaire = set(self.liste_att)

    def _convertir_objet_asc(self, obj, liste, transtable=None):
        """sort un objet asc en chaine """

        entete = _ecrire_entete_asc(obj)
        #    attributs = obj.attributs[:]
        if (
            obj.format_natif == "asc" and obj.geomnatif
        ):  # on a pas touche a la geometrie
            #        print ('natif asc')
            if obj.geom:
                geometrie = "".join(obj.geom)
            else:
                geometrie = ""
        else:
            geometrie = self.geomwriter(obj.geom_v)

        attmap = obj.schema.attmap if obj.schema else dict()
        #    print "ecriture", liste
        tliste = list()
        eliste = list()
        if liste is None:
            liste = [i for i in obj.attributs if i[0] != "#"]

        a_sortir = [i for i in liste if i in obj.attributs and obj.attributs[i]]

        #    print('asc  attributs',liste)
        #    aliste = (i for i in a_sortir if i not in obj.text_graph and i not in obj.tg_coords)
        aliste = (
            (attmap.get(i, i).upper(), str(obj.attributs[i]).translate(transtable))
            for i in a_sortir
            if i not in obj.text_graph and i not in obj.tg_coords
        )
        if obj.text_graph:
            tliste = (
                (i, str(obj.attributs[i]).translate(transtable))
                for i in a_sortir
                if i in obj.text_graph
            )
        if obj.etats:
            eliste = (i for i in a_sortir if i in obj.etats)

        #    attlist = "\n".join(("2"+attmap.get(i, i).upper()+
        #                             ",NG"+str(len(str(obj.attributs[i])))+","+
        #                         str(obj.attributs[i])+";" for i in aliste))
        attlist = "\n".join(
            ("2" + i + ",NG" + str(len(j)) + "," + j + ";" for i, j in aliste)
        )

        if tliste:
            tglist = "\n".join(
                (
                    "2"
                    + attmap.get(i, i).upper()
                    + ",TL"
                    + str(len(j))
                    + ","
                    + str(int(float(obj.attributs[i + "_X"]) * FC))
                    + ","
                    + str(int(float(obj.attributs[i + "_Y"]) * FC))
                    + ","
                    + ",".join(obj.text_graph[i])
                    + ","
                    + j
                    + ";"
                    for i, j in tliste
                )
            )
            attlist = attlist + "\n" + tglist
        if eliste:
            elist = "\n".join(
                (
                    "4"
                    + attmap.get(i, i).upper()
                    + ","
                    + str(obj.attributs.get("#_sys_E_" + i), "")
                    + ";"
                    for i in eliste
                )
            )
            attlist = attlist + "\n" + elist

        return entete + geometrie + attlist


def asc_streamer(self, obj, regle, _, attributs=None):
    """ecrit des objets asc au fil de l'eau.
        dans ce cas les objets ne sont pas stockes,  l'ecriture est effetuee
        a la sortie du pipeline (mode streaming)
    """
    if obj.virtuel:  # on ne traite pas les virtuels
        return
    # raise
    rep_sortie = regle.getvar("_sortie")
    if not rep_sortie:
        raise NotADirectoryError("repertoire de sortie non défini")
    #    print('asc:', obj.ident,regle.dident, 'sortie:', rep_sortie)

    sorties = regle.stock_param.sorties
    if obj.ident == regle.dident:
        ressource = regle.ressource
    else:
        groupe, classe = obj.ident
        if regle.fanout == "groupe":
            nom = sorties.get_id(rep_sortie, groupe, "", ".asc")
        else:
            nom = sorties.get_id(rep_sortie, groupe, classe, ".asc")

        ressource = sorties.get_res(regle, nom)
        if ressource is None:
            if os.path.dirname(nom):
                os.makedirs(os.path.dirname(nom), exist_ok=True)
            streamwriter = AscWriter(
                nom,
                encoding="cp1252",
                liste_att=attributs,
                geomwriter=self.geomwriter,
                schema=obj.schema,
            )
            ressource = sorties.creres(regle, nom, streamwriter)
        else:
            ressource.handler.changeclasse(obj.schema, attributs)

        regle.ressource = ressource
        regle.dident = obj.ident
    #    print ("fichier de sortie ",fich.nom)
    ressource.write(obj, regle.idregle)


def ecrire_objets_asc(self, regle, _, attributs=None):
    """ecrit un ensemble de fichiers asc a partir d'un stockage memoire ou temporaire"""
    # ng, nf = 0, 0
    # memoire = defs.stockage
    #    print( "ecrire_objets asc")
    rep_sortie = regle.getvar("_sortie")
    sorties = regle.stock_param.sorties
    dident = None
    ressource = None
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):  # on parcourt les objets
            if obj.virtuel:  # on ne traite pas les virtuels
                continue
            if obj.ident != dident:
                groupe, classe = obj.ident
                if regle.fanout == "groupe":
                    nom = sorties.get_id(rep_sortie, groupe, "", ".asc")
                else:
                    nom = sorties.get_id(rep_sortie, groupe, classe, ".asc")

                ressource = sorties.get_res(regle, nom)
                if ressource is None:
                    if os.path.dirname(nom):
                        os.makedirs(os.path.dirname(nom), exist_ok=True)

                    streamwriter = AscWriter(
                        nom,
                        encoding="cp1252",
                        geomwriter=self.geomwriter,
                    )
                    streamwriter.set_liste_att(attributs)
                    ressource = sorties.creres(regle, nom, streamwriter)
                regle.ressource = ressource
                dident = (groupe, classe)
            ressource.write(obj, regle.idregle)


#                       reader,      geom,    hasschema,  auxfiles, initer
READERS = {"asc": (lire_objets_asc, "geom_asc", False, ("rlt", "seq"),  init_format_asc)}
# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {
    "asc": (
        ecrire_objets_asc,
        asc_streamer,
        False,
        "up",
        0,
        "",
        "groupe",
        "geom_asc",
        "geom_asc",
        None
    )
}
#########################################################################
