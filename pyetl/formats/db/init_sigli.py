# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 22:15:56 2018

@author: claude
requetes de creation de la base sigli essentiellement
 un ensemble de definition de vues
"""

requetes_sigli = dict()

requetes_sigli[
    "info_vues"
] = """
		SELECT pg_views.schemaname AS nomschema,
			pg_views.viewname AS nomtable,
			pg_views.definition,
			false AS materialise
		   FROM pg_views
		  WHERE pg_views.schemaname != 'pg_catalog' AND pg_views.schemaname != 'information_schema'
		UNION
		 SELECT pg_matviews.schemaname AS nomschema,
			pg_matviews.matviewname AS nomtable,
			pg_matviews.definition,
			true AS materialise
		   FROM pg_matviews;
                     """
requetes_sigli[
    "def_fonctions_trigger"
] = """
         SELECT n.nspname AS schema,
            p.proname AS name,
            pg_get_functiondef(p.oid) AS definition
           FROM pg_proc p
             LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
          WHERE n.nspname <> 'pg_catalog'::name
            AND has_schema_privilege(n.nspname,'usage')
            AND n.nspname <> 'information_schema'::name
            AND p.prorettype = 'trigger'::regtype::oid;
          """

requetes_sigli[
    "info_triggers_old"
] = """
       SELECT event_object_schema AS schema,
           event_object_table AS table,
           trigger_name AS nom_trigger,
           action_condition AS condition,
           action_statement AS action,
           action_orientation AS declencheur,
           action_timing AS timing,
           array_to_string(array_agg(event_manipulation::text),' OR ') AS event
       FROM information_schema.triggers
       WHERE action_statement !~~ '%auteur%'
       GROUP BY event_object_schema,event_object_table,trigger_name,
                action_condition,action_statement,action_orientation,action_timing
       """
#          retour : schema, table, nom_trigger,condition,action,'row/statement',
#                  avant apres, operation(update...)
requetes_sigli[
    "info_triggers"
] = r"""
    with tmp1 as
     (SELECT n.nspname as nom_schema,
     c.relname as nom_table,
      t.tgname as nom_trigger,
       pg_catalog.pg_get_triggerdef(t.oid) as sql,
        t.tgenabled,
         t.tgisinternal
    FROM pg_catalog.pg_trigger t, pg_class c, pg_namespace n
    WHERE (NOT t.tgisinternal OR (t.tgisinternal AND t.tgenabled = 'D')) and t.tgrelid=c.oid and n.oid = c.relnamespace)

    SELECT nom_schema, nom_table, nom_trigger,
        substring(sql from 'TRIGGER|CONSTRAINT') as type_trigger,
        substring(sql from 'EXECUTE PROCEDURE (.*)') as action,
        substring(sql from 'FOR EACH (\w*)') as declencheur,
        substring(sql from ' (AFTER|BEFORE|INSTEAD OF) ') as timing,
        substring(sql from ' (UPDATE|DELETE|INSERT|TRUNCATE) ') as event,
        substring(sql from ' UPDATE OF (\S*) *(,\S*)* ') as colonnes,
        substring(sql from ' WHEN (.*) EXECUTE PROCEDURE') as condition,
        sql
        from tmp1
