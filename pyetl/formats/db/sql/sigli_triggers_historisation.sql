-- schema historisation
CREATE SCHEMA histo;
CREATE TYPE histo.histo_origine AS ENUM ('direct','externe','archive');
DROP table admin_sigli.historisation;
CREATE TABLE IF NOT EXISTS  admin_sigli.historisation
(
  clef bigserial,
  nom_schema text NOT NULL, -- identifiant de la table
  nom_table text NOT NULL, -- identifiant de la table
  identifiant text, -- identifiant
  complement text, -- attribut pour la repres
  donnees hstore, -- toute l'info
  date_debut_validite timestamp DEFAULT now(), -- debut et fin de validite
  date_fin_validite timestamp, -- debut et fin de validite
  courant boolean DEFAULT 't',
  origine histo.histo_origine DEFAULT 'direct'::histo.histo_origine,-- mecanisme de creation
  histo_auteur text DEFAULT session_user, -- auteur de l'operation
  geometrie Geometry,
  CONSTRAINT historisation_pkey PRIMARY KEY (clef)
);
CREATE INDEX historisation_gist
  ON admin_sigli.historisation
  USING gist (geometrie);

Create index historisation_identifiant
  ON admin_sigli.historisation
  USING btree(identifiant);

Create index historisation_date_debut_validite
  ON admin_sigli.historisation
  USING btree(date_debut_validite);

Create index historisation_date_fin_validite
  ON admin_sigli.historisation
  USING btree(date_fin_validite);

COMMENT ON COLUMN admin_sigli.historisation.clef IS 'clef primaire automatique';
COMMENT ON COLUMN admin_sigli.historisation.nom_schema IS 'identifiant de la table';
COMMENT ON COLUMN admin_sigli.historisation.nom_table IS 'identifiant de la table';
COMMENT ON COLUMN admin_sigli.historisation.identifiant IS 'identifiant';
COMMENT ON COLUMN admin_sigli.historisation.complement IS 'attribut pour la repres';
COMMENT ON COLUMN admin_sigli.historisation.donnees IS 'toute l''info';
COMMENT ON COLUMN admin_sigli.historisation.date_debut_validite IS 'debut et fin de validite';
COMMENT ON COLUMN admin_sigli.historisation.date_fin_validite IS 'debut et fin de validite';
COMMENT ON COLUMN admin_sigli.historisation.origine IS 'mecanisme de creation';
COMMENT ON COLUMN admin_sigli.historisation.histo_auteur IS 'auteur de l''operation';
COMMENT ON COLUMN admin_sigli.historisation.geometrie IS 'geometrie';


DROP table admin_sigli.historisation_non_geom;

CREATE TABLE IF NOT EXISTS  admin_sigli.historisation_non_geom
(
  clef bigserial,
  nom_schema text NOT NULL, -- identifiant de la table
  nom_table text NOT NULL, -- identifiant de la table
  identifiant text, -- identifiant
  complement text, -- attribut pour la repres
  donnees hstore, -- toute l'info
  date_debut_validite timestamp DEFAULT now(), -- debut et fin de validite
  date_fin_validite timestamp, -- debut et fin de validite
  courant boolean DEFAULT 't',
  origine histo.histo_origine DEFAULT 'direct'::histo.histo_origine,-- mecanisme de creation
  histo_auteur text DEFAULT session_user, -- auteur de l'operation
  CONSTRAINT historisation_ng_pkey PRIMARY KEY (clef)
);
Create index historisation_non_geom_identifiant
  ON admin_sigli.historisation_non_geom
  USING btree(identifiant);

Create index historisation_non_geom_date_debut_validite
  ON admin_sigli.historisation_non_geom
  USING btree(date_debut_validite);

Create index historisation_non_geom_date_fin_validite
  ON admin_sigli.historisation_non_geom
  USING btree(date_fin_validite);

