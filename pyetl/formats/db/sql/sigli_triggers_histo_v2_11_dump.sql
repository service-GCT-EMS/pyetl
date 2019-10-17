--
-- PostgreSQL database dump
--

-- Dumped from database version 11.1
-- Dumped by pg_dump version 11.1

-- Started on 2019-08-06 17:55:46

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 9 (class 2615 OID 18104)
-- Name: histo; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA histo;


ALTER SCHEMA histo OWNER TO postgres;

--
-- TOC entry 1605 (class 1255 OID 100298)
-- Name: histor_groupe(); Type: FUNCTION; Schema: histo; Owner: postgres
--

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


ALTER FUNCTION histo.histor_groupe() OWNER TO postgres;

--
-- TOC entry 1607 (class 1255 OID 100304)
-- Name: histor_groupe2(); Type: FUNCTION; Schema: histo; Owner: postgres
--

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


ALTER FUNCTION histo.histor_groupe2() OWNER TO postgres;

--
-- TOC entry 1604 (class 1255 OID 19457)
-- Name: histor_groupe_opt(); Type: FUNCTION; Schema: histo; Owner: postgres
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


ALTER FUNCTION histo.histor_groupe_opt() OWNER TO postgres;

--
-- TOC entry 1606 (class 1255 OID 100300)
-- Name: histor_traite_suivant(record); Type: FUNCTION; Schema: histo; Owner: postgres
--

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


ALTER FUNCTION histo.histor_traite_suivant(nouveau record) OWNER TO postgres;

--
-- TOC entry 1608 (class 1255 OID 100303)
-- Name: histor_traite_suivant(record, name[]); Type: FUNCTION; Schema: histo; Owner: postgres
--

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


ALTER FUNCTION histo.histor_traite_suivant(nouveau record, liste_exclusions name[]) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 222 (class 1259 OID 19101)
-- Name: historique; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.historique (
    hgid bigint NOT NULL,
    groupe text NOT NULL,
    nom_schema text NOT NULL,
    classe text NOT NULL,
    gid bigint NOT NULL,
    complement text,
    contenu public.hstore,
    debut_validite timestamp without time zone,
    fin_validite timestamp without time zone,
    geometrie public.geometry
)
PARTITION BY LIST (groupe);


ALTER TABLE histo.historique OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 19125)
-- Name: bati; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.bati PARTITION OF histo.historique
FOR VALUES IN ('bati');


ALTER TABLE histo.bati OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 19116)
-- Name: carto; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.carto PARTITION OF histo.historique
FOR VALUES IN ('carto');


ALTER TABLE histo.carto OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 19500)
-- Name: carto_gen; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.carto_gen PARTITION OF histo.historique
FOR VALUES IN ('carto_gen');


ALTER TABLE histo.carto_gen OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 19459)
-- Name: config_histo; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.config_histo (
    nom_schema name NOT NULL,
    classe name NOT NULL,
    groupe name,
    complement name,
    exclusions name[]
);


ALTER TABLE histo.config_histo OWNER TO postgres;

--
-- TOC entry 4934 (class 0 OID 0)
-- Dependencies: 268
-- Name: TABLE config_histo; Type: COMMENT; Schema: histo; Owner: postgres
--

COMMENT ON TABLE histo.config_histo IS 'table de configuration de l''historisation';


--
-- TOC entry 270 (class 1259 OID 19511)
-- Name: defaut; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.defaut PARTITION OF histo.historique
DEFAULT;


ALTER TABLE histo.defaut OWNER TO postgres;

--
-- TOC entry 272 (class 1259 OID 103806)
-- Name: elyas; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyas PARTITION OF histo.historique
FOR VALUES IN ('elyas');


ALTER TABLE histo.elyas OWNER TO postgres;

--
-- TOC entry 273 (class 1259 OID 112847)
-- Name: elyba; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyba PARTITION OF histo.historique
FOR VALUES IN ('elyba');


ALTER TABLE histo.elyba OWNER TO postgres;

--
-- TOC entry 274 (class 1259 OID 112858)
-- Name: elyea; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyea PARTITION OF histo.historique
FOR VALUES IN ('elyea');


ALTER TABLE histo.elyea OWNER TO postgres;

--
-- TOC entry 275 (class 1259 OID 112869)
-- Name: elyec; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyec PARTITION OF histo.historique
FOR VALUES IN ('elyec');


ALTER TABLE histo.elyec OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 112880)
-- Name: elyed; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyed PARTITION OF histo.historique
FOR VALUES IN ('elyed');


ALTER TABLE histo.elyed OWNER TO postgres;

--
-- TOC entry 277 (class 1259 OID 112891)
-- Name: elyep; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyep PARTITION OF histo.historique
FOR VALUES IN ('elyep');


