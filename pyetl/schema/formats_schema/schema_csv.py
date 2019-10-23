# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 09:28:45 2014
gestion des entrees et sorties de schemas
@author: 89965
"""
import os
from .. import schema_interne as SCI
from .. import fonctions_schema as FSC


def sortir_conformite_csv(conf, mode=-1, init=False):
    """ecrit une conformite en format csv"""
    # "!conformite;Ordre;VAL_CONF_NOM;VAL_CONF_TEXTE;mode;fin"
    #    print ('sortir conformite ',conf.nom,mode,conf.stock)
    #    print ([";".join((conf.nom, str(i[2]), i[4] if init else i[0], i[1],
    #                      str(i[3]) if mode == -1 else mode))
    #                      for i in sorted(conf.stock.values(), key=lambda v: v[2])])
    if conf.nom.startswith("#"):  # c'est une conformite externe
        return [";".join((conf.nombase, "#EXTERNE", ""))]

    return [
        ";".join(
            (
                conf.nombase,
                str(i[2]),
                i[4] if conf.ajust and not init else i[0],
                i[1],
                str(i[3]) if mode == -1 else str(mode),
            )
        )
        for i in sorted(conf.stock.values(), key=lambda v: v[2])
    ]


def sortir_schema_classe_csv(sc_classe, mode="util"):
    """ecrit une definition de classe en csv"""
    #    print ('sortir_schemaclasse')
    nom_compo = sc_classe.nom
    #    print ('ssc:\n','\n'.join([str((a.nom,a.nom_conformite,a.type_att,a.type_att_base, a.taille))
    #            for a in sc_classe.attributs.values()]))
    liste_att_csv = list()
    #    if sc_classe.nom=='rg_fil_troncon':
    #        print ('sortir_schema -----------------',sc_classe.schema.nom, sc_classe.nom)
    groupe = sc_classe.groupe
    sc_classe.cree_noms_courts(longueur=10)
    complement = "oui" if sc_classe.multigeom else "non"
    type_geom = SCI.TYPES_G[sc_classe.info["type_geom"]]
    #    print('sio: sortir schema', sc_classe.info["type_geom"], type_geom)
    dimension = sc_classe.info["dimension"]
    type_stockage = sc_classe.types_stock.get(sc_classe.type_table, "")
    arc = "courbe" if sc_classe.info["courbe"] else ""

    srid = "mixte" if sc_classe.sridmixte else str(sc_classe.srid)
    nbr = sc_classe.objcnt
    if not nbr:
        nbr = sc_classe.getinfo("objcnt_init")
    if mode == "fusion":
        nbr = sc_classe.poids if sc_classe.poids else sc_classe.getinfo("objcnt_init")
    liste_att_csv.append(
        ";".join(
            [
                groupe,
                nom_compo,
                "",
                str(sc_classe.alias).replace("\n", ""),
                str(type_geom),
                arc,
                complement,
                type_stockage,
                "",
                srid,
                dimension,
                str(nbr),
                "",
                "",
                "fin",
                sc_classe.listindexes,
                sc_classe.listfkeys(),
            ]
        )
    )

    iatt = sc_classe.index_par_attributs()

    for i in sc_classe.get_liste_attributs(sys=True):
        att = sc_classe.attributs.get(i)
        if not att:
            print(
                "attribut inconnu :",
                i,
                "\nk: ",
                sorted(sc_classe.attributs.keys()),
                "\nl: ",
                sorted(sc_classe.liste_attributs_cache),
            )
            continue
        # print "attribut",i
        nom = sc_classe.minmajfunc(str(att.nom))

        if att.conformite:
            # print "nom conformite",att.nom_conformite,att.conformite
            att.type_att = "T"
            att.taille = att.conformite.taille
        # graphique="oui" if att.graphique else 'non'
        if att.type_att == "A":
            att.type_att = "T" if att.type_att_defaut == "A" else att.type_att_defaut
            att.type_att_base = att.type_att
            print(
                "sio: type attribut non defini ",
                att.type_att,
                " par defaut",
                groupe,
                nom_compo,
                nom,
            )
        type_att = att.get_type()
        #        print ('type_att lu',i,att.type_att,att.conformite,att.multiple)

        multiple = "oui" if att.multiple else "non"
        defaut = att.defaut if att.defaut else ""
        oblig = "oui" if att.oblig else "non"
        conf = att.nom_conformite if att.conformite else ""
        index = iatt.get(att.nom, "")
        cible, params = sc_classe.getfkey(att.nom)
        fkey = sc_classe.minmajfunc(cible) + ("(" + params + ")") if params else ""

        liste_att_csv.append(
            ";".join(
                [
                    groupe,
                    nom_compo,
                    nom,
                    str(att.alias).replace("\n", ""),
                    type_att,
                    "non",
                    multiple,
                    defaut,
                    oblig,
                    conf,
                    dimension,
                    str(att.taille),
                    str(att.dec) if att.dec else "0",
                    str(att.nom_court),
                    "fin",
                    index,
                    fkey,
                ]
            ).replace("\n", " ")
        )
    if type_geom != "ALPHA":
        liste_att_csv.append(
            ";".join(
                [
                    sc_classe.groupe,
                    sc_classe.nom,
                    sc_classe.info["nom_geometrie"],
                    str(sc_classe.alias).replace("\n", ""),
                    str(type_geom),
                    arc,
                    complement,
                    "",
                    "",
                    srid,
                    dimension,
                    str(sc_classe.ech_denom_min),
                    str(sc_classe.ech_denom_max),
                    "",
                    "fin",
                    "G:",
                    "",
                ]
            ).replace("\n", " ")
        )
    return liste_att_csv


def sortir_schema_csv(sch, mode="all", modeconf=-1, conf_used=False, init=False):
    """ecrit un schema complet en csv"""
    conf = ["!conformite;N°_ordre;VAL_CONF_NOM;VAL_CONF_TEXTE;mode;fin"]
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
            print(
                "schema : ::: warning", len(unused), "conformites inutilisees ", unused[:10], "..."
            )

    description = [
        "!groupe;compo_nom;Nom;Alias;Type;graphique;multiple;Valeur par defaut;"
        + "Obligatoire;Conformite;dimension;taille;decimales;nom court;fin;index;FK"
    ]
    #    print("schema:  csv sortir_classes",len(sch.classes))
    if sch.metas:
        #        print ('sortir metas ',sch.metas)
        metadef = "!meta;" + ";".join(k + "=" + v for k, v in sch.metas.items())
        description.append(metadef)
    if sch.classes:
        for i in sorted(sch.classes.keys()):
            if sch.classes[i].a_sortir:
                #                print ("csv classe a sortir",i,sch.classes[i])
                #                print ('\n'.join([str((a.nom,a.nom_conformite,a.type_att,a.type_att_base))
                #                       for a in sch.classes[i].attributs.values()]))
                description.extend(sortir_schema_classe_csv(sch.classes[i], mode))
    # print ("schema: debug " , conf,cl)
    return conf, description


def lire_mapping(schema_courant, fichier, codec):
    """ lit un fichier de mapping externe"""
    if not os.path.isfile(fichier):
        print("schema io: ::: warning fichier mapping introuvable ", fichier)
        return
    liste_mapping = []
    #    print("schema io: lire_mapping ", fichier)
    with open(fichier, "r", encoding=codec) as entree:
        i = entree.readline()  # entete : on ignore
        i = entree.readline()
        while i:
            liste_mapping.append(i[:-1])
            i = entree.readline()
    schema_courant.init_mapping(liste_mapping)


def decode_conf_csv(schema_courant, entree, mode_alias=None):
    """decode un tableau de conformites
    se presente sous la forme:  nom;ordre,valeur;alias;mode
    hierarchie :
        force / fichier / demande / 1
    """
    codes_force = {"force_base": 0, "force_num": 1, "force_alias": 2, "force_inv": 3}
    codes_alias = {"base": 0, "num": 1, "alias": 2, "inv": 3}
    lin = 0
    force = codes_force.get(mode_alias)
    mode_demande = codes_alias.get(mode_alias, 1)
    for i in entree:
        if lin == 0 and "!" in i[:4]:
            #                print (" schema conf io:detecte commentaire utf8")
            lin = 1
            continue
        if i[0] == "!":
            #                print (" schema conf io:detecte commentaire")
            continue
        val_conf = i.replace("\n", "").split(";")
        if not val_conf:
            continue
        nom = val_conf[0].lower().strip()
        if not nom:
            continue
        if len(val_conf) < 2:
            print("enumeration incomplete ", val_conf)
            continue
        externe = val_conf[1] == "#externe"  # contrainte externe definie en base mais non connue
        conf = schema_courant.get_conf(nom, type_c="#EXTERNE" if externe else "")
        ordre = int(val_conf[1]) if val_conf[1].isnumeric() else 0
        valeur = val_conf[2].strip()
        alias = val_conf[3].strip() if len(val_conf) > 3 else ""
        mode_fichier = int(val_conf[4]) if len(val_conf) > 4 and val_conf[4].isdigit() else None
        if force is not None:
            mode = force
        else:
            mode = mode_fichier if mode_fichier is not None else mode_demande

        conf.stocke_valeur(valeur, alias.replace("\n", ""), mode_force=mode, ordre=ordre)
        # on ignore


def lire_conf_csv(schema_courant, fichier, mode_alias, cod):
    """lit un fichier de conformites au format csv"""
    if not os.path.isfile(fichier):
        print("schema: ::: warning fichier conformites introuvable ", fichier)
        return
    #    n=0
    with open(fichier, "r", encoding=cod) as entree:
        decode_conf_csv(schema_courant, entree, mode_alias=mode_alias)


def _lire_geometrie_csv(classe, v_tmp, dimension):
    """'decode une geometrie en fichier csv"""
    # l=v[3].split('_')
    # if l[0] not in '0123':
    gref = v_tmp[4].upper()
    if "GEOMETRY" in gref:  # description de geometrie postgis
        gref = gref.replace("GEOMETRY", "")
        gref = gref.replace("(", "")
        gref = gref.replace(")", "")
        gref = gref.split(",")[0]
        gref = gref.replace("Z", "")

    if v_tmp[5] == "courbe":
        classe.info["courbe"] = "1"

    if gref not in SCI.CODES_G:
        print("schema:", classe.nom, "erreur type", v_tmp[4], v_tmp)
    classe.info["type_geom"] = SCI.CODES_G[gref]
    classe.alias = v_tmp[3]
    if "#" in v_tmp[5]:
        for val in v_tmp[5].split(","):
            if val:
                param = val.split(":", 1)
                nom = param[0]
                contenu = param[-1]
                classe.info[nom] = contenu

    classe.multigeom = classe.info["type_geom"] > "1"
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
    """ valide la presence de l'entete"""

    if ligne and ligne[0] == "!":
        return [j.strip() for j in ligne[1:-1].split(sep)]
    elif len(ligne) > 3 and "!" in ligne[:3]:
        print(" schema io:detecte commentaire utf8")
        if cod != "utf-8":
            print("erreur encodage de lecture ", cod, " choisir utf8")
            raise TypeError
        return True
    print("ligne bizarre", ligne)
    return False


