# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:20:44 2015

@author: Claude unger

traducteur de commandes pour la definition de regles

"""
import os
import re
#import sys
import logging
from pyetl.schema.schema_interne import get_attribut
from pyetl.formats.mdbaccess import recup_table_parametres
from pyetl.moteur.regles import RegleTraitement, ParametresSelecteur
#from pyetl.moteur.selecteurs import Selecteur
from .fonctions.outils import charge_fichier

LOGGER = logging.getLogger('pyetl')

NOMS_CHAMPS_N = ['sel1', 'val_sel1', 'sel2', 'val_sel2',
                 'sortie', 'defaut', 'entree', 'commande', 'cmp1', 'cmp2',
                 'debug', 'vlocs']

# quelques fonction générales
def fdebug(regle, obj):
    '''gestion des affichages de debug'''
    if regle.debug and obj:
        regle.debug = regle.debug-1
        regle.affiche('------debug------>')
        obj.debug("avant", attlist=regle.champsdebug)
        succes = regle.f_init(regle, obj)
        obj.debug("apres", attlist=regle.champsdebug)
        liens_num = regle.branchements.liens_num()
        print("retour fonction ", succes, '->',
              liens_num["ok:"] if succes else liens_num["fail:"],
              regle.branchements.brch[obj.redirect+':'] if obj.redirect else
              regle.branchements.brch['ok:'] if succes else regle.branchements.brch['fail:'])
        if regle.copy:
            print('copy :  ->', liens_num["copy:"], regle.branchements.brch['copy:'])

    else:
        succes = regle.f_init(regle, obj)
    return succes
# =======================================selecteurs============================

class Selecteur(object):
    """ container pour les objets de selection """
    def __init__(self, regle, attribut, valeur, negatif):
        self.regle = regle
        self.fonction = self.true
        self.ligne = attribut + ";" + valeur
        self.v_nommees = {"attr":attribut, "vals":valeur}
        self.select = self.selneg if negatif else self.selpos
        self.info = dict()

    @staticmethod
    def true(*_):
        """toujours vrai"""
        return True

    @staticmethod
    def false(*_):
        """toujours faux"""
        return False

    def selpos(self, obj):
        """selecteur standard """
#        print ("dans select ", self.regle.numero, self.ligne, self.fonction)
        return self.fonction(self, obj)

    def selneg(self, obj):
        """negation"""
#        print (" dans select ",self.ligne, obj)
        return not self.fonction(self, obj)

    def setparams(self, elements, definition):
        """positionne les parametres standard"""
        self.params = ParametresSelecteur(elements, definition)

def choix_fonction_select(attribut, valeur, regle):
    ''' definition d un critere de selection '''
    mapper = regle.stock_param
    debug = regle.getvar("debug") == "1"
    if not (attribut or valeur):
        return None
    isnot = False
    if valeur.startswith('!'):
#        print ('icsv :detection negatif',fonction)
        isnot = True
        valeur = valeur[1:]


    select = Selecteur(regle, attribut, valeur, isnot)
#    debug=1
    for candidat in mapper.sortedsels:
#        print ("test sel ", candidat.nom, candidat.priorite)
        valide, elements, erreurs = validepattern(select, candidat.definition)
#        if elements["attr"] is not None:
#            print ("elements",elements,candidat.definition)
        if valide:
            if debug:
                print("candidat retenu ", regle.numero, candidat.nom,
                      candidat.work, candidat.helper)
            select.setparams(elements, candidat.definition)
            if candidat.helper:
                candidat.helper(select)
            select.fonction = candidat.work
            return select
#    print("erreur selecteur inconnu",regle.ligne.encode('utf8'),'<')
    print("erreur selecteur inconnu", ascii(attribut), ascii(valeur), 'dans:', regle)
    return None




def prepare_selecteur(regle, v_nommees):
    """prepare la fonction de selection de la regle"""
    sel1 = choix_fonction_select(regle.code_classe, v_nommees['val_sel1'], regle)
    sel2 = choix_fonction_select(v_nommees['sel2'], v_nommees['val_sel2'], regle)
    if not sel1:
        sel1, sel2 = sel2, sel1

    if not sel1: # pas de conditions
        select = None
        regle.nocond = True
    elif not sel2:
        select = sel1.select
    else:
        select = lambda x: sel1.select(x) and sel2.select(x)

    regle.selstd = select
#    print("selecteur final",regle.numero, regle.selstd)


def regles_liees(regle, param):
    ''' decode le systeme de regles liees '''
    if param and param[0] in "|+-": # mode de regles liees
        regle.niveau = 0

        while regle.niveau < len(param) and param[regle.niveau] in "|+-":
            regle.niveau += 1
        if param[regle.niveau-1] == '-':
            regle.nonext = True
        for i in regle.branchements.enchainements:
            if param[regle.niveau:regle.niveau+len(i)] == i:
                regle.enchainement = i
                regle.code_classe = param[regle.niveau+len(i):]
        if regle.enchainement == ':':
            regle.enchainement = 'ok:'
            # petite magouille pour coller aux branchements sans alourdir la syntaxe
        if not regle.enchainement:
            err = "erreur de syntaxe "+ regle.ligne[:-1]
            print('liaison:', err)
            raise SyntaxError("liaison non valide")

        if regle.getvar("debug") == '1':
            print('regle liee', param[regle.niveau:], regle.niveau, regle.ligne[:-1])
        return None

#---------------------------fonctions standard--------------------------------

def description_schema(regle):
    '''gere les definitions de schema associees a l'attribut resultat
    la description d'uun attribut prend la forme suivante ([p:]type,[D:defaut],[index])
    p: position du champ : par defaut dernier champ -1 = premier
    type : T E/EL S/BS F D

    description des index :
    PK: : clef primaire
    X: index
    U:  : unique
    FK: : clef etrangere doit etre suivi de la ref schema.table.attribut'''
#TODO: gerer les enums
    type_att_sortie = "T"
    position = -1
    valeur_defaut = ""
    def_index = ""
    desc_schema = regle.params.att_sortie.definition
    if desc_schema:
        if ':' in desc_schema[0]: #( indicateur de position)
            position = int(desc_schema[0][:desc_schema[0].index(':')])
            type_att_sortie = desc_schema[0][desc_schema[0].index(':')+1:]
        else:
            type_att_sortie = desc_schema[0]
        if not type_att_sortie:
            type_att_sortie = 'A'
        if len(desc_schema) > 1:
            if desc_schema[1][:2] == "D:":
                valeur_defaut = desc_schema[1][2:]
            else:
                def_index = desc_schema[1]
        if len(desc_schema) > 2:
            def_index = desc_schema[2]
    # on cree un attribut modele pour la sortie
    modele = get_attribut('modele', 30)
    modele.nom_court = ''
    modele.type_att = type_att_sortie
    modele.type_att_base = modele.type_att
    modele.defaut = valeur_defaut
    modele.ordre = position
    modele.def_index = def_index
    regle.params.def_sortie = modele
#    if def_index:
#    print( "modele attribut",modele.type_att, desc_schema, regle.params.att_sortie)

def extraction_operation(regle, fonction):
    ''' isole le code operation de tous les modificateurs '''
    # fonction avec les modificateurs de comportement
    # + : dupplique l'objet  un passe la regle l'autre pas
    # - : mange les objets qui ne passent pas la regle
    # > : sortie des objets passant la regle
    regle.copy = "+" in fonction
    regle.filter = "-" in fonction
    regle.final = ">"in fonction
    regle.supobj = regle.final
    mode = fonction.strip('+-> "')
    regle.mode = mode
    if regle.copy:
        regle.branchements.addsortie('copy:') # on gagne une sortie


def printpattern(commande):
    """affiche la descriprion de la commande (debug)"""
    print('commande ', commande.nom)
    for variante in commande.subfonctions:
        print("sf:   %-10s->%s<- %s,(%s)" % (variante.nom, variante.pattern,
                                             variante.description.get('#aide'),
                                             variante.clef_sec))

def printelements(elements):
    """affiche les elements detectes par les expressions regulieres (debug)"""
    print("int: parametres detectes")
#    print (elements)
    for i in elements:
#        print(i,elements[i])
        print(i, elements[i].groups(), elements[i].re)

def validepattern(regle, definition):
    """validation de la signature d'une fonction"""
