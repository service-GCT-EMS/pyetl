# -*- coding: utf-8 -*-
""" format asc en lecture et ecriture
"""

import os
import logging
import datetime
from .fileio import FileWriter


# formats geometriques ######
FC = 1000.0  # ajoute les elements d'entete a un objet
FA = 10.0
LOGGER = logging.getLogger(__name__)


# formats complets
####################################################################################
#### traitement  format asc
####################################################################################
def att_to_text(obj, liste, transtable):
    """convertit la liste d attributs en chaine"""
    attmap = obj.schema.attmap if obj.schema else dict()
    #    print "ecriture", liste
    tliste = list()
    eliste = list()
    fliste = []
    if liste is None:
        a_sortir = [i for i in obj.attributs if i[0] != "#" and obj.attributs[i]]
    else:
        a_sortir = [i for i in liste if i in obj.attributs and obj.attributs[i]]

    # print("att_to_text a_sortir", a_sortir)
    try:
        aliste = (
            [
                (attmap.get(i, i).upper(), str(obj.attributs[i]).translate(transtable))
                for i in a_sortir
                if i not in obj.attributs_speciaux
            ]
            if transtable
            else [
                (attmap.get(i, i).upper(), str(obj.attributs[i]))
                for i in a_sortir
                if i not in obj.attributs_speciaux
            ]
        )
    except Exception as err:
        aliste = ()
        # print("asc: erreur objet", obj, a_sortir)
        # print("------------->", obj.attributs)
        print(
            "------------->",
            [
                (attmap.get(i, i).upper(), str(obj.attributs.get(i,'???')))
                for i in a_sortir
            ],
        )
        print("erreur", err)
        raise
    if obj.attributs_speciaux:
        for nom, nature in obj.attributs_speciaux.items():
            if nom in a_sortir:
                if nature == "TG":
                    tliste.append(nom)
                elif nature == "C":  # complement on ignore
                    pass
                elif nature == "ET":
                    eliste.append(nom)
                else:
                    fliste.append(nom)

    attlist = "\n".join(
        ("2" + i + ",NG" + str(len(j)) + "," + j + ";" for i, j in aliste)
    )

    if tliste:
        tglist = list()
        for nom in tliste:
            val = str(obj.attributs[nom]).translate(transtable)
            adef = obj.attributs.get(nom + "_O")
            angle = (90 - float(adef)) % 360 if adef else 0
            angle = str(int(round(angle * FA)))
            tglist.append(
                "2"
                + attmap.get(nom, nom).upper()
                + ",TL"
                + str(len(val))
                + ","
                + str(int(float(obj.attributs[nom + "_X"]) * FC))
                + ","
                + str(int(float(obj.attributs[nom + "_Y"]) * FC))
                + ","
                + angle
                + ",RC1,TC1,"
                + val
                + ";"
            )
        attlist = attlist + "\n" + "\n".join(tglist)
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
    if fliste:
        tflist = (
            (attmap.get(i, i).upper(), str(obj.attributs[i]).translate(transtable))
            for i in fliste
        )
        flist = "\n".join(
            ("2" + i + ",NG" + str(len(j)) + "," + j + ";" for i, j in tflist)
        )
        attlist = attlist + "\n" + flist
    # print ("asc attlist", attlist,obj)
    return attlist


def apic2iso(date, heure):
    # convertit une date apic en format iso
    date = date.strip()
    heure = heure.strip()
    return date[6:10] + date[2:6] + date[:2] + " " + heure


def _decode_dates_apic(chaine):
    """decode une date au format apic"""
    dates = chaine.split(",")
    # on passe les dates en format ISO
    if len(dates) == 4:
        dat_cre = apic2iso(dates[0], dates[1])
        dat_mod = apic2iso(dates[2], dates[3])
    elif len(dates) == 3:  # une seule date
        if dates[0] == "":
            dat_cre = ""
            dat_mod = apic2iso(dates[0], dates[1])
        else:
            dat_cre = apic2iso(dates[2], dates[3])
            dat_mod = ""
    elif len(dates) == 2:  # une seule date partielle
        if dates[0] == "":
            dat_cre = ""
            dat_mod = apic2iso(dates[1], "")
        else:
            if ":" in dates[1]:
                dat_cre = apic2iso(dates[0], dates[1])
                dat_mod = ""
            else:
                dat_cre = apic2iso(dates[0], "")
                dat_mod = apic2iso(dates[1], "")
    else:
        dat_cre = ""
        dat_mod = ""
    # print("decode_dates apic", dates, "->", dat_cre, dat_mod)
    return dat_cre.strip(), dat_mod.strip()


