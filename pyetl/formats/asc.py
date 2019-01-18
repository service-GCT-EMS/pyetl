# -*- coding: utf-8 -*-
''' format asc en lecture et ectiture'''

import os
#import time
#from numba import jit
import logging
from .interne.objet import Objet
from .fileio import FileWriter
#import pyetl.schema as SC


# formats geometriques ######
FC = 1000. # ajoute les elements d'entete a un objet
FA = 10.
LOGGER = logging.getLogger('pyetl')

# asc ###################################################################
def _ecrire_section_asc(sect, numero_courant):
    '''ecrit une section en format asc'''
    num_sect = numero_courant[0]
    numero_courant[0] += 1
    if sect.dimension == 2:
        return "1SEC %d, %d, \n"%(num_sect, len(sect.coords))+\
        "\n".join(("%d,  %d, " % (i[0]*FC, i[1]*FC) for i in sect.coords))+\
        " %d,  %d;\n" % (sect.couleur, sect.courbe)
    return "1SEC3D %d, %d, \n"%(num_sect, len(sect.coords))+\
    "\n".join(("%d,  %d,  %d, " % (i[0]*FC, i[1]*FC, i[2]*FC)
               for i in sect.coords))+\
    " %d,  %d;\n" % (sect.couleur, sect.courbe)

def _ecrire_ligne_asc(ligne, numero_courant):
    '''ecrit une ligne en format asc.
        : suite de sections'''
    return "".join((_ecrire_section_asc(i, numero_courant) for i in ligne.sections))

def ecrire_geom_asc(geom):
    '''ecrit une geometrie en format asc.
        : suite de lignes '''
#    print ('asc: nblignes',len(geom.lignes))
    return "".join((_ecrire_ligne_asc(p, [1]) for p in geom.lignes)) if geom.valide else ''

def _get_point(attrib, geometrie):
    '''recupere une geometrie de point depuis les attributs'''
    cd_x = attrib.get("#x", 0)
    cd_y = attrib.get("#y", 0)
    cd_z = attrib.get("#z", 0)
    dim = int(attrib.get('#dimension', '0'))
    if not dim:
        if cd_x and cd_y:
            dim = 2
        if cd_z:
            dim = 3
    if dim:
        geometrie.setpoint([float(cd_x), float(cd_y), float(cd_z)],
                           float(attrib.get("#angle", 0)), int(dim))
    return dim


def geom_from_asc(obj):
    '''convertit une geometrie asc en format interne.'''
#    print ('conversion geometrie asc',obj.ido,obj.geom)
    if obj.geom_v.type == '1': # c'est un point on a deja ce qu il faut
        obj.infogeom()
        return True

    geom_demandee = '-1'
# s'il y a un schema : on force le type de geometrie demandees
    if obj.schema and obj.schema.schema.origine != 'B':
        geom_demandee = obj.schema.info["type_geom"]
#    print('gfa: geom_demandee',geom_demandee)
    geom_v = obj.geom_v
    dim = 2
    if not obj.geom:
        if obj.attributs['#type_geom'] == '0':
            return True
        geom_v.erreurs.ajout_erreur('objet_sans_geometrie')
        obj.attributs.update([('#type_geom', '0'), ('#dimension', '2')])
        return False

    for pnt in obj.geom:
        if pnt.startswith('1SEC'):
            dim = 3 if pnt.find("3D") > 0 else 2
            coords = []
        else: # on est en presence de coordonnees
            lcrd = pnt.split(",")
            try:
                coord_points = [float(lcrd[0])/FC, float(lcrd[1])/FC,
                                float(lcrd[2])/FC if dim == 3 else 0]

                coords.append(coord_points)
            except ValueError:
                geom_v.erreurs.ajout_erreur('coordonnees incompatibles '+str(pnt))
                print('error: asc  : coordonnees incompatibles ', pnt)
                geom_v.type = '0'
            if len(lcrd) > dim+1: # fin de ligne
                #print l
                try:
                    couleur = int(lcrd[dim])
                    if couleur != 500:
                        courbe = int(lcrd[1+dim].replace(";\n", ''))
                        geom_v.cree_section(coords, dim, couleur, courbe)
