# -*- coding: utf-8 -*-
# formats d'entree sortie
"""gestion des formats d'entree et de sortie.
    actuellement les formats suivants sont supportes
    asc entree et sortie
    postgis text entree (a finaliser) et sortie
    csv entree et sortie
    shape entree et sortie
"""


import os

# from numba import jit
from openpyxl import load_workbook
from .fileio import FileWriter


#########################################################################
# format csv et txt geo etc
# tous les fichiers tabules avec ou sans entete
#########################################################################
def getnoms(rep, chemin, fichier):
    """ determine les noms de groupe et de schema"""
    schema = ["schema"]
    chem = chemin
    niveaux = []
    classe = os.path.splitext(fichier)[0]
    if rep and rep != ".":
        schema = os.path.basename(rep)
    while chem:
        chem, nom = os.path.split(chem)
        niveaux.append(nom)

    if not niveaux:
        groupe = ""
    else:
        groupe = "_".join(niveaux)
    #    print(rep, "<>", chemin, "<>", fichier, "traitement", schema, "<>", groupe, "<>", classe)
    return schema, groupe, classe


def decode_entetes_csv(nom_schema, nom_groupe, nom_classe, stock_param, entete, separ):
    """prepare l'entete et les noma d'un fichier csv"""

    geom = False

    schema_courant = stock_param.schemas.get(stock_param.get_param("schema_entree"))

    #    print('decodage entete csv',schema_courant.nom if schema_courant else '' ,entete)

    if schema_courant:
        nom_groupe, nom_classe = schema_courant.map_dest((nom_groupe, nom_classe))
    else:
        schema_courant = stock_param.init_schema(nom_schema, "F")

    if (nom_groupe, nom_classe) in schema_courant.classes:
        schemaclasse = schema_courant.classes[(nom_groupe, nom_classe)]
        noms_attributs = schemaclasse.get_liste_attributs()
        geom = schemaclasse.info["type_geom"] != "0"
    else:
        schemaclasse = schema_courant.setdefault_classe((nom_groupe, nom_classe))

        noms_attributs = [i.lower().strip().replace(" ", "_") for i in entete.split(separ)]
        # on verifie que les noms existent et sont uniques
        noms = set()

        for i, nom in enumerate(noms_attributs):
            if not nom:
                noms_attributs[i] = "#champs_" + str(i)
            if nom in noms:
                noms_attributs[i] = nom + "_" + str(i)
            noms.add(noms_attributs[i])

        if noms_attributs[-1] == "tgeom" or noms_attributs[-1] == "geometrie":
            geom = True
            noms_attributs.pop(-1)  # on supprime la geom en attribut classique
        for i in noms_attributs:
            if i[0] != "#":
                schemaclasse.stocke_attribut(i, "T")
    #    else: # on adapte le schema force pur eviter les incoherences
    #        schemaclasse.adapte_schema_classe(noms_attributs)

    return nom_groupe, nom_classe, noms_attributs, geom, schemaclasse


def _controle_nb_champs(val_attributs, controle, nbwarn, ligne):
    """ ajuste le nombre de champs lus """
    if len(val_attributs) < controle:
        val_attributs.extend([""] * controle)
    else:
        nbwarn += 1
        if nbwarn < 10:
            print(
                "warning: csv  : erreur format csv : nombre de valeurs incorrect",
                len(val_attributs),
                "au lieu de",
                controle,
                ligne[:-1],
                val_attributs,
            )
    return nbwarn


