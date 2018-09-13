# -*- coding: cp1252 -*-
# formats d'entree sortie
''' format osm '''

import os
import time
import math as M
import sys
import itertools
import operator
from collections import defaultdict, namedtuple

#import numpy as np
POINT = namedtuple('pt',('x','y','z'))

class Geomobj(object):
    suivant = {0:1, 1:2, 2:0}
    precedent = {0:2, 2:1, 1:0}
    def __init__(self,nom):
        self.nom = nom
        self.points = []
        self.triangles = []
        self.triangleindex = defaultdict(set)
        self.edges = None
        self.npoints = 0
        self.ntriang = 0
        self.orig = None
        self.size = None

    def _vecteur(self, n1, n2):
        '''calcule le vecteur directeur d'une ligne'''
        p1 = self.points[n1]
        p2 = self.points[n2]
        return POINT(*(p2[i]-p1[i] for i in range(3)))

    def getp_atv(self, n1, n2, vref, indice):
        '''calcule un point sur la ligne a l'ascisse x o ordonnee'''
        p1 = self.points[n1]
        vecteur = self._vecteur(n1, n2)
        dv = vref-p1[indice]
        rapp = vecteur[indice] / dv
        p_final = POINT(*(p1[i] + vecteur[i]*rapp if i!=indice else vref for i in range(3)))
        return p_final



    def coupe_triangle(self, triangle, vref, fonction, indice):
        '''decoupe un triangle par rapport a une abscisse cote: 0 on garde les coordonnees inferieurs 1 les superieures'''
        tpt = tuple(self.points[i] for i in triangle)
        asupp = tuple(i for i in range(3) if not fonction(tpt[i][indice], vref))
        if len(asupp) == 1:
            ip = asupp[0]
#            print (" traitement sommet",ip)
            n2 = triangle[ip]
            n1 = triangle[self.suivant[ip]]
            p_suiv = self.getp_atv(n1, n2, vref, indice)
            n1 = triangle[self.precedent[ip]]
            p_pr = self.getp_atv(n1, n2, vref, indice)
            np = POINT(*((p_suiv[i]+p_pr[i])/2 if i!= indice else vref for i in range(3)))
            self.points[n2] = np


    def decoupe(self, vref, fonc, indice):
        nouveaux = []
        for tr in self.triangles:
            nok = sum(fonc(self.points[i][indice], vref) for i in tr)
            if nok == 3:
                continue
            elif nok:
                pass
#                tr2 = self.coupe_triangle(tr, vref, fonc, indice)
#                if tr2:
#                    nouveaux.add(tr2)
            else:
                tr.clear()
        self.triangles.extend(nouveaux)
        self.del_unused()
        self.reindex()




    def getused(self):
        """retourne une liste de points utilises"""
        return {j for tr in self.triangles for j in tr}
    
    def del_unused(self):
        used = self.getused()
        n=0
        for i in range(len(self.points)):
            if i in used:
                continue
            if self.points[i]:
                self.points[i]=[]
                n+=1
        print(" points inutilises supprimes ",n)

    def triangleindexer(self):
        ''' indexe les triangles par les points '''
        for num, tr in enumerate(self.triangles):
            if tr:
                n1, n2, n3 = tr
                self.triangleindex[n1].add(num)
                self.triangleindex[n2].add(num)
                self.triangleindex[n3].add(num)

    def bbox(self):
        ''' calcule la bounding box '''
#        used = self.used()
        self.orig = POINT(*(min((pt[i] for pt in self.points if pt)) for i in range(3)))
        self.size = POINT(*(max((pt[i] for pt in self.points if pt))-self.orig[i] for i in range(3)))
        print('taille modele ' ,self.size, 'point min: ',self.orig)

    def getbbox(self, garde):
        if self.orig is None:
            self.bbox()
        orig = POINT(*(self.orig[i]-garde for i in range(3)))
        size = POINT(*(self.size[i]-garde for i in range(3)))
        return orig, size

    def clean_triangles_byindex(self, n2, n1):
        for num in self.triangleindex[n2]:
            tr = self.triangles[num]
            if n1 in tr: # triangle degenere: on degage
                tr.clear()
            else:
                for index,numero in enumerate(tr):
                    if numero == n2:
                        tr[index] = n1
                self.triangleindex[n1].add(num)
        del self.triangleindex[n2]

    def vertexindexer(self):
        """ compte les vecteurs """
        vecteurs = defaultdict(int)
#        triangles_byv = defaultdict(set)
        ordre = lambda x: x if x[0] < x[1] else (x[1], x[0])
        for tr in geom.triangles:
            if not tr:
                continue
            n1, n2, n3 = tr
            e1 = ordre((n1, n2))
            e2 = ordre((n2, n3))
            e3 = ordre((n3, n1)) # les vecteurs
            vecteurs[e1] += 1
            vecteurs[e2] += 1
            vecteurs[e3] += 1



        return vecteurs

    def get_edgelist(self, reinit=False):
        ''' recupere la liste des brins de bord '''
        if not self.edges or reinit:
            vecteurs = self.vertexindexer()
            edges = list((i for i in vecteurs if vecteurs[i] == 1))

            bizarres = list((i for i in vecteurs if vecteurs[i] > 2))

            self.edges = edges
        print('bords trouves',len(edges))
        print('trucs etranges ', len(bizarres))
        return self.edges

    def edge_indexer(self):
        edges = self.get_edgelist()
        liens = defaultdict(set)
        for i in edges:
            p1, p2 = i
            liens[p1].add(p2)
            liens[p2].add(p1)
