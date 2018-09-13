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
			CASE
				WHEN i.indkey IS NULL THEN NULL::smallint
				ELSE unnest(i.indkey)
			END AS champ,
		i.indisprimary AS pk,
		i.indisunique AS uniq
	   FROM pg_class c
		 LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
		 LEFT JOIN pg_index i ON c.oid = i.indrelid
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
			END AS def_index,
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
		string_agg(t3.def_index, ' '::text ORDER BY t3.def_index) AS def_index,
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
t4.def_index,
t4."unique" AS uniq,
t4.pk AS clef_primaire,
( SELECT (n.nspname::text || '.'::text) || t.relname::text
	   FROM pg_constraint c
		 LEFT JOIN pg_class t ON t.oid = c.confrelid
		 LEFT JOIN pg_namespace n ON t.relnamespace = n.oid
	  WHERE c.conrelid = t4.identifiant AND c.contype = 'f'::"char"
			  AND (t4.attnum = ANY (c.conkey))) AS clef_etrangere,
( SELECT a1.attname
	   FROM pg_constraint c,
		pg_attribute a1
	  WHERE c.conrelid = t4.identifiant AND c.contype = 'f'::"char"
			  AND (t4.attnum = ANY (c.conkey)) AND a1.attrelid = c.confrelid AND a1.attnum = c.confkey[1]) AS cible_clef,
0 as taille,
0 as decimales
FROM t4;