#    print (definition)
    try:
        elements = {i:definition[i].match(regle.v_nommees[i]) for i in definition}
#        print ('elements',elements)
    except KeyError:
        print("definition erronnee", regle.ligne, definition)
    valide = None not in elements.values()
    explication = [i+':'+definition[i].pattern+'<>'+regle.v_nommees[i]
                   for i in elements if elements[i] is None]
    return valide, elements, explication


def select_fonc(regle, fonc):
    """validation de la signature d'une fonction"""
    definition = fonc.definition
    clef = fonc.clef_sec
#    print ("signature", regle, definition, clef)
#    if clef and clef != "-1":
#        print(definition[clef].match(regle.v_nommees[clef]))
    if clef == 'sortie' and fonc.fonctions_sortie: # on teste les sorties comme clef
#        print ('test des fonctions de sortie ',clef,'->',definition[clef])
        for j in sorted(fonc.fonctions_sortie.values(), key=lambda x: x.priorite):
#            print ('test ', j.nom,j.definition[clef])
            if j.definition[clef].match(regle.v_nommees[clef]):
#                print ('sortie validable ', j.definition[clef])
                return True
#        print ('aucune sortie validable')
        return False
    if clef and clef != '-1':
#        print ('select_fonc',clef,regle.v_nommees[clef],
#        definition[clef].match(regle.v_nommees[clef]))
        return definition[clef].match(regle.v_nommees[clef])
    return True


