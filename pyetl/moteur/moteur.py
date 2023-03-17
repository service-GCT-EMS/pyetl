# -*- coding: utf-8 -*-
"""moteur de traitement principal : gere l'enchainement des regles """
import logging
import re
import os
import typing as T
from pyetl.formats.interne.objet import Objet  # objets et outils de gestiion
from .fonctions.outils import printexception

LOGGER = logging.getLogger(__name__)


class Moteur(object):
    """gestionnaire de traitements"""

    def __init__(self, mapper):
        self.regles = ()
        self.mapper = mapper
        self.debug = 0
        self.regle_debut = 0
        self.dupcnt = 0
        self.suppcnt = 0
        self.hasstart = False

    @property
    def regle_sortir(self):
        """retourne la regle finale"""
        return self.regles[-1]

    def setregles(self, regles, debug=0):
        self.regles = regles
        self.debug = debug
        if self.debug:
            self.debug_moteur()

    def debug_moteur(self):
        print("moteur: mode debug")
        for i in self.regles:
            print("regle:","(chargeur)" if i.chargeur else "", i)

    def traitement_virtuel(self, unique=0, schema=None):
        """cree un objet virtuel et le traite pour toutes les classes non utilisees"""

        #        if self.debug != 0:
        #        print("moteur: traitement virtuel", unique)
        LOGGER.info("traitement virtuel: %s", "chargement" if unique else "classes")
        #        for i in self.regles:
        #            print (i.chargeur, i)
        if unique:  # on lance un virtuel unique pour les traitements sans entree
            # on lance un virtuel unique puis on verifie toutes les regles de chargement
            
            self.traite_regles_chargement()
        else:
            f_v = self.mapper.getvar("force_virtuel")
            force_virtuel = False
            if f_v == "1" or f_v.lower() == "all" or f_v.lower() == "true":
                force_virtuel = True
            elif self.mapper.worker and (f_v == "worker" or f_v == "w"):
                force_virtuel = True
            elif not self.mapper.worker and (f_v == "master" or f_v == "m"):
                force_virtuel = True

            for sch in list(self.mapper.schemas.values()):
                # print("traitement virtuel: schema a traiter", sch.nom, sch.origine)
                if schema and sch.nom != schema:
                    continue
                if (
                    sch.origine in "LB" and not sch.nom.startswith("#")
                ) or sch.nom == schema:

                    LOGGER.info("traitement schema " + sch.nom + " " + sch.origine)

                    # (on ne traite que les schemas d'entree')

                    for schemaclasse in list(sch.classes.values()):
                        # print("_________traitement virtuel examen", schemaclasse.nom)
                        # print(
                        #     "traitement virtuel",
                        #     schemaclasse.nom,
                        #     schemaclasse.utilise,
                        #     force_virtuel,
                        # )
                        if schemaclasse.utilise and not force_virtuel:
                            # print(
                            #     "traitement virtuel classe ignoree",
                            #     schemaclasse.identclasse,
                            # )
                            continue
                            # if schemaclasse.identclasse == ("ELYEA", "E_PROGRA"):
                            # print(
                            #     self.mapper.getvar("_wid"),
                            #     "traitement virtuel classe",
                            #     sch.nom,
                            #     schemaclasse.identclasse,
                            #     schemaclasse.utilise,
                            #     schemaclasse.maxobj,
                            # )

                        # if not self.mapper.worker:
                        #     print("traitement objet virtuel ", schemaclasse.identclasse)
                        groupe, classe = schemaclasse.identclasse
                        obj = Objet(
                            groupe, classe, conversion="virtuel", schema=schemaclasse
                        )
                        obj.attributs["#categorie"] = "traitement_virtuel"

                        obj.attributs["#type_geom"] = schemaclasse.info["type_geom"]
                        # print("tv:traitement obj", obj.ident, self.regles[0])
                        self.traite_objet(obj, self.regles[0])

    def traite_regles_chargement(self, regle=None):
        """declenche les regles de chargement pour les traitements sans entree"""
        #        if self.debug:
        #        print('moteur: regles de chargement pour un traitement sans entree', self.regles[0].mode)
        # if self.regles[0].chargeur:  # tout va bien la premiere regle va faire le job
        #     pass
        # else:
        #     obj = Objet(
        #         "_declencheur",
        #         "_chargement",
        #         format_natif="interne",
        #         conversion="virtuel",
        #     )
        #     self.traite_objet(obj, self.regles[0])
        # #        if self.regles[0].mode == "start": #on prends la main dans le script
        # #            self.regles[0].fonc(self.regles[0], None)
        # #            return
        regles = regle.liste_regles if regle else self.regles
        obj = Objet(
                        "_declencheur",
                        "_init",
                        format_natif="interne",
                        conversion="virtuel",
                    )
        if regles and not regle:
            # print ('traitement regle 0',regles[0])
            self.traite_objet(obj,regles[0]) 
            if self.hasstart:
                return           
        for i in regles:
            if i.mode == "call" and not i.declenchee:
                self.traite_regles_chargement(i)
            # elif i.chargeur:
            #     print(
            #         "--------traite_charge ",
            #         i.declenchee,
            #         i.chargeur,
            #         i.niveau,
            #         i,
            #     )
            # on ne traite pas les regles de chargement si elles sont dans des conditions
            if (
                not i.declenchee
                and i.chargeur
                and (i.niveau == 0 or (i.niveau == 1 and i.nonext))
            ):
                if (
                    i.mode == "start"
                ):  # on prends la main dans le script on est responsable de la suite
                    i.fonc(i, None)
                    break
                else:
                    obj = Objet(
                        "_declencheur",
                        "_chargement",
                        format_natif="interne",
                        conversion="virtuel",
                    )
                    # i.mode_chargeur = True
                    # print("mode chargeur", i)
                    self.traite_objet(obj, i)
                    # i.mode_chargeur = False

    def traite_objet(self, obj, regle, parent=None):
        """traitement basique toutes les regles sont testees"""
        last = None
        while regle:
            last = regle
            # if (
            #     obj.virtuel and regle.declenchee
            # ):  # un virtuel ne declenche une regle q une fois
            #     regle = regle.branchements.brch["ok"]
            #     continue
            regle.declenchee = True
            try:
                if regle.selstd is None or regle.selstd(obj):
                    #                    print ('moteur:select', regle.numero, obj.ident, regle.fonc)
                    if regle.copy:
                        #                        print ('moteur: copie', regle.numero, regle.branchements.brch["copy"],
                        #                               regle.branchements.brch["fail"])
                        self.traite_objet(
                            obj.dupplique(), regle.branchements.brch["copy"]
                        )
                        # on envoie une copie dans le circuit qui ne passe pas la regle
                        if not obj.virtuel:
                            self.dupcnt += 1
                        # print "apres copie ", obj.schema
                    #                print("traitement regle",regle)
                    resultat = regle.fonc(regle, obj) if regle.fonc else True
                    #                print ('params:action schema',regle.params.att_sortie.liste,
                    #                           resultat,obj.schema,regle.action_schema)
                    if resultat:
                        if obj.schema is not None:
                            # if regle.action_schema:
                            # print("action schema", regle, regle.action_schema)
                            #     # print("schema avant", obj.schema)
                            #     regle.action_schema(regle, obj)
                            if regle.action_schema:
                                # print("action schema", regle, regle.action_schema)
                                # print("schema avant", obj.schema)
                                regle.action_schema(regle, obj)
                            if regle.changeclasse:
                                regle.changeclasse(regle, obj)
                        if regle.changeschema:
                            regle.changeschema(regle, obj)
                    if regle.debugvalid:
                        obj.debug("apres", attlist=regle.champsdebug)
                        regle.stock_param.gestion_log.stopdebug()
                    obj.is_ok = resultat

                    if regle.mode_chargeur:  # la on fait de executtion unique
                        # print("==============mode chargeur", regle)
                        regle = None
                    else:
                        if obj.redirect and obj.redirect in regle.branchements.brch:
                            regle = regle.branchements.brch[obj.redirect]
                            if regle:
                                obj.redirect = None
                        else:
                            regle = (
                                regle.branchements.brch["ok"]
                                if resultat
                                else regle.branchements.brch["fail"]
                            )
                            if not regle and obj.virtuel:
                                # print(" ============traitement sortie virtuel", regle)
                                regle = last.branchements.brch["next"]

                else:
                    if regle.debug and "+" in regle.v_nommees["debug"]:
                        regle.affiche_debug("--non executee--->")
                        print("suite", regle.branchements.liens_num()["sinon"])
                    regle = regle.branchements.brch["sinon"]

                # if obj.virtuel:
                #     print("=========virtuel", last, "\n====>", regle)
                # if regle and regle.valide=="done":
                #     regle = regle.branchements.brch["ok"]
            except StopIteration as abort:
                #                print ('stopiteration', ab.args)

                if abort.args and abort.args[0] == 1:  # arret de traitement de l'objet
                    return
                raise  # on la passe au niveau au dessus
            except NotADirectoryError as exc:
                print("==========erreur de traitement repertoire inconnu", exc)
                print("====regle courante:", regle)
                if regle.stock_param.worker:
                    print("====mode parallele: process :", regle.getvar("_wid"))
                printexception()
                raise StopIteration(3)

            except NotImplementedError as exc:
                print("==========erreur de traitement fonction inexistante", exc)
                print("====regle courante:", regle)
                if regle.stock_param.worker:
                    print("====mode parallele: process :", regle.getvar("_wid"))
                printexception()
                raise StopIteration(3)

            except Exception as exc:
                print("==========erreur de traitement non gérée")
                print("====regle courante:", regle)
                if regle:
                    if regle.stock_param.worker:
                        print("====mode parallele: process :", regle.getvar("_wid"))
                    printexception()
                    if regle.getvar("debuglevel", "0") != "0":
                        print("==========environnement d'execution")
                        print(
                            "====pyetl :",
                            regle.stock_param.nompyetl,
                            regle.stock_param.idpyetl,
                        )
                        print("====objet courant :", obj)
                        print("====parametres\n", regle.params)
                        print(regle.context)
                        if regle.getvar("debuglevel", "0") > "1":
                            print(
                                "========================= variables globales==========",
                                regle.stock_param.context,
                            )
                        print("========== fin erreur de traitement")
                else:
                    printexception()
                raise StopIteration(3)

        if obj.redirect == "end":
            # il est deja mort
            return
        if last and not last.store:
            if last.filter or last.supobj:
                self.suppcnt += 1

            if obj.schema and not obj.virtuel:
                # c est un objet qui a ete jete par une regle filtrante
                obj.schema.objcnt -= 1
        obj.redirect = "end"
        # print("fin de l objet", obj.ido)

    def vide_stock(self):
        """vidange des tuyeaux"""
        stock = True
        while stock:
            stock = False
            for regle in self.regles:
                if regle.store and regle.nbstock:
                    # print("--------menage_final ", regle, regle.nbstock)
                    stock = True
                    regle.traite_stock(regle)