#        for i in liens:
#            if len(liens[i])!=2:
#                print('probleme de bord',i,len(liens[i]),liens[i])

        return liens


    def edge_follower(self):
        '''suit les bords pour faire des contours'''



    def triangles_degeneres(self):
        print( 'recherche de triangles degeneres')
        nd = 0
        for i in self.triangles:
            tpts = set(i)
#            print('triangle etudie',tpts)

            if tpts and len(tpts)!=3:
                nd+=1
                print('triangle dégénére',tpts)


    def reindex(self):
        self.bbox()
        self.triangleindexer()
        self.npoints = len(self.points)
        self.ntriang = len(self.triangles)


    def merge(self, geom2):
        offset = self.npoints
        self.points.extend(geom2.points)
        for tr in geom2.triangles:
            self.triangles.append(list(i+offset for i in tr))
        self.reindex()

def lire_obj(fichier):
    '''lit des objets a partir d'un fichier obj'''
    dd0 = time.time()
    nom = os.path.splitext(os.path.basename(fichier))[0]
    geom = Geomobj(nom)
    nlignes = 0
    nobj = 0

    prn = 100000
    aff = prn
    npoints = 0
    ntriang = 0
    with open(fichier,"r") as fich:
        for ligne in fich:
            nlignes += 1
            if nlignes == aff:
                print('obj: lignes lues', nlignes, 'objets:', nobj, 'en', int(time.time()-dd0),
                      's (', int(nobj/(time.time()-dd0)), ')o/s')
                aff += prn
            elements = ligne.split(" ")
#            print (" lus", elements)
            if elements[0] == "v":
                npoints += 1
                pt = POINT(*(float(i) for i in elements[1:]))
                geom.points.append(pt)

            elif elements[0] == "f":
                ntriang += 1
                triang = list(int(i.split('/')[0])-1 for i in elements[1:])
                for i in triang:
                    if i > npoints-1:
                        print ('point out of range',triang)
                geom.triangles.append(triang)
    geom.npoints = npoints
    geom.ntriang = ntriang
    print ("lu ",npoints,ntriang,nlignes)
    geom.triangleindexer()
    return geom

def ecrire_obj(geom, fichier):
    '''ecriture d un objet en obj'''
    ptmap = dict()
    with open(fichier,"w") as fich:

        used = geom.getused()
        npt = 0
        ntr = 0
        for i in used:
            npt+=1
            ptmap[i] = npt
#            print("point",i,points[i])
            fich.write("v %f %f %f\n" % tuple(geom.points[i]))
        for tr in geom.triangles:
            if tr:
                ntr += 1
                fich.write("f %d %d %d\n" % tuple((ptmap[j] for j in tr)))
    print ('ecriture finale',npt,ntr)

def limcase_1d(orig, case, casedef, num):
    ''' calcule la limite de la case'''
    casemin = orig[num] +case[num]*casedef[num]
    casemax = casemin + casedef[num]
    return casemin, casemax

def ranger(grille, pt, numero, orig, casedef):
    """range un point dans la grille"""
    pos = tuple(int((pt[i]-orig[i])/casedef[i]) for i in range(3))
    grille[pos].add(numero)

def limcase_3d(geom, grille, orig, casedef, tol):
    a_retenir = set()
    for case in grille:
#        print ('limites',case,len(grille),len(grille[case]))
        limites = []
        for i in range(3):
            limites.append(limcase_1d(orig, case, casedef, i))
        for npt in grille[case]:
            pt = geom.points[npt]
            for i in range(3):
                vmin, vmax = limites[i]
                if vmin > pt[i] or vmax < pt[i]:
                    print(" point mal range", i,vmin,pt[i],vmax, case, limcase_1d(orig, case, casedef, i))
                if abs(pt[i]-vmin) < tol or abs(vmax-pt[i]) < tol:
#                    print ('valeurs', i,vmin,pt[i],vmax)
                    a_retenir.add(npt)
                    break
#        print ('limites2',case,len(grille),len(grille[case]))
    return a_retenir


def clean_liste(geom, pts, tol2):
    detecte = 1
    npb=0
    while detecte:
        detecte = 0
#            print ('traitement ', grille[case])
        for n1, n2 in itertools.combinations(pts, 2):
            p1 = geom.points[n1]
            p2 = geom.points[n2]
            vect = tuple(((p1[i]-p2[i]) for i in range(3)))
            dist2 = sum((vect[i]*vect[i] for i in range(3)))
            if dist2<tol2:
                detecte=1
                pts.discard(n2) # on supprime p2

