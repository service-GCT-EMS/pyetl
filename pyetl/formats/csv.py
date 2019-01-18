# -*- coding: utf-8 -*-
# formats d'entree sortie
'''gestion des formats d'entree et de sortie.
    actuellement les formats suivants sont supportes
    asc entree et sortie
    postgis text entree (a finaliser) et sortie
    csv entree et sortie
    shape entree et sortie
'''


import os
import re
#from numba import jit
from .interne.objet import Objet
from .fileio import FileWriter


TOKEN_SPECIFICATION = [('N', r'-?\d+(\.\d*)?'),  # Integer or decimal number
                       ('E', r'\)|;'),            # Statement terminator
                       ('C', r'[A-Z]* *\('),    # Identifiers
                       ('S', r','),
                       ('P', r'SRID='),
                       ('K', r'[ \t]+|\n'),       # Skip over spaces and tabs
                       ('M', r'.')]            # Any other character
TOK_REGEX = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION))
KEYWORDS = {"MULTISURFACE(":"3", "MULTIPOLYGON(":"3", "POLYGON(":"3", "CURVEPOLYGON(":"3",
            "MULTILINESTRING(":"2", "MULTICURVE(":"2", "COMPOUNDCURVE(":"2",
            "CIRCULARSTRING(":"2", "LINESTRING(":"2", "POINT(":'1', "(":'0',
            "TIN(":"4", "POLYHEDRALSURFACE(":"5"}

def decode_ewkt(code):
    """ decodage du format ewkt avec expressions regulieres"""
    value = []
    liste = []
    zdef = [0.0]
    entite = ''
    dim = 2
    for token in TOK_REGEX.finditer(code):
        kind = token.lastgroup
        if kind == 'N':
            value.append(float(token.group(kind)))
#        elif kind == 'K':
#            pass
        elif kind == 'M':
            raise RuntimeError('%r unexpected on line %s' % (token.group(kind), code))
        elif kind == 'S':
            if value:
                liste.append(value if dim == 3 else value+zdef)
                value = []
        elif kind == 'E':
            if value:
                liste.append(value if dim == 3 else value+zdef)
                value = []
            yield ('end', entite, dim, liste)
            entite = ''
            liste = []
        elif kind == 'C':
            entite = token.group(kind).replace(' ', '')
            if 'Z' in entite:
                entite = entite.replace('Z', '')
                dim = 3
            liste = []
            if entite not in KEYWORDS:
                raise RuntimeError('%r inconnu' % (entite))
            yield ('start', entite, dim, liste)
        elif kind == 'P':
            entite = 'SRID'





def _parse_start(nature, niveau, poly, ring, nbring):
    """demarre un nouvel element"""
    type_geom = '0'
    try:
        tyg = KEYWORDS[nature]
    except KeyError:
        print('------------type geometrique inconnu', nature)
        return '0', None, None, None
    if tyg == '1':
        return '1', None, None, None
    if nature in {"POLYGON(", "CURVEPOLYGON("}:
        type_geom = '3'
        poly = niveau
    elif nature == "COMPOUNDCURVE(":
        if niveau == 1:
            type_geom = '2'
        elif poly:
            ring = niveau
            nbring += 1
    elif nature == "CIRCULARSTRING(":
        if niveau == 1:
            type_geom = '2'
        elif poly and not ring:
            ring = niveau
            nbring += 1
    elif nature == "(":
        if poly and not ring:
            ring = niveau
    else:
        type_geom = tyg
    return type_geom, poly, ring, nbring



def _parse_end(nature, valeurs, dim, nbring, niveau, geometrie):
    '''finalise l'element'''
    if nature == 'POINT(':
        geometrie.setpoint(valeurs[0], 0, dim)