def _toint(val):
    try:
        return int(val)
    except ValueError:
        return 0


def _decode_attribut_csv(liste):
    """ decode un attribut en csv et en fait un dictionnaire """
    noms = [
        "nom_attr",
        "alias",
        "type",
        "graphique",
        "multiple",
        "defaut",
        "obligatoire",
        "conformite",
        "dimension",
        "taille",
        "decimales",
        "nom_court",
        "fin",
        "index",
        "fkdef",
    ]
    att_dict = dict(zip(noms, liste[2:17]))
    ll_tmp = att_dict["type"].split(":")
    if len(ll_tmp) > 1:
        att_dict["clef"] = ll_tmp[1]
    att_dict["type_attr"] = ll_tmp[0].lower()
    att_dict["type_attr_base"] = att_dict["type_attr"]
    att_dict["graphique"] = att_dict["graphique"] == "oui"
    att_dict["multiple"] = att_dict["multiple"] == "oui"
    att_dict["obligatoire"] = att_dict["obligatoire"] == "oui"

    if att_dict["conformite"]:
        # print 'conformite',v
        att_dict["type_attr"] = att_dict["conformite"].lower()
        att_dict["type_attr_base"] = "text"
        # nom_conformite = type_attr
    att_dict["taille"] = _toint(att_dict.get("taille", 0))
    att_dict["decimales"] = _toint(att_dict.get("decimales", 0))
    att_dict["nom_court"] = att_dict.get("nom_court", "")
    if att_dict["nom_court"] == "fin":
        att_dict["nom_court"] = ""
    if att_dict["fkdef"]:
        if "(" in att_dict["fkdef"]:
            tmp = att_dict["fkdef"].strip().split("(")
            att_dict["fkdef"] = tmp[0]
            att_dict["fkprop"] = tmp[1][:-1]
    return att_dict


