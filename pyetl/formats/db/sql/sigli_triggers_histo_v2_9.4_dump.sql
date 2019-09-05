--
-- PostgreSQL database dump

SET client_encoding = 'UTF8';
SELECT pg_catalog.set_config('search_path', '', false);

--
-- TOC entry 9 (class 2615 OID 18104)
-- Name: histo; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA histo;


CREATE FUNCTION histo.histor_groupe() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
-- gestion de l'historique pour des dumps complets en provenance d'elyx --
DECLARE
	nom_complement name;
	nom_groupe name;
	p_id bigint;
	p_fin_val timestamp;
	p_contenu hstore;
	p_geom geometry;
	s_id bigint;
	s_deb_val timestamp;
	s_contenu hstore;
	s_geom geometry;
	historec record;
	liste_exclusions name[];
	val_complement text;

BEGIN
-- on mets les geometries a niveau
	NEW.geometrie = ST_Multi(ST_forceCurve(New.geometrie)); -- on mets les geometries a niveau
-- recuperation de la config
	SELECT groupe, complement, exclusions into nom_groupe,nom_complement,liste_exclusions
		from histo.config_histo where classe=NEW.classe and nom_schema=NEW.nom_schema;
	IF NOT FOUND THEN -- config par defaut
		nom_groupe = NEW.nom_schema;
	END IF;
-- extraction de l'information de repres
	val_complement = (NEW.contenu->nom_complement)::text;
-- la on s'interesse a ce qui existe dans la base
	SELECT hgid, fin_validite, contenu, geometrie from histo.historique INTO p_id, p_fin_val, p_contenu, p_geom
		WHERE groupe=nom_groupe AND nom_schema=NEW.nom_schema AND classe=NEW.classe AND gid=NEW.gid AND fin_validite < NEW.debut_validite
		ORDER BY debut_validite DESC LIMIT 1; -- on cherche le dernier avant

	SELECT hgid, debut_validite, contenu, geometrie from histo.historique INTO s_id, s_deb_val, s_contenu, s_geom
		WHERE groupe=nom_groupe AND nom_schema=NEW.nom_schema AND classe=NEW.classe AND gid=NEW.gid AND debut_validite > NEW.debut_validite
		ORDER BY debut_validite ASC LIMIT 1; -- on cherche le premier apres

	IF p_id IS NULL THEN --il n'y a pas de precedent
		IF s_id IS NULL THEN -- il n'y a pas de suivant : on est tout seul on l'insere avec une dureee de vie de 1 jour
			INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
			values (nom_groupe, NEW.nom_schema, NEW.classe, NEW.gid, val_complement, NEW.contenu, NEW.debut_validite, NEW.debut_validite+'1 day'::interval, NEW.geometrie);
			RETURN NEW;
		ELSE -- il y a un suivant
			IF NEW.contenu - liste_exclusions = s_contenu - liste_exclusions and NEW.geometrie = s_geom THEN -- c'est le meme : on etend sa vie
				UPDATE histo.historique SET debut_validite = NEW.debut_validite WHERE hgid=s_hgid;
				RETURN NULL;
			ELSE -- c'est pas le meme on l'insere et il est valide jusqu'au suivant
				INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
				values (nom_groupe, NEW.nom_schema, NEW.classe, NEW.gid, val_complement, NEW.contenu, NEW.debut_validite, s_deb_val, NEW.geometrie);
				RETURN NEW;
			END IF;
		END IF;
	ELSE -- il y a un precedent
		IF NEW.contenu - liste_exclusions = p_contenu - liste_exclusions and NEW.geometrie = p_geom THEN -- c'est le meme : on etend eventuellement sa vie
			IF p_fin_val > NEW.debut_validite THEN -- rien a faire
				RETURN NULL;
			ELSE -- on ajuste les durees de vie
				UPDATE histo.historique SET fin_validite = NEW.debut_validite+'1 day'::interval WHERE hgid=p_hgid;
				IF s_id THEN -- il y a un suivant on le mets a jour normalement ca devrait pas arriver ...
					UPDATE histo.historique SET debut_validite = NEW.debut_validite+'1 day'::interval WHERE hgid=s_hgid;
				END IF;
				RETURN NULL;
			END IF;
		ELSE -- le nouveau est different du precedent
			UPDATE histo.historique SET fin_validite = NEW.debut_validite WHERE hgid=p_hgid; -- on ajuste la duree de vie du precedent
			IF s_id IS NULL THEN
				-- il n'y a pas de suivant : on l'insere avec une duree de vie de 1 jour
				INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
				values (nom_groupe, NEW.nom_schema, NEW.classe, NEW.gid, val_complement, NEW.contenu, NEW.debut_validite, NEW.debut_validite+'1 day'::interval, NEW.geometrie);
			ELSE -- il y a un suivant
				UPDATE histo.historique SET debut_validite = NEW.debut_validite WHERE hgid=s_hgid; -- on ajuste sa vie
				IF NEW.contenu - liste_exclusions = s_contenu - liste_exclusions and NEW.geometrie = s_geom THEN -- c'est le meme : rien a faire
					RETURN NULL;
				ELSE -- c'est pas le meme on l'insere et il est valide jusqu'au suivant
					INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
					values (nom_groupe, NEW.nom_schema, NEW.classe, NEW.gid, val_complement, NEW.contenu, NEW.debut_validite, s_deb_val, NEW.geometrie);
					RETURN NEW;
				END IF;
			END IF;
		END IF;
	END IF;