#                    print ('detecte point ',valeurs[0], 0, dim)
    elif nature == '(':
        geometrie.cree_section(valeurs, dim, 1, 0, interieur=nbring > 1)
    elif nature == 'LINESTRING(':
        geometrie.cree_section(valeurs, dim, 1, 0, interieur=nbring > 1)
    elif nature == 'CIRCULARSTRING(':
        geometrie.cree_section(valeurs, dim, 1, 1, interieur=nbring > 1)
    elif nature == 'SRID':
        niveau += 1 # on compense
        geometrie.setsrid(valeurs[0][0])



def _parse_ewkt(geometrie, texte):
    '''convertit une geometrie ewkt en geometrie interne'''
    dim = 2
    niveau = 0
    poly = 0
    ring = 0
    nbring = 0
    type_lu = None
    if not isinstance(texte, str):
        print('geometrie non decodable', texte)
        geometrie.type = '0'
        return
    try:
        for oper, nature, dim, valeurs in decode_ewkt(texte.upper()):
            if oper == "end":
                if poly == niveau:
                    poly = 0
                    nbring = 0
                elif ring == niveau:
                    ring = 0
                niveau -= 1

                _parse_end(nature, valeurs, dim, nbring, niveau, geometrie)

            elif oper == 'start':
                dim = valeurs
                niveau += 1
                type_lu, poly, ring, nbring = _parse_start(nature, niveau, poly, ring, nbring)
                geometrie.type = type_lu
#                if not type_geom:
#                    print ('erreur decodage', texte, oper, nature, valeurs)
    except RuntimeError:
        print('erreur decodage geometrie', texte)



def geom_from_ewkt(obj):
    '''convertit une geometrie ewkt en geometrie interne'''
    if obj.geom:
        geom_demandee = obj.schema.info["type_geom"] if obj.schema else '0'
#        print ('decodage geometrie ewkt ',obj.geom)
        _parse_ewkt(obj.geom_v, obj.geom[0])
        obj.finalise_geom(type_geom=geom_demandee)
    return obj.geom_v.valide




def _ecrire_coord_ewkt2d(pnt):
    '''ecrit un point en 2D'''
    return '%f %f'% (pnt[0], pnt[1])

def _ecrire_coord_ewkt3d(pnt):
    '''ecrit un point en 3D'''
    return  '%f %f %f' % (pnt[0], pnt[1], pnt[2])

def ecrire_coord_ewkt(dim):
    ''' retourne la fonction d'ecriture adequate'''
    return _ecrire_coord_ewkt2d if dim == 2 else _ecrire_coord_ewkt3d

def _ecrire_point_ewkt(point):
    '''ecrit un point'''
    if point.coords:
        return "POINT("+_ecrire_coord_ewkt2d(point.coords[0])+")" if point.dimension == 2\
                else "POINT("+ _ecrire_coord_ewkt3d(point.coords[0])+")"
    return ''

def _ecrire_section_simple_ewkt(section):
    '''ecrit une section '''
    prefix = '('
    ecrire = ecrire_coord_ewkt(section.dimension)
    return prefix+",".join([ecrire(i) for i in section.coords])+")"



def _ecrire_section_ewkt(section, poly):
    '''ecrit une section '''
    if section.courbe:
        prefix = "CIRCULARSTRING("
    elif poly:
        prefix = '('
    else:
        prefix = "LINESTRING("
    ecrire = ecrire_coord_ewkt(section.dimension)
#    print('coords objet ')
#    for i,j in enumerate(section.coords):
#        print(i,j)
#    print([i  for i in section.coords])
    return prefix+",".join([ecrire(i) for i in section.coords])+")"


def _ecrire_ligne_ewkt(ligne, poly, erreurs, multiline=False):
    '''ecrit une ligne en ewkt'''
    if poly and not ligne.ferme:
        erreurs.ajout_erreur("ligne non fermee")
        return ''
    if not ligne.sections:
        erreurs.ajout_erreur("ligne vide")
        return ''
    sec2 = [ligne.sections[0]]
    if sec2[0].courbe == 3:
        #print ("cercle")
        sec2[0].conversion_diametre()   # c' est un cercle# on modifie la description
    else:
        #print ('fusion sections',len(ligne.sections))
        for sect_courante in ligne.sections[1:]: # on fusionne ce qui doit l'etre
            if sect_courante.courbe == sec2[-1].courbe:
#                print ('fusion ',sect_courante.courbe,sec2[-1].courbe)
                sec2[-1].fusion(sect_courante)
            else:
#                print ('ajout ',sect_courante.courbe,sec2[-1].courbe)
                sec2.append(sect_courante)
    if len(sec2) > 1:
        return "COMPOUNDCURVE(" + ",".join((_ecrire_section_ewkt(i, False)
                                            for i in sec2))+")"
    return _ecrire_section_ewkt(sec2[0], poly or multiline)

def _ecrire_multiligne_ewkt(lignes, courbe, erreurs, force_courbe=False):
    '''ecrit une multiligne en ewkt'''
    #courbe=True # test courbes
    code = "MULTICURVE(" if courbe or force_courbe else "MULTILINESTRING("
    return code +",".join((_ecrire_ligne_ewkt(i, False, erreurs, True)
                           for i in lignes)) +')'

def _ecrire_polygone_ewkt(polygone, courbe, erreurs, multi=False, force_courbe=False):
    '''ecrit un polygone en ewkt'''
    if courbe or force_courbe:
        code = "CURVEPOLYGON("
    elif  multi:
        code = "("
    else:
        code = "POLYGON("
    return code + ",".join((_ecrire_ligne_ewkt(i, True, erreurs, False)
                            for i in polygone.lignes))+')'

def _ecrire_poly_tin(polygones, tin, _):
    """ecrit un tin en ewkt ne gere pas les erreurs """
    if tin:
        code = "TIN("
    else:
        code = "POLYHEDRALSURFACE("

    return code + ",".join((_ecrire_section_simple_ewkt(i.lignes[0].sections[0])
                            for i in polygones))+')'


def _ecrire_multipolygone_ewkt(polygones, courbe, erreurs, force_courbe):
    '''ecrit un multipolygone en ewkt'''
    #print 'dans ecrire_polygone',len(polygones)
    #courbe=True # test courbes
    code = "MULTISURFACE(" if courbe or force_courbe else "MULTIPOLYGON("
    return code + ",".join((_ecrire_polygone_ewkt(i, courbe, erreurs, True)
                            for i in polygones))+')'

def _erreurs_type_geom(type_geom, geometrie_demandee, erreurs):
    if geometrie_demandee != type_geom:
        if type_geom == 1 or geometrie_demandee == 1:
            erreurs.ajout_erreur("fmt:geometrie_incompatible: demande "+
                                 str(type(geometrie_demandee))+str(geometrie_demandee)+
                                 " existante: "+str(type_geom)+str(type(type_geom)))
            return 1
        if type_geom == 2:
            erreurs.ajout_erreur("fmt:la geometrie n'est pas un polygone demande " +
                                 str(geometrie_demandee) + " existante: " + str(type_geom))
#            raise
            return 1
    else:
        return 0

def ecrire_geom_ewkt(geom, geometrie_demandee, multiple, erreurs, force_courbe=False):
    '''ecrit une geometrie en ewkt'''

    if geometrie_demandee == "0" or geom.type == '0' or geom.null:
        return None

    geomt = ''
    type_geom = geom.type
    geometrie_demandee = geometrie_demandee if geometrie_demandee != '-1' else geom.type

    if _erreurs_type_geom(type_geom, geometrie_demandee, erreurs):
        return None
    courbe = geom.courbe
    if geometrie_demandee == '1':
        geomt = _ecrire_point_ewkt(geom.point)
    elif geometrie_demandee == '2':
        if geom.lignes:
            geomt = _ecrire_multiligne_ewkt(geom.lignes, courbe, erreurs) if multiple\
                    else _ecrire_ligne_ewkt(geom.lignes[0], False, erreurs)
        else:
            erreurs.ajout_erreur("pas de geometrie ligne")
            return None
    elif geometrie_demandee == '3':
        if geom.polygones:
            geomt = _ecrire_multipolygone_ewkt(geom.polygones, courbe, erreurs,
                                               force_courbe) if multiple\
                    else _ecrire_polygone_ewkt(geom.polygones[0], courbe, erreurs,
                                               False, force_courbe)
        else:
            erreurs.ajout_erreur("polygone non ferme")
            return None

    elif geometrie_demandee > '3': # 4: tin  5: polyhedralsurface
        geomt = _ecrire_poly_tin(geom.polygones, geometrie_demandee == '4', erreurs)

    else:
        print("ecrire ewkt geometrie inconnue", geometrie_demandee)
    return geom.epsg+geomt if geomt else None

