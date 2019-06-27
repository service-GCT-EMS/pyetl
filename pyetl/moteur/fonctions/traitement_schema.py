# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de manipulation d'attributs
"""
import re
import os
import logging
import pyetl.schema.fonctions_schema as FSC
from pyetl.schema.schema_interne import Schema, init_schema
from pyetl.formats.interne.objet import Objet
from pyetl.schema.formats_schema.schema_xml import lire_schema_xml
from pyetl.schema.formats_schema.schema_csv import lire_schema_csv
from pyetl.schema.schema_io import lire_schemas_multiples

# from .outils import charge_mapping
LOGGER = logging.getLogger("pyetl")
# fonctions de manipulation de schemas


def f_info_schema_attribut(regle, obj):
    """#aide||recupere des infos du schema de l'objet
       #pattern||A;?C;?A;info_schema;=attribut;||cmp1
       #test1||obj||^V4;C1;;info_schema;attribut;;||atv;V4;1
    """
    # print ("regles:dans info schema ")
    if obj.schema:
        obj.attributs[regle.params.att_sortie.val] = FSC.info_schema(
            obj.schema, "attribut", nom=regle.getval_entree(obj)
        )
        #        print ("regles:info schema ", regle.params.att_sortie,
        #        obj.attributs[regle.params.att_sortie])
        return True
    return False


def f_info_schema(regle, obj):
    """#aide||recupere des infos du schema de l'objet
       #pattern||A;?C;;info_schema;;
       #test1||obj;ligne||^V4;dimension;;info_schema;||atv;V4;2
       #test2||obj;ligne||^V4;type_geom;;info_schema;||atv;V4;2
       #test3||obj;poly||^V4;type_geom;;info_schema;||atv;V4;3

    """
    # print ("regles:dans info schema ")
    if obj.schema:
        obj.attributs[regle.params.att_sortie.val] = FSC.info_schema(
            obj.schema, regle.params.val_entree.val
        )

        #        print ("regles:info schema ", regle.params.att_sortie,
        #        obj.attributs[regle.params.att_sortie])
        return True
    return False


def f_set_schema(regle, obj):
    """#aide||positionne des valeurs de schema (statique)
       #pattern||C;?C;;set_schema;;
       #test1||obj;poly||^type_geom;2;;set_schema;||^V4;type_geom;;info_schema;||atv;V4;2
    """
    schem = obj.schema
    if schem:
        if schem.amodifier(regle):
            FSC.set_val_schema(schem, regle.params.att_sortie.val, regle.params.val_entree.val)
        return True
    return False


def f_set_schema_d(regle, obj):
    """#aide||positionne des valeurs de schema (dynamique)
       #pattern||C;?C;A;set_schema;;
       #test1||obj;poly||^A;2;;set||^type_geom;;A;set_schema;||^V4;type_geom;;info_schema;||atv;V4;2

    """
    schem = obj.schema
    if schem:
        FSC.set_val_schema(
            schem,
            regle.params.att_sortie.val,
            obj.attributs.get(regle.params.att_entree.val, regle.params.val_entree.val),
        )
        return True
    return False


# def supp_schema(regle, obj):
#    '''desassocie un objet d'un schema'''
#    obj.resetschema()


def f_stock_schema(regle, obj):
    """#aide||cree un schema par analyse des objets et l'associe a un objet
       #aide_patt||schema,nom,nombre max de valeurs d enum
       #aide_patt||la variable taux_conformite permet de definir me taux minimum d'objets renseignes
       #pattern||=#schema?;;;schema;C?;?N
       #test||obj;point||^#schema;;;supp||^;;;schema;essai||^V4;type_geom;;info_schema;||atv;V4;1
    """
    if obj.virtuel:
        return False
    if not regle.schema_courant:  # on choisit un nom
        if regle.params.cmp1.val:
            nom_base = regle.params.cmp1.val
        elif obj.schema:
            nom_base = obj.schema.schema.nom
        #            print("detection schema", nom_base)

        else:
            nom_base = obj.attributs.get("#schema", "schema")

        regle.schema_courant = regle.getschema(nom_base)
        if not regle.schema_courant:
            regle.schema_courant = Schema(nom_base)
            regle.stock_param.schemas[nom_base] = regle.schema_courant
        if regle.stock_param.get_param("taux_conformite"):
            print("reglage_taux conformite", int(regle.getvar("taux_conformite")))
            regle.schema_courant.taux_conformite = int(regle.getvar("taux_conformite"))
    FSC.ajuste_schema(
        regle.schema_courant, obj, regle.params.cmp2.num if regle.params.cmp2.num else 30
    )
    if regle.final:  # on force la sortie du schema l' objet est mort il n'a plus besoin de schema
        obj.schema = None
    if regle.params.att_sortie.val:
        obj.schema = regle.schema_courant
    return True


def f_force_alias(regle, obj):
    """#aide||remplace les valeurs par les alias
       #pattern||;;;force_alias;?C;
    """

    # types_entiers = {'E':1, 'entier':1}

    schem = obj.schema
    mode = regle.params.cmp1.num
    if schem:
        if mode and schem.schema.defmodeconf != mode:
            schem.schema.defmodeconf = mode
        # TODO valider le mecanisem de changement de mode alias

        for i in [j for j in obj.attributs.keys() if j and j[0] != "#"]:
            attr = schem.attributs.get(i)
            # print 'test attribut', attr.nom, attr.type_att
            if attr and attr.conformite:
                conf = attr.conformite
                val = obj.attributs[i]
                #                attr.type_att_base = 'T'
                obj.attributs[i] = conf.ajuste_valeur(val)
        #                if obj.attributs['#classe'] == 'as_bassin':
        #                    print("dans force_alias", conf.nom, val, '->', obj.attributs[i])

        return True
    else:
        return False


def f_valide_schema(regle, obj):
    """#aide||verifie si des objets sont compatibles avec un schema
     #pattern||?=#schema;?C;;valide_schema;?=strict;
     #pattern2||?=#schema;?C;;valide_schema;=supp_conf;
     #test||obj||X;1;;;;;;pass||^;;;valide_schema||+:;;;;res;1;;set||atv;res;1
     #test2||obj;point||^type_geom;2;;set_schema||^;;;valide_schema||+fail:;;;;res;1;;set||atv;res;1

    """
    #    print ('fonctions : valide_schema', obj.ident, obj.schema)
    #    raise
    if obj.virtuel:
        #        print('valide_schema : obj virtuel')
        return True
    if regle.params.val_entree.val:
        # on copie le schema pour ne plus le modifier apres ecriture
        regle.change_schema_nom(obj, regle.params.val_entree.val)
    schem = obj.schema
    if schem:
        retour = FSC.valide_schema(schem, obj, regle.params.cmp1.val)
        #        print ('retour validation schema', retour, obj)
        return retour
    #            if not v :
    #                print ("---------------------------------------------------------retour fail ")
    obj.attributs["#erreurs"] = "objet sans schema"
    return False


def h_def_schema(regle):
    """ lecture de schema : preparation
    format: nom du schema (entree ou sortie ou autre )
    cmp1: nom du fichier
    cmp2: extension
    """

    cod = regle.getvar("codec_entree", "cp1252")
    fusion = False
    if regle.params.cmp1.dyn:
        fusion = True
    regle.fichier = regle.params.cmp1.val.replace("*", "")  # nom du fichier
#    print('interpreteur: lire schema_entree', regle.numero, regle.params, regle.fichier)
    nom = regle.params.val_entree.val
    regle.differe = False
    if not regle.fichier:
        LOGGER.error("pas de schema a lire " + regle.ligne)
        regle.valide = False
        return
    if regle.fichier.startswith("#schema:"):  # fichier precharge (base de donnees)
        nomschema = regle.params.cmp2.val
        regle.fichier = nomschema
        if not nom:
            nom = nomschema
        regle.remap = regle.params.att_entree.val == "map"
        regle.valide = True

        if nom != nomschema:
            if nomschema in regle.stock_param.schemas:  # le schema existe deja
                init_schema(
                    regle.stock_param,
                    nom,
                    origine=None,
                    fich="",
                    defmodeconf=0,
                    stable=True,
                    modele=nomschema,
                    copie=True,
                )
            #                print ('copie de schema', nomschema, '->', nom,
            #                       regle.stock_param.worker, regle.getvar('_wid'),
            #                       len(regle.stock_param.schemas[nomschema].classes), '->',
            #                       len(regle.stock_param.schemas[nom].classes))
            #                raise
            else:
                regle.differe = True
        regle.nomschema = nom
        #        print ('demande schema interne',nomschema, '->', nom, 'differe',regle.differe)
        return
    ext = regle.params.cmp2.val

    if re.search(r"\[[CF]\]", regle.fichier):
        regle.statique = False
    else:
        regle.statique = True
        # on precharge le fichier de schema
    if regle.stock_param.rdef:
        regle.fichier = regle.fichier.replace("D:", regle.stock_param.rdef + "/")
    # fichier de jointure dans le repertoire de regles
    if not nom:
        nom = os.path.basename(regle.fichier)

    if not nom:
        LOGGER.error("regle incorrecte" + regle.ligne)
        regle.valide = False
        return

    if regle.params.att_sortie.val == "schema_entree":
        regle.context.setvar("schema_entree", nom)
        LOGGER.info("positionnement schema d entree " + nom)
        regle.valide = "done"  # on a fait le boulot on peut jeter la regle

    if regle.params.att_sortie.val == "schema_sortie":
        regle.context.setvar("schema_sortie", nom)
        LOGGER.info("positionnement schema_sortie " + nom)
        regle.valide = "done"  # on a fait le boulot on peut jeter la regle

    LOGGER.debug("lecture schema " + " ".join((str(regle.numero), nom, cod)))

    if ext == "csv":
        mode_alias = regle.context.getvar("mode_alias", "num")
        cod_csv = regle.context.getvar("codec_csv", cod)
        if fusion:
            regle.stock_param.schemas[nom] = lire_schemas_multiples(
                nom, regle.fichier, mode_alias, cod=cod_csv, fusion=fusion
            )
        else:
            regle.stock_param.schemas[nom] = lire_schema_csv(
                nom, regle.fichier, mode_alias, cod=cod_csv
            )
    else:
        regle.stock_param.schemas[nom] = lire_schema_xml(nom, regle.fichier, cod=cod)
    regle.nomschema = nom
    LOGGER.info(
        "lecture schema " + nom + ":" + str(len(regle.stock_param.schemas[nom].classes)) + "classes"
    )

    regle.remap = regle.params.att_entree.val == "map"


#   print('definition schema entree:', regle.nomschema, len(regle.stock_param.schemas[nom].classes))


def fschema_change_classe(_, obj):
    """changement de classe """

    schema2 = obj.schema.schema
    ident = obj.ident
    schema_classe = schema2.get_classe(ident, cree=True, modele=obj.schema, filiation=True)
    #    print ('regles : changement de classe',obj.schema.identclasse,'--->',
    #           ident,schema_classe.info['type_geom'] )

    obj.setschema(schema_classe)


def f_def_schema(regle, obj):
    """#aide||associe un schema lu dans un ficher a un objet
  #aide_spec||type du schema (entree, sortie ou autre);nom;;lire_schema;nom du fichier;extension
   #pattern1||?=schema_entree;?C;?=map;lire_schema;?C;?C
   #pattern2||?=schema_sortie;?C;?=map;lire_schema;?C;?C
   #pattern3||?=#schema;?C;?=map;lire_schema;?C;?C
       #test||obj;batch||^#schema;;;lire_schema;%testrep%/schemas/pyetl;csv;||atv;#groupe;pyetl
     """

    nom_base = regle.nomschema
    ident = obj.ident
    groupe, nom = ident
    # print "definition schema", nom_base, regle.stock_param.schemas[nom_base]
    # print "schemas", regle.stock_param.schemas.keys()
    # print ('def_schema:',ident,nom_base,regle.stock_param.schemas)
    if nom_base not in regle.stock_param.schemas:
        if regle.differe:  # c'etait un schema interne on le cree
            init_schema(
                regle.stock_param,
                nom_base,
                origine='G',
                fich="",
                defmodeconf=0,
                stable=True,
                modele=regle.params.cmp2.val,
                copie=True,
            )
            print("copie de schema differee", regle.params.cmp2.val, nom_base)
        #            raise
        else:
            LOGGER.error("schema inconnu " + nom_base)
            print("erreur schema inconnu", nom_base)
            return False

    schema = regle.stock_param.schemas[nom_base]
    ident2 = schema.map_dest(ident) if schema.stock_mapping.existe else ident

    schema_classe = schema.get_classe(ident2)
    if not schema_classe:
        schema_classe = schema.get_classe(("", nom))
        if schema_classe:
            schema_classe.setorig((obj.groupe, obj.ident))
    if schema_classe:
        obj.setschema(schema_classe)

        groupe = schema_classe.groupe

        obj.attributs["#groupe"] = groupe
        #            if obj.format_natif == 'shp': # on gere la conversion de noms
        if schema_classe.conversion_noms and regle.remap:
            # print ("moteur : schema shape ", obj.attributs)
            for i in schema_classe.attributs:
                nom_court = schema_classe.attributs[i].nom_court
                if nom_court and nom_court != i:
                    attval = obj.attributs.get(nom_court, "")
                    # print ("moteur : ", nom_court, i, a)
                    obj.attributs[i] = attval
                    if nom_court in obj.attributs:
                        del obj.attributs[nom_court]
        #                print('moteur : renommage ', i, '<-', nom_court)
        # print ("moteur : schema long ", obj.attributs)

        for i in schema_classe.attributs:
            # cas particuliers des entiers et des conformites
            #            print ('---positionnements attributs',i,obj.attributs.get(i,
            #                    'rien trouve'), obj.attributs)
            obj.attributs.setdefault(i, "")
        #            print ('                __apres positionnements attributs',i,obj.attributs.get(i))

        # raise
        if ident2:  # c 'est un mapping
            obj.setidentobj(ident2)
        #            schema2 = obj.schema.schema
        #            schema_classe = schema2.get_classe(ident2, cree=True,
        #                                               modele=obj.schema, filiation=True)
        #            obj.setschema(schema_classe)
        #        print( 'positionnement schema ',obj.schema)
        return True
    else:
        if obj.virtuel:
            obj.schema = None
            return True
        print(
            "regles:", regle.numero, "classe non trouvee", nom_base, ident, "dans ", regle.nomschema
        )
        print("regles: liste classes ", list(schema.classes.keys())[:10], "....")
        obj.schema = None
        return False


def f_match_schema(regle, obj):
    """#aide||associe un schema en faisant un mapping au mieux
    #pattern||;?C;;match_schema;C;?N