#                            geom_v.fin_section(couleur, courbe)
#                        else: geom_v.annule_section()
#                    except ImportError:
                except ValueError:
                    geom_v.erreurs.ajout_erreur('valeurs incompatibles '+str(pnt))
                    print('error: asc  : valeurs incompatibles ', lcrd)
                    geom_v.annule_section()
#    print ("asc:finalisation geom", geom_demandee)
    obj.finalise_geom(orientation='L', type_geom=geom_demandee)

    geom_v.valide = geom_v.erreurs.actif < 2
    return geom_v.valide


# formats complets
####################################################################################
#### traitement  format asc
####################################################################################

def _decode_dates_apic(chaine):
    ''' decode une date au format apic'''
    dates = chaine.split(",")

    if len(dates) == 4:
        dat_cre = " ".join(dates[:2]).strip()
        dat_mod = " ".join(dates[2:4]).strip()
    elif len(dates) == 3: # une seuele date
        if dates[0] == "":
            dat_cre = ''
            dat_mod = " ".join(dates[1:2]).strip()
        else:
            dat_cre = " ".join(dates[:2]).strip()
            dat_mod = ''
    elif len(dates) == 2: # une seule date partielle
        if dates[0] == "":
            dat_cre = ''
            dat_mod = dates[1].strip()
        else:
            if ':' in dates[1]:
                dat_cre = " ".join(dates[:2]).strip()
                dat_mod = ''
            else:
                dat_cre = dates[0].strip()
                dat_mod = dates[1].strip()
    else:
        dat_cre = ""
        dat_mod = ""

    return dat_cre, dat_mod


def _point_apic(obj, liste_elt, log_erreurs):
    '''positionne une geometrie de point et des parties d'entete '''
    types_geom = {'3':'1', '5':'0', '6':'1', '9':'2'}
    type_geom = '0'
    dim = '2'
    angle = '0'

    type_geom_asc = liste_elt[0][0]
    classe = liste_elt[1].strip()
    index = liste_elt[2].strip()
    _, oclasse = obj.ident
    if classe != oclasse: # on est en mode multiclasse
        obj.setident((oclasse, classe))

    try:
        type_geom = types_geom[type_geom_asc]
        obj.geomnatif = False
        if type_geom_asc == '3':
            cd_x, cd_y = float(liste_elt[3])/FC, float(liste_elt[4])/FC
            angle = 90-round(float(liste_elt[5])/FA, 1)
            obj.geom_v.setpoint([cd_x, cd_y, 0], angle, 2)

        elif type_geom_asc == '6':
            cd_x, cd_y = float(liste_elt[3])/FC, float(liste_elt[4])/FC
            cd_z = float(liste_elt[5])/FC
            angle = 90-round(float(liste_elt[6])/FA, 1) # point 3D
            obj.geom_v.setpoint([cd_x, cd_y, cd_z], angle, 3)
            dim = '3'
    except ValueError:
        obj.attributs["#erreurs"] = 'erreur lecture entete'
        log_erreurs.send(obj.ident)
    return index, type_geom, dim, angle



def _decode_entete_asc(obj, entete, log_erreurs):
    '''decode un point dans l'entete apic'''
    liste1 = entete.split(";")
    liste_elt = liste1[1].split(",")
    gid = liste_elt[0][2:].strip() # gid
    if len(liste_elt) < 3:
        print('asc:erreur point ', liste1[0])

    index, type_geom, dim, angle = _point_apic(obj, liste_elt, log_erreurs)
    dat_cre, dat_mod = _decode_dates_apic(liste1[2])

    obj.attributs.update([("#gid", gid), ("#clef", index), ('#type_geom', type_geom),
                          ('#dimension', dim), ("#_sys_date_cre", dat_cre),
                          ("#_sys_date_mod", dat_mod),
                          ("#complement", ";".join(liste1[3:-1])),
                          ("#angle", str(angle))
                         ])