#                clean_triangles(n2,n1)
                geom.clean_triangles_byindex(n2,n1)
                npb += 1
#                    print ('suppression point ', n2, p2)
                break
    return npb


def cleaner(geom, tol, liste=[]):
    """ nettoie les triangles de taille inferieure a la tolerance"""
    # definition de la grille
    garde = 10*tol

    orig, size = geom.getbbox(garde)
    taille=len(liste) if liste else geom.npoints
    optidecoup = int(M.sqrt(taille/100)+1)
    dx, dy, dz = geom.size
    casesize = (dx+dy)/(2*optidecoup)
    print ('decoupage optimal ', optidecoup, casesize)
    casedef = (dx/optidecoup, dy/optidecoup, dz/optidecoup)
    print ('decoupage reel ', casedef, orig)
    grille = defaultdict(set)
    used = geom.getused()
    npt = 0
    indices = liste if liste else range(geom.npoints)
    for numero in indices:
        if numero in used:
            npt = npt+1
            pt = geom.points[numero]
            ranger(grille, pt, numero, orig, casedef)

    print (npt+1, "points ranges", 'dans ', len(grille), 'cases')
    tol2 = tol*tol
    npb=0
    ncases = 0
    maxp = 0
    for case in grille:
        ncases += 1
        pts = grille[case]
        maxp = max(maxp,len(pts))
        npb += clean_liste(geom, pts, tol2)
        if ncases %1000 == 0:
            print (ncases, 'traitees', npb ,'(',maxp,')')
            maxp = 0

    pts_limites = limcase_3d(geom, grille, orig, casedef, tol)

    print ("problemes detectes:",npb)

    print ('pts_limites trouves ', len(pts_limites))
    return pts_limites

def rec_cleaner(geom, tol):
    ''' nettoyeur iteratif'''
    suite = 1
    residu = []
    garde = 10*tol
    orig, size = geom.getbbox(garde)
    lenp = 0
    while suite:
        residu = cleaner(geom, tol, liste=residu)
        suite = len(residu) > 100 and len(residu) != lenp
        lenp =len(residu)
    npb2 = clean_liste(geom, residu, tol*tol)
    print ("problemes detectes en limite:",npb2)


def traite_boucle(nouveau, pt):
    boucle = list()
    pos = nouveau.index(pt)
    boucle = nouveau[pos:]
    nouveau[:] = nouveau[:pos]
    return boucle






def hole_detector(geom):
    '''detecte des trous'''
    geom.triangles_degeneres()
    edgeindex = geom.edge_indexer()
    print('segments de bord detectes:',len(geom.edges))


def recale(geom, dec, cote):
    orig,taille = geom.getbbox(0)
    refx = orig.x+dec
    refy = orig.y+dec
    endx = refx + cote
    endy = refy + cote
    print (" recalage x", refx)
    geom.decoupe(refx, operator.gt, 0)
    print (" recalage y", refy)
    geom.decoupe(refy, operator.gt, 1)
    print (" recalage x", endx)
    geom.decoupe(endx, operator.lt, 0)
    print (" recalage y", endy)
    geom.decoupe(endy, operator.lt, 1)
#    raise



#    while vbords:
#        print("nombre de bords", len(vbords))
#        courant = vbords.pop()
#        debut, fin_c = courant # on demarre un nouveau bord
#        controle = set(fin_c) # index decontrole pour detecter les croisements
#
#        nouveau = [fin_c]
#
#        while fin_c!=debut:
#
#            suite = bords[fin_c]
#            d_c = fin_c
#            fin_c = suite.pop()
#
#            nouveau.append(fin_c)
#            if (d_c,fin_c) in vbords:
#                vbords.remove((d_c, fin_c))
#            else:
#                vbords.remove((fin_c, fin_c))
#            if fin_c in controle and fin_c != debut:
#                print ("detection boucle")
#                boucle = traite_boucle(nouveau,fin_c)
#                listebords.append(boucle)
#
#            print ('bord en cours', len(nouveau), debut, fin_c)
#        print(' detecte bord', nouveau, len(nouveau))



#points = []
#triangles = []
#triangleindex = defaultdict(set)

t1= time.time()
liste_a_lire = sys.argv[1].split(",")
fich1 = liste_a_lire[0]

geom = lire_obj(fich1)
recale(geom, 1.5, 100)
recale(geom, 20, 50)
for fich in liste_a_lire[1:]:
    g2 = lire_obj(fich)
    geom.merge(g2)
tol = float(sys.argv[3])
t2=time.time()
rec_cleaner(geom, tol/2)
rec_cleaner(geom, tol)
#rec_cleaner(geom, tol)

t3=time.time()
hole_detector(geom)
ecrire_obj(geom, sys.argv[2])
print ("temps de traitement %.1f s"% (time.time()-t1,))
print ("lecture %.1f s"% (t2-t1,))
print ("nettoyage %.1f s"% (t3-t2,))
print ("ecriture %.1f s"% (time.time()-t3,))
#