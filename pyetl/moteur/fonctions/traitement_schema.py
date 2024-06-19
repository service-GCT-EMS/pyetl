# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015
#titre||manipulation de schemas
@author: 89965
fonctions de manipulation d'attributs
"""
import re
import os
import logging
import pyetl.schema.fonctions_schema as FSC
from pyetl.formats.interne.objet import Objet
from pyetl.schema.formats_schema.schema_xml import lire_schema_xml
from pyetl.schema.formats_schema.schema_csv import (
    lire_schema_csv,
    decode_classes_csv,
    decode_conf_csv,
)

LOGGER = logging.getLogger(__name__)
# fonctions de manipulation de schemas


def h_info_schema(regle):
    """prepare l'acces a un schema different de l'objet"""
    regle.nomschema = regle.params.cmp1.val
    regle.schemaref = None
    regle.fixe = ""
    if regle.params.att_entree.val.startswith(":"):
        regle.fixe = regle.params.att_entree.val[1:]


def getschemaclasse(regle, obj):
    """fournit le schema de recherche"""
    schemaclasse = None
    if not regle.nomschema:
        return obj.schema
    if not regle.schemaref:
        regle.schemaref = regle.stock_param.schemas.get(regle.nomschema)
        if not regle.schemaref:
            # print("schema inconnu", regle.nomschema, regle.stock_param.schemas.keys())
            LOGGER.error("schema inconnu %s", regle.nomschema)
            return None
    return regle.schemaref.get_classe(
        (None, obj.attributs.get(regle.getdyn(obj, "cmp2")))
    )


def f_info_schema(regle, obj):
    """#aide||recupere des infos du schema de l'objet
      #pattern1||A;C;;info_schema;?C;?C
      #pattern2||A;=attribut;C;info_schema;?C;?C
    #parametres||attribut qui recupere le resultat;parametre a recuperer;nom de l'attribut;commande,schema,classe
      #test1||obj;ligne||^V4;dimension;;info_schema;||atv;V4;2
      #test2||obj;ligne||^V4;type_geom;;info_schema;||atv;V4;2
      #test3||obj;poly||^V4;type_geom;;info_schema;||atv;V4;3

    """
    # print ("regles:dans info schema ")
    schemaclasse = getschemaclasse(regle, obj)
    nom = None
    if schemaclasse:
        # print("infoschema", regle.params.pattern, regle.params.att_entree.val)
        if regle.params.pattern == "2":
            nom = (
                regle.fixe
                if regle.fixe
                else obj.attributs.get(regle.params.att_entree.val)
            )
        obj.attributs[regle.params.att_sortie.val] = FSC.info_schema(
            schemaclasse, regle.params.val_entree.val, nom=nom
        )
        #        print ("regles:info schema ", regle.params.att_sortie,
        #        obj.attributs[regle.params.att_sortie])
        return True
    return False


def f_set_schema(regle, obj):
    """#aide||positionne des parametres de schema (statique)
       #pattern||C;?C;;set_schema;;
       #aide_spec||parametres positionnables:
        || pk : nom de la clef primaire
        || alias : commentaire de la table
        || dimension : dimension geometrique
        || no_multiple : transforme les attributs multiples en simple
        || stable : declare un schema stable
        || instable declare un schema instable
    #parametres||nom du parametre a positionner;valeur
       #test1||obj;poly||^type_geom;2;;set_schema;||^V4;type_geom;;info_schema;||atv;V4;2
    """
    schem = obj.schema
    if schem:
        if schem.amodifier(regle):
            FSC.set_val_schema(
                schem, regle.params.att_sortie.val, regle.params.val_entree.val
            )
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





def f_stock_schema(regle, obj):
    """#aide||cree un schema par analyse des objets et l'associe a un objet
    #parametres||applique le shema a l objet;schema;nom;nombre max de valeurs d enum (30)
    #aide_spec||la variable taux_conformite permet de definir me taux minimum d'objets renseignes
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
        else:
            nom_base = obj.attributs.get("#schema", "schema")

        regle.schema_courant = regle.getschema(nom_base)
        if not regle.schema_courant:
            regle.schema_courant = regle.stock_param.init_schema(nom_base)
        
        if regle.getvar("taux_conformite"):
            # print("reglage_taux conformite", int(regle.getvar("taux_conformite")))
            regle.schema_courant.taux_conformite = int(regle.getvar("taux_conformite"))

    regle.schema_courant.ajuste(
        obj, regle.params.cmp2.num if regle.params.cmp2.num else 30, force=regle.istrue("force_analyse")
    )
    if regle.final:
        # on force la sortie du schema l' objet est mort il n'a plus besoin de schema
        obj.schema = None
    if regle.params.att_sortie.val:
        obj.schema = regle.schema_courant.get_classe(obj.ident)
    return True


