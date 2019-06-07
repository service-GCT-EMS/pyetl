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
import codecs

# from numba import jit
from .fileio import FileWriter

#########################################################################
# format csv et txt geo etc
# tous les fichiers tabules avec ou sans entete
#########################################################################
# def getnoms(rep, chemin, fichier):
#     """ determine les noms de groupe et de schema"""
#     schema = ["schema"]
#     chem = chemin
#     niveaux = []
#     classe = os.path.splitext(fichier)[0]
#     if rep and rep != ".":
#         schema = os.path.basename(rep)
#     while chem:
#         chem, nom = os.path.split(chem)
#         niveaux.append(nom)

#     if not niveaux:
#         groupe = ""
#     else:
#         groupe = "_".join(niveaux)
#     #    print(rep, "<>", chemin, "<>", fichier, "traitement", schema, "<>", groupe, "<>", classe)
#     return schema, groupe, classe


def decode_entetes_csv(reader, entete, separ):
    """prepare l'entete et les noma d'un fichier csv"""
    # geom = False
    #    print('decodage entete csv',schema_courant.nom if schema_courant else '' ,entete)
    # if (nom_groupe, nom_classe) in schema_courant.classes:
    #     schemaclasse = schema_courant.classes[(nom_groupe, nom_classe)]
    #     noms_attributs = schemaclasse.get_liste_attributs()
    #     geom = schemaclasse.info["type_geom"] != "0"
    # else:
    #     schemaclasse = schema_courant.setdefault_classe((nom_groupe, nom_classe))
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
        noms_attributs[-1]='#geom'
        # geom = True
        # noms_attributs.pop(-1)  # on supprime la geom en attribut classique
    if reader.newschema:
        for i in noms_attributs:
            if i[0] != "#":
                reader.schemaclasse.stocke_attribut(i, "T")
    #    else: # on adapte le schema force pur eviter les incoherences
    #        schemaclasse.adapte_schema_classe(noms_attributs)

    return noms_attributs


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


def _lire_objets_csv(reader, rep, chemin, fichier, entete=None, separ=None):
    """lit des objets a partir d'un fichier csv"""
    reader.prepare_lecture_fichier(rep,chemin,fichier)
    reader.setidententree(reader.groupe, reader.classe)

    if separ is None:
        separ = reader.separ
    # nom_schema, nom_groupe, nom_classe = getnoms(rep, chemin, fichier)
    try:
        with open(os.path.join(rep, chemin, fichier), "r", encoding=reader.encoding) as fich:
            if not entete:
                entete = fich.readline()[:-1]
                # si l'entete n'est pas fourni on le lit dans le fichier
            if entete[0] == "!":
                entete = entete[1:]
            else:  # il faut l'inventer...
                entete = separ * len(fich.readline()[:-1].split(separ))
                fich.seek(0)  # on remet le fichier au debut
            noms_attributs= decode_entetes_csv(reader,entete, separ)
            reader.prepare_attlist(noms_attributs)
            type_geom = '-1' if noms_attributs[-1]=='#geom' else '0'
            controle = len(noms_attributs)
            nbwarn = 0
            nlignes = 0
            for i in fich:
                # nlignes = nlignes + 1

                val_attributs = [j.strip() for j in i[:-1].split(separ)]
                # liste_attributs = zip(noms_attributs, val_attributs)
                # print ('lecture_csv:',[i for i in liste_attributs])
                if len(val_attributs) != controle:
                    nbwarn = _controle_nb_champs(val_attributs, controle, nbwarn, i)
                obj = reader.getobj(valeurs=val_attributs)
                # print ('attributs:',obj.attributs['nombre_de_servitudes'])
                # if geom:
                #     obj.geom = [val_attributs[-1]]
                #     #                print ('geometrie',obj.geom)
                obj.attributs["#type_geom"] = type_geom
                # else:
                #     obj.attributs["#type_geom"] = "0"
                obj.attributs["#chemin"] = chemin
                # reader.traite_objets(obj, reader.regle_start)
                reader.process(obj)

                # if maxobj and nlignes >= maxobj:  # nombre maxi d'objets a lire par fichier
                #     break

                # if nlignes % 100000 == 0:
                #     regle_ref.stock_param.aff.send(("interm", 0, nlignes))
                #     # gestion des affichages de patience
    except UnicodeError:
        print("erreur encodage le fichier", fichier, "n'est pas en ", reader.encoding)
    if nbwarn:
        print(nbwarn, "lignes avec un nombre d'attributs incorrect")
    return


