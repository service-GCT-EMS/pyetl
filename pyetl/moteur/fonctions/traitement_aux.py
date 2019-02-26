# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965


fonctions de sortie et de schema auxiliaires

 description des patterns pour les fonctions :
     un pattern est la description de la syntaxe de la fonction, il est déclare dans
     la docstring de la fonction sous la forme '#patternX||description||clef'
         si une fonction accepte plusieures descriptions il est possible de declarer
         des patterns 1 a N
         la clef est un champs permettan de faire la distinction entre les differents
         patterns autorises
         la description comprend 5 champs (eventuellemnt vides) seule la commande
         est obligatoire
     chaque description comprend 5 champs sous la forme:
     C1;C2;C3;C4;C5;C6
     C1: sortie
         A : attribut
         L : liste
         [A] : indirect
         =nom : nom impose

         modifieurs +  : composition autorisee
                    ?  : facultatif

    C2: defaut
        C   : chaine de caractère
        [A] : indirect
        N   : numerique
    C3: entree
        A: attribut
        L liste
        / obligatoire si pas defaut
        :NC expression de calcul
    C4: commande
    C5: parametre 1
    C6: parametre 2

 description des tests:


"""
#from pyetl.formats.formats import Stat

from pyetl.formats.formats import Stat, Statdef
from pyetl.schema.fonctions_schema import copyschema


# fonctions de remplacement

def sh_simple(regle):
    """ helper pour les sorties simples"""
    regle.changeschema = regle.params.att_sortie.val == "#schema"
    regle.changeclasse = regle.params.att_sortie.val in ("#groupe", "#classe")
    regle.action_schema = fschema_ajout_attribut
    if regle.params.att_sortie.val and regle.params.att_sortie.val[0] == "#":
        regle.action_schema = None

def sh_liste(regle):
    """ helper pour les sorties listes"""
    regle.changeschema = "#schema" in regle.params.att_sortie.liste
    regle.changeclasse = "#classe" in regle.params.att_sortie.liste or \
                         "#groupe" in regle.params.att_sortie.liste
    regle.action_schema = None
    for i in regle.params.att_sortie.liste:
        if i[0] != "#":
            regle.action_schema = fschema_ajout_attribut

def sh_dyn(regle):
    """ helper pour les sorties dynamiques"""
    regle.changeschema = True
    regle.changeclasse = True
    regle.action_schema = fschema_ajout_attribut_d



def s_simple(sortie, obj, valeur):
    '''#aide||affectation cree l' attribut si necessaire
        #pattern||A||S
        #shelper||simple
        #test1||X:x||X?||X:x||S:X
    '''
    obj.attributs[sortie.val] = valeur

def s_indirect(sortie, obj, valeur):
    '''#aide||cree ou affecte une variable indirectement,cree l' attribut si necessaire
       #pattern||[A]||S
       #shelper||dyn
       #test1||X:x||X:Z||Z:x||S:Z

    '''
    atts = obj.attributs.get(sortie.val)
    if atts:
        obj.attributs[atts] = valeur
        if obj.schema:
            obj.schema.stocke_attribut(atts, 'T')

def s_liste(sortie, obj, valeur):
    '''#aide|| affecte un ensemble d'attributs, les cree si necessaire
        #pattern||L||M
        #shelper||liste
    '''
    obj.attributs.update(zip(sortie.liste, valeur))


def s_simple_pre(sortie, obj, valeur):
    '''#aide|| ajoute la valeur devant  cree l' attribut si necessaire
       #pattern||+A||S
       #shelper||simple
    '''
    obj.attributs[sortie.val] = valeur+obj.attributs.get(sortie.val, '')

def s_simple_post(sortie, obj, valeur):
    '''#aide|| cree l' attribut si necessaire
       #pattern||A+||S
       #shelper||simple
    '''
    obj.attributs[sortie.val] = obj.attributs.get(sortie.val, '')+valeur


def s_liste_pre(sortie, obj, valeur):
    '''#aide|| affecte un ensemble d'attributs cree l' attribut si necessaire
        #pattern||+L||M
        #shelper||liste
    '''

    refs = [obj.attributs.get(i, '') for i in sortie.liste]
    vals = [''.join(i) for i in zip(valeur, refs)]
    obj.attributs.update(zip(sortie.liste, vals))

def s_liste_post(sortie, obj, valeur):
    '''#aide|| cree l' attribut si necessaire
    #pattern||L+||M
    #shelper||liste
    '''
    refs = [obj.attributs.get(i, '') for i in sortie.liste]
    vals = [''.join(i) for i in zip(refs, valeur)]
    obj.attributs.update(zip(sortie.liste, vals))



def s_indirect_pre(sortie, obj, valeur):
    '''#aide|| cree l' attribut si necessaire
       #pattern||+[A]||S
       #shelper||dyn
    '''
    atts = obj.attributs.get(sortie.val)
    if atts:
        obj.attributs[atts] = valeur+obj.attributs.get(atts, '')
        if obj.schema:
            obj.schema.stocke_attribut(atts, 'T')

def s_indirect_post(sortie, obj, valeur):
    '''#aide|| cree l' attribut si necessaire
       #pattern||[A]+||S
       #shelper||dyn
    '''
    atts = obj.attributs.get(sortie.val)
    if atts:
        obj.attributs[atts] = obj.attributs.get(atts, '')+valeur
        if obj.schema:
            obj.schema.stocke_attribut(atts, 'T')

def s_dyn_pre(sortie, obj, valeur):
    '''#aide|| cree les attributs dynamiquement en fonction des dictionaires
       #pattern||A*||D
       #shelper||dyn
       '''
    pref = sortie.val
#    print("stockage dynamique", pref, valeur)
    for i in valeur:
        obj.attributs[pref+i] = valeur[i]
        if obj.schema:
            obj.schema.stocke_attribut(pref+i, 'T')

def s_dyn_post(sortie, obj, valeur):
    '''#aide|| cree les attributs dynamiquement en fonction des dictionaires
       #pattern||*A||D
       #shelper||dyn
       '''
    pref = sortie.val
    for i in valeur:
        obj.attributs[i+pref] = valeur[i]
        if obj.schema:
            obj.schema.stocke_attribut(i+pref, 'T')

def s_dyn(sortie, obj, valeur):
    '''#aide|| cree les attributs dynamiquement en fonction des dictionaires
       #pattern||*||D
       #shelper||dyn
       '''
    pref = sortie.val
    for i in valeur:
        obj.attributs[i+pref] = valeur[i]
        if obj.schema:
            obj.schema.stocke_attribut(i+pref, 'T')



def h_stat(regle):
    '''preparation mode stat'''
    regle.modestat = regle.params.cmp1.val
    if regle.stock_param.debug:
        print("moteur: stat", regle.code_classe)
#TODO  attention risque de melange des statdefs si on utilise la meme colonne
    regle.id_stat = regle.code_classe
    if regle.id_stat not in regle.stock_param.statdefs:
        regle.stock_param.statdefs[regle.id_stat] = Statdef(regle.id_stat,\
                                  regle.stock_param.debug)
    regle.stock_param.statdefs[regle.id_stat].ajout_colonne(regle.params.att_sortie.val,
                                                            regle.modestat)


def f_stat(regle, obj):
    '''#aide||fonctions statistiques
    #aide_spec||nom de la colonne de stat;val;col entree;stat;fonction stat
    #aide_spec1||fonctions disponibles
    #aide_spec2||cnt : comptage
    #aide_spec3||val : liste des valeurs
    #aide_spec4||min : minimum numerique
    #aide_spec5||max : maximum numerique
    #aide_spec6||somme : somme
    #aide_spec7||moy : moyenne
    #pattern||C;?;?A;stat;C;?C
    #test1 cnt||obj;;4||#classe;;;;T;;;stat;cnt||anstat;atv:T:4;
    #test2 somme||obj;;4||#classe;;;;T;1;;stat;somme||anstat;atv:T:4;
    #test3 min||obj;;4||#classe;;;;T;;V0;stat;min||anstat;atv:T:0;
    #test4 max||obj;;4||#classe;;;;T;;V0;stat;max||anstat;atv:T:3;
    #!test2 ||obj;;4||#classe;;;;T;1;;stat;val||statprint;;||end;
    '''
    if obj.virtuel:
        return True
    entree = (obj.attributs.setdefault("#statgroupe", "total"), regle.id_stat)
    if entree not in regle.stock_param.stats:
        regle.stock_param.stats[entree] = Stat(entree,
                                               regle.stock_param.statdefs[regle.id_stat])
    if regle.stock_param.stats[entree].ajout_valeur(\
            obj.attributs.get(regle.code_classe, ""),#ligne
            regle.params.att_sortie.val,             #colonne
            regle.getval_entree(obj), #valeur
            regle.params.cmp2.val+obj.attributs.get(regle.params.att_sortie.val[1:-1],
                                                    regle.params.att_sortie.val)):
        #print ('regles:fstat ',regle.params.att_sortie[1:-1],
#        obj.attributs.get(regle.params.att_sortie[1:-1],regle.params.att_sortie),
#                          obj.attributs.get(regle.params.att_entree, regle.params.val_entree))
        return True
    print('regles:erreurs_statistiques:', regle.ligne, obj.attributs)
    #raise
    return False

#"""
#fonctions de gestion des schemas :
#    ces fonctions permettent de synchroniser la definition des schemas avec les
#    modifications d'objets.
#    elles sont appelees apres les actions classiques si les objets comportent des schemas
#"""


