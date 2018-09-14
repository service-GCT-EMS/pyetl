# -*- coding: cp1252 -*-
"""
Created on Wed Dec 10 09:28:45 2014

@author: 89965
"""
import copy
#import re
from .elements import attribut as A
from .elements import schemaclasse as C
from .elements import mapping as M
# schemas : description de la structure des objets

TYPES_G = C.TYPES_G
CODES_G = C.CODES_G







def get_attribut(nom, vmax):
    ''' recupere une structure d'attribut pour creer des modeles'''
    return A.Attribut(nom, vmax, nom_conformite='')

def init_schema(mapper, nom_schema, origine='G', fich='', defmodeconf=0,
                stable=True, modele=None):
    ''' retourne le schemas qui va bien et les cree si necsssaire '''
    if not nom_schema:
        print('pyetl: schema sans nom')
        raise ValueError
#    print ('creation schema ',nom_schema)
    if nom_schema not in mapper.schemas:
        mapper.schemas[nom_schema] = Schema(nom_schema, origine=origine,
                                            fich=fich, defmodeconf=defmodeconf)
        mapper.schemas[nom_schema].stable = stable
#            self.schemas[nom_schema].modele = modele

        if modele is not None: # on transmet les informations specifiques
            mapper.schemas[nom_schema].elements_specifiques =\
                copy.deepcopy(modele.elements_specifiques)
            mapper.schemas[nom_schema].alias_groupes = dict(modele.alias_groupes)
            mapper.schemas[nom_schema].dbsql = modele.dbsql
#                self.schemas[nom_schema].dic_abrev = modele.dic_abrev
    return mapper.schemas[nom_schema]

class Schema(object):
    ''' definition d'un schema : ensemble de classes et de conformites '''
    #types_G={0:"NOGEOM",1:"POINT",2:"LIGNE",3:"POLYGONE",4:""}
    dic_abrev = {'commune':'com',
                 'date':'dt', 'annee':'an',
                 'code':'cd',
                 'libelle':'lib', 'final':'fin',
                 'niveau':'niv', 'niv':'n',
                 'intervention':'intrv',
                 'batiment':'bat',
                 'circulation':'circ',
                 'correspondance':'corresp', 'corresp':'crsp',
                 'concessionaire':'concess', 'concess':'ccs',
                 'concession':'concess',
                 'dependance':'dep', 'dependances':'dep',
                 'domanialite':'dom',
                 'distance':'dist',
                 'deformation':'def',
                 'emplacement':'emplact', 'emplact':'emp',
                 'emprise':'empr',
                 'fissure':'fis',
                 'gestion':'gest',
                 'numero':'num', 'num':'n',
                 'prestataire':'prest',
                 'proprietaire':'prop', 'propriete':'prop',
                 'remplissage':'remp',
                 'route':'rte',
                 'surface':'surf', 'surf':'s',
                 'taux':'tx',
                 'taux_remplissage':'tr',
                 'toponyme':'tpny',
                 'transversale':'trv',
                 'usage':'usg',
                 'geometrie':'geom', 'geometrique':"geom", "geom":"g",
                 'commentaire':'comment', 'coment':'cmt',
                 'largeur':'larg', 'longueur':'long',
                 "source":"src", "comptage":"compt", "compt":"ctg",
                 "creation":"cre", "date_mise_a_jour":"date_maj",
                 'date_creation':'date_creat',
                 'dernier':'der', "deplacement":"depl",
                 'dossier':'dos', "registre":"reg",
                 'identifiant':'id', 'primaire':"prim",
                 'sous':'ss', 'troncon':'trc',
                 'adresse':'adr',
                 'parcelle':'parc', 'parcellaire':'parc', 'section':'sec',
                 'description':'desc',
                 'exploitant':'exp',
                 'volume':'vol', 'diametre':'d', ' diam':'d',
                 'droit':'d', 'gauche':'g',
                 'gestionnaire':'gest',
                 'nature_materiau':'mat',
                 'fiche_pdf':'pdf',
                 'reparation':'repar', 'chaussee':'ch', 'structure':'str',
                 'pann1':'p1', 'pann2':'p2', 'pann3':'p3',
                 'panneau':'pan', 'panneaux':'pan'
                }
    def __init__(self, nom_schema, fich='', origine='G', defmodeconf=0, alias=''):
        self.classes = dict()
        self.conformites = dict()
        self.defmodeconf = defmodeconf
        self.taux_conformite = 10
        self.direct = dict()
#        self.dic_abrev = dict()
        self.stock_mapping = M.Mapping()
        self.origine = origine  #G: schema genere L: schema lu S: schema de sortie B: schema base
        self.modele = None
        self.nom = nom_schema
        self.fich = fich if fich else self.nom
        self.alias = alias
        self.conf_deja_analyse = False
        self.mode_sortie = None
        self.elements_specifiques = dict()
#        self.dialecte = None # dialecte (sql)
        self.format_sortie = '' # format de sortie
        self.rep_sortie = ''
        self.dbsql = None # generateur sql
        self.alias_groupes = dict()


    def def_classe(self, ident):
        ''' cree un schema pour une nouvelle classe'''
        return self.ajout_classe(C.SchemaClasse(ident, self))

    def ajout_classe(self, sc_classe):
        '''ajoute une classe dans un schema'''
        ident = sc_classe.identclasse
        self.classes[ident] = sc_classe
        self.direct[ident[1]] = ident
        sc_classe.schema = self
        return sc_classe

    def get_classe(self, ident, cree=False, modele=None, filiation=False, guess=False):
        ''' recupere la description d'une classe'''
        schema_classe = self.classes.get(ident)
        if schema_classe:
            return schema_classe
        # on tente une recherche par le nom s il n'y a pas de groupe
        if not ident[0]:
            schema_classe = self.classes.get(self.direct.get(ident[1]))
            if schema_classe:
                return schema_classe
        if guess:
            classe = self.guess_classe(ident[1])
            if classe:
                return classe
        if cree: # on va tenter de creer la classe
            return self._cree_classe(ident, modele, filiation)

    def guess_classe(self, nom):
        ''' essaye de matcher une classe au mieux avec un nom approximatif '''
        ref = nom.lower()
        for i in self.classes:
            if i[1].lower() == ref:
                return self.classes[i]
        for i in self.classes:
            if ref in i[1].lower():
                return self.classes[i]
        for i in self.classes:
            if  i[1].lower() in ref:
                return self.classes[i]
        return None


    def renomme_classe(self, ancien_ident, nouvel_ident, spec=False):
        '''gere un renommage de classe en terant compte des clefs etrangeres'''
