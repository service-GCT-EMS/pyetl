# -*- coding: utf-8 -*-
"""gestion des grilles de conversion"""
import csv

# import pickle
import math as M
import os

# def charge(nom): # retourne une grille chargee
#    gril = grille()
#    gril = pickle.load(open(nom, 'rb'))
#    return gril
#
# def stocke(gril, nom):
#    pickle.dump(gril, open(nom, 'wb'), 2) # sauve une grille
#


def lire(nom):
    """lit une grille en csv"""
    reader = csv.reader(
        open(nom + ".csv"), delimiter=";"
    )  # lecture du fichier csv de forme id;x;y
    grille = Grille()
    for row in reader:  # stockage des points en memoire
        if row[0] == "#pas_grille":
            grille.pas = float(row[1])
        elif row[0] == "#nom_grille":
            grille.nom = row[1]
        elif "#" in row[0]:
            pass  # on ignore tous les commentaires
        else:
            grille.stocke_noeud(row[0], row[1], row[2])
    grille.nom_orig = grille.nom
    grille.valide_grille()  # on verifie que tous les coins sont presents et on prepare les mailles
    return grille


def ecrire(grille, nom):
    """ecrit une grille en csv"""
    writer = csv.writer(open(nom + ".csv", "wb"), delimiter=";")
    # ecriture du fichier csv de forme id;x;y
    writer.writerow(["#pas_grille", "%f" % grille.pas])
    writer.writerow(["#nom_grille", grille.nom_orig])
    noeuds = grille.valeurs.keys()
    noeuds.sort()
    for noeud in noeuds:
        xc_noeud, yc_noeud = noeud
        xreel, yreel = xc_noeud * grille.pas, yc_noeud * grille.pas
        dec_x, dec_y, _ = grille.valeurs[noeud]
        writer.writerow(
            ["%6.6d%6.6d" % noeud, "%f" % (xreel + dec_x), "%f" % (yreel + dec_y)]
        )


class ListeGrilles:
    """liste de grilles"""

    def __init__(self, repertoire, liste, sens):
        self.grilles = list()
        #        print ('grilles a lire ',repertoire,liste)
        lgrille = os.path.join(repertoire, liste)
        for i in open(
            lgrille, "r"
        ):  # fichier contenant la liste des grilles à utiliser
            nom = i.strip("\n")  # lecture des différents noms de fichiers de grille
            grille = lire(repertoire + "/" + nom)  # chargement de la grille
            # modification du nom pour tenir compte du sens d'utilisation de la grille
            if sens == 2:
                grille.nom = grille.nom + " inverse"
            grille.sens = sens
            grille.valide = 1
            self.grilles.append(grille)  # liste des definitions de grilles

    def recup_corrections(self, x_orig, y_orig):
        """Transformation de coordonnées en utilisant une grille locale"""
        for grille in self.grilles:  # on cherche la bonne grille
            dec_x, dec_y, calcul = grille.recup_corrections(x_orig, y_orig)
            # if calcul : print (dx,dy,g.nom)
            if calcul:
                return (dec_x, dec_y, grille.nom)
        return (0.0, 0.0, "nogrille")
        # RETOUR : coordonées planes transformées et grille utilisée

    def controle_coherence(self, correct=0):
        """controle la coherence d'une liste de grilles"""
        print("controle")
        inc = 0
        for grille in self.grilles:
            grille.valide = 0
            # on devalide la grille courante pour calculer avec la grille de niveau superieur
            nbnoeuds = len(grille.valeurs)
            xmin, ymin, xmax, ymax = grille.emprise
            nth = ((xmax - xmin) / grille.pas + 1) * ((ymax - ymin) / grille.pas + 1)
            if nbnoeuds != nth:
                print("dg3: nombre de noeuds incorrects")
            dmax, ninc = 0, 0

            for noeud in grille.valeurs:
                code_x, code_y = noeud
                x_noeud, y_noeud = code_x * grille.pas, code_y * grille.pas

                if (
                    x_noeud == xmin
                    or x_noeud == xmax
                    or y_noeud == ymin
                    or y_noeud == ymax
                ):
                    # noeud du bord
                    dx1, dy1, nom = self.recup_corrections(x_noeud, y_noeud)
                    dx0, dy0, calcul = grille.valeurs[noeud]
                    ecart = M.sqrt(
                        (dx0 - dx1) * (dx0 - dx1) + (dy0 - dy1) * (dy0 - dy1)
                    )
                    if ecart > 0.000002:
                        ninc += 1
                        dmax = max(dmax, ecart)

                        if correct:  # on force la coherence
                            grille.valeurs[noeud] = dx1, dy1, calcul
                            # print "modifié,",noeud,dx1,dy1,calcul
                        else:
                            print(
                                "dg3:grille incoherente",
                                grille.nom,
                                "<>",
                                nom,
                                noeud,
                                dx0,
                                "<>",
                                dx1,
                                dy0,
                                "<>",
                                dy1,
                            )
            if ninc:
                inc = 1
                print("dg3:grille incoherente", grille.nom, "<>", nom, ninc, dmax)
            grille.valide = 1  # on reenclenche la grille
        if inc:
            print("dg3:ensemble de grilles incoherent")
            if correct:  # on force la coherence
                for grille in self.grilles:
                    grille.valide_grille()  # on reporte les modifs dans les mailles precalculees
        else:
            print("dg3:ensemble de grilles coherent")
        return inc

    def ecrire_liste(self, repertoire, liste):
        """cree la liste de grilles """
        with open(repertoire + "/" + liste, "w") as fich:
            for grille in self.grilles:
                fich.write(grille.nom_orig + "\n")
                ecrire(grille, repertoire + "/" + grille.nom_orig)