def fschema_supprime_attribut(regle, obj):
    '''supprime un attribut du schema'''
    if obj.schema.amodifier(regle):
        for att in regle.params.att_entree.liste or regle.params.att_sortie.liste:
            obj.schema.supprime_attribut(att)

def fschema_ajout_attribut_d(regle, obj):
    '''ajoute un attribut au schema mode dynamique on regarde tout le temps'''
    for att in [a for a in regle.params.att_sortie.liste if a and a[0] != '#']:
#        print ('ajout 2',att)
        obj.schema.ajout_attribut_modele(regle.params.def_sortie, nom=att)
#    print ('schema', obj.schema.attributs)

def fschema_ajout_att_from_obj_dyn(regle, obj):
    '''ajoute des attributs a partir de la definition de l'objet'''
    for att in [a for a in obj.attributs if a and a[0] != '#']:
        obj.schema.ajout_attribut_modele(regle.params.def_sortie, nom=att)


def fschema_ajout_att_from_liste_d(regle, obj, liste):
    '''ajoute des attributs a partir de la definition de l'objet'''
    if liste is None:
        return
    for att in [a for a in liste if a and a[0] != '#']:
        obj.schema.ajout_attribut_modele(regle.params.def_sortie, nom=att)


def fschema_ajout_att_from_liste(regle, obj, liste=None):
    '''ajoute un attribut au schema'''
    if obj.schema.amodifier(regle):