class Macro(object):
    """structure de gestion des macros"""

    def __init__(self, nom, file="", vpos=None):
        self.nom = nom
        self.apis = dict()
        self.retour = "text"
        self.file = file
        self.commandes_macro = dict()
        self.lignes=[]
        self.help = ""
        self.help_detaillee = []
        self.parametres_pos = dict()
        self.vars_utilisees = dict()
        self.vpos = []
        self.vdef = dict()
        self.e_s = dict()
        self.no_in = True
        if vpos is not None:
            self.vpos = [i.split("=")[0].strip() for i in vpos if i and i != "\n"]
            for i in vpos:
                if "=" in i:
                    nom, defaut = i.split("=", 1)
                    self.vdef[nom.strip()] = defaut
                else:
                    self.vdef[i] = ""
                self.parametres_pos[i] = i

    def add_command(self, ligne, numero):
        """ajoute une commande a la liste"""
        self.lignes.append(ligne)
        try:
            if ligne.startswith("!#help") or ligne.startswith("!#aide"):
                self.help = ligne.split(";")[1]
                return
            if ligne.startswith("!#description"):
                self.help_detaillee.append(ligne.split(";")[1])
                return
            if ligne.startswith("!#parametres"):
                nomp, defp = ligne.split(";")[1:3]
                self.parametres_pos[nomp] = defp
                return
            if ligne.startswith("!#e_s"):
                nomp, defp = ligne.split(";")[1:3]
                self.e_s[nomp] = defp
                return
            if ligne.startswith("!#variables"):
                nomv, defv = ligne.split(";")[1:3]
                self.vars_utilisees[nomv] = defv
                return
            if ligne.startswith("!#api"):
                apidef = ligne.split(";")
                apiname = apidef[1] if len(apidef)>1 else self.nom[1:]
                retour = apidef[2] if len(apidef)>2 else "text"
                template = apidef[3] if (len(apidef)>3 and apidef[3]!="no_in") else ""
                no_in = "1" if "no_in" in ligne else "0"
                auxv=apidef[-1] if '=' in apidef[-1] else ""
                aux=dict()
                if auxv:
                    vars=auxv.split(',')
                    aux={i.split("=") for i in vars}
                self.apis[apiname] = (self.nom, retour, template, no_in, aux)
                return
            if ligne.startswith("!"):  # commentaire on jette
                return
        except (ValueError, IndexError):
            print("ligne mal formee", ligne)
        self.commandes_macro[numero] = ligne

    def close(self):
        """ajoute une commande pass au cas ou la macro finit par un niveau"""
        pass
        # maxnum = max(self.commandes_macro.keys())
        # last = self.commandes_macro[maxnum]
        # # if last.startswith("|") or last.startswith("+"):
        # #     self.commandes_macro[maxnum + 1] = ";;;;;;;pass;;"
        # self.commandes_macro[maxnum + 1] = ";;;;;;;return;;"
        # self.commandes_macro[maxnum + 2] = ";;;;;;;pass;;"

    def bind(self, liste, context):
        """mappe les variables locales et retourne un environnement"""
        # print("bind", liste)
        macroenv = context.getmacroenv(self.nom)
        for i in self.vpos:  # on initialise le contexte local
            macroenv.setlocal(
                i, self.vdef[i] if self.vdef.get(i) else context.getvar(i)
            )
        # print("macro bind", self.nom, self.vpos, macroenv, macroenv.vlocales, liste)
        if not liste:
            args = context.getvar("_args")
            # permet d affecter les variables positinelles a partir d un texte avec ,
            if args:
                liste = args.split(",")
        context.affecte(liste, context=macroenv, vpos=self.vpos)
        # print("variables locales", macroenv.vlocales)
        return macroenv

    def get_commands(self, add_return=False):
        """recupere les commandes de la macro"""
        cmds = [(i, self.commandes_macro[i]) for i in sorted(self.commandes_macro)]
        if add_return:
            maxnum = max(self.commandes_macro.keys())
            cmds.append((maxnum + 1, ";;;;;;;return;;"))
        return cmds

    def get_lignes(self):
        return self.lignes

    def __repr__(self):
        """affichage lisible de la macro"""
        header = "&&#def;" + self.nom + ";" + ";".join(self.vpos) + "\n"
        return " ".join(
            [header]
            + [self.help]
            + self.help_detaillee
            + [self.commandes_macro[i] for i in sorted(self.commandes_macro)]
        )