def set_resultat_regle(regle, fonc):
    ''' positionne la fonction de sortie de la regle'''
    cref = "sortie"
    elements = regle.elements
#                for j in sorted(fonc.fonctions_sortie.values(),key=lambda x:x.priorite):
#                    print ('ordre choix ',j.work)
    for j in sorted(fonc.fonctions_sortie.values(), key=lambda x: x.priorite):
#                print ('sortie')
        if j.definition[cref].match(regle.v_nommees[cref]):
            regle.fstore = j.work
            regle.action_schema = regle.action_schema or j.fonction_schema
            regle.shelper = j.helper
#            if not regle.action_schema:
#                print('erreur action', j.nom, j.fonction_schema,
#                      fonc.nom, regle.ligne[:-1])
            elements[cref] = j.definition[cref].match(regle.v_nommees[cref])
            break
#                print ('fonction sortie',regle,'sortie:',j.work)
    if regle.fstore:
        return True
    regle.erreurs.append("erreur sortie")
    elements[cref] = None
    return False

def identifie_operation(regle):
    ''' identifie la fonction a appliquer et recupere les parametres '''
    fonction = regle.stock_param.commandes[regle.mode]
#    print ('detecte commande',regle.valide, regle.mode, regle.ligne, fonction.nom)
#        printpattern (fonction)
#        definitions=[i.definition for i in fonction.subfonctions.values()]
    elements = None
    definition = None
    valide = False
    fonc = None
    regle.elements = None
    erreurs = []
#    print( 'traitement fonction',fonction.nom,erreurs)
    if regle.mode == "":
        print("mode non defini", regle.ligne)
        return valide, fonc
    for fonc in fonction.subfonctions:
        if fonc.style != regle.style:
            continue
        if select_fonc(regle, fonc):
            valide, elements, erreurs = validepattern(regle, fonc.definition)
#            print( 'recherche pattern',fonc.nom,erreurs)
            definition = fonc.definition
            if valide:
                break
    else:
        afficher_erreurs(regle, fonction, "fonction non valide")
        return valide, fonc

    if callable(fonc.work):
        regle.fonc = fonc.work
        regle.action_schema = fonc.fonction_schema
        regle.elements = elements
        if fonc.fonctions_sortie:
            valide = set_resultat_regle(regle, fonc)
            if not regle.fstore:
                afficher_erreurs(regle, fonc, "fonction de sortie non valide")
#        print ("regle.setparams", regle.elements, definition)
        regle.setparams(regle.elements, definition)
        return valide, fonc

    afficher_erreurs(regle, fonc, "fonction non implementee:")
    return False, fonc
#            print ("fonction sortie a traiter",len(fonc.fonctions_sortie),
#                   fonc.fonctions_sortie)



def afficher_erreurs(regle, fonc, message):
    '''donne des indications sur les erreurs de syntaxe'''
    motif = '------->'
    print(motif+' erreur interpretation regle', regle.fichier, regle.numero,)
    print(motif, regle.ligne.replace("\n", ""))
    print(motif, message)
    if regle.erreurs:
        print(motif, '\n'.join(regle.erreurs))
    if not regle.mode: # pas de mode en general un decalage
        print(motif, "regle vide")
        morceaux = regle.ligne.replace("\n", "").split(";")
        morceaux[7] = "???"
        print(motif, ";".join(morceaux))
    if regle.elements:
        for i in regle.elements:
            if regle.elements[i] is None:
                print(motif +'erreur commande>', regle.mode, '<', i, fonc.nom if fonc else '',
                      fonc.definition[i].pattern if fonc else '', '<-//->', regle.v_nommees[i])
    else:
        fonction = regle.stock_param.commandes.get(regle.mode)
        if fonction:
            patternlist = [i.pattern for i in fonction.subfonctions if i.style == regle.style]
            print(motif+' patterns autorises ', patternlist)
    raise SyntaxError('erreurs parametres de commande')