ALTER TABLE histo.elyep OWNER TO postgres;

--
-- TOC entry 278 (class 1259 OID 112902)
-- Name: elyev; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyev PARTITION OF histo.historique
FOR VALUES IN ('elyev');


ALTER TABLE histo.elyev OWNER TO postgres;

--
-- TOC entry 279 (class 1259 OID 112913)
-- Name: elygc; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elygc PARTITION OF histo.historique
FOR VALUES IN ('elygc');


ALTER TABLE histo.elygc OWNER TO postgres;

--
-- TOC entry 280 (class 1259 OID 112924)
-- Name: elyin; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyin PARTITION OF histo.historique
FOR VALUES IN ('elyin');


ALTER TABLE histo.elyin OWNER TO postgres;

--
-- TOC entry 281 (class 1259 OID 112935)
-- Name: elypg; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elypg PARTITION OF histo.historique
FOR VALUES IN ('elypg');


ALTER TABLE histo.elypg OWNER TO postgres;

--
-- TOC entry 282 (class 1259 OID 112946)
-- Name: elypu; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elypu PARTITION OF histo.historique
FOR VALUES IN ('elypu');


ALTER TABLE histo.elypu OWNER TO postgres;

--
-- TOC entry 283 (class 1259 OID 112957)
-- Name: elyrc; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyrc PARTITION OF histo.historique
FOR VALUES IN ('elyrc');


ALTER TABLE histo.elyrc OWNER TO postgres;

--
-- TOC entry 284 (class 1259 OID 112968)
-- Name: elyre; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyre PARTITION OF histo.historique
FOR VALUES IN ('elyre');


ALTER TABLE histo.elyre OWNER TO postgres;

--
-- TOC entry 285 (class 1259 OID 112979)
-- Name: elyse; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyse PARTITION OF histo.historique
FOR VALUES IN ('elyse');


ALTER TABLE histo.elyse OWNER TO postgres;

--
-- TOC entry 286 (class 1259 OID 112990)
-- Name: elysg; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elysg PARTITION OF histo.historique
FOR VALUES IN ('elysg');


ALTER TABLE histo.elysg OWNER TO postgres;

--
-- TOC entry 287 (class 1259 OID 113001)
-- Name: elysi; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elysi PARTITION OF histo.historique
FOR VALUES IN ('elysi');


ALTER TABLE histo.elysi OWNER TO postgres;

--
-- TOC entry 288 (class 1259 OID 113012)
-- Name: elytd; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elytd PARTITION OF histo.historique
FOR VALUES IN ('elytd');


ALTER TABLE histo.elytd OWNER TO postgres;

--
-- TOC entry 289 (class 1259 OID 113023)
-- Name: elyti; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elyti PARTITION OF histo.historique
FOR VALUES IN ('elyti');


ALTER TABLE histo.elyti OWNER TO postgres;

--
-- TOC entry 290 (class 1259 OID 113034)
-- Name: elytr; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.elytr PARTITION OF histo.historique
FOR VALUES IN ('elytr');


ALTER TABLE histo.elytr OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 19532)
-- Name: histo_load; Type: VIEW; Schema: histo; Owner: postgres
--

CREATE VIEW histo.histo_load AS
 SELECT historique.groupe,
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


ALTER TABLE histo.histo_load OWNER TO postgres;

--
-- TOC entry 4938 (class 0 OID 0)
-- Dependencies: 271
-- Name: VIEW histo_load; Type: COMMENT; Schema: histo; Owner: postgres
--

COMMENT ON VIEW histo.histo_load IS 'pseudo vue de chargement des tables historiques';


--
-- TOC entry 221 (class 1259 OID 19099)
-- Name: historique_hgid_seq; Type: SEQUENCE; Schema: histo; Owner: postgres
--

CREATE SEQUENCE histo.historique_hgid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE histo.historique_hgid_seq OWNER TO postgres;

--
-- TOC entry 4939 (class 0 OID 0)
-- Dependencies: 221
-- Name: historique_hgid_seq; Type: SEQUENCE OWNED BY; Schema: histo; Owner: postgres
--

ALTER SEQUENCE histo.historique_hgid_seq OWNED BY histo.historique.hgid;


--
-- TOC entry 223 (class 1259 OID 19107)
-- Name: voirie; Type: TABLE; Schema: histo; Owner: postgres
--

CREATE TABLE histo.voirie PARTITION OF histo.historique
FOR VALUES IN ('voirie');


ALTER TABLE histo.voirie OWNER TO postgres;