def decode_entete_asc(entete):
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
        # print("asc:erreur point ", liste1[0])
        LOGGER.error("erreurs point %s ", liste1[0])
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
        LOGGER.error("erreurs entete " + classe + " -> %s", entete)
        # LOGGER.debug("erreurs entete %s -> %s", classe, entete)
        erreurs = "erreur lecture entete: " + entete

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


def traite_booleen(vatt):
    """traitement des booleens"""
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
def ajout_attribut_asc(attributs, attr, speciaux):
    """decodage d'un attribut asc et stockage"""
    code = attr[0]
    suite = False
    liste_elts = attr.split(",", 2)  # les 2 premiers suffisent en general
    nom = liste_elts[0][1:]
    vatt = ""
    type_att = "A"

    if code == "2":
        code_att = liste_elts[1][0:2]
        long_attrib = int(liste_elts[1][2:])
        if code_att == "NG":
            # vl = ', '.join(l[2:])
            vatt = liste_elts[2][0:long_attrib]
            suite = len(vatt) < long_attrib

        elif code_att == "TL":
            speciaux[nom] = "TG"  # texte_graphique
            nom_x = nom + "_X"
            nom_y = nom + "_Y"
            nom_o = nom + "_O"
            speciaux[nom_x] = "C"
            speciaux[nom_y] = "C"
            speciaux[nom_o] = "C"
            liste_elts = attr.split(",")  # d on decode plus loin
            #            try:
            attributs[nom_x] = str(float(liste_elts[2]) / FC)
            attributs[nom_y] = str(float(liste_elts[3]) / FC)
            attributs[nom_o] = str(90 - round(float(liste_elts[4]) / FA, 1))
            #            except ValueError:
            #                print("error: asc  : texte graphique incorrect", liste_elts)
            texte_candidat = ",".join(liste_elts[7:])
            vatt = texte_candidat[0:long_attrib]
        elif code_att == "CT":  # texte symbolique (recupere en texte)
            liste_elts = attr.split(",")  # d on decode plus loin
            speciaux[nom] = "TS"
            vatt = liste_elts[6]
        else:
            print("error: asc  : lecture_asc code inconnu ", code_att, attr)
    elif code == "4":
        vatt = liste_elts[1][:-1]
        speciaux[nom] = "ET"
        nom = "#_sys_E_" + liste_elts[0][1:]
    else:
        print("error: asc  : code inconnu", liste_elts)

    attributs[nom] = vatt if nom not in attributs else attributs[nom]+';'+vatt
    return nom, suite
    # print l, l[-1].strip()
    # print 1/0


def init_reader_asc(reader):
    """positionnne des elements de lecture (traitement des booleens)"""
    reader.formatters["B"] = traite_booleen
    reader.setvar("codec_asc", "cp1252")


def init_ascw(output):
    output.writerclass = AscWriter


def finalise_obj(reader, attributs, coords, geom, angle, dim, speciaux):
    """finalise un objet et le traite"""
    # print("finalisation ", attributs)
    # if attributs and not "GID" in attributs:
    #     attributs["gid"] = attributs["#gid"]
    obj = reader.getobj(attributs=attributs, geom=geom) if attributs or geom else None
    if obj is None:  # filtrage en entree
        return
    obj.attributs_speciaux.update(speciaux)
    if coords:
        obj.geom_v.setpoint(coords, angle, dim)
    if geom:
        obj.attributs["#dimension"] = "3" if geom[0].find("3D") else "2"
    if obj.dimension == 0:
        print("asc: erreur finalisation ", obj, coords, geom, dim)
    # print ('creation obj', obj)
    reader.process(obj)


def lire_objets_asc(self, rep, chemin, fichier):
    """lecture d'un fichier asc et stockage des objets en memoire"""
    obj = None
    nom = ""
    attributs = dict()
    speciaux = dict()
    geom = []
    coords = []
    angle = 0
    dim = 2
    groupe, dclasse = self.prepare_lecture_fichier(rep, chemin, fichier)
    #    print ('lire_asc ', schema, schema_init)
    #    print('asc:entree', fichier)
    with open(
        self.fichier, "r", 65536, encoding=self.encoding, errors="backslashreplace"
    ) as ouvert:
        suite = False
        basename = os.path.splitext(os.path.basename(fichier))[0]
        if not chemin:
            chemin = os.path.basename(rep)
        for i in ouvert:
            if suite:
                # suite, nom = complete_attribut(attributs, nom, i)
                attributs[nom] += i
                suite = False
                continue
            if len(i) <= 2 or i.startswith("*") or i.startswith(";4"):
                continue
            code_0, code_1 = i[0], i[1]
            if code_0 == ";" and code_1.isnumeric():
                # print ('asc lecture', i)
                finalise_obj(self, attributs, coords, geom, angle, dim, speciaux)
                geom = []
                speciaux = dict()
                if code_1 in "9356":
                    classe, attributs, coords, angle, dim = decode_entete_asc(i)
                    if classe != dclasse:
                        groupe = chemin if basename == classe else basename
                        self.setidententree(groupe, classe)
                        dclasse = classe

            elif (code_0 == "2" or code_0 == "4") and (
                code_1.isalpha() or code_1 == "_"
            ):
                nom, suite = ajout_attribut_asc(attributs, i, speciaux)
            elif i.startswith("FIN"):
                continue
            else:
                geom.append(i)
        finalise_obj(self, attributs, coords, geom, angle, dim, speciaux)
    return


