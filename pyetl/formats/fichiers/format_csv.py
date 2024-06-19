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
import csv
import codecs

# from numba import jit
from .fileio import FileWriter
from ..generic_io import getdb


def csvreader(reader, rep, chemin, fichier, entete=None, separ=None, mode="csv"):
    reader.prepare_lecture_fichier(rep, chemin, fichier)
    logger = reader.regle_ref.stock_param.logger
    # print("dertermination separ", separ, reader.separ)
    if separ is None:
        separ = reader.separ
    # nom_schema, nom_groupe, nom_classe = getnoms(rep, chemin, fichier)
    nbwarn = 0
    # print(" lecture_csv, separ:", len(separ), separ, "<>", reader.encoding)

    dialect = None
    with open(
        os.path.join(rep, chemin, fichier), newline="", encoding=reader.encoding
    ) as csvfile:
        sample = csvfile.read(4094)
        csvfile.seek(0)
        if not (separ and entete):
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=separ)
                has_header = csv.Sniffer().has_header(sample) or sample.startswith("!")
            except csv.Error:
                logger.warning(
                    "erreur determination dialecte csv, parametres par defaut (%s)",
                    separ,
                )
                linesep = "\r\n" if "\r\n" in sample else "\n"
                has_header = sample.startswith("!")
                if has_header:
                    hline = sample.split(linesep, 1)[0]
                    entete = hline[1:].split(separ)
        # print("dialect trouve", dialect, "->", dialect.delimiter, "(", separ, ")")
        if not dialect:
            dref = csv.get_dialect("excel")
            linesep = "\r\n" if "\r\n" in sample else "\n"
            csv.register_dialect(
                "special", dref, delimiter=separ, lineterminator=linesep
            )
            dialect = csv.get_dialect("special")
            has_header = sample.startswith("!")
        if not entete:
            entete = reader.regle_ref.getvar("csvheader", "")
            if entete:
                entete = entete.split(",")
            else:
                lecteur = csv.DictReader(csvfile, dialect=dialect)
                # print("lecteur , ", lecteur.fieldnames)
                if has_header:
                    entete = [
                        i.replace(" ", "_").replace("!", "") for i in lecteur.fieldnames
                    ]
                else:
                    nfields = int(reader.regle_ref.getvar("csvfields", 0))
                    nfields = nfields if nfields else len(lecteur.fieldnames)
                    entete = ["champ_" + str(i) for i in range(nfields)]
        try:
            if entete[-1] == "tgeom" or entete[-1] == "geometrie":
                entete[-1] = "#geom"
        except IndexError:
            logger.error("entete incorrect (%s)", entete)
        reste = reader.regle_ref.getvar("restfields", "#reste")
        lecteur = csv.DictReader(
            csvfile, fieldnames=entete, dialect=dialect, restval="", restkey=reste
        )
        csvfile.seek(0)
        if has_header:  # on teste la presence de metadonnees
            lecteur.__next__()
            ligne = list(lecteur.__next__().values())
            nlin = 1
            while ligne[0].startswith("!"):
                nlin += 1
                ligne = list(lecteur.__next__().values())
            csvfile.seek(0)
            # print("csv:",nlin,"entete")
            for i in range(nlin):
                lecteur.__next__()

        # print("entete csv", entete, dialect.delimiter, separ, dialect)
        if reader.newschema:
            for i in entete + [reste]:
                if i[0] != "#":
                    reader.schemaclasse.stocke_attribut(i, "T")
        reader.prepare_attlist(entete + [reste])
        # print("attlist", reader.attlist)
        type_geom = "-1" if entete[-1] == "#geom" else "0"
        reader.fixe["#type_geom"] = type_geom
        for attributs in lecteur:
            obj = reader.getobj(attributs=attributs)
            # print(" recup objet", obj)
            if obj is None:
                continue  # filtrage entree
            reader.process(obj)


