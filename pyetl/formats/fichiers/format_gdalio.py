# -*- coding: utf-8 -*-
''' format geojson en lecture et ecriture'''

import os
#import time
import collections
import itertools
import fiona
from fiona.crs import from_epsg
#from ..interne.objet import Objet
from .fileio import FileWriter



def recup_schema_fiona(schema_courant, ident, description):
    '''cree un schema a partir d une description fiona'''
    code_g = {'Point':'1', 'LineString':'2', "MultiLineString":'2',
              "Polygon":'3', "MultiPolygon":'3', "None":'0'}
    types_a = {"str":"T", "int":"E", "float":"F",
               "datetime":"D", "date":"D", "time":"D"}
    sc_classe = schema_courant.get_classe(ident)
#    print ('gdalio:recherche schema ',ident, sc_classe, schema_courant.nom,
#           schema_courant.classes.keys())
#    print ('recup_schema fiona:', description)
    if sc_classe:
        return sc_classe
    sc_classe = schema_courant.def_classe(ident)
    if 'geometry' in description:
        nom_geom = description['geometry']
        type_geom = code_g.get(nom_geom, '-1')
        dimension = 2
        if '3D ' in nom_geom:
            dimension = 3
            nom_geom = nom_geom.split(' ')[1]
            type_geom = code_g.get(nom_geom, '-1')
        if 'Multi' in nom_geom:
            sc_classe.multigeom = True
    else:
        nom_geom = ''
        type_geom = '0'
        dimension = 0
#    print('type geometrique fiona', type_geom, nom_geom)
    sc_classe.info["type_geom"] = type_geom
    for i in description['properties']:
        type_att = description['properties'][i]
        taille = '0'
        dec = '0'
        if ':' in type_att:
            vv_tmp = type_att.split(':')
            type_att = vv_tmp[0]
            taille = vv_tmp[1]
            if "." in taille:
                vv_tmp = taille.split(".")
                taille = vv_tmp[0]
                dec = vv_tmp[1]

        sc_classe.stocke_attribut(i, types_a[type_att], dimension=dimension,
                                  force=True, taille=int(taille), dec=int(dec), ordre=-1)
    return sc_classe

def schema_fiona(sc_classe, liste_attributs=None, l_nom=0):
    '''cree une description fiona d un schema'''
#    nom_g_s = {'1': 'Point', '2': 'LineString', '3': "Polygon"}
    nom_g_m = {'1': 'Point', '2': "MultiLineString", '3': "MultiPolygon"}
    nom_a = {"texte": "str",
             "entier": "int", "sequence": "int", "entier_long": "str",
             "reel": "float", "date": "date", "hstore": "str"}
    description = dict()
    type_geom = sc_classe.info["type_geom"]
    if type_geom > '0':
        nom_geom = (nom_g_m[type_geom])
#        nom_geom = (nom_g_m[type_geom] if sc_classe.multigeom or sc_classe.info['courbe']
#                    else nom_g_s[type_geom])
        if sc_classe.info["dimension"] == '3':
            nom_geom = '3D '+ nom_geom
        description['geometry'] = nom_geom
    elif type_geom == '-1':
        print('geometrie inconnue', sc_classe)
        description['geometry'] = None
    else:
        description['geometry'] = None

    props = collections.OrderedDict()
    description["properties"] = props
    if l_nom:
        sc_classe.use_noms_courts = True
    for i in sc_classe.get_liste_attributs(liste=liste_attributs):
        att = sc_classe.attributs[i]
        if l_nom and att.nom_court:
            nom = att.nom_court
        else:
            nom = att.nom
        nom = sc_classe.minmajfunc(nom)
#        print ("fiona: attribut",i,att.nom_court,nom, l_nom)
        if att.conformite:
            att.type_att = 'T'
            att.taille = att.conformite.taille
        #graphique="oui" if att.graphique else 'non'
        taille = ''
        type_att = nom_a[att.get_type()]

        if att.taille:
            taille = str(att.taille)
            if att.dec:
                taille = taille+'.'+str(att.dec)
        if taille:
            type_att = type_att+":"+taille
        props[nom] = type_att
    if not props:
        props[sc_classe.minmajfunc("gid")] = "str"
    return description

def map_schema_initial(stock_param, nomschema, groupe, classe):
    ''' gere les mapping initiaux a la lecture '''
    if stock_param.get_param("schema_entree"):
        nomschema = stock_param.get_param("schema_entree")
#        print ('gdalio:schema initial',nomschema)
    if not nomschema:
        nomschema = groupe if groupe else classe
    if not nomschema:
        nomschema = 'defaut'
    if nomschema not in stock_param.schemas:
        stock_param.init_schema(nomschema)
    schema_courant = stock_param.schemas[nomschema]
    groupe, classe = schema_courant.map_dest((groupe, classe))
#    print('fiona:schema courant', schema_courant.nom, groupe, classe)

    return schema_courant, groupe, classe