def ecrire_point_asc(geom):
    """retourne un point pour l'entete"""

    dim = geom.dimension
    angle = (90 - geom.angle) % 360 if geom.angle is not None else 0
    angle = round(angle * FA)
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
        return ";0 ", ""


def format_date(date, format_d="ISO"):
    """genere une date en format entete elyx"""
    if not date:
        return ""
    if format_d == "ISO":
        if isinstance(date, datetime.datetime):
            return date.strftime("%d-%m-%Y,%H:%M:%S")
        elif isinstance(date, str):
            dd1 = date.split(".")[0]
            return dd1[8:10] + dd1[4:8] + dd1[:4] + "," + dd1[11:]
    else:
        return date.replace("/", "-").replace(" ", ",").split(".")[0] if date else ""


def ecrire_entete_asc(obj) -> str:
    """genere le texte d'entete asc a partir d'un objet en memoire"""
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
            print(
                "geometrie asc invalide ",
                obj.ident,
                id_num,
                obj.attributs["#geom"],
                obj.geom_v.erreurs,
                obj.geom_v.type,
                "<>",
                type_geom
                # obj,
            )
            type_geom_sortie = ";5 "
            return None

    dcre = format_date(attr.get("#_sys_date_cre"))
    dmod = format_date(attr.get("#_sys_date_mod"))
    fin_ent = ";" + dcre + "," + dmod + ";" + attr.get("#complement", "")
    idobj = id_num + "," + classe + "," + index
    if fin_ent[-1] == "\n":
        fin_ent = fin_ent[:-1]

    if type_geom_sortie == "3":
        code, chaine = ecrire_point_asc(obj.geom_v)
        entete = code + idobj + chaine + fin_ent + ";\n"
    else:
        entete = type_geom_sortie + idobj + fin_ent + ";\n"
        # print ('entete asc',entete,dmod, obj)
    return entete


class AscWriter(FileWriter):
    """gestionnaire d'ecriture pour fichiers asc"""

    def __init__(self, nom, schema=None, regle=None):
        super().__init__(nom, schema=schema, regle=regle)
        self.htext = "*****\n** sortie_mapper\n*****\n"
        if schema and schema.schema.metas:
            self.htext += (
                "** meta;"
                + ";".join(k + "=" + v for k, v in schema.schema.metas.items())
                + "\n*****\n"
            )
        self.ttext = "FIN\n"
        self.transtable = str.maketrans({"\n": "\\" + "n", "\r": ""})
        self.converter = self.convertir_objet_asc
        self.liste_graphique = None
        self.liste_ordinaire = None

    def changeclasse(self, schemaclasse, attributs=None):
        """ecriture multiclasse on change de schema"""
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

    def convertir_objet_asc(self, obj, liste, transtable=None):
        """sort un objet asc en chaine"""
        entete = ecrire_entete_asc(obj)
        if not entete:  # ca na rien donne
            return ""
        #    attributs = obj.attributs[:]
        if (
            obj.format_natif == "asc" and obj.geomnatif
        ):  # on a pas touche a la geometrie
            #        print ('natif asc')
            if "#geom" in obj.attributs:
                geometrie = "".join(obj.attributs["#geom"])
            else:
                geometrie = ""
        else:
            geometrie = self.geomwriter(obj.geom_v)

        attlist = att_to_text(obj, liste, transtable or self.transtable)
        return entete + geometrie + attlist


#                reader,      geom,    hasschema,  auxfiles,       initer
READERS = {
    "asc": (lire_objets_asc, "#asc", False, ("rlt", "seq"), init_reader_asc, None)
}
# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom, init)
WRITERS = {"asc": ("", "", False, "up", 0, "asc", "groupe", "#asc", "#asc", init_ascw)}
DESCRIPTION = {
    "asc": ("le format asc est le format externe du logiciel ELYX de one spatial")
}
#########################################################################