def decode_classes_csv(schema_courant, entree):
    """stocke les  classes  dans le schema"""
    metas = dict()
    for i in entree:
        if not i:
            continue
        if i[0] == "!":
            if i.startswith("!meta;"):  # le fichier contient des metadonnees
                v_tmp = [
                    j.strip().split("=") if "=" in j else [j.strip(), ""] for j in i.split(";") if j.strip() and j!='!meta'
                ]
                print ('decodage metas', v_tmp)
                metas = {var[0]: var[1] for var in v_tmp}
                schema_courant.metas = metas
            continue
        v_tmp = [j.strip() for j in i.split(";")]

        if len(v_tmp) < 11:
            print("sio:ligne trop courte ", len(v_tmp))
            continue
        clef_etr = ""
        props_fk = ""
        index = ""
        if len(v_tmp) >= 16:
            index = v_tmp[15]
        if len(v_tmp) >= 17:
            if v_tmp[16].replace("\n", "").strip() != "":
                clef_etr = v_tmp[16].replace("\n", "")
                if "(" in clef_etr:
                    tmp = clef_etr.strip().split("(")
                    clef_etr = tmp[0]
                    props_fk = tmp[1][:-1]

        groupe = v_tmp[0]
        nom = v_tmp[1]
        #            print ('schema_io:lecture_attribut ', nom, v_tmp[2])
        if groupe and nom:
            schema_courant.origine = "L"
            idorig = (groupe, nom)
            ident = idorig
            classe = schema_courant.setdefault_classe(ident)
            attr = v_tmp[2]
            #                print ("sio : lecture", classe.identclasse, attr)
            #                if not attr:
            #                    print ('sio: definition classe', idorig, ident)
            #                    continue
            alias = v_tmp[3]
            ll_tmp = v_tmp[4].split(":")
            if len(ll_tmp) > 1:
                clef_etr = ll_tmp[1]
            type_attr = ll_tmp[0].lower()
            type_attr_base = type_attr
            graphique = v_tmp[5] == "oui"
            multiple = v_tmp[6] == "oui"
            defaut = v_tmp[7]
            obligatoire = v_tmp[8] == "oui"
            # nom_conformite = ''
            if v_tmp[9]:
                # print 'conformite',v
                type_attr = v_tmp[9].lower()
                type_attr_base = "text"
                # nom_conformite = type_attr
            dimension = v_tmp[10]
            taille = int(v_tmp[11]) if len(v_tmp) > 11 and v_tmp[11].isnumeric() else 0
            dec = int(v_tmp[12]) if len(v_tmp) > 12 and v_tmp[12].isnumeric() else 0
            nom_court = ""
            if len(v_tmp) > 13:
                nom_court = v_tmp[13] if v_tmp[13] != "fin" else ""

            if attr == "geometrie":
                _lire_geometrie_csv(classe, v_tmp, dimension)
            elif attr:  # c'est un attribut
                classe.stocke_attribut(
                    attr,
                    type_attr,
                    defaut=defaut,
                    type_attr_base=type_attr_base,
                    force=True,
                    taille=taille,
                    dec=dec,
                    alias=alias,
                    ordre=-1,
                    parametres_clef=props_fk,
                    nom_court=nom_court,
                    clef_etr=clef_etr,
                    index=index,
                    obligatoire=obligatoire,
                    multiple=multiple,
                )
                # print ('sio:stocke_attribut',attr,type_attr,nom_court, v_tmp)
                # print ('stocke',classe.attributs[attr].type_att)
                if graphique:
                    classe.stocke_attribut(
                        attr + "_X",
                        "reel",
                        "",
                        "reel",
                        ordre=-1,
                        obligatoire=obligatoire,
                        multiple=multiple,
                    )
                    classe.stocke_attribut(
                        attr + "_Y",
                        "reel",
                        "",
                        "reel",
                        ordre=-1,
                        obligatoire=obligatoire,
                        multiple=multiple,
                    )
            else:  # on ne fait que definir l'alias de la classe
                if v_tmp[11].isnumeric():
                    classe.poids = int(v_tmp[11])
                classe.alias = v_tmp[3]
                if v_tmp[5] == "courbe":
                    classe.courbe = True
                    classe.info["courbe"] = "1"
                if v_tmp[9].isnumeric():
                    classe.srid = str(int(v_tmp[9]))
                # cas particulier des classes alpha sans attribut geom
                if v_tmp[4] in SCI.CODES_G:
                    classe.info["type_geom"] = SCI.CODES_G[v_tmp[4]]