END;

$$;


CREATE FUNCTION histo.histor_groupe2() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
-- gestion de l'historique pour des dumps complets en provenance d'elyx --
DECLARE
	nom_complement name;
	nom_groupe name;
	p_id bigint;
	p_fin_val timestamp;
	p_contenu hstore;
	p_geom geometry;

	liste_exclusions name[];

BEGIN
-- on mets les geometries a niveau
	NEW.geometrie = ST_Multi(ST_forceCurve(New.geometrie)); -- on mets les geometries a niveau
-- recuperation de la config
	SELECT groupe, complement, exclusions into nom_groupe,nom_complement,liste_exclusions
		from histo.config_histo where classe=NEW.classe and nom_schema=NEW.nom_schema;
	IF NOT FOUND THEN -- config par defaut
		nom_groupe = NEW.nom_schema;
	END IF;
	NEW.groupe = nom_groupe;
-- extraction de l'information de repres
	NEW.complement = (NEW.contenu->nom_complement)::text;
-- la on s'interesse a ce qui existe dans la base
	SELECT hgid, fin_validite, contenu, geometrie from histo.historique INTO p_id, p_fin_val, p_contenu, p_geom
		WHERE groupe=nom_groupe AND nom_schema=NEW.nom_schema AND classe=NEW.classe AND gid=NEW.gid AND fin_validite < NEW.debut_validite
		ORDER BY debut_validite DESC LIMIT 1; -- on cherche le dernier avant

	IF NOT FOUND THEN --il n'y a pas de precedent
		RETURN  histo.histor_traite_suivant(NEW, liste_exclusions);
	ELSE -- il y a un precedent
		IF NEW.contenu - liste_exclusions = p_contenu - liste_exclusions and NEW.geometrie = p_geom THEN -- c'est le meme : on etend eventuellement sa vie
			IF p_fin_val > NEW.debut_validite THEN -- rien a faire
				RETURN NULL;
			ELSE -- on ajuste les durees de vie
				UPDATE histo.historique SET fin_validite = NEW.debut_validite+'1 day'::interval WHERE hgid=p_hgid;
				IF s_id THEN -- il y a un suivant on le mets a jour normalement ca devrait pas arriver ...
					UPDATE histo.historique SET debut_validite = NEW.debut_validite+'1 day'::interval WHERE hgid=s_hgid;
				END IF;
				RETURN NULL;
			END IF;
		ELSE -- le nouveau est different du precedent
			UPDATE histo.historique SET fin_validite = NEW.debut_validite WHERE hgid=p_hgid; -- on ajuste la duree de vie du precedent
			RETURN  histo.histor_traite_suivant(NEW, liste_exclusions);
		END IF;
	END IF;
