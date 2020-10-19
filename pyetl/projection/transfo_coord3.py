# -*- coding: utf-8 -*-
"""gestion des reprojections"""
import math as M
from . import defgrille3 as G


# sens=1  # Systeme local --> systeme global (WGS84, RGF93)
# sens=2  # Systeme global (WGS84, RGF93) --> systeme local

TOLDEF = 0.00000000001
PI = M.pi

# Ys,Lambda c,n,c,e=excentricite,1/2 grand axe,Xs
CONSTANTES = {
    "CC48": (
        12952888.0864,
        0.0523598775598299,
        0.743166306071,
        11676255.9949,
        0.081819191,
        6378137,
        1700000,
    ),
    "CC49": (
        13754395.7452,
        0.0523598775598299,
        0.754731385179,
        11626445.9012,
        0.081819191,
        6378137,
        1700000,
    ),
    "L1": (
        5657616.674,
        0.0407923443319766,
        0.7604059656,
        11603796.98,
        0.08248325676,
        6378249.2,
        600000,
    ),
    "L2": (
        6199695.768,
        0.0407923443319766,
        0.7289686274,
        11745793.39,
        0.08248325676,
        6378249.2,
        600000,
    ),
    "L93": (
        12655612.05,
        0.0523598775598299,
        0.725607765,
        11754255.426,
        0.081819191,
        6378137,
        700000,
    ),
    "LL": (0, 0, 0, 0, 0, 0, 0),
}

GRILLE_IGN = "gr3df97a.csv"


