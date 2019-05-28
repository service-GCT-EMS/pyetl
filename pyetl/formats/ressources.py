# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 10:19:32 2017

@author: 89965
"""
import collections
import os
import logging
DEBUG = 0
LOGGER = logging.getLogger("pyetl")  # un logger

class RessourceDistante(object):
    """une ressource distante est geree par un worker en traitement parallele
        on simule son existance pour les stats"""

    def __init__(self, nom):
        self.nom = nom
        self.etat = 0  # 0: non cree 1:ouvert 2:ferme 3:finalise
        self.nbo = 0

    def __repr__(self):
        return 'ressource distante:'+self.nom+' '+str(self.etat)

    def finalise(self):
        """ retourne le nombre d'objet"""
        if self.etat > 2:
            print ('ressource deja finalisee',self)
            return -1
        self.etat = 3
        return self.nbo

    def cnt(self):
        """ incremente le compteur"""
        self.nbo += 1

class Ressource(object):
    """ stockage des infos d'une ressource
    une ressource peut etre un fichier ou une table"""

    def __init__(self, nom, handler):
        self.nom = nom
        self.handler = handler
        self.lastid = None
        self.etat = 0  # 0: non cree 1:ouvert 2:ferme 3:finalise
        self.nbo = 0
        self.regles = set()

    def __repr__(self):
        return 'ressource:'+self.nom+' '+str(self.etat)+' '+repr(self.handler)

    def ouvrir(self, id_regle):
        """ ouvre une ressource (en general un fichier)"""
        try:
            if self.etat == 3:
                return False
            self.regles.add(id_regle)
            if self.etat == 0:
                self.handler.open()
                self.etat = 1
            if self.etat == 2:
                self.handler.reopen()
                self.etat = 1
        except IOError as err:
            LOGGER.critical("erreur ouverture fichier " +self.nom+'->'+repr(err))
            raise StopIteration(2)


    def fermer(self, id_regle):
        """ referme une ressource """
        if id_regle == -1:
            self.handler.close()
            self.etat = 2
            self.regles = set()
        self.regles.discard(id_regle)
        #        print ('fermeture ressource',self.nom,self.regles,id_regle)
        if not self.regles:
            if self.etat == 1:
                self.handler.close()
            self.etat = 2
    def bwrite(self, obj, id_regle):
        try:
            if self.etat != 1:
                self.ouvrir(id_regle)
            if self.lastid and self.lastid != obj.ident:
                self.handler.changeclasse(obj.schema)
            self.lastid = obj.ident
            if self.handler.bwrite(obj):
                self.nbo += 1
        except IOError as err:
            LOGGER.critical("erreur ecriture fichier " +self.nom+'->'+repr(err))
            raise StopIteration(2)

    def write(self, obj, id_regle):
        """ecrit un objet en gerant les changements de classe et les comptages"""
        #        print('dans ressouce.write',self.lastid,self.etat)
        try:
            if self.etat != 1:
                self.ouvrir(id_regle)
            if self.lastid and self.lastid != obj.ident:
                self.handler.changeclasse(obj.schema)
            self.lastid = obj.ident
            if self.handler.write(obj):
                self.nbo += 1
        except IOError as err:
            LOGGER.critical("erreur ecriture fichier " +self.nom+'->'+repr(err))
            raise StopIteration(2)

    def compte(self, nbr):
        """ compte le nobre d'objets sortie vers une ressource"""
        self.nbo += nbr

    def finalise(self):
        """ finalise une ressource : une resource finalisee ne peut pas etre reouverte"""
        if self.etat == 0:
            LOGGER.error("ressource indisponible "+self.nom)
            return -1
        if self.etat > 2:
            LOGGER.warning("ressource deja finalisee "+self.nom)
            return -1
        self.etat = self.handler.finalise()
        return self.nbo