"""
    schema_classe = obj.schema
    if schema_classe:
        if schema_classe.attmap is None:
            schema_destination = regle.getschema(regle.params.cmp1.val)
            if not schema_destination:
                return False
            schema_classe.init_mapping(
                schema_destination, regle.params.cmp2.num if regle.params.cmp2.val else 0.5
            )
            if schema_classe.attmap is None:
                return False

        #        schema_classe.remap(obj)
        return True
    return False


def liste_table_traite_stock(regle):
    """retourne la liste des tables du schema"""
    liste = regle.schema_courant.classes.keys()
    nom_groupe = regle.schema_courant.nom
    nom_classe = "liste_tables"
    schemaclasse = regle.schema_courant.setdefault_classe((nom_groupe, nom_classe))
    schemaclasse.stocke_attribut("nom_schema", "T")
    schemaclasse.stocke_attribut("nom_classe", "T")
    for i in liste:
        sch, nom = i
        obj = Objet(nom_groupe, nom_classe)
        obj.attributs["nom_schema"] = sch
        obj.attributs["nom_classe"] = nom
        obj.setschema(schemaclasse)
        regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["next"])
    regle.nbstock = 0
    regle.store = False


def h_liste_tables(regle):
    """pepare la liste des tables"""
    schema = regle.params.cmp1.val
    regle.schema_courant = regle.getschema(schema)
    regle.store = True
    regle.nbstock = 1
    regle.traite_stock = liste_table_traite_stock


def f_liste_tables(regle, obj):
    """#aide||recupere la liste des tables d un schema a la fin du traitement
     #groupe||schema
    #pattern||;;;liste_tables;C;?=reel
    """
    # TODO mettre en coherence avec la commande liste_schema ( a fusionner)
    pass


def h_remap_schema(regle):
    """#aide||effectue des modifications sur un schema en gerant les correspondances"""
    pass