def lire_objets_excel(self, rep, chemin, fichier, stock_param, regle, entete=None, separ=None):
    """lit des objets a partir d'un fichier csv"""
    if separ is None:
        separ = stock_param.get_param("separ_csv_in", stock_param.get_param("separ_csv", ";"))
    #    print('lecture_csv:', rep, chemin, fichier,separ)
    maxobj = stock_param.get_param("lire_maxi", 0)
    nom_schema, nom_groupe, nom_classe = getnoms(rep, chemin, fichier)
    with open(
        os.path.join(rep, chemin, fichier),
        "r",
        encoding=stock_param.get_param("codec_entree", "utf-8"),
    ) as fich:

        if not entete:
            entete = fich.readline()[:-1]  # si l'entete n'est pas fourni on le lit dans le fichier
            if entete[0] == "!":
                entete = entete[1:]
            else:  # il faut l'inventer...
                entete = separ * len(fich.readline()[:-1].split(separ))
                fich.seek(0)  # on remet le fichier au debut

        nom_groupe, nom_classe, noms_attributs, geom, schemaclasse = decode_entetes_csv(
            nom_schema, nom_groupe, nom_classe, stock_param, entete, separ
        )
        controle = len(noms_attributs)
        nbwarn = 0
        nlignes = 0
        self.setidententree(nom_groupe, nom_classe)
        for i in fich:
            nlignes = nlignes + 1
            obj = self.getobj()
            obj.setschema(schemaclasse)
            obj.setorig(nlignes)
            val_attributs = [j.strip() for j in i[:-1].split(separ)]
            # liste_attributs = zip(noms_attributs, val_attributs)
            # print ('lecture_csv:',[i for i in liste_attributs])
            if len(val_attributs) != controle:
                nbwarn = _controle_nb_champs(val_attributs, controle, nbwarn, i)

            obj.attributs.update(zip(noms_attributs, val_attributs))
            # print ('attributs:',obj.attributs['nombre_de_servitudes'])
            if geom:
                obj.attributs["#geom"] = [val_attributs[-1]]
                #                print ('geometrie',obj.geom)
                obj.attributs["#type_geom"] = "-1"
            else:
                obj.attributs["#type_geom"] = "0"
            obj.attributs["#chemin"] = chemin
            stock_param.moteur.traite_objet(obj, regle)

            if maxobj and nlignes >= maxobj:  # nombre maxi d'objets a lire par fichier
                break

            if nlignes % 100000 == 0:
                stock_param.aff.send(("interm", 0, nlignes))  # gestion des affichages de patience

        if nbwarn:
            print(nbwarn, "lignes avec un nombre d'attributs incorrect")
    return


class XlsxWriter(FileWriter):
    """ gestionnaire des fichiers csv en sortie """

    def __init__(
        self,
        nom,
        schema,
        extension,
        separ,
        entete,
        encoding="utf-8",
        null="",
        f_sortie=None,
    ):

        super().__init__(
            nom, encoding=encoding, schema=schema, f_sortie=f_sortie
        )

        self.extension = extension
        self.separ = separ
        self.nom = nom
        self.schema = schema

        self.entete = entete
        self.null = null
        self.classes = set()
        if schema:
            #            print ('writer',nom, schema.schema.init, schema.info['type_geom'])
            if schema.info["type_geom"] == "indef":
                schema.info["type_geom"] = "0"
            self.type_geom = self.schema.info["type_geom"]
            self.multi = self.schema.multigeom
            self.liste_att = schema.get_liste_attributs()
            self.force_courbe = self.schema.info["courbe"]
        else:
            print("attention csvwriter a besoin d'un schema", self.nom)
            raise ValueError("csvwriter: schema manquant")
        self.escape = "\\" + separ
        self.repl = "\\" + self.escape
        self.fichier = None
        self.encoding = encoding
        self.transtable = str.maketrans(
            {"\n": "\\" + "n", "\r": "\\" + "n", self.separ: self.escape}
        )

    def header(self, init=1):
        """ preparation de l'entete du fichiersr csv"""
        if not self.entete:
            return ""
        geom = self.separ + "geometrie" + "\n" if self.schema.info["type_geom"] != "0" else "\n"
        return "!" + self.separ.join(self.liste_att) + geom

    def write(self, obj):
        """ecrit un objet"""
        if obj.virtuel:
            return False  #  les objets virtuels ne sont pas sortis

        atlist = (str(obj.attributs.get(i, "")).translate(self.transtable) for i in self.liste_att)
        #        print ('ectriture_csv',self.schema.type_geom, obj.format_natif,
        #                obj.geomnatif, obj.type_geom)
        #        print ('orig',obj.attributs)
        attributs = self.separ.join((i if i else self.null for i in atlist))

        ligne = attributs

        if self.writerparms.get("nodata"):
            return False

        #        print("sortie ewkt",len(geom))

        self.fichier.write(ligne)
        self.fichier.write("\n")
        return True


