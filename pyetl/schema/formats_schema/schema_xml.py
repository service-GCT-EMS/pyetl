# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 09:28:45 2014
gestion des entrees et sorties de schemas
@author: 89965
"""
import os
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from .. import schema_interne as SCI


ESC_XML = lambda t: (
    str(t)
    .replace("&", "&amp;")
    .replace("'", "&apos;")
    .replace("<", "&lt;")
    .replace("\\'", "&apos;")
)


def _sortir_conformite_xml(conf, mode=-1, init=False):
    """ecrit une conformite en format xml"""
    entete = [
        '<conformite nom="'
        + conf.nombase
        + '" type="'
        + str(conf.type_conf)
        + '" nb_elements="'
        + str(len(conf.stock))
        + '">'
    ]
    if conf.usages:
        entete.extend(
            [
                '\t<usage schema = "'
                + schema
                + '" classe = "'
                + classe
                + '" attribut = "'
                + attribut
                + '"/>'
                for schema, classe, attribut in sorted(conf.usages, key=lambda x: x[1])
            ]
        )

    valeurs = []
    for i in sorted(conf.stock.values(), key=lambda v: v[2]):
        valeurs.append(
            '\t<VALEUR v="'
            + (ESC_XML(i[4]) if init else ESC_XML(i[0]))
            + '" alias="'
            + ESC_XML(i[1])
            + '" ordre="'
            + str(i[2])
            + '" mode="'
            + (str(mode) if mode != -1 else str(i[3]))
            + '"/>'
        )
    entete.extend(valeurs)
    entete.append("</conformite>")
    return "\n".join(entete)


def _sortir_attribut_xml(classe, attr, keys):
    """ecrit une definition d'attribut en xml"""

    type_att = "enum" if attr.conformite else attr.get_type()
    type_att_base = attr.nom_conformite if attr.conformite else attr.type_att_base
    texte = (
        "\t<attribut nom='"
        + ESC_XML(attr.nom)
        + "' type='"
        + str(type_att)
        + "' type_base='"
        + str(type_att_base)
        + "' fonction='"
        + ESC_XML(attr.defaut)
        + "' alias='"
        + ESC_XML(attr.alias)
        + "' taille='"
        + str(attr.taille)
        + "' decimales='"
        + str(attr.dec)
        + "'"
    )

    if attr.nom in keys:
        #        print ("clefs primaires",keys)
        texte = (
            texte
            + " clef_primaire = 'oui' ordre = '"
            + str(keys.index(attr.nom) + 1)
            + "'"
        )
    if attr.nom in classe.fkey_attribs:
        cible, params = classe.getfkey(attr.nom)
        dec = cible.split(".")
        if len(dec) == 3:
            c_schema, c_classe, c_attr = dec
            texte = (
                texte
                + " clef_etrangere = 'oui'"
                + " cible_schema = '"
                + c_schema.replace("FK:", "")
                + "'"
                + " cible_classe = '"
                + c_classe
                + "'"
                + " cible_attribut = '"
                + c_attr
                + "'"
                + " contrainte = '"
                + str(params)
                + "'"
            )
    for i in classe.indexes:
        if attr.nom in classe.indexes[i]:
            texte = texte + " index = 'oui'"
            break
    if attr.oblig:
        texte = texte + " obligatoire = 'oui'"
    if attr.unique:
        texte = texte + " unique = 'oui'"

    if attr.conf and attr.nom_conformite == "":
        description = [texte + ">"]
        if attr.type_att in {"E", "EL", "F", "S", "BS", "N"} or attr.type_att_base in {
            "E",
            "EL",
            "F",
            "S",
            "BS",
            "N",
        }:
            # types numeriques
            # print "type attribut",self.type_att
            try:
                vals = sorted([i for i in attr.valeurs if i], key=float)
            except ValueError:
                vals = []
                print(
                    "erreur: sortie schema xml erreur valeurs",
                    attr.type_att,
                    attr.type_att_base,
                    attr.valeurs,
                )
        else:
            vals = sorted(attr.valeurs)

        valeurs_conf = [
            "\t\t<valeur_conformite v='"
            + ESC_XML(str(j))
            + "' n='"
            + str(attr.valeurs[j])
            + "'/>"
            for j in vals
        ]
        description.extend(valeurs_conf)
        description.append("\t</attribut>")
    else:
        description = [texte + "/>"]
    return description