COMMENT ON COLUMN admin_sigli.historisation_non_geom.clef IS 'clef primaire automatique';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.nom_schema IS 'identifiant de la table';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.nom_table IS 'identifiant de la table';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.identifiant IS 'identifiant';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.complement IS 'attribut pour la repres';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.donnees IS 'toute l''info';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.date_debut_validite IS 'debut et fin de validite';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.date_fin_validite IS 'debut et fin de validite';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.origine IS 'mecanisme de creation';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.histo_auteur IS 'auteur de l''operation';


CREATE TABLE IF NOT EXISTS admin_sigli.codes_geom
(
	type_geometrique text,
	code text,
	type_histo text,
	CONSTRAINT codes_geom_pkey PRIMARY KEY (type_geometrique)
)
WITH (OIDS=FALSE);
-- ###### creation des indexes #######
-- ###### definition des commentaires ####
COMMENT ON COLUMN admin_sigli.codes_geom.type_histo IS 'type utilise pour la table historique';

copy "admin_sigli"."codes_geom" (type_geometrique, code, type_histo) FROM stdin;
alpha	a	alpha
geometry	\N	geometry
geometry(Geometry,3948)	\N	geometry
geometry(LineString,3948)	l	geometry(MultiLineString,3948)
geometry(MultiLineString,3948)	l	geometry(MultiLineString,3948)
geometry(Point,3948)	p	geometry(Point,3948)
geometry(MultiPolygon,3948)	s	geometry(MultiPolygon,3948)
geometry(Polygon,3948)	s	geometry(MultiPolygon,3948)
\.

-- creation d'une table dans le schema histor
-- DROP FUNCTION admin_sigli.creTG_ARGV[1](text,text);

CREATE OR REPLACE FUNCTION admin_sigli.histo_cretable(nom text, type_geom text)
    RETURNS void AS
$BODY$
DECLARE requete text;
BEGIN
    raise notice 'creation table % %', nom, type_geom;

    if type_geom = 'alpha' OR type_geom='' THEN
        requete = 'CREATE TABLE IF NOT EXISTS histo.'||quote_ident(nom)||' (LIKE admin_sigli.historisation_non_geom INCLUDING ALL)';
        EXECUTE requete;
    ELSE
        requete = 'CREATE TABLE IF NOT EXISTS histo.'||quote_ident(nom)||' (LIKE admin_sigli.historisation INCLUDING ALL)';
        EXECUTE requete;
        requete = 'ALTER TABLE histo.'||quote_ident(nom)||' ALTER COLUMN geometrie TYPE '||type_geom;
        raise notice 'adaptation geom: %', requete;
        EXECUTE requete;
    END IF;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1000;

-- historisation d'une table
-- DROP FUNCTION admin_sigli.historise(text,text,text,text[])
CREATE OR REPLACE FUNCTION admin_sigli.historise(nom text, complement text default Null, histo text default Null,  exc text[] default Array[''])
  RETURNS void AS
$BODY$
DECLARE nom_table text; nom_schema text;
        type_histo text; suffix text; ident text;
        nom_histo text; tmp oid;
