# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965

#titre||fonctions auxiliaires

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
# from pyetl.formats.formats import Stat
import logging
from pyetl.formats.interne.stats import Stat, Statdef

LOGGER = logging.getLogger(__name__)

# fonctions de remplacement
def setajout(regle, liste):
    """cree l'ajout d'attributs au schema si necessaire"""
    regle.changeschema = "#schema" in regle.params.att_sortie.liste
    regle.changeclasse = (
        "#classe" in regle.params.att_sortie.liste
        or "#groupe" in regle.params.att_sortie.liste
    )
    # print("setajout", regle.params.att_sortie.liste, regle.changeclasse, regle)
    if not regle.action_schema and not all(i.startswith("#") for i in liste):
        regle.action_schema = fschema_ajout_attribut
        # print("-----regle.action_schema", liste, regle.action_schema)


def sh_simple(regle):
    """ helper pour les sorties simples"""
    setajout(regle, [regle.params.att_sortie.val])


def sh_liste(regle):
    """ helper pour les sorties listes"""
    setajout(regle, regle.params.att_sortie.liste)


def sh_dyn(regle):
    """ helper pour les sorties dynamiques"""
    regle.changeschema = True
    regle.changeclasse = True
    regle.dynschema = True
    regle.action_schema = fschema_ajout_attribut_d


def s_hstore(sortie, obj, valeur):
    """#aide||fonction de stockage d'un hstore
    #pattern||H:A||H
    #shelper||simple
    """
    # print("dans s_hstore")
    if isinstance(valeur, str):
        obj.attributs[sortie.val] = valeur
    else:
        obj.sethtext(sortie.val, dic=valeur)
    return True


def s_hupdate(sortie, obj, valeur):
    """#aide||fonction de stockage d'un hstore
    #pattern||+H:A||H
    #shelper||simple
    """
    # print("dans s_hstore")
    if isinstance(valeur, str):
        if sortie.val in obj.attributs and obj.attributs[sortie.val]:
            obj.attributs[sortie.val] = obj.attributs[sortie.val] + ", " + valeur
        else:
            obj.attributs[sortie.val] = valeur
    else:
        obj.sethtext(sortie.val, dic=valeur, upd=True)
    return True


def s_simple(sortie, obj, valeur):
    """#aide||affectation cree l' attribut si necessaire
    #pattern||A||S
    #pattern1||AE||S
    #pattern2||AN||S
    #pattern3||AD||S
    #shelper||simple
    #test1||X:x||X?||X:x||S:X
    """
    obj.attributs[sortie.val] = valeur


def s_indirect(sortie, obj, valeur):
    """#aide||cree ou affecte une variable indirectement,cree l' attribut si necessaire
    #pattern||[A]||S
    #shelper||dyn
    #test1||X:x||X:Z||Z:x||S:Z

    """
    atts = obj.attributs.get(sortie.val)
    if atts:
        obj.attributs[atts] = valeur
        if obj.schema:
            obj.schema.stocke_attribut(atts, "T")


def s_liste(sortie, obj, valeur):
    """#aide|| affecte un ensemble d'attributs, les cree si necessaire
    #pattern||L||M
    #shelper||liste
    """
    if isinstance(valeur, dict):
        obj.attributs.update([(i, valeur.get(i)) for i in sortie.liste])
    else:
        obj.attributs.update(zip(sortie.liste, valeur))


def s_simple_pre(sortie, obj, valeur):
    """#aide|| ajoute la valeur devant  cree l' attribut si necessaire
    #pattern||+A||S
    #shelper||simple
    """
    obj.attributs[sortie.val] = valeur + obj.attributs.get(sortie.val, "")


def s_simple_post(sortie, obj, valeur):
    """#aide|| cree l' attribut si necessaire
    #pattern||A+||S
    #shelper||simple
    """
    obj.attributs[sortie.val] = obj.attributs.get(sortie.val, "") + valeur


def s_liste_pre(sortie, obj, valeur):
    """#aide|| affecte un ensemble d'attributs cree l' attribut si necessaire
    #pattern||+L||M
    #shelper||liste
    """

    refs = [obj.attributs.get(i, "") for i in sortie.liste]
    vals = ["".join(i) for i in zip(valeur, refs)]
    obj.attributs.update(zip(sortie.liste, vals))


