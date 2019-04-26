# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 09:28:45 2014

@author: 89965
"""
# import copy
# import re
import difflib


class MatchClasses(object):
    """ objet de conversion permettant de passer d'une description a l'autre """

    def __init__(self, source, destination, att_source, att_dest):
        self.classe_source = source
        self.classe_destination = destination
        self.att_source = att_source if att_source else dict()
        self.att_dest = att_dest if att_dest else dict()

    def _match_direct(self):
        """egalite"""

        # match direct
        a_traiter = [i for i in self.att_source if self.att_source[i] is None]
        nb_a_traiter = len(a_traiter)
        for i in a_traiter:
            if i in self.att_dest:
                self.att_dest[i] = i
                self.att_source[i] = i
        reste = len([i for i in self.att_source if self.att_source[i] is None])
        return nb_a_traiter - reste, reste

    def _match_upper(self):
        """ match majuscule sans tenir compte de la casse"""

        upperdest = {i.upper(): i for i in self.att_dest if self.att_dest[i] is None}
        a_traiter = [i for i in self.att_source if self.att_source[i] is None]
        nb_a_traiter = len(a_traiter)
        for i in a_traiter:
            if i.upper() in upperdest:
                self.att_source[i] = upperdest[i.upper()]
                self.att_dest[upperdest[i.upper()]] = i
        reste = len([i for i in self.att_source if self.att_source[i] is None])
        return nb_a_traiter - reste, reste

    def _match_fuzzy(self, qual=0.5):
        """mode rantanplan par defaut on limite les initiatives en gardant qual a 0.5"""
        upperdest = {i.upper(): i for i in self.att_dest if self.att_dest[i] is None}
        a_traiter = {i.upper(): i for i in self.att_source if self.att_source[i] is None}
        nb_a_traiter = len(a_traiter)
        matcher = difflib.SequenceMatcher(None)
        while a_traiter and upperdest:
            valmatch = dict()
            score = dict()
            for i in a_traiter:
                matcher.set_seq2(i)
                vmax = 0
                bestmatch = None
                for j in upperdest:
                    matcher.set_seq1(j)
                    vmatch = matcher.ratio()
                    if vmatch > qual and vmatch > vmax:  # on a trouve mieux
                        vmax = vmatch
                        bestmatch = j
                valmatch[i] = bestmatch
                score[i] = vmax
            vmax = 0
            for i in a_traiter:
                if score[i] > vmax:
                    vmax = score[i]
                    valeur = i
                    bestmatch = valmatch[i]
            if vmax == 0:
                print("impossible de matcher le reste", a_traiter.values(), upperdest.values())
                break
            self.att_source[a_traiter[valeur]] = upperdest[bestmatch]
            print("match", a_traiter[valeur], upperdest[bestmatch], vmax)
            self.att_dest[upperdest[bestmatch]] = self.att_source[a_traiter[valeur]]
            upperdest = {i.upper(): i for i in self.att_dest if self.att_dest[i] is None}
            a_traiter = {i.upper(): i for i in self.att_source if self.att_source[i] is None}
        if upperdest:
            print("attributs destination non mappes ", upperdest.values())
        if a_traiter:
            print("attributs source non mappes ", a_traiter.values())
        reste = len(a_traiter)
        return nb_a_traiter - reste, reste

    def automatch(self, source=None, dest=None, qual=0.5):
        """genere une correspodnace automatique """
        if source:
            self.att_source = source
        if dest:
            self.att_dest = dest
        self.set_map(None, auto=3, qual=qual)

        for i in self.att_source:
            print(i, "--->", self.att_source[i])

        # match comme on peut

    def set_map(self, correspondance, auto=2, qual=0.5):
        """ on fournit une liste de correspondance
        si auto est vrai les match exact sont ajoutes apres la correspondance """
        directmatch, casematch, fuzzymatch = 0, 0, 0

        for i in correspondance:
            self.att_source[i] = correspondance[i]
            self.att_dest[correspondance[i]] = i
        reste = len([i for i in self.att_source if self.att_source[i] is None])
        if auto > 0 and reste:  # match direct
            directmatch, reste = self._match_direct()
        if auto > 1 and reste:  # match sans tenir compte de la casse
            casematch, reste = self._match_upper()
        if auto > 2 and reste:  # match au mieux
            fuzzymatch, reste = self._match_fuzzy(qual)
        print("generation de correspondance ", directmatch, casematch, fuzzymatch, reste)

    def map_attributs(self, obj):
        """ remappe les attributs d'un objet"""
        obj.attributs = {
            self.att_source.get(nom, nom): valeur for nom, valeur in obj.attributs.items()
        }
        obj.attributs["#classe"] = self.classe_destination.nom
        obj.setschema(self.classe_destination.schema)