class MacroStore(object):
    """conteneur de traitement des macros"""

    def __init__(self, parent=None):
        self.macros = dict() if parent is None else dict(parent.macros)

    def regmacro(self, nom, file="", liste_commandes=None, vpos=None):
        """enregistrement d'une macro"""
        nouvelle = Macro(nom, file=file, vpos=vpos)
        if liste_commandes is not None:
            nouvelle.commandes_macro = liste_commandes
        # if vpos is not None:
        #     nouvelle.vpos = vpos
        # print ('enrregistrement macro',nom, vpos, nouvelle.vpos)
        self.macros[nom] = nouvelle
        return nouvelle

    def stocke_macro(self, description, origine):
        """stocke une description de macro"""
        macro = None
        for num, conf in description:
            # if not conf or conf.startswith("!"):
            #     continue
            if conf.endswith("\n"):
                conf = conf[:-1].strip()
            if conf.startswith("&&#define"):
                if macro:
                    macro.close()
                liste = [i for i in conf.split(";")]
                nom = liste[1]
                vpos = [i for i in liste[2:] if i]
                macro = self.regmacro(nom, file=origine, vpos=vpos)
            elif conf.startswith("&&#include;"):
                if macro:
                    macro.close()
                configfile = conf.split(";")[1]
                if os.path.isfile(configfile):
                    description2 = enumerate(open(configfile, "r").readlines())
                    self.stocke_macro(description2, configfile)
            elif macro:
                macro.add_command(conf, num)
        macro.close()

    def getmacro(self, nom):
        return self.macros.get(nom)

    def getmacros(self):
        return self.macros.items()

    def rename(self, nom, nom2):
        macro = self.getmacro(nom)
        if macro:
            self.macros[nom2] = macro
            del self.macros[nom]

    def getmacrolist(self):
        return self.macros.keys()