class CsvWriter(FileWriter):
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
        geomwriter=None,
    ):

        super().__init__(
            nom,
            encoding=encoding,
            schema=schema,
            f_sortie=f_sortie,
            geomwriter=geomwriter,
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
        self.encoding = encoding
        self.transtable = str.maketrans(
            {"\n": "\\" + "n", "\r": "\\" + "n", self.separ: self.escape}
        )

    def header(self, init=1):
        """ preparation de l'entete du fichiersr csv"""
        print("csvheader ", self.entete)
        if not self.entete:
            #            raise
            return ""
        geom = self.separ + "geometrie" + "\n" if self.schema.info["type_geom"] != "0" else "\n"
        return "!" + self.separ.join(self.liste_att) + geom

    def prepare_attributs(self, obj):
        ''' prepare la es attributs en fonction du format'''
        atlist = (str(obj.attributs.get(i, "")).translate(self.transtable) for i in self.liste_att)
        #        print ('ectriture_csv',self.schema.type_geom, obj.format_natif,
        #                obj.geomnatif, obj.type_geom)
        #        print ('orig',obj.attributs)
        attributs = self.separ.join((i if i else self.null for i in atlist))
        return attributs


    def write(self, obj):
        """ecrit un objet"""
        if obj.virtuel:
            return False  #  les objets virtuels ne sont pas sortis
        attributs = self.prepare_attributs(obj)
        # atlist = (str(obj.attributs.get(i, "")).translate(self.transtable) for i in self.liste_att)
        #        print ('ectriture_csv',self.schema.type_geom, obj.format_natif,
        #                obj.geomnatif, obj.type_geom)
        #        print ('orig',obj.attributs)
        # attributs = self.separ.join((i if i else self.null for i in atlist))
        if self.type_geom != "0":
            if obj.format_natif == "#ewkt" and obj.geomnatif:  # on a pas change la geometrie
                geom = obj.attributs['#geom']
                if not geom:
                    geom = self.null  # on recupere la geometrie native
            #                print("sortie ewkt geom0",len(geom))
            else:
                if obj.initgeom():
                    geom = self.geomwriter(obj.geom_v, self.type_geom, self.multi, obj.erreurs)
                else:
                    if not obj.attributs['#geom'] and self.type_geom == "-1":
                        geom = self.null
                    else:
                        print(
                            "csv: geometrie invalide : erreur geometrique",
                            obj.ident,
                            obj.numobj,
                            "demandé:",
                            self.type_geom,
                            obj.geom_v.erreurs.errs,
                            obj.attributs["#type_geom"],
                            self.schema.info["type_geom"],
                            obj.attributs['#geom'],
                        )
                        geom = ""

                obj.format_natif = "#ewkt"
                obj.attributs['#geom'] = geom
                obj.geomnatif = True
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
                    )
                    print("prep ligne ", attributs, "G:", geom)

                    return False
            if not geom:
                geom = self.null
            ligne = attributs + self.separ + geom
        else:
            ligne = attributs
        if self.writerparms.get("nodata"):
            return False

        #        print("sortie ewkt",len(geom))

        self.fichier.write(ligne)
        self.fichier.write("\n")
#        self.stats[self.nom] += 1
        return True