def s_liste_post(sortie, obj, valeur):
    """#aide|| cree l' attribut si necessaire
    #pattern||L+||M
    #shelper||liste
    """
    refs = [obj.attributs.get(i, "") for i in sortie.liste]
    vals = ["".join(i) for i in zip(refs, valeur)]
    obj.attributs.update(zip(sortie.liste, vals))


def s_indirect_pre(sortie, obj, valeur):
    """#aide|| cree l' attribut si necessaire
    #pattern||+[A]||S
    #shelper||dyn
    """
    atts = obj.attributs.get(sortie.val)
    if atts:
        obj.attributs[atts] = valeur + obj.attributs.get(atts, "")
        if obj.schema:
            obj.schema.stocke_attribut(atts, "T")


def s_indirect_post(sortie, obj, valeur):
    """#aide|| cree l' attribut si necessaire
    #pattern||[A]+||S
    #shelper||dyn
    """
    atts = obj.attributs.get(sortie.val)
    if atts:
        obj.attributs[atts] = obj.attributs.get(atts, "") + valeur
        if obj.schema:
            obj.schema.stocke_attribut(atts, "T")


def s_dyn_pre(sortie, obj, valeur):
    """#aide|| cree les attributs dynamiquement en fonction des dictionaires avec prefixe
    #pattern||A*||D
    #shelper||dyn
    """
    pref = sortie.val
    #    print("stockage dynamique", pref, valeur)
    for i in valeur:
        obj.attributs[pref + i] = valeur[i]
        if obj.schema:
            obj.schema.stocke_attribut(pref + i, "T")


def s_dyn_post(sortie, obj, valeur):
    """#aide|| cree les attributs dynamiquement en fonction des dictionaires avec suffixe
    #pattern||*A||D
    #shelper||dyn
    """
    pref = sortie.val
    for i in valeur:
        obj.attributs[i + pref] = valeur[i]
        if obj.schema:
            obj.schema.stocke_attribut(i + pref, "T")


def s_dyn(sortie, obj, valeur):
    """#aide|| cree les attributs dynamiquement en fonction des dictionaires
    #pattern||*||D
    #shelper||dyn
    """
    for i in valeur:
        obj.attributs[i] = valeur[i]
        if obj.schema:
            obj.schema.stocke_attribut(i, "T")


def h_stat(regle):
    """preparation mode stat"""
    regle.modestat = regle.params.cmp1.val
    if regle.debug:
        print("moteur: stat", regle.code_classe)
    # TODO  attention risque de melange des statdefs si on utilise la meme colonne
    regle.id_stat = regle.code_classe
    # statdef = regle.params.statstore.getstatdef(regle.id_stats, debug=regle.debug)
    # statdef.ajout_colonne(regle.params.att_sortie.val, regle.modestat)
    regle.stock_param.statstore.ajout_colonne(
        regle.id_stat, regle.params.att_sortie.val, regle.modestat, debug=regle.debug
    )
    # print("def stats, ", regle.id_stat, regle.stock_param.statstore.statdefs)


def f_stat(regle, obj):
    """#aide||fonctions statistiques
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
    #!test2 ||obj;;4||#classe;;;;T;1;;stat;val||statprint;;||out;
    """
    if obj.virtuel:
        return True
    entree = (obj.attributs.setdefault("#statgroupe", "total"), regle.id_stat)
    # stat = regle.params.statstore.getstat(entree,regle.id_stat)
    # if entree not in regle.stock_param.stats:
    #     regle.stock_param.stats[entree] = Stat(entree, regle.stock_param.statdefs[regle.id_stat])
    # if regle.stock_param.stats[entree].ajout_valeur(
    if regle.stock_param.statstore.ajout_valeur(
        entree,
        obj.attributs.get(regle.code_classe, ""),  # ligne
        regle.params.att_sortie.val,  # colonne
        regle.getval_entree(obj),  # valeur
        regle.params.cmp2.val
        + obj.attributs.get(
            regle.params.att_sortie.val[1:-1], regle.params.att_sortie.val
        ),
    ):
        # print ('regles:fstat ',regle.params.att_sortie[1:-1],
        #        obj.attributs.get(regle.params.att_sortie[1:-1],regle.params.att_sortie),
        #                          obj.attributs.get(regle.params.att_entree, regle.params.val_entree))
        return True
    # print("regles:erreurs_statistiques:", regle.ligne, obj.attributs)
    LOGGER.error("erreurs_statistiques:%s", repr(regle), str(obj.attributs))
    # raise
    return False


