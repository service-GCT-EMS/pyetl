WITH info_fk AS
 (SELECT c.confrelid::regclass AS cible,
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
   FROM pg_constraint c
	 LEFT JOIN pg_constraint p ON c.conrelid = p.conrelid AND p.contype = 'p'::"char"
	 LEFT JOIN pg_constraint p2 ON c.confrelid = p2.conrelid AND p2.contype = 'p'::"char"
  WHERE c.contype = 'f'::"char"),

t AS (
	 SELECT c.oid AS identifiant,
		n.nspname AS nomschema,
		c.relname AS nomtable,
		c.relkind AS type_table,
		i.indrelid,
		(i.indrelid::text || ':'::text) || array_to_string(i.indkey, ':'::text) AS clef,
		row_number() OVER (PARTITION BY i.indrelid) AS num_index,
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
		  AND n.nspname !~~ 'pg_%'::text
		  AND (c.relkind::text = ANY (ARRAY['r'::text, 'v'::text, 'm'::text]))),
	t2 AS (
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
		 LEFT JOIN pg_attribute pa ON t.identifiant = pa.attrelid AND pa.attnum = t.champ),
	t3 AS (
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
				WHEN t2.uniq
					THEN 'U:'::text || string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs)
				WHEN (string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs)
					IN ( SELECT info_fk.attribut_lien::text AS attribut_lien
						FROM info_fk
						WHERE t2.identifiant = info_fk.fk::oid))
					THEN 'K:'::text || string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs)
				WHEN string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs) <> 'geometrie'::text
					THEN 'X:'::text || string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs)
				ELSE NULL::text
			END AS def_index,
			CASE
				WHEN string_agg(t2.nom_champ::text, ','::text ORDER BY t2.ordre_champs) = 'geometrie'::text
					THEN 'geometrie'::text
				ELSE NULL::text
			END AS index_geometrique
	   FROM t2
	   GROUP BY t2.identifiant, t2.clef, t2.nomschema, t2.nomtable, t2.type_table, t2.pk, t2.uniq),
	t4 AS (
	 SELECT t3.identifiant,
		t3.nomschema,
		t3.nomtable,
		t3.type_table,
		string_agg(t3.index_geometrique, ''::text) AS index_geometrique,
		string_agg(t3.clef_primaire, ''::text) AS clef_primaire,
		string_agg(t3.def_index, ' '::text ORDER BY t3.def_index DESC) AS def_index,
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
t4.def_index,
string_agg(t4.clef_etrangere, ' '::text) AS clef_etrangere
FROM t4
GROUP BY t4.identifiant, t4.nomschema, t4.nomtable, t4.type_table, obj_description(t4.identifiant, 'pg_class'::name),
	 COALESCE(( SELECT format_type(a.atttypid, a.atttypmod) AS format_type
		   FROM pg_attribute a
	 WHERE a.attrelid = t4.identifiant AND a.attname = 'geometrie'::name), 'alpha'::text), COALESCE(( SELECT
			CASE
				WHEN "position"(format_type(a.atttypid, a.atttypmod), 'Z'::text) > 0 THEN 3
				ELSE 2
			END AS dim_geom
	   FROM pg_attribute a
	 WHERE a.attrelid = t4.identifiant AND a.attname = 'geometrie'::name), 0), t4.index_geometrique, t4.clef_primaire, t4.def_index