class SqlWriter(CsvWriter):
    """getionnaire decriture sql en fichier"""

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
        geomwriter=None,
    ):
        super().__init__(
            nom,
            schema,
            extension,
            separ,
            entete,
            encoding,
            null,
            f_sortie,
            geomwriter=geomwriter,
        )
        if self.writerparms:
            self.schema.setsortie(self.f_sortie)
        self.transtable = str.maketrans(
            {"\\": r"\\", "\n": "\\" + "n", "\r": "\\" + "n", self.separ: self.escape}
        )
        self.htranstable = str.maketrans(
            {"\\": r"\\", "\n": "\\" + "n", "\r": "\\" + "n", '"':r'""', self.separ: self.escape}
        )



    def __repr__(self):
        return ('sqlwriter '+self.nom)

    def prepare_hstore(self, val):
        ''' gere le cas particulier du hstore '''



    def prepare_attributs(self, obj):
        ''' prepare la es attributs en fonction du format'''
        if obj.hdict:
            # atlist = []
            atlist = (", ".join(['"'+i+'" => "'+str(j).translate(self.htranstable)+'"' for i, j in sorted(obj.hdict[nom].items())]) if nom in obj.hdict else
            str(obj.attributs.get(nom, "")).translate(self.transtable) for nom in self.liste_att)
            # for nom in self.liste_att:
            #     if nom in obj.hdict:
            #         val = ", ".join(['"'+i+'" => "'+str(j).translate(self.htranstable)+'"' for i, j in sorted(obj.hdict[nom].items())])
            #         atlist.append(val)
            #         # print ('traitement hdict', nom, val)
            #     else:
            #         atlist.append(obj.attributs.get(nom, "").translate(self.transtable))
        else:
            atlist = (str(obj.attributs.get(i, "")).translate(self.transtable) for i in self.liste_att)
        return self.separ.join((i if i else self.null for i in atlist))

        # atlist = (str(obj.attributs.get(i, "")).translate(self.transtable) for i in self.liste_att)
        # #        print ('ectriture_csv',self.schema.type_geom, obj.format_natif,
        # #                obj.geomnatif, obj.type_geom)
        # #        print ('orig',obj.attributs)
        # attributs = self.separ.join((i if i else self.null for i in atlist))
        # return attributs

    def header(self, init=1):
        separ = ","
        gensql = self.schema.schema.dbsql
        if not gensql:
            print(
                "header sql: erreur generateur sql non defini",
                self.schema.schema.nom,
                self.schema.identclasse,
                self.schema.schema.format_sortie,
            )
            raise StopIteration(3)
        niveau, classe = self.schema.identclasse
        nouveau = self.schema.identclasse not in self.classes
        self.classes.add(self.schema.identclasse)
        prefix = "SET client_encoding = 'UTF8';\n" if init else ""
        #        print ('parametres sql ', self.writerparms)
        nodata = False

        type_geom = self.schema.info["type_geom"]
        dim = self.schema.info["dimension"]

        if self.writerparms and nouveau:
            reinit = self.writerparms.get("reinit")
            #            dialecte = self.writerparms.get('dialecte', 'sql')
            nodata = self.writerparms.get("nodata")

            gensql.initschema(self.schema.schema)
            # on positionne les infos de schema pour le generateur sql

            prefix = prefix + gensql.prefix_charge(niveau, classe, reinit, gtyp=type_geom, dim=dim)

        if nodata:
            return prefix
        prefix = prefix + 'copy "' + niveau.lower() + '"."' + classe.lower() + '" ('
        end = ") FROM stdin;"

        geom = (
            separ + "geometrie" + end + "\n" if self.schema.info["type_geom"] != "0" else end + "\n"
        )
        return prefix + separ.join([gensql.ajuste_nom(i.lower()) for i in self.liste_att]) + geom

    def fin_classe(self):
        """fin de classe pour remettre les sequences"""
        reinit = self.writerparms.get("reinit", "0")
        niveau, classe = self.schema.identclasse
        gensql = self.schema.schema.dbsql

        type_geom = self.schema.info["type_geom"]
        courbe = self.schema.info["courbe"]
        dim = self.schema.info["dimension"]
        if not gensql:
            print(
                "finclasse sql: erreur generateur sql non defini",
                self.schema.identclasse,
                self.schema.schema.format_sortie,
            )
            raise StopIteration(3)
        if self.fichier.closed:
            self.reopen()
        if self.writerparms.get("nodata"):
            self.fichier.write(gensql.tail_charge(niveau, classe, reinit))
            return
        self.fichier.write(r"\." + "\n")

        self.fichier.write(
            gensql.tail_charge(niveau, classe, reinit, gtyp=type_geom, dim=dim, courbe=courbe)
        )

    def finalise(self):
        """ligne de fin de fichier en sql"""
        self.fin_classe()
        super().finalise()
        return 3  # on ne peut pas le reouvrir

    def changeclasse(self, schemaclasse, attributs=None):
        """ ecriture de sql multiclasse on cree des entetes intermediaires"""
        #        print( 'dans changeclasse')
        # raise
        self.fin_classe()
        self.schema = schemaclasse
        if schemaclasse.info["type_geom"] == "indef":  # pas de geometrie
            schemaclasse.info["type_geom"] = "0"
        self.type_geom = schemaclasse.info["type_geom"]
        self.multi = schemaclasse.multigeom
        self.liste_att = schemaclasse.get_liste_attributs(attributs)
        self.fichier.write(self.header(init=0))


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