def _erreurs_entete():
    '''cumul des erreurs d'entete et affichage'''
    classe_courante = ''
#    classe='1'
    nb_err = 0
    while True:
        classe = yield
        if classe_courante and classe_courante != classe:
            LOGGER.error('asc  : erreurs entetes : '+str(nb_err)+' sur la classe '+ classe_courante)
#            print('error: asc  : erreurs entetes :', nb_err, 'sur la classe ', classe_courante)
            nb_err = 0
            classe_courante = classe
        nb_err += 1
    return



    #print obj.attributs
# entree sortie en asc
#@jit
def ajout_attribut_asc(obj, attr):
    '''decodage d'un attribut asc et stockage'''
    code = attr[0]
    suite = False
    liste_elts = attr.split(",", 2)  # les 2 premiers suffisent en general
    nom = liste_elts[0][1:]
    if obj.schema:
        if nom in obj.schema.attmap:
            nom = obj.schema.attmap[nom].nom
        elif nom not in obj.schema.attributs:
            if obj.schema.schema.origine == 'B': # c'est un schema autogenere
                obj.schema.stocke_attribut(nom, 'A')
            else:
                nom = '#'+nom
    if code == '2':
        code_att = liste_elts[1][0:2]
        long_attrib = int(liste_elts[1][2:])
        if code_att == "NG":
            #vl = ', '.join(l[2:])
            vatt = liste_elts[2][0:long_attrib]
            suite = (len(vatt) < long_attrib)

        elif code_att == "TL":
            obj.text_graph[liste_elts[0][1:]] = liste_elts[2:-1]#texte_graphique
            nom_x = nom+"_X"
            nom_y = nom+"_Y"
            obj.tg_coords[nom_x] = 1
            obj.tg_coords[nom_y] = 1
            liste_elts = attr.split(",") #d on decode plus loin
#            try:
            obj.attributs[nom_x] = str(float(liste_elts[2])/FC)
            obj.attributs[nom_y] = str(float(liste_elts[3])/FC)
#            except ValueError:
#                print("error: asc  : texte graphique incorrect", liste_elts)
            texte_candidat = ','.join(liste_elts[7:])
            vatt = texte_candidat[0:long_attrib]
        elif code_att == "CT": # texte symbolique (recupere en texte)
            liste_elts = attr.split(",") #d on decode plus loin
            vatt = liste_elts[6]
        else:
            print("error: asc  : lecture_asc code inconnu ", code_att, attr)
    elif code == '4':
#        print('detection code etat ', obj.ident, liste_elts)
        if obj.etats is None:
            obj.etats = dict()
        obj.etats[liste_elts[0][1:]] = liste_elts[1][:-1] # code etat
        vatt = liste_elts[1][:-1]
        nom = '#_sys_E_'+liste_elts[0][1:]
    else:
        print("error: asc  : code inconnu", liste_elts)

    obj.attributs[nom] = vatt
    return nom, suite
    #print l, l[-1].strip()
    #print 1/0

def complete_attribut(obj, nom, chaine):
    '''ajoute une ligne a un attribut'''
    obj.attributs[nom] += chaine
    return nom, False


def _finalise(obj, schema_init, schema, numero, chemin):
    ''' finalise un objet avant de l'envoyer '''
    if obj.attributs['#type_geom'] != '1': #pour les points c 'est deja fait
        if obj.geom:
            obj.nogeom = False
            obj.attributs['#dimension'] = '3' if obj.geom[0].find("3D") else '2'
        obj.geompending() #on signale qu on a pas traite la geom
    if schema_init:
#        objid = obj.ident
        objid = ('',obj.ident[1]) # on ignore les niveaux
        newid = schema_init.map_dest(objid)