def attreader(reader, ouvert):
    header = reader.regle_ref.istrue("header")
    champs = reader.regle_ref.params.cmp2.liste
    reste = reader.regle_ref.getvar("restfields", "#reste")

    if champs:
        nchamps = len(champs)
        champs.extend([reste])
        reader.prepare_attlist(champs)
    # print("attreader", ouvert)
    for i in ouvert:
        # print("attreader csv lecture", i, champs)
        if i.endswith("\r\n"):
            i = i[:-2]
        elif i.endswith("\n"):
            i = i[:-1]
        if header:
            champs = i.split(";")
            header = False
            champs.extend([reste])
            reader.prepare_attlist(champs)
            nchamps = len(champs)
            continue
        if not champs:
            champs = ["champ_" + str(i + 1) for i in range(len(i.split(";")) - 1)]
        attributs = list(zip(champs, i.split(";", nchamps)))
        # print("attreader csv lecture", attributs)
        obj = reader.getobj(attributs=attributs)
        reader.process(obj)
    # print("attreader", ouvert)


class CsvWriter(FileWriter):
    """gestionnaire des fichiers csv en sortie"""

    def __init__(self, nom, schema, regle):
        super().__init__(nom, schema=schema, regle=regle)
        self.headerfonc = str
        self.classes = set()
        self.errcnt = 0
        self.objs = dict()
        if self.schemaclasse:
            #            print ('writer',nom, schema.schema.init, schema.info['type_geom'])
            if self.schemaclasse.info["type_geom"] == "indef":
                self.schemaclasse.info["type_geom"] = "0"
            self.type_geom = self.schemaclasse.info["type_geom"]
            self.multi = self.schemaclasse.multigeom
            self.liste_att = self.schemaclasse.get_liste_attributs()
            self.force_courbe = self.schemaclasse.info["courbe"]
        else:
            print("attention csvwriter a besoin d'un schema", self.nom)
            raise ValueError("csvwriter: schema manquant")
        self.escape = "\\" + self.separ
        self.repl = "\\" + self.escape
        if len(self.separ) != 1:
            print("attention separateur non unique", self.separ)
            self.transtable = str.maketrans({"\n": "\\" + "n", "\r": "\\" + "n"})
        else:
            self.transtable = str.maketrans(
                {"\n": "\\" + "n", "\r": "\\" + "n", self.separ: self.escape}
            )

    def header(self, init=1):
        """preparation de l'entete du fichiersr csv"""
        # print("csvheader ", self.entete)
        entete = self.writerparms.get("entete")
        if not entete:
            #            raise
            return ""
        geom = (
            self.separ + self.headerfonc(self.schemaclasse.info["nom_geometrie"]) + "\n"
            if self.schemaclasse.info["type_geom"] != "0"
            else "\n"
        )
        return (
            ("" if entete == "csv_f" else "!")
            + self.separ.join([self.headerfonc(i) for i in self.liste_att])
            + geom
        )

    def prepare_attributs(self, obj):
        """prepare les attributs en fonction du format"""

        if obj.hdict:
            # atlist = []
            atlist = (
                ",".join(
                    [
                        '"' + i + '"=>"' + str(j).translate(self.htranstable) + '"'
                        for i, j in sorted(obj.hdict[nom].items())
                    ]
                )
                if nom in obj.hdict
                else str(obj.attributs.get(nom, "")).translate(self.transtable)
                for nom in self.liste_att
            )

        else:
            atlist = (
                str(obj.attributs.get(nom, "")).translate(self.transtable)
                for nom in self.liste_att
            )

        return self.separ.join((i or self.null for i in atlist))

    # def prepare_attributs(self, obj):
    #     """prepare les attributs en fonction du format"""
    #     atlist = (
    #         str(obj.attributs.get(i, "")).translate(self.transtable)
    #         for i in self.liste_att
    #     )
    #     #        print ('ectriture_csv',self.schema.type_geom, obj.format_natif,
    #     #                obj.geomnatif, obj.type_geom)
    #     #        print ('orig',obj.attributs)
    #     attributs = self.separ.join((i or self.null for i in atlist))
    #     print("attributs", attributs)
    #     return attributs

    def prep_write(self, obj):
        """ecrit un objet"""
        # print("writer: ", id(self), self.regle.idregle)
        if obj.virtuel:
            return False  #  les objets virtuels ne sont pas sortis
        attributs = self.prepare_attributs(obj)
        if self.type_geom != "0":
            if (
                obj.format_natif == self.writerparms["geom"] and obj.geomnatif
            ):  # on a pas change la geometrie
                geom = obj.attributs["#geom"]
                if not geom:
                    geom = self.null
            #                print("sortie ewkt geom0",len(geom))
            else:
                if obj.initgeom():
                    # print ("geomwriter",self.geomwriter)
                    geom = self.geomwriter(
                        obj.geom_v, self.type_geom, self.multi, obj.erreurs
                    )
                else:
                    if not obj.attributs["#geom"]:
                        geom = self.null
                    else:
                        if self.errcnt < 10:
                            print(
                                "csv: geometrie invalide : erreur geometrique",
                                obj.ident,
                                obj.numobj,
                                "demandé:",
                                self.type_geom,
                                obj.geom_v.erreurs.errs,
                                obj.attributs["#type_geom"],
                                self.schema.info["type_geom"],
                                "->" + repr(obj.attributs["#geom"]) + "<-",
                            )
                        self.errcnt += 1
                        geom = self.null

                if obj.erreurs and obj.erreurs.actif == 2:
                    print(
                        "error: writer csv :",
                        self.extension,
                        obj.ident,
                        obj.ido,
                        "erreur geometrique: type",
                        obj.attributs["#type_geom"],
                        "demandé:",
                        obj.schema.info["type_geom"],
                        obj.erreurs.errs,
                        "->" + repr(obj.attributs["#geom"]) + "<-",
                    )
                    print("prep ligne ", attributs, "\nG:", geom)
                    print("geom initiale", obj.attributs["#geom"])
                    return False

            if not geom:
                geom = self.null
            obj.format_natif = "#ewkt"
            obj.attributs["#geom"] = geom
            obj.geomnatif = True
            ligne = attributs + self.separ + geom
        else:
            ligne = attributs
        if self.writerparms.get("nodata"):
            return False

        # print("ecriture csv", ligne, obj, self.liste_att)

        # self.fichier.write(ligne)
        # self.fichier.write("\n")
        return ligne

    def write(self, obj):
        ligne = self.prep_write(obj)
        if ligne:
            self.fichier.write(ligne)
            self.fichier.write("\n")
            return True
        return False

    def attstore(self, att, obj):
        ligne = self.prep_write(self, obj)
        clef = tuple(obj.attributs.get(i) for i in self.regle_ref.clef)
        if clef in self.objs:
            self.objs[clef].attributs[att].append(ligne)
        else:
            self.objs[clef] = self.getobj(att)
            self.objs[clef].attributs[att] = [ligne]
        return True