#format sqlloader===========================================================



#########################################################################
# format csv et txt geo etc
# tous les fichiers tabules avec ou sans entete
#########################################################################
def getnoms(rep, chemin, fichier):
    """ determine les noms de groupe et de schema"""
    schema = ["schema"]
    chem = chemin
    niveaux = []
    classe = os.path.splitext(fichier)[0]
    if rep and rep != ".":
        schema = os.path.basename(rep)
    while chem:
        chem, nom = os.path.split(chem)
        niveaux.append(nom)

    if not niveaux:
        groupe = ''
    else:
        groupe = "_".join(niveaux)
#    print(rep, "<>", chemin, "<>", fichier, "traitement", schema, "<>", groupe, "<>", classe)
    return schema, groupe, classe



def decode_entetes_csv(nom_schema, nom_groupe, nom_classe, stock_param, entete, separ):
    '''prepare l'entete et les noma d'un fichier csv'''

    geom = False


    schema_courant = stock_param.schemas.get(stock_param.get_param("schema_entree"))

#    print('decodage entete csv',schema_courant.nom if schema_courant else '' ,entete)

    if schema_courant:
        nom_groupe, nom_classe = schema_courant.map_dest((nom_groupe, nom_classe))
    else:
        schema_courant = stock_param.init_schema(nom_schema, 'F')

    if (nom_groupe, nom_classe) in schema_courant.classes:
        schemaclasse = schema_courant.classes[(nom_groupe, nom_classe)]
        noms_attributs = schemaclasse.get_liste_attributs()
        geom = schemaclasse.info["type_geom"] != "0"
    else:
        schemaclasse = schema_courant.setdefault_classe((nom_groupe, nom_classe))

        noms_attributs = [i.lower().strip().replace(' ', '_') for i in entete.split(separ)]
        # on verifie que les noms existent et sont uniques
        noms = set()

        for i, nom in enumerate(noms_attributs):
            if not nom:
                noms_attributs[i] = '#champs_'+str(i)
            if nom in noms:
                noms_attributs[i] = nom+'_'+str(i)
            noms.add(noms_attributs[i])


        if noms_attributs[-1] == 'tgeom' or noms_attributs[-1] == 'geometrie':
            geom = True
            noms_attributs.pop(-1) # on supprime la geom en attribut classique
        for i in noms_attributs:
            if i[0] != '#':
                schemaclasse.stocke_attribut(i, 'T')
#    else: # on adapte le schema force pur eviter les incoherences
#        schemaclasse.adapte_schema_classe(noms_attributs)

    return nom_groupe, nom_classe, noms_attributs, geom, schemaclasse


def _controle_nb_champs(val_attributs, controle, nbwarn, ligne):
    ''' ajuste le nombre de champs lus '''
    if len(val_attributs) < controle:
        val_attributs.extend(['']*controle)
    else:
        nbwarn += 1
        if nbwarn < 10:
            print('warning: csv  : erreur format csv : nombre de valeurs incorrect',
                  len(val_attributs), 'au lieu de', controle, ligne[:-1], val_attributs)
    return nbwarn