def traite_helpers(regle, fonc):
    """execute les fonctions auxiliaires """
    if fonc.helper:
        # la fonction prevoit une sequence d'initialisation : on l'execute
#                print ("execution helper",fonc.nom)
        mode_orig = regle.mode
        fonc.helper(regle) # on prepare les elements
#                print ('retour', regle.valide)
        if regle.mode != mode_orig: # la fonction helper a change la fonction a appeler
            fonc = regle.stock_param.commandes[regle.mode]
            if callable(fonc.work):
                regle.fonc = fonc.work
            else:
                afficher_erreurs(regle, fonc, "fonction non implementee:")
    if regle.shelper:
        regle.shelper(regle)
    if regle.changeclasse:
        regle.changeclasse = fonc.changeclasse
    if regle.changeschema:
        regle.changeschema = fonc.changeschema
    else:
        if regle.action_schema:
            if (regle.params.att_sortie.dyn
                    or "#classe" in regle.params.att_sortie.liste
                    or '#groupe' in regle.params.att_sortie.liste
               ):
                regle.changeclasse = fonc.changeclasse


            if regle.params.att_sortie.dyn or "#schema" in regle.params.att_sortie.liste:
                regle.changeschema = fonc.changeschema
#    if regle.params.att_sortie.val:
    description_schema(regle) # mets en place le schema pour l'attribut de sortie


def analyse_operation(regle):
    ''' identifie la fontion de traitement'''
#    print ('analyse',regle.mode,regle)
    if regle.mode and regle.mode in regle.stock_param.commandes:
        valide, fonc = identifie_operation(regle)
        if valide:
            regle.valide = valide
            traite_helpers(regle, fonc)
    else:
        afficher_erreurs(regle, None, "commande inconnue ->"+regle.mode)
    if regle.valide is None:
        afficher_erreurs(regle, None, 'regle non traitee')
    if not regle.mode or (regle.valide and not regle.fonc):
        afficher_erreurs(regle, None, "regle sans fonction ")




def prepare_regle(regle, valeurs):
    ''' positionne les elements standard de la regle'''
#    print ('prep regle:',regle,regle.valide)

    if len(valeurs) <= 11:
        valeurs.extend(['']*(12-len(valeurs)))
    v_nommees = dict(zip(NOMS_CHAMPS_N, valeurs))
    if not any(valeurs):
        regle.valide = "vide"
    regle.valeurs = valeurs
    regle.v_nommees = v_nommees
    ndebug = 10
    if "debug" in v_nommees['debug']:
        vdebug = v_nommees['debug'].split(',')
        if vdebug[-1].isnumeric():
            ndebug = vdebug.pop()
        regle.debug = int(ndebug)
        if len(vdebug) > 1:
            regle.champsdebug = vdebug[1:]
        print("debug regle ::::", valeurs)
    regle.code_classe = v_nommees['sel1']
#    print ('interpreteur:  ',regle.v_nommees)
    vldef = v_nommees['vlocs']
    if '=>' in vldef:
        listevlocs = [i.strip().strip('"').replace('"=>"', '=')
                      for i in vldef.split('","')] if vldef else []
    else:
        listevlocs = vldef.split(',')
    for i in listevlocs:
#        print('detecte', i)
        nom, val, *_ = i.split('=')+['']
        regle.vloc[nom] = val
#    print( 'detection variables locales ', vldef, listevlocs, regle.vloc)
    # decodage des liens entre regles (structure de blocs)
#    param = valeurs[0]
    # premier parametre : nom de la classe avec elements de structure
    # de la forme [\+*][sinon|fail]:nom_d'attribut
    regles_liees(regle, v_nommees['sel1'])
#    print ('2regle:',regle,regle.valide)
    if regle.code_classe[:3] == 'db:': # mode d'acces a la base de donnees
        regle.selstd = Selecteur.true
        regle.valide = True
#        print ("interp: mode dbaccess",regle.code_classe,regle.mode,regle)
    else:
        prepare_selecteur(regle, v_nommees)

    fonction = v_nommees["commande"]
#    regle.valide = "vide"
    if fonction:
        extraction_operation(regle, fonction)
        analyse_operation(regle)
    else:
#            if re.match('^( *;*)*$',regle.ligne):
        if regle.valide != "vide":
            print(regle.stock_param.nompyetl, regle.stock_param.idpyetl, regle.valide,
                  '------>regle sans fonction', regle.numero)
            morceaux = regle.ligne.replace("\n", "").split(";")
            morceaux[7] = "???"
            print('                ------>', ";".join(morceaux))
#            print('decodage champs', ' '.join([i+'->'+j for i, j in regle.v_nommees.items()]))
            raise SyntaxError('regle sans fonction')