def f_force_alias(regle, obj):
    """#aide||remplace les valeurs par les alias
    #pattern||;;;force_alias;?C;
    """

    # types_entiers = {'E':1, 'entier':1}

    schem = obj.schema
    mode = int(regle.params.cmp1.num)
    if schem:
        if mode and schem.schema.defmodeconf != mode:
            schem.schema.defmodeconf = mode
        if schem.amodifier(regle): # on ajuste les defauts
            for nom,attr in schem.attributs.items():
                if attr.conformite and attr.defaut and attr.defaut.startswith("'"):
                    old_defaut=attr.defaut.strip("'")
                    attr.defaut = "'"+attr.conformite.ajuste_valeur(old_defaut)+"'"
                    # print ('modif defaut >'+old_defaut+'<',attr.defaut,attr.conformite.ajust.get(old_defaut), attr.conformite.ajust)
        # TODO valider le mecanisem de changement de mode alias

        for i in [j for j in obj.attributs.keys() if j and j[0] != "#"]:
            attr = schem.attributs.get(i)
            # print 'test attribut', attr.nom, attr.type_att
            if attr and attr.conformite:
                conf = attr.conformite
                val = obj.attributs[i]
                #                attr.type_att_base = 'T'
                obj.attributs[i] = conf.ajuste_valeur(val)
                
                # print("dans force_alias", mode, conf.nom, val, '->', obj.attributs[i])


        return True
    else:
        return False


def f_valide_schema(regle, obj):
    """#aide||verifie si des objets sont compatibles avec un schema
    #parametres||;nom du schema;;
    #pattern||?=#schema;?C;;valide_schema;?=strict;
    #pattern2||?=#schema;?C;;valide_schema;=supp_conf;
    #variables||log;err ou warn par defaut no;
    #test||obj||X;1;;;;;;pass||^;;;valide_schema||+:;;;;res;1;;set||atv;res;1
    #test2||obj;point||^type_geom;2;;set_schema||^;;;valide_schema||+fail:;;;;res;1;;set||atv;res;1

    """
    #    print ('fonctions : valide_schema', obj.ident, obj.schema)
    #    raise

    if regle.params.val_entree.val:
        # on copie le schema pour ne plus le modifier apres ecriture
        regle.change_schema_nom(obj, regle.params.val_entree.val)
    if obj.virtuel:
        #        print('valide_schema : obj virtuel')
        return True
    if obj.schema:
        modeconf = regle.params.cmp1.val
        loglevel = regle.getvar("log", "no")
        retour = FSC.valide_schema(regle, obj, modeconf, log=loglevel)
        #        print ('retour validation schema', retour, obj)
        return retour
    #            if not v :
    #                print ("---------------------------------------------------------retour fail ")
    obj.attributs["#erreurs"] = "objet sans schema"
    return False

def f_supp_enums(regle,obj):
    """#aide||transforme un schema en mode basique (supprime des enums)
    #aide_spec||;;attributs a traiter(tous);;
     #pattern1||;;?L;supp_enums;;
    """
    schem = obj.schema
    if schem:
        if schem.amodifier(regle):
            if regle.params.att_entree.liste:
                for i in regle.params.att_entree.liste:
                    att = schem.attributs.get(i)
                    if att:
                        att.setbasic()
            else:
                schem.setbasic(attributs=regle.params.att_entree.liste)
        return True
    return False