class SqlWriter(CsvWriter):
    """getionnaire decriture sql en fichier"""

    def __init__(self, nom, schema, regle):
        super().__init__(nom, schema, regle)
        if self.writerparms:
            self.schemaclasse.setsortie(self.output)
        self.transtable = str.maketrans(
            {"\\": r"\\", "\n": "\\" + "n", "\r": "\\" + "n", self.separ: self.escape}
        )
        self.htranstable = str.maketrans(
            {
                "\\": r"\\",
                "\n": "\\" + "n",
                "\r": "\\" + "n",
                '"': r'\\"',
                self.separ: self.escape,
            }
        )

    def __repr__(self):
        return "sqlwriter " + self.nom

    def prepare_hstore(self, val):
        """gere le cas particulier du hstore"""

    def header(self, init=1):
        separ = ", "
        gensql = self.schema.dbsql
        if not gensql:
            print(
                "header sql: erreur generateur sql non defini",
                self.schema.nom,
                self.schemaclasse.identclasse,
                self.schema.format_sortie,
            )
            raise StopIteration(3)
        niveau, classe = self.schemaclasse.identclasse
        nouveau = self.schemaclasse.identclasse not in self.classes
        self.classes.add(self.schemaclasse.identclasse)
        gensql.regle_ref = self.regle_ref
        prefix = "SET client_encoding = 'UTF8';\n" if init else ""
        #        print ('parametres sql ', self.writerparms)
        nodata = False

        type_geom = self.schemaclasse.info["type_geom"]
        nom_geom = self.schemaclasse.info["nom_geometrie"]
        dim = self.schemaclasse.info["dimension"]

        if self.writerparms and nouveau:
            reinit = self.writerparms.get("reinit")
            #            dialecte = self.writerparms.get('dialecte', 'sql')
            nodata = self.writerparms.get("nodata")

            gensql.initschema(self.schemaclasse.schema)
            # on positionne les infos de schema pour le generateur sql

            prefix = prefix + gensql.prefix_charge(
                niveau, classe, reinit, gtyp=type_geom, dim=dim
            )

        if nodata:
            return prefix
        prefix = prefix + 'copy "' + niveau.lower() + '"."' + classe.lower() + '" ('
        end = ") FROM stdin;"
        # print ("generation geometrie",type_geom,"->",nom_geom)
        geom = (
            separ + nom_geom + end + "\n"
            if self.schemaclasse.info["type_geom"] != "0"
            else end + "\n"
        )
        return (
            prefix
            + separ.join([gensql.ajuste_nom_q(i.lower()) for i in self.liste_att])
            + geom
        )

    def fin_classe(self):
        """fin de classe pour remettre les sequences"""
        reinit = self.writerparms.get("reinit", "0")
        niveau, classe = self.schemaclasse.identclasse
        gensql = self.schema.dbsql
        gensql.regle_ref = self.regle_ref
        type_geom = self.schemaclasse.info["type_geom"]
        courbe = self.schemaclasse.info["courbe"] == "1"
        dim = self.schemaclasse.info["dimension"]
        if not gensql:
            print(
                "finclasse sql: erreur generateur sql non defini",
                self.schemaclasse.identclasse,
                self.schema.format_sortie,
            )
            raise StopIteration(3)
        if self.fichier.closed:
            self.reopen()
        if self.writerparms.get("nodata"):
            self.fichier.write(
                gensql.tail_charge(niveau, classe, reinit, schema=self.schemaclasse)
            )
            return
        self.fichier.write(r"\." + "\n")

        self.fichier.write(
            gensql.tail_charge(
                niveau,
                classe,
                reinit,
                gtyp=type_geom,
                dim=dim,
                courbe=courbe,
                schema=self.schemaclasse,
            )
        )

    def finalise(self):
        """ligne de fin de fichier en sql"""
        self.fin_classe()
        super().finalise()
        return 3  # on ne peut pas le reouvrir

    def changeclasse(self, schemaclasse, attributs=None):
        """ecriture de sql multiclasse on cree des entetes intermediaires"""
        #        print( 'dans changeclasse')
        # raise
        if schemaclasse == self.schemaclasse:
            return
        self.fin_classe()
        self.schemaclasse = schemaclasse
        if schemaclasse.info["type_geom"] == "indef":  # pas de geometrie
            schemaclasse.info["type_geom"] = "0"
        self.type_geom = schemaclasse.info["type_geom"]
        self.multi = schemaclasse.multigeom
        self.liste_att = schemaclasse.get_liste_attributs(attributs)
        self.fichier.write(self.header(init=0))


