# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
"""
import re
import os
import copy
from collections import namedtuple
import pyetl.schema.schema_interne as SC
import pyetl.schema.fonctions_schema as FSC
#from pyetl.moteur.selecteurs import Selecteur
#import pyetl.formats.formats as F
#from pyetl.formats.interne.objet import Objet
import pyetl.formats.temporaire as T
#import pyetl.formats.mdbaccess as DB
#from pyetl.moteur.fonctions import gestion_schema as GS

class Branch(object):
    '''gestion des liens avec possibilite de creer de nouvelles sorties'''
    enchainements = {":", "sinon:", "fail:", "next:"}

    def __init__(self):
        self.brch = {'ok:': None, 'sinon:': None, 'fail:': None, 'next:': None, 'gen:': None}
        self.suivante = False

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
            self.suivante = self.brch['sinon:'].suivante if self.brch['sinon:'] else None



class ParametresFonction(object):
    ''' stockage des parametres standanrds des regles '''
    st_val = namedtuple("valeur", ("val", "num", "liste", "dyn", 'definition'))

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

    def _crent(self, nom, taille=0):
        '''extrait les infos de l'entite selectionnee'''
#        print("creent",nom,self.valeurs[nom].groups(),self.valeurs[nom].re)
        try:
            val = self.valeurs[nom].group(1)
            if r'\;' in val:
                val = val.replace(r'\;', ';') # permet de specifier un ;
#                val = val.replace(r'\b', 'b')
        except (IndexError, AttributeError):
            val = ""
        try:
            defin = self.valeurs[nom].group(2).split(',')
        except (IndexError, AttributeError):
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
        if self.definitions[nom].pattern == '|L':
            liste = val.split("|") if val else []
        dyn = "*" in val
#        var = "P:" in val

        return self.st_val(val, num, liste, dyn, defin)


    def __repr__(self):
        listev = ["sortie:%s"%(str(self.att_sortie)),
                  "entree:%s"%(str(self.att_entree)),
                  "defaut:%s"%(str(self.val_entree)),
                  "cmp1:%s"%(str(self.cmp1)),
                  "cmp2:%s"%(str(self.cmp2))
                 ]
        return "\n\t".join(listev)

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
#    enchainements = {":", "sinon:", "fail:", "next:"}
#    debug_ench = {0:'non lie', 1:'suite', 2:"sinon", 3:"fail", 4:"next"}
#    selecteurs = Selecteur
    def __init__(self, ligne, stock_param, fichier, numero, vloc=None):

        self.ligne = ligne
        self.stock_param = stock_param
        self.branchements = Branch()
        self.vloc = vloc if vloc is not None else dict() # variables locales a une macro
        self.params = None
        self.selstd = None
        self.valide = None
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
        self.debug = False # modificateurs de comportement
        self.champsdebug = None
        self.store = False
        self.nonext = False
        self.fonc = None
        self.fstore = None
        self.shelper = None
        self.fonction_schema = None

        self.val_tri = re.compile('')
        self.numero = numero
        self.index = 0
        self.bloc = 0

        self.action_schema = None
        self.final = False
        self.filter = False
        self.copy = False

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

        self.memlimit = int(self.getvar("memlimit"))
        self.erreurs = []
        self.v_nommees = dict()


    def __repr__(self):
        """pour l impression"""
        if self.ligne:
            return self.ligne[:-1] if self.ligne[-1] == '\n' else self.ligne
        return 'regle vide'


    def setparams(self, valeurs, definition):
        """positionne les parametres """
        self.params = ParametresFonction(valeurs, definition)


    def ftrue(self, *_):
        ''' toujours vrai  pour les expressions sans conditions'''
        return True

    def getregle(self, ligne, fichier, numero, vloc=None):
        '''retourne une regle pour des operations particulieres'''
        return RegleTraitement(ligne, self.stock_param, self.fichier, numero, vloc=vloc)

# acces aux variables
    def getvar(self, nom, defaut="", loc=1):
        """ retourne la valeur d'une variable
        si loc =0 on ne regarde pas les variables locales
        """
#        self.affiche('')
#        print(' recherche' ,nom,loc,self.vloc)
        if loc == 2 and nom+str(self.numero) in self.vloc: # superprivé
            return self.vloc[nom+str(self.numero)]
        if loc and nom in self.vloc:
#            print('variable locale',nom,self.vloc)
            return self.vloc[nom]
        return self.stock_param.get_param(nom, defaut)


    def setvar(self, nom, valeur, loc=0):
        """affecte une variable et la cree eventuellement en local
            loc  0 : affecte la variable en local si elle existe en global sinon
                 1 : affecte la variable en local
                 -1: affecte la variable en global
                 2 affecte en local mais ne cache pas la globale
                 """
        if loc == 2:
            self.vloc[nom+str(self.numero)] = valeur
        elif (nom in self.vloc and loc != -1) or loc == 1:
            self.vloc[nom] = valeur
        else:
#            print ('regle:set fallback ',nom,valeur)
#            raise
            self.stock_param.parms[nom] = valeur


    def affiche(self, origine=''):
        '''fonction d'affichage de debug'''

        print(origine+"regle:----->", self.index, "(", self.numero, ")", self.ligne[:-1],
              "bloc "+str(self.bloc) if self.bloc else ' '+ "enchainement:"+\
              self.enchainement if self.enchainement else ''+\
              " copy "+str(self.copy) if self.copy else ''+\
              " final "+str(self.final) if self.final else '')

    def endstore(self, nom_base, groupe, obj, freeze, geomwriter=None, nomgeom=None):
        ''' fonction de stockage avant ecriture finale necessiare si le schema
    doit etre determine a partir des donnees avant de les ecrire sur disque'''
#        print ('regle:dans endstore',self.numero,nom_base,groupe)
#        raise
        classe_ob = obj.ident
        if obj.virtuel:
            return
        if self.f_sortie.calcule_schema:
            if not obj.schema:
                nomschem = nom_base if nom_base else "defaut"
                schem = self.stock_param.schemas.get(nomschem)
                if not schem:
                    schem = SC.Schema(nomschem)
                    self.stock_param.schemas[nomschem] = schem

                FSC.ajuste_schema(schem, obj)
#                print (obj.schema.nom)

            for nom_att in obj.text_graph:
                obj.schema.stocke_attribut(nom_att+"_X", "float", '', 'reel')
                obj.schema.stocke_attribut(nom_att+"_Y", "float", '', 'reel')

        if freeze:
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
        for classe in self.stockage[groupe]:
            liste = self.stockage[groupe][classe]
            for obj in liste:
                if obj.schema is None:
                    print('recupliste: objet sans schema', obj.ido)
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
#        print ("changeschema:",obj.ident,obj.schema.schema.nom,"->",nom_schema)
        schema2 = self.stock_param.schemas.get(nom_schema)
        if not schema2:
#            print ('------------------------------------creation schema',
#                   obj.schema.schema.nom, '->', nom_schema)
            schema2 = self.stock_param.init_schema(nom_schema,
                                                   fich=self.nom_fich_schema,
                                                   origine='S',
                                                   modele=obj.schema.schema
                                                   if obj.schema else None)

        schema_classe = schema2.get_classe(ident, cree=True, modele=obj.schema,
                                           filiation=True)
        if not schema_classe:
            print('erreur changement classe', ident, obj.schema)
        obj.setschema(schema_classe)

    def dupplique(self):
        '''retourne une copie de la regle
            sert pour le multiiprocessing'''
        stock_param = self.stock_param
        self.stock_param = None
        reg2 = copy.deepcopy(self)
        self.stock_param = stock_param

#        ob2.schema = old_sc
#        if old_sc is not None:
#            old_sc.objcnt += 1 # on a un objet de plus dans le schema
        return reg2
