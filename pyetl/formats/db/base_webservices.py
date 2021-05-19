# -*- coding: utf-8 -*-
"""
Acces aux services web wfs

commandes disponibles :

    * requete getcapabilities et analyse des donnees disponibles


necessite la librairie owslib

il est necessaire de positionner les parametres suivant:


"""
from copy import Error

# version patchee de owslib pour eviter un crash sur data.strasbourg.eu
# from owslib.wfs import WebFeatureService
# import owslib.fes as F
# from owslib.etree import etree

# from pyetl.formats.csv import geom_from_ewkt, ecrire_geom_ewkt
from .database import DbConnect, Cursinfo
from .gensql import DbGenSql

TYPES_A = {
    "T": "T",
    "F": "F",
    "D": "D",
    "DS": "DS",
    "E": "E",
    "EL": "EL",
    "N": "N",
    "B": "B",
    "S": "S",
    "xsd:string": "T",
    "string": "T",
    "xsd:date": "DS",
    "date": "DS",
    "xsd:int": "E",
    "int": "E",
    "short": "E",
    "long": "EL",
    "integer": "E",
    "xsd:dateTime": "D",
    "dateTime": "D",
    "xsd:double": "F",
    "decimal": "F",
    "double": "F",
    "boolean": "B",
}

TYPES_G = {
    "GeometryCollection": "-1",
    "Point": "1",
    "MultiPoint": "1",
    "3D Polygon": "3",
    "3D MultiPolygon": "3",
}

ALLTYPES = dict(TYPES_A)
ALLTYPES.update(TYPES_G)


def getnamespace(root):
    """extrait les namespaces xml"""
    roottag = root.tag
    namespace = ""
    if "}" in roottag:
        namespace = roottag.split("}")[0] + "}"
    return namespace


class WfsCursinfo(Cursinfo):
    pass


class WfsConnect(DbConnect):
    """connecteur wwfs: simule un acces base a partir du schema"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        from owslib.wfs import WebFeatureService
        import owslib.fes as F
        from owslib.etree import etree

        self.types_base.update(TYPES_A)
        self.type_base = "wfs"
        self.tablelist = []
        self.connect()
        self.geographique = True
        self.accept_sql = "no"
        self.curtable = ""
        self.curnb = 0

    def connect(self):
        """effectue un getcapabilities pour connaitre le schema"""
        try:
            print("connection wfs", self.serveur)
            if "version=" in self.serveur:
                serveur, vdef = self.serveur.split(" ", 1)
                version = vdef.split("=")[1]
            else:
                serveur = self.serveur
                version = "1.1.0"
            self.connection = WebFeatureService(url=serveur, version=version)
            self.connection.cursor = lambda: None
            # simulation de curseur pour l'initialisation
        except Error as err:
            print("erreur wfs", err)
            return False
        self.tablelist = [
            tuple(i.split(":", 1) if ":" in i else ["", i])
            for i in self.connection.contents
        ]
        # print("retour getcap", len(self.tablelist))

    def commit(self):
        pass

    def get_tables(self):
        """ retourne la liste des tables """
        return list(self.tables.values())

    @property
    def rowcount(self):
        return -1

    def get_attr_of_classe(self, schemaclasse):
        """recupere la description d une classe"""
        ident = schemaclasse.identclasse
        print("analyse classe", ident)
        groupe, nom = ident
        wfsid = ":".join(ident)
        schemadef = self.connection.get_schema(wfsid)
        # print("recup attlist ", attdict)
        del schemaclasse.attributs["__pending"]
        if schemadef is None:
            print("schema non present sur le serveur", ident)
            return
        attdict = schemadef["properties"]
        if attdict is not None:
            for nom_att, xmltype in attdict.items():
                # print(nom_att, xmltype)
                pyetltype = ALLTYPES.get(xmltype)
                if pyetltype is None:
                    print(" type inconnu", xmltype)
                    pyetltype = "T"
                schemaclasse.stocke_attribut(nom_att, pyetltype)
        type_geom = schemadef.get("geometry")
        if type_geom:
            if type_geom in TYPES_G:
                type_geom = TYPES_G[type_geom]
            else:
                print("geometrie inconnue", type_geom)
                type_geom = "-1"
            nom_geom = schemadef["geometry_column"]
            dimension = 2
            schemaclasse.stocke_geometrie(
                type_geom, dimension=dimension, srid="3948", multiple=1, nom=nom_geom
            )

    def get_attributs(self):
        """description des attributs de la base sqlite
        structure fournie :
            nom_groupe;nom_classe;nom_attr;alias;type_attr;graphique;multiple;\
            defaut;obligatoire;enum;dimension;num_attribut;index;unique;clef_primaire;\
            clef_etrangere;cible_clef;taille;decimales"""

        attlist = []
        tables = self.tablelist
        print("webservices: lecture tables", tables)

        for groupe, nom in tables:
            att = self.attdef(
                groupe,
                nom,
                "__pending",
                self.get_attr_of_classe,
                "T",
                "",
                "",
                "",
                "",
                "",
                2,
                0,
                "",
                "",
                "",
                "",
                "",
                "",
                0,
                0,
            )
            attlist.append(att)

            ident = (groupe, nom)
            nouv_table = [groupe, nom, "", "", "", -1, "", "", "", "", ""]
            # print ('table', nouv_table)
            self.tables[ident] = nouv_table
        return attlist

    def get_enums(self):
        return ()

    def get_type(self, nom_type):
        if nom_type in TYPES_G:
            return nom_type
        return self.types_base.get(nom_type.upper(), "?")

    def get_cursinfo(self, volume=0, nom="", regle=None):
        """recupere un curseur"""
        # print(" postgres get cursinfo")
        return (
            WfsCursinfo(self, volume=volume, nom=nom, regle=regle)
            if self.connection
            else None
        )

    def get_surf(self, nom):
        return ""

    def get_perim(self, nom):
        return ""

    def get_long(self, nom):
        return ""

    def get_geom(self, nom):
        return ""

    def set_geom(self, geom, srid):
        return ""

    def set_geomb(self, geom, srid, buffer):
        return ""

    def set_limit(self, maxi, _):
        if maxi:
            return "maxFeatures=" + str(maxi)
        return ""

    def cond_geom(self, nom_fonction, nom_geometrie, geom2):
        cond = ""
        fonction = ""
        if nom_fonction == "dans_emprise":
            bbox = getbbox(geom2)
            return bbox
        return ""

    def req_alpha(self, ident, schema, attribut, valeur, mods, maxi=0, ordre=None):
        """recupere les elements d'une requete alpha"""
        niveau, classe = ident
        requete = ""
        data = ""
        schema.resolve()
        attlist = schema.get_liste_attributs()
        self.get_attr_of_classe
        params = {"typename": niveau + ":" + classe}
        if attribut:
            filter = F.PropertyIsLike(
                propertyname=attribut, literal=valeur, wildCard="*"
            )
            filterxml = etree.tostring(filter.toXML(), encoding="unicode")
            params["filter"] = filterxml
        print("envoi requete", params)
        # reponse = self.connection.getfeature(**params)
        reponse = self.connection.getfeature(typename=niveau + ":" + classe)
        print("wfs apres reponse", type(reponse))
        return reponse


class WfstGenSql(DbGenSql):
    """generateur sql"""

    pass


DBDEF = {"wfs2": (WfsConnect, WfstGenSql, "server", "", "#gml", "acces wfs")}