class GestionSorties(object):
    """ gestion des ressources ouvertes """

    def __init__(self, maxcles=20, rep_sortie=None):
        self.locks = dict()  # regle verouille ressource
        self.used = collections.OrderedDict()  # ressources ouvertes
        self.maxcles = maxcles
        self.ressources = dict()
        self.rep_sortie = rep_sortie

    def get_res(self, id_demand, id_ressource):
        """ verouille une ressource existante"""
        if id_ressource in self.ressources:
            self.lock(id_demand, id_ressource)
            return self.ressources[id_ressource]
        return None

    def creres(self, id_demand, id_ressource, handler):
        """ verouille une recssource et la cree si necessaire"""
        if id_ressource not in self.ressources:
            self.ressources[id_ressource] = Ressource(id_ressource, handler)
            self.lock(id_demand, id_ressource)
            return self.ressources[id_ressource]
        return self.get_res(id_demand, id_ressource)

    def creres_distante(self, nom, nbo):
        """cree une ressource virtuelle pour les traitements parraleles"""
        if nom not in self.ressources:
            self.ressources[nom] = RessourceDistante(nom)
        self.ressources[nom].nbo += nbo
        return self.ressources[nom]

    def setcnt(self, nom):
        """cree une ressource de comptage pour la sortie poubelle"""
        if nom not in self.ressources:
            self.ressources[nom] = RessourceDistante(nom)
        self.ressources[nom].cnt()


    def lock(self, id_demand, id_ressource):
        """declare l utilisation de la ressource"""
        if id_ressource in self.used and id_demand in self.ressources[id_ressource].regles:
            self.used.move_to_end(id_ressource, last=True)
        elif id_ressource in self.used:
            self.used.move_to_end(id_ressource, last=True)
            self.ressources[id_ressource].regles.add(id_demand)
            self.used[id_ressource] += 1
            self.unlock(id_demand)
        else:
            self.unlock(id_demand)
            self.used[id_ressource] = 1
            self.ressources[id_ressource].regles.add(id_demand)
            if self.maxcles and len(self.used) > self.maxcles:
                #            il y a trop de ressources ouvertes on en ferme une
                #                print ('fermeture ressource')
                for i in self.used:
                    if self.used[i] == 0:
                        ressource = self.ressources[i]
                        ressource.fermer(id_demand)
                        del self.used[i]
                        break

        self.ressources[id_ressource].ouvrir(id_demand)
        self.locks[id_demand] = id_ressource

    def unlock(self, id_demand):
        """libere une ressource"""
        if id_demand in self.locks:
            id_ressource = self.locks[id_demand]
            if id_ressource in self.used:
                self.used[id_ressource] -= 1
            self.ressources[id_ressource].regles.discard(id_demand)
            del self.locks[id_demand]

    def final(self):
        """fin de ficher"""
        nb_obj = 0
#        print ('dans final', self.ressources)
        nb_fich = 0
        for res in self.ressources.values():
            nob = res.finalise()
            if nob != -1:
                nb_obj += nob
                nb_fich += 1
#        print('final', nb_fich, nb_obj)
        return nb_fich, nb_obj

    def close(self, id_demand, id_ressource):
        """ferme une ressource et la libere"""
        ressource = self.ressources[id_ressource]
        ressource.fermer(id_demand)
        self.unlock(id_demand)
        #        del self.rescount[id_ressource]
        if self.used.get(id_ressource) == 0:
            del self.used[id_ressource]

    #    def closeall(self):
    #        for i in list(self.liste_ouverts):
    #            self.close(i)
    def set_sortie(self, rep_sortie):
        """positionne le repertoire de sortie par defaut"""

        self.rep_sortie = rep_sortie

    def get_id(self, rep_sortie, groupe, classe, ext, nom=None):
        """retourne un nom de fichier standardise"""
        rep_sortie = rep_sortie if rep_sortie else self.rep_sortie
        if not rep_sortie:
            raise NotADirectoryError("repertoire de sortie non défini")
        if nom:
#            print("-------------------nom forcé", os.path.join(rep_sortie, nom))
            if os.path.isabs(nom):
                return nom
            return os.path.join(rep_sortie, nom)
        if groupe == "#nogroup":
            groupe = ""
        if groupe and classe and groupe.upper() != classe.upper():
            return os.path.join(rep_sortie, groupe, classe + ext)
        if groupe:
            return os.path.join(rep_sortie, groupe + ext)
        if classe:
            return os.path.join(rep_sortie, classe + ext)
        print("!!!!! clef non definie", rep_sortie, "<->", os.path.join(rep_sortie, "defaut" + ext))
        #        raise
        return os.path.join(rep_sortie, "defaut" + ext)

    def getstats(self):
        """recupere les stats d'ecriture"""
        return {nom:self.ressources[nom].nbo for nom in self.ressources}