# def csvstreamer(writer, obj, regle, _):
#     """ ecrit des objets csv en streaming"""
#     #    sorties = regle.stock_param.sorties
#     if regle.ressource.lastid != obj.ident:
#         regle.ressource = writer.change_ressource(obj)
#         # regle.dident = obj.ident
#     print("write: regle", regle.idregle)

#     regle.ressource.write(obj, regle.idregle)


def initwriter(self, extension, header, separ, null, writerclass=CsvWriter):
    """positionne les parametres du writer csv (sql et txt)"""
    # print ('initialisation writer', extension, header,separ,null)
    self.writerparms["separ"] = separ
    self.writerparms["extension"] = extension
    self.writerparms["entete"] = header
    self.writerparms["null"] = null
    self.writerclass = writerclass


def init_csv(self):
    """writer csv"""
    separ = self.regle_ref.getchain(("separ_csv_out", "separ_csv", "sep"), ";")
    if separ == r"\;":
        separ = ";"
    self.regle_ref.stock_param.logger.info(
        "init writer csv separateur: %s (%s)",
        separ,
        self.regle_ref.getvar("separ_csv_out"),
    )
    self.regle_ref.stock_param.logger.debug(
        "init writer csv parametres: %s ", repr(self.writerparms)
    )
    headerdef = self.regle_ref.getvar("csvheader")
    header = "csv_f" if "no!" in headerdef else "csv"
    initwriter(self, "csv", header, (";" if separ == "#std" else separ), "")
    if "up" in headerdef:
        self.headerfonc = str.upper
    elif "low" in headerdef:
        self.headerfonc = str.lower
    else:
        self.headerfonc = str
    # print("initwriter csv ", self)


