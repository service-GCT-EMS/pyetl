# -*- coding: utf-8 -*-
""" definition interne des objets
attributs et geometrie """

import math as Ma
import itertools
import logging

LOGGER = logging.getLogger("__name__")


def points_egaux(point1, point2, dim):
    """teste l'egalite de deux points"""

    for i in range(dim):
        if point1[i] != point2[i]:
            return False
    return True


def cercle_3pts(pt1, pt2, pt3):
    """calcule le centre et le rayon d'un cercle par 3 points """
    cx1, cy1 = pt1[0:2]
    cx2, cy2 = pt2[0:2]
    cx3, cy3 = pt3[0:2]

    if cx1 == cx2 or cy1 == cy2:
        cx2, cy2, cx3, cy3 = cx3, cy3, cx2, cy2
    if cx2 == cx3:
        cx1, cy1, cx2, cy2 = cx2, cy2, cx1, cy1

    vma = (cy2 - cy1) / (cx2 - cx1) if cx1 != cx2 else 1e6
    vmb = (cy3 - cy2) / (cx3 - cx2) if cx2 != cx3 else 1e6
    if vma == vmb:
        print("error: compos: erreur cercle ", cx1, cy1, cx2, cy2, cx3, cy3)
        raise ValueError("cercle degenere")
    xctr = (vma * vmb * (cy1 - cy3) + vmb * (cx1 + cx2) - vma * (cx2 + cx3)) / (
        2 * (vmb - vma)
    )
    yctr = (
        -(xctr - (cx1 + cx2) / 2) / vma + (cy1 + cy2) / 2
        if vma != 0
        else -(xctr - (cx2 + cx3) / 2) / vmb + (cy2 + cy3) / 2
    )

    rayon = Ma.sqrt((xctr - cx1) * (xctr - cx1) + (yctr - cy1) * (yctr - cy1))
    pcentre = [xctr, yctr]
    return pcentre, rayon

def discretise(pt1, pt2, pt3,ang=30,tol=0.05):
    """discretise un arc en fonction d'une tolerance anguraire et de cord a arc"""
    angrad=Ma.pi*ang/180
    pcentre,r=cercle_3pts(pt1, pt2, pt3)
    xc,yc=pcentre
    xd,yd=pt1
    xf,yf=pt3
    tolrad=Ma.sqrt(1-((r-tol)/tol)**2)
    angletol=min(abs(tolrad),abs(angrad))
    ad=Ma.acos((xd-xc)/r)
    af=Ma.acos((xf-xc)/r)
    pas=Ma.copysign(angletol,(af-ad))
    coordlist=[(xc+r*Ma.cos(i),yc+r*Ma.sin(i)) for i in range(ad,af,pas)]+[pt3]
    return coordlist