# """
# fonctions de gestion des schemas :
#    ces fonctions permettent de synchroniser la definition des schemas avec les
#    modifications d'objets.
#    elles sont appelees apres les actions classiques si les objets comportent des schemas
# """


def fschema_supprime_attribut(regle, obj):
    """supprime un attribut du schema"""
    if obj.schema.amodifier(regle):
        for att in regle.params.att_entree.liste or regle.params.att_sortie.liste:
            obj.schema.supprime_attribut(att)


def fschema_ajout_attribut_d(regle, obj):
    """ajoute un attribut au schema mode dynamique on regarde tout le temps"""
    for att in [a for a in regle.params.att_sortie.liste if a and a[0] != "#"]:
        #        print ('ajout 2',att)
        obj.schema.ajout_attribut_modele(regle.params.def_sortie, nom=att)
    for att in [a for a in regle.ajout_attributs if a and a[0] != "#"]:
        #        print ('ajout 2',att)
        obj.schema.ajout_attribut_modele(regle.params.def_sortie, nom=att)


#    print ('schema', obj.schema.attributs)


def fschema_ajout_att_from_obj_dyn(regle, obj):
    """ajoute des attributs a partir de la definition de l'objet"""
    for att in [a for a in obj.attributs if a and a[0] != "#"]:
        obj.schema.ajout_attribut_modele(regle.params.def_sortie, nom=att)


def fschema_ajout_att_from_liste_d(regle, obj):
    """ajoute des attributs a partir de la definition de l'objet"""
    # print ('ajout attribut',liste)
    if not regle.liste_atts:
        return
    for att in [a for a in regle.liste_atts if a and a[0] != "#"]:
        if att in obj.schema.attributs:
            continue
        # print ('ajout attribut',att)
        obj.schema.ajout_attribut_modele(regle.params.def_sortie, nom=att)


def fschema_ajout_att_from_liste(regle, obj):
    """ajoute un attribut au schema"""
    if obj.schema.amodifier(regle):
        #        print('ajout 1',regle.params.att_sortie,obj.schema.schema.nom)
        fschema_ajout_att_from_liste_d(regle, obj)


def fschema_ajout_att_from_obj(regle, obj):
    """ajoute un attribut au schema"""
    if obj.schema.amodifier(regle):
        #        print('ajout 1',regle.params.att_sortie,obj.schema.schema.nom)
        fschema_ajout_att_from_obj_dyn(regle, obj)


def fschema_ajout_attribut(regle, obj, typedefaut="T"):
    """ajoute un attribut au schema"""
    # print("ajout attribut", regle, regle.params.def_sortie, obj.schema.regles_modif)
    if obj.schema.amodifier(regle):
        # print("ajout 1", regle.params.att_sortie, obj.schema.schema.nom)
        fschema_ajout_attribut_d(regle, obj)


def fschema_set_geom(regle, obj):
    """positionne la geometrie du schema"""
    # print("-----demande modif schema geom", regle.getvar("macromode"), regle)
    if obj.schema.amodifier(regle):
        #        print('modif schema geom', obj.schema.nom, obj.schema.info["type_geom"],
        #        '->', obj.attributs['#type_geom'])
        # print("-----modif schema geom", regle.getvar("macromode"), regle)
        if regle.getvar("macromode") == "geomprocess":
            # print("detecte geomprocess", regle)
            return
            # on est dans un traitement geometrique virtuel on ne touche a rien
        if regle.getvar("type_geom"):
            obj.schema.info["type_geom"] = regle.getvar("type_geom")
        elif obj.geom_v.valide:
            obj.schema.info["type_geom"] = obj.geom_v.type
        else:
            obj.schema.info["type_geom"] = obj.attributs["#type_geom"]
        # print("set type geom", obj.schema.info["type_geom"], regle)


#        print ('--------------------modif schema ',obj.schema.nom,obj.schema.info["type_geom"])


def fschema_rename_attribut(regle, obj):
    """ renomme un attribut"""
    if obj.schema.amodifier(regle):
        #        print ('dans rename_attribut',regle.params.att_entree.val,'->',regle.params.att_sortie.val)
        #        print ('dans rename_attribut',obj.attributs.get(regle.params.att_sortie.val))
        for source, dest in zip(
            regle.params.att_entree.liste, regle.params.att_sortie.liste
        ):
            obj.schema.rename_attribut(source, dest, modele=regle.params.def_sortie)