#        else:
#            print ('regle vide',regle,regle.valide)
#    if regle.valide:
#        analyse_operation(regle)
    return regle.valide
#            if regle.mode in regle.init_schema:
#                regle.traitement_schema = True # on active le traitement des schemas

def map_vars(mapper, ligne, vloc=None):
    '''gere le mapping des variables positionelles avec fallback sur les globales'''
#TODO non géré pour le moment : l'affectation dynamique de variables ne marche pas
    binding = dict()
#    print('mv:ligne',ligne)
    if vloc is None:
        vloc = dict()
    for j in mapper.param_exp.findall(ligne): # substitution des parametres positionnels
        nom_param = j.replace('%', '')

#        if '#' in nom_param: # cest une reference a un groupe de parametres (bases de donnees)
#            tmp = nom_param.split('#')
#            modif_nom = '_'+vloc.get(tmp[1], mapper.get_param(tmp[1], ''))
#            nom = tmp[0]+modif_nom
##            print (" modifieur",modif_nom,mapper.parms)
#        else:
#            nom = nom_param


        ligne = ligne.replace(j, vloc.get(nom_param, mapper.get_param(nom_param, '')))
#        print ('icsv:substitution >'+j+"<>"+nom_param+'<',vloc.get(nom_param,
#               mapper.get_param(nom,'')),ligne)
        binding[nom_param] = vloc.get(nom_param, nom_param)
        if mapper.param_exp.search(ligne): # double indirections
            ligne, binding2 = map_vars(mapper, ligne, vloc)
            binding.update(binding2)
#        mapper.liens_variables.setdefault(vloc.get(nom, nom), []).append(len(mapper.regles))
#    print('mv:ligne sortie',ligne,sorted(mapper.parms.items()))

    return ligne, binding







def reinterprete_regle(regle, mapper, vloc=None):
    ''' reinterprete les variables d'une regle pour la mise a jour'''
#TODO gerer correctement ce truc
    texte_regle = regle.texte_brut
    texte_regle, binding = map_vars(mapper, texte_regle, vloc)

#    for j in mapper.param_exp.findall(texte_regle): # substitution des parametres positionnels
#        np=j.replace('%', '')
##            print ('icsv:substitution >' , j,'<',vloc.get(np,mapper.get_param(np,'')))
#        texte_regle=texte_regle.replace(j,mapper.get_param(np,''))
    champs_texte = [i[1:-1] if i.startswith("'") else i.strip() for i in texte_regle.split(';')]
    if regle.ligne:
        prepare_regle(regle, champs_texte)


def interprete_ligne_csv(mapper, ligne, fichier, numero, vloc=None):
    '''decode une ligne du fichier cs v de regles
    et la stocke en structure interne'''

    liste_val = [i[1:-1] if i.startswith("'") else i.strip()  for i in ligne.split(';')]

#    print('traitement_ligne', fichier, ligne, liste_val)
    regle = RegleTraitement(ligne, mapper, fichier, numero, vloc=vloc)
    regle.valide = "inconnu"
    prepare_regle(regle, liste_val)
    if regle.valide == "vide":
#        print('regle vide ',regle)
        return None

    if not regle.valide:
        return regle

    if regle.debug:
        print("---------debug ligne--->", regle.numero, regle.ligne)
        regle.f_init = regle.fonc
        regle.fonc = fdebug

    mapper.done = False
    if regle.valide == 'done':
        # c'est une regle qui n'a pas de consequences sur les objets
        mapper.done = True # on a fait qque chose
        return None

    return regle

def decoupe_liste_commandes(mapper, fichier_regles, vloc):
    ''' gere les cas ou la liste de commandes est un assemblage complexe de macros'''

    liste_regles = []
    pars = []
#    print ('decoupe_liste',fichier_regles, vloc)
    if fichier_regles.startswith("[") and fichier_regles.endswith("]"):
        fichier_regles = fichier_regles[1:-1]
    if fichier_regles.startswith("'") and fichier_regles.endswith("'"):
        fichier_regles = fichier_regles[1:-1]
    if "'," in fichier_regles or ",'" in fichier_regles:
        liste_commandes = re.split("' *, *'", fichier_regles)
    else:
        liste_commandes = fichier_regles.split(',')
#        commande, *pars = liste_commandes[0].split(",")
    for i in liste_commandes:
        cmd, *pars = i.split("|" if '|' in i else ':')
        macro = mapper.macros.get(cmd)

        LOGGER.debug('lecture macro '+cmd+','+str(pars))