def calcule_maille(noeud):  # codes des 4 coins de la maille
    """determine les codes des 4 points de la maille"""
    maillex, mailley = noeud
    noeud2 = (maillex + 1, mailley)
    noeud3 = (maillex, mailley + 1)
    noeud4 = (maillex + 1, mailley + 1)
    return (noeud, noeud2, noeud3, noeud4)


class Grille:
    """grille de correction lambert lambert"""

    def __init__(self):
        self.precision = 0
        self.valide = 0
        self.emprise = (1e99, 1e99, -1e99, -1e99)
        #        self.xmin = 1e99
        #        self.ymin = 1e99
        #        self.xmax = -1e99
        #        self.ymax = -1e99
        self.nom = " "
        self.nom_orig = " "
        self.pas = " "
        self.valeurs = dict()
        self.cache_corrections = dict()

    def set_emprise(self, x_ref, y_ref):
        """ actualise l'emprise de la grille"""
        self.emprise = (
            min(x_ref, self.emprise[0]),
            min(y_ref, self.emprise[1]),
            max(x_ref, self.emprise[2]),
            max(y_ref, self.emprise[3]),
        )

    def dans_emprise(self, x_point, y_point):
        """ valide si un point est dans l'emprise"""
        xmin, ymin, xmax, ymax = self.emprise
        return self.valide and xmin < x_point < xmax and ymin < y_point < ymax

    def stocke_noeud(self, code, x_final, y_final):
        """ range un noeude dans la liste"""
        code = "%12.12d" % int(code)
        code_x = int(code[0:6])
        code_y = int(code[6:12])
        x_ref, y_ref = code_x * self.pas, code_y * self.pas
        self.valeurs[(code_x, code_y)] = (
            float(x_final) - x_ref,
            float(y_final) - y_ref,
            0,
        )
        # print xr,yr,row[0],row[1],row[2],row[0][0:4], row[0][4:8]
        self.set_emprise(x_ref, y_ref)

    #        self.xmin = min(x_ref, self.xmin)
    #        self.xmax = max(x_ref, self.xmax)
    #        self.ymin = min(y_ref, self.ymin)
    #        self.ymax = max(y_ref, self.ymax)
    # print code,xr,yr
    # print "emprise",self.xmin,self.xmax,self.ymin,self.ymax

    def valide_grille(self):  # prestocke toutes les valeurs ( acceleration du calcul)
        """prepare la grille ne memoire pour un acces plus rapide"""
        self.valide = 1
        for noeud in self.valeurs:
            noeud1, noeud2, noeud3, noeud4 = calcule_maille(noeud)
            # print coin, p1,p2,p3,p4
            if (
                noeud2 in self.valeurs
                and noeud3 in self.valeurs
                and noeud4 in self.valeurs
            ):
                dx1, dy1, _ = self.valeurs[noeud1]
                self.valeurs[noeud] = dx1, dy1, 1
                dx2, dy2, _ = self.valeurs[noeud2]
                dx3, dy3, _ = self.valeurs[noeud3]
                dx4, dy4, _ = self.valeurs[noeud4]
                self.cache_corrections[noeud] = dx1, dy1, dx2, dy2, dx3, dy3, dx4, dy4

    #        print ("dg3:emprise", self.xmin, self.xmax, self.ymin, self.ymax, self.nom)

    def calcule_coin(self, x_lamb, y_lamb):
        """identifie la maille contenant un point (code de la maille)"""
        return (
            int(x_lamb / self.pas),
            int(y_lamb / self.pas),
        )  # code de la maille contenant un point

    def recup_corrections(self, x_point, y_point):
        """retourne une correction calculee sur la grille"""
        if self.dans_emprise(x_point, y_point):
            #        if self.valide and self.xmin < x_point < self.xmax and self.ymin < y_point < self.ymax:
            x_rel = x_point / self.pas
            y_rel = y_point / self.pas
            code_x = int(x_rel)
            code_y = int(y_rel)
            # p1=self.calcule_coin(x,y)
            try:
                ex1, ey1, ex2, ey2, ex3, ey3, ex4, ey4 = self.cache_corrections[
                    (code_x, code_y)
                ]
            except KeyError:
                return (0, 0, 0)
            pos_x = x_rel - code_x  # position dans la maille
            pos_y = y_rel - code_y
            #            eax = (pos_y*ex3+(1-pos_y)*ex1)       # calcul bilineaire
            #            eay = (pos_y*ey3+(1-pos_y)*ey1)
            #            ebx = (pos_y*ex4+(1-pos_y)*ex2)
            #            eby = (pos_y*ey4+(1-pos_y)*ey2)
            ecart_x = (pos_y * ex4 + (1 - pos_y) * ex2) * pos_x + (
                pos_y * ex3 + (1 - pos_y) * ex1
            ) * (1 - pos_x)
            ecart_y = (pos_y * ey4 + (1 - pos_y) * ey2) * pos_x + (
                pos_y * ey3 + (1 - pos_y) * ey1
            ) * (1 - pos_x)
            return (ecart_x, ecart_y, 1)
        return (0, 0, 0)