END;

$$;



--

CREATE FUNCTION histo.histor_groupe_opt() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
-- gestion de l'historique pour des dumps complets en provenance d'elyx --
DECLARE
	nom_complement name;
	nom_groupe name;
	h_hgid bigint;
	h_fin_val timestamp;
	h_contenu hstore;
	historec record;
	liste_exclusions name[];
	val_complement text;

BEGIN
-- on mets les geometries a niveau
	NEW.geometrie = ST_Multi(ST_forceCurve(New.geometrie)); -- on mets les geometries a niveau
-- recuperation de la config
	SELECT groupe, complement, exclusions into nom_groupe,nom_complement,liste_exclusions
		from histo.config_histo where classe=NEW.classe and nom_schema=NEW.nom_schema;
	IF NOT FOUND THEN -- config par defaut
		nom_groupe = NEW.nom_schema;
	END IF;
-- extraction de l'information de repres
	val_complement = (NEW.contenu->nom_complement)::text;
-- la on s'interesse a ce qui existe dans la base
	SELECT hgid, fin_validite, contenu from histo.historique INTO h_hgid, h_fin_val, h_contenu
		WHERE groupe=nom_groupe AND nom_schema=NEW.nom_schema AND classe=NEW.classe AND gid=NEW.gid AND fin_validite > NEW.debut_validite
		ORDER BY debut_validite LIMIT 1;
	IF NOT FOUND THEN
		INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
			values (nom_groupe, NEW.nom_schema, NEW.classe, NEW.gid, val_complement, NEW.contenu, NEW.debut_validite, NEW.debut_validite+'1 day'::interval, NEW.geometrie);
		RETURN NEW;
	END IF;
		-- on enleve les champs qui ne servent pas --
	IF NEW.contenu - liste_exclusions = h_contenu - liste_exclusions THEN
		RETURN NULL;
	END IF;
	NEW.fin_validite = h_fin_val;
	UPDATE histo.historique SET fin_validite=NEW.debut_validite WHERE hgid=h_hgid;
	INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
			values (nom_groupe, NEW.nom_schema, NEW.classe, NEW.gid, val_complement, NEW.contenu, NEW.debut_validite,
					h_fin_val, NEW.geometrie) ;
	RETURN NEW;


END;

$$;



CREATE FUNCTION histo.histor_traite_suivant(nouveau record) RETURNS void
    LANGUAGE plpgsql
    AS $$
-- gestion de l'historique enregistrements suivants --
DECLARE
	nouveau record;
	s_id bigint;
	s_deb_val timestamp;
	s_contenu hstore;
	s_geom geometry;

BEGIN
	SELECT hgid, debut_validite, contenu, geometrie from histo.historique INTO s_id, s_deb_val, s_contenu, s_geom
		WHERE groupe=nouveau.groupe AND nom_schema=nouveau.nom_schema AND classe=nouveau.classe AND gid=nouveau.gid AND debut_validite > nouveau.debut_validite
		ORDER BY debut_validite ASC LIMIT 1; -- on cherche le premier apres
	IF NOT FOUND THEN -- il n'y a pas de suivant : on est tout seul on l'insere avec une duree de vie de 1 jour
		INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
		values (nouveau.groupe, nouveau.nom_schema, nouveau.classe, nouveau.gid, val_complement, nouveau.contenu, nouveau.debut_validite,
				nouveau.debut_validite+'1 day'::interval, nouveau.geometrie);
		RETURN;
	ELSE -- il y a un suivant
		IF NEW.contenu - liste_exclusions = s_contenu - liste_exclusions and nouveau.geometrie = s_geom THEN -- c'est le meme : on etend sa vie
			UPDATE histo.historique SET debut_validite = nouveau.debut_validite WHERE hgid=s_hgid;
			RETURN ;
		ELSE -- c'est pas le meme on l'insere et il est valide jusqu'au suivant
			INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
			values (nouveau.groupe, nouveau.nom_schema, nouveau.classe, nouveau.gid, nouveau.complement, nouveau.contenu, nouveau.debut_validite, s_deb_val, nouveau.geometrie);
			RETURN;
		END IF;
	END IF;