class Section(object):
    """# definition d'une section
    - la section est l'element fondamental d une geometrie"""

    __slots__ = ["coords", "couleur", "courbe", "aire", "dimension", "encours"]

    def __init__(self, pnt, dim):
        if pnt:
            self.coords = [list(pnt)]
        else:
            self.coords = list()
        self.couleur = "1"
        self.courbe = 0
        self.aire = 0
        self.dimension = dim
        #        self.ferme = False
        self.encours = True

    @property
    def dpt(self):
        return self.coords[-1] if self.coords else None

    @property
    def ppt(self):
        return self.coords[0] if self.coords else None

    @property
    def npt(self):
        return len(self.coords)

    @property
    def ferme(self):
        return (
            True
            if self.courbe == 3
            else self.coords[0] == self.coords[-1]
            if self.coords
            else False
        )

    @property
    def __list_if__(self):
        dim = self.dimension
        return ",".join([" ".join([str(j) for j in i[:dim]]) for i in self.coords])

    def dupplique(self):
        """retourne un double """
        double = Section(None, self.dimension)
        double.couleur = self.couleur
        double.courbe = self.courbe
        double.aire = self.aire
        double.encours = self.encours
        double.coords = [i[:] for i in self.coords]
        return double

    def addpoint(self, pnt):
        """ajoute un point"""
        if self.coords and self.coords[-1] == pnt:  # on evite les points doubles
            print("detecte point_double", pnt)
            return
        self.coords.append(list(pnt))

    #        print ('coords',pnt,self.coords)

    def addpoints(self, liste):
        """ajoute une liste de points"""
        self.coords.extend([list(i) for i in liste])

    def setsect(self, liste, couleur, courbe):
        """ajoute une liste de points"""
        self.coords = [list(i) for i in liste]
        self.encours = False
        self.courbe = courbe
        # if courbe==3: raise
        self.couleur = couleur

    def fusion(self, sect):
        """fusionne 2 sections si possible"""
        if self.coords[-1] == sect.coords[0]:
            self.coords.extend(sect.coords[1:])
        else:
            self.coords.extend(sect.coords[:])

    def inverse(self):
        """inverse le sens d'une section"""
        self.coords.reverse()

    def finalise(self, couleur, courbe):
        """finalise une section et calcule certains parametres"""
        self.encours = False
        self.courbe = courbe
        self.couleur = couleur
        npt = self.npt
        if npt == 0:
            return False
        if courbe and (npt < 3 or npt % 2 == 0):
            print("error: compos: courbe invalide", self.dpt, self.npt)
            self.courbe = 0
        #        self.ferme = self.dpt == self.ppt
        return True

    def conversion_diametre(self):
        """modifie la description d'un cercle centre rayon vers 3pts"""
        if self.courbe == 3:  # definition d'un cercle il faut modifier les points
            centre, rayon = cercle_3pts(self.coords[0], self.coords[1], self.coords[2])
            self.aire = Ma.pi * rayon ** 2
            if self.aire_orient() < 0:
                self.aire = -self.aire
            ccx, ccy = centre
            px1, py1 = ccx, ccy - rayon
            px2, py2 = ccx, ccy + rayon
            ccz = (
                (self.coords[0][2] + self.coords[1][2] + self.coords[2][2]) / 3
                if self.dimension == 3
                else 0
            )
            self.coords = [[px1, py1, ccz], [px2, py2, ccz], [px1, py1, ccz]]
        #            self.ferme = True
        return self

    def set_2d(self):
        """ cache le Z """
        self.dimension = 2

    def set_3d(self):
        """ montre le Z """
        self.dimension = 3

    @property
    def longueur(self):
        """ calcule la longueur : attention faux pour les courbes"""
        long = 0
        coords = self.coords
        #        print("calcul longueur",coords)
        if len(coords) > 1:
            if self.dimension == 3:
                xpr, ypr, zpr = coords[0][:3]
                for pnt in coords[1:]:
                    xcour, ycour, zcour = pnt[:3]
                    long += Ma.sqrt(
                        ((xpr - xcour)) ** 2
                        + ((ypr - ycour)) ** 2
                        + ((zpr - zcour)) ** 2
                    )
                    #                print("calcul",pnt,long)
                    xpr, ypr, zpr = xcour, ycour, zcour
                return long
            xpr, ypr = coords[0][:2]
            for pnt in coords[1:]:
                xcour, ycour = pnt[:2]
                long += Ma.sqrt(((xpr - xcour)) ** 2 + ((ypr - ycour)) ** 2)
                #                print("calcul",pnt,long)
                xpr, ypr = xcour, ycour
        #        raise
        return long

    def convert(self, fonction):
        """applique une fonction aux coordonnees"""
        self.coords = list(map(fonction, self.coords))

    def aire_orient(self):
        """calcule l'aire (positive ou negative selon l'orientation)
        : attention faux pour les courbes"""
        aire = 0
        ncoord = len(self.coords)
        ppt = self.ppt
        # aire = sum([(self.coords[(i + 1)][0] - self.coords[i][0]) * (self.coords[(i + 1)][1] + self.coords[i][1] - 2 * ppt[1]) for i in range(ncoord-1)])+\
        #             (ppt[0] - self.coords[ncoord][0]) * (self.coords[ncoord][1] - ppt[1])
        for i in range(ncoord):
            aire += (
                (self.coords[(i + 1) % ncoord][0] - self.coords[i][0])
                * (
                    self.coords[(i + 1) % ncoord][1]
                    + self.coords[i][1]
                    - 2 * self.ppt[1]
                )
                / 2
            )
        return aire

    def print_debug(self):
        """affichage debug"""
        print("debug: compos: geom->section ", len(self.coords), self.coords)