"""



requetes_sigli[
    "info_tables_distantes"
] = """
    SELECT ftrelid::regclass, srvname ,ftoptions
    FROM pg_foreign_table, pg_foreign_server fs
    WHERE ftserver =  fs.oid"""


requetes_sigli[
    "info_fk"
] = """
     SELECT c.confrelid::regclass AS cible,
        ( SELECT a.attname
               FROM pg_attribute a
              WHERE a.attrelid = c.conrelid AND a.attnum = c.conkey[1]) AS attribut_cible,
        ( SELECT a.attname
               FROM pg_attribute a
              WHERE a.attrelid = c.confrelid AND a.attnum = p2.conkey[1]) AS attributpk1_cible,
        ( SELECT a.attname
               FROM pg_attribute a
              WHERE a.attrelid = c.confrelid AND a.attnum = p2.conkey[2]) AS attributpk2_cible,
        ( SELECT a.adsrc
               FROM pg_attrdef a
              WHERE a.adrelid = p2.conrelid AND a.adnum = p2.conkey[1]) AS defaut_cible,
        c.conrelid::regclass AS fk,
        ( SELECT a.attname
               FROM pg_attribute a
              WHERE a.attrelid = c.confrelid AND a.attnum = c.confkey[1]) AS attribut_lien,
        ( SELECT a.attname
               FROM pg_attribute a
              WHERE a.attrelid = c.conrelid AND a.attnum = p.conkey[1]) AS attributpk1,
        ( SELECT a.attname
               FROM pg_attribute a
              WHERE a.attrelid = c.conrelid AND a.attnum = p.conkey[2]) AS attributpk2,
        ( SELECT a.adsrc
               FROM pg_attrdef a
              WHERE a.adrelid = p.conrelid AND a.adnum = p.conkey[1]) AS defaut
        'u'||c.confupdtype||',d'||c.confdeltype||',m'||c.confmatchtype||','
        || (case when c.condeferrable then 'defer' else 'nd' end) as parametres
       FROM pg_constraint c
         LEFT JOIN pg_constraint p ON c.conrelid = p.conrelid AND p.contype = 'p'::"char"
         LEFT JOIN pg_constraint p2 ON c.confrelid = p2.conrelid AND p2.contype = 'p'::"char"
      WHERE c.contype = 'f'::"char";
   """


requetes_sigli[
    "info_tables"
] = """

     WITH info_fk as (
         SELECT
         c.confrelid::regclass AS cible,
         c.conrelid::regclass AS fk,
         ( SELECT a.attname
               FROM pg_attribute a
              WHERE a.attrelid = c.conrelid AND a.attnum = c.conkey[1]) AS attribut_cible,
         ( SELECT a.attname
              FROM pg_attribute a
              WHERE a.attrelid = c.confrelid AND a.attnum = c.confkey[1]) AS attribut_lien
       FROM pg_constraint c
      WHERE c.contype = 'f'::"char"),

     t AS ( SELECT c.oid AS identifiant,
                n.nspname AS nomschema,
                c.relname AS nomtable,
                c.relkind AS type_table,
                i.indrelid,
                (i.indrelid::text || ':'::text) || array_to_string(i.indkey, ':'::text)
                    AS clef,
                row_number() OVER (PARTITION BY i.indrelid) AS num_index,
                i.indkey,
                champ.champ,
                i.indisprimary AS pk,
                i.indisunique AS uniq
               FROM pg_class c
                 LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                 LEFT JOIN pg_index i ON c.oid = i.indrelid
                 LEFT JOIN LATERAL unnest(i.indkey) champ(champ) ON true
              WHERE n.nspname <> 'public'::name
                  AND has_schema_privilege(n.nspname,'usage')
                  AND n.nspname <> 'information_schema'::name
                  AND n.nspname !~~ 'pg_%'::text
                  AND (c.relkind::text = ANY (ARRAY['r'::text, 'v'::text, 'm'::text, 'f'::text]))
            ), t2 AS (
             SELECT t.identifiant,
                t.nomschema,
                t.nomtable,
                t.type_table,
                t.num_index,
                t.champ AS num_champ,
                row_number() OVER (PARTITION BY t.clef) AS ordre_champs,
                pa.attname AS nom_champ,
                t.pk,
                t.uniq,
                t.clef
               FROM t
                 LEFT JOIN pg_attribute pa ON t.identifiant = pa.attrelid AND pa.attnum = t.champ
            ), t3 AS (
             SELECT t2.identifiant,
                t2.nomschema,
                t2.nomtable,
                t2.type_table,
                    CASE
                        WHEN t2.pk THEN string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs)
                        ELSE NULL::text
                    END AS clef_primaire,
                    CASE
                        WHEN t2.pk THEN NULL::text
                        WHEN t2.uniq THEN 'U:'::text ||
                            string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs)
                        WHEN (string_agg(t2.nom_champ::text, ','::text
                                         ORDER BY t2.ordre_champs)
                             IN (SELECT info_fk.attribut_lien::text AS attribut_lien
                                 FROM info_fk
                                 WHERE t2.identifiant = info_fk.fk::oid))
                            THEN 'K:'::text ||
                                 string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs)
                        WHEN string_agg(t2.nom_champ::text, ','::text
                                        ORDER BY t2.ordre_champs) <> 'geometrie'::text
                            THEN 'X:'::text
                                || string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs)
                        ELSE NULL::text
                    END AS index,
                    CASE
                        WHEN string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs) = 'geometrie'::text THEN 'geometrie'::text
                        ELSE NULL::text
                    END AS index_geometrique
               FROM t2
              GROUP BY t2.identifiant, t2.clef, t2.nomschema, t2.nomtable, t2.type_table, t2.pk, t2.uniq
            ), t4 AS (
             SELECT t3.identifiant,
                t3.nomschema,
                t3.nomtable,
                t3.type_table,
                string_agg(t3.index_geometrique, ''::text) AS index_geometrique,
                string_agg(t3.clef_primaire, ''::text) AS clef_primaire,
                string_agg(t3.index, ' '::text ORDER BY t3.index DESC) AS index,
                (((fk.attribut_lien::text || '->'::text) || (( SELECT ((( SELECT pg_namespace.nspname
                               FROM pg_namespace
                              WHERE pg_namespace.oid = pg_class.relnamespace))::text || '.'::text) || pg_class.relname::text
                       FROM pg_class
                      WHERE pg_class.oid = fk.cible::oid))) || '.'::text) || fk.attribut_cible::text AS clef_etrangere
               FROM t3
                 LEFT JOIN info_fk fk ON t3.identifiant = fk.fk::oid
              GROUP BY t3.identifiant, t3.nomschema, t3.nomtable, t3.type_table, fk.attribut_lien, fk.cible, fk.attribut_cible
            )
     SELECT
        --t4.identifiant AS oid,
        t4.nomschema,
        t4.nomtable,
        obj_description(t4.identifiant, 'pg_class'::name) AS commentaire,
        COALESCE(( SELECT format_type(a.atttypid, a.atttypmod) AS format_type
               FROM pg_attribute a
              WHERE a.attrelid = t4.identifiant AND a.attname = 'geometrie'::name), 'alpha'::text) AS type_geometrique,
        COALESCE(( SELECT
                    CASE
                        WHEN "position"(format_type(a.atttypid, a.atttypmod), 'Z'::text) > 0 THEN 3
                        ELSE 2
                    END AS dim_geom
               FROM pg_attribute a
              WHERE a.attrelid = t4.identifiant AND a.attname = 'geometrie'::name), 0) AS dimension,
        pg_stat_get_live_tuples(t4.identifiant) AS nb_enreg,
        t4.type_table,
        t4.index_geometrique,
        t4.clef_primaire,
        t4.index,
        string_agg(t4.clef_etrangere, ' '::text) AS clef_etrangere
       FROM t4
      GROUP BY t4.identifiant, t4.nomschema, t4.nomtable, t4.type_table, (obj_description(t4.identifiant, 'pg_class'::name)), (COALESCE(( SELECT format_type(a.atttypid, a.atttypmod) AS format_type
               FROM pg_attribute a
              WHERE a.attrelid = t4.identifiant AND a.attname = 'geometrie'::name), 'alpha'::text)), (COALESCE(( SELECT
                    CASE
                        WHEN "position"(format_type(a.atttypid, a.atttypmod), 'Z'::text) > 0 THEN 3
                        ELSE 2
                    END AS dim_geom
               FROM pg_attribute a
              WHERE a.attrelid = t4.identifiant AND a.attname = 'geometrie'::name), 0)), t4.index_geometrique, t4.clef_primaire, t4.index;