def lire_objets_csv(rep, chemin, fichier, stock_param, regle, entete=None, separ=None):
    '''lit des objets a partir d'un fichier csv'''
    if separ is None:
        separ = stock_param.get_param('separ_csv_in', stock_param.get_param('separ_csv', ';'))
#    print('lecture_csv:', rep, chemin, fichier,separ)
    maxobj = stock_param.get_param('lire_maxi', 0)
    nom_schema, nom_groupe, nom_classe = getnoms(rep, chemin, fichier)
    with open(os.path.join(rep, chemin, fichier), "r",
              encoding=stock_param.get_param('codec_entree', 'utf-8')) as fich:

        if not entete:
            entete = fich.readline()[:-1] # si l'entete n'est pas fourni on le lit dans le fichier
            if entete[0] == '!':
                entete = entete[1:]
            else: # il faut l'inventer...
                entete = separ*len(fich.readline()[:-1].split(separ))
                fich.seek(0) # on remet le fichier au debut

        nom_groupe, nom_classe, noms_attributs, geom, schemaclasse =\
            decode_entetes_csv(nom_schema, nom_groupe, nom_classe, stock_param, entete, separ)
        controle = len(noms_attributs)
        nbwarn = 0
        nlignes = 0
        for i in fich:
            nlignes = nlignes+1
            obj = Objet(nom_groupe, nom_classe, format_natif='csv', conversion=geom_from_ewkt)
            obj.setschema(schemaclasse)
            obj.setorig(nlignes)
            val_attributs = [j.strip() for j in i[:-1].split(separ)]
            #liste_attributs = zip(noms_attributs, val_attributs)
            #print ('lecture_csv:',[i for i in liste_attributs])
            if len(val_attributs) != controle:
                nbwarn = _controle_nb_champs(val_attributs, controle, nbwarn, i)

            obj.attributs.update(zip(noms_attributs, val_attributs))
            #print ('attributs:',obj.attributs['nombre_de_servitudes'])
            if geom:
                obj.geom = [val_attributs[-1]]
#                print ('geometrie',obj.geom)
                obj.attributs['#type_geom'] = '-1'
            else:
                obj.attributs['#type_geom'] = '0'
            obj.attributs['#chemin'] = chemin
            stock_param.moteur.traite_objet(obj, regle)

            if maxobj and nlignes >= maxobj: # nombre maxi d'objets a lire par fichier
                break

            if nlignes % 100000 == 0:
                stock_param.aff.send(('interm', 0, nlignes)) # gestion des affichages de patience

        if nbwarn:
            print(nbwarn, "lignes avec un nombre d'attributs incorrect")
    return nlignes

class CsvWriter(FileWriter):
    """ gestionnaire des fichiers csv en sortie """
    def __init__(self, nom, schema, extension, separ, entete, encoding='utf-8',
                 liste_fich=None, null='', f_sortie=None):

        super().__init__(nom, encoding=encoding, liste_fich=liste_fich, schema=schema, f_sortie=f_sortie)

        self.extension = extension
        self.separ = separ
        self.nom = nom
        self.schema = schema

        self.entete = entete
        self.null = null
        self.classes = set()
        if schema:
#            print ('writer',nom, schema.schema.init, schema.info['type_geom'])
            if schema.info['type_geom'] == 'indef':
                schema.info['type_geom'] = '0'
            self.type_geom = self.schema.info["type_geom"]
            self.multi = self.schema.multigeom
            self.liste_att = schema.get_liste_attributs()
            self.force_courbe = self.schema.info["courbe"]
        else:
            print("attention csvwriter a besoin d'un schema", self.nom)
            raise ValueError("csvwriter: schema manquant")
        self.escape = '\\'+separ
        self.repl = '\\'+self.escape
        self.fichier = None
        self.stats = liste_fich if liste_fich is not None else dict()
        self.encoding = encoding
        self.transtable = str.maketrans({'\\':r'\\', '\n':'\\'+'n', '\r':'\\'+'n',
                                         self.separ:self.escape})

    def header(self, init=1):
        ''' preparation de l'entete du fichiersr csv'''
        if not self.entete:
            return ''
        geom = self.separ+"geometrie"+"\n" if self.schema.info["type_geom"] != '0' else "\n"
        return '!'+self.separ.join(self.liste_att)+geom


    def write(self, obj):
        '''ecrit un objet'''
        if obj.virtuel:
            return False#  les objets virtuels ne sont pas sortis

        atlist = (str(obj.attributs.get(i, '')).translate(self.transtable) for i in self.liste_att)
