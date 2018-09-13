-- schema historisation
CREATE SCHEMA histo;
CREATE type public.histo_origine AS ENUM ('direct','externe','archive');
--DROP table admin_sigli.historisation;
CREATE TABLE admin_sigli.historisation
(
  id bigserial,
  nom_schema text NOT NULL, -- identifiant de la table
  nom_table text NOT NULL, -- identifiant de la table
  identifiant int, -- identifiant
  complement text, -- attribut pour la repres
  donnees hstore, -- toute l'info
  date_creation timestamp DEFAULT now(), -- debut et fin de validite
  date_fin_validite timestamp, -- debut et fin de validite
  origine histo_origine,-- mecanisme de creation
  histo_auteur text, -- auteur de l'operation
  geometrie Geometry,
  CONSTRAINT historisation_pkey PRIMARY KEY (id)
);
COMMENT ON COLUMN admin_sigli.historisation.id IS 'clef primaire automatique';
COMMENT ON COLUMN admin_sigli.historisation.nom_schema IS 'identifiant de la table';
COMMENT ON COLUMN admin_sigli.historisation.nom_table IS 'identifiant de la table';
COMMENT ON COLUMN admin_sigli.historisation.identifiant IS 'identifiant';
COMMENT ON COLUMN admin_sigli.historisation.complement IS 'attribut pour la repres';
COMMENT ON COLUMN admin_sigli.historisation.donnees IS 'toute l''info';
COMMENT ON COLUMN admin_sigli.historisation.date_creation IS 'debut et fin de validite';
COMMENT ON COLUMN admin_sigli.historisation.date_fin_validite IS 'debut et fin de validite';
COMMENT ON COLUMN admin_sigli.historisation.origine IS 'mecanisme de creation';
COMMENT ON COLUMN admin_sigli.historisation.histo_auteur IS 'auteur de l''operation';
COMMENT ON COLUMN admin_sigli.historisation.geometrie IS 'geometrie';

CREATE TABLE admin_sigli.historisation_non_geom
(
  id bigserial,
  nom_schema text NOT NULL, -- identifiant de la table
  nom_table text NOT NULL, -- identifiant de la table
  identifiant int, -- identifiant
  complement text, -- attribut pour la repres
  donnees hstore, -- toute l'info
  date_creation timestamp DEFAULT now(), -- debut et fin de validite
  date_fin_validite timestamp, -- debut et fin de validite
  origine histo_origine,-- mecanisme de creation
  histo_auteur text, -- auteur de l'operation
  CONSTRAINT historisation_pkey PRIMARY KEY (id)
);
COMMENT ON COLUMN admin_sigli.historisation_non_geom.id IS 'clef primaire automatique';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.nom_schema IS 'identifiant de la table';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.nom_table IS 'identifiant de la table';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.identifiant IS 'identifiant';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.complement IS 'attribut pour la repres';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.donnees IS 'toute l''info';
COMMENT ON COLUMN admin_sigli.historisation_non_geom.date_creation IS 'debut et fin de validite';
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
        requete = 'CREATE TABLE histo.'||quote_ident(nom)||' (LIKE admin_sigli.historisation_non_geom (INCLUDING INDEXES INCLUDING COMMENTS))';
        EXECUTE requete;
    ELSE
        requete = 'CREATE TABLE histo.'||quote_ident(nom)||' (LIKE admin_sigli.historisation (INCLUDING INDEXES INCLUDING COMMENTS))';
        EXECUTE requete;
        requete = 'ALTER TABLE histo.'||quote_ident(nom)||' ALTER COLUMN geometrie SET TYPE Geometry('||typegeom||,'3948)';
        EXECUTE requete;
    END IF;
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
	declare data hstore;
	        ligne admin_sigli.historisation%ROWTYPE;
BEGIN
	ligne.nom_table := TG_TABLE_NAME;
	ligne.nom_schema := split_part(concat_ws(',', TG_ARGV[2], TG_TABLE_SCHEMA), ',', 1)
	ligne.origine := 'trigger';
	ligne.start := now();
	ligne.operation := TG_OP
	IF TG_OP = 'DELETE' THEN
		data := hstore(OLD);
		ligne.courant := 'f';
		ligne.donnees := hstore('auteur_dest',session_user);
	ELSE
		data := hstore(NEW);
		-- on renseigle les infos complementaires pour la deco s'il y a lieu
		ligne.complement := data->TG_ARGV[1];
		ligne.geometrie := data->'geometrie';
		ligne.donnees := delete(data,'geometrie');
		ligne.courant := 't';

	END IF;
	ligne.idobjet := data->split_part(concat_ws(',',TG_ARGV[0],'gid'),',',1);

	EXECUTE format('INSERT INTO histo.%s(classe, idobjet, origine, date_creation, courant, complement, donnees ,geometrie)
			SELECT $1.classe, $1.idobjet, $1.origine, $1.date_creation, $1.courant, $1.complement, $1.donnees, $1.geometrie',
		        split_part(concat_ws(',', TG_ARGV[2], TG_TABLE_SCHEMA), ',', 1))
		 USING ligne;
	RETURN OLD;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;





-- Function: admin_sigli.stocke_histo()
-- fonction de stockage de l'historique declencheee sur origine = trigger
-- DROP FUNCTION admin_sigli.stocke_histo();

CREATE OR REPLACE FUNCTION admin_sigli.stocke_histo_tr()
  RETURNS trigger AS
$BODY$
	declare data hstore;
	        clef_histo bigint;
BEGIN
	IF NEW.courant = 't' THEN
--		EXECUTE format('SELECT clef FROM %s WHERE classe=$1.classe AND idobjet=$1.idobjet and courant =''t'' ', TG_RELID::regclass )
--		INTO clef_histo USING NEW;
		EXECUTE format('UPDATE %s SET date_fin_validite = $1.date_creation, courant = ''f''
		                WHERE clef = (SELECT clef FROM %s WHERE classe=$1.classe AND idobjet=$1.idobjet and courant =''t'')',
		               TG_RELID::regclass, TG_RELID::regclass) USING NEW;
		RETURN NEW;
	END IF;
	EXECUTE format('SELECT clef,donnees FROM %s WHERE classe=$1.classe AND idobjet=$1.idobjet and courant =''t'' ',
	               TG_RELID::regclass ) INTO clef_histo,data USING NEW;
	               data := data || NEW.donnees;
	EXECUTE format('UPDATE %s SET date_fin_validite = $2.date_creation, courant = ''f'', donnees = $3 WHERE clef = $1', TG_RELID::regclass)
		        USING clef_histo,NEW,data;
	RETURN Null;
END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
