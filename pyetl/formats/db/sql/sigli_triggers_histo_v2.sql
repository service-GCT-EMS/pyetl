-- FUNCTION: admin_sigli.histor()
 -- DROP FUNCTION admin_sigli.histor();

CREATE OR REPLACE FUNCTION admin_sigli.histor() RETURNS trigger LANGUAGE 'plpgsql' COST 100 VOLATILE NOT LEAKPROOF SECURITY DEFINER AS $BODY$
declare   nouveau hstore; ancien hstore;
          donnees hstore;
          cmp_n hstore; cmp_a hstore;
          g_histo geometry; d_histo hstore;
          clef_histo bigint;
          req_histo text;
BEGIN
  req_histo = 'INSERT INTO histo.%I(nom_table, nom_schema, identifiant, complement, donnees , geometrie, courant, date_debut_validite, date_fin_validite)
              VALUES(%L, %L, %L, %L, %L, %L, %L, %L, %L)';
  ancien = hstore(coalesce(OLD,NEW));
  cmp_a=ancien-TG_ARGV[3]::text[];
  donnees=cmp_a-'geometrie'::text;

  IF TG_OP = 'UPDATE' THEN
    nouveau := hstore(NEW);
    cmp_n = nouveau-TG_ARGV[3]::text[];
    IF cmp_a = cmp_n THEN
      return NEW; -- rien a faire
    END IF;
  END IF;
  EXECUTE format('SELECT clef,donnees,geometrie FROM  histo.%I WHERE nom_table=%L AND identifiant=%L and courant =''t'' ',
                  TG_ARGV[1],TG_TABLE_NAME,ancien->TG_ARGV[2]) INTO clef_histo,d_histo,g_histo;
  IF clef_histo IS NOT NULL THEN -- l objet existe en base histo : on l annulle
    EXECUTE format('UPDATE histo.%I SET date_fin_validite = now(), courant = ''f'' WHERE clef = %L', TG_ARGV[1],clef_histo);
    IF d_histo <> donnees OR g_histo <> ancien->'geometrie'::text  THEN -- incoherence on ajoute un enregistrement pour garder la trace
      EXECUTE format(req_histo,TG_ARGV[1], TG_TABLE_NAME,TG_TABLE_SCHEMA,ancien->TG_ARGV[2], ancien->TG_ARGV[0],donnees,ancien->'geometrie'::text,'f',now(),now());
    END IF;
  ELSE --l' element n existe pas on le cree
    IF TG_OP = 'UPDATE' OR TG_OP = 'DELETE' THEN
      EXECUTE format(req_histo,TG_ARGV[1], TG_TABLE_NAME,TG_TABLE_SCHEMA,ancien->TG_ARGV[2], ancien->TG_ARGV[0],donnees,ancien->'geometrie'::text,'f',NULL,now());
    END IF;
  END IF;
  IF TG_OP = 'UPDATE' OR TG_OP='INSERT' THEN
    donnees=cmp_n-'geometrie'::text;
    EXECUTE format(req_histo,TG_ARGV[1], TG_TABLE_NAME,TG_TABLE_SCHEMA,nouveau->TG_ARGV[2], nouveau->TG_ARGV[0],donnees,nouveau->'geometrie'::text,'t',now(),Null);
    RETURN NEW;
  END IF;
  RETURN OLD;
END;
$BODY$;