def init_txt(self):
    """writer txt separateur tab pour le mode copy de postgres"""
    separ = self.regle_ref.getchain(("separ_txt_out", "separ_txt", "sep"), "\t")
    ext = self.regle_ref.getvar("ext", "txt")
    initwriter(self, ext, False, ("\t" if separ == "#std" else separ), "")


def init_geo(self):
    """writer geo covadis"""
    initwriter(self, "geo", False, "  ", "")


def init_sql(self):
    """writer sql :  mode copy avec gestion des triggers et des sequences"""
    initwriter(self, "sql", "sql", "\t", r"\N", writerclass=SqlWriter)
    if self.dialecte == "":
        self.dialecte = "natif"
    else:
        # dialecte = dialecte if dialecte in DATABASES else "sql"
        self.writerparms["dialecte"] = getdb(self.dialecte)
        self.writerparms["base_dest"] = self.destination
        self.writerparms["destination"] = self.fich
        if self.dialecte == "sigli":
            self.writerparms["sys_gid"] = "gid"

    # gestion des dialectes sql et du mode connecté
    self.writerparms["reinit"] = self.regle_ref.getvar("reinit")
    self.writerparms["nodata"] = self.regle_ref.getvar("nodata")
    if self.destination:  # on va essayer de se connecter
        connection = self.regle_ref.stock_param.getdbaccess(
            self.regle_ref, self.destination
        )
        if connection and connection.valide:
            self.gensql = connection.gensql  # la on a une instance connectee
    elif "dialecte" in self.writerparms:
        self.gensql = self.writerparms["dialecte"].gensql()


def lire_objets_txt(self, rep, chemin, fichier):
    """format sans entete le schema doit etre fourni par ailleurs"""
    separ = self.regle_ref.getchain(("separ_txt_in", "separ_txt", "sep"), "\t")
    schema = self.regle_ref.stock_param.schemas.get(
        self.regle_ref.getvar("schema_entree")
    )
    if schema:
        # geom = separ + "geometrie" + "\n" if schema.info["type_geom"] else "\n"
        # entete = separ.join(schema.get_liste_attributs()) + geom
        entete = schema.get_liste_attributs()
        if schema.info["type_geom"] > "0":
            entete.append(self.schemaclasse.info["nom_geometrie"])
    else:
        entete = None
    return csvreader(self, rep, chemin, fichier, entete=entete, separ=separ)

    # return _lire_objets_csv(self, rep, chemin, fichier, entete, separ=separ)


def lire_objets_csv(self, rep, chemin, fichier):
    """format csv en lecture"""
    headerdef = self.regle_ref.getvar("csvheader")
    header = headerdef.split(",") if headerdef else None
    return csvreader(self, rep, chemin, fichier, entete=header)


# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom,initer)
WRITERS = {
    "csvj": ("", "", True, "low", 0, "csv", "classe", "#geojson", "#ewkt", init_csv),
    "csv": ("", "", True, "low", 0, "csv", "classe", "#ewkt", "#ewkt", init_csv),
    "txt": ("", "", True, "low", 0, "txt", "classe", "#ewkt", "#ewkt", init_txt),
    "sql": ("", "", True, "low", 0, "txt", "all", "#ewkt", "#ewkt", init_sql),
    "geo": ("", "", True, "low", 0, "txt", "classe", "#ewkt", "#ewkt", init_geo),
}

#                  reader,geom,hasschema,auxfiles,initer
READERS = {
    "csv": (lire_objets_csv, "#ewkt", True, (), None, attreader),
    "txt": (lire_objets_txt, "#ewkt", True, (), None, None),
}