#                liste_regles.append("<"+i.replace(",",";"))"
#                print("regles transmises", liste_regles)
        if macro:
            vpos = [i for i in pars if not "=" in i]
#            macroenv = mapper.macros.getenv(vpos)
            if vpos:
                vloc.update(macro.bind(vpos))
            LOGGER.debug('macro:variables positionelles '+str(vpos)+str(vloc))

            liste_regles.extend(macro.get_commands())
#                print('recup lignes macro:',macro.get_commands())
        else:
            print(mapper.nompyetl, 'macro: commande inconnue >'+i+
                  '< entrez #help pour la liste des commandes')
            print('regles a interpreter', liste_commandes)
#                print('macros ', mapper.macros.keys())
            raise SyntaxError('macro inconnue '+i)

    return liste_regles

def lire_commandes_en_base(mapper, fichier_regles, vloc):
    ''' lit les commandes en base de donnees'''
    defs = fichier_regles.split(':')
    if len(defs) != 2:
        print('erreur commande en base de donnees la commande doit'
              'avoir le format suivant  #db:nom')
        raise SyntaxError('erreur script en base: ' + fichier_regles)
    nom = defs[1]
    mapper.load_paramgroup('dbscriptmode')
    serv = mapper.get_param('scriptserver')
    nomschema = mapper.get_param('scriptschema')
    LOGGER.info("lecture commande en base "+serv)
#    print('lire_db: chargement ', serv)
    mapper.load_paramgroup(serv, nom=serv)
#        print ('parametres',mapper.parms)
    type_base = mapper.get_param('db_'+serv)
#        base = mapper.get_param('base_'+serv)
    if nom.startswith('#'):
        nomtable = mapper.get_param('macrotable')
    else:
        nomtable = mapper.get_param('scripttable')
#    print('lecture de regles en base ', serv, type_base, nomschema+"."+nomtable,
#          "->", nom)
    recup = recup_table_parametres(mapper, serv, nomschema, nomtable, clef='nom',
                                   valeur=nom, ordre='ordre', type_base=type_base)

    liste_regles = [(v[3], ';'.join([str(i) if i is not None else ''
                                     for i in v[4:]])) for v in recup]

#    print('regles lues en base:', serv, nom, liste_regles)

    return liste_regles





def _lire_commandes(mapper, fichier_regles, vloc, niveau):
    '''lit les commandes quelle que soit l'origine base de donnees fichier ou macro'''
#    print(" lecture",fichier_regles)
    if fichier_regles.startswith('#db:'): # acces a des commandes en base de donnees
        liste_regles = lire_commandes_en_base(mapper, fichier_regles, vloc)


    elif fichier_regles.startswith('#') or fichier_regles.startswith("['#"):
#       assemblage complexe de macros
        liste_regles = decoupe_liste_commandes(mapper, fichier_regles, vloc)

    else:
        liste_regles = charge_fichier(fichier_regles, "", defext=".csv")

    if niveau: # on force un niveau d'indentation
        avant = niveau
#        avant = '+'*niveau
        regle2 = []
        for regle in liste_regles:
            num, texte = regle
            if texte:
                prefixe = avant if texte[0] in '|+-' else avant+':'
                texte = prefixe+texte
            regle2.append((num, texte))

        liste_regles = regle2

    return liste_regles


def affecte_variable(mapper, commande, vloc):
    ''' affecte une variable avec gestion des valeurs par defaut'''
    commande, binding = map_vars(mapper, commande, vloc)
    modif = r'\;' in commande # gestion des ';' comme parametre
#    print('affecte',commande,modif)
    affectation = commande.split(';')[0][1:]
#            print ('affectation:',affectation)
    pos_egal = commande.index('=')
    val_var = ''
    if pos_egal != -1: # c'est une affectation
#        print ('affectation ', affectation[:pos_egal-1], '->'+affectation[pos_egal:]+'<-')
        if not affectation[pos_egal:]: # parametre vide
            tmp_s = commande.split(';')[1:-1] # on regarde s'il y a une valeur par defaut
#            print ('defauts',tmp_s)
#                    print ('init',i)
            for j in tmp_s:
                if j:
                    val_var = j
                    break
            if val_var:
                if val_var == '#env' and commande.split(';')[2]:
                # on affecte une variable d'environnement
                    mapper.parms[affectation[:pos_egal-1]] =\
                        mapper.env.get(commande.split(';')[2], '')
                else:
                    mapper.parms[affectation[:pos_egal-1]] = val_var
#                print ('affectation defaut',affectation[:pos_egal-1],'->',val_var)
        else:
            vtmp = affectation[pos_egal:]
            valeur = vtmp[1:-1] if vtmp.startswith("'") else vtmp.strip()

            mapper.parms[affectation[:pos_egal-1]] = valeur if not modif else ';'