def match_classe(classe, schema_sortie, qual):
    """ cree le tableau de correspondance pour une classe """
    classe_sortie = schema_sortie.guess_classe(classe.nom)
    if classe_sortie:
        attmap = MatchClasses(
            classe,
            classe_sortie,
            {i: None for i in classe.attributs},
            {i: None for i in classe_sortie.attributs},
        )
        attmap.automatch(qual=qual if qual else 0.5)
        classe.attmap = attmap


def match_schema(entree, sortie, qual):
    """ mets en correspondance 2 schemas  """
    for classe in entree:
        match_classe(entree[classe], sortie, qual)


class Mapping(object):
    """ gestion des mappings permet de conserver le lien entre les classes
    d'entree et les classes de sortie"""

    def __init__(self):
        self.liste_mapping = []
        self.mapping_classe_schema = dict()  # donne le lien classe -> schema
        self.mappings_ambigus = dict()  # liste des problemes potentiels
        self.mapping_destination = dict()  # liens id_orig -> id_dest
        self.mapping_origine = dict()  # lien
        self.mapping_class_destination = dict()
        self.mapping_class_origine = dict()
        self.mode_fusion = False
        self.existe = False
        self.multiple = True
        self.debug = 0

    @property
    def __dic_if__(self):
        """interface de traansfert"""
        return self.liste_mapping

    def from_dic_if(self, dic_if):
        """interface de traansfert"""
        self.init_mapping(None, dic_if)

    def mapping_schema(self, classes, fusion):
        """ sort la table de correspondance entre schemas"""
        def_mapping = ["!schema;classe;schema_orig;classe_orig;nombre"]
        if self.mode_fusion:
            fusion = True
        if fusion:
            #            print('sc interne: fusion', len(classes))
            def_mapping.extend(
                [
                    ";".join(i + classes[i].ident_origine + (str(classes[i].poids),))
                    for i in sorted(classes)
                ]
            )
        else:
            def_mapping.extend(
                [
                    ";".join(
                        i
                        + classes[i].ident_origine
                        + (
                            str(
                                classes[i].objcnt
                                if classes[i].objcnt
                                else classes[i].getinfo("objcnt_init")
                            ),
                        )
                    )
                    for i in sorted(classes)
                    if classes[i].a_sortir
                ]
            )
        # print ('schema:mapping ',mapping)

        return def_mapping

    def _valide_mapping(self, entree, mapping, ref, message):
        """identifie les ambiguites de mapping"""
        if entree in mapping and mapping[entree] != ref:
            self.mappings_ambigus[entree] = 1
            if self.debug:
                print("mapping ambigu " + message, entree, ref, mapping[entree])
        else:
            mapping[entree] = ref

    def init_mapping(self, classes, liste_mapping):
        """traitement des mappings initialisation des structures"""
        self.liste_mapping = liste_mapping
        for i in liste_mapping:
            # traitement des mappings : permet de definir des actions en
            # denominations elyx ou sans preciser les schemas
            # print("valeur de i ", i)
            try:
                s_fin, c_fin, s_orig, c_orig = i.split(";")[:4]
            except ValueError:
                print("ligne incomplete", i)
                continue
            self.existe = True
            if '*' in s_orig or '*' in c_orig:
                self.multiple = True
            orig = (s_orig, c_orig)
            fin = (s_fin, c_fin)
            self.mapping_destination[orig] = fin
            self.mapping_origine[fin] = orig
            if classes and fin in classes:
                classes[fin].origine = orig
            self._valide_mapping(c_orig, self.mapping_class_destination, fin, "orig 1")
            self._valide_mapping(c_fin, self.mapping_class_origine, orig, "fin 1")
            self._valide_mapping(c_orig, self.mapping_classe_schema, s_orig, "orig 2")
            self._valide_mapping(c_fin, self.mapping_classe_schema, s_fin, "fin 2")


    def map_classes(self, classes):
        """ force les origines des classes"""
        if self.existe:
            for i in classes:
                groupe, nom = i
                if i in self.mapping_origine:
                    classes[i].origine = self.mapping_origine[i]
                else:
                    if nom in self.mapping_classe_schema and not nom in self.mappings_ambigus:
                        groupe = self.mapping_classe_schema[nom]
                        if (groupe, nom) in self.mapping_origine:
                            classes[i].origine = self.mapping_origine[(groupe, nom)]
        else:
            for i in classes:
                classes[i].setorig(i)

    def map_dest(self, id_orig):
        """retourne la destination du mapping"""
        # print ('map _orig', self.mapping_origine)
        if self.existe:
            id_dest = None
            if self.multiple:
                g_orig, c_orig = id_orig
                for gref,cref in self.mapping_destination:
                    # print ('test' , gref,cref, g_orig,c_orig)
                    if gref.replace('*','') in g_orig and cref.replace('*','') in c_orig:
                        id_dest = self.mapping_destination.get((gref, cref))
                        break
            else:
                id_dest = self.mapping_destination.get(id_orig)
            # print ('--------------------------mapping',id_orig,'->',id_dest,self.mapping_destination )

            if id_dest:
                return id_dest
            if id_orig in self.mapping_origine:
                return id_orig
            #        print ('mapping non trouve',id_orig,self.mapping_destination)
            #        raise
            if id_orig[1] in self.mappings_ambigus:
                print(" mapping ambigu ", id_orig[1])
                raise KeyError("mapping destination ambigu " + id_orig[1])
            #                return None
            id_dest = self.mapping_class_destination.get(id_orig[1])
            if not id_dest:
                id_dest = self.mapping_class_destination.get(id_orig[1].lower())
            if not id_dest:
                id_dest = self.mapping_class_destination.get(id_orig[1].upper())
            return id_dest if id_dest else id_orig
        return id_orig

    def map_orig(self, id_dest):
        """retourne l origine du mapping"""
        #        print ('mapping',id_orig,'->',self.mapping_destination.get(id_orig))
        if self.existe:
            id_orig = self.mapping_origine.get(id_dest)

            if id_orig:
                return id_orig
            #        print ('mapping non trouve',id_orig,self.mapping_destination)
            #        raise
            if id_dest in self.mapping_destination:
                return id_dest

            if id_dest[1] in self.mappings_ambigus:
                print(" mapping ambigu ", id_dest[1])
                raise KeyError("mapping origine ambigu " + id_dest[1])
            #                return None
            id_orig = self.mapping_class_origine.get(id_dest[1])
            if not id_orig:
                id_orig = self.mapping_class_origine.get(id_dest[1].lower())
            if not id_orig:
                id_orig = self.mapping_class_origine.get(id_dest[1].upper())
            return id_orig if id_orig else id_dest
        return id_dest

    def mapping(self, classes, id_cl):
        """#retourne un identifiant complet et une origine complete"""
        # ci=cl
        if self.existe:
            if not id_cl[0]:
                # print ('recherche ',cl[0],cl[1])
                if id_cl[1] in self.mappings_ambigus:
                    print(" mapping ambigu ", id_cl[1])
                    return ""
                else:
                    id_cl = self.mapping_classe_schema.get(id_cl[1], ("non trouve", id_cl[1]))
                    # print ('recuperation',ci,cl[1])
            if id_cl in self.mapping_origine:
                origine = self.mapping_origine[id_cl]
                destination = id_cl
            elif id_cl in self.mapping_destination:
                origine = id_cl
                destination = self.mapping_destination[id_cl]
            elif id_cl in classes:
                origine = ""
                destination = id_cl
            else:
                # print (' schema: mapping : classe inconnue ',cl)
                return ""
            return origine, destination
        else:
            return ""
