# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 09:28:45 2014

@author: 89965
"""
import copy

import re
import logging
from collections import defaultdict
from .elements import attribut as A
from .elements import schemaclasse as C
from .elements import mapping as M
from .abbrev import dic_abrev as abbr
from .fonctions_schema import analyse_interne, analyse_conformites, ajuste_schema

# schemas : description de la structure des objets
LOGGER = logging.getLogger(__name__)

TYPES_G = C.TYPES_G
CODES_G = C.CODES_G


def get_attribut(nom, vmax):
    """ recupere une structure d'attribut pour creer des modeles"""
    return A.Attribut(nom, vmax, nom_conformite="")


def init_schema(
    mapper,
    nom_schema,
    origine="G",
    fich="",
    defmodeconf=0,
    stable=True,
    modele=None,
    copie=False,
    force=False,
):
    """ retourne le schemas qui va bien et les cree si necsssaire """
    if not nom_schema:  # on demande un schema temporaire
        return Schema("##tmp", origine=origine, fich=fich, defmodeconf=defmodeconf)
    # print(
    #     "demande schema ",
    #     nom_schema,
    #     "creation",
    #     nom_schema not in mapper.schemas,
    #     modele,
    # )
    if not mapper:  # on demande un schema temporaire nomme
        return Schema(nom_schema, origine=origine, fich=fich, defmodeconf=defmodeconf)
    if isinstance(modele, str):
        if modele in mapper.schemas:
            modele = mapper.schemas[modele]
        else:
            print("schema introuvable", modele, "dans", mapper.schemas.keys())
            modele = None
    if nom_schema not in mapper.schemas or force:
        nouveau = Schema(
            nom_schema, origine=origine, fich=fich, defmodeconf=defmodeconf
        )
        mapper.schemas[nom_schema] = nouveau
        nouveau.stable = stable
        nouveau.metas["script_ref"] = mapper.getvar("pyetl_script_ref")
        #            self.schemas[nom_schema].modele = modele
        #        print (nom_schema, 'creation schema', modele.nom if modele else 'init')

        if modele is not None:  # on transmet les informations specifiques
            nouveau.elements_specifiques = copy.deepcopy(modele.elements_specifiques)
            nouveau.alias_groupes = dict(modele.alias_groupes)
            nouveau.dbsql = modele.dbsql
            if copie:  # la on fait une copie conforme
                nouveau.origine = modele.origine
                for ident in modele.classes:
                    modele.classes[ident].copy(ident, nouveau)

    #                self.schemas[nom_schema].dic_abrev = modele.dic_abrev
    if mapper.schemas[nom_schema].origine is None:
        print("schema incorrect", origine, modele)
        raise ValueError
    return mapper.schemas[nom_schema]


def choix_multi(schemaclasse, ren, rec, negniv, negclass, nocase):
    """ determine si une table est a retenir """
    if nocase:
        # print("choix_multi", schemaclasse.identclasse)
        # print(
        #     bool(ren.search(schemaclasse.groupe.lower())),
        #     bool(rec.search(schemaclasse.nom.lower())),
        # )
        return (
            bool(ren.search(schemaclasse.groupe.lower())) != negniv
            and bool(rec.search(schemaclasse.nom.lower())) != negclass
        )
    return (
        bool(ren.search(schemaclasse.groupe)) != negniv
        and bool(rec.search(schemaclasse.nom)) != negclass
    )


def choix_simple(schemaclasse, exp_niv, exp_class, negniv, negclass, nocase):
    """ determine si une table est a retenir """
    groupe = schemaclasse.groupe.lower() if nocase else schemaclasse.groupe
    vniv = groupe == exp_niv if exp_niv else True
    vniv = vniv and not negniv
    nom = schemaclasse.nom.lower() if nocase else schemaclasse.nom
    vclass = nom == exp_class if exp_class else True
    vclass = vclass and not negclass
    #    if vniv and vclass:
    #        print ('choix simple ',groupe,nom,exp_niv,'.',exp_class)
    return vniv and vclass


