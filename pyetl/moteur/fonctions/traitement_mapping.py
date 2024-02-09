# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de structurelles diverses
"""
import re
import logging

from .outils import expandfilename, charge_liste


LOGGER = logging.getLogger(__name__)


def prepare_elmap(mapping):
    """precalcule les dictionaires pour le mapping"""
    mapping_special = (
        dict()
    )  # mapping simplifie pour modifier les scripts de base de donnees
    for i in mapping:
        schema1, table1 = i
        schema2, table2 = mapping[i]
        mapping_special[schema1] = schema2
        mapping_special[table1] = table2
    items = sorted(mapping_special, key=lambda i: len(mapping_special[i]), reverse=True)
    intmap1 = {j: "**<<" + str(i) + ">>**" for i, j in enumerate(items)}
    intmap2 = {
        "**<<" + str(i) + ">>**": mapping_special[j] for i, j in enumerate(items)
    }
    elmap = (items, intmap1, intmap2)
    #    print ('definition intmap2', intmap2)
    return elmap


def remap_noms(items, intmap1, intmap2, elt):
    """remappe un nom"""
    elt2 = elt
    for tbl in items:
        elt2 = elt2.replace(tbl, intmap1[tbl])
    #        if intmap1[tbl] in elt2:
    #            print ('remplacement', elt2, tbl, intmap1[tbl])
    for code in intmap2:
        elt2 = elt2.replace(code, intmap2[code])
    #        if intmap2[code] in elt2:
    #            print ('remplacement', elt2, code, intmap2[code])
    #    print ('remap_noms',elt,'->',elt2)
    return elt2


def remap_ident(elmap, ident):
    """remappe un identifiant"""
    if isinstance(ident, tuple):
        schema, table = ident
        schema2 = remap_noms(*elmap, schema)
        table2 = remap_noms(*elmap, table)
        return (schema2, table2)
    elif isinstance(ident, str):
        return remap_noms(*elmap, ident)
    return ident


def remap(element, elmap):
    """remappe des noms de tables et de schema dans des structures"""
    #    print ('valeur elmap',elmap)
    #    raise
    if isinstance(element, dict):
        return {
            remap_ident(elmap, ident): remap(val, elmap)
            for ident, val in element.items()
        }
    elif isinstance(element, (list, tuple)):
        return [remap(val, elmap) for val in element]
    elif isinstance(element, str):
        return remap_noms(*elmap, element)
    return element


def traite_mapping(elements):
    """decode une definition de mapping
    elements est une liste de definitions de mapping
    a ce stade une definition  se presente sous la forme suivante:
    (groupe.classe, groupe.classe,[(attribut => attribut,...)])
    ou
    (groupe,classe, groupe,classe,[(attribut => attribut,...)])
    """
    mapping = dict()
    mapping_attributs = dict()
    map_enum_prefix = ()
    map_enums = dict()

    for els in elements:
        # print ("traitement els", els)
        if not els or els[0].startswith("!") or not els[0]:
            continue
        attrmap = ""
        if els[0] == "#enum":  # mapping d 'enums
            if els[1].endswith("*"):
                map_enum_prefix = (els[1][:-1], els[2])
            else:
                map_enums[els[1]] = els[2]
            # print("mapping enums", map_enum_prefix, map_enums)

        elif len(els) == 2 or len(els) == 3:
            id1 = tuple(els[0].split("."))
            id2 = tuple(els[1].split("."))
            if len(els) == 3:
                attrmap = els[2]
        #            print ('mapping',i,id1,id2)
        elif len(els) == 4 or len(els) == 5:
            id1 = (els[0], els[1])
            id2 = (els[2], els[3])
            if len(els) == 5:
                attrmap = els[4]
        else:
            print(
                "traite_mapping :description incorrecte", len(els), els, elements[els]
            )
            continue
        if len(id1) == 3:  # on a ajoute la base : on supprime
            id1 = tuple(id1[1:])
        if attrmap:
            attrmap = attrmap.replace('"', "")
            attrmap = attrmap.replace("'", "")
            map_attributs = dict(
                [re.split(" *=> *", i) for i in re.split(" *, *", attrmap)]
            )
            mapping_attributs[id1] = map_attributs
            mapping_attributs[id2] = dict(
                (b, a) for a, b in map_attributs.items()
            )  # mapping inverse

        mapping[id1] = id2
        mapping[id2] = id1
    return mapping, mapping_attributs, map_enum_prefix, map_enums


def charge_mapping(regle, mapping=None):
    """precharge un mapping"""

    if regle.params.cmp1.val.startswith("{"):  # c'est une definition in line
        # {groupe.classe,groupe.classe,att=>att,att=>att...:groupe.classe,groupe.classe,att=>att,...:...}
        vtmp = regle.params.cmp1.val[1:-1].split(":")
        elements = [i.split(",", 2) for i in vtmp]

    elif regle.params.cmp1.val:
        regle.fichier = regle.params.cmp1.val  # nom du fichier
        fichier = expandfilename(
            regle.fichier,
            regle.stock_param.rdef,
            regle.stock_param.racine,
            regle.stock_param.chemin_courant,
            regle.stock_param.fichier_courant,
        )
        elements = charge_liste(fichier, taille=-1).values()
        # on precharge le fichier de mapping
    else:
        elements = []

    (
        regle.mapping,
        regle.mapping_attributs,
        regle.map_enum_prefix,
        regle.map_enums,
    ) = traite_mapping(elements)

    if regle.params.att_sortie.val == "#schema":
        regle.schema_dest = regle.getschema(regle.params.val_entree.val)
    #        mapping_attributs
    regle.elmap = prepare_elmap(regle.mapping)
    # print ('definition mapping', '\n'.join([str(i)+':\t\t'+str(regle.mapping[i])
    #     for i in sorted(regle.mapping)]))
    # print (regle.mapping_attributs)
    #

    if not regle.mapping:
        LOGGER.warning("mapping introuvable %s", regle.fichier)
        # print("h_map:mapping introuvable", regle.fichier)


def map_struct(regle):
    """mappe la structure clef etrangeres et fonctions"""
    charge_mapping(regle, mapping=regle.schema.mapping)


def _map_schemas(regle, obj):
    """essaye de trouver un mapping pour une classe"""
    # print("appel map_schema", regle, obj)
    if obj is None:
        if regle.getvar("schema_entree"):
            schema_origine = regle.stock_param.schemas[regle.getvar("schema_entree")]
            # print("-------------------------mapping", schema_origine)
            regle.schema = schema_origine
        #        else:
        #            return
        #        if regle.params.val_entree.val:
        #            schema2 = regle.stock_param.init_schema(regle.params.val_entree.val,
        #                                                    modele=schema_origine, origine='B')
        #        else:
        return
    elif not regle.schema:
        if not obj.schema:
            print("objet sans schema", obj)
            return
        schema_origine = obj.schema.schema
        if regle.params.val_entree.val:
            schema2 = regle.stock_param.init_schema(
                regle.params.val_entree.val, modele=schema_origine, origine="B"
            )
        else:
            schema2 = obj.schema.schema
        regle.schema = schema2

        if schema2.elements_specifiques:
            for i in schema2.elements_specifiques:
                #            print('mapping specifique', i)
                spec = schema2.elements_specifiques[i]
                mapped = remap(spec, regle.elmap)
                #            print('mapping specifique', i, len(spec), '->', len(mapped))
                schema2.elements_specifiques[i] = mapped
        else:
            LOGGER.info("pas d'elements specifiques")

            # print("-----------------------------pas d'elements specifiques")

        for i in schema_origine.classes:
            schema2.get_classe(i, modele=schema_origine.classes[i], cree=True)
        # on ajuste les mappings si il y a des * dedans
        complement=dict()
        for i in regle.mapping:
            niv,clas=i
            if clas.endswith('*'): #c est du generique
                prefix = clas.replace('*','')
                n2,remplacement = regle.mapping[i]
                for j in list(schema_origine.classes.keys()):
                    n1,c1 = j
                    if n1==niv and c1.startswith(prefix):
                        c2 = c1.replace(prefix,remplacement,1)
                        complement[(niv,c1)] = (n2,c2)
                        complement[(n2,c2)] = (niv,c1)
                        if i in regle.mapping_attributs:
                            regle.mapping_attributs[(niv,c1)] = regle.mapping_attributs[i]
                            regle.mapping_attributs[n2,c2] = regle.mapping_attributs[n2,remplacement]
        regle.mapping.update(complement)    
        # print("mapping enums:", regle.schema.nom, regle.schema.conformites.keys())
        if schema2.conformites and (regle.map_enum_prefix or regle.map_enums):
            for classe in schema2.classes.values():
                # print("traitement classe", classe.identclasse)
                for attribut in classe.attributs.values():
                    if attribut.nom_conformite:
                        # print("conformite avant", regle.schema.nom,attribut.nom_conformite)
                        if regle.map_enum_prefix:
                            attribut.nom_conformite = attribut.nom_conformite.replace(
                                *regle.map_enum_prefix
                            )
                        attribut.nom_conformite = regle.map_enums.get(
                            attribut.nom_conformite, attribut.nom_conformite
                        )

                        attribut.conformite = schema2.conformites.get(
                            attribut.nom_conformite, attribut.conformite
                        )
                        # print("conformite apres", attribut.nom_conformite)
                        # print("changement conformite", attribut)
                # print("changement classe", classe.attributs)
            new_enums = schema2.conformites
            if regle.map_enum_prefix:
                new_enums = {
                    i.replace(*regle.map_enum_prefix): j
                    for i, j in schema2.conformites.items()
                }
            new_enums = {regle.map_enums.get(i, i): j for i, j in new_enums.items()}

            for i, j in new_enums.items():
                j.nom = i

            # print("enums orig", schema2.conformites.keys())
            # print("conversion enums", new_enums.keys())
            schema2.conformites.update(new_enums)
            # print("mapping enums", schema2.conformites.keys())
            # print("schema origine", schema_origine.name)

        for i in list(schema_origine.classes.keys()):
            #        print ('map_schemas ',schema_origine.nom,i,regle.mapping.get(i))
            if i in regle.mapping:
                schema2.renomme_classe(i, regle.mapping[i])
                # print("renommage", i, regle.mapping[i])
                # print("attributs", schema2.classes[regle.mapping[i]].attributs)
            # mapping foreign keys :

        # print("-------------------------------------------------mapping effectue", schema2.nom, len(schema2.classes))
        for clef in schema2.classes:
            if clef in regle.mapping_attributs:
                for dest, orig in regle.mapping_attributs[clef].items():
                    schema2.classes[clef].rename_attribut(orig, dest)
                    # print ('-----------------------------mappin attributs', clef, orig,dest)


def applique_mapping(regle):
    """gere les clefs etrangeres et les elements speciaux dans les mappings"""
    mapping = regle.schema.mapping
    regle.elmap = prepare_elmap(mapping)
    _map_schemas(regle, None)
    regle.nbstock = 0
    for i in mapping:
        for scl in regle.schema.classes.values():
            scl.renomme_cible_classe(i, mapping[i])


def h_map2(regle):
    """prepare le mapping des structures"""
    regle.store = True
    regle.blocksize = 1
    regle.nbstock = 0
    regle.traite_stock = applique_mapping


def f_map2(regle, obj):
    """#aide||mapping en fonction d'une creation dynamique de schema
    #aide_spec||parametres: mappe les structures particulieres
     #pattern2||;;;map;=#struct;;
    """
    regle.schema = obj.schema.schema
    regle.nbstock = 1


def h_map(regle):
    """precharge le fichier de mapping et prepare les dictionnaires"""
    regle.dynlevel = 0  # les noms de mapping dependent ils des donnees d entree
    regle.mapping = None
    regle.schema = None
    #    if regle.params.att_sortie.val == '#schema': # mapping d un schema existant
    #        schema2 =
    regle.changeschema = True
    fich = regle.params.cmp1.val
    if "[F]" in fich:
        regle.dynlevel = 2
    elif "[C]" in fich:
        regle.dynlevel = 1
    if regle.dynlevel:
        regle.clefdyn = ""
    else:
        charge_mapping(regle)
        _map_schemas(regle, None)


def f_map(regle, obj):
    """#aide||mapping en fonction d'un fichier
     #aide_spec||parametres: map; nom du fichier de mapping
    #aide_spec2||si #schema est indique les objets changent de schema
       #pattern||?=#schema;?C;;map;C;;
     #test||obj||^#schema;test;;map;%testrep%/refdata/map.csv;;||^;;;pass;;;||atv;toto;AB
    #!test2||obj||^#schema;test;;map+-;%testrep%/refdata/map.csv;;||^;;;pass;;;debug||cnt;2
    """
    #    print ("dans map ===============",obj)
    if regle.dynlevel:  # attention la regle est dynamique
        clef_dyn = (
            regle.stock_param.chemin_courant
            if regle.dynlevel == 1
            else regle.stock_param.fichier_courant
        )
        if clef_dyn != regle.clef_dyn:
            charge_mapping(regle)
    if not regle.schema:
        _map_schemas(regle, obj)
    clef = obj.ident
    schema2 = regle.schema
    # print(
    #     " mapping objet",
    #     clef,
    #     regle.mapping,
    #     obj.schema.schema.nom,
    #     schema2.nom,
    # )
    oldschema = obj.schema.schema
    if clef in regle.mapping:
        nouv = regle.mapping.get(clef)
        obj.setidentobj(nouv, schema2=schema2)
        # print("changement obj", oldschema.nom, obj.schema)
        if clef in regle.mapping_attributs:
            for orig, dest in regle.mapping_attributs[clef].items():
                # print("mapping", clef, nouv, orig, dest)
                try:
                    obj.attributs[dest] = obj.attributs.get(orig, "")
                    del obj.attributs[orig]
                    # if obj.schema and obj.schema.amodifier(regle):
                    #     # print
                    #     obj.schema.rename_attribut(orig, dest)
                except KeyError:
                    obj.attributs[dest] = ""
        return True
    print("====================== mapping non trouve", clef, regle.mapping)
    raise
    #    print ('definition mapping', '\n'.join([str(i)+':\t\t'+str(regle.mapping[i])
    #                                            for i in sorted(regle.mapping)]))
    return False


def h_map_data(regle):
    """precharge le fichier de mapping et prepare les dictionnaires"""
    regle.dynlevel = 0  # les noms de mapping dependent ils des donnees d entree
    regle.mapping = None
    regle.identclasse = None
    regle.liste_att = None
    #    if regle.params.att_sortie.val == '#schema': # mapping d un schema existant
    #        schema2 =
    regle.lastfich = None
    fich = regle.params.cmp1.val
    if "[F]" in fich:
        regle.dynlevel = 2
    elif "[C]" in fich:
        regle.dynlevel = 1
    if regle.dynlevel:
        regle.clefdyn = ""
    else:
        charge_mapping(regle)


def f_map_data(regle, obj):
    """#aide||applique un mapping complexe aux donnees
    #aide_spec||C: fichier de mapping
    #pattern||A;?C;A;map_data;C
    #schema||ajout_attribut
    """
    val = regle.entree
    obj.attributs[regle.params.att_sortie.val] = regle.elmap.get(val, val)
    return val in regle.elmap


def f_map_data_liste(regle, obj):
    """#aide||applique un mapping complexe aux donnees
    #aide_spec||C: fichier de mapping
    #pattern||L;?C;L;map_data;C
    #helper||map_data
    #schema||ajout_attribut
    """
    defaut = regle.params.val_entree.val
    for entree, sortie in zip(
        regle.params.att_entree.liste, regle.params.att_sortie.liste
    ):
        val = obj.attributs.get(entree, defaut)
        obj.attributs[sortie] = regle.elmap.get(val, val)
    return True


def f_map_data_type(regle, obj):
    """#aide||applique un mapping complexe aux donnees
    #aide_spec||C: fichier de mapping
    #aide_spec||T: definition de type de donnees (T:)
    #pattern||*;?C;T:;map_data;C
    #helper||map_data
    #schema||ajout_attribut
    """
    if obj.schema is None:
        return False
    ident = obj.schema.identclasse
    if ident != regle.identclasse:
        regle.identclasse = ident
        regle.liste_att = [
            i
            for i in obj.schema.attributs
            if obj.schema.attributs[i].type_att == regle.params.att_entree.val
        ]
    defaut = regle.params.val_entree.val
    if not regle.liste_att:
        return False
    for att in regle.liste_att:
        val = obj.attributs.get(att, defaut)
        obj.attributs[att] = regle.elmap.get(val, val)
    return True
