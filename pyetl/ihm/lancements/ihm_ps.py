# -*- coding: utf-8 -*-
"""creation d ihm poweshell a partir d un fichier de definition"""
import itertools
import os

def creihm(nom):
    nbb = 0
    class Ihm(object):
        def __init__(self, nom=None, interpreteur=None):
            self.nom=nom
            self.main=None
            self.elements=[]

        @property
        def colonnes(self):
            return self.main.colonnes

        @property
        def lignes(self):
            return self.main.lignes

        def genps(self):
            """genere le code ps pour l´ihm"""
            code =[]


    class Fenetre(object):
        _ido = itertools.count(1)
        def __init__(self,titre,largeur=None) -> None:
            self.id = "fenetre"+str(next(self._ido))
            self.largeur=largeur
            self.hauteur=0
            self.messages=None
            self.titre=titre
            self.elements=[]

        @property
        def colonnes(self):
            return max((i.colonne for i in self.elements))

        @property
        def lignes(self):
            maxlin=0
            cour=0
            for i in self.elements:
                if i.ligne=="+":
                    cour+=1
                elif i.ligne.isnum:
                    cour=int(i.ligne)
            maxlin=max(maxlin,cour)
            return maxlin

    class Fileselect(object):
        _ido = itertools.count(1)
        def __init__(self,lin,col,titre,selecteur,variable):
            self.id = "fselect"+str(next(self._ido))
            self.ligne=lin
            self.colonne=int(col)
            self.titre=titre
            self.selecteur=selecteur
            self.variable=variable


    class Droplist(object):
        _ido = itertools.count(1)
        def __init__(self,lin,col,titre,selecteur,variable):
            self.id = "dlist"+str(next(self._ido))
            self.ligne=lin
            self.colonne=int(col)
            self.titre=titre
            self.selecteur=selecteur
            self.variable=variable


    class Bouton(object):
        _ido = itertools.count(1)
        def __init__(self,lin,col,titre):
            self.id = "bouton"+str(next(self._ido))
            self.ligne=lin
            self.colonne=int(col)
            self.titre=titre
            self.elements=[]


    class Commande(object):
        def __init__(self,texte):
            self.commande=texte
            self.ligne="="
            self.colonne=0


    elem=None
    ihm=None
    courant=None
    with open(nom, "r") as f:
        for ligne in f:
            code, position, commande = ligne.split(";", 3)
            if code == "!ihm":
                if position == "init":
                    interpreteur = commande
                    nom_ihm=os.path.splitext(nom)[0]
                    if ihm:
                        "print erreur redefinition ihm "
                        raise StopIteration
                    ihm=Ihm(nom_ihm,interpreteur)
            elif code == "!fenetre":
                largeur = int(position)
                titre = commande
                if not ihm:
                    "print erreur cadre ihm non defini"
                    raise StopIteration
                elem=Fenetre(titre, largeur)
                if courant is None:
                    ihm.main=elem
                elif isinstance (courant,Bouton):
                    courant.elements.append(elem)
                elif isinstance (courant,Fenetre):
                    courant.elements.append(elem)
                courant=elem

            elif code == "!fileselect":
                lin, col = position.split(",")
                titre, selecteur, variable = commande
                courant.elements.append(Fileselect(titre,selecteur,variable))

            elif code == "!ps":
                courant.elements.append(Commande(commande))

            elif code == "!droplist":
                lin, col = position.split(",")
                titre, liste, variable = commande
                courant.elements.append(Droplist(lin,col,titre,liste,variable))

            elif code == "!button":
                lin, col = position.split(",")
                titre = commande
                elem=Bouton(lin,col,titre)
                if isinstance(courant,Bouton):
                    courant=ihm.elements[-1]
                courant.elements.append(elem)
                courant=elem

    nbcols =  ihm.maxcol
    nblignes = max(ihm.lignes)
    lcols=int((largeur-40)/nbcols)
    hauteur= lcols*50
    sortie=ihm.nom_ihm+".ps1"
    with open(sortie, "w") as f:
        f.write("# genere automatiquement par le generateur d ihm de mapper")
        f.write("")
        f.write("")
        f.write("Add-Type -AssemblyName System.Windows.Forms")
        f.write("$font=New-Object System.Drawing.Font('Microsoft Sans Serif',10)")
        f.write("$startx=20")
        f.writelines(ihm.genps)


$startx=40
