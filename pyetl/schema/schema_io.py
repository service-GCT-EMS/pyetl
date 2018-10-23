# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 09:28:45 2014
gestion des entrees et sorties de schemas
@author: 89965
"""
import os
from  zipfile import ZipFile
import xml.etree.ElementTree as ET
from pyetl.formats.db import DATABASES

from . import schema_interne as SCI
from . import fonctions_schema as FSC
ESC_XML = lambda t: (str(t).replace('&', '&amp;').replace("'", '&apos;').replace('<', '&lt;')
                     .replace("\\'", '&apos;'))

def sortir_conformite_xml(conf, mode=-1, init=False):
    '''ecrit une conformite en format xml'''
    entete = ['<conformite nom="' + conf.nombase + '" type="' + str(conf.type_conf) +\
    '" nb_elements="' + str(len(conf.stock)) +'">']
    if conf.usages:
        entete.extend(['\t<usage schema = "'+schema+'" classe = "'+ classe
                       +'" attribut = "'+attribut+'"/>'
                       for schema, classe, attribut in sorted(conf.usages, key=lambda x: x[1])])

    valeurs = []
    for i in sorted(conf.stock.values(), key=lambda v: v[2]):
        valeurs.append('\t<VALEUR v="' + (ESC_XML(i[4]) if init else ESC_XML(i[0]))+
                       '" alias="'+ ESC_XML(i[1])+'" ordre="'+ str(i[2])+
                       '" mode="'+(str(mode) if mode != -1 else str(i[3]))+'"/>')
    entete.extend(valeurs)
    entete.append('</conformite>')
    return '\n'.join(entete)

def sortir_conformite_csv(conf, mode=-1, init=False):
    '''ecrit une conformite en format csv'''
    #"!conformite;Ordre;VAL_CONF_NOM;VAL_CONF_TEXTE;mode;fin"
#    print ('sortir conformite ',conf.nom,mode,conf.stock)
#    print ([";".join((conf.nom, str(i[2]), i[4] if init else i[0], i[1],
#                      str(i[3]) if mode == -1 else mode))
#                      for i in sorted(conf.stock.values(), key=lambda v: v[2])])
    return [";".join((conf.nombase, str(i[2]), i[4] if conf.ajust and not init else i[0], i[1],
                      str(i[3]) if mode == -1 else str(mode)))
            for i in sorted(conf.stock.values(), key=lambda v: v[2])]


def sortir_attribut_xml(classe, attr, keys):
    '''ecrit une definition d'attribut en xml'''

    type_att = 'enum' if attr.conformite else attr.get_type()
    type_att_base = attr.nom_conformite if attr.conformite else attr.type_att_base
    texte = "\t<attribut nom='" + ESC_XML(attr.nom) +\
            "' type='" + str(type_att) +\
            "' type_base='" + str(type_att_base) +\
            "' fonction='" + ESC_XML(attr.defaut) +\
            "' alias='" +ESC_XML(attr.alias) +\
            "' taille='" + str(attr.taille) +\
            "' decimales='" + str(attr.dec) + "'"

    if  attr.nom in keys:
#        print ("clefs primaires",keys)
        texte = texte+" clef_primaire = 'oui' ordre = '"+str(keys.index(attr.nom)+1)+"'"
    if attr.nom in classe.fkey_attribs:
        dec = classe.getfkey(attr.nom).split('.')
        if len(dec) == 3:
            c_schema, c_classe, c_attr = dec
            texte = texte+" clef_etrangere = 'oui'"+\
            " cible_schema = '"+c_schema.replace('FK:', '')+ "'"+\
            " cible_classe = '"+c_classe+ "'"+\
            " cible_attribut = '"+c_attr+ "'"
    for i in classe.indexes:
        if attr.nom in classe.indexes[i]:
            texte = texte+" index = 'oui'"
            break
    if attr.oblig:
        texte = texte+" obligatoire = 'oui'"
    if attr.unique:
        texte = texte+" unique = 'oui'"

    if attr.conf and attr.nom_conformite == '':
        description = [texte+">"]
        if attr.type_att in ["E", "EL", "F"] or attr.type_att_base in ["E", "EL", "F"]:
            # types numeriques
            #print "type attribut",self.type_att
            try:
                vals = sorted([i for i in attr.valeurs if i], key=float)
            except ValueError:
                vals = []
                print('erreur: sortie schema xml erreur valeurs', attr.type_att,
                      attr.type_att_base, attr.valeurs)
        else:
            vals = sorted(attr.valeurs)

        valeurs_conf = ["\t\t<valeur_conformite v='" + ESC_XML(str(j)) + "' n='" +
                        str(attr.valeurs[j]) + "'/>" for j in vals]
        description.extend(valeurs_conf)
        description.append("\t</attribut>")
    else:
        description = [texte+"/>"]
    return description


def sortir_schema_classe_xml(sc_classe, mode='util'):
    '''ecrit une definition de classe en xml'''

    nom_atts = sc_classe.get_liste_attributs(sys=True)
    type_stockage = sc_classe.types_stock.get(sc_classe.type_table, '')
    nb_obj = sc_classe.objcnt
    if not nb_obj:
        nb_obj = sc_classe.getinfo('objcnt_init')
    if mode == 'fusion':
        nb_obj = sc_classe.poids
    description = ["<classe nom='" + sc_classe.nom +
                   ("' nberr='" + str(sc_classe.errcnt) if sc_classe.errcnt else '') +
                   "' groupe='" + str(sc_classe.groupe) +
                   "' alias='" + ESC_XML(sc_classe.alias) +
                   "' type='"+(str(SCI.TYPES_G[sc_classe.info["type_geom"]])
                               if sc_classe.info["type_geom"] != "0" else 'ALPHA')+
                   "' clef_primaire='" + sc_classe.getpkey +\
                   "' nb_objets='" +str(nb_obj)+\
                   "' type_table='" +type_stockage+\
                   "'>"]
    keys = sc_classe.getpkey.split(',')
    for i in nom_atts:
        attribut = sc_classe.attributs[i]
        if attribut.conformite:
            attribut.taille = attribut.conformite.taille
        description.extend(sortir_attribut_xml(sc_classe, attribut, keys))
    complement = 'MULTIPLE' if sc_classe.multigeom else 'SIMPLE'
    arc = 'COURBE' if sc_classe.info['courbe'] else 'LIGNE'
    dimension = sc_classe.info["dimension"]
    #print 'type_geom',self.info["type_geom"]
    if sc_classe.info["type_geom"]:
        description.append("\t<geometrie type='" +
                           str(SCI.TYPES_G[sc_classe.info["type_geom"]]) + "' " +
                           " complement='"+complement+"' arc='"+arc+
                           "' dimension='"+dimension+
                           "' nom_geometrie='"+sc_classe.info["nom_geometrie"]+"'/>")
    description.append("</classe>")
    #print "description",description
    return "\n".join(description)


def sortir_schema_classe_csv(sc_classe, mode='util'):
    '''ecrit une definition de classe en csv'''

    nom_compo = sc_classe.nom
#    print ('ssc:\n','\n'.join([str((a.nom,a.nom_conformite,a.type_att,a.type_att_base))
#    for a in sc_classe.attributs.values()]))
    liste_att_csv = list()
#    if sc_classe.nom=='rg_fil_troncon':
#        print ('sortir_schema -----------------',sc_classe.schema.nom, sc_classe.nom)
    groupe = sc_classe.groupe
    sc_classe.cree_noms_courts(longueur=10)
    complement = 'oui' if sc_classe.multigeom else 'non'
    type_geom = SCI.TYPES_G[sc_classe.info["type_geom"]]
#    print('sio: sortir schema', sc_classe.info['type_geom'], type_geom)
    dimension = sc_classe.info["dimension"]
    type_stockage = sc_classe.types_stock.get(sc_classe.type_table, '')
    arc = 'courbe' if sc_classe.info['courbe'] else ''

    srid = 'mixte' if sc_classe.sridmixte else str(sc_classe.srid)
    nbr = sc_classe.objcnt
    if not nbr:
        nbr = sc_classe.getinfo('objcnt_init')
    if mode == 'fusion':
        nbr = sc_classe.poids
    liste_att_csv.append(";".join([groupe, nom_compo, '', str(sc_classe.alias).replace('\n', ''),
                                   str(type_geom), arc,
                                   complement, type_stockage, '', srid, dimension, str(nbr), '',
                                   '', 'fin', sc_classe.listindexes, sc_classe.listfkeys()]))

    iatt = sc_classe.index_par_attributs()

    for i in sc_classe.get_liste_attributs(sys=True):
        att = sc_classe.attributs.get(i)
        if not att:
            print('attribut inconnu :', i, '\nk: ', sorted(sc_classe.attributs.keys()),
                  '\nl: ', sorted(sc_classe.liste_attributs_cache))
            continue
        #print "attribut",i
        nom = sc_classe.minmajfunc(str(att.nom))

        if att.conformite:
            #print "nom conformite",att.nom_conformite,att.conformite
            att.type_att = 'T'
            att.taille = att.conformite.taille
        #graphique="oui" if att.graphique else 'non'
        if att.type_att == 'A':
            att.type_att = 'T'
            print("sio: type attribut non defini texte par defaut", groupe, nom_compo, nom)
        type_att = att.get_type()
#        print ('type_att lu',i,att.type_att,att.conformite,att.multiple)

        multiple = "oui" if att.multiple else 'non'
        defaut = att.defaut if att.defaut else ''
        oblig = "oui" if att.oblig else 'non'
        conf = att.nom_conformite if att.conformite else ''
        index = iatt.get(att.nom, '')
        fkey = sc_classe.minmajfunc(sc_classe.getfkey(att.nom))

        liste_att_csv.append(";".join([groupe, nom_compo, nom, str(att.alias).replace('\n', ''),
                                       type_att, 'non',
                                       multiple, defaut, oblig, conf, dimension, str(att.taille),
                                       str(att.dec) if att.dec else '0',
                                       str(att.nom_court), 'fin', index, fkey]).replace('\n', ' '))
    if type_geom != 'NOGEOM':
        liste_att_csv.append(";".join([sc_classe.groupe, sc_classe.nom,
                                       sc_classe.info["nom_geometrie"],
                                       str(sc_classe.alias).replace('\n', ''), str(type_geom),
                                       arc, complement, "", "", srid, dimension,
                                       str(sc_classe.ech_denom_min), str(sc_classe.ech_denom_max),
                                       "", "fin", 'G:', '']).replace('\n', ' '))
    return liste_att_csv

def sortir_schema_xml(sch, header, alias_schema, codec, mode='util'):
    '''ecrit un schema complet en xml'''

    entete = '<?xml version="1.0" encoding="'+codec+'"?>\n'+\
        (header+'\n' if header else '') +\
        "<structure nom='" + sch.nom +\
        ("' alias='"+ alias_schema if alias_schema else "")+\
        "' type='"+ sch.origine+"'>"
    conf = ''
    classes = ''
    #print ("schema_io:sortir schema xml",sch.nom,sch.classes)
    nbclasses = 0
    if sch.conformites:
        conf = "<conformites>\n"+\
               '\n'.join([sortir_conformite_xml(sch.conformites[i])
                          for i in sorted(sch.conformites.keys())])+\
               "\n</conformites>\n"
    if sch.classes:
        # regroupement par groupes
        groupes = dict()
#        print ('schema io xml : classes dans le schema',sch.nom,mode,len(sch.classes))
        for i in sorted(sch.classes.keys()):
            if sch.classes[i].a_sortir:
                groupe, classe = i
#                print ('schema io xml : classe',groupe,classe)
                if groupe not in groupes:
                    groupes[groupe] = []
                groupes[groupe].append(classe)
        description = ["<schemas>"]
        for groupe in sorted(groupes.keys()):
            alias_g = ESC_XML(sch.alias_groupes.get(groupe, ''))
#            print ('sortir schema',g,alias_g,sch.alias_groupes)
            description.append("<schema nom='"+groupe+"' alias='"+alias_g+"'>")
            description.append("<classes>")
            nbclasses += 1
            for classe in groupes[groupe]:
                description.append(sortir_schema_classe_xml(sch.classes[(groupe, classe)],
                                                            mode=mode))
            description.append("</classes>")
            description.append("</schema>")
        description.append("</schemas>")
        classes = '\n'.join(description)
    if nbclasses:
        return entete + '\n' + conf + '\n' + classes + "\n</structure>"
    return None


def sortir_schema_csv(sch, mode='all', modeconf=-1, conf_used=False, init=False):
    '''ecrit un schema complet en csv'''
    conf = ["!conformite;Ordre;VAL_CONF_NOM;VAL_CONF_TEXTE;mode;fin"]
#    print("schema: info sortir_schema", sch.nom, len(sch.conformites),
#          'conformites', len(sch.classes), 'classes')
#    print ('conformites presentes',
#          [(sch.conformites[i].nom,sch.conformites[i].stock.values())
#          for i in sch.conformites])
#    print('schema_csv : conformites', len(sch.conformites))
    if sch.conformites:
        unused = []
        for i in sorted(sch.conformites.keys()):
            if conf_used and not sch.conformites[i].utilise:
                unused.append(i)
                continue
            conf.extend(sortir_conformite_csv(sch.conformites[i], modeconf, init))
        if unused:
            print("schema : ::: warning", len(unused), "conformites inutilisees ",
                  unused[:10], '...')

    description = ["!groupe;compo_nom;Nom;Alias;Type;graphique;multiple;Valeur par defaut;"+
                   "Obligatoire;Conformite;dimension;taille;decimales;nom court;fin;index;FK"]
    #print("schema:  csv sortir_classes",len(self.classes))
    if sch.classes:
        for i in sorted(sch.classes.keys()):
            if sch.classes[i].a_sortir:
#                print ("csv classe a sortir",i,sch.classes[i])
#                print ('\n'.join([str((a.nom,a.nom_conformite,a.type_att,a.type_att_base))
#                       for a in sch.classes[i].attributs.values()]))
                description.extend(sortir_schema_classe_csv(sch.classes[i], mode))
    #print ("schema: debug " , conf,cl)
    return conf, description


def lire_mapping(schema_courant, fichier, codec):
    ''' lit un fichier de mapping externe'''
    if not os.path.isfile(fichier):
        print("schema io: ::: warning fichier mapping introuvable ", fichier)
        return
    liste_mapping = []
#    print("schema io: lire_mapping ", fichier)
    with open(fichier, 'r', encoding=codec) as entree:
        i = entree.readline() #entete : on ignore
        i = entree.readline()
        while i:
            liste_mapping.append(i[:-1])
            i = entree.readline()
    schema_courant.init_mapping(liste_mapping)
#    print ('lecture_mapping','\n'.join(liste_mapping[:10]))


def decode_conf_csv(schema_courant, entree, mode_alias):
    """decode un tableau de conformites"""
    codes_force = {'force_base':0, 'force_num':1, 'force_alias':2, 'force_inv':3}
    codes_alias = {'num':1, 'alias':2, 'inv':3}
    lin = 0
    for i in entree:
        if lin == 0 and '!' in i[:4]:
#                print (" schema conf io:detecte commentaire utf8")
            lin = 1
            continue
        if i[0] == '!':
#                print (" schema conf io:detecte commentaire")
            continue
        val_conf = i.replace('\n', '').split(';')
        nom = val_conf[0].lower()
        if not nom:
            continue
        conf = schema_courant.get_conf(nom)
        mode = codes_force.get(mode_alias, None)
        if not mode and len(val_conf) > 4 and val_conf[4].isdigit():
            mode = int(val_conf[4])
#                print ('scio:lecture mode conf ', mode)
        else:
            mode = codes_alias.get(mode_alias, 1)
        conf.type_conf = 1
#        n=n+1
#        if n<3 : print("schema: stockage ", val_conf,'..',val_conf[4],'----->',mode,mode_alias)
        if len(val_conf) > 3:

            conf.stocke_valeur(val_conf[2], val_conf[3].replace('\n', ''), mode) # on ignore
        else:
            print("schema: conformite non conforme ", val_conf)




def lire_conf_csv(schema_courant, fichier, mode_alias, cod):
    '''lit un fichier de conformites au format csv'''
    if not os.path.isfile(fichier):
        print("schema: ::: warning fichier conformites introuvable ", fichier)
        return
#    n=0
    with open(fichier, 'r', encoding=cod) as entree:
        decode_conf_csv(schema_courant, entree, mode_alias)









def _lire_geometrie_csv(classe, v_tmp, dimension):
    ''''decode une geometrie en fichier csv'''
    #l=v[3].split('_')
    #if l[0] not in '0123':
    gref = v_tmp[4].upper()
    if 'GEOMETRY' in gref: # description de geometrie postgis
        gref = gref.replace('GEOMETRY', '')
        gref = gref.replace('(', '')
        gref = gref.replace(')', '')
        gref = gref.split(',')[0]
        gref = gref.replace('Z', '')

    if v_tmp[5] == 'courbe':
        classe.info['courbe'] = '1'

    if gref not in SCI.CODES_G:
        print("schema: erreur type ", v_tmp[4])
    classe.info["type_geom"] = SCI.CODES_G[gref]
    classe.alias = v_tmp[3]
    if '#' in v_tmp[5]:
        for val in v_tmp[5].split(','):
            if val:
                param = val.split(':', 1)
                nom = param[0]
                contenu = param[-1]
                classe.info[nom] = contenu

    classe.multigeom = classe.info['type_geom'] > '1'
    classe.setdim(dimension[0])

    if len(dimension) > 1 and dimension[1] == "F":
        # option de forcage de la dimension
        classe.force_dim = True
#                        if classe.is_3d:
        if classe.info["dimension"] == "3":
            if len(dimension) > 2:
                classe.V3D = float(dimension[2:])
            else:
                classe.V3D = 0
    if dimension == "0":
        classe.autodim = True
#    print( 'geometrie lue',classe.info["type_geom"], classe.info["dimension"], v_tmp)


def _valide_entete_csv(ligne, cod, sep):
    ''' valide la presence de l'entete'''

    if ligne and ligne[0] == '!':
        return [j.strip() for j in ligne[1:-1].split(sep)]
    elif len(ligne) > 3 and '!' in ligne[:3]:
        print(" schema io:detecte commentaire utf8")
        if cod != 'utf-8':
            print('erreur encodage de lecture ', cod, ' choisir utf8')
            raise TypeError
        return True
    print('ligne bizarre', ligne)
    return False


def _toint(val):
    try:
        return int(val)
    except ValueError:
        return 0


def _decode_attribut_csv(liste):
    ''' decode un attribut en csv et en fait un dictionnaire '''
    noms = ['nom_attr', 'alias', 'type', 'graphique', 'multiple', 'defaut', 'obligatoire',
            'conformite', 'dimension', 'taille', 'decimales', 'nom_court']
    att_dict = dict(zip(noms, liste[2:14]))
    ll_tmp = att_dict[type].split(':')
    if len(ll_tmp) > 1:
        att_dict['clef'] = ll_tmp[1]
    att_dict['type_attr'] = ll_tmp[0].lower()
    att_dict['type_attr_base'] = att_dict['type_attr']
    att_dict['graphique'] = att_dict['graphique'] == 'oui'
    att_dict['multiple'] = att_dict['multiple'] == 'oui'
    att_dict['obligatoire'] = att_dict['obligatoire'] == 'oui'

    if att_dict['conformite']:
        #print 'conformite',v
        att_dict['type_attr'] = att_dict['conformite'].lower()
        att_dict['type_attr_base'] = "text"
        #nom_conformite = type_attr
    att_dict['taille'] = _toint(att_dict.get('taille', 0))
    att_dict['decimales'] = _toint(att_dict.get('decimales', 0))
    att_dict['nom_court'] = att_dict.get('nom_court', '')
    if att_dict['nom_court'] == "fin":
        att_dict['nom_court'] = ''
    return att_dict


def decode_classes_csv(schema_courant, entree):
    """stocke les  classes  dans le schema"""
    for i in entree:
        if not i:
            continue
        if i[0] == '!':
            continue
        v_tmp = [j.strip() for j in i.split(';')]

        if len(v_tmp) < 11:
            print('sio:ligne trop courte ', len(v_tmp))
            continue
        clef_etr = ''
        index = ''
        if len(v_tmp) >= 16:
            index = v_tmp[15]
        if len(v_tmp) >= 17:
            if v_tmp[16].replace('\n', '').strip() != '':
                clef_etr = v_tmp[16].replace('\n', '')

        groupe = v_tmp[0]
        nom = v_tmp[1]
    #            print ('schema_io:lecture_attribut ', nom, v_tmp[2])
        if groupe and nom:
            schema_courant.origine = 'L'
            idorig = (groupe, nom)
            ident = schema_courant.map_dest(idorig)
            if not ident:
                ident = idorig
            classe = schema_courant.setdefault_classe(ident)
            attr = v_tmp[2]
    #                print ("sio : lecture", classe.identclasse, attr)
    #                if not attr:
    #                    print ('sio: definition classe', idorig, ident)
    #                    continue
            alias = v_tmp[3]
            ll_tmp = v_tmp[4].split(':')
            if len(ll_tmp) > 1:
                clef_etr = ll_tmp[1]
            type_attr = ll_tmp[0].lower()
            type_attr_base = type_attr
            graphique = v_tmp[5] == 'oui'
            multiple = v_tmp[6] == 'oui'
            defaut = v_tmp[7]
            obligatoire = v_tmp[8] == 'oui'
            #nom_conformite = ''
            if v_tmp[9]:
                #print 'conformite',v
                type_attr = v_tmp[9].lower()
                type_attr_base = "text"
                #nom_conformite = type_attr
            dimension = v_tmp[10]
            taille = int(v_tmp[11]) if len(v_tmp) > 11 and v_tmp[11].isnumeric() else 0
            dec = int(v_tmp[12]) if len(v_tmp) > 12 and v_tmp[12].isnumeric() else 0
            nom_court = ''
            if len(v_tmp) > 13:
                nom_court = v_tmp[13] if v_tmp[13] != "fin" else""

            if attr == 'geometrie':
                _lire_geometrie_csv(classe, v_tmp, dimension)
            elif attr: #c'est un attribut
                classe.stocke_attribut(attr, type_attr, defaut=defaut,
                                       type_attr_base=type_attr_base,
                                       force=True, taille=taille, dec=dec,
                                       alias=alias, ordre=-1,
                                       nom_court=nom_court, clef_etr=clef_etr, index=index,
                                       obligatoire=obligatoire, multiple=multiple)
    #                    print ('sio:stocke_attribut',attr,type_attr,nom_court)
    #                    print ('stocke',classe.attributs[attr].type_att)
                if graphique:
                    classe.stocke_attribut(attr+'_X', 'reel', '', 'reel',
                                           ordre=-1, obligatoire=obligatoire,
                                           multiple=multiple)
                    classe.stocke_attribut(attr+'_Y', 'reel', '', 'reel',
                                           ordre=-1, obligatoire=obligatoire,
                                           multiple=multiple)
            else: #on ne fait que definir l'alias de la classe
                if v_tmp[11].isnumeric():
                    classe.poids = int(v_tmp[11])
                classe.alias = v_tmp[3]
                if v_tmp[5] == 'courbe':
                    classe.courbe = True
                    classe.info['courbe'] = '1'
                if v_tmp[9].isnumeric():
                    classe.srid = str(int(v_tmp[9]))




def lire_classes_csv(schema_courant, fichier, cod):
    '''lit un fichier de description de classes au format csv'''
    if not os.path.isfile(fichier):
        print("!!!!!!! schema: erreur fichier schema introuvable ", fichier)
        return
#    print('sio:lecture classes', fichier)
    with open(fichier, 'r', encoding=cod) as entree:
        ent = _valide_entete_csv(entree.readline(), cod, ';')
        if not ent:
            print('entete invalide ', ent)
            entree.seek(0)
        decode_classes_csv(schema_courant, entree)


def recup_schema_csv(base, classes, confs, mapping):
    """recompose un schema a partir du retour de traitements paralleles"""
    schema = SCI.Schema(base, origine='L')
    decode_conf_csv(schema, confs, mode_alias="num")
    decode_classes_csv(schema, classes)
    schema.init_mapping(mapping)
    return schema


def lire_schema_csv(base, fichier, mode_alias='num', cod='cp1252', schema=None, specifique=None):
    '''lit un schema conplet en csv'''
    if schema is None:
#        print ('lecture_csv')
        schema = SCI.Schema(base, origine='L')

    fichier_conf = '_'.join((fichier, "enumerations.csv"))
    fichier_classes = '_'.join((fichier, "classes.csv"))
    mapping = '_'.join((fichier, "mapping.csv"))
    # modifications manuelles du schema
    complements_conf = '_'.join((fichier, "complements_enumerations.csv"))
    complements_classe = '_'.join((fichier, "complements_classes.csv"))
    complements_mapping = '_'.join((fichier, "complements_mapping.csv"))
    # on lit d'abord les mappings pour voir s'il faut rectifier les schemas en entree
    if os.path.exists(mapping):
        lire_mapping(schema, mapping, cod)
    if os.path.exists(complements_mapping):
        lire_mapping(schema, complements_mapping, cod)

    lire_conf_csv(schema, fichier_conf, mode_alias, cod=cod)
    if os.path.exists(complements_conf):
        lire_conf_csv(schema, complements_conf, mode_alias, cod=cod)
    #g.conformites.calcule_taille()
    lire_classes_csv(schema, fichier_classes, cod)
    if os.path.exists(complements_classe):
        lire_classes_csv(schema, complements_classe, cod)
    if specifique: # on lit des informations complementaires
        for i in specifique:
            fichier_special = '_'.join((fichier, i+".csv"))
            if os.path.exists(fichier_special):
                liste = open(fichier_special, 'r').readlines()
                entete = liste[0]
                contenu = liste[1:]
                schema.elements_specifiques.divers[i] = (entete, contenu)

    FSC.analyse_interne(schema, 'init')
#    print("schema: lecture_schema realisee --->", fichier, len(schema.classes),
#          "<-----")
#    print ('mapping enregistre','\n'.join(schema.mapping_schema(fusion=True)[:10]))
    return schema


def fusion_schema(nom, schema, schema_tmp):
    '''fusionne 2 schemas en se basant sur les poids pour garder le bon'''
    if not schema or not schema_tmp:
        print ('schema vide fusion impossible', nom, schema,schema_tmp)
        return
    for i in schema_tmp.conformites:
        if i in schema.conformites:
            if schema.conformites[i].poids >= schema_tmp.conformites[i].poids:
                continue
        schema.conformites[i] = schema_tmp.conformites[i]
    for i in schema_tmp.classes:
        if i in schema.classes:
            if schema.classes[i].poids >= schema_tmp.classes[i].poids:
                continue
        schema.ajout_classe(schema_tmp.classes[i])
    schema_tmp.map_classes()
    liste_mapping = schema_tmp.mapping_schema(fusion=True)
#    print ('mapping_fusion','\n'.join(liste_mapping[:10]))
    schema.init_mapping(liste_mapping[1:])

    del schema_tmp


def lire_schemas_multiples(nom, rep, racine, mode_alias='num', cod='cp1252', specifique=None):
    '''initialise le schema et rajoute tous les elements necessaires'''
    schema = SCI.Schema(nom)
    if os.path.isdir(rep):
        for element in os.listdir(rep):
#            print ('examen ',element ,racine)
            if racine.lower() in element.lower() and 'classes' in element\
               and os.path.splitext(element)[1] == '.csv':
                #print("schema:lecture ",element,racine,os.path.splitext(element))
                element_modif = '_'.join(element.split("_")[:-1])
                fichier = os.path.join(rep, element_modif)
                fusion_schema(schema, lire_schema_csv('tmp', fichier, mode_alias,
                                                      cod=cod, specifique=specifique))
    schema.map_classes()
    if schema.classes:
        print("schema:classes totales", len(schema.classes), cod)
    else:
        print("pas de definition de schema", rep, racine)
    return schema


def fusion_schema_xml(schema, fichier, cod='utf-8'):
    '''# complete la lecture d'un fichier'''
    origine = ET.parse(open(fichier, 'r', encoding=cod))
#    g=schema(groupe)
#    g.origine='L'
    for i in origine.getiterator("conformite"):
        nom = i.get('nom')
        type_c = i.get('type')
        mode = i.get('mode')
        conf = schema.get_conf(nom, type_c=type_c, mode=mode)
        for j in i.getiterator("VALEUR"):
            conf.stocke_valeur(j.get('v'), j.get('alias'))
        #print "stockage_conf",conf.valeurs
    for i in origine.getiterator("classe"):
        nom = i.get("nom")
        groupe = i.get("schema")
        ident = (groupe, nom)
        classe = schema.def_classe(ident)
#        g[nom]=sc
        for j in i.getiterator("attribut"):
            nom_a = j.get('nom')
            type_a = j.get('type')
            type_base = j.get('type_base')
            defaut_a = j.get('defaut')
            taille_a = j.get('taille')
            dec_a = j.get("decimales")
            classe.stocke_attribut(nom_a, type_a, defaut_a, type_base, taille=taille_a,
                                   dec=dec_a, ordre=-1)

        for j in i.getiterator("geometrie"):
            classe.info["type_geom"] = j.get('type')
            classe.alias = j.get('alias')
            dimension = j.get('dimension', '2')
            classe.setdim(dimension)


def lire_schema_xml(base, fichier, cod='utf-8'):
    '''lit un ensemble de fichiers schema en xml'''
    print("lecture xml")
    schema = SCI.Schema(base)
    schema.origine = 'L'
    fusion_schema_xml(schema, fichier, cod=cod)
    return schema


def ecrire_schema_xml(rep, schema, mode='util', cod='utf-8', header='', alias='', prefix=''):
    '''ecrit un schema en xml'''
    xml = sortir_schema_xml(schema, header, alias, cod, mode=mode)
    nomschema = prefix+schema.nom.replace('#', '_')
    if xml:
        print("schema: ecriture schema xml", os.path.join(rep, nomschema)+".xml")
        open(os.path.join(rep, nomschema+".xml"), "w", encoding=cod).write(xml)


def ecrire_fich_csv(chemin, nom, contenu, cod):
    ''' ecriture physique du csv'''
#    print ('ecriture_csv', nom, cod)
    try:
        with open(chemin+nom, "w", encoding=cod) as fich:
            fich.write("\n".join(contenu))
            fich.write('\n')
    except PermissionError:
        print("!"*30+"impossible d'ecrire le fichier ", chemin+nom)


def ecrire_schema_csv(rep, schema, mode, cod='utf-8', modeconf=-1):
    ''' ecrit un schema en csv '''
    init = False
    if schema.origine == 'B' or schema.origine == 'L':
        init = True
    conf, classes = sortir_schema_csv(schema, mode=mode, modeconf=modeconf, init=init)
    mapping = schema.mapping_schema()
    nomschema = schema.nom.replace('#', '_')
    deftrig = []
    if 'def_triggers' in schema.elements_specifiques:
        for trig in schema.elements_specifiques['def_triggers']:
            ligne = ";".join(str(i) for i in trig)
            deftrig.append(ligne)

    if rep:
        chemref = os.path.join(rep, nomschema)
        if len(classes) > 1:
            #print (conf,'\n',schemas)
    #        print("schema: ecriture schema csv", chemref+" en csv ("+cod+")")
            ecrire_fich_csv(chemref, "_classes.csv", classes, cod)
            ecrire_fich_csv(chemref, "_enumerations.csv", conf, cod)
            ecrire_fich_csv(chemref, "_mapping.csv", mapping, cod)
            if deftrig:
                ecrire_fich_csv(chemref, "_triggers.csv", deftrig, cod)
    else:
        return classes, conf, mapping, deftrig


def set_transaction(liste):
    ''' ajoute des transactions explicites sur les fichiers'''
    liste.insert(0, "START TRANSACTION;\n")
    liste.append('COMMIT;\n')


def ecrire_fichier_sql(rep, nomschema, numero, nomfich, valeurs, cod='utf-8', transact=False):
    ''' ecrit la description du schema en sql '''
    if valeurs is None:
        return
    if numero:
        nomfich = os.path.join(rep, '_'.join((numero, nomschema, nomfich+'.sql')))
    else:
        nomfich = os.path.join(rep, '_'.join((nomschema, nomfich+'.sql')))
    if transact:
        set_transaction(valeurs)
    nberr = 0
    for i in valeurs:
        lignes = i.split('\n')
        for j in lignes:
            try:
                j.encode(cod)
            except UnicodeEncodeError:
#                print ('ligne en erreur ',j)
#                print (j.encode(cod, errors='replace'))
                nberr += 1
    if nberr:
        print("schema: ecriture schema sql", nomfich, cod)
        print('erreurs d''encodage', nberr)

    with open(nomfich, "w", encoding=cod) as fich:
        codecinfo = "-- ########### encodage fichier "+ str(fich.encoding) +\
                    ' ###(controle: n°1: éàçêè )####\n'
        fich.write(codecinfo)
        fich.write('\n'.join(valeurs))


def ecrire_schema_sql(rep, schema, type_base='std',
                      cod='utf-8', modeconf=-1, dialecte=None,
                      transact=False, autopk=False, role=None):
    ''' ecrit un schema en script sql '''
    # on determine le dialacte sql a choisir

    if dialecte == 'natif':
        if schema.dbsql: # dialecte sql adapte a la base de sortie
            gsql = schema.dbsql
        else:
            print('attention pas de dialecte natif', schema.nom)
            dialecte = 'sql'
            gsql = DATABASES[dialecte].gensql()
    elif schema.dbsql and schema.dbsql.dialecte == dialecte:
        gsql = schema.dbsql
    elif dialecte in DATABASES:
        gsql = DATABASES[dialecte].gensql()
    else:
        dialecte = 'sql'
        type_base = 'basic'
        gsql = DATABASES[dialecte].gensql()
#    print('ecriture schema sql', schema.nom, gsql.dialecte, len(schema.classes))
    gsql.initschema(schema)
    nomschema = schema.nom
    nomschema = nomschema.replace('#', '_')

    print('sio:ecriture schema sql pour ', gsql.dialecte, nomschema)
    if type_base == 'basic':
        gsql.setbasic()

    tsql, dtsql, csql, dcsql = gsql.sio_cretable(cod, autopk=autopk, role=role)
    crsc, dsc = gsql.sio_creschema(cod)

    csty = gsql.sio_crestyle()

    if type_base == 'basic':
        #on concatene tout
        tout = crsc
        tout.extend(tsql)
        ecrire_fichier_sql(rep, nomschema, '01', 'schema', tout, cod, False)

    else:

        if tsql:
            ecrire_fichier_sql(rep, nomschema, '03', 'tables', tsql, cod, transact)
            ecrire_fichier_sql(rep, nomschema, '11', 'droptables', dtsql, cod)
        if csql:
            ecrire_fichier_sql(rep, nomschema, '02', 'enums', csql, cod, transact)
            ecrire_fichier_sql(rep, nomschema, '12', 'dropenums', dcsql, cod)
        if csty:
            ecrire_fichier_sql(rep, nomschema, '04', 'styles', csty, cod)
        if crsc:
            ecrire_fichier_sql(rep, nomschema, '01', 'schemas', crsc, cod, transact)
            ecrire_fichier_sql(rep, nomschema, '13', 'dropschemas', dsc, cod)


def copier_xsl(rep):
    ''' copie un xsl par defaut pour la visibilite du schema'''
    xslref = os.path.join(os.path.dirname(__file__), 'xsl.zip')
#    print(" copie fichier ", xslref)
    with ZipFile(xslref) as xsl:
        xsl.extractall(path=os.path.join(rep, 'xsl'))



def ecrire_au_format(schema, formats_a_sortir, stock_param, mode, confs):
    ''' sort un schema dans les differents formats disponibles '''

    rep_s = schema.rep_sortie if schema.rep_sortie else\
            os.path.dirname(os.path.join(stock_param.get_param('_sortie'),
                                         schema.fich if schema.fich else ''))
    os.makedirs(rep_s, exist_ok=True)
    cod = stock_param.get_param('codec_sortie', "utf-8")
    print ('sio: ecrire_schemas',schema.nom,formats_a_sortir)
    for form in formats_a_sortir:
        if 'sql' in form: # on met le sql en premier car on modifie des choses
#            print('sio:sortie sql', schema.nom, 'rep:',
#                  rep_s, schema.dbsql, schema.dbsql.connection if schema.dbsql else 'NC', form)
            dialecte = "sql"
            if ":" in form:
                dialecte = form.split('sql:')[1]
            else:
                dialecte = stock_param.get_param('base_destination', 'sql')

            if dialecte == 'sql' and schema.dbsql:
                dialecte = 'natif'


            autopk = stock_param.get_param('autopk', '')
            role = stock_param.get_param('db_role')
            if not role:
                role = None
            type_base = 'basic' if stock_param.get_param('dbgenmode') == 'basic' else 'std'
            if type_base == 'basic':
                schema.setbasic()
                autopk = '' if autopk == 'no' else True

            print('dialecte de sortie', dialecte)

            ecrire_schema_sql(rep_s, schema,
                              type_base=type_base, cod=cod, modeconf=confs,
                              dialecte=dialecte, transact=stock_param.get_param('transact'),
                              autopk=autopk, role=role)
        if 'csv' in form:
            cod_csv = stock_param.get_param('codec_sortie_schema', "cp1252")
            ecrire_schema_csv(rep_s, schema, mode,
                              codec=cod_csv, modeconf=confs)
        if form == 'xml':
#            header = stock_param.get_param('xmlheader', '')
#            if header:
#                header = header+'\n'
            header = ''
            header = header+stock_param.get_param('xmldefaultheader')

            alias = ESC_XML(stock_param.get_param('xmlalias'))
            ecrire_schema_xml(rep_s, schema, mode=mode, cod='utf-8',
                              header=header, alias=alias)

        if form == 'xml_d':

            header = stock_param.get_param('xmlheader_dist', '')
            prefix = stock_param.get_param('xmlprefix_dist', 'd')
            if header:
                header = header+'\n'
#            header = ''
#            header = header+stock_param.get_param('xmldefaultheader')

                alias = ESC_XML(stock_param.get_param('xmlalias'))
                ecrire_schema_xml(rep_s, schema, mode=mode, cod='utf-8',
                                  header=header, alias=alias, prefix=prefix)
            else:
                print('header distant (xmlheader_dist) non defini')


def retour_schemas(schemas, mode='util'):
    '''renvoie les schemas pour un retour'''
    retour = dict()
    if mode == 'no':
        return retour
    for i in schemas:
#        print('ecriture schema', i, len(schemas[i].classes))
        if not i:
            continue
        nom = schemas[i].nom
        mode_sortie = schemas[i].mode_sortie if schemas[i].mode_sortie is not None else mode
        if i.startswith("#") and mode_sortie != 'int':
            continue # on affiche pas les schemas de travail
        if schemas[i].origine == 'G':
            FSC.analyse_conformites(schemas[i])
#        print ('avant analyse ',i,len(schemas[i].classes),len(schemas[i].conformites))
        if FSC.analyse_interne(schemas[i], mode_sortie):
            retour[nom] = ecrire_schema_csv(None, schemas[i], mode, modeconf=-1)
    return retour


def ecrire_schemas(stock_param, mode='util', formats='csv', confs=-1):
    '''prepare les schemas pour la sortie '''
    print('ecriture_schemas', mode, stock_param.schemas.keys())
    if mode == 'no':
        return
    rep_sortie = stock_param.get_param('_sortie')
    print('sio:repertoire sortie schema', rep_sortie,formats)
#        raise FileNotFoundError

    for i in formats.split(','): # en cas de format inconnu on sort en csv
        if i not in ['csv', 'xml'] and 'sql' not in i:
            formats = formats+',csv'
            break

    schemas = stock_param.schemas
    xml = False

    for i in schemas:
#        print('ecriture schema', i, len(schemas[i].classes))
        if not i:
            continue
        mode_sortie = schemas[i].mode_sortie if schemas[i].mode_sortie is not None else mode
#        print('sortir schema ', i, mode_sortie, len(schemas[i].classes),
#              FSC.analyse_interne(schemas[i], mode_sortie))
        if i.startswith("#") and mode_sortie != 'int':
            continue # on affiche pas les schemas de travail
        if not rep_sortie:

            print('sio:pas de repertoire de sortie ', stock_param.get_param('_sortie'),
                  stock_param.liste_params)
            raise NotADirectoryError('repertoire de sortie non défini')

        rep = os.path.dirname(os.path.join(rep_sortie, schemas[i].fich if schemas[i].fich else ''))
#        nombase = os.path.basename(os.path.join(rep_sortie, schemas[i].fich))
        if stock_param.schemas[i].origine == 'G':
            FSC.analyse_conformites(schemas[i])
#        print ('avant analyse ',i,len(schemas[i].classes),len(schemas[i].conformites))
        if FSC.analyse_interne(schemas[i], mode_sortie):
            formats_a_sortir = set(formats.split(","))
            if schemas[i].format_sortie:
                if schemas[i].format_sortie=='sql':
                    dialecte = False
                    for form in formats_a_sortir:
                        if 'sql:' in form:
                            dialecte = True
                    if not dialecte:
                        formats_a_sortir.add('sql')
                else:
                    formats_a_sortir.add(schemas[i].format_sortie)
#controle du sql et de ses dialectes
#            print('sio:analyse interne ', i, len(schemas[i].classes), formats, mode_sortie)
            ecrire_au_format(schemas[i], formats_a_sortir, stock_param, mode_sortie, confs)
            if 'xml' in formats_a_sortir:
                xml = True

    if xml:
#        print("ecriture xsl local", rep)
        copier_xsl(rep)