--
-- TOC entry 4524 (class 2604 OID 19128)
-- Name: bati hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.bati ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4523 (class 2604 OID 19119)
-- Name: carto hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.carto ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4525 (class 2604 OID 19503)
-- Name: carto_gen hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.carto_gen ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4526 (class 2604 OID 19514)
-- Name: defaut hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.defaut ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4527 (class 2604 OID 103809)
-- Name: elyas hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyas ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4528 (class 2604 OID 112850)
-- Name: elyba hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyba ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4529 (class 2604 OID 112861)
-- Name: elyea hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyea ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4530 (class 2604 OID 112872)
-- Name: elyec hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyec ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4531 (class 2604 OID 112883)
-- Name: elyed hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyed ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4532 (class 2604 OID 112894)
-- Name: elyep hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyep ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4533 (class 2604 OID 112905)
-- Name: elyev hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyev ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4534 (class 2604 OID 112916)
-- Name: elygc hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elygc ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4535 (class 2604 OID 112927)
-- Name: elyin hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyin ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4536 (class 2604 OID 112938)
-- Name: elypg hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elypg ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4537 (class 2604 OID 112949)
-- Name: elypu hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elypu ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4538 (class 2604 OID 112960)
-- Name: elyrc hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyrc ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4539 (class 2604 OID 112971)
-- Name: elyre hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyre ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4540 (class 2604 OID 112982)
-- Name: elyse hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyse ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4541 (class 2604 OID 112993)
-- Name: elysg hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elysg ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4542 (class 2604 OID 113004)
-- Name: elysi hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elysi ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4543 (class 2604 OID 113015)
-- Name: elytd hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elytd ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4544 (class 2604 OID 113026)
-- Name: elyti hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyti ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4545 (class 2604 OID 113037)
-- Name: elytr hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elytr ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4521 (class 2604 OID 19104)
-- Name: historique hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.historique ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4522 (class 2604 OID 19110)
-- Name: voirie hgid; Type: DEFAULT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.voirie ALTER COLUMN hgid SET DEFAULT nextval('histo.historique_hgid_seq'::regclass);


--
-- TOC entry 4550 (class 2606 OID 19106)
-- Name: historique historique_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.historique
    ADD CONSTRAINT historique_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4565 (class 2606 OID 19130)
-- Name: bati bati_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.bati
    ADD CONSTRAINT bati_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4572 (class 2606 OID 19505)
-- Name: carto_gen carto_gen_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.carto_gen
    ADD CONSTRAINT carto_gen_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4560 (class 2606 OID 19121)
-- Name: carto carto_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.carto
    ADD CONSTRAINT carto_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4567 (class 2606 OID 19466)
-- Name: config_histo config_histo_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.config_histo
    ADD CONSTRAINT config_histo_pkey PRIMARY KEY (nom_schema, classe);


--
-- TOC entry 4577 (class 2606 OID 19516)
-- Name: defaut defaut_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.defaut
    ADD CONSTRAINT defaut_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4582 (class 2606 OID 103811)
-- Name: elyas elyas_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyas
    ADD CONSTRAINT elyas_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4587 (class 2606 OID 112852)
-- Name: elyba elyba_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyba
    ADD CONSTRAINT elyba_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4592 (class 2606 OID 112863)
-- Name: elyea elyea_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyea
    ADD CONSTRAINT elyea_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4597 (class 2606 OID 112874)
-- Name: elyec elyec_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyec
    ADD CONSTRAINT elyec_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4602 (class 2606 OID 112885)
-- Name: elyed elyed_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyed
    ADD CONSTRAINT elyed_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4607 (class 2606 OID 112896)
-- Name: elyep elyep_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyep
    ADD CONSTRAINT elyep_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4612 (class 2606 OID 112907)
-- Name: elyev elyev_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyev
    ADD CONSTRAINT elyev_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4617 (class 2606 OID 112918)
-- Name: elygc elygc_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elygc
    ADD CONSTRAINT elygc_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4622 (class 2606 OID 112929)
-- Name: elyin elyin_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyin
    ADD CONSTRAINT elyin_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4627 (class 2606 OID 112940)
-- Name: elypg elypg_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elypg
    ADD CONSTRAINT elypg_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4632 (class 2606 OID 112951)
-- Name: elypu elypu_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elypu
    ADD CONSTRAINT elypu_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4637 (class 2606 OID 112962)
-- Name: elyrc elyrc_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyrc
    ADD CONSTRAINT elyrc_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4642 (class 2606 OID 112973)
-- Name: elyre elyre_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyre
    ADD CONSTRAINT elyre_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4647 (class 2606 OID 112984)
-- Name: elyse elyse_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyse
    ADD CONSTRAINT elyse_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4652 (class 2606 OID 112995)
-- Name: elysg elysg_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elysg
    ADD CONSTRAINT elysg_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4657 (class 2606 OID 113006)
-- Name: elysi elysi_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elysi
    ADD CONSTRAINT elysi_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4662 (class 2606 OID 113017)