#def lire_objets_asc(rep, chemin, fichier, td, ouv=None):
def lire_objets(self, rep, chemin, fichier):
    ''' lecture d'un fichier reconnu et stockage des objets en memoire'''
    n_lin, n_obj = 0, 0
#    print ('lecture gdal',(rep, chemin, fichier))
#    raise
    #ouv = None
    stock_param = self.regle_ref.stock_param
    obj = None
    classe = os.path.splitext(os.path.basename(fichier))[0]
    groupe = chemin if chemin else os.path.basename(os.path.dirname(fichier))
    if not groupe:
        groupe = 'defaut'
    groupe = groupe


#    traite_objet = stock_param.moteur.traite_objet
    maxobj = stock_param.get_param('lire_maxi', 0)
    entree = os.path.join(rep, chemin, fichier)
    layers = fiona.listlayers(entree)
#    print('fiona:lecture niveaux',  layers)
    for layer in layers:
        with fiona.open(entree, 'r', layer=layer) as source:
            schema_courant, groupe, classe = map_schema_initial(stock_param, groupe, groupe, layer)

            schemaclasse = recup_schema_fiona(schema_courant, (groupe, classe), source.schema)
            self.classe = classe
            self.groupe = groupe
#            print('fiona:', classe, 'schema.type_geom',
#                  schemaclasse.info["type_geom"], 'mg:', schemaclasse.multigeom)
            driver = source.driver
            gen = (i for i in source if i)
            if maxobj:
                gen = itertools.islice(gen, maxobj)
            for i in gen:
                obj = self.getobj()
#                obj = Objet(groupe, classe, format_natif=driver)
                obj.schema = schemaclasse
                n_obj += 1
                if n_obj % 100000 == 0:
                    print("formats :", fichier, "lecture_objets_gdal ", driver, n_lin, n_obj)
                obj.from_geo_interface(i)
    #            print ('entree', i)
    #            print ('objet', obj.__geo_interface__)
                obj.attributs["#chemin"] = chemin
                self.traite_objet(obj, self.regle_start)
    return n_obj



class GdalWriter(FileWriter):
    ''' gestionnaire d'ecriture pour fichiers gdal'''
    def __init__(self, nom, liste_att=None, encoding='utf-8', converter=str,
                 schema=None, f_sortie=None, liste_fich=None, srid='3948', layer=None):
        if f_sortie is not None:
            self.driver = f_sortie.driver
            self.l_max = f_sortie.l_max
            if f_sortie.minmaj == 'up':
                self.minmajfunc = str.upper
            elif f_sortie.minmaj == 'low':
                self.minmajfunc = str.lower
            else:
                self.minmajfunc = str
            self.layer = layer
#            print('convertisseur de casse ', f_sortie.minmaj, self.minmajfunc)
            self.fanout = f_sortie.multiclasse
            self.fanoutmax = f_sortie.fanoutmax
        super().__init__(nom, liste_att=liste_att, converter=converter,
                         encoding=encoding, liste_fich=liste_fich, srid=srid, schema=schema)

#        print ('ascwriter ',liste_att)

    def open(self):
        '''ouvre  sur disque'''
        crs = from_epsg(int(self.srid))
        if self.l_max:
            self.schema.cree_noms_courts(longueur=self.l_max)
        schema = schema_fiona(self.schema, liste_attributs=self.liste_att, l_nom=self.l_max)
#        print('fiona: ouverture', self.nom, self.layer)
        self.fichier = fiona.open(self.nom, 'w', crs=crs, encoding=self.encoding,
                                  driver=self.driver, schema=schema, layer=self.layer)
        self.stats[self.nom] = self.stats.get(self.nom, 0)
        self.etat = self.OPEN

    def changeclasse(self, schemaclasse, attributs=None):
        ''' change de classe '''
        super().changeclasse(schemaclasse, attributs=None)
        self.fichier.close()
        _, classe = schemaclasse.identclasse
        self.layer = classe
        crs = from_epsg(int(self.srid))
        self.schema = schemaclasse
        schema = schema_fiona(self.schema, liste_attributs=self.liste_att, l_nom=self.l_max)
#        print ('fiona: reouverture' ,self.nom, self.layer)
        self.fichier = fiona.open(self.nom, 'w', crs=crs, encoding=self.encoding,
                                  driver=self.driver, schema=schema, layer=self.layer)


    def reopen(self):
        '''reouvre le fichier s'il aete ferme entre temps'''
        crs = from_epsg(int(self.srid))
        schema = schema_fiona(self.schema, liste_attributs=self.liste_att, l_nom=self.l_max)
        self.fichier = fiona.open(self.nom, 'a', crs=crs, encoding=self.encoding,
                                  driver=self.driver, schema=schema, layer=self.layer)


    def set_liste_att(self, liste_att):
        '''stocke la liste des attributs a sortir'''
        self.liste_att = liste_att


    def write(self, obj):
        '''ecrit un objet complet'''
        chaine = self.converter(obj, self.liste_att, self.minmajfunc)
