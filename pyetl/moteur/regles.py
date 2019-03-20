# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
"""
import re
import os
import logging
from itertools import zip_longest
#from collections import namedtuple
import pyetl.schema.schema_interne as SC
import pyetl.schema.fonctions_schema as FSC
#from pyetl.moteur.selecteurs import Selecteur
#import pyetl.formats.formats as F
#from pyetl.formats.interne.objet import Objet
import pyetl.formats.format_temporaire as T
#import pyetl.formats.mdbaccess as DB
#from pyetl.moteur.fonctions import gestion_schema as GS
LOGGER = logging.getLogger('pyetl')


class Branch(object):
    '''gestion des liens avec possibilite de creer de nouvelles sorties'''
    enchainements = {"", "sinon", "fail", "next"}

    def __init__(self):
        self.brch = {'ok': None, 'sinon': None, 'fail': None, 'next': None, 'gen': None}
        self.suivante = False

    def __repr__(self):
        return self.liens_num().__repr__()

    def setlink(self, lien):
        '''positionne les liens'''
        self.brch.update({i:lien for i in self.brch})

    def setclink(self, lien):
        '''positionne les liens s'ils ne le sont pas'''
        self.brch.update({i:lien for i in self.brch if self.brch[i] is None})

    def addsortie(self, sortie):
        '''positionne iune sortie supplementaire'''
        if sortie not in self.brch:
            self.brch[sortie] = None
            self.enchainements.add(sortie)

    def liens_num(self):
        '''retourne les numeros de regles '''
        liens_num = {i:self.brch[i].numero if self.brch[i] else 99999 for i in self.brch}
        return liens_num

    def liens_pos(self):
        '''retourne les index dans la liste de regles finale avec les inclus'''
        liens_num = {i:self.brch[i].index if self.brch[i] else 99999 for i in self.brch}
        return liens_num

    def changeliens(self, regles):
        '''reassigne les liens en cas de copie d'un ensemble de regles sert pour
        le fonctionnement en mode multiprocessing'''
        liens_pos = self.liens_pos()
        brch2 = {i:regles[j] for i, j in liens_pos.items()}
        self.brch = brch2

    def setsuivante(self, regle):
        '''positionne le lien vers la prochaine regle a executer'''
        if regle:
            self.suivante = regle
        else:
            self.suivante = self.brch['sinon'].suivante if self.brch['sinon'] else None

class Valdef(object):
    '''classe de stockage d'un parametre'''
    def __init__(self, val, num, liste, dyn, definition, origine, texte):
        self.val = val
        self.num = num
        self.liste = liste
        self.dyn = dyn
        self.definition = definition
#        self.besoin = None
        self.origine = origine
        self.texte = texte

    def update(self, obj):
        '''mets a jour les elements a partir de l'objet'''
        self.val = obj.attributs.get(self.origine, '')

    def __repr__(self):
        return self.texte+'->'+str(self.val)



class ParametresFonction(object):
    ''' stockage des parametres standanrds des regles '''
#    st_val = namedtuple("valeur", ("val", "num", "liste", "dyn", 'definition'))

    def __init__(self, valeurs, definition):
        self.valeurs = valeurs
        self.definitions = definition
        self.att_sortie = self._crent("sortie")
        self.def_sortie = None
        self.att_entree = self._crent("entree")
        taille = len(self.att_entree.liste or self.att_sortie.liste)
        self.val_entree = self._crent("defaut", taille=taille)
        self.cmp1 = self._crent("cmp1")
        self.cmp2 = self._crent("cmp2")
        self.specif = dict()
        self.fstore = None
        self.att_ref = self.att_entree if self.att_entree.val else self.att_sortie

    def _crent(self, nom, taille=0):
        '''extrait les infos de l'entite selectionnee'''
#        print("creent",nom,self.valeurs[nom].groups(),self.valeurs[nom].re)
        val = ''
        try:
            val = self.valeurs[nom].group(1)
            if r'\;' in val:
                val = val.replace(r'\;', ';') # permet de specifier un ;
#                val = val.replace(r'\b', 'b')
        except (IndexError, AttributeError, KeyError):
#            print ('creent erreur', self.valeurs)
            val = ""
        try:
            defin = self.valeurs[nom].group(2).split(',')
        except (IndexError, AttributeError, KeyError):
            defin = []
        try:
            num = float(val)
        except ValueError:
            num = None
        liste = val.split(",") if val else []
        if taille > len(liste):
            if liste:
                liste.extend([liste[-1]]*(taille-len(liste)))
            else:
                liste.extend([""]*taille)
#        print (self.definitions)
        try:
            if self.definitions[nom].pattern == '|L':
                liste = val.split("|") if val else []
        except (IndexError, AttributeError, KeyError):
            liste = []
        dyn = "*" in val
        origine = None
        if val.startswith('['):
            dyn = True
            origine = val[1:-1]

#        var = "P:" in val
        texte = self.valeurs[nom].string if nom in self.valeurs else ''

#        return self.st_val(val, num, liste, dyn, defin)
        return Valdef(val, num, liste, dyn, defin, origine, texte)


    def __repr__(self):
        listev = ["sortie:%s"%(str(self.att_sortie)),
                  "entree:%s"%(str(self.att_entree)),
                  "defaut:%s"%(str(self.val_entree)),
                  "cmp1:%s"%(str(self.cmp1)),
                  "cmp2:%s"%(str(self.cmp2))
                 ]
        return '\t'+"\n\t".join(listev)



class ParametresSelecteur(ParametresFonction):
    '''stockage des parametres des selecteurs'''
    def __init__(self, valeurs, definition):
#        print ('creation param selecteur', valeurs, definition)
        self.valeurs = valeurs
        self.definitions = definition
        self.attr = self._crent("attr")
        self.vals = self._crent("vals")
        self.specif = dict()

    def __repr__(self):
        listev = ["attr:%s"%(str(self.attr)),
                  "vals:%s"%(str(self.vals)),
                 ]
        return "\n\t".join(listev)


class RegleTraitement(object): # regle de mapping
    ''' descripteur de traitement unitaire '''
    def __init__(self, ligne, stock_param, fichier, numero, context=None):

        self.ligne = ligne
        self.stock_param = stock_param
        self.branchements = Branch()
        self.params = None
        self.selstd = None
        self.valide = 'inconnu'
        self.enchainement = ''
        self.ebloc = 0
        self.mode = ''
        self.source = fichier
        self.fichier = ""
        self.style = "N"
#        self.traitement_schema = True
        self.niveau = 0
        self.declenchee = False
        self.chargeur = False  # definit si une regle cree des objets
        self.mode_chargeur = False
        self.debug = False # modificateurs de comportement
        self.champsdebug = None
        self.store = False
        self.blocksize = 0
        self.nonext = False
        self.fonc = None
        self.fstore = self.ftrue
        self.shelper = None
        self.fonction_schema = None
        self.numero = numero

        self.context = stock_param.getcontext(context, ident='R'+str(numero))
#        print ('contexte regle',self.ligne, self.context)
        self.val_tri = re.compile('')
        self.index = 0
        self.bloc = 0
        #-----------------flags de comportement-------------------
        self.action_schema = None
        self.final = False
        self.filter = False
        self.copy = False
        self.call = False
        self._return = False
        self.liste_regles = []

        self.nom_fich_schema = ''
#        self.nom_base = 'defaut'
        self.changeclasse = None
        self.changeschema = None
        self.elements = None
        self.f_sortie = None

        self.stockage = dict()
        self.discstore = dict()
        self.tmp_store = list()
        self.compt_stock = 0
        self.dident = ''

        self.schema_courant = None
        self.menage = False

        self.memlimit = self.getvar("memlimit", 0)
        self.erreurs = []
        self.v_nommees = dict()


    def __repr__(self):
        """pour l impression"""
        if self.ligne:
            return str(self.numero)+':'+(self.ligne[:-1]\
                   if self.ligne.endswith('\n') else self.ligne)
        return 'regle vide'


    def setparams(self, valeurs, definition):
        """positionne les parametres """
        self.params = ParametresFonction(valeurs, definition)

    def ftrue(self, *_):
        ''' toujours vrai  pour les expressions sans conditions'''
        return True

    def getregle(self, ligne, fichier, numero):
        '''retourne une regle pour des operations particulieres'''
        return RegleTraitement(ligne, self.stock_param, self.fichier, numero, context=self.context)

    def getvar(self, nom, defaut=''):
        """recupere une variable dans le contexte"""
        return self.context.getvar(nom, defaut)

    def getchain(self, noms, defaut=''):
        """recupere une variable avec une chaine de fallbacks"""
        return self.context.getchain(noms, defaut)

    def setvar(self, nom, valeur):
        """positionne une variable dans le contexte"""
        self.context.setvar(nom, valeur)


# =========================acces standardises aux objets==================
    def getval_entree(self, obj):
        '''acces standadise a la valeur d'entree valeur avec defaut'''
        return obj.attributs.get(self.params.att_entree.val, self.params.val_entree.val)


    def getval_ref(self, obj):
        '''acces standadise a la valeur d'entree valeur avec defaut'''
#        print("recup att_ref ",self.params.att_ref,"valeur",
#              obj.attributs.get(self.params.att_ref.val))
        return obj.attributs.get(self.params.att_ref.val, self.params.val_entree.val)


    def getlist_entree(self, obj):
        '''acces standadise a la liste d'entree valeur avec defaut en liste'''
        return [obj.attributs.get(i, j)
                for i, j in zip_longest(self.params.att_entree.liste,
                                        self.params.val_entree.liste)]

    def getlist_ref(self, obj):
        '''acces standadise a la liste d'entree valeur avec defaut en liste'''
        return [obj.attributs.get(i, j)
                for i, j in zip_longest(self.params.att_ref.liste,
                                        self.params.val_entree.liste)]


    def setval_sortie(self, obj, valeurs):
        '''stockage standardise'''
#        print ("----------stockage ", valeurs, self.params.att_sortie.val, "----",
#               self, self.fstore)
        self.fstore(self.params.att_sortie, obj, valeurs)
#        print ("-----val stockee- ", obj.attributs[self.params.att_sortie.val])


    def process_liste(self, obj, fonction):
        '''applique une fonction a une liste d'attributs et affecte une nouvelle liste'''
        self.fstore(self.params.att_sortie, obj, map(fonction, self.getlist_entree(obj)))


    def process_listeref(self, obj, fonction):
        '''applique une fonction a une liste d'attributs'''
        self.fstore(self.params.att_ref, obj, map(fonction, self.getlist_ref(obj)))


    def process_val(self, obj, fonction):
        '''applique une fonction a un attribut'''
        self.fstore(self.params.att_sortie, obj, fonction(self.getval_entree(obj)))


#    def process_list_inplace(self, obj, fonction):
#        '''applique une fonction a une liste d'attributs'''
##        print ('application fonction',fonction,self.getlist_ref(obj),self.fstore )
#        obj.attributs.update(zip(self.params.att_ref.liste,
#                                 map(fonction, self.getlist_ref(obj))))


    def affiche(self, origine=''):
        '''fonction d'affichage de debug'''
        msg = ' '.join((origine+"regle:----->", str(self.index),
                        "(", str(self.numero), ")", self.ligne[:-1],
                        ("bloc "+str(self.bloc) if self.bloc else ''),
                        ("enchainement:"+ str(self.enchainement) if self.enchainement else ''),
                        " copy " if self.copy else '',
                        " final " if self.final else '',
                        " filter" if self.filter else ''))
        print(msg)
        LOGGER.debug(msg)


    def setstore(self):
        '''definit une regle comme stockante et ajuste les sorties'''
        self.branchements.brch["end"] = self.branchements.brch["ok"]
        self.branchements.brch["ok"] = None


    def endstore(self, nom_base, groupe, obj, final, geomwriter=None, nomgeom=None):
        ''' fonction de stockage avant ecriture finale necessiare si le schema
    doit etre determine a partir des donnees avant de les ecrire sur disque'''
#        print ('regle:dans endstore',self.numero,nom_base,groupe, obj.schema)
#        raise
        classe_ob = obj.ident
        if obj.virtuel:
            return
        if self.f_sortie.calcule_schema:
            if not obj.schema:
                nomschem = nom_base if nom_base else "defaut_auto"
                schem = self.stock_param.schemas.get(nomschem)
                if not schem:
                    schem = SC.Schema(nomschem)
                    self.stock_param.schemas[nomschem] = schem
                if classe_ob not in schem.classes:
                    LOGGER.warning('schema de sortie non trouve '+nomschem+' '+
                                   str(classe_ob)+' -> creation')
#                    print('init schema de sortie ', nomschem, classe_ob)
                FSC.ajuste_schema(schem, obj)
#                print (obj.schema.nom)

            for nom_att in obj.text_graph:
                obj.schema.stocke_attribut(nom_att+"_X", "float", '', 'reel')
                obj.schema.stocke_attribut(nom_att+"_Y", "float", '', 'reel')

        if not final:
            obj = obj.dupplique() # on cree une copie si on veut reutiliser l'objet original
#            print ("endstore:copie de l'objet ",obj.ident,self.stock_param.stream)
        groupe_courant = self.stockage.get(groupe)
#        print ('stockage objet ',obj.ido, obj.copie, obj.ident, obj.schema, freeze)
        if groupe_courant:
            stockage = groupe_courant.get(classe_ob)
            if stockage:
                stockage.append(obj)
            else:
                groupe_courant[classe_ob] = [obj]
        else:
            self.stockage[groupe] = {classe_ob:[obj]}
        self.compt_stock += 1
#        gr = self.stockage.setdefault(groupe, dict())
#        gr.setdefault(classe_ob, []).append(obj)
#        if self.compt_stock%10000 == 0:
#            print ("stok courant", self.compt_stock)
        if self.memlimit and self.compt_stock >= self.memlimit:
            print("stockage disque")
#            raise
            self.tmpwrite(groupe, geomwriter, nomgeom)
        obj.stored = True

    def tmpwrite(self, groupe, geomwriter, nomgeom):
        ''' stockage intermediaire sur disque pour limiter la consommation memoire'''
        tmpfile = os.path.join(self.getvar("tmpdir"),
                               "tmp_"+self.params.cmp1.val+'_'+self.params.cmp2.val+
                               '_'+groupe.replace('/', '_'))
        os.makedirs(self.getvar("tmpdir"), exist_ok=True)
#        if self.stock_param.debug:
#        print("stockage intermediaire ", groupe, self.compt_stock, tmpfile)

        mode = 'w'
        if groupe in self.discstore:
            mode = 'a'
        else:
            self.discstore[groupe] = tmpfile
        T.ecrire_objets(tmpfile, mode, self.stockage[groupe],
                        geomwriter, nomgeom)

        self.stockage[groupe] = dict()
        self.compt_stock = 0



    def recupobjets(self, groupe):
        '''recuperation des objets du stockage intermediaire'''
        nb_recup = 0
        if groupe in self.discstore: # les objets sont sur disque
            if self.stock_param.debug:
                print("regles : recupobjets ouverture", self.discstore[groupe])
            for obj in T.lire_objets(self.discstore[groupe], self.stock_param):
                schem = obj.attributs.get('#schema')
                if schem:
                    obj.schema = self.stock_param.schemas[schem].get_classe(obj.ident)
                    nb_recup += 1
                if obj.schema is None:
                    print('recup: objet sans schema', obj.ido, obj.attributs)
                yield obj

            if self.stock_param.debug:
                print("nombre d'objets relus :", nb_recup)
            os.remove(self.discstore[groupe]) # on fait le menage
            del self.discstore[groupe]
#        print ('recupobjets',self.stockage[groupe].keys())
#        print(self.stockage[groupe])

        for classe in self.stockage[groupe]:
            liste = self.stockage[groupe][classe]
            for obj in liste:
                if obj.schema is None:
                    print('recupliste: objet sans schema', obj.ido, obj.ident, obj.virtuel)
                    continue
#                print ('recup obj',obj.ido,obj.copie,obj.ident,'->',obj.schema,obj.virtuel)
                yield obj
        del self.stockage[groupe]

    def add_tmp_store(self, obj):
        ''' stockage temporaire au niveau de la regle pour les regles necessitant
    l'ensemble des donnees pour faire le traitement'''
#TODO prevoir un stockage disque si la conso memeoire est trop forte
        self.tmp_store.append(obj) # on stocke les objet pour l'execution de la regle


    def change_schema_nom(self, obj, nom_schema):
        '''change le schema d'une classe et le cree si besoin'''
        ident = obj.ident
        #groupe, classe = ident
        schema2 = self.stock_param.init_schema(nom_schema, fich=self.nom_fich_schema, origine='S',
                                               modele=obj.schema.schema if obj.schema else None)

        schema_classe = schema2.get_classe(ident, cree=True, modele=obj.schema,
                                           filiation=True)
        if not schema_classe:
            print('erreur changement classe', ident, obj.schema)
        obj.setschema(schema_classe)

#    def dupplique(self):
#        '''retourne une copie de la regle
#            sert pour le multiiprocessing'''
#        stock_param = self.stock_param
#        self.stock_param = None
#        reg2 = copy.deepcopy(self)
#        self.stock_param = stock_param

#        ob2.schema = old_sc
#        if old_sc is not None:
#            old_sc.objcnt += 1 # on a un objet de plus dans le schema
#        return reg2

    def runscope(self):
        '''determine si une regle peut tourner'''
        pdef = self.getvar('process', 'all')
#        print('runscope', pdef, self.stock_param.parent is None)
        if pdef == 'all':
            return True
        if pdef == 'worker':
            return self.stock_param.worker
        if pdef == 'main':
            return self.stock_param.parent is None and not self.stock_param.worker
        if pdef == 'child':
            return self.stock_param.parent is not None
        return True


    def get_max_workers(self):
        ''' retourne le nombre de threads paralleles demandes'''
        try:
            multi = self.getvar('multi', '1')
            if ':' in multi:
                tmp = multi.split(':')
                process = int(tmp[0])
                ext = int(tmp[1])
            else:
                process = int(multi)
                ext = -1
        except ValueError:
            process, ext = 1, 1
        nprocs = os.cpu_count()
        if self.stock_param.worker: # si on est deja en parallele on ne multiplie plus
            process = 1
        if nprocs is None:
                nprocs = 1
        if process < 0:
            process = -nprocs*process
        if ext < 0:
            ext = -process*ext
        return process, ext