class Projection(object):
    """definition des correspondances entre 2 systemes de coordonnees"""

    def __init__(self, repertoire, liste, proj1, proj2, sens):

        self.sens = sens
        # self.grilles.ecrire_liste(repertoire+"_C",liste) # on ecrit les grilles coherentes
        try:
            self.proj1 = CONSTANTES[proj1]  # constantes de projection
            self.proj2 = CONSTANTES[proj2]
        except KeyError:
            print("projection non géreé")
            self.valide = 0
            raise
        _, _, _, _, self.ex1, self.ga1, _ = self.proj1
        _, _, _, _, self.ex2, self.ga2, _ = self.proj2

        self.recalcul = 0
        self.oxign = 55  # decalage d'origine pour commencer en 0,0
        self.oyign = -410
        self.grilles_ign = dict()
        self.x_cour = 0
        self.y_cour = 0
        self.grille_courante = "Nogrille"
        if sens:
            self.grilles = G.ListeGrilles(repertoire, liste, sens)
            inc = self.grilles.controle_coherence(1)
            while inc:
                inc = self.grilles.controle_coherence(1)

        if "CC" in proj1 or "CC" in proj2:
            for i in open(
                repertoire + "/" + GRILLE_IGN, "r"
            ):  # chargement de la grille IGN
                vals = i.split(";")
                self.grilles_ign[
                    (
                        int(float(vals[0]) * 10 + self.oxign + 0.5),
                        int(float(vals[1]) * 10 + self.oyign + 0.5),
                    )
                ] = (float(vals[2]), float(vals[3]), float(vals[4]))
            self.optimise_grilleign()

        self.from_proj = (
            self.from_lamb_cus if proj1 == "L1" and sens == 1 else self.en_geo
        )
        if proj1 == "LL":
            self.from_proj = self.torad

        self.grille_ign = None
        if proj1 in ("L1", "L2") and proj2 in ("CC48", "CC49"):
            self.grille_ign = self.lamb_to_cc_grille_ign
            self.grille_ign_inv = self.cc_to_lamb_grille_ign
        elif proj1 in ("CC48", "CC49") and proj2 in ("L1", "L2"):
            self.grille_ign = self.cc_to_lamb_grille_ign
        else:
            self.grille_ign = None

        self.to_proj = self.to_lamb_cus if proj2 == "L1" and sens == 2 else self.geo_EN
        if proj2 == "LL":
            self.to_proj = self.todeg

        self.description = (
            proj1
            + "->"
            + proj2
            + " sens grille cus: "
            + str(sens)
            # + "\n"
            # + str(self.from_proj)
            # + "\n-> "
            # + str(self.to_proj)
            + " grille ign "
            + str(self.grille_ign)
        )

        self.valide = 1

    def torad(self, x_cour, y_cour, tol):
        return x_cour * PI / 180, y_cour * PI / 180

    def todeg(self, lam, phi):
        return (lam * 180 / PI, phi * 180 / PI)

    def calcule_point_proj(self, x_cour, y_cour, tol=TOLDEF):
        """ calcul de reprojection d'un point """
        lam, phi = self.from_proj(x_cour, y_cour, tol)
        # if self.from_proj
        # else (x_cour * PI / 180, y_cour * PI / 180)

        #        print ('coord initiales', x, y, self.grille_courante, self.sens)
        #        print ('coord geo      ', lam, phi)
        if self.grille_ign:
            self.x_cour = x_cour
            self.y_cour = y_cour
            lam1, phi1 = self.grille_ign(lam, phi)
        #            lam2, phi2 = self.grille_ign_inv(lam, phi)
        else:
            lam1, phi1 = lam, phi

        #        print ('apr grille ign ',lam1,phi1)
        (x_proj, y_proj) = self.to_proj(lam1, phi1)
        #        print ('coord finales  ',X, Y , self.grille_courante, self.sens)
        #        raise
        return self.grille_courante, x_proj, y_proj

    def calcule_point_grille_cus(self, xinit, yinit):
        """Transformation de coordonnées en utilisant une grille locale"""
        if self.sens == 0:
            self.grille_courante = "nogrille"
            return xinit, yinit
        ecart_x, ecart_y, nom = self.grilles.recup_corrections(xinit, yinit)
        self.grille_courante = nom
        if self.sens == 1:
            return xinit - ecart_x, yinit - ecart_y
        return xinit + ecart_x, yinit + ecart_y

    def inv_liso(self, liso, exc, tol):
        """inversion de la latitude isométrique"""
        phi1 = 2 * M.atan(M.exp(liso)) - PI / 2
        phi0 = 9999
        expliso = M.exp(liso)
        while abs(phi1 - phi0) >= tol:
            phi0 = phi1
            phi1 = (
                2
                * M.atan(
                    pow(((1 + exc * M.sin(phi0)) / (1 - exc * M.sin(phi0))), (exc / 2))
                    * expliso
                )
                - PI / 2
            )
        #            print ('calcul',p)
        return phi1  # RETOUR : latitude isométrique

    def en_geo(self, x_en, y_en, tol):
        """passage de coordonnées planes à géographiques"""
        yn0, lc, n, c, exc, _, xn0 = self.proj1
        R = M.sqrt((x_en - xn0) ** 2 + (y_en - yn0) ** 2)
        ga = M.atan((x_en - xn0) / (yn0 - y_en))
        lam = lc + ga / n
        liso = -M.log(abs(R / c)) / n
        phi = self.inv_liso(liso, exc, tol)
        return lam, phi  # RETOUR : coordonnées géographiques (radian)

    def geo_EN(self, lam, phi):
        """passage de coordonnées géographiques à planes"""
        yn, lc, n, c, exc, _, xn = self.proj2
        liso = M.log(
            M.tan(PI / 4 + phi / 2)
            * pow((1 - exc * M.sin(phi)) / (1 + exc * M.sin(phi)), exc / 2)
        )
        X = xn + c * M.exp(-n * liso) * M.sin(n * (lam - lc))
        Y = yn - c * M.exp(-n * liso) * M.cos(n * (lam - lc))
        #        print ('dans geo_en',X,Y)
        return X, Y  # RETOUR : coordonnées planes (m)

    def geo_xyz(self, lam, phi, hel, gra, exc):
        """passage de coordonnées géographiques à cartésiennes géocentriques"""
        n_interm = gra / M.sqrt(1 - (exc * exc) * pow(M.sin(phi), 2))
        x_cart = (n_interm + hel) * M.cos(phi) * M.cos(lam)
        y_cart = (n_interm + hel) * M.cos(phi) * M.sin(lam)
        z_cart = (n_interm * (1 - exc * exc) + hel) * M.sin(phi)
        return x_cart, y_cart, z_cart
        # RETOUR : coordonnées artésiennes géocentriques (m)

    def xyz_geo(self, x_ca, y_ca, z_ca, v_a, exc, tol):
        """passage de coordonnées cartésiennes géocentriques à géographiques"""
        lam = M.atan(y_ca / x_ca)
        dist = M.sqrt(x_ca * x_ca + y_ca * y_ca)
        exc2 = exc * exc
        phi1 = M.atan(
            z_ca
            / (
                dist
                * (1 - ((v_a * exc2) / M.sqrt(x_ca * x_ca + y_ca * y_ca + z_ca * z_ca)))
            )
        )
        phi = 999999
        #        print ('calcul', phi1,phi,abs(phi1-phi)<tol)
        while abs(phi1 - phi) >= tol:
            phi = phi1
            phi1 = M.atan(
                z_ca
                / dist
                * pow(
                    1
                    - (v_a * (exc2) * M.cos(phi))
                    / (dist * M.sqrt(1 - exc2 * M.sin(phi) ** 2)),
                    -1,
                )
            )
        return lam, phi1  # RETOUR : coordonnées géographiques (radian)

    def optimise_grilleign(self):
        """ indexe la grille ign pour un acces plus rapide"""
        self.grilles_ign_opt = dict()
        for noeud in self.grilles_ign:
            codelamSO, codephiSO = noeud

            codelamNO = codelamSO
            codelamNE = codelamNO + 1
            codelamSE = codelamNE

            codephiSE = codephiSO
            codephiNO = codephiSO + 1
            codephiNE = codephiNO

            try:
                xNO, yNO, zNO = self.grilles_ign[(codelamNO, codephiNO)]
                xSE, ySE, zSE = self.grilles_ign[(codelamSE, codephiSE)]
                xSO, ySO, zSO = self.grilles_ign[(codelamSO, codephiSO)]
                xNE, yNE, zNE = self.grilles_ign[(codelamNE, codephiNE)]
            except KeyError:
                continue
            self.grilles_ign_opt[noeud] = (
                xNO,
                yNO,
                zNO,
                xSE,
                ySE,
                zSE,
                xSO,
                ySO,
                zSO,
                xNE,
                yNE,
                zNE,
            )

    # PROG : changement de système de coordonnées avec la grille IGN
    def calcule_point_grille_ign(self, x_orig, y_orig, z_orig, lam_r, phi_r):
        """ calcule un point par la grille ign"""
        # passage en degré (on travaille en x 10 comme cela la maille vaut 1)
        lam = lam_r * 1800 / PI
        phi = phi_r * 1800 / PI

        codelam_so = int(lam) + self.oxign  # determination de la maille
        codephi_so = int(phi) + self.oyign

        try:
            x_no, y_no, z_no, x_se, y_se, z_se, x_so, y_so, z_so, x_ne, y_ne, z_ne = self.grilles_ign_opt[
                codelam_so, codephi_so
            ]
            # position relative dans la maille (on travaille en x 10 comme cela la maille vaut 1)
            xint = lam + self.oxign - codelam_so
            yint = phi + self.oyign - codephi_so
            # interpolation bilineaire
            x_grid = (
                (1 - xint) * (1 - yint) * x_so
                + (1 - xint) * yint * x_no
                + xint * (1 - yint) * x_se
                + xint * yint * x_ne
            )
            y_grid = (
                (1 - xint) * (1 - yint) * y_so
                + (1 - xint) * yint * y_no
                + xint * (1 - yint) * y_se
                + xint * yint * y_ne
            )
            z_grid = (
                (1 - xint) * (1 - yint) * z_so
                + (1 - xint) * yint * z_no
                + xint * (1 - yint) * z_se
                + xint * yint * z_ne
            )

        except KeyError:
            print("...............point hors grille IGN", self.x_cour, self.y_cour)
            return x_orig, y_orig, z_orig

        if self.sens == 1:
            return x_orig + x_grid, y_orig + y_grid, z_orig + z_grid
        return x_orig - x_grid, y_orig - y_grid, z_orig - z_grid

    def from_lamb_cus(self, x_cus, y_cus, tol=TOLDEF):
        """part de coordonnees lambert et va vers des coordonnees _geo """
        #       transformation locale (grille CUS)
        x_lam, y_lam = self.calcule_point_grille_cus(x_cus, y_cus)
        #        print ('grille_cus', xg, yg)
        return self.en_geo(x_lam, y_lam, tol)

    def to_lamb_cus(self, lam, phi):
        """ on va vers des coordonnees lamb CUS """
        x_lam, y_lam = self.geo_EN(lam, phi)
        return self.calcule_point_grille_cus(
            x_lam, y_lam
        )  # transformation locale (grille CUS)

    def lamb_to_cc_grille_ign(self, lam_r, phi_r, tol=TOLDEF):
        """applique la grille de correction IGN dans le sens L->C"""
        haut_elips = 0
        # passage en coordonnées cartésiennes
        x_cart, y_cart, z_cart = self.geo_xyz(
            lam_r, phi_r, haut_elips, self.ga1, self.ex1
        )
        x_trans = x_cart - 168  # transformation approchée NTF->RGF93
        y_trans = y_cart - 60
        z_trans = z_cart + 320
        # calcul des coordonnées géographiques approchées dans le nouveau système
        lamt, phit = self.xyz_geo(x_trans, y_trans, z_trans, self.ga2, self.ex2, tol)
        x_trans, y_trans, z_trans = self.calcule_point_grille_ign(
            x_cart, y_cart, z_cart, lamt, phit
        )
        # passage en coordonnées géographiques précises dans le nouveau système
        return self.xyz_geo(x_trans, y_trans, z_trans, self.ga2, self.ex2, tol)

    def cc_to_lamb_grille_ign(self, lam_r, phi_r, tol=TOLDEF):
        """applique la grille de correction IGN dans le sens C->L"""
        haut_elips = 0
        # passage en coordonnées cartésiennes
        x_cart, y_cart, z_cart = self.geo_xyz(
            lam_r, phi_r, haut_elips, self.ga1, self.ex1
        )
        #  calcul des coordonnées cartésienne précises dans le nouveau système (grille IGN)
        x_grid, y_grid, z_grid = self.calcule_point_grille_ign(
            x_cart, y_cart, z_cart, lam_r, phi_r
        )
        # passage en coordonnées géographiques
        return self.xyz_geo(x_grid, y_grid, z_grid, self.ga2, self.ex2, tol)