-- Name: elytd elytd_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elytd
    ADD CONSTRAINT elytd_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4667 (class 2606 OID 113028)
-- Name: elyti elyti_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elyti
    ADD CONSTRAINT elyti_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4672 (class 2606 OID 113039)
-- Name: elytr elytr_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.elytr
    ADD CONSTRAINT elytr_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4555 (class 2606 OID 19112)
-- Name: voirie voirie_pkey; Type: CONSTRAINT; Schema: histo; Owner: postgres
--

ALTER TABLE ONLY histo.voirie
    ADD CONSTRAINT voirie_pkey PRIMARY KEY (hgid, groupe);


--
-- TOC entry 4547 (class 1259 OID 166675)
-- Name: historique_gist; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX historique_gist ON ONLY histo.historique USING gist (geometrie);


--
-- TOC entry 4561 (class 1259 OID 166676)
-- Name: bati_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX bati_geometrie_idx ON histo.bati USING gist (geometrie);


--
-- TOC entry 4546 (class 1259 OID 19143)
-- Name: historique_classe; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX historique_classe ON ONLY histo.historique USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4562 (class 1259 OID 19144)
-- Name: bati_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX bati_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.bati USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4548 (class 1259 OID 19139)
-- Name: historique_hgid; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX historique_hgid ON ONLY histo.historique USING btree (hgid);


--
-- TOC entry 4563 (class 1259 OID 19140)
-- Name: bati_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX bati_hgid_idx ON histo.bati USING btree (hgid);


--
-- TOC entry 4568 (class 1259 OID 166678)
-- Name: carto_gen_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX carto_gen_geometrie_idx ON histo.carto_gen USING gist (geometrie);


--
-- TOC entry 4569 (class 1259 OID 19507)
-- Name: carto_gen_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX carto_gen_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.carto_gen USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4570 (class 1259 OID 19506)
-- Name: carto_gen_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX carto_gen_hgid_idx ON histo.carto_gen USING btree (hgid);


--
-- TOC entry 4556 (class 1259 OID 166677)
-- Name: carto_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX carto_geometrie_idx ON histo.carto USING gist (geometrie);


--
-- TOC entry 4557 (class 1259 OID 19145)
-- Name: carto_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX carto_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.carto USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4558 (class 1259 OID 19141)
-- Name: carto_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX carto_hgid_idx ON histo.carto USING btree (hgid);


--
-- TOC entry 4573 (class 1259 OID 166699)
-- Name: defaut_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX defaut_geometrie_idx ON histo.defaut USING gist (geometrie);


--
-- TOC entry 4574 (class 1259 OID 19518)
-- Name: defaut_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX defaut_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.defaut USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4575 (class 1259 OID 19517)
-- Name: defaut_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX defaut_hgid_idx ON histo.defaut USING btree (hgid);


--
-- TOC entry 4578 (class 1259 OID 166679)
-- Name: elyas_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyas_geometrie_idx ON histo.elyas USING gist (geometrie);


--
-- TOC entry 4579 (class 1259 OID 103813)
-- Name: elyas_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyas_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyas USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4580 (class 1259 OID 103812)
-- Name: elyas_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyas_hgid_idx ON histo.elyas USING btree (hgid);


--
-- TOC entry 4583 (class 1259 OID 166680)
-- Name: elyba_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyba_geometrie_idx ON histo.elyba USING gist (geometrie);


--
-- TOC entry 4584 (class 1259 OID 112854)
-- Name: elyba_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyba_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyba USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4585 (class 1259 OID 112853)
-- Name: elyba_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyba_hgid_idx ON histo.elyba USING btree (hgid);


--
-- TOC entry 4588 (class 1259 OID 166681)
-- Name: elyea_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyea_geometrie_idx ON histo.elyea USING gist (geometrie);


--
-- TOC entry 4589 (class 1259 OID 112865)
-- Name: elyea_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyea_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyea USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4590 (class 1259 OID 112864)
-- Name: elyea_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyea_hgid_idx ON histo.elyea USING btree (hgid);


--
-- TOC entry 4593 (class 1259 OID 166682)
-- Name: elyec_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyec_geometrie_idx ON histo.elyec USING gist (geometrie);


--
-- TOC entry 4594 (class 1259 OID 112876)
-- Name: elyec_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyec_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyec USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4595 (class 1259 OID 112875)
-- Name: elyec_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyec_hgid_idx ON histo.elyec USING btree (hgid);


--
-- TOC entry 4598 (class 1259 OID 166683)
-- Name: elyed_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyed_geometrie_idx ON histo.elyed USING gist (geometrie);