def f_remap_schema(regle, obj):
    """#aide||effectue des modifications sur un schema en gerant les correspondances
    #pattern||=#schema;C;;map_schema;C;;||sortie
"""
    # pattern||;?C;;match_schema;C;?N

    pass


def h_diff_schema(regle):
    """compare les schemas"""
    nomsource = regle.params.val_entree.val
    nomdest = regle.params.att_sortie.val
    schemasource = regle.getschema(nomsource)
    schemadest = regle.getschema(nomdest)


def f_diff_schema(regle, obj):
    """#aide||compare un nouveau schema en sortant les differences
    #pattern||;?C;;compare_schema;C;?N
    #patternC||C;C;;compare_schema;;;
    """
    pass

def h_schema_add_attribut(regle):
    """cas statique : on ajoute les attributs a une liste de classes"""
    if regle.params.cmp2.val:
        nom_schema = regle.params.cmp1.val
        classes = [
                regle.stock_param.schemas[nom_schema].classes.get(i)
                for i in regle.params.cmp2.liste
            ]
        for i in classes:
            for att in [a for a in regle.params.att_sortie.liste if a[0] != "#"]:
                #            print('ajout 2', att)
                i.ajout_attribut_modele(regle.params.def_sortie, nom=att)
        regle.valide='done'