def compile_regex(regex):
    """ essaye de compile une regex en transformant les * en .* si ce n est deja fait """
    placeholder1 = "#1§"
    placeholder2 = "#2§"
    while placeholder1 in regex:
        placeholder1 += "§"
    while placeholder2 in regex:
        placeholder2 += "§"

    tmp = regex.replace(".*", placeholder1)
    tmp = tmp.replace("]*", placeholder2)
    tmp = tmp.replace("*", ".*")
    tmp = tmp.replace(placeholder2, "]*")
    tmp = tmp.replace(placeholder1, ".*")

    try:
        creg = re.compile(tmp)
    except:
        print("erreur compil", tmp)
        creg = None
    return creg


class Schema(object):
    """definition d'un schema : ensemble de classes et de conformites
    code origine : L schema lu
                   B base de donnees / fichier
                   S schema de sortie
                   G schema généré
    """

    # types_G={0:"ALPHA",1:"POINT",2:"LIGNE",3:"POLYGONE",4:""}
    dic_abrev = abbr
    analyse_interne = analyse_interne
    analyse_conformites = analyse_conformites
    ajuste = ajuste_schema

    def __init__(self, nom_schema, fich="", origine="G", defmodeconf=0, alias=""):
        self.classes = dict()
        self.nocase = dict()
        self.conformites = dict()
        self.defmodeconf = defmodeconf
        self.taux_conformite = 10
        self.direct = dict()
        #        self.dic_abrev = dict()
        self.stock_mapping = M.Mapping()
        self.origine = (
            origine  # G: schema genere L: schema lu S: schema de sortie B: schema base
        )
        self.systeme_orig = (
            "def"  # systeme d'origine : permets de gerer les particularites
        )
        self.metas = dict()  # metadonnees du schema
        self.modele = None
        self.nom = nom_schema
        self.fich = fich if fich else self.nom
        self.alias = alias
        self.conf_deja_analyse = False
        self.mode_sortie = None
        self.elements_specifiques = dict()
        self.init = False  # le schema a ete analyse en mode initial
        #        self.dialecte = None # dialecte (sql)
        self.format_sortie = ""  # format de sortie
        #        self.rep_sortie = ''
        self.dbsql = None  # generateur sql
        self.alias_groupes = dict()
        self.groupes = dict()
        self.compteurs = defaultdict(int)
        self.stable = True
        self.pending = False

    def __repr__(self):
        return "schema:" + self.nom + " " + str(len(self.classes)) + " classes"

    def copy(self, nom=None):
        "retourne une copie du schema "
        nouveau = Schema(self.nom if nom is None else nom)
        nouveau.from_dic_if(self.__dic_if__)
        return nouveau

    def resolve(self):
        "genere les schemas non totalement resolus"
        if self.pending:
            for cl in self.classes:
                cl.resolve
        self.pending = False

    @property
    def __dic_if__(self):
        """retourne une interface de transfert"""
        infos = {
            "defmodeconf",
            "taux_conformite",
            "origine",
            "systeme_orig",
            "metas",
            "nom",
            "fich",
            "alias",
            "elements_specifiques",
            "alias_groupes",
            "compteurs",
        }

        d_if = {i: getattr(self, i) for i in infos}
        d_if["__infos__"] = infos
        d_if["classes"] = {
            nom: cl.__dic_if__ for nom, cl in self.classes.items() if cl.a_sortir
        }
        d_if["conformites"] = {
            nom: conf.__dic_if__ for nom, conf in self.conformites.items()
        }
        d_if["stock_mapping"] = self.stock_mapping.__dic_if__
        return d_if

    def from_dic_if(self, d_if):
        """regenere la structure apres transfert"""
        for i in d_if["__infos__"]:
            setattr(self, i, d_if[i])
        for conf, cd_if in d_if["conformites"].items():
            self.get_conf(conf).from_dic_if(cd_if)
        for ident, cd_if in d_if["classes"].items():
            sc_classe = self.setdefault_classe(ident)
            sc_classe.from_dic_if(cd_if)
            #            print ('recup schemaclasse',sc_classe)
            self.gere_conformites(sc_classe)

        self.stock_mapping.from_dic_if(d_if["stock_mapping"])

    #        print ('fin recup_schema')

    def ajout_classe(self, sc_classe):
        """ajoute une classe dans un schema"""
        ident = sc_classe.identclasse
        self.classes[ident] = sc_classe
        self.direct[ident[1]] = ident
        niv, cla = ident
        nocase = (niv.lower(), cla.lower())
        self.nocase[nocase] = ident
        if ident[0] not in self.groupes:
            self.groupes[ident[0]] = 1
        else:
            self.groupes[ident[0]] += 1
        sc_classe.schema = self
        # print("sci:ajout_classe", self.nom, len(self.classes))
        return sc_classe

    def get_classe(self, ident, cree=False, modele=None, filiation=False, guess=False):
        """ recupere la description d'une classe"""
        schema_classe = self.classes.get(ident)
        if schema_classe:
            return schema_classe
        # on tente une recherche par le nom s il n'y a pas de groupe
        if not ident[0] or guess == 1:
            schema_classe = self.classes.get(self.direct.get(ident[1]))
            if schema_classe:
                return schema_classe
        if guess == 2:
            classe = self.guess_classe(ident[1])
            if classe:
                return classe
        if cree:  # on va tenter de creer la classe
            return self._cree_classe(ident, modele, filiation)

    def guess_classe(self, nom):
        """ essaye de matcher une classe au mieux avec un nom approximatif """
        ref = nom.lower()
        for i in self.classes:
            if i[1].lower() == ref:
                return self.classes[i]
        for i in self.classes:
            if ref in i[1].lower():
                return self.classes[i]
        for i in self.classes:
            if i[1].lower() in ref:
                return self.classes[i]
        return None

    def renomme_classe(self, ancien_ident, nouvel_ident, spec=False):
        """gere un renommage de classe en terant compte des clefs etrangeres"""
        #        print ('renommage classe ',self.nom,ancien_nom, nouveau_nom)
        classe = self.classes[ancien_ident]
        classe.setidentclasse(nouvel_ident)
        self.supp_classe(ancien_ident, force=True)
        self.ajout_classe(classe)
        for scl in self.classes.values():
            scl.renomme_cible_classe(ancien_ident, nouvel_ident)
        self.liste_groupes()

    def supp_classe(self, ident, force=False):
        """supprime une classe du schema"""
        if ident in self.classes and (self.classes[ident].objcnt == 0 or force):
            del self.classes[ident]
            niv, cla = ident
            nocase = (niv.lower(), cla.lower())
            del self.nocase[nocase]
            self.liste_groupes()

    def gere_conformites(self, schemaclasse):
        """ recree les liens de conformites vers classe """
        for i in schemaclasse.attributs:
            # il faut verifier les conformites
            nom_conf = schemaclasse.attributs[i].nom_conformite
            # print (i,cf.nom if cf else "non reference")
            if nom_conf:
                # n = n+1
                if nom_conf in self.conformites:
                    # elle existe deja on se branche dessus
                    schemaclasse.attributs[i].conformite = self.conformites[nom_conf]
                    # n2 += 1
                else:
                    print("conformite inconnue", nom_conf)  # on la stocke
                    schemaclasse.attributs[i].nom_conformite = ""

    def _cree_classe(self, ident, modele, filiation=True):
        """copie du schema d'une classe vers un nouveau schema avec gestion des conformites"""
        #        print ('avant copie',modele.type_geom, modele)
        if modele is None:  # on cree une classe a partir de 0
            return self.setdefault_classe(ident)
        #        on recopie le modele
        old_schema = modele.schema  # on evite de recopier toute la structure
        old_fils = modele.fils
        old_regles_modif = modele.regles_modif
        #        print ("copie schema ",ident,modele.identclasse)
        modele.schema = None
        modele.fils = None
        modele.regles_modif = None
        groupe, nom = ident
        nouvelle_classe = copy.deepcopy(modele)
        nouvelle_classe.nom = nom
        nouvelle_classe.groupe = groupe
        nouvelle_classe.objcnt = 0
        nouvelle_classe.settype_table("i")
        nouvelle_classe.deleted = modele.deleted
        modele.schema = old_schema
        modele.fils = old_fils
        modele.regles_modif = old_regles_modif
        if filiation:
            old_fils.append(nouvelle_classe)  # gestion des filiations de classes
        # n = 0
        # n2 = 0
        nouvelle_classe.regles_modif = set()
        nouvelle_classe.fils = []
        for i in nouvelle_classe.attributs:
            # il faut verifier les conformites
            conf = nouvelle_classe.attributs[i].conformite
            # print (i,cf.nom if cf else "non reference")
            if conf:
                # n = n+1
                if conf.nom in self.conformites:
                    # elle existe deja on se branche dessus
                    nouvelle_classe.attributs[i].conformite = self.conformites[conf.nom]
                    # n2 += 1
                else:
                    self.conformites[conf.nom] = conf  # on la stocke
        self.ajout_classe(nouvelle_classe)
        #        print ('copie schema',self.nom, modele.identclasse,modele,
        #                nouvelle_classe.identclasse,nouvelle_classe, modele.info['type_geom'],
        #                nouvelle_classe.info["type_geom"])

        return nouvelle_classe

    def calcule_cibles(self):
        """determine quelles ont les classes cibles de fk"""
        for i in self.classes:
            for j in self.classes[i].fkey_dep:
                self.classes[j].cibles.add(i)

    def is_cible(self, ident):
        """ determine si une table est cible de clef etrangere"""
        return self.classes[ident].cibles

    def setdefault_classe(self, ident):
        """ trouve une classe ou la cree au besoin"""
        if ident in self.classes:
            return self.classes[ident]
        return self.ajout_classe(C.SchemaClasse(ident, self))

    # -------------------gestion interne des mappings ---------------------------#
    def mapping_schema(self, fusion=False):
        """retourne les origines des classes"""
        return self.stock_mapping.mapping_schema(self.classes, fusion)

    def init_mapping(self, liste_mapping):
        """traitement des mappings initialisation des structures"""
        return self.stock_mapping.init_mapping(self.classes, liste_mapping)

    def map_classes(self):
        """ force les origines des classes"""
        return self.stock_mapping.map_classes(self.classes)

    def map_dest(self, id_orig, virtuel=False):
        """ force les origines des classes"""

        id2 = self.stock_mapping.map_dest(id_orig)
        if id2 is None:
            if not virtuel:
                print(
                    "attention mapping destination impossible",
                    self.nom,
                    id_orig,
                    self.classes,
                )
            return id_orig
        return id2

    def map_orig(self, id_dest):
        """ force les origines des classes"""
        return self.stock_mapping.map_orig(id_dest)

    def mapping(self, id_classe):
        """#retourne un identifiant complet et une origine complete"""
        return self.stock_mapping.mapping(self.classes, id_classe)

    # -------------------------------------------------------------------------#

    def liste_classes(self, groupe):
        """ retourne la liste des classes d'un groupe"""
        return [i for i in self.classes if i[0] == groupe]

    def liste_groupes(self):
        """ retourne la liste des groupes d'un schema"""
        groupes = dict()
        for i in self.classes:
            groupes[i[0]] = (groupes[i[0]] + 1) if i[0] in groupes else 1
        self.groupes = groupes
        return sorted(groupes.keys())

    def stat_schema(self):
        """ sort les stats standard"""
        groupes = self.liste_groupes()
        print(
            "schema : stat schema",
            self.nom,
            len(groupes),
            len(self.classes),
            len(self.conformites),
        )

    def get_conf(self, nom_conf, type_c="", mode=1):
        """ retourne une conformite en la creeant si besoin"""
        conf = self.conformites.get(nom_conf)
        if conf:
            return conf
        conf = A.Conformite(nom_conf, type_c, mode)
        self.conformites[nom_conf] = conf
        return conf

    def adapte_attributs(self, fonction):
        """ajuste les noms dans le schema pour tenir compte des contraintes du sql"""
        for i in self.classes:
            self.classes[i].adapte_attributs(fonction)

    def setbasic(self, mode):
        """simplifie un schema pour supprimer les enums et les liens / fonctions vues etc..."""
        if mode == "basic":
            self.conformites = dict()
        for i in self.classes:
            self.classes[i].setbasic(mode)
        self.elements_specifiques = {}

    def valide_condition(self, classe, tables):
        """ valide la selection du type de tables"""
        return tables == "a" or self.classes[classe].type_table in tables

    def single_select(self, condition, tables, indice, multi, nocase, neg):
        """selectionne un niveeau entier"""
        if multi:
            tmp = {i for i in self.classes if (condition.match(i[indice])) != neg}
        elif nocase:
            niveau = condition.lower()
            tmp = {i for i in self.classes if (i[indice].lower() == niveau) != neg}
        else:
            tmp = {i for i in self.classes if (i[indice] == condition) != neg}

        return {i for i in tmp if self.valide_condition(i, tables)}

    def select_classe(self, classe, tables, multi, nocase, neg):
        """selectionne un niveeau entier"""
        return self.single_select(classe, tables, 1, multi, nocase, neg)

    def select_niveau(self, niveau, tables, multi, nocase, neg):
        """selectionne un niveeau entier"""
        return self.single_select(niveau, tables, 0, multi, nocase, neg)

    def select_niv_classe(
        self, niveau, classe, attr, tables=None, multi=True, nocase=False
    ):
        """selectionne des classes a partir d une seule description"""
        # print("select_niv_classes", niveau, classe, attr, tables, multi)
        LOGGER.debug(
            "select_niv_classes %s %s %s %s %s",
            niveau,
            classe,
            attr,
            tables,
            str(multi),
        )
        # if niveau is None or classe is None:
        #     return []
        if not tables:
            tables = {"A"}
        tables = "".join(tables)
        tables_a_sortir = set()
        exp_niv = niveau.strip() if niveau else ""
        exp_clas = classe.strip() if classe else ""
        convert = {"v": "vm", "t": "r", "r": "r"}
        tables = convert.get(tables.lower(), tables.lower())
        lmulti = multi
        if nocase:
            exp_niv = exp_niv.lower()
            exp_clas = exp_clas.lower()
        negniv = False
        negclass = False
        if exp_niv and exp_niv[0] == "!":
            negniv = True
            exp_niv = exp_niv[1:]
        if exp_clas and exp_clas[0] == "!":
            negclass = True
            exp_clas = exp_clas[1:]
        if "*" in exp_clas or not exp_clas:
            lmulti = True
        if negniv or negclass:
            lmulti = True
        if not exp_niv:
            lmulti = True
        # print("select_niv_classes n:", exp_niv, "c:", exp_clas, attr, tables, lmulti)
        if lmulti:
            if exp_niv and not multi:
                exp_niv = "^" + exp_niv if not exp_niv.startswith("^") else exp_niv
                exp_niv = exp_niv + "$" if not exp_niv.endswith("$") else exp_niv
            if exp_clas and not multi:
                exp_clas = "^" + exp_clas if not exp_clas.startswith("^") else exp_clas
                exp_clas = exp_clas + "$" if not exp_clas.endswith("$") else exp_clas
            ren = compile_regex(exp_niv)
            if ren is None:
                print("erreur de description de niveau ", exp_niv)
                return set()
            rec = compile_regex(exp_clas)
            if rec is None:
                print("erreur de description de classe ", exp_clas)
                return set()
            # print("selection ", exp_niv, exp_clas)
            for i in self.classes:
                if tables != "a" and self.classes[i].type_table not in tables:
                    # print("non retenu", tables, self.classes[i].type_table)
                    continue
                if choix_multi(self.classes[i], ren, rec, negniv, negclass, nocase):
                    if not attr or attr in self.classes[i].attributs:
                        tables_a_sortir.add(i)

        else:
            if nocase:
                idclas = self.nocase.get((exp_niv.lower(), exp_clas.lower()))
            else:
                idclas = (exp_niv, exp_clas)
                if idclas not in self.classes:
                    idclas = None
            if idclas:
                if tables == "a" or self.classes[idclas].type_table in tables:
                    if not attr or attr in self.classes[idclas].attributs:
                        tables_a_sortir.add(idclas)

        return tables_a_sortir

    #    print('db: Nombre de tables a sortir:', len(tables_a_sortir))

    def select_classes(
        self, niveau, classe, attr, tables="A", multi=True, nocase=False
    ):
        """produit la liste des classes demandees a partir du schema utile pour id_in:"""
        # print("select_classes", niveau, classe, attr)
        if niveau is None or classe is None:
            return []
        tables_a_sortir = set()
        if len(niveau) == 1 and niveau[0][:2] == "s:":  # selection directe
            ident = niveau[0][:2]
            if ident in self.classes:
                return [ident]
            else:
                return []
        convert = {"v": "vm", "t": "r"}
        tables = convert.get(tables.lower(), tables.lower())
        for exp_niv, exp_clas in zip(niveau, classe):
            tables_a_sortir.update(
                self.select_niv_classe(exp_niv, exp_clas, attr, tables, multi, nocase)
            )

        if not tables_a_sortir:
            print("pas de tables a sortir")
            print("select tables: requete", tables, niveau, classe, multi)
            print("taille schema", self.nom, len(self.classes))
        return list(tables_a_sortir)

    def fkref(self, liste, niveau, niv_ref, add=False):
        """identifie les tables referenceees par des fk"""
        trouve = 0
        adds = set()
        for ident in liste:
            if niveau[ident] == niv_ref:
                cibles = self.is_cible(ident)
                #            print(ident,":tables  visant la classe",cibles)
                for j in cibles:
                    if j not in niveau:
                        if add:
                            adds.add(j)
                            trouve = 1
                            # print("fkref: ajout cible", niv_ref, j)
                        else:
                            LOGGER.warning(
                                "cible foreign key non selectionnée %s , (%d)",
                                j,
                                niv_ref,
                            )
                            # print("fkref: erreur cible", niv_ref, j)
                        continue
                    if niveau[j] >= niv_ref and j != ident:
                        if ident in self.is_cible(j):
                            print("attention references croisees", ident, j)
                        else:
                            niveau[ident] += 1
                            # print(" trouve", ident, niveau[ident], j)
                            trouve = 1
                        break
        return trouve, adds

    def tablesorter(self, liste, complete=False):
        """ trie les tables en fonction des cibles de clef etrangeres """
        ajouts = True
        niveau = dict()
        tables = set(liste)
        while ajouts:
            ajouts = set()
            self.calcule_cibles()
            niveau = {i: 0 for i in tables}
            trouve = 1
            niv_ref = 0
            while trouve:
                trouve, adds = self.fkref(tables, niveau, niv_ref, add=complete)
                ajouts.update(adds)
                niv_ref += 1
            #    print("niveau maxi", niv_ref)
            if complete and ajouts:
                tables.update(ajouts)
        niv2 = {i: "%5.5d_%s.%s" % (99999 - niveau[i], *i) for i in niveau}
        liste.clear()
        liste.extend(sorted(tables, key=niv2.get))
        return niveau

    def creschematravail(self, regle, liste, nomschema, liste_mapping=None):
        """cree un schema de travail a partir d une liste de classes"""
        params = regle.stock_param
        nomschema = nomschema if nomschema else self.nom.replace("#", "")
        schema_travail = init_schema(params, nomschema, "B", modele=self)
        schema_travail.metas.update(self.metas)
        complete = regle.getvar("gestion_coherence") == "1"
        liste2 = liste[:]
        niv = self.tablesorter(liste2, complete=complete)
        for ident in liste2:
            classe = self.get_classe(ident)
            classe.resolve()
            #        print ('classe a copier ',classe.identclasse,classe.attributs)
            clas2 = classe.copy(ident, schema_travail)
            clas2.setinfo("objcnt_init", classe.getinfo("objcnt_init", "0"))
            # on renseigne le nombre d'objets de la table
            clas2.settype_table(classe.type_table)
        return schema_travail, liste2

    def getschematravail(
        self, regle, niveau, classe, tables="A", multi=True, nocase=False, nomschema=""
    ):
        """recupere le schema de travail"""
        # print ( 'schema base ',connect.schemabase.classes.keys())
        liste = self.select_classes(niveau, classe, [], tables, multi, nocase)
        schema_travail, liste2 = self.creschematravail(regle, liste, nomschema)
        schema_travail.metas["tables"] = tables
        schema_travail.metas["filtre niveau"] = ",".join(niveau) if niveau else ""
        schema_travail.metas["filtre classe"] = ",".join(classe) if classe else ""
        # print("recup schema travail", schema_travail.metas)
        return schema_travail, liste2

    def cleanrules(self):
        for classe in self.classes.values():
            classe.regles_modif = set()

    def printelements_specifiques(self):
        print(
            self.nom,
            ":elements specifiques",
            [(i, len(j[1])) for i, j in self.elements_specifiques.items()],
        )