--
-- TOC entry 4599 (class 1259 OID 112887)
-- Name: elyed_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyed_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyed USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4600 (class 1259 OID 112886)
-- Name: elyed_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyed_hgid_idx ON histo.elyed USING btree (hgid);


--
-- TOC entry 4603 (class 1259 OID 166684)
-- Name: elyep_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyep_geometrie_idx ON histo.elyep USING gist (geometrie);


--
-- TOC entry 4604 (class 1259 OID 112898)
-- Name: elyep_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyep_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyep USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4605 (class 1259 OID 112897)
-- Name: elyep_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyep_hgid_idx ON histo.elyep USING btree (hgid);


--
-- TOC entry 4608 (class 1259 OID 166685)
-- Name: elyev_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyev_geometrie_idx ON histo.elyev USING gist (geometrie);


--
-- TOC entry 4609 (class 1259 OID 112909)
-- Name: elyev_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyev_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyev USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4610 (class 1259 OID 112908)
-- Name: elyev_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyev_hgid_idx ON histo.elyev USING btree (hgid);


--
-- TOC entry 4613 (class 1259 OID 166686)
-- Name: elygc_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elygc_geometrie_idx ON histo.elygc USING gist (geometrie);


--
-- TOC entry 4614 (class 1259 OID 112920)
-- Name: elygc_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elygc_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elygc USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4615 (class 1259 OID 112919)
-- Name: elygc_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elygc_hgid_idx ON histo.elygc USING btree (hgid);


--
-- TOC entry 4618 (class 1259 OID 166687)
-- Name: elyin_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyin_geometrie_idx ON histo.elyin USING gist (geometrie);


--
-- TOC entry 4619 (class 1259 OID 112931)
-- Name: elyin_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyin_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyin USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4620 (class 1259 OID 112930)
-- Name: elyin_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyin_hgid_idx ON histo.elyin USING btree (hgid);


--
-- TOC entry 4623 (class 1259 OID 166688)
-- Name: elypg_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elypg_geometrie_idx ON histo.elypg USING gist (geometrie);


--
-- TOC entry 4624 (class 1259 OID 112942)
-- Name: elypg_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elypg_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elypg USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4625 (class 1259 OID 112941)
-- Name: elypg_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elypg_hgid_idx ON histo.elypg USING btree (hgid);


--
-- TOC entry 4628 (class 1259 OID 166689)
-- Name: elypu_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elypu_geometrie_idx ON histo.elypu USING gist (geometrie);


--
-- TOC entry 4629 (class 1259 OID 112953)
-- Name: elypu_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elypu_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elypu USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4630 (class 1259 OID 112952)
-- Name: elypu_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elypu_hgid_idx ON histo.elypu USING btree (hgid);


--
-- TOC entry 4633 (class 1259 OID 166690)
-- Name: elyrc_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyrc_geometrie_idx ON histo.elyrc USING gist (geometrie);


--
-- TOC entry 4634 (class 1259 OID 112964)
-- Name: elyrc_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyrc_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyrc USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4635 (class 1259 OID 112963)
-- Name: elyrc_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyrc_hgid_idx ON histo.elyrc USING btree (hgid);


--
-- TOC entry 4638 (class 1259 OID 166691)
-- Name: elyre_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyre_geometrie_idx ON histo.elyre USING gist (geometrie);


--
-- TOC entry 4639 (class 1259 OID 112975)
-- Name: elyre_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyre_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyre USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4640 (class 1259 OID 112974)
-- Name: elyre_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyre_hgid_idx ON histo.elyre USING btree (hgid);


--
-- TOC entry 4643 (class 1259 OID 166692)
-- Name: elyse_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyse_geometrie_idx ON histo.elyse USING gist (geometrie);


--
-- TOC entry 4644 (class 1259 OID 112986)
-- Name: elyse_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyse_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyse USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4645 (class 1259 OID 112985)
-- Name: elyse_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyse_hgid_idx ON histo.elyse USING btree (hgid);


--
-- TOC entry 4648 (class 1259 OID 166693)
-- Name: elysg_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elysg_geometrie_idx ON histo.elysg USING gist (geometrie);


--
-- TOC entry 4649 (class 1259 OID 112997)
-- Name: elysg_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elysg_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elysg USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4650 (class 1259 OID 112996)
-- Name: elysg_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elysg_hgid_idx ON histo.elysg USING btree (hgid);


--
-- TOC entry 4653 (class 1259 OID 166694)
-- Name: elysi_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elysi_geometrie_idx ON histo.elysi USING gist (geometrie);


--
-- TOC entry 4654 (class 1259 OID 113008)
-- Name: elysi_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elysi_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elysi USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4655 (class 1259 OID 113007)
-- Name: elysi_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elysi_hgid_idx ON histo.elysi USING btree (hgid);