class Context(object):
    """contexte de stockage des variables"""

    PARAM_EXP = re.compile(r"%((\*?)#?[a-zA-Z0-9_]+(?:#[a-zA-Z0-9_]+)?)%")
    PARAM_BIND = re.compile(r"^%(\*#?[a-zA-Z0-9_]+(?:#[a-zA-Z0-9_]+)?)%$")
    SPLITTER_PV = re.compile(r"(?<!\\);")  # reconnait les ; non précédes d'un \
    SPLITTER_V = re.compile(r"(?<!\\),")  # reconnait les , non précédes d'un \
    SPLITTER_B = re.compile(r"(?<!\\)\|")  # reconnait les | non précédes d'un \
    SPLITTER_2P = re.compile(r"(?<!\\):")  # reconnait les : non précédes d'un \
    SPLITTERS={';':SPLITTER_PV,'v':SPLITTER_V,'|':SPLITTER_B,':':SPLITTER_2P, }

    def __init__(self, parent=None, ident="", type_c="C", root=False):
        self.nom = type_c + ident
        self.ident = self.nom
        self.type_c = type_c
        self.vlocales = dict()
        self.binding = dict()
        self.search = [self.vlocales]
        self.parent = parent
        self.ref = None
        self.root = self
        self.niveau = 0
        # gestion des hierarchies
        self.setparent(parent)
        if root:
            self.root = self
            self.ref = None
        # print('creation contexte', self, self.nom)

    def __repr__(self):
        return self.ident + ("(" + self.ref.nom + ")" if self.ref else "")

    def parse_sep(self, texte, sep):
        """decoupe une chaine en respectant les guillemets"""
        if sep in self.SPLITTERS and not '"' in texte:
            return self.SPLITTERS[sep].split(texte)
        liste=[""]
        sc=sep
        escape=False
        for v in texte:
            if v=='\\':
                escape=True
                continue
            if escape:
                escape=False
                if v==sep or v=='\\' or v=='"':
                    liste[-1]+=v
                else:
                    liste[-1]+='\\'+v
                continue
            if v=='"':
                sc=sep if sc is None else None
            if v==sc:
                liste.append("")
            else:
                liste[-1]+=v
        return liste


    def setenv(self, env):
        "ajoute les variables d environnement au contexte courant"
        self.search.append(env)

    def setref(self, context):
        """modifie l'enchainement des contextes"""
        self.ref = context

    def setparent(self, parent, ref=True):
        """modifie l'enchainement des contextes"""
        self.parent = parent
        if parent is not None:
            self.ident = parent.ident + "<-" + self.nom
            self.search.extend(parent.search)
            self.root = self.parent.root
            self.ref = parent if (ref or not parent.ref) else parent.ref

    def getmacroenv(self, ident=""):
        """fournit un contexte ephemere lie au contexte de reference"""
        return Context(parent=self, ident=ident, type_c="M")

    def getblocenvenv(self, ident=""):
        """fournit un contexte ephemere lie au contexte de reference"""
        return Context(parent=self, ident=ident, type_c="B")

    def setbinding(self, nom, binding):
        """gere les retours de parametres"""
        self.binding[nom] = binding

    def getcontext(self, ident="", liste=None, ref=False, type_c="C"):
        """fournit un nouveau contexte de reference empilé"""
        context = Context(parent=self, ident=ident, type_c=type_c)
        if ref:
            context.ref = self.ref if self.ref else self
        if liste:
            self.affecte(liste, context=context)
        return context

    def getvar_b(self, nom, defaut):
        for ctx in self.search:
            if nom in ctx:
                return ctx[nom]
        return defaut

    def getvar(self, nom, defaut=""):
        """fournit la valeur d'un parametre selon des contextes standardises"""
        #        if nom == 'nbaffich':
        #            print ('chemin de recherche ',self.search)

        return self.getvar_b(nom, defaut)
        ret = self.getvar_b(nom, defaut)

        print(
            "retour getvar",
            (
                ret
                if not isinstance(ret, (list, tuple))
                else ",".join([str(i) for i in ret])
            ),
        )
        return (
            ret
            if not isinstance(ret, (list, tuple))
            else ",".join([str(i) for i in ret])
        )

    def istrue(self, nom, defaut=False):
        """retourne vrai si la valeur de la variable est un booleen"""
        val = self.getvar_b(nom, None)
        if val is None:
            return defaut
        if isinstance(val, str):
            if not val:
                return defaut
            if val.lower() in ("0", "f", "false", "non", "faux"):
                return False
            return True
        else:
            return bool(val)

    def isfalse(self, nom):
        return not self.istrue(nom)

    def resolve(self, element: str) -> T.Tuple[str, str]:
        """effectue le remplacement de variables"""
        element = element.strip()  # on debarasse les blancs parasites

        if self.PARAM_BIND.match(element):
            return self.getvar(element[2:-1]), element[2:-1]
        while self.PARAM_EXP.search(element):
            for i, j in self.PARAM_EXP.findall(element):
                cible = "%" + j + i + "%"
                # print(
                #     "recup getvar", self, element, cible, i, "->", self.getvar(i)
                # ), element.replace(cible, str(self.getvar(i)))
                element = element.replace(cible, str(self.getvar(i)))

        if element.startswith("#env:") and element.split(":")[1]:
            # on affecte une variable d'environnement
            element = self.env.get(element.split(":")[1], "")
        elif element.startswith("#eval:") and element.split(":")[1]:
            if "__" in element:
                raise SyntaxError("fonction non autorisee " + element)
            element = eval(element.split(":")[1], {})
        # print('resolve ', element)
        # element = self.getfirst(element)
        element = element.strip()  # on enleve les blancs parasites
        if element.startswith("'") and element.endswith("'"):
            element = element[1:-1]
        # if element.startswith(r"\ "):  # mais on garde les blancs voulus
        #     element = element[1:]
        # if element.endswith(" \\"):  # mais on garde les blancs voulus
        #     element = element[:-1]
        return element, ""

    def getfirst(self, element):
        """retourne le premier non vide d'une liste d'elements"""
        liste = self.SPLITTER_B.split(element)
        for valeur in liste:
            if valeur:
                if valeur.startswith("#env:") and valeur.split(":")[1]:
                    # on affecte une variable d'environnement
                    valeur = self.env.get(valeur.split(":")[1], "")
                elif valeur.startswith("#eval:") and valeur.split(":")[1]:
                    if "__" in valeur:
                        raise SyntaxError("fonction non autorisee " + valeur)
                    valeur = eval(valeur.split(":")[1], {})
                if valeur:
                    return valeur
        return element

    def traite_egalite(self, element):
        """gere une affectation par egal"""
        defnom, defval = element.split("=", 1)
        nom, _ = self.resolve(defnom)
        local = not nom.startswith("*")
        val, binding = self.resolve(defval)
        # print("traite_egalite", defnom, nom, "=", defval, val)
        return nom, val, binding, local

    # TODO a revoir la gestion des hstore dans les variables positionelles
    def traite_hstore(self, element, context):
        """mappe un hstore sur l'environnement"""
        val, binding = self.resolve(element[1:])  # c'est un eclatement de hstore
        liste = [i.strip().strip('"').replace('"=>"', "=") for i in val.split('","')]
        self.affecte(liste, context=context)

    def affecte(self, liste, context=None, vpos=[], dloc=None):
        """gestion directe d'une affectation"""
        local = True
        # print("affecte_contexte", liste)
        for num, element in enumerate(liste):
            if element.startswith("'") and element.endswith("'"):
                val = element[1:-1]
                binding = ""
                nom = vpos[num] if num < len(vpos) else "v_" + str(num)
            elif "=" in element:  # c'est une affectation
                nom, val, binding, local = self.traite_egalite(element)
            elif element.startswith("*%"):
                self.traite_hstore(element, context)
                continue
            else:
                val, binding = self.resolve(element)
                nom = vpos[num] if num < len(vpos) else "v_" + str(num)
                if nom.startswith("*"):
                    local = False
                    nom = nom[1:]

            if nom:
                nom = nom.strip()
                if isinstance(dloc, dict):
                    dloc[nom] = val
                else:
                    if local:
                        # print("setlocal", nom, val)
                        context.setlocal(nom, val) if context else self.setlocal(
                            nom, val
                        )
                    else:
                        context.setroot(nom, val)
                    if binding:
                        context.setbinding(nom, binding)

    def getchain(self, noms, defaut=""):
        """fournit un parametre a partir d'une chaine de fallbacks"""
        for nom in noms:
            res = self.getvar(nom, None)
            if res is not None:
                return res
        return defaut

    def getlocal(self, nom, defaut=""):
        """fournit la valeur d'un parametre selon des contextes standardises"""
        return self.vlocales.get(nom, defaut)

    def getgroup(self, prefix):
        """fournit une liste de variables respectant un prefixe"""

        retour = self.parent.getgroup(prefix) if self.parent else dict()
        # print ('getgroup',self, retour)
        retour.update(
            ((i, j) for i, j in self.vlocales.items() if i.startswith(prefix))
        )
        return retour

    def setvar(self, nom, valeur):
        """positionne une variable du contexte de reference"""
        # print("contexte setvar", self, nom, valeur)
        local = False
        if nom.startswith("."):
            local = True
            nom = nom[1:]
        if nom in self.vlocales or local or self.root == self:
            self.vlocales[nom] = valeur
            if nom in self.binding and self.ref:
                self.ref.setvar(self.binding[nom], valeur)
                # print ("binding",nom,"->",self.binding[nom],':',valeur, self.parent)
        else:
            self.ref.setvar(nom, valeur) if self.ref else self.setlocal(nom, valeur)
        # print("--- verif", print("contexte setvar", self, nom, self.getvar(nom)))

    def setlocal(self, nom, valeur):
        """positionne une variable locale du contexte"""
        # print("----contexte setlocal", self, nom, "->", valeur)
        # if nom == "nom" and not valeur:
        #     raise

        self.vlocales[nom] = valeur

    def setroot(self, nom, valeur):
        """positionne une variable du contexte racine"""
        #        print ('contexte setvar', nom, valeur)
        self.root.vlocales[nom] = valeur

    def setretour(self, nom, valeur):
        """positionne une variable et la mappe sur le contexte parent"""
        self.vlocales[nom] = valeur
        if nom in self.binding and self.ref:
            self.ref.setlocal(self.binding[nom], valeur)

    def setretour_env(self, nom, valeur):
        """positionne une variable et la mappe sur le contexte parent"""
        self.vlocales[nom] = valeur
        if nom in self.binding and self.root.parent:
            self.root.parent.setvar(self.binding[nom], valeur)

    def exists(self, nom):
        """la variable existe"""
        return nom in self.ref.vlocales

    def update(self, valeurs):
        """affectation en masse"""
        self.vlocales.update(valeurs)

    def getvars(self):
        """recupere toutes les variables d'un contexte"""
        vlist = set()
        for ctx in self.search:
            vlist = vlist | ctx.keys()
        return {i: self.getvar(i) for i in vlist}

    #                print ('contexte getvar', nom, c[nom])


##        return self.ref.vlocales.__repr__(), self.search.__repr__()
#        return self.search.__repr__()
#        return '==============================variables locales========\n' +\
#                 '\n\t'+'\n\t'.join([i+':'+str(j) for i, j in sorted(self.vlocales.items())])+\
#                 '========================= variables globales==========\n'+\
#                 '\n\t'+'\n\t'.join([i+':'+str(j) for i, j in sorted(self.ref.vlocales.items())])
def list_input(mapper, liste, reader):
    """gere les listes d entree avec acces seie ou parallele"""
    for element in liste:
        reader(mapper, element)