def lire_classes_csv(schema_courant, fichier, cod):
    """lit un fichier de description de classes au format csv"""
    if not os.path.isfile(fichier):
        print("!!!!!!! schema: erreur fichier schema introuvable ", fichier)
        return
    #    print('sio:lecture classes', fichier)
    with open(fichier, "r", encoding=cod) as entree:
        ent = _valide_entete_csv(entree.readline(), cod, ";")
        if not ent:
            print("entete invalide ", ent)
            entree.seek(0)
        decode_classes_csv(schema_courant, entree)


def fichs_schema(racine):
    """determine les fichiers lies au schema"""
    f_aux = {
        "_classes",
        "_mapping",
        "_enumerations",
        "complements_enumerations.csv",
        "complements_classes.csv",
        "complements_mapping.csv",
    }

    fschemas = {racine + i for i in f_aux}
    return fschemas


def lire_schema_csv(mapper, nom, fichier, mode_alias="num", cod="cp1252", schema=None, specifique=None):
    """lit un schema conplet en csv"""
    if schema is None:
        #        print ('lecture_csv')
        schema = mapper..init_schema(nom, origine="L")

    fichier_conf = "_".join((fichier, "enumerations.csv"))
    fichier_classes = "_".join((fichier, "classes.csv"))
    mapping = "_".join((fichier, "mapping.csv"))
    # modifications manuelles du schema
    complements_conf = "_".join((fichier, "complements_enumerations.csv"))
    complements_classe = "_".join((fichier, "complements_classes.csv"))
    complements_mapping = "_".join((fichier, "complements_mapping.csv"))
    # on lit d'abord les mappings pour voir s'il faut rectifier les schemas en entree
    if os.path.exists(mapping):
        lire_mapping(schema, mapping, cod)
    if os.path.exists(complements_mapping):
        lire_mapping(schema, complements_mapping, cod)

    lire_conf_csv(schema, fichier_conf, mode_alias, cod=cod)
    if os.path.exists(complements_conf):
        lire_conf_csv(schema, complements_conf, mode_alias, cod=cod)
    # g.conformites.calcule_taille()
    lire_classes_csv(schema, fichier_classes, cod)
    if os.path.exists(complements_classe):
        lire_classes_csv(schema, complements_classe, cod)
    if specifique:  # on lit des informations complementaires
        for i in specifique:
            fichier_special = "_".join((fichier, i + ".csv"))
            if os.path.exists(fichier_special):
                liste = open(fichier_special, "r").readlines()
                entete = liste[0]
                contenu = liste[1:]
                schema.elements_specifiques.divers[i] = (entete, contenu)

    FSC.analyse_interne(schema, "init")
    #    print("schema: lecture_schema realisee --->", fichier, len(schema.classes),
    #          "<-----")
    #    print ('mapping enregistre','\n'.join(schema.mapping_schema(fusion=True)[:10]))
    return schema