--
-- TOC entry 4658 (class 1259 OID 166695)
-- Name: elytd_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elytd_geometrie_idx ON histo.elytd USING gist (geometrie);


--
-- TOC entry 4659 (class 1259 OID 113019)
-- Name: elytd_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elytd_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elytd USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4660 (class 1259 OID 113018)
-- Name: elytd_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elytd_hgid_idx ON histo.elytd USING btree (hgid);


--
-- TOC entry 4663 (class 1259 OID 166696)
-- Name: elyti_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyti_geometrie_idx ON histo.elyti USING gist (geometrie);


--
-- TOC entry 4664 (class 1259 OID 113030)
-- Name: elyti_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyti_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elyti USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4665 (class 1259 OID 113029)
-- Name: elyti_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elyti_hgid_idx ON histo.elyti USING btree (hgid);


--
-- TOC entry 4668 (class 1259 OID 166697)
-- Name: elytr_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elytr_geometrie_idx ON histo.elytr USING gist (geometrie);


--
-- TOC entry 4669 (class 1259 OID 113041)
-- Name: elytr_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elytr_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.elytr USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4670 (class 1259 OID 113040)
-- Name: elytr_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX elytr_hgid_idx ON histo.elytr USING btree (hgid);


--
-- TOC entry 4551 (class 1259 OID 166698)
-- Name: voirie_geometrie_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX voirie_geometrie_idx ON histo.voirie USING gist (geometrie);


--
-- TOC entry 4552 (class 1259 OID 19146)
-- Name: voirie_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX voirie_groupe_nom_schema_classe_gid_debut_validite_idx ON histo.voirie USING btree (groupe, nom_schema, classe, gid) INCLUDE (debut_validite);


--
-- TOC entry 4553 (class 1259 OID 19142)
-- Name: voirie_hgid_idx; Type: INDEX; Schema: histo; Owner: postgres
--

CREATE INDEX voirie_hgid_idx ON histo.voirie USING btree (hgid);


--
-- TOC entry 4681 (class 0 OID 0)
-- Name: bati_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.bati_geometrie_idx;


--
-- TOC entry 4682 (class 0 OID 0)
-- Name: bati_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.bati_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4683 (class 0 OID 0)
-- Name: bati_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.bati_hgid_idx;


--
-- TOC entry 4684 (class 0 OID 0)
-- Name: bati_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.bati_pkey;


--
-- TOC entry 4685 (class 0 OID 0)
-- Name: carto_gen_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.carto_gen_geometrie_idx;


--
-- TOC entry 4686 (class 0 OID 0)
-- Name: carto_gen_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.carto_gen_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4687 (class 0 OID 0)
-- Name: carto_gen_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.carto_gen_hgid_idx;


--
-- TOC entry 4688 (class 0 OID 0)
-- Name: carto_gen_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.carto_gen_pkey;


--
-- TOC entry 4677 (class 0 OID 0)
-- Name: carto_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.carto_geometrie_idx;


--
-- TOC entry 4678 (class 0 OID 0)
-- Name: carto_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.carto_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4679 (class 0 OID 0)
-- Name: carto_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.carto_hgid_idx;


--
-- TOC entry 4680 (class 0 OID 0)
-- Name: carto_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.carto_pkey;


--
-- TOC entry 4689 (class 0 OID 0)
-- Name: defaut_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.defaut_geometrie_idx;


--
-- TOC entry 4690 (class 0 OID 0)
-- Name: defaut_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.defaut_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4691 (class 0 OID 0)
-- Name: defaut_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.defaut_hgid_idx;


--
-- TOC entry 4692 (class 0 OID 0)
-- Name: defaut_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.defaut_pkey;


--
-- TOC entry 4693 (class 0 OID 0)
-- Name: elyas_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyas_geometrie_idx;


--
-- TOC entry 4694 (class 0 OID 0)
-- Name: elyas_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyas_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4695 (class 0 OID 0)
-- Name: elyas_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyas_hgid_idx;


--
-- TOC entry 4696 (class 0 OID 0)
-- Name: elyas_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyas_pkey;


--
-- TOC entry 4697 (class 0 OID 0)
-- Name: elyba_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyba_geometrie_idx;


--
-- TOC entry 4698 (class 0 OID 0)
-- Name: elyba_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyba_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4699 (class 0 OID 0)
-- Name: elyba_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyba_hgid_idx;


--
-- TOC entry 4700 (class 0 OID 0)
-- Name: elyba_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyba_pkey;


--
-- TOC entry 4701 (class 0 OID 0)
-- Name: elyea_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyea_geometrie_idx;


--
-- TOC entry 4702 (class 0 OID 0)
-- Name: elyea_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyea_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4703 (class 0 OID 0)
-- Name: elyea_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyea_hgid_idx;


