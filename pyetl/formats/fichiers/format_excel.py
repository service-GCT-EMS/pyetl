# -*- coding: utf-8 -*-
# formats d'entree sortie
"""gestion des formats d'entree et de sortie.
    actuellement les formats suivants sont supportes
    asc entree et sortie
    postgis text entree (a finaliser) et sortie
    csv entree et sortie
    shape entree et sortie
"""
printtime = False
if printtime:
    import time

    t1 = time.time()

import os

# from numba import jit


def importer():
    global XL, unidecode
    import openpyxl as XL
    from unidecode import unidecode


if printtime:
    print(" excel      ", time.time() - t1)
    t1 = time.time()

from .fileio import FileWriter

if printtime:
    print(" filewriter      ", time.time() - t1)
    t1 = time.time()


#########################################################################
# format xlsx
# tous fichiers excel multi tabs
#########################################################################
def getnoms(rep, chemin, fichier):
    """ determine les noms de groupe et de schema"""
    schema = ["schema"]
    niveaux = os.path.splitext(fichier)[0]
    if rep and rep != ".":
        schema = os.path.basename(rep)
    return schema, niveaux


def cleanname(nom):
    return unidecode(str(nom).lower()).strip("!").strip().replace(" ", "_")


def creschema_excel(nom_schema, nom_groupe, nom_classe, regle, entete):
    """prepare le schema a partir d un fichier excel"""
    exn = lambda n: (exn(n // 26) if n > 26 else "") + chr(63 + n % 26)
    geom = False
    stock_param = regle.stock_param
    schema_courant = stock_param.schemas.get(regle.getvar("schema_entree"))

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

        noms_attributs = [cleanname(i) for i in entete]
        # on verifie que les noms existent et sont uniques
        noms = set()

        for i, nom in enumerate(noms_attributs):
            if not nom:
                noms_attributs[i] = "#" + exn(i)
            if nom in noms:
                noms_attributs[i] = nom + "_" + str(i)
            noms.add(noms_attributs[i])

        for i in noms_attributs:
            if i[0] != "#":
                schemaclasse.stocke_attribut(i, "T")
    #    else: # on adapte le schema force pur eviter les incoherences
    #        schemaclasse.adapte_schema_classe(noms_attributs)

    return nom_groupe, nom_classe, noms_attributs, schemaclasse


def isnovide(ligne):
    """determine si une ligne est vide:
    contient autre chose que blanc null ou !"""
    return any((i.value for i in ligne if i.value != "!"))


def maybheader(ligne):
    """essaye de savoir s il y a un entete: commence par "!xxx" et pas de colonnes vides"""
    start = 0
    end = len(ligne)
    header = False
    for n, v in enumerate(ligne):
        # print("analyse", n, v)
        if not header:
            if v == "!":
                header = ligne[n + 1] if n + 1 < end else False
                start = n + 1
            elif v.startswith("!") and v[1:].strip():
                header = True
                start = n
        else:
            if v:
                end = n
    return header, start, end


def lire_objets_excel(self, rep, chemin, fichier, entete=None, separ=None):
    """lit des objets a partir d'un fichier csv"""
    importer()

    exn = lambda n: (exn(n // 26) if n > 26 else "") + chr(64 + n % 26)
    maxobj = self.regle_ref.getvar("lire_maxi", 0)
    nom_schema, nom_groupe = getnoms(rep, chemin, fichier)
    alire = os.path.join(rep, chemin, fichier)
    # print("ouverture fichier", alire)
    nlignes = 0
    wb = XL.load_workbook(filename=alire, data_only=True)
    # print("ouverture excel", wb, dir(wb))
    for i in wb.worksheets:
        # print("lecture table", i)
        nom_classe = cleanname(i.title)
        self.setidententree(nom_groupe, nom_classe)
        lecteur = i.iter_rows()
        for j in lecteur:
            if isnovide(j):
                ligne = [str(v.value) if v.value else "" for v in j]
                header, start, end = maybheader(ligne)
                # print("test_entete", header, start, end)
                # print("candidat", ligne[start:end])
                if header:
                    entete = (str(v.value) if v.value else "" for v in j[start:end])
                    (
                        nom_groupe,
                        nom_classe,
                        noms_attributs,
                        schemaclasse,
                    ) = creschema_excel(
                        nom_schema, nom_groupe, nom_classe, self.regle_ref, entete
                    )
                    # print("fin_entete", schemaclasse)
                    break
        # print("fin_entete", j)
        for j in lecteur:
            if isnovide(j):
                ligne = [str(c.value) if c.value else "" for c in j[start:end]]
                nlignes = nlignes + 1
                obj = self.getobj()
                obj.setschema(schemaclasse)
                obj.setorig(nlignes)
                obj.attributs.update(zip(noms_attributs, ligne))

                # print("ligne", ligne)
                obj.attributs["#type_geom"] = "0"
                obj.attributs["#chemin"] = chemin
                self.regle_ref.stock_param.moteur.traite_objet(obj, self.regle_start)
    return


class XlsxWriter(FileWriter):
    """ gestionnaire des fichiers csv en sortie """

    def __init__(
        self,
        nom,
        schema,
        # extension,
        # separ,
        # entete,
        # encoding="utf-8",
        # null="",
        # f_sortie=None,
        regle=None,
    ):

        super().__init__(nom, schema=schema, regle=regle)

        self.extension = regle.extension
        self.separ = regle.separ
        self.nom = nom
        self.schema = schema

        self.entete = regle.entete
        self.null = regle.null
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
        self.escape = "\\" + self.separ
        self.repl = "\\" + self.escape
        self.fichier = None
        self.encoding = self.encoding
        self.transtable = str.maketrans(
            {"\n": "\\" + "n", "\r": "\\" + "n", self.separ: self.escape}
        )

    def header(self, init=1):
        """ preparation de l'entete du fichiersr csv"""
        if not self.entete:
            return ""
        geom = (
            self.separ + "geometrie" + "\n"
            if self.schema.info["type_geom"] != "0"
            else "\n"
        )
        return "!" + self.separ.join(self.liste_att) + geom

    def write(self, obj):
        """ecrit un objet"""
        if obj.virtuel:
            return False  #  les objets virtuels ne sont pas sortis

        atlist = (
            str(obj.attributs.get(i, "")).translate(self.transtable)
            for i in self.liste_att
        )
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
            ressource = sorties.get_res(regle, nom)
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
        nom = sorties.get_id(
            os.path.join(rep_sortie, bfich), groupe, "", extention, nom=dest
        )

    else:
        nom = sorties.get_id(
            os.path.join(rep_sortie, bfich), groupe, classe, extention, nom=dest
        )

    ressource = sorties.get_res(regle, nom)
    #    print('csv:fichier', regle.getvar('_wid'), regle.fanout, rep_sortie, bfich, groupe,nom)
    return ressource, nom


def change_ressource(regle, obj, writer, separ, extention, entete, null, initial=False):
    """ change la definition de la ressource utilisee si necessaire"""

    ident = obj.ident

    ressource, nom = getfanout(regle, extention, ident, initial)
    #    ressource = sorties.get_res(regle, nom)

    #    print ('change_ressoures ', regle.f_sortie.writerparms)
    if ressource is None:
        if separ is None:
            separ = regle.getvar("separ_csv_out", regle.getvar("separ_csv", ";"))
        if not nom.startswith("#"):
            #            print('creation ',nom,'rep',os.path.abspath(os.path.dirname(nom)))
            os.makedirs(os.path.dirname(nom), exist_ok=True)
        str_w = writer(
            nom,
            obj.schema,
            extention,
            separ,
            entete,
            encoding=regle.getvar("codec_sortie", "utf-8"),
            null=null,
            f_sortie=regle.f_sortie,
            regle=regle,
        )
        ressource = regle.stock_param.sorties.creres(nom, str_w)
    #    print ('recup_ressource ressource stream csv' , ressource, nom, ident, ressource.etat)
    regle.ressource = ressource
    regle.dident = ident
    return ressource


def excel_streamer(
    obj,
    regle,
    _,
    entete="csv",
    separ=None,
    extention=".csv",
    null="",
    writer=XlsxWriter,
):  # ecritures non bufferisees
    """ ecrit des objets csv en streaming"""
    #    sorties = regle.stock_param.sorties
    if regle.dident == obj.ident:
        ressource = regle.ressource
    else:
        ressource = change_ressource(
            regle, obj, writer, separ, extention, entete, null, initial=True
        )

    ressource.write(obj, regle.idregle)


#    if obj.geom_v.courbe:
#        obj.schema.info['courbe'] = '1'


def ecrire_objets_excel(
    regle, _, entete="csv", separ=None, extention=".csv", null="", writer=XlsxWriter
):
    """ ecrit des objets csv a partir du stockage interne"""
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

            ressource.write(obj, regle)

    #            if obj.geom_v.courbe:
    #                obj.schema.info['courbe'] = '1'


READERS = {"xlsx": (lire_objets_excel, "", False, (), None, None)}
# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom, initer)
WRITERS = {
    "xlsx": (
        ecrire_objets_excel,
        excel_streamer,
        False,
        "",
        0,
        "",
        "groupe",
        "",
        "",
        None,
    )
}