def change_ressource(
    regle, obj, writerclass, separ, extention, entete, null, initial=False, geomwriter=None
):
    """ change la definition de la ressource utilisee si necessaire"""

    ident = obj.ident

    ressource, nom = getfanout(regle, extention, ident, initial)
    #    ressource = sorties.get_res(regle.numero, nom)

    #    print ('change_ressoures ', regle.f_sortie.writerparms)
    if ressource is None:
        if separ is None:
            separ = regle.getchain(("separ_csv_out","separ_csv"), "|")
            print('separateur retenu',separ)
        if not nom.startswith("#"):
            #            print('creation ',nom,'rep',os.path.abspath(os.path.dirname(nom)))
            os.makedirs(os.path.dirname(nom), exist_ok=True)
        str_w = writerclass(
            nom,
            obj.schema,
            extention,
            separ,
            entete,
            encoding=regle.stock_param.get_param("codec_sortie", "utf-8"),
            null=null,
            f_sortie=regle.f_sortie,
            geomwriter=geomwriter,
        )
        ressource = regle.stock_param.sorties.creres(regle.numero, nom, str_w)
    #    print ('recup_ressource ressource stream csv' , ressource, nom, ident, ressource.etat, entete)
    regle.context.setvar("derniere_sortie", nom)
    regle.ressource = ressource
    regle.dident = ident
    return ressource


def _csvstreamer(
    writer,
    obj,
    regle,
    _,
    entete="csv",
    separ=None,
    extention=".csv",
    null="",
    writerclass=CsvWriter,
):
    """ ecrit des objets csv en streaming"""
    #    sorties = regle.stock_param.sorties
    if regle.dident == obj.ident:
        ressource = regle.ressource
    else:
        ressource = change_ressource(
            regle,
            obj,
            writerclass,
            separ,
            extention,
            entete,
            null,
            initial=True,
            geomwriter=writer.geomwriter,
        )

    ressource.write(obj, regle.numero)


#    if obj.geom_v.courbe:
#        obj.schema.info['courbe'] = '1'