def ecrire_fich_csv(chemin, nom, contenu, cod):
    """ ecriture physique du csv"""
    print ('ecriture_csv', chemin, nom, cod)
    try:
        with open(chemin + nom, "w", encoding=cod, errors="replace") as fich:
            fich.write("\n".join(contenu))
            fich.write("\n")
    except PermissionError:
        print("!" * 30 + "impossible d'ecrire le fichier ", chemin + nom)


def ecrire_schema_csv(rep, schema, mode, cod="utf-8", modeconf=-1):
    """ ecrit un schema en csv """
    os.makedirs(rep, exist_ok=True)

    init = False
    if schema.origine == "B" or schema.origine == "L":
        init = True
    conf, classes = sortir_schema_csv(schema, mode=mode, modeconf=modeconf, init=init)
    mapping = schema.mapping_schema()
    nomschema = str(os.path.basename(schema.nom.replace("#", "_")))
    deftrig = ['schema;table;trigger;condition;fonction;etendue;timing;declencheur']
    if "def_triggers" in schema.elements_specifiques:
        for table, triggers in sorted(schema.elements_specifiques["def_triggers"].items()):
            # lignes = [';'.join(table+(trig,)+definition) for trig, definition in sorted(triggers.items())]
            lignes = [';'.join(table+(trig,)+tuple(str(i) for i in definition)) for trig, definition in sorted(triggers.items())]
            deftrig.extend(lignes)
    metas = dict()
    metas["origine"] = schema.origine
    if rep:
        chemref = os.path.join(str(rep), nomschema)
        if len(classes) > 1:
            # print (conf,'\n',schemas)
            #        print("schema: ecriture schema csv", chemref+" en csv ("+cod+")")
            ecrire_fich_csv(chemref, "_classes.csv", classes, cod)
            ecrire_fich_csv(chemref, "_enumerations.csv", conf, cod)
            ecrire_fich_csv(chemref, "_mapping.csv", mapping, cod)
            if deftrig:
                ecrire_fich_csv(chemref, "_triggers.csv", deftrig, cod)
    else:
        return classes, conf, mapping, deftrig, metas