END;

$$;



CREATE FUNCTION histo.histor_traite_suivant(nouveau record, liste_exclusions name[]) RETURNS record
    LANGUAGE plpgsql
    AS $$
-- gestion de l'historique enregistrements suivants --
DECLARE
	s_id bigint;
	s_deb_val timestamp;
	s_contenu hstore;
	s_geom geometry;

BEGIN
	SELECT hgid, debut_validite, contenu, geometrie from histo.historique INTO s_id, s_deb_val, s_contenu, s_geom
		WHERE groupe=nouveau.groupe AND nom_schema=nouveau.nom_schema AND classe=nouveau.classe AND gid=nouveau.gid AND debut_validite > nouveau.debut_validite
		ORDER BY debut_validite ASC LIMIT 1; -- on cherche le premier apres
	IF NOT FOUND THEN -- il n'y a pas de suivant : on est tout seul on l'insere avec une duree de vie de 1 jour

		INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
		values (nouveau.groupe, nouveau.nom_schema, nouveau.classe, nouveau.gid, nouveau.complement, nouveau.contenu, nouveau.debut_validite,
				nouveau.debut_validite+'1 day'::interval, nouveau.geometrie);
		RETURN nouveau;
	ELSE -- il y a un suivant
		IF NEW.contenu - liste_exclusions = s_contenu - liste_exclusions and nouveau.geometrie = s_geom THEN -- c'est le meme : on etend sa vie
			UPDATE histo.historique SET debut_validite = nouveau.debut_validite WHERE hgid=s_hgid;
			RETURN NULL;
		ELSE -- c'est pas le meme on l'insere et il est valide jusqu'au suivant
			INSERT INTO histo.historique (groupe, nom_schema, classe, gid, complement, contenu, debut_validite, fin_validite, geometrie)
			values (nouveau.groupe, nouveau.nom_schema, nouveau.classe, nouveau.gid, nouveau.complement, nouveau.contenu, nouveau.debut_validite, s_deb_val, nouveau.geometrie);
			RETURN nouveau;
		END IF;
	END IF;
END;

$$;

SET default_with_oids = false;

--
-- TOC entry 222 (class 1259 OID 19101)
-- Name: historique; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.historique_modele (
    hgid bigserial ,
    nom_schema text NOT NULL,
    classe text NOT NULL,
    gid bigint NOT NULL,
    complement text,
    contenu public.hstore,
    debut_validite timestamp without time zone,
    fin_validite timestamp without time zone,
    courant boolean,
    geometrie public.geometry,
    CONSTRAINT historique_modele_pkey PRIMARY KEY (hgid);

)
CREATE INDEX historique_modele_gist ON ONLY histo.historique_modele USING gist (geometrie);
CREATE INDEX historique_classe ON ONLY histo.historique_modele USING btree (nom_schema, classe, gid, debut_validite);

CREATE TABLE histo.config_histo (
    nom_schema name NOT NULL,
    classe name NOT NULL,
    groupe name,
    complement name,
    exclusions name[]
);


COMMENT ON TABLE histo.config_histo IS 'table de configuration de l''historisation';



--

CREATE VIEW histo.histo_load AS
 SELECT
    historique.nom_schema,
    historique.classe,
    historique.gid,
    historique.complement,
    historique.contenu,
    historique.debut_validite,
    historique.fin_validite,
    historique.geometrie
   FROM histo.historique
 LIMIT 1;


COMMENT ON VIEW histo.histo_load IS 'pseudo vue de chargement des tables historiques';


--

CREATE TRIGGER trig_histo_load INSTEAD OF INSERT ON histo.histo_load FOR EACH ROW EXECUTE PROCEDURE histo.histor_groupe2();

COMMENT ON TRIGGER trig_histo_load ON histo.histo_load IS 'trigger de chargement de l''historique';