def _sortir_schema_classe_xml(sc_classe, mode="util"):
    """ecrit une definition de classe en xml"""

    nom_atts = sc_classe.get_liste_attributs(sys=True)
    type_stockage = sc_classe.types_stock.get(sc_classe.type_table, "")
    nb_obj = sc_classe.objcnt
    if not nb_obj:
        nb_obj = sc_classe.getinfo("objcnt_init")
    if mode == "fusion":
        nb_obj = sc_classe.poids
    description = [
        "<classe nom='"
        + sc_classe.nom
        + ("' nberr='" + str(sc_classe.errcnt) if sc_classe.errcnt else "")
        + "' groupe='"
        + str(sc_classe.groupe)
        + "' alias='"
        + ESC_XML(sc_classe.alias)
        + "' type='"
        + (
            str(SCI.TYPES_G[sc_classe.info["type_geom"]])
            if sc_classe.info["type_geom"] != "0"
            else "ALPHA"
        )
        + "' clef_primaire='"
        + sc_classe.getpkey
        + "' nb_objets='"
        + str(nb_obj)
        + "' type_table='"
        + type_stockage
        + "'>"
    ]
    keys = sc_classe.getpkey.split(",")
    for i in nom_atts:
        attribut = sc_classe.attributs[i]
        if attribut.conformite:
            attribut.taille = attribut.conformite.taille
        description.extend(_sortir_attribut_xml(sc_classe, attribut, keys))
    complement = "MULTIPLE" if sc_classe.multigeom else "SIMPLE"
    arc = "COURBE" if sc_classe.info["courbe"] else "LIGNE"
    dimension = sc_classe.info["dimension"]
    # print 'type_geom',self.info["type_geom"]
    if sc_classe.info["type_geom"]:
        description.append(
            "\t<geometrie type='"
            + str(SCI.TYPES_G[sc_classe.info["type_geom"]])
            + "' "
            + " complement='"
            + complement
            + "' arc='"
            + arc
            + "' dimension='"
            + dimension
            + "' nom_geometrie='"
            + sc_classe.info["nom_geometrie"]
            + "'/>"
        )
    description.append("</classe>")
    # print "description",description
    return "\n".join(description)


def sortir_schema_xml(sch, header, alias_schema, codec, mode="util"):
    """ecrit un schema complet en xml"""

    entete = (
        '<?xml version="1.0" encoding="'
        + codec
        + '"?>\n'
        + (header + "\n" if header else "")
        + "<structure nom='"
        + sch.nom
        + ("' alias='" + alias_schema if alias_schema else "")
        + "' type='"
        + sch.origine
        + "'>"
    )
    conf = ""
    classes = ""
    # print ("schema_io:sortir schema xml",sch.nom,sch.classes)
    nbclasses = 0
    if sch.conformites:
        conf = (
            "<conformites>\n"
            + "\n".join(
                [
                    _sortir_conformite_xml(sch.conformites[i])
                    for i in sorted(sch.conformites.keys())
                ]
            )
            + "\n</conformites>\n"
        )
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
            alias_g = ESC_XML(sch.alias_groupes.get(groupe, ""))
            #            print ('sortir schema',g,alias_g,sch.alias_groupes)
            description.append("<schema nom='" + groupe + "' alias='" + alias_g + "'>")
            description.append("<classes>")
            nbclasses += 1
            for classe in groupes[groupe]:
                description.append(
                    _sortir_schema_classe_xml(sch.classes[(groupe, classe)], mode=mode)
                )
            description.append("</classes>")
            description.append("</schema>")
        description.append("</schemas>")
        classes = "\n".join(description)
    if nbclasses:
        return entete + "\n" + conf + "\n" + classes + "\n</structure>"
    return None


def fusion_schema_xml(schema, fichier, cod="utf-8"):
    """# complete la lecture d'un fichier"""
    origine = ET.parse(open(fichier, "r", encoding=cod))
    #    g=schema(groupe)
    #    g.origine='L'
    for i in origine.getiterator("conformite"):
        nom = i.get("nom")
        type_c = i.get("type")
        mode = i.get("mode")
        conf = schema.get_conf(nom, type_c=type_c, mode=mode)
        for j in i.getiterator("VALEUR"):
            conf.stocke_valeur(j.get("v"), j.get("alias"))
        # print "stockage_conf",conf.valeurs
    for i in origine.getiterator("classe"):
        nom = i.get("nom")
        groupe = i.get("schema")
        ident = (groupe, nom)
        classe = schema.setdefault_classe(ident)
        #        g[nom]=sc
        for j in i.getiterator("attribut"):
            nom_a = j.get("nom")
            type_a = j.get("type")
            type_base = j.get("type_base")
            defaut_a = j.get("defaut")
            taille_a = j.get("taille")
            dec_a = j.get("decimales")
            classe.stocke_attribut(
                nom_a, type_a, defaut_a, type_base, taille=taille_a, dec=dec_a, ordre=-1
            )

        for j in i.getiterator("geometrie"):
            classe.info["type_geom"] = j.get("type")
            classe.alias = j.get("alias")
            dimension = j.get("dimension", "2")
            classe.setdim(dimension)


def lire_schema_xml(mapper, base, fichier, cod="utf-8"):
    """lit un ensemble de fichiers schema en xml"""
    print("lecture xml")
    schema = mapper.init_schema(base, origine="L")
    fusion_schema_xml(schema, fichier, cod=cod)
    return schema


def ecrire_schema_xml(
    rep, schema, mode="util", cod="utf-8", header="", alias="", prefix=""
):
    """ecrit un schema en xml"""
    os.makedirs(rep, exist_ok=True)
    alias = ESC_XML(alias)
    xml = sortir_schema_xml(schema, header, alias, cod, mode=mode)
    nomschema = prefix + schema.nom.replace("#", "_")

    if xml:
        print("schema: ecriture schema xml", os.path.join(rep, nomschema) + ".xml")
        open(os.path.join(rep, nomschema + ".xml"), "w", encoding=cod).write(xml)
    if not prefix:
        copier_xsl(rep)


def copier_xsl(rep):
    """ copie un xsl par defaut pour la visibilite du schema"""
    xslref = os.path.join(os.path.dirname(__file__), "xsl.zip")
    #    print(" copie fichier ", xslref)
    with ZipFile(xslref) as xsl:
        xsl.extractall(path=os.path.join(rep, "xsl"))