#        print('ajout 1',regle.params.att_sortie,obj.schema.schema.nom)
        fschema_ajout_att_from_liste_d(regle, obj, liste)



def fschema_ajout_att_from_obj(regle, obj):
    '''ajoute un attribut au schema'''
    if obj.schema.amodifier(regle):
#        print('ajout 1',regle.params.att_sortie,obj.schema.schema.nom)
        fschema_ajout_att_from_obj_dyn(regle, obj)


def fschema_ajout_attribut(regle, obj):
    '''ajoute un attribut au schema'''
    if obj.schema.amodifier(regle):
#        print('ajout 1',regle.params.att_sortie,obj.schema.schema.nom)
        fschema_ajout_attribut_d(regle, obj)

def fschema_set_geom(regle, obj):
    '''positionne la geometrie du schema'''
#    print ('------------------modif schema ',obj.schema.nom,obj.schema.info["type_geom"])
    if obj.schema.amodifier(regle):
#        print('modif schema geom', obj.schema.nom, obj.schema.info["type_geom"],
#        '->', obj.attributs['#type_geom'])
        if regle.getvar('type_geom'):
            obj.schema.info["type_geom"] = regle.getvar('type_geom')
        elif obj.geom_v.valide:
            obj.schema.info["type_geom"] = obj.geom_v.type
        else:
            obj.schema.info["type_geom"] = obj.attributs['#type_geom']