#        print ('ectriture_csv',self.schema.type_geom, obj.format_natif,
#                obj.geomnatif, obj.type_geom)
#        print ('orig',obj.attributs)
        attributs = self.separ.join((i if i else self.null for i in atlist))
        if self.type_geom != '0':
            if obj.format_natif == "#ewkt" and obj.geomnatif: # on a pas change la geometrie
                geom = obj.geom[0] if obj.geom else self.null# on recupere la geometrie native
#                print("sortie ewkt geom0",len(geom))
            else:
                if obj.initgeom():
                    geom = ecrire_geom_ewkt(obj.geom_v, self.type_geom, self.multi, obj.erreurs)
                else:
                    if not obj.geom and self.type_geom == '-1':
                        geom = ''
                    else:
                        print('csv: geometrie invalide : erreur geometrique',
                              obj.ident, obj.numobj, 'demandé:', self.type_geom,
                              obj.geom_v.erreurs.errs, obj.attributs['#type_geom'],
                              self.schema.info["type_geom"], obj.geom)
                        geom = ""

                obj.format_natif = "#ewkt"
                obj.geom = geom
                obj.geomnatif = True
                if obj.erreurs and obj.erreurs.actif == 2:
                    print('error: writer csv :', obj.ident, obj.ido, 'erreur geometrique: type',
                          obj.attributs['#type_geom'], 'demandé:',
                          obj.schema.info["type_geom"], obj.erreurs.errs)
                    return False
#            print ('prep ligne ', attributs,'G:', geom)
            if not geom:
                geom = self.null
            ligne = attributs+self.separ+geom
        else:
            ligne = attributs
        if self.writerparms.get('nodata'):
            return False

#        print("sortie ewkt",len(geom))

        self.fichier.write(ligne)
        self.fichier.write('\n')
        self.stats[self.nom] += 1
        return True


class SqlWriter(CsvWriter):
    """getionnaire decriture sql en fichier"""
    def __init__(self, nom, schema, extension, separ, entete, encoding='utf-8',
                 liste_fich=None, null='', f_sortie=None):
        super().__init__(nom, schema, extension, separ, entete, encoding,
                         liste_fich, null, f_sortie)
        if self.writerparms:
            self.schema.setsortie(self.f_sortie)



    def header(self, init=1):
        separ = ','
        gensql = self.schema.schema.dbsql
        if not gensql:
            print('header sql: erreur generateur sql non defini', self.schema.schema.nom,
                  self.schema.identclasse, self.schema.schema.format_sortie)
            raise StopIteration(3)
        niveau, classe = self.schema.identclasse
        nouveau = self.schema.identclasse not in self.classes
        self.classes.add(self.schema.identclasse)
        prefix = "SET client_encoding = 'UTF8';\n" if init else ''
#        print ('parametres sql ', self.writerparms)
        nodata = False

        type_geom = self.schema.info['type_geom']
        dim = self.schema.info['dimension']

        if self.writerparms and nouveau:
            reinit = self.writerparms.get('reinit')