#        print ('renommage classe ',self.nom,ancien_nom, nouveau_nom)
        self.classes[nouvel_ident] = self.classes[ancien_ident]
        self.classes[nouvel_ident].setident(nouvel_ident)
        del self.classes[ancien_ident]
        for scl in self.classes.values():
            scl.renomme_cible_classe(ancien_ident, nouvel_ident)

    def supp_classe(self, ident):
        '''supprime une classe du schema'''
        if ident in self.classes and self.classes[ident].objcnt==0:
            del self.classes[ident]





    def _cree_classe(self, ident, modele, filiation=True):
        '''copie du schema d'une classe vers un nouveau schema avec gestion des conformites'''
#        print ('avant copie',modele.type_geom, modele)
        if modele is None: # on cree une classe a partir de 0
            return C.SchemaClasse(ident, self)
#        on recopie le modele
        old_schema = modele.schema # on evite de recopier toute la structure
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
        nouvelle_classe.type_table = 'i'
        modele.schema = old_schema
        modele.fils = old_fils
        modele.regles_modif = old_regles_modif
        if filiation:
            old_fils.append(nouvelle_classe) # gestion des filiations de classes
        #n = 0
        #n2 = 0
        nouvelle_classe.regles_modif = set()
        nouvelle_classe.fils = []
        for i in nouvelle_classe.attributs:
        # il faut verifier les conformites
            conf = nouvelle_classe.attributs[i].conformite
            #print (i,cf.nom if cf else "non reference")
            if conf:
                #n = n+1
                if conf.nom in self.conformites:
                    # elle existe deja on se branche dessus
                    nouvelle_classe.attributs[i].conformite = self.conformites[conf.nom]
                    #n2 += 1
                else:
                    self.conformites[conf.nom] = conf #on la stocke
        self.ajout_classe(nouvelle_classe)
#        print ('copie schema',self.nom, modele.identclasse,modele,
#                nouvelle_classe.identclasse,nouvelle_classe, modele.info['type_geom'],
#                nouvelle_classe.info['type_geom'])

        return nouvelle_classe


    def calcule_cibles(self):
        """determine quelles ont les classes cibles de fk"""
        for i in self.classes:
            for j in self.classes[i].fkey_dep:
                self.classes[j].cibles.add(i)


    def is_cible(self, ident):
        ''' determine si une table est cible de clef etrangere'''
        return self.classes[ident].cibles


    def setdefault_classe(self, ident):
        ''' trouve une classe ou la cree au besoin'''
        classe = self.classes.get(ident)
        return classe if classe else self.def_classe(ident)


    # -------------------gestion interne des mappings ---------------------------#
    def mapping_schema(self, fusion=False):
        '''retourne les origines des classes'''
        return self.stock_mapping.mapping_schema(self.classes, fusion)

    def init_mapping(self, liste_mapping):
        '''traitement des mappings initialisation des structures'''
        return self.stock_mapping.init_mapping(self.classes, liste_mapping)

    def map_classes(self):
        ''' force les origines des classes'''
        return self.stock_mapping.map_classes(self.classes)

    def map_dest(self, id_orig):
        ''' force les origines des classes'''
        return self.stock_mapping.map_dest(id_orig)

    def map_orig(self, id_dest):
        ''' force les origines des classes'''
        return self.stock_mapping.map_orig(id_dest)

    def mapping(self, id_classe):
        '''#retourne un identifiant complet et une origine complete'''
        return self.stock_mapping.mapping(self.classes, id_classe)
    # -------------------------------------------------------------------------#

    def liste_classes(self, groupe):
        ''' retourne la liste des classes d'un groupe'''
        return [i for i in self.classes if i[0] == groupe]

    def liste_groupes(self):
        ''' retourne la liste des groupes d'un schema'''
        groupes = dict()
        for i in self.classes:
            groupes[i[0]] = 1
        return sorted(groupes.keys())


    def stat_schema(self):
        ''' sort les stats standard'''
        groupes = dict()
        for i in self.classes:
            groupes[i[0]] = 1
        print("schema : stat schema", self.nom, len(groupes), len(self.classes),
              len(self.conformites))

    def get_conf(self, nom_conf, type_c='', mode=1):
        ''' retourne une conformite en la creeant si besoin'''
        conf = self.conformites.get(nom_conf)
        if conf:
            return conf
        conf = A.Conformite(nom_conf, type_c, mode)
        self.conformites[nom_conf] = conf
        return conf


    def adapte_attributs(self, fonction):
        '''ajuste les noms dans le schema pour tenir compte des contraintes du sql'''
        for i in self.classes:
            self.classes[i].adapte_attributs(fonction)


    def setbasic(self):
        '''simplifie un schema pour supprimer les enums et les liens / fonctions vues etc...'''
        self.conformites = dict()
        for i in self.classes:
            self.classes[i].setbasic()
        self.elements_specifiques = {}