def param(v_a, ext, _, p_0, p_1, p_2):
    """détermination des paramètres dérivés de projection à partir des paramètres publics"""
    n_1 = v_a / M.sqrt(1 - ext ** 2 * M.sin(p_1) ** 2)
    n_2 = v_a / M.sqrt(1 - ext ** 2 * M.sin(p_2) ** 2)
    liso1 = M.log(
        M.tan(PI / 4 + p_1 / 2)
        * pow((1 - ext * M.sin(p_1)) / (1 + ext * M.sin(p_1)), ext / 2)
    )
    liso2 = M.log(
        M.tan(PI / 4 + p_2 / 2)
        * pow((1 - ext * M.sin(p_2)) / (1 + ext * M.sin(p_2)), ext / 2)
    )
    liso0 = M.log(
        M.tan(PI / 4 + p_0 / 2)
        * pow((1 - ext * M.sin(p_0)) / (1 + ext * M.sin(p_0)), ext / 2)
    )
    param_pn = M.log((n_2 * M.cos(p_2)) / (n_1 * M.cos(p_1))) / (liso1 - liso2)
    print("tc3:param pn ", param_pn)
    param_pc = (n_1 * M.cos(p_1)) / param_pn * M.exp(param_pn * liso1)
    print("tc3:param pc ", param_pc)
    param_ys = 8200000 + param_pc * M.exp(-param_pn * liso0)
    print("tc3:param ys ", param_ys)
