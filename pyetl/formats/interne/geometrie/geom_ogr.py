# -*- coding: utf-8 -*-
""" definition interne des objets
attributs et geometrie """

import itertools

# from . import composants as C
from shapely import geometry as SG
from shapely import prepared as P
from osgeo import ogr, osr, gdal


class Geometrie(object):
    """classe de base de stockage de la geometrie d'un objet"""

    TYPES_G = {
        "0": "ALPHA",
        "1": "POINT",
        "2": "LIGNE",
        "3": "SURFACE",
        "-1": "GEOMETRIE",
        "4": "TIN",
        "5": "POLYHEDRAL",
        "indef": "ALPHA",
    }
    STYPES = {
        "Point": "1",
        "MultiPoint": "1",
        "LineString": "2",
        "LinearRing": "2",
        "MultiLineString": "2",
        "Polygon": "3",
        "MultiPolygon": '3"',
    }
    __slots__ = [
        "geom",
        "polygones",
        "ligne",
        "points",
        "type",
        "null",
        "valide",
        "courbe",
        "angle",
        "sgeom",
        "sgp",
        "longueur_point",
        "dim",
        "multi",
        "srid",
        "force_multi",
        "erreurs",
    ]

    def __init__(self):
        self.geom = ogr.Geometry()
        self.points = []
        self.ligne = None
        self.section = None
        self.type = "indef"  # type de geometrie
        self.null = True  # geometrie nulle
        self.valide = False
        self.courbe = False
        self.longueur_point = 0
        self.dim = 0
        self.multi = False
        self.srid = "3948"
        self.force_multi = False
        self.angle = 0
        self.sgeom = None
        self.sgp = None
        # self.epsg = 'SRID=3948;'
        self.erreurs = Erreurs()

    @property
    def epsg(self):
        """ retourne la projection sous forme d'une chaine SRID"""
        return "SRID=" + self.srid + ";"

    def setsrid(self, srid):
        """positionne le code EPSG"""
        if srid:
            self.srid = str(int(srid))

    # ------------------------------------informations----------------------------------------------

    @property
    def dimension(self):
        if self.geom.IsEmpty():
            return 0
        return 3 if self.geom.is3D() else 2

    @property
    def type_geom(self):
        if self.sgeom:
            type_geom = self.sgeom.geom_type
            return self.STYPES[type_geom]
        return self.type

    @property
    def npt(self):
        """ retourne le nombre de points en eliminant les points doubles entre sections"""
        return 0 if self.geom is None else self.geom.GetPointCount()

    @property
    def ferme(self):
        """ retourne True si la geometrie est fermee"""
        return self.geom.IsRing()

    @property
    def longueur(self):
        """longueur de la geometrie"""
        return self.longueur_point if self.longueur_point else self.geom.Length()

    @property
    def area(self):
        return self.geom.Area()

    def setsgeom(self, shape=None):
        """positionne l'element shapely"""
        if shape:
            self.sgeom = shape
            self.valide = False
        else:
            self.sgeom = SG.shape(self)

    def setpoint(self, coordlist, angle=None, dim=2, longueur=0, srid="3948"):
        """cree une geometrie de point"""
        self.type = "1"
        self.null = False
        self.multi = False
        self.srid = str(int(srid))
        self.valide = True
        self.sgeom = None
        self.dim = dim
        self.angle = angle
        self.sgeom = None
        if coordlist is None:
            self.null = True
        else:
            points = list(coordlist)
            if len(points) == 1:
                self.geom = ogr.Geometry(ogr.wkbPoint)
                self.geom.addpoint(*(points[0][:dim]))
            else:
                self.geom = ogr.Geometry(ogr.wkbMultiPoint)
                for p in points:
                    self.geom.addpoint(*p[:dim])
            self.longueur_point = longueur

    #       print ('creation point ',coords, self.point.coords)

    def addpoint(self, coordlist, dim):
        """ajoute un point a une geometrie"""
        self.shapesync()
        if self.type == "1":
            if coordlist is None:
                self.null = True
                return
            self.points.append(list(coordlist[:dim]))
            self.multi = len(self.points) > 1
            self.dim = dim
            # raise
            return

        if self.lignes:
            ligne_active = self.lignes[-1]
            if ligne_active.addpoint(coordlist, dim):
                # la ligne est fermee
                self.nouvelle_ligne_p(coordlist, dim)
                # on ajoute un point a une nouvelle ligne
        else:
            self.lignes = [C.Ligne(C.Section(coordlist, dim))]
        self.sgeom = None
        if coordlist is None:
            return
        if self.type == "1":
            if not self.multi:
                self.geom = ogr.ForceToMultiPoint(self.geom)
                self.multi = True
            for p in coordlist:
                self.geom.addpoint(*p[:dim])
            return

        if self.section is None:
            self.section = ogr.Geometry(ogr.wkbLineString)
        for p in coordlist:
            self.section.addpoint(*p[:dim])
        if self.section.IsRing():
            if self.ligne is None:
                self.section = ogr.Geometry(ogr.wkbLineString)

        if self.lignes:
            ligne_active = self.lignes[-1]
            if ligne_active.addpoint(coords, dim):
                # la ligne est fermee
                self.nouvelle_ligne_p(coords, dim)
                # on ajoute un point a une nouvelle ligne
        else:
            self.lignes = [C.Ligne(C.Section(coords, dim))]
        self.sgeom = None

    #

    def nouvelle_ligne_s(self, sect, interieur=None):
        """finit la ligne courante et en demarre une nouvelle avec une section"""
        self.lignes.append(C.Ligne(sect, interieur=interieur))

    def nouvelle_ligne_p(self, pnt, dim=2):
        """finit la ligne courante et en demarre une nouvelle avec un point"""
        self.lignes.append(C.Ligne(C.Section(pnt, dim)))

    def cree_section(self, liste_pts, dim, couleur, courbe, interieur=None):
        """cree une section et l'ajoute a la geometrie courante"""
        sect = C.Section(None, dim)
        sect.setsect(liste_pts, couleur, courbe)
        self.ajout_section(sect, interieur)
        # self.print_debug()

    def ajout_section(self, sect, interieur):
        """ajoute une section a la geometrie"""
        if self.lignes:
            if self.lignes[-1].ajout_section(sect):
                #                print ('objet:creation nouvelle ligne')
                self.nouvelle_ligne_s(sect, interieur)
        else:
            self.lignes = [C.Ligne(sect, interieur=False)]

    def fin_section(self, couleur, courbe):
        """ termine la section courante """
        sect = self.lignes[-1].fin_section(couleur, courbe)
        if sect:  # on a tente d'ajouter un cercle
            self.nouvelle_ligne_s(sect)

    def annule_section(self):
        """annule la derniere section en cours"""
        if self.lignes[-1].annule_section():
            self.lignes.pop()

    def traite_desordre(self):
        """on a des lignes dans le desordre"""
        a_traiter = self.lignes
        final = []
        reste = []
        suite = True
        while suite:
            #            print ('traitement', len(a_traiter))
            #            for i in final:
            #                print ('final: debut, fin',i.ppt,i.dpt, i.ferme)
            #            for i in a_traiter:
            #                print ('a_traiter: debut, fin',i.ppt,i.dpt, i.ferme)
            suite = False
            reste = []
            ligne = a_traiter.pop(0)
            if ligne.ferme:
                final.append(ligne)
            else:
                reste.append(ligne)
                for ligne2 in a_traiter:
                    if ligne.ajout_ligne(ligne2, desordre=True):
                        suite = True
                    else:
                        reste.append(ligne2)
            a_traiter = reste
        final.extend(reste)
        self.lignes = final
        #        for i in self.lignes:
        #            print ('sortie: debut, fin',i.ppt,i.dpt, i.ferme)
        #        print ('geometrie',self.ferme)
        if reste:
            print("ligne orpheline", reste)

    def finalise_geom(self, type_geom="0", orientation="L", desordre=False):
        """termine une geometrie et finalise la structure"""
        self.valide = True
        self.sgeom = None
        self.multi = False
        self.courbe = False

        self.null = (len(self.points) + len(self.lignes)) == 0
        # print ("finalise:",type_geom, len(self.points)+len(self.lignes))
        if type_geom == "0":
            self.type = "0"
            self.lignes = []
            self.polygones = []
            return True

        if self.null:
            self.valide = False
            self.type = "0"
            return False
        if self.type == "1":
            self.multi = len(self.points) > 1
            self.lignes = []
            self.polygones = []
            return True

        if type_geom != "2":
            if desordre:
                self.traite_desordre()
                # les lignes peuvent etre en desordre (gestion de la partition)
            if self.ferme:
                # toutes les lignes sont fermees et on autorise des polygones
                #                print( 'finalisation', len(self.lignes))
                for i in self.lignes:
                    aire = i.aire_orientee()
                    if aire == 0 and self.dimension == 2:
                        self.erreurs.ajout_erreur("contour degénéré " + type_geom)
                        self.valide = False
                        return False
                    if orientation == "R":
                        aire = -aire
                    if i.interieur is None:
                        i.interieur = aire < 0
                    if i.interieur:
                        if self.polygones:
                            self.polygones[-1].ajout_contour(i)
                        else:
                            i.interieur = False
                            self.polygones.append(C.Polygone(i))
                            self.erreurs.ajout_warning("interieur")
                    else:
                        self.polygones.append(C.Polygone(i))

        if self.lignes:
            self.type = "3" if self.polygones else "2"
        #        print ('fin_geom:type_geom ', self.type, type_geom)
        #        if typegeom==2:
        #            raise
        if self.type == "2":
            for i in self.lignes:
                for j in i.sections:
                    if j.npt < 2:
                        self.erreurs.ajout_erreur("section un point")
                        self.valide = False
        self.multi = len(self.polygones) - 1 if self.polygones else len(self.lignes) - 1
        self.courbe = any([i.courbe for i in self.lignes])
        if self.lignes:
            self.dim = self.lignes[0].dimension
        if self.type == "3" and (type_geom == "4" or type_geom == "5"):
            self.type = type_geom

        elif type_geom != "-1" and type_geom != "indef" and type_geom != self.type:
            self.erreurs.ajout_warning(
                "attention geometrie demandee: "
                + str(type_geom)
                + " trouve "
                + str(self.type)
            )
        #            self.valide = 0
        #        print ('fin_geom2:type_geom ', self.type, type_geom)
        return self.valide

    def split_couleur(self, couleurs):
        """decoupe une ligne selon la couleur des sections"""
        geoms = dict()
        self.shapesync()
        for i in self.lignes:
            for j in i.sections:
                coul_sect = j.couleur
                if couleurs and coul_sect not in couleurs:
                    coul_sect = "#autre"
                if coul_sect not in geoms:
                    geoms[coul_sect] = Geometrie()
                geoms[coul_sect].ajout_section(j.dupplique(), False)
        for i in geoms:
            geoms[i].finalise_geom("2")  # on force en ligne
        #        liste_couleurs = {j.couleur for j in itertools.chain.from_iterable([i.sections for i in self.lignes])}
        #        print ("decoupage en couleurs ", couleurs, len(geoms), liste_couleurs, len(self.lignes))
        return geoms

    def extract_couleur(self, couleurs):
        """ recupere les sections d'une couleur"""
        self.shapesync()
        geom = Geometrie()
        for i in self.lignes:
            for j in i.sections:
                if j.couleur in couleurs:
                    geom.ajout_section(j.dupplique(), False)
        return geom

    def has_couleur(self, couleur):
        """retourne True si la couleur existe dans l'objet"""
        self.shapesync()
        liste_couleurs = {
            j.couleur
            for j in itertools.chain.from_iterable([i.sections for i in self.lignes])
        }
        #        print('has_couleur',couleur, liste_couleurs, couleur in liste_couleurs)
        return couleur in liste_couleurs

    def forcecouleur(self, couleur1, couleur2):
        """remplace une couleur par une autre"""
        self.shapesync()
        for i in self.lignes:
            for j in i.sections:
                if j.couleur == couleur1:
                    j.couleur = couleur2
        self.sgeom = None

    def forceligne(self):
        """force la geometrie en ligne pour des polygones"""
        self.shapesync()

        if self.type == "3":
            self.type = "2"
        self.multi = len(self.lignes) - 1
        self.sgeom = None

    def translate(self, dx, dy, dz):
        """decale une geometrie"""
        self.shapesync()
        #        print ("translate geom avant :", list(self.coords))
        fonction = lambda coords: list(i + j for i, j in zip(coords, (dx, dy, dz)))
        self.convert(fonction)
        self.sgeom = None
        return True

    #        print ("translate geom aprest :", list(self.coords))

    def prolonge(self, longueur, mode):
        self.shapesync()

        """prolonge une multiligne"""
        #        print("dans prolonge", longueur, mode)
        if self.type != "2":
            return False
        if mode > 10:
            for i in self.lignes:
                i.prolonge(longueur, mode - 10)
        else:
            if mode % 2:  # prolongation du debut
                #                print("dans prolonge debut", longueur, mode)
                self.lignes[0].prolonge_debut(longueur)
            if mode >= 2:
                self.lignes[-1].prolonge_fin(longueur)
        self.sgeom = None
        return True

    #        print("geom apres prolonge", list(self.coords))
    #        print("longueur ",self.longueur)

    def forcepoly(self, force=False):
        """convertit la geometrie des lignes en polygones en fermant de force"""
        self.shapesync()
        if self.type == "2":
            valide = True
            for i in self.lignes:
                if not i.ferme:
                    valide = force and i.force_fermeture()

                if valide:
                    if i.aire < 0:
                        if self.polygones:
                            self.polygones[-1].ajout_contour(i)
                        else:
                            i.inverse()
                        self.polygones.append(C.Polygone(i))
                    else:
                        self.polygones.append(C.Polygone(i))
            if valide:
                self.type = "3"
                self.multi = len(self.polygones) - 1
            else:
                self.polygones = []
        self.sgeom = None

    @property
    def coords(self):
        """ iterateur sur les coordonnees"""
        self.shapesync()
        if self.points:
            return self.points
        if self.lignes:
            return itertools.chain(*[i.coords for i in self.lignes])
        return iter(())

    def convert(self, fonction, srid=None):
        """ applique une fonction aux points """
        self.shapesync()
        for crd in self.coords:
            for i, val in enumerate(fonction(crd)):
                crd[i] = val
        if srid:
            self.srid = str(int(srid))
        self.sgeom = None

    def set_2d(self):
        """transforme la geometrie en 2d"""
        self.shapesync()
        if self.dimension == 2:
            return
        self.dim = 2
        for i in self.lignes:
            i.set_2d()
        self.sgeom = None

        # if self.point:
        #     self.point.set_2d()

    def set_3d(self):
        """transforme la geometrie en 2d"""
        self.shapesync()
        if self.dimension == 3:
            return
        self.dim = 3
        for i in self.coords:
            if len(i) < 3:
                i.append(0)
        for i in self.lignes:
            i.set_3d()
        self.sgeom = None
        # if self.point:
        #     self.point.set_2d()

    def setz(self, val_z, force=False):
        """force le z """
        self.shapesync()
        if self.dimension == 3:
            if not force:
                return
        self.dim = 3
        for i in self.coords:
            i[2] = val_z if len(i) == 3 else i.append(val_z)
        for i in self.lignes:
            i.set_3d()
        self.sgeom = None
        # if self.point:
        #     self.point.setz(val_z)

    def emprise(self, coords=None):
        """calcule l'emprise"""
        if self.sgeom:
            return self.sgeom.bounds
        else:
            self.shapesync()

        liste_coords = list(self.coords) if coords is None else coords
        xmin, xmax, ymin, ymax = 0, 0, 0, 0
        try:
            if liste_coords:
                xmin = min([i[0] for i in liste_coords])
                xmax = max([i[0] for i in liste_coords])
                ymin = min([i[1] for i in liste_coords])
                ymax = max([i[1] for i in liste_coords])
        except:
            print(liste_coords)
            print("erreur emprise")
        return (xmin, ymin, xmax, ymax)

    def emprise_3d(self):
        """calcule l'emprise"""
        liste_coords = list(self.coords)
        zmin = 0
        zmax = 0
        xmin, xmax, ymin, ymax = self.emprise(liste_coords)
        try:
            if liste_coords:
                zmin = min([i[2] for i in liste_coords])
                zmax = max([i[2] for i in liste_coords])
        except:
            print(liste_coords)
            print("erreur emprise 3D")
        return (xmin, ymin, zmin, xmax, ymax, zmax)

    def getpoint(self, numero):
        """retourne le n ieme point"""
        #        print ('coordlist',self.type,list(self.coordlist()))
        if numero < 0:
            return list(self.coords)[numero]
        return next(itertools.islice(self.coords, numero, None), ())
        # for i in self.coords:
        #     if n == numero:
        #         return i
        #     n += 1
        # return i

    def print_debug(self):
        """affichage de debug"""
        print("debug: geom : geometrie", Geometrie)
        print("debug: geom : type: ", self.type, "lignes", len(self.lignes))
        for i in self.lignes:
            i.print_debug()

    # -------------------------------------------------------------------
    # ---------------------- interfaces ---------------------------------
    # -------------------------------------------------------------------

    @property
    def __json_if__(self):
        """  interface de type json """
        #        print ('jsonio ',self.type, self.null)
        if self.type == "0":
            return None
        dim = self.dimension
        if self.null:  # geometrie non definie
            return '"geometry": null\n'
        if self.type == "1":  # point
            if self.multi:
                return (
                    '"geometry": {\n"type": "MultiPoint",\n"coordinates":[\n['
                    + "],\n[".join([",".join(map(str, i[:dim])) for i in self.coords])
                    + "]\n]\n}"
                )
            else:
                return (
                    '"geometry": {\n"type": "Point",\n"coordinates":['
                    + ",".join(map(str, self.points[0][:dim]))
                    + "]\n}"
                )

        if self.type == "2":
            #            print ('type 2')
            if len(self.lignes) == 1:
                return (
                    '"geometry": {\n"type": "LineString",\n"coordinates":[\n['
                    + "],\n[".join(
                        [",".join(map(str, i[:dim])) for i in self.lignes[0].coords]
                    )
                    + "]\n]\n}"
                )
            else:
                return (
                    '"geometry": {\n"type": "MultiLineString",\n"coordinates":[\n[\n['
                    + "]],\n[[".join(
                        [
                            "],\n[".join(
                                [",".join(map(str, i[:dim])) for i in j.coords]
                            )
                            for j in self.lignes
                        ]
                    )
                    + "]\n]\n]\n}"
                )
        if self.type == "3":
            if len(self.polygones) == 1:
                if len(self.lignes) == 1:  # polygone sans trous
                    return (
                        '"geometry": {\n"type": "Polygon",\n"coordinates":[\n[\n['
                        + "],\n[".join(
                            [",".join(map(str, i[:dim])) for i in self.lignes[0].coords]
                        )
                        + "]\n]\n]\n}"
                    )
                else:
                    return (
                        '"geometry": {\n"type": "Polygon",\n"coordinates":[\n[\n['
                        + "]],\n[[".join(
                            [
                                "],\n[".join(
                                    [",".join(map(str, i[:dim])) for i in j.coords]
                                )
                                for j in self.lignes
                            ]
                        )
                        + "]\n]\n]\n}"
                    )

            return (
                '"geometry": {\n"type": "MultiPolygon",\n"coordinates":[\n[\n[\n['
                + "]]],\n[[[".join(
                    [
                        "]],\n[[".join(
                            [
                                "],\n[".join(
                                    [
                                        ",".join(map(str, pnt[:dim]))
                                        for pnt in lin.coords
                                    ]
                                )
                                for lin in pol.lignes
                            ]
                        )
                        for pol in self.polygones
                    ]
                )
                + "]\n]\n]\n]\n}"
            )
        if self.type == "4":  # tin
            return (
                '"geometry": {\n"type": "Tin",\n"coordinates":[\n[\n[\n['
                + "]]],\n[[[".join(
                    [
                        "]],\n[[".join(
                            [
                                "],\n[".join(
                                    [
                                        ",".join(map(str, pnt[:dim]))
                                        for pnt in lin.coords
                                    ]
                                )
                                for lin in pol.lignes
                            ]
                        )
                        for pol in self.polygones
                    ]
                )
                + "]\n]\n]\n]\n}"
            )

        if self.type == "5":  # polyhedralsurface
            return (
                '"geometry": {\n"type": "PolyhedralSurface",\n"coordinates":[\n[\n[\n['
                + "]]],\n[[[".join(
                    [
                        "]],\n[[".join(
                            [
                                "],\n[".join(
                                    [
                                        ",".join(map(str, pnt[:dim]))
                                        for pnt in lin.coords
                                    ]
                                )
                                for lin in pol.lignes
                            ]
                        )
                        for pol in self.polygones
                    ]
                )
                + "]\n]\n]\n]\n}"
            )

    @property
    def __geo_interface__(self):
        if self.type == "0":
            return {}
        dim = self.dimension
        if self.type == "1":  # point
            if not self.points:
                print("geo_interface : point inexistant")
                if self.force_multi or self.multi:
                    return {"type": "MultiPoint", "coordinates": ()}
                else:
                    return {"type": "Point", "coordinates": ()}
            multi = self.force_multi or self.multi or len(self.points) > 1
            if multi:
                return {
                    "type": "MultiPoint",
                    "coordinates": tuple([tuple(p[:dim]) for p in self.coords]),
                }
            else:
                return {"type": "Point", "coordinates": tuple(self.points[0][:dim])}

        elif self.type == "2":
            multi = self.force_multi or self.multi or len(self.lignes) > 1
            if multi:
                coordinates = []
                for ligne in self.lignes:
                    coordinates.append(tuple([tuple(p[:dim]) for p in ligne.coords]))
                return {"type": "MultiLineString", "coordinates": tuple(coordinates)}

            else:
                return {
                    "type": "LineString",
                    "coordinates": tuple(
                        [tuple(p[:dim]) for p in self.lignes[0].sections[0].coords]
                    ),
                }

        elif self.type == "3":

            multi = self.force_multi or self.multi or len(self.polygones) > 1

            if multi:
                if not self.polygones:
                    return {"type": "MultiPolygon", "coordinates": ()}
                polys = []
                for poly in self.polygones:
                    rings = []
                    #                    print ('geoif mpol',len(poly.lignes), len(self.polygones) )

                    for ligne in poly.lignes:
                        rings.append(tuple([tuple(p[:dim]) for p in ligne.coords]))
                    polys.append(tuple(rings))
                return {"type": "MultiPolygon", "coordinates": tuple(polys)}
            else:
                if not self.polygones:
                    return {"type": "Polygon", "coordinates": ()}
                rings = []
                #                print ('geoif pol',len(self.polygones[0].lignes))
                for ligne in self.polygones[0].lignes:
                    rings.append(tuple([tuple(p[:dim]) for p in ligne.coords]))
                return {"type": "Polygon", "coordinates": tuple(rings)}

        elif self.type == "4":  # tin
            polys = []
            for poly in self.polygones:
                rings = []
                for ligne in poly.lignes:
                    rings.append(tuple([tuple(p[:dim]) for p in ligne.coords]))
                polys.append(tuple(rings))
            return {"type": "Tin", "coordinates": tuple(polys)}

        elif self.type == "5":  # tin
            polys = []
            for poly in self.polygones:
                rings = []
                for ligne in poly.lignes:
                    rings.append(tuple([tuple(p[:dim]) for p in ligne.coords]))
                polys.append(tuple(rings))
            return {"type": "PolyhedralSurface", "coordinates": tuple(polys)}

    def from_geo_interface(
        self, geo_if
    ):  # cree une geometrie a partir de la geo_interface
        #        print ('geom from geo_if',geo_if)
        if not geo_if:
            self.finalise_geom(type_geom="0")
            return
        if geo_if["type"] == "Point":
            self.setpoint(geo_if["coordinates"], None, len(geo_if["coordinates"]))
            self.finalise_geom(type_geom="1")

        elif geo_if["type"] == "MultiPoint":
            dim = len(geo_if["coordinates"][0])
            for point in geo_if["coordinates"]:
                self.addpoint(point, dim)
            self.finalise_geom(type_geom="1")

        elif geo_if["type"] == "LineString":
            dim = len(geo_if["coordinates"][0])
            self.cree_section(geo_if["coordinates"], dim, 1, 0)

            #            self.nouvelle_ligne_s(C.Section(list(geo_if["coordinates"]),dim))
            #            for pt in geo_if["coordinates"]:
            #                self.addpoint(pt,dim)
            self.finalise_geom(type_geom="2")
        elif geo_if["type"] == "MultiLineString":
            dim = len(geo_if["coordinates"][0][0])
            for ligne in geo_if["coordinates"]:
                self.cree_section(ligne, dim, 1, 0)

            #                self.nouvelle_ligne_s(C.Section(list(ligne),dim))

            #                for pt in ligne:
            #                    self.addpoint(pt,dim)
            #                self.fin_section(1,0)
            self.finalise_geom(type_geom="2")
        elif geo_if["type"] == "Polygon":
            dim = len(geo_if["coordinates"][0][0])
            #            print ('gif:polygone',geo_if["coordinates"][0][0])
            interieur = False
            for ligne in geo_if["coordinates"]:
                self.cree_section(ligne, dim, 1, 0, interieur=interieur)
                #                print ('lin',ligne,interieur,len(self.lignes))

                interieur = True

            #                self.nouvelle_ligne_s(C.Section(list(ligne),dim))

            #            for pt in geo_if["coordinates"][0]:
            #                self.addpoint(pt,dim)
            self.finalise_geom(type_geom="3")
            self.multi = True

        #            print ('creation polygone',len(self.polygones), self.multi)
        elif geo_if["type"] == "MultiPolygon":
            dim = len(geo_if["coordinates"][0][0][0])
            interieur = False
            for poly in geo_if["coordinates"]:
                for ligne in poly:
                    self.cree_section(ligne, dim, 1, 0)
                    interieur = True
            #                    self.nouvelle_ligne_s(C.Section(list(ligne),dim))
            #                    for pt in ligne:
            #                        self.addpoint(pt,dim)
            #                    self.fin_section(1,0)
            self.finalise_geom(type_geom="3")
            self.multi = True

        elif geo_if["type"] == "Tin":
            dim = len(geo_if["coordinates"][0][0][0])
            for poly in geo_if["coordinates"]:

                for ligne in poly:
                    self.cree_section(ligne, dim, 1, 0)

            #                    self.nouvelle_ligne_s(C.Section(list(ligne),dim))
            #                    for pt in ligne:
            #                        self.addpoint(pt,dim)
            #                    self.fin_section(1,0)
            self.finalise_geom(type_geom="4", orientation="L")

        elif geo_if["type"] == "PolyhedralSurface":
            dim = len(geo_if["coordinates"][0][0][0])
            for poly in geo_if["coordinates"]:

                for ligne in poly:
                    self.cree_section(ligne, dim, 1, 0)

            #                    self.nouvelle_ligne_s(C.Section(list(ligne),dim))
            #                    for pt in ligne:
            #                        self.addpoint(pt,dim)
            #                    self.fin_section(1,0)
            self.finalise_geom(type_geom="5", orientation="L")
        else:
            print("geom:geometrie inconnue ", geo_if)

    #        print ('geometrie',self.type,list(self.coords))

    @property
    def __shapelygeom__(self):
        """ retourne un format shapely de la geometrie"""
        # print("geom:",self)
        if not self.sgeom:
            self.sgeom = SG.shape(self)
        return self.sgeom

    @property
    def __shapelyprepared__(self):
        """stocke une geometrie pereparee de l'objet"""
        if not self.sgp:
            self.sgp = P.prep(self.__shapelygeom__)
        return self.sgp

    def shapesync(self):
        """recree la geometrie a partir d'un element shapely"""
        if not self.valide and self.sgeom:
            self.from_geo_interface(SG.mapping(self.sgeom))

    @property
    def fold(self):
        """retourne une structure compacte pour les comparaisons"""
        return self.geom.ExportToWkb()

    def unfold(self, folded):
        """recree une geometrie a partir de la forme compacte"""
        if folded is None:
            self.valide = True
            self.sgeom_valide = False
            self.type = "0"
            self.null = True
            return
        if folded == ((), (), ()):
            self.__init__()
            return
        crd, ldef, pdef = folded
        if len(crd) == 1:  # c 'est un point
            coords, angle, longueur = crd[0]
            self.setpoint(coords, angle, len(coords), longueur)
            self.finalise_geom(type_geom="1")
            return
        dim = len(crd[0])
        if not ldef:
            for pnt in crd:
                self.addpoint(pnt, dim)
            self.finalise_geom(type_geom="1")
            return
        if not pdef:
            for ligne in ldef:
                depart = 0
                for fin, couleur, courbe in ligne:
                    fin = fin + depart
                    self.cree_section(crd[depart:fin], dim, couleur, courbe)
                    depart = fin
            self.finalise_geom(type_geom="2")
            return
        for poly in pdef:
            dep_p = 0
            for fin_p in poly:
                fin_p = dep_p + fin_p
                interieur = False
                for ligne in ldef[dep_p:fin_p]:
                    depart = 0
                    for fin, couleur, courbe in ligne:
                        fin = fin + depart
                        self.cree_section(crd[depart:fin], dim, couleur, courbe)
                        depart = fin
                    interieur = True
                dep_p = fin_p
        self.finalise_geom(type_geom="2")

    def __repr__(self):
        if self.null:
            return "geometrie vide"
        if self.valide:
            return "type:" + self.type + " ".join(str(i) for i in self.coords)
        elif self.sgeom:
            return repr(self.sgeom)
        return "geometrie invalide " + repr(self.erreurs)