def f_schema_add_attribut(regle, obj):
    """#aide||ajoute un attribut a un schema sans toucher aux objets
       #pattern||A;;;sc_add_attr;C?;L?
       #test||obj||^Z;;;sc_add_attr||^W;Z;;info_schema;attribut||atv;W;1
    """

    schemaclasse = obj.schema
    if not schemaclasse:
        return False
    if schemaclasse.amodifier(regle):
        for att in [a for a in regle.params.att_sortie.liste if a[0] != "#"]:
            #            print('ajout 2', att)
            schemaclasse.ajout_attribut_modele(regle.params.def_sortie, nom=att)
    return True


def h_schema_supp_attribut(regle):
    """cas statique : on supprime les attributs a une liste de classes"""
    if regle.params.cmp1.val:
        nom_schema = regle.params.cmp1.val
        if regle.params.cmp2.val:
            classes = [
                regle.stock_param.schemas[nom_schema].classes.get(i)
                for i in regle.params.cmp2.liste
            ]
        else:
            classes = regle.stock_param.schemas[nom_schema].classes.keys()
        for i in classes:
            for att in [a for a in regle.params.att_sortie.liste if a[0] != "#"]:
                #            print('ajout 2', att)
                if att in i.attributs:
                    del i.attributs[att]
        regle.valide='done'



def f_schema_supp_attribut(regle, obj):
    """#aide||supprime un attribut d un schema sans toucher aux objets
       #pattern||A;;;sc_supp_attr;C?;L?
       #test||obj||^C1;;;sc_supp_attr||^W;C1;;info_schema;attribut||atv;W;0;
    """

    schemaclasse = obj.schema
    if not schemaclasse:
        return False
    if schemaclasse.amodifier(regle):
        for att in [a for a in regle.params.att_sortie.liste if a[0] != "#"]:
            #            print('ajout 2', att)
            if att in schemaclasse.attributs:
                del schemaclasse.attributs[att]