#            print ('affectation ', affectation[:pos_egal-1], '->'+affectation[pos_egal:]+'<-')
#    print ('final',affectation[:pos_egal-1],'->'+mapper.parms[affectation[:pos_egal-1]]+'<-')


def prepare_texte(defligne):
    ''' prepare le texte pour l 'interpretation et verifie s 'il y a des choses a faire '''
    numero, texte_brut = defligne
#        texte_brut = texte
    texte = texte_brut.strip()
    if not texte:
        return None, None, texte_brut
    if re.match(r"^[\+\-\|]*:?!", texte):
        return None, None, texte_brut
    if texte[0] == '"': # on a mis des cotes dans les champs : petite touille pour nettoyer
        tmp = texte.replace('""', '&&trucmuch&&') # on sauve les doubles cotes
        tmp = tmp.replace('"', '')
        texte = tmp.replace('&&trucmuch&&', '"')
    return numero, texte, texte_brut






def traite_regle_std(mapper, numero, texte, texte_brut, vloc, fichier_regles, bloc):
    ''' traite une regle classique '''
#    texte = texte_brut.strip()
    erreurs = 0
    texte, binding = map_vars(mapper, texte, vloc)
#            print ('interpretation',i)
#            if mapper.init: # on rentre dans les commandes : on initialise les es
#                mapper.gestion_pospars()
    try:
        r_cour = interprete_ligne_csv(mapper, texte, fichier_regles, numero, vloc=vloc)
#                print ('interp regle',i,erreurs)
    except SyntaxError:
#        print( 'syntaxerror ',r_cour)
        erreurs = 1
        raise
#            print ('icsv:traitement ligne ',i[:-1], r_cour)
#            print ('retour',r_cour)
    if r_cour is None:
        return bloc, 0
    if r_cour.valide:
        r_cour.texte_brut = texte_brut
        r_cour.bloc = bloc
        bloc += r_cour.ebloc # gestion des blocs
        if bloc < 0:
            print("erreur structure de blocs", bloc, numero, texte)
            erreurs = 1
        position = len(mapper.regles)
        mapper.regles.append(r_cour)
        for i in binding: # enregistre les regles dynamiques
            mapper.bindings.setdefault(texte, []).append(r_cour)
        if position:
            mapper.regles[position-1].branchements.suivante = r_cour
        r_cour.suivante = None
        r_cour.index = position
#                print ('regle valide ', r_cour.ligne, r_cour.val_entree, r_cour.valide)
    else:
        print('interp: regle invalide -------------->', r_cour)
        if r_cour.erreurs:
            print('\t', r_cour.erreurs)
        print('decodage champs', ' '.join([i+'->'+j for i, j in r_cour.v_nommees.items()]))
        erreurs = 1
    return bloc, erreurs


def prepare_importe_macro(mapper, texte, vloc, fichier_regles):
    ''' importe une macro et l 'interprete'''
#    numero, texte_brut = defligne
#    texte = texte_brut.strip()
#    texte_brut = texte
    match = re.match(r'(([\|\+-]+)([a-z]*):)?(<.*)', texte)
#            niveau = len(match.group(2)) if match.group(2) else 0 +(1 if match.group(3) else 0)
    niveau = match.group(2) if match.group(2) else ""+("+" if match.group(3) else "")
    texte = match.group(4)
    texte, binding = map_vars(mapper, texte, vloc)
    champs = texte.split(';')
    nom_inclus = champs[0][1:].strip()
    vpos = [champs[i] for i in range(1, len(champs)) if not "=" in champs[i]]
    settings = {i.split["="][0]:i.split["="][1]
                for i in range(1, len(champs)) if "=" in champs}

#    print ('lecture macro',texte_brut,'->',texte,vloc, nom_inclus, vpos, settings)
#            vloc = dict()

    localmacro = dict() if vloc is None else vloc
    if nom_inclus[0] == "#":
        inclus = nom_inclus #macro
        macro = mapper.macros.get(inclus)
        if macro:
            localmacro.update(macro.bind(vpos)) # affectation des variables locales
    else:
        inclus = os.path.join(os.path.dirname(fichier_regles), champs[0][1:])
#            print("lecture de regles incluses", inclus,pps)
    localmacro.update(settings)
#            print ("demarrage macro",vloc)
    erreurs = lire_regles_csv(mapper, inclus, vloc=localmacro, niveau=niveau)
    return erreurs

            # fichier inclus