#        print ('--------------------modif schema ',obj.schema.nom,obj.schema.info["type_geom"])



def fschema_rename_attribut(regle, obj):
    ''' renomme un attribut'''
    if obj.schema.amodifier(regle):
#        print ('dans rename_attribut',regle.params.att_entree.val,'->',regle.params.att_sortie.val)
#        print ('dans rename_attribut',obj.attributs.get(regle.params.att_sortie.val))

        obj.schema.rename_attribut(regle.params.att_entree.val, regle.params.att_sortie.val,
                                   modele=regle.params.def_sortie)
#        print ( 'renommage' , obj.schema.attributs[regle.params.att_sortie.val].nom )


def fschema_garder_attributs(regle, obj):
    '''supprime tous les attributs du schema qui ne figurent pas dans l'objet'''
#    for att in [i for i in obj.schema.attributs if i not in regle.liste_attributs]:
#        obj.schema.supprime_attribut(att)

    if obj.schema.amodifier(regle):
        agarder = regle.params.att_sortie.liste if regle.params.att_sortie.liste else \
                  [i for i in obj.attributs if i[0] != '#' and i in regle.selset]
        obj.schema.garder_attributs(agarder, ordre=regle.params.att_sortie.liste)

def fschema_change_schema(regle, obj):
    '''changement de schema '''
    nom_schema = obj.attributs.get("#schema")
    if not nom_schema:
        print('F-schema: schema sans nom ', obj.ident, regle.ligne)
        return False
    if obj.schema is None:
        schema2 = regle.stock_param.init_schema(nom_schema, fich=regle.nom_fich_schema
                                                if regle.nom_fich_schema else nom_schema,
                                                origine='S')
        schema_classe = schema2.setdefault_classe(obj.ident)
        obj.setschema(schema_classe)
        return

    if nom_schema == obj.schema.schema.nom:
        return
    schemaclasseold = obj.schema
    schema2 = regle.stock_param.init_schema(nom_schema,
                                            fich=(regle.nom_fich_schema
                                                  if regle.nom_fich_schema else nom_schema),
                                            origine='S', modele=obj.schema.schema)
#    print ('schema2 ',schema2.classes.keys())
    ident = obj.ident
    schema_classe = schema2.get_classe(ident)
    if not schema_classe:
#        print ("moteur : copie schema ", nom_schema, ident,  schema2.nom)
#        raise
        schema_classe = copyschema(obj.schema, ident, schema2, filiation=True)
    if schema_classe.amodifier(regle):
        mode = regle.getvar('schema_nocase', False)
        if mode: # on adapte la casse
#            print('adaptation schema ', mode)
            fonction = lambda x: x.lower() if mode == 'min' else lambda x: x.upper()
            schema_classe.adapte_attributs(fonction)

    obj.setschema(schema_classe)
#    print( 'changement de schema ',schemaclasseold.schema.nom, obj.schema.schema.nom)
#    print( 'destination',obj.schema.schema.nom, obj.schema.schema.classes.keys())

    if schemaclasseold is None:
        return
    if regle.getvar('supp_schema', False):
        schemaclasseold.schema.supp_classe(schemaclasseold.identclasse)

def fschema_map(regle, obj):
    '''gere la fonction de mapping sur l'objet'''
    return