#            dialecte = self.writerparms.get('dialecte', 'sql')
            nodata = self.writerparms.get('nodata')

            gensql.initschema(self.schema.schema)
            # on positionne les infos de schema pour le generateur sql

            prefix = prefix + gensql.prefix_charge(niveau, classe, reinit,
                                                   gtyp=type_geom, dim=dim)

        if nodata:
            return prefix
        prefix = prefix+'copy "'+niveau.lower()+'"."'+classe.lower()+'" ('
        end = ") FROM stdin;"

        geom = separ+"geometrie"+end+"\n" if self.schema.info["type_geom"] != '0' else end+"\n"
        return prefix+separ.join([gensql.ajuste_nom(i.lower()) for i in self.liste_att])+geom


    def fin_classe(self):
        """fin de classe pour remettre les sequences"""
        reinit = self.writerparms.get('reinit', '0')
        niveau, classe = self.schema.identclasse
        gensql = self.schema.schema.dbsql

        type_geom = self.schema.info['type_geom']
        courbe = self.schema.info['courbe']
        dim = self.schema.info['dimension']
        if not gensql:
            print('finclasse sql: erreur generateur sql non defini', self.schema.identclasse,
                  self.schema.schema.format_sortie)
            raise StopIteration(3)
        if self.writerparms.get('nodata'):
            self.fichier.write(gensql.tail_charge(niveau, classe, reinit))
            return
        self.fichier.write(r'\.'+'\n')

        self.fichier.write(gensql.tail_charge(niveau, classe, reinit,
                                              gtyp=type_geom, dim=dim, courbe=courbe))



    def finalise(self):
        '''ligne de fin de fichier en sql'''
        self.fin_classe()
        self.fichier.close()

    def changeclasse(self, schemaclasse, attributs=None):
        ''' ecriture de sql multiclasse on cree des entetes intermediaires'''
#        print( 'dans changeclasse')
        self.fin_classe()
        self.schema = schemaclasse
        if schemaclasse.info['type_geom'] == 'indef': # pas de geometrie
            schemaclasse.info['type_geom'] = '0'
        self.type_geom = schemaclasse.info["type_geom"]
        self.multi = schemaclasse.multigeom
        self.liste_att = schemaclasse.get_liste_attributs(attributs)
        self.fichier.write(self.header(0))


def getfanout(regle, extention, ident, initial):
    '''determine le mode de fanout'''
    sorties = regle.stock_param.sorties
    rep_sortie = regle.getvar('_sortie')
    groupe, classe = ident
    dest = regle.f_sortie.writerparms.get('destination')
#    print ('dans getfanout ', regle.fanout, regle.f_sortie.fanoutmax, ident, initial,extention, dest, regle.vloc)

    bfich = ''
    if regle.params.cmp2.val:
        nfich = regle.params.cmp2.val
        if nfich == "#print":
            nom = "#print"
            ressource = sorties.get_res(regle.numero, nom)
            return ressource, nom

    if regle.fanout == 'no' and regle.f_sortie.fanoutmax == 'all':
        bfich = dest if dest else 'all'
        nom = sorties.get_id(rep_sortie, bfich, '', extention, nom=dest)
#            print('nom de fichier sans fanout ', rep_sortie, nfich, nom)
    elif regle.fanout == 'groupe' and (regle.f_sortie.fanoutmax == 'all'
                                       or regle.f_sortie.fanoutmax == 'groupe'):
#            print('csv:recherche fichier',obj.ident,groupe,classe,obj.schema.nom,
#            len(obj.schema.attributs))
        nom = sorties.get_id(os.path.join(rep_sortie, bfich), groupe, '', extention, nom=dest)

    else:
        nom = sorties.get_id(os.path.join(rep_sortie, bfich), groupe, classe, extention, nom=dest)

    ressource = sorties.get_res(regle.numero, nom)
#    print('csv:fichier', regle.getvar('_wid'), regle.fanout, rep_sortie, bfich, groupe,nom)
    return ressource, nom





def change_ressource(regle, obj, writer, separ, extention, entete, null, initial=False):
    ''' change la definition de la ressource utilisee si necessaire'''

    ident = obj.ident

    ressource, nom = getfanout(regle, extention, ident, initial)
