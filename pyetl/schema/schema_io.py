# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 09:28:45 2014
gestion des entrees et sorties de schemas
@author: 89965
"""
import os

# import xml.etree.ElementTree as ET
from pyetl.formats.db import DATABASES

from . import schema_interne as SCI
from . import fonctions_schema as FSC

from .formats_schema.schema_xml import ecrire_schema_xml, lire_schema_xml
from .formats_schema.schema_csv import ecrire_schema_csv, lire_schema_csv


def fusion_schema(nom, schema, schema_tmp):
    """fusionne 2 schemas en se basant sur les poids pour garder le bon"""
    if not schema or not schema_tmp:
        print("schema vide fusion impossible", nom, schema, schema_tmp)
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
    print ('mapping_fusion','\n'.join(liste_mapping[:10]))
    schema.init_mapping(liste_mapping[1:])

    del schema_tmp


def lire_schemas_multiples(
    nom, chemin, mode_alias="num", cod="utf-8", cod_csv=None, specifique=None, fusion=None
):
    """initialise le schema et rajoute tous les elements necessaires"""
    schema = SCI.Schema(nom)
    if cod_csv is None:
        cod_csv = cod
    if os.path.isdir(chemin):
        rep = chemin
        racine = ""
        fusion = True
    else:
        rep = os.path.dirname(chemin)
        racine = os.path.basename(chemin).lower()
        if fusion is None:
            fusion = False

    for element in os.listdir(rep):
        #            print ('examen ',element ,racine)
        if racine in element.lower():
            ext = os.path.splitext(element)[1]
            if "classes" in element and ext == ".csv":
                # print("schema:lecture ",element,racine,os.path.splitext(element))
                element_modif = "_".join(element.split("_")[:-1])
                fichier = os.path.join(rep, element_modif)
                ext = os.path.splitext(element)[1]
                fusion_schema(
                    nom,
                    schema,
                    lire_schema_csv("tmp", fichier, mode_alias, cod=cod_csv, specifique=specifique),
                )
            elif ext == ".xml":
                fusion_schema(nom, schema, lire_schema_xml("tmp", element, cod=cod_csv))
    schema.map_classes()
    if schema.classes:
        print("schema:classes totales", len(schema.classes), cod)
    else:
        print("pas de definition de schema", rep, racine)
    return schema


def set_transaction(liste):
    """ ajoute des transactions explicites sur les fichiers"""
    liste.insert(0, "START TRANSACTION;\n")
    liste.append("COMMIT;\n")


def ecrire_fichier_sql(rep, nomschema, numero, nomfich, valeurs, cod="utf-8", transact=False):
    """ ecrit la description du schema en sql """
    if valeurs is None:
        return
    if numero:
        nomfich = os.path.join(rep, "_".join((numero, nomschema, nomfich + ".sql")))
    else:
        nomfich = os.path.join(rep, "_".join((nomschema, nomfich + ".sql")))
    if transact:
        set_transaction(valeurs)
    nberr = 0
    for i in valeurs:
        lignes = i.split("\n")
        for j in lignes:
            try:
                j.encode(cod)
            except UnicodeEncodeError:
                print("!!!!!!!!!!!!!!!!!! erreur d'encodage sur un caractère (?)")
                print(j.encode(cod, errors="replace"))
                nberr += 1
    if nberr:
        print("schema: ecriture schema sql", nomfich, cod)
        print("erreurs d" "encodage", nberr)

    with open(nomfich, "w", encoding=cod, errors="replace") as fich:
        codecinfo = (
            "-- ########### encodage fichier "
            + str(fich.encoding)
            + " ###(controle: n°1: éàçêè )####\n"
        )
        fich.write(codecinfo)
        fich.write("\n".join(valeurs))


def ecrire_schema_sql(
    rep,
    schema,
    type_base="std",
    cod="utf-8",
    modeconf=-1,
    dialecte=None,
    transact=False,
    autopk=False,
    role=None,
):
    """ ecrit un schema en script sql """
    # on determine le dialacte sql a choisir
    os.makedirs(rep, exist_ok=True)

    if dialecte == "natif":
        if schema.dbsql:  # dialecte sql adapte a la base de sortie
            gsql = schema.dbsql
        else:
            print("attention pas de dialecte natif", schema.nom)
            dialecte = "postgis"
            gsql = DATABASES[dialecte].gensql()
    elif schema.dbsql and schema.dbsql.dialecte == dialecte:
        gsql = schema.dbsql
    elif dialecte in DATABASES:
        gsql = DATABASES[dialecte].gensql()
    else:
        dialecte = "postgis"
        type_base = "basic"
        gsql = DATABASES[dialecte].gensql()
    #    print('ecriture schema sql', schema.nom, gsql.dialecte, len(schema.classes))
    gsql.initschema(schema)
    nomschema = schema.nom
    nomschema = nomschema.replace("#", "_")
    nomschema = os.path.basename(nomschema)

    #    print('sio:ecriture schema sql pour ', gsql.dialecte, nomschema)
    if type_base == "basic" or type_base == "consult":
        gsql.setbasic(type_base)

    tsql, dtsql, csql, dcsql = gsql.sio_cretable(cod, autopk=autopk, role=role)
    crsc, dsc, dscc = gsql.sio_creschema(cod)

    csty = gsql.sio_crestyle()

    if type_base == "basic":
        # on concatene tout
        tout = crsc
        tout.extend(tsql)
        ecrire_fichier_sql(rep, nomschema, "01", "schema", tout, cod, False)

    else:

        if tsql:
            ecrire_fichier_sql(rep, nomschema, "03", "tables", tsql, cod, transact)
            ecrire_fichier_sql(rep, nomschema, "11", "droptables", dtsql, cod)
        if csql:
            ecrire_fichier_sql(rep, nomschema, "02", "enums", csql, cod, transact)
            ecrire_fichier_sql(rep, nomschema, "12", "dropenums", dcsql, cod)
        if csty:
            ecrire_fichier_sql(rep, nomschema, "04", "styles", csty, cod)
        if crsc:
            ecrire_fichier_sql(rep, nomschema, "01", "schemas", crsc, cod, transact)
            ecrire_fichier_sql(rep, nomschema, "13", "dropschemas", dsc, cod)
            ecrire_fichier_sql(rep, nomschema, "99c", "dropschemas", dscc, cod)


def ecrire_au_format(schema, rep, formats_a_sortir, stock_param, mode, confs):
    """ sort un schema dans les differents formats disponibles """

    nom = schema.nom.replace("#", "")
    rep_s = os.path.join(rep, 'schemas')
    cod = stock_param.get_param("codec_sortie", "utf-8")

    for form in formats_a_sortir:
        #        print('sio: ecrire_schema', rep_s, schema.nom, form)
        if "sql" in form:  # on met le sql en premier car on modifie des choses
            #            print('sio:sortie sql', schema.nom, 'rep:',
            #                  rep_s, schema.dbsql, schema.dbsql.connection if schema.dbsql else 'NC', form)
            dialecte = "sql"
            if ":" in form:
                dialecte = form.split("sql:")[1]
            else:
                dialecte = stock_param.get_param("base_destination", "sql")

            if dialecte == "sql" and schema.dbsql:
                dialecte = "natif"

            autopk = stock_param.get_param("autopk", "")
            role = stock_param.get_param("db_role")
            if not role:
                role = None
            type_base = stock_param.get_param("dbgenmode")
            if type_base and type_base not in {"basic", "consult"}:
                print("type base inconnu ", type_base, "passage en standard")
                type_base = None
            if type_base == "basic":
                schema.setbasic(type_base)
                autopk = "" if autopk == "no" else True
                rep_s = rep


            print("dialecte de sortie", dialecte)

            ecrire_schema_sql(
                rep_s,
                schema,
                type_base=type_base,
                cod=cod,
                modeconf=confs,
                dialecte=dialecte,
                transact=stock_param.get_param("transact"),
                autopk=autopk,
                role=role,
            )
        if "csv" in form:
            cod_csv = stock_param.get_param("codec_csv", "utf-8")
            ecrire_schema_csv(rep_s, schema, mode, cod=cod_csv, modeconf=confs)
        if form == "xml":
            #            header = stock_param.get_param('xmlheader', '')
            #            if header:
            #                header = header+'\n'
            header = ""
            header = header + stock_param.get_param("xmldefaultheader")

            #            alias = ESC_XML(stock_param.get_param('xmlalias'))
            ecrire_schema_xml(
                rep_s,
                schema,
                mode=mode,
                cod="utf-8",
                header=header,
                alias=stock_param.get_param("xmlalias"),
            )
        #            copier_xsl(rep_s)

        if form == "xml_d":

            header = stock_param.get_param("xmlheader_dist", "")
            prefix = stock_param.get_param("xmlprefix_dist", "d")
            if header:
                header = header + "\n"
                #            header = ''
                #            header = header+stock_param.get_param('xmldefaultheader')

                #                alias = ESC_XML(stock_param.get_param('xmlalias'))
                ecrire_schema_xml(
                    rep_s,
                    schema,
                    mode=mode,
                    cod="utf-8",
                    header=header,
                    alias=stock_param.get_param("xmlalias"),
                    prefix=prefix,
                )
            else:
                print("header distant (xmlheader_dist) non defini")


def ecrire_schemas(stock_param, rep_sortie, mode="util", formats="csv", confs=-1):
    """prepare les schemas pour la sortie """
    #    print('ecriture_schemas', mode, stock_param.schemas.keys())
    if mode == "no":
        return
    #    rep_sortie = stock_param.get_param('sortie_schema', stock_param.get_param('_sortie'))
    #    rep_sortie = stock_param.get_param('_sortie')
    type_schemas_a_sortir = stock_param.get_param("orig_schema")
    print("sio:repertoire sortie schema", stock_param.idpyetl, rep_sortie)
    #        raise FileNotFoundError

    for i in formats.split(","):  # en cas de format inconnu on sort en csv
        if i not in ["csv", "xml"] and "sql" not in i:
            formats = formats + ",csv"
            break

    schemas = stock_param.schemas

    a_sortir = stock_param.get_param("schemas_a_sortir")
    a_sortir = a_sortir.split(",") if a_sortir else None
    for i in schemas:
        #        print('ecriture schema', i, len(schemas[i].classes))
        if not i:
            continue
        if a_sortir and i not in a_sortir:
            print("schema non sorti", i, "(", a_sortir, ")")
            continue
        mode_sortie = schemas[i].mode_sortie if schemas[i].mode_sortie is not None else mode
        #        print('sortir schema ', i, mode_sortie, len(schemas[i].classes),
        #              FSC.analyse_interne(schemas[i], mode_sortie))
        if i.startswith("#") and mode_sortie != "int":
            continue  # on affiche pas les schemas de travail
        if not rep_sortie:

            print("sio:pas de repertoire de sortie ", rep_sortie, stock_param.liste_params)
            raise NotADirectoryError("repertoire de sortie non défini")

        if stock_param.schemas[i].origine == "G":
            FSC.analyse_conformites(schemas[i])
        #        print('avant analyse ', i, len(schemas[i].classes),
        #              len(schemas[i].conformites),mode_sortie)
        #        print('choix', FSC.analyse_interne(schemas[i], mode_sortie,
        #                                           type_schema=type_schemas_a_sortir))
        if FSC.analyse_interne(schemas[i], mode_sortie, type_schema=type_schemas_a_sortir):
            formats_a_sortir = set(formats.split(","))
            if schemas[i].format_sortie:
                if schemas[i].format_sortie == "sql":
                    dialecte = False
                    for form in formats_a_sortir:
                        if "sql:" in form:
                            dialecte = True
                    if not dialecte:
                        formats_a_sortir.add("sql")
                else:
                    formats_a_sortir.add(schemas[i].format_sortie)
            # controle du sql et de ses dialectes
            #            print('sio:analyse interne ', i, len(schemas[i].classes), formats, mode_sortie)
            ecrire_au_format(
                schemas[i], rep_sortie, formats_a_sortir, stock_param, mode_sortie, confs
            )


# =================formatage interne des schemas pour les traitements en parallele================


def retour_schemas(schemas, mode="util"):
    """renvoie les schemas pour un retour"""
    retour = dict()
    if mode == "no":
        return retour
    for nom, schema in schemas.items():
        #        print('ecriture schema', nom, len(schema.classes))
        if not nom:
            continue
        mode_sortie = schema.mode_sortie if schema.mode_sortie is not None else mode
        if nom.startswith("#") and mode_sortie != "int":
            continue  # on affiche pas les schemas de travail
        if schema.origine == "G":
            FSC.analyse_conformites(schema)
        #        print ('avant analyse ', nom ,FSC.analyse_interne(schema, mode_sortie))
        if FSC.analyse_interne(schema, mode_sortie):
            #            print ('stockage', nom, len(schema.__dic_if__))
            retour[nom] = schema.__dic_if__
    return retour


def integre_schemas(schemas, nouveaux):
    """ recree les schemas apres transmission"""
    nomschemas = set()
    for nom, description in nouveaux.items():
        nomschemas.add(nom)
        tmp = SCI.Schema(nom)
        tmp.from_dic_if(description)

        #        print ('recup schema ', nom, tmp, schemas.get(nom))
        if nom in schemas:
            fusion_schema(nom, schemas[nom], tmp)
        else:
            schemas[nom] = tmp
    #            schemas[nom].origine=metas['origine']
    #    print ('schemas recuperes ',nomschemas,schemas.keys())
    for nom in nomschemas:  # on reporte les comptages d'objets
        for cla in schemas[nom].classes.values():
            cla.objcnt = cla.poids


#    print ('fin_recup_schema')
#    print ('recup_schema_csv',ecrire_schema_csv(None, schemas['elyx_prod'],'all', modeconf=-1))
#    print ('fin integration')