--
-- TOC entry 4704 (class 0 OID 0)
-- Name: elyea_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyea_pkey;


--
-- TOC entry 4705 (class 0 OID 0)
-- Name: elyec_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyec_geometrie_idx;


--
-- TOC entry 4706 (class 0 OID 0)
-- Name: elyec_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyec_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4707 (class 0 OID 0)
-- Name: elyec_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyec_hgid_idx;


--
-- TOC entry 4708 (class 0 OID 0)
-- Name: elyec_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyec_pkey;


--
-- TOC entry 4709 (class 0 OID 0)
-- Name: elyed_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyed_geometrie_idx;


--
-- TOC entry 4710 (class 0 OID 0)
-- Name: elyed_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyed_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4711 (class 0 OID 0)
-- Name: elyed_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyed_hgid_idx;


--
-- TOC entry 4712 (class 0 OID 0)
-- Name: elyed_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyed_pkey;


--
-- TOC entry 4713 (class 0 OID 0)
-- Name: elyep_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyep_geometrie_idx;


--
-- TOC entry 4714 (class 0 OID 0)
-- Name: elyep_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyep_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4715 (class 0 OID 0)
-- Name: elyep_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyep_hgid_idx;


--
-- TOC entry 4716 (class 0 OID 0)
-- Name: elyep_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyep_pkey;


--
-- TOC entry 4717 (class 0 OID 0)
-- Name: elyev_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyev_geometrie_idx;


--
-- TOC entry 4718 (class 0 OID 0)
-- Name: elyev_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyev_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4719 (class 0 OID 0)
-- Name: elyev_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyev_hgid_idx;


--
-- TOC entry 4720 (class 0 OID 0)
-- Name: elyev_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyev_pkey;


--
-- TOC entry 4721 (class 0 OID 0)
-- Name: elygc_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elygc_geometrie_idx;


--
-- TOC entry 4722 (class 0 OID 0)
-- Name: elygc_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elygc_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4723 (class 0 OID 0)
-- Name: elygc_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elygc_hgid_idx;


--
-- TOC entry 4724 (class 0 OID 0)
-- Name: elygc_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elygc_pkey;


--
-- TOC entry 4725 (class 0 OID 0)
-- Name: elyin_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyin_geometrie_idx;


--
-- TOC entry 4726 (class 0 OID 0)
-- Name: elyin_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyin_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4727 (class 0 OID 0)
-- Name: elyin_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyin_hgid_idx;


--
-- TOC entry 4728 (class 0 OID 0)
-- Name: elyin_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyin_pkey;


--
-- TOC entry 4729 (class 0 OID 0)
-- Name: elypg_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elypg_geometrie_idx;


--
-- TOC entry 4730 (class 0 OID 0)
-- Name: elypg_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elypg_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4731 (class 0 OID 0)
-- Name: elypg_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elypg_hgid_idx;


--
-- TOC entry 4732 (class 0 OID 0)
-- Name: elypg_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elypg_pkey;


--
-- TOC entry 4733 (class 0 OID 0)
-- Name: elypu_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elypu_geometrie_idx;


--
-- TOC entry 4734 (class 0 OID 0)
-- Name: elypu_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elypu_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4735 (class 0 OID 0)
-- Name: elypu_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elypu_hgid_idx;


--
-- TOC entry 4736 (class 0 OID 0)
-- Name: elypu_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elypu_pkey;


--
-- TOC entry 4737 (class 0 OID 0)
-- Name: elyrc_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyrc_geometrie_idx;


--
-- TOC entry 4738 (class 0 OID 0)
-- Name: elyrc_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyrc_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4739 (class 0 OID 0)
-- Name: elyrc_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyrc_hgid_idx;


--
-- TOC entry 4740 (class 0 OID 0)
-- Name: elyrc_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyrc_pkey;


--
-- TOC entry 4741 (class 0 OID 0)
-- Name: elyre_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyre_geometrie_idx;


--
-- TOC entry 4742 (class 0 OID 0)
-- Name: elyre_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyre_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4743 (class 0 OID 0)
-- Name: elyre_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyre_hgid_idx;


--
-- TOC entry 4744 (class 0 OID 0)
-- Name: elyre_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyre_pkey;


--
-- TOC entry 4745 (class 0 OID 0)
-- Name: elyse_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyse_geometrie_idx;


--
-- TOC entry 4746 (class 0 OID 0)
-- Name: elyse_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyse_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4747 (class 0 OID 0)
-- Name: elyse_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyse_hgid_idx;


--
-- TOC entry 4748 (class 0 OID 0)
-- Name: elyse_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyse_pkey;


--
-- TOC entry 4749 (class 0 OID 0)
-- Name: elysg_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elysg_geometrie_idx;


