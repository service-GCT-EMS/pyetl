# -*- coding: utf-8 -*-
"""
Acces aux services web wfs

commandes disponibles :

    * requete getcapabilities et analyse des donnees disponibles


necessite la librairie owslib

il est necessaire de positionner les parametres suivant:


"""
from codecs import unicode_escape_decode
from copy import Error
from re import I
import html

# version patchee de owslib pour eviter un crash sur data.strasbourg.eu

# from pyetl.formats.csv import geom_from_ewkt, ecrire_geom_ewkt
from .database import DbConnect, Cursinfo
from .gensql import DbGenSql
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService
from owslib.csw import CatalogueServiceWeb
from owslib.namespaces import Namespaces
from owslib.util import Authentication
import owslib.fes as F
from owslib.etree import etree

# global F, etree, WebFeatureService

# def importer():

#     from owslib.wfs import WebFeatureService
#     import owslib.fes as F
#     from owslib.etree import etree


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
    "str":"T",
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

OSWNAMESPACES=Namespaces()

def get_oswnamespace(nom):
    return OSWNAMESPACES.get_namespace(nom)


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
        # importer()

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
            nouv_table = [groupe, nom, "", "", "", -1, "", "", "", "", "",""]
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



class CswCursinfo(Cursinfo):
    """simule un curseur pour recuperer les resultats"""
    def __init__(self,connecteur, volume=0, nom="", regle=None):
        super().__init__(connecteur, volume, nom, regle)
        self.cursor=CswCursor(self)

class CswCursor(object):
    """simule un curseur pour recuperer les resultats"""
    def __init__(self,cursinfo):
        self.cursinfo=cursinfo
        self.regle=cursinfo.regle
        self.connecteur=cursinfo.connecteur
        self.connection=self.connecteur.connection
        self.description=None
        self.lire_maxi=int(self.regle.getvar("lire_maxi",0))
        # self.connection.getrecords2(esn="full",maxrecords=1,cql=self.connecteur.requete,startposition=1)
        self.connection.getrecords2(esn="full",outputschema=get_oswnamespace("gmd"),maxrecords=1,cql=self.connecteur.requete,startposition=1)
        self.returned=self.connection.results["returned"]
        if self.returned:
            record=self.connection.records.popitem()[1]
            self.cursinfo.attlist=[i for i in dir(record) if not i.startswith("_")]

            

        
    def __iter__(self):
        print ("dans cswcursor")
        nextrecord=1
        while nextrecord and (nextrecord<=self.lire_maxi) if self.lire_maxi else nextrecord:
            nbrec=min(100,(self.lire_maxi+1-nextrecord) if self.lire_maxi else 100)
            self.connection.getrecords2(esn="full",outputschema=get_oswnamespace("gmd"),maxrecords=nbrec,cql=self.connecteur.requete,startposition=nextrecord)
            # self.connection.getrecords2(esn="full",maxrecords=nbrec,cql=self.connecteur.requete,startposition=nextrecord)
            nmatch=self.connection.results["matches"]
            nextrecord=self.connection.results["nextrecord"]
            # print ("recup",self.connection.results)
            while self.connection.records:
                record=self.connection.records.popitem()[1]
                valeurs=[getattr(record,i) for i in self.cursinfo.namelist]
                valeurs=[(i.decode(encoding='UTF-8')) if isinstance(i,bytes) else i for i in valeurs ]
                valeurs=[(html.unescape(i)) if isinstance(i,str) else i for i in valeurs ]
                # print ("lecture valeurs csw",valeurs)
                yield valeurs
                
    def close(self):
        pass
    
    