def getfanout(regle, extention, ident, initial):
    """determine le mode de fanout"""
    sorties = regle.stock_param.sorties
    rep_sortie = regle.getvar("_sortie")
    groupe, classe = ident
    dest = regle.f_sortie.writerparms.get("destination")
    #    print ('dans getfanout ', regle.fanout, regle.f_sortie.fanoutmax, ident,
    #           initial,extention, dest)

    bfich = ""
    if regle.params.cmp2.val:
        nfich = regle.params.cmp2.val
        if nfich == "#print":
            nom = "#print"
            ressource = sorties.get_res(regle.numero, nom)
            return ressource, nom

    if regle.fanout == "no" and regle.f_sortie.fanoutmax == "all":
        bfich = dest if dest else "all"
        nom = sorties.get_id(rep_sortie, bfich, "", extention, nom=dest)
    #            print('nom de fichier sans fanout ', rep_sortie, nfich, nom)
    elif regle.fanout == "groupe" and (
        regle.f_sortie.fanoutmax == "all" or regle.f_sortie.fanoutmax == "groupe"
    ):
        #            print('csv:recherche fichier',obj.ident,groupe,classe,obj.schema.nom,
        #            len(obj.schema.attributs))
        nom = sorties.get_id(os.path.join(rep_sortie, bfich), groupe, "", extention, nom=dest)

    else:
        nom = sorties.get_id(os.path.join(rep_sortie, bfich), groupe, classe, extention, nom=dest)

    ressource = sorties.get_res(regle.numero, nom)
    #    print('csv:fichier', regle.getvar('_wid'), regle.fanout, rep_sortie, bfich, groupe,nom)
    return ressource, nom


def change_ressource(regle, obj, writer, separ, extention, entete, null, initial=False):
    """ change la definition de la ressource utilisee si necessaire"""

    ident = obj.ident

    ressource, nom = getfanout(regle, extention, ident, initial)
    #    ressource = sorties.get_res(regle.numero, nom)

    #    print ('change_ressoures ', regle.f_sortie.writerparms)
    if ressource is None:
        if separ is None:
            separ = regle.getvar("separ_csv_out", regle.getvar("separ_csv", "|"))
        if not nom.startswith("#"):
            #            print('creation ',nom,'rep',os.path.abspath(os.path.dirname(nom)))
            os.makedirs(os.path.dirname(nom), exist_ok=True)
        str_w = writer(
            nom,
            obj.schema,
            extention,
            separ,
            entete,
            encoding=regle.stock_param.get_param("codec_sortie", "utf-8"),
            null=null,
            f_sortie=regle.f_sortie,
        )
        ressource = regle.stock_param.sorties.creres(regle.numero, nom, str_w)
    #    print ('recup_ressource ressource stream csv' , ressource, nom, ident, ressource.etat)
    regle.stock_param.set_param("derniere_sortie", nom, parent=1)
    regle.ressource = ressource
    regle.dident = ident
    return ressource


def excel_streamer(
    obj, regle, _, entete="csv", separ=None, extention=".csv", null="", writer=XlsxWriter
):  # ecritures non bufferisees
    """ ecrit des objets csv en streaming"""
    #    sorties = regle.stock_param.sorties
    if regle.dident == obj.ident:
        ressource = regle.ressource
    else:
        ressource = change_ressource(
            regle, obj, writer, separ, extention, entete, null, initial=True
        )

    ressource.write(obj, regle.numero)


#    if obj.geom_v.courbe:
#        obj.schema.info['courbe'] = '1'


def ecrire_objets_excel(
    regle, _, entete="csv", separ=None, extention=".csv", null="", writer=XlsxWriter
):
    """ ecrit des objets csv a partir du stockage interne"""
    #    sorties = regle.stock_param.sorties
    #    numero = regle.numero
    print("csv:ecrire csv", regle.stockage.keys())

    for groupe in list(regle.stockage.keys()):
        # on determine le schema
        print("csv:ecrire groupe", groupe)

        for obj in regle.recupobjets(groupe):
            #            print("csv:ecrire csv", obj)
            #            print( regle.stockage)
            #            groupe, classe = obj.ident
            if obj.ident != regle.dident:
                ressource = change_ressource(
                    regle, obj, writer, separ, extention, entete, null, initial=False
                )

            ressource.write(obj, regle.numero)

    #            if obj.geom_v.courbe:
    #                obj.schema.info['courbe'] = '1'


READERS = {"xlsx": (lire_objets_excel, "", False, (), None)}
# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {"xlsx": (ecrire_objets_excel, excel_streamer, False, "", 0, "", "groupe", "", "")}