BEGIN
  nom_table = split_part(nom,'.',2);
  nom_schema = split_part(nom,'.',1);
  raise notice 'cherche table % % %', nom, nom_schema, nom_table;

  SELECT code, c.type_histo, clef_primaire
        FROM admin_sigli.info_tables t,admin_sigli.codes_geom c
        WHERE t.nomschema=nom_schema AND t.nomtable=nom_table and c.type_geometrique = t.type_geometrique
        INTO suffix, type_histo, ident;
  raise notice 'trouve table % % %', suffix, type_histo, ident;
  nom_histo = 'hi_'||COALESCE(histo, nom_schema)||'_'||suffix;
  SELECT oid FROM admin_sigli.info_tables WHERE nomschema='histo' AND nomtable=nom_histo into tmp;
  IF tmp is NULL THEN-- il faut creer la table
    raise notice 'appel creation table % %', nom_histo, type_histo;
    PERFORM admin_sigli.histo_cretable(nom_histo, type_histo);
  END IF;
  if exc <> Array[''] THEN -- s'il y a des exclusions on ne traque plus auteur et date_maj
    exc = exc || array['auteur'::text,'date_maj'::text];
  END IF;
  EXECUTE format('DROP TRIGGER IF EXISTS z_histo ON %I.%I',nom_schema,nom_table);
  if suffix = 'a' THEN
  EXECUTE format('CREATE TRIGGER z_histo BEFORE UPDATE OR INSERT OR DELETE ON %I.%I FOR EACH ROW EXECUTE PROCEDURE admin_sigli.histor_ng(%L,%L,%L,%L)',
            nom_schema,nom_table,complement,nom_histo,ident,exc);
  ELSE
  EXECUTE format('CREATE TRIGGER z_histo BEFORE UPDATE OR INSERT OR DELETE ON %I.%I FOR EACH ROW EXECUTE PROCEDURE admin_sigli.histor(%L,%L,%L,%L)',
            nom_schema,nom_table,complement,nom_histo,ident,exc);
  END IF;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1000;

-- arret historisation d'une table
-- DROP FUNCTION admin_sigli.stop_histo(text)
CREATE OR REPLACE FUNCTION admin_sigli.stop_histo(nom text)
  RETURNS void AS
$BODY$
DECLARE requete text;
BEGIN
  EXECUTE format('DROP TRIGGER z_histo ON %I.%I',split_part(nom,'.',1),split_part(nom,'.',2));
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1000;

-- Function: admin_sigli.histor()
-- arguments : id, complement, destination, exclusions
-- DROP FUNCTION admin_sigli.histor();

CREATE OR REPLACE FUNCTION admin_sigli.histor()
  RETURNS trigger AS
$BODY$
	declare nouveau hstore; ancien hstore;
          cmp_n hstore; cmp_a hstore;
          clef_histo bigint;
BEGIN

  IF TG_OP = 'INSERT' THEN
    nouveau := hstore(NEW)-'geometrie'::text;
    EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees , geometrie)
                    VALUES(%L, %L, %L, %L,%L, %L)',
                    TG_ARGV[1],TG_TABLE_NAME,TG_TABLE_SCHEMA,nouveau->TG_ARGV[2],nouveau->TG_ARGV[0],nouveau,NEW.geometrie);
    RETURN NEW;
  END IF;
  ancien :=hstore(OLD);
  cmp_a = ancien-TG_ARGV[3]::text[];
  EXECUTE format('SELECT clef FROM  histo.%I WHERE nom_table=%L AND identifiant=%L and courant =''t'' ',
                  TG_ARGV[1],TG_TABLE_NAME,ancien->TG_ARGV[2]) INTO clef_histo;

  IF clef_histo IS Null THEN -- l'historique n'existe pas on enregistre
    IF TG_OP = 'DELETE' THEN
      ancien = ancien-'geometrie'::text;
      EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees , geometrie, courant, date_debut_validite, date_fin_validite)
                      VALUES(%L, %L, %L, %L,%L, %L,%L,%L,%L)',
                      TG_ARGV[1], TG_TABLE_NAME,TG_TABLE_SCHEMA,ancien->TG_ARGV[2], ancien->TG_ARGV[0],ancien,OLD.geometrie,'f',Null,now());
      RETURN OLD;
    END IF;
    nouveau := hstore(NEW);
    cmp_n := nouveau-TG_ARGV[3]::text[];
    IF cmp_a = cmp_n THEN
      return NEW; -- rien a faire
    END IF;
    nouveau = nouveau-'geometrie'::text;
    EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees , geometrie, courant, date_debut_validite,date_fin_validite)
                    VALUES(%L, %L, %L, %L,%L, %L,%L,%L,%L)',
                    TG_ARGV[1], TG_TABLE_NAME,TG_TABLE_SCHEMA,ancien->TG_ARGV[2],ancien->TG_ARGV[0],ancien,OLD.geometrie,'f',Null, now());
  END IF;
  EXECUTE format('UPDATE histo.%I SET date_fin_validite = now(), courant = ''f'' WHERE clef = %L', TG_ARGV[1],clef_histo);
  IF TG_OP = 'DELETE' THEN
    RETURN OLD;
  ELSE
    nouveau := hstore(NEW);
    cmp_n := nouveau-TG_ARGV[3]::text[];
    IF cmp_a = cmp_n THEN
      return NEW; -- rien a faire
    END IF;
    EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees , geometrie)
                    VALUES(%L, %L, %L, %L,%L, %L)',
                    TG_ARGV[1], TG_TABLE_NAME, TG_TABLE_SCHEMA, nouveau->TG_ARGV[2], nouveau->TG_ARGV[0], nouveau, NEW.geometrie);
    RETURN NEW;
  END IF;