class CswConnect(DbConnect):
    """connecteur csw: simule un acces base a partir du schema pour des services de catalogue"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        # importer()

        self.types_base.update(TYPES_A)
        self.type_base = "csw"
        self.tablelist = []
        self.connect()
        self.geographique = True
        self.accept_sql = "no"
        self.curtable = ""
        self.curnb = 0

    def connect(self):
        """effectue un getcapabilities pour connaitre le schema"""
        try:
            # print("connection csw", self.serveur)
            
            serveur = self.serveur
            from requests_negotiate_sspi import HttpNegotiateAuth
            from requests.auth import AuthBase
            auth = HttpNegotiateAuth()
            # print("recup auth",dir(auth),
            #                     [(i,getattr(auth,i)) for i in dir(auth)] 
            #                     )
            
            self.connection = CatalogueServiceWeb(url=serveur,auth=Authentication(auth_delegate=auth))
            self.connection.cursor = lambda: None
            # simulation de curseur pour l'initialisation
            self.connection.getrecords2(esn="full",maxrecords=2)
        except Exception as err:
            print( "erreur de connection au service ", serveur)
            self.refrecord=None
            if self.regle.istrue("debug"):
                print("erreur wfs", err)
            return False
        
        self.storedrowcount=self.connection.results["matches"]
        if self.storedrowcount=="0":
            print ("pas de retour wfs") 
            return False
        if self.connection.records:
            self.refrecord=self.connection.records.popitem()
        else:
            self.refrecord={}
            print("retour",self.refrecord)

        reponse=self.connection.response
        self.tablelist = ["metadata"]

        import requests
        req_test=requests.Request('GET', url=serveur,auth=auth)
        r = req_test.prepare()
        print ("requete",r, dir(r))
        print("recup auth",dir(r),'\n'.join( ["=".join((i,repr(getattr(r,i)))) for i in dir(r) if not i.startswith('_')] )
                            )
    #   >>> req = requests.Request('GET', 'https://httpbin.org/get')
    #   >>> r = req.prepare()
    #   >>> r
        # print("retour getcap", len(self.tablelist))

    def commit(self):
        pass

    def get_tables(self):
        """ retourne la liste des tables """
        return list(self.tables.values())

    @property
    def rowcount(self):
        return self.storedrowcount

    def get_attr_of_classe(self, schemaclasse):
        """recupere la description d une classe"""
        pass
        
    def get_attributs(self):
        """description des attributs de la base sqlite
        structure fournie :
            nom_groupe;nom_classe;nom_attr;alias;type_attr;graphique;multiple;\
            defaut;obligatoire;enum;dimension;num_attribut;index;unique;clef_primaire;\
            clef_etrangere;cible_clef;taille;decimales"""

        attlist = []
        tables = self.tablelist
        # print("webservices: lecture tables", tables)
        if self.refrecord:
            attdict={i:type(i).__name__ for i in dir(self.refrecord[1]) if not i.startswith("_")} 
        else:
            attdict={}
        # print ("format metadonnee", attdict)
        for nom,typedef in attdict.items():
            pyetltype = ALLTYPES.get(typedef)
            if pyetltype is None:
                print(" type inconnu", typedef)
                pyetltype = "T"
            att=self.attdef(nom_groupe="md",nom_classe="metadata",nom_attr=nom,type_attr=pyetltype)
            attlist.append(att)
        ident = ("md", "metadata")
        nouv_table = ["md", "metadata", "", "", "", -1, "", "", "", "", "",""]
            # print ('table', nouv_table)
        self.tables[ident] = nouv_table
        self.attlist=attlist[:]
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
            CswCursinfo(self, volume=volume, nom=nom, regle=regle)
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

    def req_alpha(self, ident, schema, attr, val, mods, maxi=0, ordre=None):
        """recupere les elements d'une requete alpha"""
        niveau, classe = ident
        self.requete = None
        cond=""
        # print ("req_alpha",ident,attr,val)
        if val:
            if val.startswith("~"):
                cond=' Like '
                val="%"+val[1:]+"%"
            else:
                cond=' = '
            val="'"+val+"'"
            if not attr or attr=="*":
                attr="csw:AnyText"
            self.requete= attr+cond + val
        # print ("construction requete",self.requete, ident,attr,val)
        # raise
            # self.requete=r"csw:AnyText Like '%ilot%'"

        # self.connection.getrecords2(esn="full",maxrecords=10)
        # reponse=self.connection.records
    
        # print(" reponse", reponse)
        return self.get_cursinfo(regle=self.regle)
        
    def dbinsert(self,schema,ident,valeurs,updatemode=1):
        """insere sur le webservice : accepte un seul champs en entree : le xml"""
        print ("dans dbibsert webservice",ident, len(valeurs))
        if len(schema)>1:
            raise KeyError("un seul champs autorisé", ','.join(valeurs.keys()))

        for value in valeurs:
            texte=value[0].replace('&','\\&')
            print ('preparation insertion ', texte)
            try:
                self.connection.transaction(ttype='insert', typename='gmd:MD_Metadata', record=texte)
                print ("------------------------------insertion csw")
            except :
                print ('erreur insertion')
                raise
        return True

    def dbload(self, schema, ident, valeurs, insertmode):
        """charge des objets en base de donnees par dbload"""
        return self.dbinsert(schema,ident,valeurs,updatemode=insertmode)






DBDEF = {"wfs2": (WfsConnect, WfstGenSql, "server", "", "#gml", "acces wfs"),
         "csw": (CswConnect, WfstGenSql, "server", "", "#gml", "acces metadonnees")}
