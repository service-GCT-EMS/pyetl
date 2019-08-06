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
CREATE INDEX historisation_gist
  ON admin_sigli.historisation
  USING gist (geometrie);

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


-- creation d'une table dans le schema histor
-- DROP FUNCTION admin_sigli.cretable_histo(text,text);

CREATE OR REPLACE FUNCTION admin_sigli.histo_cretable(nom text, type_geom text)
    RETURNS void AS
$BODY$
DECLARE requete text;
BEGIN

    if type_geom = 'ALPHA' OR type_geom='' THEN
        requete = 'CREATE TABLE IF NOT EXISTS histo.'||quote_ident(nom)||' (LIKE admin_sigli.historisation_non_geom INCLUDING ALL)';
        EXECUTE requete;
    ELSE
        requete = 'CREATE TABLE IF NOT EXISTS histo.'||quote_ident(nom)||' (LIKE admin_sigli.historisation INCLUDING ALL)';
        EXECUTE requete;
        requete = 'ALTER TABLE histo.'||quote_ident(nom)||' ALTER COLUMN geometrie TYPE Geometry('||type_geom||',3948)';
        -- raise notice '%s', requete;
        EXECUTE requete;
    END IF;
    requete = 'CREATE TRIGGER hi_stocke_histo BEFORE INSERT ON histo.'||quote_ident(nom)||' FOR EACH ROW EXECUTE PROCEDURE admin_sigli.stocke_histo_tr()';
      EXECUTE requete;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1000;

-- historisation d'une table
-- DROP FUNCTION admin_sigli.historise(text,text,text)
CREATE OR REPLACE FUNCTION admin_sigli.historise(nom text, complement text default Null, histo text default Null, ident text default Null, exc text default Null)
  RETURNS void AS
$BODY$
DECLARE requete text;
BEGIN

  EXECUTE format('CREATE TRIGGER histo_cre BEFORE UPDATE OR INSERT ON %I.%I FOR EACH ROW EXECUTE PROCEDURE admin_sigli.histor(%L,%L,%L)',
            split_part(nom,'.',1),split_part(nom,'.',2),complement,histo,ident);
  EXECUTE format('CREATE TRIGGER histo_del BEFORE DELETE ON %I.%I FOR EACH ROW EXECUTE PROCEDURE admin_sigli.histor_del(%L,%L)',
            split_part(nom,'.',1),split_part(nom,'.',2),histo,ident);
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1000;

-- arret historisation d'une table
-- DROP FUNCTION admin_sigli.set_histor(text,text,text)
CREATE OR REPLACE FUNCTION admin_sigli.stop_histo(nom text)
  RETURNS void AS
$BODY$
DECLARE requete text;
BEGIN
  EXECUTE format('DROP TRIGGER histo_cre ON %I.%I',split_part(nom,'.',1),split_part(nom,'.',2));
  EXECUTE format('DROP TRIGGER histo_del ON %I.%I',split_part(nom,'.',1),split_part(nom,'.',2));
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 1000;

-- Function: admin_sigli.histor()
-- arguments : id, complement, schema
-- DROP FUNCTION admin_sigli.histor();

CREATE OR REPLACE FUNCTION admin_sigli.histor()
  RETURNS trigger AS
$BODY$
	declare donnees hstore;
BEGIN
  donnees := hstore(NEW)-'geometrie'::text;
  -- on renseigle les infos complementaires pour la deco s'il y a lieu
	EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees , geometrie)
                        VALUES(%L, %L, %L, %L,%L, %L)', COALESCE(TG_ARGV[1], TG_TABLE_SCHEMA),
                            TG_TABLE_NAME,TG_TABLE_SCHEMA,donnees->COALESCE(TG_ARGV[2],'gid'),
                            donnees->TG_ARGV[0],donnees,NEW.geometrie);
	RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;

CREATE OR REPLACE FUNCTION admin_sigli.histor_ng()
  RETURNS trigger AS
$BODY$
	declare donnees hstore;
BEGIN
  donnees := hstore(NEW);
  -- on renseigle les infos complementaires pour la deco s'il y a lieu
	EXECUTE format('INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees )
                      VALUES( %L, %L, %L,%L, %L)', COALESCE(TG_ARGV[2], TG_TABLE_SCHEMA),
                          TG_TABLE_NAME,TG_TABLE_SCHEMA,donnees->COALESCE(TG_ARGV[2],'gid'),
                          donnees->TG_ARGV[0],donnees);
	RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;

-- Function: admin_sigli.histor()
-- arguments : id, complement, schema
-- DROP FUNCTION admin_sigli.histor();

CREATE OR REPLACE FUNCTION admin_sigli.histor_del()
  RETURNS trigger AS
$BODY$
  declare clef_histo bigint;
BEGIN
  -- on renseigle les infos complementaires pour la deco s'il y a lieu
  EXECUTE format('SELECT clef FROM  histo.%I WHERE nom_table=%L AND identifiant=OLD.%I and courant =''t'' ',
	               COALESCE(TG_ARGV[0], TG_TABLE_SCHEMA),TG_TABLE_NAME,COALESCE(TG_ARGV[1],'gid') ) INTO clef_histo;
	EXECUTE format('UPDATE histo.%I SET date_fin_validite = now(), courant = ''f'' WHERE clef = %L', COALESCE(TG_ARGV[0], TG_TABLE_SCHEMA),clef_histo);
	RETURN OLD;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;


-- Function: admin_sigli.stocke_histo_tr()
-- trigger sur classe historique declenche par trigger

CREATE OR REPLACE FUNCTION admin_sigli.stocke_histo_tr()
  RETURNS trigger AS
$BODY$
  BEGIN
    EXECUTE format('UPDATE %s SET date_fin_validite = %L, courant = ''f''
                         WHERE nom_table=%L AND identifiant=%L and courant =''t'' ', TG_RELID::regclass,NEW.date_debut_validite,NEW.nom_table,NEW.identifiant );
	RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