class Ligne(object):
    """definition d'une ligne"""

    __slots__ = [
        "sections",
        "termine",
        "interieur",
        "err",
        "point_double",
        "aire",
        "dimension",
        "courbe",
        "type",
    ]

    def __init__(self, sect, interieur=False):
        self.sections = [sect.dupplique()]
        self.termine = False
        self.interieur = interieur
        self.err = ""
        self.point_double = False
        self.aire = 0
        self.dimension = sect.dimension
        self.courbe = sect.courbe
        self.type = "2"

    @property
    def dpt(self):
        return self.sections[-1].dpt

    @property
    def ppt(self):
        return self.sections[0].ppt

    @property
    def npt(self):
        return sum([i.npt for i in self.sections])

    @property
    def ferme(self):
        try:
            return (
                True
                if len(self.sections) == 1 and self.sections[0].courbe == 3
                else self.sections[0].coords[0] == self.sections[-1].coords[-1]
            )
        except:
            print("erreur geometrie")
            return False

    def addpoint(self, pnt, dim):
        """on ajoute un point a une ligne"""
        #        print ('addpoint_ligne')
        if self.termine:
            return pnt  # pas possible la ligne est fermee
        sc = self.sections[-1]
        if sc.encours:
            sc.addpoint(pnt)
            return 0
        if self.dpt == pnt:
            sect = Section(pnt, dim)
            self.sections.append(sect)
            return 0
        self.termine = True
        return pnt

    def force_fermeture(self):
        """force la fermeture d'une ligne"""
        if self.ferme:
            return True
        if self.npt < 3:
            return False
        sc = self.sections[-1]
        sc.coords.append(self.ppt)
        return True

    def ajout_section(self, sect):
        """on ajoute une section a la ligne courante """
        if self.dpt != sect.ppt or self.termine:
            self.termine = True
            # print ('fin ligne ',self.dpt != sect.ppt , sect.ferme , self.termine , self.ferme)
            return sect
        if sect.ferme or self.ferme:  # geometrie malsaine pour un polygone
            self.point_double = True
            self.termine = True
            return sect
        self.sections.append(sect.dupplique())
        self.courbe = sect.courbe or self.courbe
        return 0

    def ajout_ligne(self, ligne, desordre=False):
        """fusionne 2 ligne en les inversant si necessaire"""
        if self.ferme or ligne.ferme:
            return False
        if desordre and self.dpt == ligne.dpt:  # on inverse si necessaire
            ligne.inverse()
        if (
            self.dpt == ligne.ppt
        ):  # cas simple on ajoute les sections sans se poser de questions
            self.termine = False
            for sect in ligne.sections:
                if self.ajout_section(sect):
                    print("erreur ajout", sect.coords)
            return True
        return False

    def fin_section(self, couleur, courbe):
        """ finalise la geometrie d'une section """
        sc = self.sections[-1]
        sc.finalise(couleur, courbe)
        self.termine = True
        if courbe == 3:  # cas particulier du cercle
            if (
                len(self.sections) > 1
            ):  # il y a deja des sections il faut une nouvelle ligne
                return self.sections.pop()
        self.courbe = sc.courbe or self.courbe

    def annule_section(self):
        if len(self.sections) < 2:
            return 1
        self.sections.pop()
        return 0

    def inverse(self):
        """inverse le sens d'une ligne"""
        self.sections.reverse()
        for i in self.sections:
            i.inverse()

    def set_2d(self):
        """cache le z pour la ligne"""
        self.dimension = 2
        for i in self.sections:
            i.set_2d()

    def set_3d(self):
        """ouvre le z pour la ligne"""
        self.dimension = 3
        for i in self.sections:
            i.set_3d()

    def prolonge(self, long, mode=3):
        """ prolonge une geometrie d'une certaine longueur"""
        if long == 0:
            return
        if mode % 2 == 1:
            self.prolonge_debut(long)
        if mode > 1:
            self.prolonge_fin(long)

    def prolonge_debut(self, long):
        """prolonge le debut d'une ligne"""
        #        print ("prolonge_debut_ligne",long,list(self.coords))
        if self.sections[0].courbe:  # on commence par un arc
            pt1, pt2, pt3 = self.sections[0].coords[:3]
            centre, rayon = cercle_3pts(pt1, pt2, pt3)
            dx1, dy1 = pt1[0] - centre[0], pt1[1] - centre[1]
            facteur = long / rayon
            dx2, dy2 = dy1 * facteur, dx1 * facteur
            pt_supp = [pt1[0] + dx2, pt1[1] + dy2, pt1[2]]
            nouv_sect = Section(pt_supp, self.dimension)
            nouv_sect.addpoint(pt_supp)
            self.sections.insert(0, nouv_sect)
        else:
            pt1, pt2 = self.sections[0].coords[:2]
            dx1, dy1, dz1 = pt1[0] - pt2[0], pt1[1] - pt2[1], pt1[2] - pt2[2]
            if dx1 == 0 and dy1 == 0 and dz1 == 0:
                facteur = 1
            else:
                facteur = long / Ma.sqrt(dx1 * dx1 + dy1 * dy1 + dz1 * dz1)
            dx2, dy2, dz2 = dx1 * facteur, dy1 * facteur, dz1 * facteur
            pt_supp = [pt1[0] + dx2, pt1[1] + dy2, pt1[2] + dz2]
            self.sections[0].coords.insert(0, pt_supp)

    #        print("apres prolonge", list(self.coords))

    def prolonge_fin(self, long):
        """prolonge la fin d'une ligne"""
        if self.sections[-1].courbe:  # on finit par un arc
            pt1, pt2, pt3 = self.sections[-1].coords[-3:]
            centre, rayon = cercle_3pts(pt1, pt2, pt3)
            dx1, dy1 = pt3[0] - centre[0], pt3[1] - centre[1]
            facteur = long / rayon
            dx2, dy2 = dy1 * facteur, dx1 * facteur
            pt_supp = [pt3[0] - dx2, pt3[1] - dy2]
            if self.dimension == 3:
                pt_supp.append(pt3[2])
            nouv_sect = Section(pt3, self.dimension)
            nouv_sect.addpoint(pt_supp)
            self.sections.append(nouv_sect)
        else:
            pt1, pt2 = self.sections[-1].coords[-2:]
            dx1, dy1 = pt1[0] - pt2[0], pt1[1] - pt2[1]
            if dx1 == 0 and dy1 == 0:
                facteur = 1
            else:
                facteur = long / Ma.sqrt(dx1 * dx1 + dy1 * dy1)
            dx2, dy2 = dx1 * facteur, dy1 * facteur
            pt_supp = [pt2[0] - dx2, pt2[1] - dy2, pt2[2]]
            self.sections[-1].addpoint(pt_supp)

    @property
    def longueur(self):
        """calcul de la longueur"""
        # self.l = 0
        long = sum([i.longueur for i in self.sections if i])
        #        for i in self.sections:
        #            self.l+ = i.longueur()
        return long

    @property
    def coords(self):
        """iterateur sur les coordonnees"""
        return itertools.chain(*[i.coords for i in self.sections])

    def sdef(self):
        """retourne un descriptif des sections"""
        return ((len(i), i.courbe) for i in self.sections)

    def convert(self, fonction):
        #        print("ligne avant conv",list(self.coords))

        for i in self.sections:
            i.convert(fonction)

    #        print("ligne apres conv",list(self.coords))

    def aire_orientee(self):
        """calcule une aire avec un signe selon le sens de rotation"""
        if self.aire == 0:
            if self.ferme:
                aire = 0
                if self.npt < 3:
                    if self.npt:
                        LOGGER.error("geometrie 3 points minimum pour une boucle")
                    # print(
                    #     "error: compos: erreur geometrique 3 points minimum pour une boucle",
                    #     [i for i in self.coords],
                    # )
                    return 0
                itc = self.coords

                cxa, cya = next(itc)[0:2]
                cxb, cyb = next(itc)[0:2]
                cxb, cyb = cxb - cxa, cyb - cya
                for i in itc:
                    cxc, cyc = i[0:2]
                    cxc, cyc = cxc - cxa, cyc - cya
                    aire += cxb * cyc - cxc * cyb
                    cxb, cyb = cxc, cyc
                self.aire = aire / 2
        return self.aire

    def print_debug(self):
        """affichage debug"""
        print("debug: compos: geom->ligne ", self, len(self.sections))
        for i in self.sections:
            i.print_debug()


class Polygone(object):
    """definition d'un polygone eventuellement a trous"""

    __slots__ = ["lignes", "dimension", "courbe"]

    def __init__(self, lig):
        self.lignes = [lig]
        self.dimension = lig.dimension
        self.courbe = lig.courbe

    def ajout_contour(self, lig):
        """on ajoute un anneau ou un trou """
        self.lignes.append(lig)
        if lig.courbe:
            self.courbe = True

    def aire(self):
        if not self.lignes:
            return 0
        base = abs(self.lignes[0].aire_orientee())
        if len(self.lignes) > 1:
            base -= sum((abs(i.aire_orientee()) for i in self.lignes[1:]))
        return base
