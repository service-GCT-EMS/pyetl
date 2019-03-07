# -*- coding: utf-8 -*-
''' format texte en lecture et ecriture'''

#import time
#import pyetl.schema as SC
import sys
import os
from . import fileio
from .interne.objet import Objet



class TextWriter(fileio.FileWriter):
    """writer de fichiers texte"""

#    def open(self):
#        """ouverture de fichier"""
#        try:
#            self.fichier = sys.stdout if self.nom == "#print" else\
#                           open(self.nom, 'w', encoding=self.encoding)#stdout
#            self.stats[self.nom] = self.stats.get(self.nom, 0)
#        except IOError:
#            self.etat = self.FAIL
#            print("erreur ouverture fichier")

    def reopen(self):
        """reouverture"""
        self.fichier = sys.stdout if self.nom == "#print" else\
                       open(self.nom, 'a', encoding=self.encoding)#stdout

    def close(self):
        """fermeture"""
#        print("fileeio fermeture", self.nom)
        if self.nom == "#print":
            return # stdout
        try:
            self.fichier.close()
        except AttributeError:
            print('error: fw  : writer close: fichier non defini', self.nom)


    def write(self, obj):
        '''ecrit un objet complet'''
        chaine = obj.attributs['contenu']
        self.fichier.write(chaine)
        if chaine[-1] != "\n":
            self.fichier.write("\n")
        self.stats[self.nom] += 1
        return True



def lire_textfile(self, rep, chemin, fichier):
    ''' lecture d'un fichier et stockage des objets en memoire de l'ensemble du texte en memmoire'''
    regle = self.regle_ref
    stock_param = regle.stock_param
    n_obj = 0
    #ouv = None
    if chemin:
        groupe = chemin
    else:
        groupe = os.path.basename(rep)
    classe = fichier
    regle.ext = os.path.splitext[fichier][-1]
    if stock_param.get_param('filemode', 'ligne') == 'ligne':
        with open(os.path.join(rep, chemin, fichier), "r", 65536,
                  encoding=stock_param.get_param('codec_entree', 'utf-8'),
                  errors="backslashreplace") as ouvert:
            contenu = ''.join(ouvert.readlines())
            obj = Objet(groupe, classe, format_natif='file', conversion='noconversion')
            obj.attributs['contenu'] = contenu
            stock_param.moteur.traite_objet(obj, regle) # on traite l'objet precedent
            n_obj = 1
        return n_obj
    self.setident(groupe, classe)
    with open(os.path.join(rep, chemin, fichier), "r", 65536,
              encoding=stock_param.get_param('codec_entree', 'utf-8'),
              errors="backslashreplace") as ouvert:
        for ligne in ouvert:
            obj = self.getobj()
#            obj = Objet(groupe, classe, format_natif='file', conversion='noconversion')
            obj.attributs['contenu'] = ligne
            stock_param.moteur.traite_objet(obj, self.regle_start) # on traite l'objet precedent
            n_obj += 1
    return n_obj



def ecrire_objets(regle, _, attributs=None):
    '''ecrit un fichier dont le contenu est dans un attribut
    a partir d'un stockage memoire ou temporaire'''
#ng, nf = 0, 0
#memoire = defs.stockage
#    print( "ecrire_objets asc")
    rep_sortie = regle.getvar('_sortie')
    sorties = regle.stock_param.sorties
    numero = regle.numero
    dident = None
    ressource = None
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):# on parcourt les objets
            if obj.virtuel: # on ne traite pas les virtuels
                continue
            if obj.ident != dident:
                groupe, classe = obj.ident
                if regle.fanout == 'groupe':
                    nom = sorties.get_id(rep_sortie, groupe, '', regle.ext)
                else:
                    nom = sorties.get_id(rep_sortie, groupe, classe, regle.ext)

                ressource = sorties.get_res(numero, nom)
                if ressource is None:
                    if os.path.dirname(nom):
                        os.makedirs(os.path.dirname(nom), exist_ok=True)

                    streamwriter = TextWriter(nom, encoding=regle.stock_param.get_param
                                              ('codec_sortie', 'utf-8'),
                                              liste_fich=regle.stock_param.liste_fich)
                    streamwriter.set_liste_att(attributs)
                    ressource = sorties.creres(numero, nom, streamwriter)
                regle.ressource = ressource
                dident = (groupe, classe)
            ressource.write(obj, regle.numero)