class Erreurs(object):
    """gere le stockage de erreurs sur un objet."""

    def __init__(self):
        self.errs = []
        self.warns = []
        self.actif = 0

    def ajout_erreur(self, nature):
        """ ajoute un element dans la structure erreurs et l'active"""
        self.errs.append(nature)
        self.actif = 2

    def ajout_warning(self, nature):
        """ ajoute un element de warning dans la structure erreurs et l'active"""
        self.warns.append(nature)
        if self.actif == 0:
            self.actif = 1

    def reinit(self):
        """reinitialise la structure"""
        self.__init__()

    def getvals(self):
        """recupere les erreurs en format texte"""
        return "; ".join(self.errs)

    def __repr__(self):
        """erreurs et warnings pour affichage direct"""
        if not self.actif:
            return ""
        return "\n".join(("actif:" + str(self.actif), "errs:" + self.getvals()))


class AttributsSpeciaux(object):
    """gere les attibuts speciaux a certains formats """

    def __init__(self):
        self.special = dict()

    def set_att(self, nom, nature):
        """positionne un attribut special"""
        self.special[nom] = nature

    def get_speciaux(self):
        """ recupere la lisdte des attributs speciaux"""
        return self.special


def noconversion(obj):
    """ conversion geometrique par defaut """
    return obj.attributs["#type_geom"] == "0"
