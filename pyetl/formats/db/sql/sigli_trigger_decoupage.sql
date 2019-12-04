-- Function: admin_sigli.dependances_decoupe_ligne()
-- DROP FUNCTION admin_sigli.dependances_decoupe_ligne();
CREATE OR REPLACE FUNCTION admin_sigli.dependances_decoupe_ligne()
  RETURNS trigger AS
$BODY$
DECLARE
	str_refid text;
	ciblepk text;
	valeur_cible text;
	ident oid;
	tmp hstore;
	tmp2 hstore;
	txt text;
	nouvid text;
	transfert hstore;
	dependance admin_sigli.info_fk;
	item record;
	toto int;
BEGIN
	ident := TG_RELID; -- classe courante
	str_refid := NEW.old_id; -- ancien identifiant servira a mettre a jour les dependances
	-- on cherche la clef primaire de la classe_courante
	EXECUTE 'select attname from pg_constraint,pg_attribute where conrelid=$1 and contype=''p'' and attrelid=conrelid and attnum=conkey[1]' USING ident INTO ciblepk;
	tmp := hstore(NEW);
	nouvid := tmp -> ciblepk; -- trouve la valeur de la clef primaire
	EXECUTE 'UPDATE '|| ident::regclass || ' set old_id = $1 WHERE '||ciblepk||'::text = $1 ' USING nouvid; -- reporte la clef primaire dans old_id

	--raise notice 'decoupage old_id: %',str_refid;

	IF str_refid IS NOT NULL THEN -- ne se declenche que si le champ old_id possede une valeur ( decoupage d'une entite existante  ou fusion )
		-- on trouve les dependances: toutes les classes qui ont une foreign key qui pointe sur la classe courante--
		--raise notice 'decoupage classes : %',(SELECT count(*) FROM admin_sigli.info_fk WHERE cible=ident);
		FOR dependance IN SELECT * FROM admin_sigli.info_fk WHERE cible=ident  LOOP -- premiere boucle sur les classes
			--pour chaque classe on cherche tous les enregistrements qui pointent sur l'enregistrement courant
			valeur_cible := tmp->dependance.attribut_cible;
			FOR item IN EXECUTE 'SELECT * FROM ' || dependance.fk::regclass || ' WHERE ' || dependance.attribut_lien || '::text = $1' USING str_refid LOOP -- pour tous les enregistrements d'une classe
				IF dependance.defaut is not null THEN --si la clef primaire est un serial il faut l'initialiser et il faut renseigner l'attribut de la clef etrangere
					transfert := dependance.attribut_cible || '=>' || valeur_cible ||','||dependance.attributpk1|| '=>NULL';
				ELSE
					transfert := dependance.attribut_cible || '=>' || valeur_cible;
				END IF;
				--on injecte cela dans une copie de l'enregistrement
				item := (SELECT item #= transfert);
				--raise notice 'transfert fk : %',hstore(item);
				PERFORM admin_sigli.fk_insert_from_hstore(dependance.fk,hstore(item)); -- et on le reinjecte dans la table
			END LOOP;
		END LOOP;
		-- et on recharge tous les elements detruits s'il y en a
		PERFORM admin_sigli.fk_restore_fk(ident, str_refid, nouvid);
	END IF;
	RETURN NEW;
END;

$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 1000;
ALTER FUNCTION admin_sigli.dependances_decoupe_ligne()
  OWNER TO sigli;