def h_def_schema(regle):
    """lecture de schema : preparation
    format: nom du schema (entree ou sortie ou autre )
    cmp1: nom du fichier
    cmp2: extension
    """
    # print ("h_def_schema",regle.params)
    cod = regle.getvar("codec_entree", "cp1252")
    fusion = False
    if regle.params.cmp1.dyn or regle.getvar("force_schema") == "fusion":
        fusion = True
    regle.fichier = regle.params.cmp1.val.replace("*", "")  # nom du fichier
    nom = regle.params.val_entree.val
    # print ("h_def_schema",regle.fichier, nom)

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
                regle.stock_param.init_schema(
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
        # print ('demande schema interne',nomschema, '->', nom, 'differe',regle.differe)
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
    # print ("h_def_schema fichier",regle.fichier)

    if not nom:
        nom = os.path.basename(regle.fichier)

    if not nom:
        LOGGER.warning("pas de nom schema -> nom fixe a 'schema'")
        nom = "schema"

    if regle.params.att_sortie.val == "schema_entree":
        regle.setvar("schema_entree", nom)
        LOGGER.info("positionnement schema d entree " + nom)
        regle.valide = "done"  # on a fait le boulot on peut jeter la regle

    if regle.params.att_sortie.val == "schema_sortie":
        regle.setvar("schema_sortie", nom)
        LOGGER.info("positionnement schema_sortie " + nom)
        regle.valide = "done"  # on a fait le boulot on peut jeter la regle

    LOGGER.debug("lecture schema " + " ".join((str(regle.numero), nom, cod)))

    if ext == "csv":
        mode_alias = regle.context.getvar("mode_alias", "num")
        cod_csv = regle.context.getvar("codec_csv", cod)
        if fusion:
            regle.stock_param.lire_schemas_multiples(
                nom, regle.fichier, mode_alias, cod=cod_csv, fusion=fusion
            )
        else:
            lire_schema_csv(
                regle.stock_param, nom, regle.fichier, mode_alias, cod=cod_csv
            )
    else:
        lire_schema_xml(regle.stock_param, nom, regle.fichier, cod=cod)
    regle.nomschema = nom
    taille_schema = len(regle.stock_param.schemas[nom].classes)
    if taille_schema > 0:
        LOGGER.info("lecture schema %s:%d classes", nom, taille_schema)
    else:
        regle.valide = False

    regle.remap = regle.params.att_entree.val == "map"


def schema_from_objs(regle):
    """transforme les objets stockes en schema"""
    tables = []
    enums = []
    defclasse = regle.params.cmp1.val
    defenum = regle.params.cmp2.val
    for obj in regle.tmpstore:
        niveau, classe = obj.ident
        if regle.params.cmp1.origine:
            defclasse = obj.attributs.get(regle.params.cmp1.origine)
        # print("traitement ligne", obj.ident, defclasse, defenum)
        description = {i: j for i, j in obj.attributs.items() if not i.startswith("#")}
        ligne = ";".join([j for j in description.values()])
        if re.match(defenum, classe):
            # print("defenum", description, ligne)
            if description.get("nom_enumeration"):
                enums.append(ligne)
        elif re.match(defclasse, classe):
            if description.get("table"):
                tables.append(ligne)
    schema_courant = regle.stock_param.init_schema(regle.nom, origine="L")
    # print("decodage confs", "\n".join(enums))
    decode_conf_csv(schema_courant, enums)
    decode_classes_csv(schema_courant, tables)

    # print(" decodage schema", regle.nom, schema_courant)
    # on envoie un objet virtuel dans le circuit
    regle.stock_param.moteur.traitement_virtuel(schema=schema_courant.nom)
    regle.nbstock = 0


def h_schema_from_classe(regle):
    """creation schema regle stockante"""
    regle.store = True
    regle.traite_stock = schema_from_objs
    regle.nbstock = 0
    regle.tmpstore = list()
    regle.nom = regle.params.val_entree.val if regle.params.val_entree.val else "schema"


def f_schema_from_classe(regle, obj):
    """#aide||cree un schema a partir d objets contenant la structure
    #aide_spec||;nom;;cree_schema;classe table;classe enums
     #pattern1||;?C;;cree_schema;C;C

    """
    niveau, classe = obj.ident
    regle.tmpstore.append(obj)
    regle.nbstock += 1
    return True


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
            regle.stock_param.init_schema(
                nom_base,
                origine="G",
                fich="",
                defmodeconf=0,
                stable=True,
                modele=regle.params.cmp2.val,
                copie=True,
            )
            LOGGER.info(
                "copie de schema differee %s %s", regle.params.cmp2.val, nom_base
            )
            # print("copie de schema differee", regle.params.cmp2.val, nom_base)
        #            raise
        else:
            LOGGER.error("schema inconnu %s", nom_base)
            # print("erreur schema inconnu", nom_base)
            return False

    schema = regle.stock_param.schemas[nom_base]
    ident2 = (
        schema.map_dest(ident, virtuel=obj.virtuel)
        if schema.stock_mapping.existe
        else ident
    )

    schema_classe = schema.get_classe(ident2)
    if not schema_classe:
        schema_classe = schema.get_classe(("", nom))
        if schema_classe:
            schema_classe.setorig(obj.ident)
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
        LOGGER.warning(
            "regle %d classe non trouvée %s %s dans %s",
            regle.numero,
            nom_base,
            ident,
            regle.nomschema,
        )
        # print(
        #     "regles:",
        #     regle.numero,
        #     "classe non trouvee",
        #     nom_base,
        #     ident,
        #     "dans ",
        #     regle.nomschema,
        # )
        LOGGER.warning("liste classes %s ....", str(list(schema.classes.keys())[:10]))
        # print("regles: liste classes ", list(schema.classes.keys())[:10], "....")
        obj.schema = None
        return False


def f_match_schema(regle, obj):
    """#aide||associe un schema en faisant un mapping au mieux
    #pattern||;?C;;match_schema;C;?N"""
    schema_classe = obj.schema
    if schema_classe:
        if schema_classe.attmap is None:
            schema_destination = regle.getschema(regle.params.cmp1.val)
            if not schema_destination:
                return False
            schema_classe.init_mapping(
                schema_destination,
                regle.params.cmp2.num if regle.params.cmp2.val else 0.5,
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
        regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["gen"])
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
    #pattern||=#schema;C;;map_schema;C;;||sortie"""
    # pattern||;?C;;match_schema;C;?N

    pass


def h_diff_schema(regle):
    """compare les schemas"""
    nomsource = regle.params.val_entree.val
    schemaref = regle.getschema(regle.params.cmp1.val)
    if nomsource:
        schemasource = regle.getschema(nomsource)
        rapport = FSC.compare_schema(
            schemasource, schemaref, full=regle.params.cmp2.val == "full"
        )
        regle.setvar(regle.params.att_sortie.val, rapport)
        regle.valide = "done"
        return True
    regle.schemaref = schemaref
    regle.rapports = dict()
    regle.branchements.addsortie("new")
    regle.branchements.addsortie("diff")


def f_diff_schema(regle, obj):
    """#aide||compare un nouveau schema en sortant les differences
    #parametres||;schema;;compare_schema;ref
    #pattern||P;C;;compare_schema;C;?=full
    #pattern2||A;;;compare_schema;C;
    """
    if not obj.schema:
        return False
    if obj.ident not in regle.rapports:
        regle.rapports[obj.ident] = FSC.compare_classe(obj.schema, regle.schemaref)
    rapport = regle.rapports[obj.ident]
    regle.setvalsortie(obj, rapport)
    if rapport == "new":
        obj.redirect = "new"
    elif rapport:
        obj.redirect = "diff"
    return True


def h_schema_add_attribut(regle):
    """cas statique : on ajoute les attributs a une liste de classes"""
    if regle.params.cmp1.val:
        nom_schema = regle.params.cmp1.val
        classes = [
            regle.stock_param.schemas[nom_schema].classes.get(i)
            for i in regle.params.cmp2.liste
        ]
        for i in classes:
            for att in [a for a in regle.params.att_sortie.liste if a[0] != "#"]:
                #            print('ajout 2', att)
                i.ajout_attribut_modele(regle.params.def_sortie, nom=att)
        regle.valide = "done"


def f_schema_add_attribut(regle, obj):
    """#aide||ajoute un attribut a un schema sans toucher aux objets
    #pattern||A;;;sc_add_attr;C?;L?
    #test||obj||^Z;;;sc_add_attr||^W;attribut;:Z;info_schema;||atv;W;1
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
        regle.valide = "done"


def f_schema_supp_attribut(regle, obj):
    """#aide||supprime un attribut d un schema sans toucher aux objets
    #pattern||A;;;sc_supp_attr;C?;L?
    #test||obj||^C1;;;sc_supp_attr||^W;attribut;:C1;info_schema;||atv;W;0;
    """

    schemaclasse = obj.schema
    if not schemaclasse:
        return False
    if schemaclasse.amodifier(regle):
        for att in [a for a in regle.params.att_sortie.liste if a[0] != "#"]:
            #            print('ajout 2', att)
            if att in schemaclasse.attributs:
                del schemaclasse.attributs[att]


def f_schema_order(regle, obj):
    """#aide||ordonne les champs dans un schema
    #pattern||L;;;sc_ordre;;
    """
    schemaclasse = obj.schema
    if not schemaclasse:
        return False
    if schemaclasse.amodifier(regle):
        nummax = len(schemaclasse.attributs) + 1
        for att in schemaclasse.attributs.values():
            if att.nom in regle.params.att_sortie.liste:
                att.ordre = regle.params.att_sortie.liste.index(att.nom) + 1
            else:
                nummax += 1
                att.ordre = nummax
    return True


def h_schema_change_type(regle):
    """cas statique : on ajoute les attributs a une liste de classes"""
    regle.typefiltre=regle.params.val_entree
    regle.typecast=regle.params.att_sortie
    if regle.params.cmp1.val:
        nom_schema = regle.params.cmp1.val
        classes = [
            regle.stock_param.schemas[nom_schema].classes.get(i)
            for i in regle.params.cmp2.liste
        ] if regle.cmp2.val else regle.stock_param.schemas[nom_schema].classes
        for i in classes:
            if regle.params.att_entree.val:
                liste_att=regle.params.att_entree.liste
            else:
                liste_att=i.attributs.keys()
            
            for att in liste_att:
                if not regle.typefiltre or i.attributs.get(att).type==regle.typefiltre:
                    i.attributs[att].type=regle.typecast
        regle.valide = "done"



def f_schema_change_type(regle, obj):
    """#aide||change le type d'attributs attribut d un schema sans toucher aux objets
    #aide_spec1||change le type d'une liste d'attributs
    #aide_spec2||cas statique change un type en un autre sur une liste de classes d'un schema
    #pattern1||C;?C;?L;sc_change_type;
    #pattern2||C;?C;?L;sc_change_type;C;?L
    """

    schemaclasse = obj.schema
    if not schemaclasse:
        return False
    if schemaclasse.amodifier(regle):
        if regle.params.att_entree.val:
            liste_att=regle.params.att_entree.liste
        else:
            liste_att=schemaclasse.attributs.keys()
            
        for att in liste_att:
            if not regle.typefiltre or schemaclasse.attributs.get(att).type==regle.typefiltre:
                schemaclasse.attributs[att].type=regle.typecast
    return True