#        print ( 'renommage' , obj.schema.attributs[regle.params.att_sortie.val].nom )


def fschema_garder_attributs(regle, obj):
    """supprime tous les attributs du schema qui ne figurent pas dans l'objet"""
    #    for att in [i for i in obj.schema.attributs if i not in regle.liste_attributs]:
    #        obj.schema.supprime_attribut(att)
    # print("garder attributs", obj.schema.identclasse, regle.params.att_sortie.liste)
    if obj.schema.amodifier(regle):
        agarder = (
            regle.params.att_sortie.liste
            if regle.params.att_sortie.liste
            else [i for i in obj.attributs if i[0] != "#" and i in regle.selset]
        )
        obj.schema.garder_attributs(agarder, ordre=regle.params.att_sortie.liste)
    # print("garder attributs ->", obj.schema)


def fschema_change_schema(regle, obj):
    """changement de schema """
    nom_schema = obj.attributs.get("#schema")
    if not nom_schema:
        # print("F-schema: schema sans nom ", obj, regle.ligne)
        # raise
        return
    if obj.schema is None:
        schema2 = regle.stock_param.init_schema(
            nom_schema,
            fich=regle.nom_fich_schema if regle.nom_fich_schema else nom_schema,
            origine="S",
        )
        schema_classe = schema2.setdefault_classe(obj.ident)
        obj.setschema(schema_classe)
        return

    if nom_schema == obj.schema.schema.nom:
        return
    schemaclasseold = obj.schema
    schema2 = regle.stock_param.init_schema(
        nom_schema,
        fich=(regle.nom_fich_schema if regle.nom_fich_schema else nom_schema),
        origine="S",
        modele=obj.schema.schema,
    )
    #    print ('schema2 ',schema2.classes.keys())
    ident = obj.ident
    schema_classe = schema2.get_classe(ident)
    if not schema_classe:
        #        print ("moteur : copie schema ", nom_schema, ident,  schema2.nom)
        #        raise
        schema_classe = obj.schema.copy(ident, schema2, filiation=True)
    if schema_classe.amodifier(regle):
        mode = regle.getvar("schema_nocase", False)
        if mode:  # on adapte la casse
            #            print('adaptation schema ', mode)
            fonction = lambda x: x.lower() if mode == "min" else lambda x: x.upper()
            schema_classe.adapte_attributs(fonction)

    obj.setschema(schema_classe)
    #    print( 'changement de schema ',schemaclasseold.schema.nom, obj.schema.schema.nom)
    #    print( 'destination',obj.schema.schema.nom, obj.schema.schema.classes.keys())

    if schemaclasseold is None:
        return
    if regle.getvar("supp_schema", False):
        schemaclasseold.schema.supp_classe(schemaclasseold.identclasse)


def fschema_change_classe(_, obj):
    """changement de classe """

    schema2 = obj.schema.schema
    ident = obj.ident
    schema_classe = schema2.get_classe(
        ident, cree=True, modele=obj.schema, filiation=True
    )
    # debug = ("elyre", "ima_2017_psmv")
    # if debug == schema_classe.identclasse:
    #     print(
    #         "change classe",
    #         schema2.nom,
    #         obj.schema.nom,
    #         schema2.classes[debug].nom,
    #         schema2.classes[debug].poids,
    #         schema2.classes[debug].objcnt,
    #         schema2.classes[debug].maxobj,
    #         schema2.classes[debug].a_sortir,
    #         schema2.classes[debug].deleted,
    #         obj.schema.deleted,
    #         obj,
    #     )
    obj.setschema(schema_classe)


def fschema_nochange(regle, obj):
    """ inhibe les changements de schema si non utiles """
    regle.changeschema = None


def fschema_supp_classe(regle, obj):
    """ marque une classe pour suppression dans un schema """
    obj.schema.deleted = True


def fschema_map(regle, obj):
    """gere la fonction de mapping sur l'objet"""
    return


def h_setval(regle):
    """helper de fonctiond'entree"""
    if not regle.params.att_entree.val:
        regle.get_entree = regle.get_defaut