END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
---------------------------- trigger non geometrique
-- Function: admin_sigli.histor_ng()
-- arguments : id, complement, destination, exclusions
-- DROP FUNCTION admin_sigli.histor_ng();

CREATE OR REPLACE FUNCTION admin_sigli.histor_ng()
  RETURNS trigger AS
$BODY$
	declare nouveau hstore; ancien hstore;
          cmp_n hstore; cmp_a hstore;
          clef_histo bigint;
BEGIN

  IF TG_OP = 'INSERT' THEN
    nouveau := nouveau-'geometrie'::text;
    EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees)
                    VALUES(%L, %L, %L, %L,%L)',
                    TG_ARGV[1],TG_TABLE_NAME,TG_TABLE_SCHEMA,nouveau->TG_ARGV[2],nouveau->TG_ARGV[0],nouveau);
    RETURN NEW;
  END IF;
  ancien :=hstore(OLD);
  cmp_a = ancien-TG_ARGV[3]::text[];
  EXECUTE format('SELECT clef FROM  histo.%I WHERE nom_table=%L AND identifiant=%L and courant =''t'' ',
                  TG_ARGV[1],TG_TABLE_NAME,ancien->TG_ARGV[2]) INTO clef_histo;
  IF clef_histo IS Null THEN -- l'historique n'existe pas on enregistre
    IF TG_OP = 'DELETE' THEN
      EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees , courant, date_debut_validite, date_fin_validite)
                      VALUES(%L, %L, %L, %L,%L, %L,%L,%L)',
                      TG_ARGV[1], TG_TABLE_NAME,TG_TABLE_SCHEMA,ancien->TG_ARGV[2], ancien->TG_ARGV[0],ancien,'f',Null,now());
      RETURN OLD;
    END IF;
    nouveau := hstore(NEW);
    cmp_n := nouveau-TG_ARGV[3]::text[];
    IF cmp_a = cmp_n THEN
      return NEW; -- rien a faire
    END IF;
    EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees , courant, date_debut_validite,date_fin_validite)
                    VALUES(%L, %L, %L, %L,%L, %L,%L,%L)',
                    TG_ARGV[1], TG_TABLE_NAME,TG_TABLE_SCHEMA,ancien->TG_ARGV[2],ancien->TG_ARGV[0],ancien,'f',Null, now());
  ELSE
    EXECUTE format('UPDATE histo.%I SET date_fin_validite = now(), courant = ''f'' WHERE clef = %L', TG_ARGV[1],clef_histo);
    IF TG_OP = 'DELETE' THEN
      RETURN OLD;
    ELSE
      EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees)
                  VALUES(%L, %L, %L, %L,%L)',
                  TG_ARGV[1], TG_TABLE_NAME, TG_TABLE_SCHEMA, nouveau->TG_ARGV[2], nouveau->TG_ARGV[0], nouveau );
	    RETURN NEW;
    END IF;
  END IF;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
