# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 12:03:23 2015

@author: 89965
"""
import os
from .interne.objet import Objet

# statistiques

class Statdef(object):# definition d'une statistique
    '''gestion des objets statistiques
        les objets statistiques ne sont pas lies a un objet mais permettent
        d'accumuler des informations attributaires sur un ensemble d'objets
        les statistiques gérees sont actuellement :
        cont : comptage
        somme : somme des valeurs
        min : minimum
        max : maximum
        moy: moyenne
        val : ensemble des valeurs distinctes
        une stat est associee a un ensemble d'objets remplissant une condition,
        eventuellement eclatee en fonction d'un attribut.

    '''
    def __init__(self, nom, debug=1):
        self.nom = nom
        self.colonnes = []
        self.colonnes_sortie = None
        self.debug = debug
#        self.debug = 1
        self.indirect = False
        self.types = dict() # type des colonnes
        self.formats = {"cnt": lambda x: '%d' % (x,) if x else '0',
                        "somme": lambda x: '%g' % (x,) if x else '0',
                        "min": lambda x: '%g' % (x,) if x else '0',
                        "max": lambda x: '%g' % (x,) if x else '0',
                        "moy": lambda x: str(float(x[0])/x[1]) if x and x[1] else " ",
                        "minc": str,
                        "maxc": str,
                        "val": lambda x: ','.join(x) if x else '',
                        "valtri": lambda x: ','.join(sorted(x)) if x else '',
                        "val_uniq": lambda x: ','.join(sorted(x)) if x else ''}

    def ajout_colonne(self, colonne, vtype):
        '''ajoute une colonne a une stat
           une colonne correspond a l'accumulation d'un type d'information
        '''
        if not colonne:
            print('stat: ajout_colonne:erreur definition colonne', vtype)
            return
        self.colonnes.append(colonne)
        self.types[colonne] = vtype #ajoute une colonne a une stat
        if colonne[0] == '[':
            self.indirect = True
        if self.debug:
            print("debug:format: definition stat ", colonne, vtype, self.types)


    def get_names(self, colonnes_indirectes, process=False):
        '''refait la liste des colonnes pour tenir compte des indirections'''
        nouv_colonnes = []
        for i in self.colonnes:
            if i[0] == '[':
                nouv_colonnes.extend([j for j in sorted(colonnes_indirectes.keys())
                                      if colonnes_indirectes[j] == i])
                for j in colonnes_indirectes.keys():
                    self.types[j] = self.types[i]
            else:
                if i[0] != '#' or process:
                    nouv_colonnes.append(i)
        self.colonnes_sortie = nouv_colonnes
        return nouv_colonnes



    def entete(self, colonnes_indirectes):
        '''retourne la ligne d'entete pour l'ecriture finale.'''
        # s'il y a des colonnes par contenu : il faut refaire la liste des colonnes
        self.get_names(colonnes_indirectes)
        return ";".join([self.nom]+self.colonnes_sortie)

    def entete_liste(self, colonnes_indirectes):
        '''retourne la ligne d'entete pour l'ecriture finale.'''
        # s'il y a des colonnes par contenu : il faut refaire la liste des colonnes
        self.get_names(colonnes_indirectes)
        return [self.nom]+self.colonnes_sortie

    def get_vals(self, categorie, valeurs):
        ''' retourne la liste des valeurs pour une categorie'''
        try:
            return [self.formats[self.types[i]](valeurs.get((categorie, i), 0))
                    for i in self.colonnes_sortie]
        except KeyError:
            print([(valeurs.get((categorie, i), 0)) for i in self.colonnes_sortie])
            return []


    def ligne(self, categorie, valeurs):
        '''retourne une ligne formatee pour l'ecriture finale.'''
        return ";".join([categorie]+self.get_vals(categorie, valeurs))

    def ligne_liste(self, categorie, valeurs):
        """retourne les elements sous forme de liste"""
        return [categorie]+self.get_vals(categorie, valeurs)
#    @staticmethod
#    def sortir_moyenne(valeur):
#        '''calcul de la moyenne pour l'ecriture finale'''
#        return str(float(valeur[0])/valeur[1]) if valeur[1] else " "
#
def _get_number(valeur):
    '''teste si une valeur est numerique'''
    try:
        val = int(valeur)
    except ValueError:
        val = float(valeur)
    return val

class ExtStat(object):
    ''' structure de stockage simplifie de stats externes'''
    def __init__(self, nom, entete):
        self.nom = nom # nom de la stat (fichier de sortie)
        self.entete = entete
        self.lignes = [] # nom des colonnes

    def add(self, entete, contenu):
        '''ajoute du contenu a une stat'''
        if entete != self.entete:
            print('erreur stats incomtatibles', self.nom, self.entete, '->', entete)
            return False
        self.lignes.extend(contenu)
#        print('contenu de la stat' ,self.nom, len(self.lignes))

    def ecrire(self, rep_sortie, affiche=False, filtre='', defaut=None, codec='utf-8', wid=''):
        ''' sortie stat en format csv'''
        nom = self.nom
        if wid:
            nom = nom+'_'+wid
        result = sorted(self.lignes)
#        print ("extstats:",result)
        if rep_sortie:
            try:
                os.makedirs(rep_sortie, exist_ok=True)
                fichier = open(os.path.join(rep_sortie, nom+".csv"), "w",
                               encoding=codec)
                fichier.write(';'.join(self.entete)+"\n")
                fichier.write('\n'.join([';'.join(i) for i in result]))
                fichier.close()
                return
            except PermissionError:
                print('!!!!!!!! erreur ouverture fichier stats',
                      os.path.join(rep_sortie, nom)+".csv")
                affiche = True
            except NotADirectoryError:
                print('!!!!!!!! repertoire de sortie non defini')
                affiche = True
        else:
            if defaut == "affiche":
                affiche = True

        if affiche:
#            print('affichage stats ext', nom, "[", filtre, "]")
#            print('\t'.join(self.entete))
#            print('\n'.join(['\t'.join(i) for i in result if filtre in i[0]]))

            nom, entete, contenu = self.retour(filtre)
            print('affichage stats ext', nom, ("["+filtre+"]" if filtre else ''))
            statprint(nom, entete, contenu)


    def to_obj(self, stock_param):
        '''convertit une stat en objets pour traitement'''

        nlignes = 0
        nom_groupe, nom_classe = self.nom.split('_')
#        print(" conversion stat en objet", nom_schema, nom_groupe, nom_classe)
        maxobj = stock_param.get_param('lire_maxi', 0)

        if stock_param.get_param("schema_entree"):
            schema_courant = stock_param.schemas[stock_param.get_param("schema_entree")]
            nom_groupe, nom_classe = schema_courant.map_dest((nom_groupe, nom_classe))
        else:
            schema_courant = stock_param.init_schema(':schema_stats', 'F')

        schemaclasse = schema_courant.setdefault_classe((nom_groupe, nom_classe))

        colonnes = self.entete
        noms_attributs = [i.strip().replace(' ', '_') for i in colonnes]
#        print( "conversion stats,",result, self.valeurs)
#        print("stattoobj",noms_attributs)
        for valtmp in sorted(self.lignes):
#            print ("traitement stat",i)
            obj = Objet(nom_groupe, nom_classe, format_natif='interne')
            obj.setschema(schemaclasse)

            obj.attributs.update([(n, v) for n, v in zip(noms_attributs, valtmp)])
            nlignes = nlignes+1
            obj.setorig(nlignes)
            obj.attributs['#type_geom'] = '0'
#            print("traitement objet stat",obj.attributs)
            stock_param.moteur.traite_objet(obj, stock_param.regles[0])
            if maxobj: # nombre maxi d'objets a lire par fichier
                if nlignes >= maxobj:
                    obj = None
                    break
        return nlignes

    def retour(self, filtre=''):
        """renvoie une description de stats"""
        nom = self.nom.replace('#', '')
        return (nom, self.entete, self.lignes)







class Stat(object):
    ''' structure de stockage des statistiques.'''

    def __init__(self, nom, structure):
        self.nom = nom # nom de la stat (fichier de sortie)
        self.lignes = set()# nom des lignes
        self.colonnes_indirect = dict() # nom des colonnes
        self.valeurs = dict() # valeurs
        self.structure = structure # description de la stat # type statdef
        self.clef_tri = None
        self.ordre = None
        self.fonctions_stat = {"cnt": self._cnt,
                               "somme": self._somme,
                               "min": self._min,
                               "minc": self._minc,
                               "maxc": self._maxc,
                               "max": self._max,
                               "moy": self._moy,
                               "valtri": self._val,
                               "val": self._val,
                               "val_uniq": self._val_unique}

        self.types_stat = {"cnt": 'E', "somme": 'F', "min": 'F',
                           "minc": 'T', "maxc": 'T', "max": 'F',
                           "moy": 'F', "val": 'T', "valtri": 'T', "val_uniq": 'T'}


    def _cnt(self, clef, _):
        '''compteur'''

        self.valeurs[clef] = self.valeurs.get(clef, int(0))+1
#        print ("compteur",clef,valeur,ligne,self.valeurs,self.lignes)


    def _val(self, clef, valeur):
        '''stocke la liste des valeurs'''
        if clef in self.valeurs:
            self.valeurs[clef].append(valeur)
        else:
            self.valeurs[clef] = [valeur]

    def _val_unique(self, clef, valeur):
        '''stocke la liste des valeurs uniques'''
        if clef in self.valeurs:
            self.valeurs[clef].add(valeur)
        else:
            self.valeurs[clef] = {valeur}

    def _somme(self, clef, valeur):
        '''somme des valeurs'''
#        print ("somme",clef,valeur,self.valeurs,self.lignes)

        val = _get_number(valeur)
        self.valeurs[clef] = self.valeurs.get(clef, 0)+val
#        print ("somme", clef, self.valeurs[clef], val)

    def _min(self, clef, valeur):
        '''min des valeurs'''
        val = _get_number(valeur)
        self.valeurs[clef] = min(self.valeurs.get(clef, val), val)

    def _minc(self, clef, valeur):
        '''min des valeurs en mode alpha'''
        self.valeurs[clef] = min(self.valeurs.get(clef, valeur), valeur)

    def _max(self, clef, valeur):
        '''max des valeurs'''
        val = _get_number(valeur)
        self.valeurs[clef] = max(self.valeurs.get(clef, val), val)

    def _maxc(self, clef, valeur):
        '''max des valeurs en mode alpha'''
        self.valeurs[clef] = max(self.valeurs.get(clef, valeur), valeur)

    def _moy(self, clef, valeur):
        '''moyenne des valeurs'''
        val = _get_number(valeur)
        somme, nbval = self.valeurs.get(clef, (0, 0))
        self.valeurs[clef] = (somme+val, nbval+1)


    def ajout_valeur(self, ligne, colonne, valeur, val_colonne=None):
        '''ajoute une valeur a une stat.
        appele dans le traitement des objets pour chaque objet
        perfs a ameliorer a l'occasion
        '''
        #print self.structure.types
        #print ('formats:ajout_valeur',ligne,colonne,valeur,val_colonne)
        if colonne[0] == '[': #eclatement par colonnes
            clef = (ligne, val_colonne)
            self.colonnes_indirect[val_colonne] = colonne
        else:
            clef = (ligne, colonne)
        vtype = self.structure.types[colonne]
#        print('ajout_stat',clef,valeur,vtype)
        try:
            retour = self.fonctions_stat[vtype](clef, valeur)
            self.lignes.add(retour if retour is not None else ligne)

        except KeyError:
            print('error:format: fonction statistique inconnue', vtype)
            return False
        except ValueError:
            if valeur:
                print("error:format: stat valeur non numerique", vtype, valeur)
            return False

#
#        if vtype == "cnt":
#            self._cnt(clef, valeur)
#        elif vtype == "val":
#            self._val(clef, valeur)
#        elif vtype == "val_uniq":
#            self._val_unique(clef, valeur)
#        elif vtype == "somme":
#            self._somme(clef, valeur)
#        elif vtype == "min":
#            self._min(clef, valeur)
#        elif vtype == "max":
#            self._max(clef, valeur)
#        elif vtype == "moy":
#            self._moy(clef, valeur)
#        else:
#            print('error:format: fonction statistique inconnue', vtype)
#            return False
#        self.lignes[ligne] = 1
        return True


    def set_ordre(self, tri, sens):
        '''definit le mode de tri pour la sortie
            non utilise pour le moment
        '''
        self.clef_tri = tri
        self.ordre = sens

    def to_obj(self, stock_param):
        '''convertit une stat en objets pour traitement'''

        nlignes = 0
        #geom=False
        #separ=td.separ

        nom_groupe, nom_classe = self.nom
#        print(" conversion stat en objet", nom_schema, nom_groupe, nom_classe)
        maxobj = stock_param.get_param('lire_maxi', 0)

        if stock_param.get_param("schema_entree"):
            schema_courant = stock_param.schemas[stock_param.get_param("schema_entree")]
            nom_groupe, nom_classe = schema_courant.map_dest((nom_groupe, nom_classe))
        else:
            schema_courant = stock_param.init_schema(':schema_stats', 'F')

        schemaclasse = schema_courant.setdefault_classe((nom_groupe, nom_classe))

        colonnes = ["_clef"]+self.structure.get_names(self.colonnes_indirect,
                                                      process=True)
        noms_attributs = [i.strip().replace(' ', '_') for i in colonnes]
#        print( "conversion stats,",result, self.valeurs)
#        print("stattoobj",noms_attributs)
        for i in sorted(self.lignes):
#            print ("traitement stat",i)
            obj = Objet(nom_groupe, nom_classe, format_natif='interne')
            obj.setschema(schemaclasse)
            valtmp = i.split(':')+self.structure.get_vals(i, self.valeurs)

            obj.attributs.update([(n, v) for n, v in zip(noms_attributs, valtmp)])
            nlignes = nlignes+1
            obj.setorig(nlignes)
            obj.attributs['#type_geom'] = '0'
#            print("traitement objet stat",obj.attributs)
            stock_param.moteur.traite_objet(obj, stock_param.regles[0])

            if maxobj: # nombre maxi d'objets a lire par fichier
                if nlignes >= maxobj:
                    obj = None
                    break
        return nlignes

    def retour(self, filtre=''):
        """renvoie une description de stats"""
        nom = '_'.join(self.nom).replace('#', '')
        result = sorted(self.lignes)
        entete = self.structure.entete_liste(self.colonnes_indirect)
        corps = [self.structure.ligne_liste(i, self.valeurs)
                 for i in result if filtre in i]
        return (nom, entete, corps)



    def ecrire(self, rep_sortie, affiche=False, filtre='', defaut=None, codec='utf-8', wid=''):
        ''' sortie stat en format csv'''
        nom = '_'.join(self.nom).replace('#', '')
        if wid:
            nom = nom+'_'+wid
        result = sorted(self.lignes)
#        print ("stats:",result)

#            print("info :format: pas d ecriture stat ", affiche)
#        print("info :format: ecriture stat ", os.path.join(rep_sortie, nom)+".csv", affiche)

        if rep_sortie:
            if not wid:
                try:
                    os.makedirs(rep_sortie, exist_ok=True)
                    fichier = open(os.path.join(rep_sortie, nom+".csv"), "w",
                                   encoding=codec)
                    fichier.write(self.structure.entete(self.colonnes_indirect)+"\n")
                    fichier.writelines((self.structure.ligne(i, self.valeurs)+"\n" for i in result))
                    fichier.close()
                    return
                except PermissionError:
                    print('!!!!!!!! erreur ouverture fichier stats',
                          os.path.join(rep_sortie, nom)+".csv")
                    affiche = True
                except NotADirectoryError:
                    print('!!!!!!!! repertoire de sortie non defini')
                    affiche = True

        else:
            if defaut == "affiche":
                affiche = True

        if affiche:
            nom, entete, contenu = self.retour(filtre)
            print('affichage stats', nom, ("["+filtre+"]" if filtre else ''))
            statprint(nom, entete, contenu)


def statprint(nom, entete, contenu):
    '''formatte des stats pour l'affichage'''

    tailles = [max(map(len, i)) for i in zip(*contenu, entete)]
    longueur = sum(tailles)+3*len(tailles)-2

    pformat = '| %-'+str(tailles[0])+'s'+' | '.join('%'+str(i)+'s' for i in tailles[1:])+' |'
    print('-'*longueur)

    print(pformat % tuple(entete))
    print('-'*longueur)

#            print("\n".join((self.structure.ligne(i, self.valeurs).replace(';', '\t')
#                             for i in result if filtre in i)))
    print("\n".join((pformat % tuple(i) for i in contenu)))
    print('-'*longueur)