def initmacro(mapper, texte, fichier_regles):
    ''' initialise le stockage '''
    champs_macro = texte.split(';')
    nom = champs_macro[1]
    vlocmacro = [i for i in champs_macro[2:] if i]
    macro = mapper.regmacro(nom, file=fichier_regles, vloc=vlocmacro)
#            print('enregistrement macro',nom)
    return macro



def lire_regles_csv(mapper, fichier_regles, numero_ext=0, vloc=None, liste_regles=None, niveau=""):
    ''' lecture des fichiers de regles '''
    erreurs = 0
#    mstore = False
    autonum = 0
    macro = None
    if vloc is None:
        vloc = dict()
    if liste_regles is None:
        liste_regles = []
    else:
        liste_regles = liste_regles
    numero = numero_ext
#    print ('dans lire_regles', fichier_regles, liste_regles)

    if fichier_regles:
        liste_regles = _lire_commandes(mapper, fichier_regles, vloc, niveau)

#        print ('regles lues \n',''.join(str(liste_regles)))

    bloc = 0
    for defligne in liste_regles[:]:
#        print ('lecture regle', defligne)
#        numero, texte = defligne
        numero, texte, texte_brut = prepare_texte(defligne)

        if texte is None:
            continue
# lignes conditionelles (lignes incluses dans le code seulement si la condition est vraie)
# sous la forme K:variable:valeur ou K:variable
        liste_val = texte.split(';', 1)
        if texte.startswith('K:') and not macro:
            liste_val = texte.split(';', 1)
            cond, binding = map_vars(mapper, liste_val[0], vloc)
            condmatch = re.match("^K:(.*?):(.*)", cond) or re.match("^K:(.*)", cond)
#            print( "lire: condmatch",condmatch, cond,liste_val[0])
            if condmatch: # interpretation conditionelle
#                print( "lire: trouve condmatch",condmatch.groups(), liste_val[0])
                if condmatch.group(1) == '':
                    continue
                if condmatch.lastindex == 2 and condmatch.group(1) != condmatch.group(2):
                    continue
                defligne = (defligne[0], texte_brut.split(';', 1)[1])
        #        liste_val[0] = ''
        #        liste_val[1] = ''
                numero, texte, texte_brut = prepare_texte(defligne)
#                print('traitement_ligne', texte)


# enregistrement d'une macro

        if texte.startswith('&&#define'):
            macro = initmacro(mapper, texte, fichier_regles)
            continue

        elif texte.startswith('&&#end'):
            if not macro: # cas particulier on est dans un schema de
#                           scripts multiples enchaines: on transforme les autres en macros locales
                autonum += 1
                nom = '#autochain_'+autonum
                texte = ';;;;;'+nom+';;;batch;;'
                macro = mapper.regmacro(nom, file=fichier_regles)
            else:
                macro = None
                continue
        elif macro:
#            print('stockage macro',texte,numero)
            macro.add_command(texte, numero)
            continue

#        print ('icsv: regle ',i)

        elif texte.startswith("$#"):
            ligne, binding = map_vars(mapper, texte, vloc)
#            print('map _vars ' ,i, ligne)
            champs_var = ligne.split(';')+['']*3
            vgroup = champs_var[0][2:].strip()
            ngroup = champs_var[1].strip() if champs_var[1].strip() else vgroup
            check = champs_var[2].strip() # verif si le groupe n'a pas ete defini d'une autre facon
#            print ("avt chargement groupe", vgroup, champs_var)

            mapper.load_paramgroup(vgroup, nom=ngroup, check=check)

            # genere des variables internes de la forme 'nomDefiniDansLeFichier_nomDuGroupe
#            print ("apres chargement groupe",vgroup,ngroup)
#            print ("variables", mapper.parms)

        elif texte.startswith("$"):
            affecte_variable(mapper, texte, vloc)

        elif re.match(r'(([\|\+-]+)[a-z_]*:)?<', texte):
#            print ('avant macro',vloc)
            erreurs += prepare_importe_macro(mapper, texte, vloc, fichier_regles)

        else:
#            print('regles std', defligne)
            bloc, errs = traite_regle_std(mapper, numero, texte, texte_brut,
                                          vloc, fichier_regles, bloc)
            erreurs += errs
#            print('apres,regles std', defligne, errs)

    if bloc != 0:
        erreurs += 1
        print("erreur structure de blocs", bloc)
    mapper.debug = int(mapper.get_param('debug'))
    if mapper.debug:
        print("niveau debug :", mapper.get_param('debug'))
        # on initialise les parametres our finir #print 'parametres ', i
#    print('fin lecture regles',erreurs)
    return erreurs