def _ecrire_objets_csv(
    writer, regle, _, entete="csv", separ=None, extention=".csv", null="", writerclass=CsvWriter
):
    """ ecrit des objets csv a partir du stockage interne"""
    #    sorties = regle.stock_param.sorties
    #    numero = regle.numero
    print("csv:ecrire csv", regle.stockage.keys())
    ressource = None
    for groupe in list(regle.stockage.keys()):
        # on determine le schema
        print("csv:ecrire groupe", groupe)

        for obj in regle.recupobjets(groupe):
            #            print("csv:ecrire csv", obj)
            #            print( regle.stockage)
            #            groupe, classe = obj.ident
            if obj.ident != regle.dident:
                ressource = change_ressource(
                    regle,
                    obj,
                    writerclass,
                    separ,
                    extention,
                    entete,
                    null,
                    initial=False,
                    geomwriter=writer.geomwriter,
                )

            ressource.write(obj, regle.numero)

    #            if obj.geom_v.courbe:
    #                obj.schema.info['courbe'] = '1'
    return


def ecrire_objets_txt(self, regle, final):
    """format txt (csv sans entete) pour postgis"""
    return _ecrire_objets_csv(self, regle, final, False, "\t", ".txt")


def lire_objets_txt(self, rep, chemin, fichier):
    """format sans entete le schema doit etre fourni par ailleurs"""
    separ = self.regle_ref.get_param("separ_txt_in", self.regle_ref.get_param("separ_txt", "\t"))
    schema = self.regle_ref.stock_param.schemas.get(self.regle_ref.get_param("schema_entree"))
    if schema:
        geom = separ + "geometrie" + "\n" if schema.info["type_geom"] else "\n"
        entete = separ.join(schema.get_liste_attributs()) + geom
    else:
        entete = []
    return _lire_objets_csv(self, rep, chemin, fichier, entete, separ=separ)


def txtstreamer(self, obj, regle, final):
    """format txt en straming"""
    return _csvstreamer(self, obj, regle, final, False, "\t", ".txt")


def csvstreamer(self, obj, regle, final):
    """format txt en straming"""
    separ = self.regle.getchain(("separ_csv_out","separ_csv"), "|")
    return _csvstreamer(self, obj, regle, final, "csv", separ, ".csv")


def ecrire_objets_csv(self, regle, final):
    """format txt (csv sans entete) pour postgis"""
    separ = self.regle.getchain(("separ_csv_out","separ_csv"), "|")
    return _ecrire_objets_csv(self, regle, final, "csv", separ, ".csv")


def lire_objets_csv(self, rep, chemin, fichier):
    """format csv en lecture"""
    return _lire_objets_csv(self, rep, chemin, fichier)


def ecrire_objets_geo(self, regle, final):
    """geodatabase pour les outils topo"""
    return _ecrire_objets_csv(self, regle, final, False, "  ", ".geo")


def ecrire_objets_sql(self, regle, final):
    """format sql copy pour postgis"""

    return _ecrire_objets_csv(
        self, regle, final, "sql", "\t", ".sql", null=r"\N", writerclass=SqlWriter
    )


def sqlstreamer(self, obj, regle, final):
    """format sql copy pour postgis en streaming """

    return _csvstreamer(
        self, obj, regle, final, "sql", "\t", ".sql", null=r"\N", writerclass=SqlWriter
    )


# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {
    "csv": (ecrire_objets_csv, csvstreamer, True, "low", 0, "csv", "classe", "#ewkt", "#ewkt"),
    "txt": (ecrire_objets_txt, txtstreamer, True, "low", 0, "txt", "classe", "#ewkt", "#ewkt"),
    "sql": (ecrire_objets_sql, sqlstreamer, True, "low", 0, "txt", "all", "#ewkt", "#ewkt"),
    "geo": (ecrire_objets_geo, None, True, "low", 0, "txt", "classe", "#ewkt", "#ewkt"),
}

#                  reader,geom,hasschema,auxfiles
READERS = {"csv": (lire_objets_csv, "#ewkt", True, (), None), "txt": (lire_objets_csv, "#ewkt", True, (), None)}