#        print('gdal:write', chaine)
        try:
            self.fichier.write(chaine)
        except:
            print('erreur ecriture', obj.ident, self.liste_att, chaine)
            raise
        self.stats[self.nom] += 1
        return True

    def finalise(self):
        super().finalise()
        return 3


def gdalconverter(obj, liste_att, minmajfunc):
    '''convertit un objet dans un format compatible avec la lib gdal'''
    if liste_att:
        obj.set_liste_att(liste_att)
    obj.casefold = minmajfunc
    a_sortir = obj.__geo_interface__
    if not a_sortir["properties"]:
        a_sortir["properties"][obj.casefold("gid")] = a_sortir["id"]
    return a_sortir

def gdalstreamer(self, obj, regle, final, attributs=None, rep_sortie=None):
    '''ecrit des objets json au fil de l'eau.
        dans ce cas les objets ne sont pas stockes,  l ecriture est effetuee
        a la sortie du pipeline (mode streaming)
    '''
    extension = regle.f_sortie.ext
    sorties = regle.stock_param.sorties

    if obj.ident == regle.dident:
        ressource = regle.ressource
    else:
        if obj.virtuel:
            return
        groupe, classe = obj.ident
        rep_sortie = regle.getvar('_sortie') if rep_sortie is None else rep_sortie
        if regle.fanout == 'no':
            nom = sorties.get_id(rep_sortie, 'defaut', '', extension)
        elif regle.fanout == 'groupe':
            nom = sorties.get_id(rep_sortie, groupe, '', extension)
        else:
            nom = sorties.get_id(rep_sortie, groupe, classe, extension)
        ressource = sorties.get_res(regle.numero, nom)
#        print ('gdal: recup ressource',ressource, nom, regle.fanout, groupe)


        if ressource is None:
            if os.path.dirname(nom):
                os.makedirs(os.path.dirname(nom), exist_ok=True)
#            print ('ascstr:creation liste',attributs)
            streamwriter = GdalWriter(nom,
                                      converter=gdalconverter,
                                      encoding=regle.stock_param.get_param('codec_sortie', 'utf-8'),
                                      f_sortie=regle.f_sortie, schema=obj.schema,
                                      liste_fich=regle.stock_param.liste_fich,
                                      liste_att=attributs, layer=classe,
                                      srid=obj.geom_v.srid)
            ressource = sorties.creres(regle.numero, nom, streamwriter)
#            print ('nouv ressource', regle.numero,nom,ressource.handler.nom)
        regle.ressource = ressource
        regle.dident = obj.ident
#    print ("fichier de sortie ",fich.nom)
    obj.initgeom()

    if obj.geom_v.type != '0':
#                    print (obj.schema.multigeom,obj.schema.info["type_geom"])
#        obj.geom_v.force_multi = obj.schema.multigeom or obj.schema.info['courbe']
        obj.geom_v.force_multi = True
#    print ('gdal: ecriture objet',obj)
#    print ('gdal: ecriture objet',obj.__geo_interface__)
    try:
        ressource.write(obj, regle.numero)
    except Exception as err:
        print('erreur gdal:', err, ' ecriture objet', obj.__geo_interface__)
        raise

    if final:
        print('gdal:final', regle.stock_param.liste_fich)
        ressource.finalise()


def ecrire_objets(self, regle, _, attributs=None, rep_sortie=None):
    '''ecrit un ensemble de fichiers a partir d'un stockage memoire ou temporaire'''
    #ng, nf = 0, 0
    #memoire = defs.stockage
#    raise
    rep_sortie = regle.getvar('_sortie') if rep_sortie is None else rep_sortie
    print("gdalio:ecriture_objets", rep_sortie)

#    extension = regle.f_sortie.ext
    regle.fanout = regle.fanout if regle.f_sortie.multiclasse else 'classe'
    #groupes = memoire.keys()
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):
            self.ecrire_objets_stream(obj, regle, None, attributs=attributs,
                                      rep_sortie=rep_sortie)


#def asc_streamer(obj, groupe, rep_sortie, regle, final, attributs=None,
#                 racine=''):

#                       reader,      geom,    hasschema,  auxfiles
READERS = {'dxf':(lire_objets, None, True, ()),
           'shp':(lire_objets, None, True, ('dbf', 'prj', 'shx', 'cpg')),
           'mif':(lire_objets, None, True, (('mid', ))),
           'gpkg':(lire_objets, None, True, ())}

# writer, streamer, force_schema, casse, attlen, driver, fanout, geom, tmp_geom)
WRITERS = {'shp':(ecrire_objets, gdalstreamer, True, 'up', 10,
                  'ESRI Shapefile', 'classe', None, '#tmp'),
           'mif':(ecrire_objets, gdalstreamer, True, '', 0,
                  'MapInfo File', 'classe', None, '#tmp'),
           'dxf':(ecrire_objets, gdalstreamer, True, '', 0,
                  'DXF', 'classe', None, '#tmp'),
           'gpkg':(ecrire_objets, gdalstreamer, True, '', 0,
                   'GPKG', 'all', None, '#tmp')}




#########################################################################