#        if not newid:
#            print ("!!!!!!!attention objet non defini dans le schema d'entree", objid)
        if newid == objid:
            classe = schema_init.get_classe(objid)
            if classe:
                newid = classe.identclasse
        if newid != objid:
            obj.setident(newid)
            objid = newid

        if objid not in schema_init.classes:
            print("!!!!!!!attention objet non defini dans le schema d'entree",
                  schema_init.nom, objid)
        obj.setschema_auto(schema_init)
#                    if objid in schema.classes:
    elif schema:
        obj.setschema_auto(schema)
    obj.setorig(numero) # on renseigne l'idenbtifiant d 'origine
    obj.attributs['#chemin'] = chemin

def _get_schemas(regle, rep, fichier):
    '''definit le schemas de reference et les elementt immuables '''
    schema = None
    schema_init = None
    stock_param = regle.stock_param
    stock_param.fichier_courant = os.path.splitext(fichier)[0]
    if regle.getvar("schema_entree"):
        schema = stock_param.schemas.get(regle.getvar("schema_entree"),None)
        schema_init = schema
    else:
        if regle.getvar('autoschema'):
            schema = stock_param.init_schema(rep, origine='B', fich=fichier, stable=False)
    return schema, schema_init





def lire_objets_asc(rep, chemin, fichier, stock_param, regle):
    ''' lecture d'un fichier asc et stockage des objets en memoire'''
    n_obj = 0
    affich = 20000
    nextaff = 20000
    #ouv = None
    obj = None
    nom = None
    schema, schema_init = _get_schemas(regle, rep, fichier)
#    print ('lire_asc ', schema, schema_init)
    maxobj = stock_param.get_param('lire_maxi', 0)
#    print('asc:entree', fichier)
    log_erreurs = _erreurs_entete()
    next(log_erreurs)
    with open(os.path.join(rep, chemin, fichier), "r", 65536,
              encoding=stock_param.get_param('codec_entree', 'utf-8'),
              errors="backslashreplace") as ouvert:
        suite = False
        if not chemin:
            chemin = os.path.basename(rep)
        for i in ouvert:
            if suite:
                suite, nom = complete_attribut(obj, nom, i)
                continue
            if len(i) <= 2 or i.startswith('*'):
                continue

            code_0, code_1 = i[0], i[1]
            if code_0 == ";" and code_1.isnumeric():
                if obj:
                    n_obj += 1
                    _finalise(obj, schema_init, schema, n_obj, chemin)
                    stock_param.moteur.traite_objet(obj, regle) # on traite l'objet precedent
                    if n_obj >= nextaff:
                        nextaff += affich
                        stock_param.aff.send(('interm', 0, n_obj))
#                            print("info: asc  : lecture ", fichier, n_lin,
#                                  "lignes ", n_obj, "objets ")
                    if maxobj and n_obj >= maxobj:
                        obj = None
                        break
                if code_1 in "9356":
                    obj = Objet(chemin, stock_param.fichier_courant, format_natif='asc',
                                conversion=geom_from_asc)
                    _decode_entete_asc(obj, i, log_erreurs)
            elif (code_0 == "2" or code_0 == "4") and (code_1.isalpha() or code_1 == '_'):
                nom, suite = ajout_attribut_asc(obj, i)
            elif i.startswith("FIN"):
                continue
            elif obj:
                obj.geom.append(i)
        if obj:
            _finalise(obj, schema_init, schema, n_obj, chemin)
            stock_param.moteur.traite_objet(obj, regle) # on traite le dernier objet
        log_erreurs.send('')
    return n_obj

def _ecrire_point_asc(point):
    '''retourne un point pour l'entete'''

    dim = point.dimension
    angle = round((90-point.angle)*FA, 0)
    try:
        if dim == 2:
            ccx, ccy = point.coords[0][:2]
            code = ';3 '
            chaine = ",".join(('', "%d"%(ccx*FC), "%d"%(ccy*FC), "%d"%(angle)))
        else:
            ccx, ccy, ccz = point.coords[0][:3]
            code = ';6 '
            chaine = ",".join(('', "%d"%(ccx*FC), "%d"%(ccy*FC), "%d"%(ccz*FC), "%d"%(angle)))
        return code, chaine
    except ValueError:
        print('erreur ecriture point', point.coords, dim)