#    ressource = sorties.get_res(regle.numero, nom)
#    print ('recup_ressource ressource stream csv' , ressource, nom, ident)
#    print ('change_ressoures ', regle.f_sortie.writerparms)
    if ressource is None:
        if separ is None:
            separ = regle.getvar('separ_csv_out', regle.getvar('separ_csv', '|'))
        if not nom.startswith("#"):
#            print('creation ',nom,'rep',os.path.abspath(os.path.dirname(nom)))
            os.makedirs(os.path.dirname(nom), exist_ok=True)
        str_w = writer(nom, obj.schema, extention, separ, entete,
                       encoding=regle.stock_param.get_param('codec_sortie', 'utf-8'),
                       liste_fich=regle.stock_param.liste_fich, null=null,
                       f_sortie=regle.f_sortie)
        ressource = regle.stock_param.sorties.creres(regle.numero, nom, str_w)
    regle.stock_param.set_param('derniere_sortie', nom, parent=1)
    regle.ressource = ressource
    regle.dident = ident
    return ressource



def csvstreamer(obj, regle, _, entete='csv', separ=None,
                extention='.csv', null='',
                writer=CsvWriter): #ecritures non bufferisees
    ''' ecrit des objets csv en streaming'''
#    sorties = regle.stock_param.sorties
    if regle.dident == obj.ident:
        ressource = regle.ressource
    else:
        ressource = change_ressource(regle, obj, writer, separ,
                                     extention, entete, null, initial=True)

    ressource.write(obj, regle.numero)
#    if obj.geom_v.courbe:
#        obj.schema.info['courbe'] = '1'


def ecrire_objets_csv(regle, _, entete='csv', separ=None,
                      extention='.csv', null='',
                      writer=CsvWriter):
    ''' ecrit des objets csv a partir du stockage interne'''
#    sorties = regle.stock_param.sorties
#    numero = regle.numero
    print("csv:ecrire csv", regle.stockage.keys())

    for groupe in list(regle.stockage.keys()):
        # on determine le schema
        print("csv:ecrire groupe", groupe)

        for obj in regle.recupobjets(groupe):
#            print("csv:ecrire csv", obj)
#            print( regle.stockage)
#            groupe, classe = obj.ident
            if obj.ident != regle.dident:
                ressource = change_ressource(regle, obj, writer,
                                             separ, extention, entete, null, initial=False)

            ressource.write(obj, regle.numero)

#            if obj.geom_v.courbe:
#                obj.schema.info['courbe'] = '1'
    return


def ecrire_objets_txt(regle, final):
    '''format txt (csv sans entete) pour postgis'''
    return ecrire_objets_csv(regle, final, False, '\t', '.txt')

def lire_objets_txt(rep, chemin, fichier, tdr, regle, schema=None):
    '''format sans entete le schema doit etre fourni par ailleurs'''
    separ = tdr.get_param('separ_txt_in', tdr.get_param('separ_txt', '\t'))
    if schema:
        geom = separ+"geometrie"+"\n" if schema.info["type_geom"] else "\n"
        entete = separ.join(schema.get_liste_attributs())+geom
    else:
        entete = []
    return lire_objets_csv(rep, chemin, fichier, tdr, regle, entete, separ=separ)


def txtstreamer(obj, regle, final):
    '''format txt en straming'''
    return csvstreamer(obj, regle, final, False, '\t', '.txt')

def ecrire_objets_geo(regle, final):
    '''geodatabase pour les outils topo'''
    return ecrire_objets_csv(regle, final, False, '  ', '.geo')

def ecrire_objets_sql(regle, final):
    '''format sql copy pour postgis'''

    return ecrire_objets_csv(regle, final, 'sql', '\t', '.sql',
                             null=r'\N', writer=SqlWriter)

def sqlstreamer(obj, regle, final):
    '''format sql copy pour postgis en streaming '''

    return csvstreamer(obj, regle, final, 'sql', '\t',
                       '.sql', null=r'\N', writer=SqlWriter)