"""

requetes_sigli[
    "info_attributs"
] = """
 WITH t AS (
         SELECT c.oid AS identifiant,
            n.nspname AS nomschema,
            c.relname AS nomtable,
            c.relkind AS type_table,
            i.indexrelid,
            (c.oid::text || ':'::text) || COALESCE(array_to_string(i.indkey, ':'::text),
             ':'::text) AS clef,
            row_number() OVER (PARTITION BY c.oid, i.indrelid) AS num_index,
            i.indkey,
            champ.champ,
            i.indisprimary AS pk,
            i.indisunique AS uniq
           FROM pg_class c
             LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
             LEFT JOIN pg_index i ON c.oid = i.indrelid
             LEFT JOIN LATERAL unnest(i.indkey) champ(champ) ON true
          WHERE n.nspname <> 'information_schema'::name
           --AND n.nspname <> 'public'::name
           AND has_schema_privilege(n.nspname,'usage')
           AND n.nspname !~~ 'pg_%'::text
           AND (c.relkind::text = ANY (ARRAY['r'::text, 'v'::text, 'm'::text]))
        ), t2 AS (
         SELECT t.identifiant,
            t.nomschema,
            t.nomtable,
            t.type_table,
            t.indkey,
            t.num_index,
            t.champ AS num_champ,
            row_number() OVER (PARTITION BY t.clef) AS ordre_champs,
            t.pk,
            t.uniq,
            t.clef
           FROM t
        ), t3 AS (
         SELECT t2.identifiant,
            t2.nomschema,
            t2.nomtable,
            a.attname,
            a.attnum,
            a.atttypid,
            a.atttypmod,
            a.atthasdef,
            a.attnotnull,
                CASE
                    WHEN t2.num_champ <> a.attnum THEN NULL::text
                    WHEN t2.indkey IS NULL THEN NULL::text
                    WHEN a.attname = 'geometrie'::name THEN 'G:'::text
                    WHEN t2.pk THEN 'P:'::text || t2.ordre_champs
                    WHEN t2.uniq THEN (('U'::text || t2.num_index) || ':'::text) || t2.ordre_champs
                    ELSE (('I'::text || t2.num_index) || ':'::text) || t2.ordre_champs
                END AS index,
                CASE
                    WHEN t2.num_champ <> a.attnum THEN NULL::bigint
                    WHEN t2.pk THEN t2.ordre_champs
                    ELSE NULL::bigint
                END AS pk,
                CASE
                    WHEN t2.num_champ <> a.attnum THEN NULL::bigint
                    WHEN t2.uniq THEN t2.ordre_champs
                    ELSE NULL::bigint
                END AS "unique"
           FROM pg_attribute a,
            t2
          WHERE a.attrelid = t2.identifiant AND a.attnum > 0 AND NOT a.attisdropped
        ), t4 AS (
         SELECT t3.identifiant,
            t3.nomschema,
            t3.nomtable,
            t3.attname,
            t3.attnum,
            t3.atttypid,
            t3.atttypmod,
            t3.atthasdef,
            t3.attnotnull,
            string_agg(t3.index, ' '::text ORDER BY t3.index) AS index,
            string_agg(t3.pk::text, ''::text) AS pk,
            string_agg(t3."unique"::text, ''::text) AS "unique"
           FROM t3
          GROUP BY t3.identifiant, t3.nomschema, t3.nomtable, t3.attname, t3.attnum,
           t3.atttypid, t3.atttypmod, t3.atthasdef, t3.attnotnull
        )
 SELECT t4.nomschema,
    t4.nomtable,
    t4.attname AS attribut,
    col_description(t4.identifiant, t4.attnum::integer) AS alias,
        CASE
            WHEN (( SELECT pg_type.typtype
               FROM pg_type
              WHERE t4.atttypid = pg_type.oid)) = 'e'::"char" THEN 'text'::text
            WHEN ( format_type(t4.atttypid, t4.atttypmod) = 'integer'
		        AND ( select pg_get_serial_sequence(t4.nomschema||'.'||t4.nomtable,t4.attname) IS NOT Null))
		    THEN 'serial'
	        WHEN ( format_type(t4.atttypid, t4.atttypmod) = 'bigint'
		        AND ( select pg_get_serial_sequence(t4.nomschema||'.'||t4.nomtable,t4.attname) IS NOT Null))
		    THEN 'bigserial'
            ELSE format_type(t4.atttypid, t4.atttypmod)
        END AS type_attribut,
    'non'::text AS graphique,
    'non'::text AS multiple,
    ( SELECT "substring"(pg_get_expr(d.adbin, d.adrelid), 1, 128) AS "substring"
           FROM pg_attrdef d
          WHERE d.adrelid = t4.identifiant AND d.adnum = t4.attnum AND t4.atthasdef) AS defaut,
        CASE
            WHEN t4.attnotnull = false THEN 'non'::text
            ELSE 'oui'::text
        END AS obligatoire,
        CASE
            WHEN (( SELECT pg_type.typtype
               FROM pg_type
              WHERE t4.atttypid = pg_type.oid)) = 'e'::"char" THEN ( SELECT pg_type.typname
               FROM pg_type
              WHERE t4.atttypid = pg_type.oid)
            ELSE NULL::name
        END AS enum,
    COALESCE(( SELECT
                CASE
                    WHEN "position"(format_type(a.atttypid, a.atttypmod), 'Z'::text) > 0 THEN 3
                    ELSE 2
                END AS dim_geom
           FROM pg_attribute a
          WHERE a.attrelid = t4.identifiant AND a.attname = 'geometrie'::name), 0) AS dimension,
    --'fin'::text AS fin,
    t4.attnum AS num_attribut,
    t4.index,
    t4."unique" AS uniq,
    t4.pk AS clef_primaire,
    ( SELECT (n.nspname::text || '.'::text) || t.relname::text
           FROM pg_constraint c
             LEFT JOIN pg_class t ON t.oid = c.confrelid
             LEFT JOIN pg_namespace n ON t.relnamespace = n.oid
          WHERE has_schema_privilege(n.nspname,'usage') AND c.conrelid = t4.identifiant AND c.contype = 'f'::"char"
           AND (t4.attnum = ANY (c.conkey))) AS clef_etrangere,
    ( SELECT a1.attname
           FROM pg_constraint c,
            pg_attribute a1
          WHERE c.conrelid = t4.identifiant AND c.contype = 'f'::"char"
            AND (t4.attnum = ANY (c.conkey)) AND a1.attrelid = c.confrelid AND a1.attnum = c.confkey[1]) AS cible_clef,
   ( SELECT 'u'||c.confupdtype||',d'||c.confdeltype||',m'||c.confmatchtype||','|| (case when c.condeferrable then 'defer' else 'nd' end)
          FROM pg_constraint c
          WHERE c.conrelid = t4.identifiant AND c.contype = 'f'::"char" AND (t4.attnum = ANY (c.conkey))) as parametres_clef,
    0 as taille,
    0 as decimales
   FROM t4;
        """

requetes_sigli[
    "info_enums"
] = """
                SELECT pg_type.typname AS nom_enum,
                    pg_enum.enumsortorder AS ordre,
                    pg_enum.enumlabel AS valeur,
                    pg_enum.enumlabel AS alias,
                    '1'::text AS mode
                FROM pg_type,pg_enum
                WHERE pg_enum.enumtypid = pg_type.oid
                ORDER BY pg_type.typname, pg_enum.enumsortorder
                """


def cree_sigli(nomschema):
    """enregistre les requetes en base pour creer  la structure sigli"""
    sql = list()
    for i in requetes_sigli:
        sql.append("CREATE VIEW " + nomschema + "." + i + " AS " + requetes_sigli[i])

    return sql