def format_date(date):
    ''' genere une date ne format entete elyx'''
    return date.replace('/', '-').replace(' ', ',').split('.')[0] if date else '01-01-1000,00:00:00'

def _ecrire_entete_asc(obj):
    ''' genere le texte d'entete asc a partir d'un objet en memoire'''
    types_geom_asc = {'0':';5 ', '1':'3', '2':';9 ', '3':';9 '}
    type_geom_sortie = ';5 '
    attr = obj.attributs
    try:
        id_num = attr['#gid']
    except KeyError:
        id_num = str(obj.ido)

    classe = attr['#classe'].upper()
    if '#clef' in classe:
        index = attr.get('#clef')
    else:
        index = ' '
#    print ("entete asc ",obj.attributs)
    type_geom = obj.attributs['#type_geom']
    if type_geom != '0':
        if obj.initgeom():
            type_geom_sortie = types_geom_asc.get(type_geom, ';5 ')
        else:
            print("geometrie invalide ",id_num, obj.geom)
            type_geom_sortie = ';5 '

    dcre = format_date(attr.get("#_sys_date_cre"))
    dmod = format_date(attr.get("#_sys_date_mod"))
    fin_ent = (";"+dcre+','+dmod+";"+attr.get('#complement', ''))
    idobj = id_num+','+classe+','+index
    if fin_ent[-1] == '\n':
        fin_ent = fin_ent[:-1]

    if type_geom_sortie == "3":
        code, chaine = _ecrire_point_asc(obj.geom_v.point)
        entete = code+idobj+chaine+fin_ent+';\n'
    else:
        entete = type_geom_sortie+idobj+fin_ent+';\n'
    return entete



def _convertir_objet_asc(obj, liste, transtable=None):
    '''sort un objet asc en chaine '''

    entete = _ecrire_entete_asc(obj)

    if obj.format_natif == 'asc' and obj.geomnatif: # on a pas touche a la geometrie
#        print ('natif asc')
        if obj.geom:
            geometrie = "".join(obj.geom)
        else:
            geometrie = ''
    else:
        geometrie = ecrire_geom_asc(obj.geom_v)

    attmap = obj.schema.attmap if obj.schema else dict()
#    print "ecriture", liste
    tliste = list()
    eliste = list()
    if liste is None:
        liste = [i for i in obj.attributs if i[0] != '#']

    a_sortir = [i for i in liste if i in obj.attributs and obj.attributs[i]]
#    print('asc  attributs',liste)
#    aliste = (i for i in a_sortir if i not in obj.text_graph and i not in obj.tg_coords)
    aliste = ((attmap.get(i, i).upper(),str(obj.attributs[i]).translate(transtable))
              for i in a_sortir if i not in obj.text_graph and i not in obj.tg_coords)
    if obj.text_graph:
        tliste = ((i,str(obj.attributs[i]).translate(transtable))
                  for i in a_sortir if i in obj.text_graph)
    if obj.etats:
        eliste = (i for i in a_sortir if i in obj.etats)

#    attlist = "\n".join(("2"+attmap.get(i, i).upper()+",NG"+str(len(str(obj.attributs[i])))+","+
#                         str(obj.attributs[i])+";" for i in aliste))
    attlist = "\n".join(("2"+i+",NG"+str(len(j))+","+j+";" for i,j in aliste))

    if tliste:
        tglist = "\n".join(("2"+attmap.get(i, i).upper()+",TL"+str(len(j))+","+
                            str(int(float(obj.attributs[i+'_X'])*FC))+","+
                            str(int(float(obj.attributs[i+'_Y'])*FC))+","+
                            ",".join(obj.text_graph[i])+","+j+";" for i, j in tliste))
        attlist = attlist+"\n"+tglist
    if eliste:
        elist = "\n".join(("4"+attmap.get(i, i).upper()+","+
                           str(obj.attributs.get('#_sys_E_'+i), '')+";" for i in eliste))
        attlist = attlist+"\n"+elist

    return entete+geometrie+attlist