--
-- TOC entry 4750 (class 0 OID 0)
-- Name: elysg_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elysg_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4751 (class 0 OID 0)
-- Name: elysg_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elysg_hgid_idx;


--
-- TOC entry 4752 (class 0 OID 0)
-- Name: elysg_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elysg_pkey;


--
-- TOC entry 4753 (class 0 OID 0)
-- Name: elysi_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elysi_geometrie_idx;


--
-- TOC entry 4754 (class 0 OID 0)
-- Name: elysi_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elysi_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4755 (class 0 OID 0)
-- Name: elysi_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elysi_hgid_idx;


--
-- TOC entry 4756 (class 0 OID 0)
-- Name: elysi_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elysi_pkey;


--
-- TOC entry 4757 (class 0 OID 0)
-- Name: elytd_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elytd_geometrie_idx;


--
-- TOC entry 4758 (class 0 OID 0)
-- Name: elytd_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elytd_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4759 (class 0 OID 0)
-- Name: elytd_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elytd_hgid_idx;


--
-- TOC entry 4760 (class 0 OID 0)
-- Name: elytd_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elytd_pkey;


--
-- TOC entry 4761 (class 0 OID 0)
-- Name: elyti_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elyti_geometrie_idx;


--
-- TOC entry 4762 (class 0 OID 0)
-- Name: elyti_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elyti_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4763 (class 0 OID 0)
-- Name: elyti_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elyti_hgid_idx;


--
-- TOC entry 4764 (class 0 OID 0)
-- Name: elyti_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elyti_pkey;


--
-- TOC entry 4765 (class 0 OID 0)
-- Name: elytr_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.elytr_geometrie_idx;


--
-- TOC entry 4766 (class 0 OID 0)
-- Name: elytr_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.elytr_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4767 (class 0 OID 0)
-- Name: elytr_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.elytr_hgid_idx;


--
-- TOC entry 4768 (class 0 OID 0)
-- Name: elytr_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.elytr_pkey;


--
-- TOC entry 4673 (class 0 OID 0)
-- Name: voirie_geometrie_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_gist ATTACH PARTITION histo.voirie_geometrie_idx;


--
-- TOC entry 4674 (class 0 OID 0)
-- Name: voirie_groupe_nom_schema_classe_gid_debut_validite_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_classe ATTACH PARTITION histo.voirie_groupe_nom_schema_classe_gid_debut_validite_idx;


--
-- TOC entry 4675 (class 0 OID 0)
-- Name: voirie_hgid_idx; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_hgid ATTACH PARTITION histo.voirie_hgid_idx;


--
-- TOC entry 4676 (class 0 OID 0)
-- Name: voirie_pkey; Type: INDEX ATTACH; Schema: histo; Owner:
--

ALTER INDEX histo.historique_pkey ATTACH PARTITION histo.voirie_pkey;


--
-- TOC entry 4769 (class 2620 OID 100306)
-- Name: histo_load trig_histo_load; Type: TRIGGER; Schema: histo; Owner: postgres
--

CREATE TRIGGER trig_histo_load INSTEAD OF INSERT ON histo.histo_load FOR EACH ROW EXECUTE PROCEDURE histo.histor_groupe2();


--
-- TOC entry 4940 (class 0 OID 0)
-- Dependencies: 4769
-- Name: TRIGGER trig_histo_load ON histo_load; Type: COMMENT; Schema: histo; Owner: postgres
--

COMMENT ON TRIGGER trig_histo_load ON histo.histo_load IS 'trigger de chargement de l''historique';


--
-- TOC entry 4932 (class 0 OID 0)
-- Dependencies: 9
-- Name: SCHEMA histo; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA histo TO role_sigli_histo_a;


--
-- TOC entry 4933 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE bati; Type: ACL; Schema: histo; Owner: postgres
--

GRANT ALL ON TABLE histo.bati TO role_sigli_histo_a;


--
-- TOC entry 4935 (class 0 OID 0)
-- Dependencies: 268
-- Name: TABLE config_histo; Type: ACL; Schema: histo; Owner: postgres
--

GRANT ALL ON TABLE histo.config_histo TO role_sigli_histo_a;


--
-- TOC entry 4936 (class 0 OID 0)
-- Dependencies: 270
-- Name: TABLE defaut; Type: ACL; Schema: histo; Owner: postgres
--

GRANT ALL ON TABLE histo.defaut TO role_sigli_histo_a;


--
-- TOC entry 4937 (class 0 OID 0)
-- Dependencies: 272
-- Name: TABLE elyas; Type: ACL; Schema: histo; Owner: postgres
--

GRANT ALL ON TABLE histo.elyas TO role_sigli_histo_a;


-- Completed on 2019-08-06 17:55:47

--
-- PostgreSQL database dump complete
--