class AscWriter(FileWriter):
    ''' gestionnaire d'ecriture pour fichiers asc'''
    def __init__(self, nom, liste_att=None, encoding='cp1252', liste_fich=None, schema=None):
        super().__init__(nom, liste_att=liste_att, converter=_convertir_objet_asc,
                         encoding='cp1252', liste_fich=liste_fich, schema=schema)
        self.htext = "*****\n** sortie_mapper\n*****\n"
        self.ttext = "FIN\n"
        self.transtable = str.maketrans({'\n':'\\'+'n','\r':''})

def asc_streamer(obj, regle, _, attributs=None):
    '''ecrit des objets asc au fil de l'eau.
        dans ce cas les objets ne sont pas stockes,  l'ecriture est effetuee
        a la sortie du pipeline (mode streaming)
    '''
    if obj.virtuel: # on ne traite pas les virtuels
        return
    #raise
    rep_sortie = regle.getvar('_sortie')
    if not rep_sortie:
        raise NotADirectoryError('repertoire de sortie non défini')
#    print('asc:', obj.ident,regle.dident, 'sortie:', rep_sortie)

    sorties = regle.stock_param.sorties
    if obj.ident == regle.dident:
        ressource = regle.ressource
    else:
        groupe, classe = obj.ident
        if regle.fanout == 'groupe':
            nom = sorties.get_id(rep_sortie, groupe, '', '.asc')
        else:
            nom = sorties.get_id(rep_sortie, groupe, classe, '.asc')

        ressource = sorties.get_res(regle.numero, nom)
        if ressource is None:
            if os.path.dirname(nom):
                os.makedirs(os.path.dirname(nom), exist_ok=True)
#            print ('ascstr:creation liste',attributs)
            streamwriter = AscWriter(nom,
                                     encoding=regle.getvar('codec_sortie', 'utf-8'),
                                     liste_att=attributs,
                                     liste_fich=regle.stock_param.liste_fich, schema=obj.schema)
            ressource = sorties.creres(regle.numero, nom, streamwriter)
        else:
            ressource.handler.changeclasse(obj.schema, attributs)
#            print ('nouv ressource', regle.numero,nom,ressource.handler.nom)

        regle.ressource = ressource
        regle.dident = obj.ident
#    print ("fichier de sortie ",fich.nom)
    ressource.write(obj, regle.numero)


def ecrire_objets_asc(regle, _, attributs=None):
    '''ecrit un ensemble de fichiers asc a partir d'un stockage memoire ou temporaire'''
    #ng, nf = 0, 0
    #memoire = defs.stockage
#    print( "ecrire_objets asc")
    rep_sortie = regle.getvar('_sortie')
    sorties = regle.stock_param.sorties
    dident = None
    ressource = None
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recupobjets(groupe):# on parcourt les objets
            if obj.virtuel: # on ne traite pas les virtuels
                continue
            if obj.ident != dident:
                groupe, classe = obj.ident
                if regle.fanout == 'groupe':
                    nom = sorties.get_id(rep_sortie, groupe, '', '.asc')
                else:
                    nom = sorties.get_id(rep_sortie, groupe, classe, '.asc')

                ressource = sorties.get_res(regle.numero, nom)
                if ressource is None:
                    if os.path.dirname(nom):
                        os.makedirs(os.path.dirname(nom), exist_ok=True)

                    streamwriter = AscWriter(nom, encoding=regle.stock_param.get_param
                                             ('codec_sortie', 'utf-8'),
                                             liste_fich=regle.stock_param.liste_fich)
                    streamwriter.set_liste_att(attributs)
                    ressource = sorties.creres(regle.numero, nom, streamwriter)
                regle.ressource = ressource
                dident = (groupe, classe)
            ressource.write(obj, regle.numero)

#def asc_streamer(obj, groupe, rep_sortie, regle, final, attributs=None,
#                 racine=''):


#########################################################################
