# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 10:00:04 2018
''' generateur de sql pour la base postgres '''
@author: 89965
"""
# import os
import re

# import subprocess
from .database import DbGenSql

# from .postgres import RESERVES, GTYPES_DISC, GTYPES_CURVE, TYPES_A
RESERVES = {"analyse": "analyse_pb", "type": "type_entite", "as": "ass"}
SCHEMA_CONF = "public"


class PgrGenSql(DbGenSql):
    """classe de generation des structures sql"""

    def __init__(self, connection=None, basic=False, maj=True):
        super().__init__(connection=connection, basic=basic)
        self.geom = True
        self.courbes = False
        self.schemas = True
        self.types_db = {
            "T": "text",
            "texte": "text",
            "": "text",
            "t": "text",
            "A": "text",
            "E": "integer",
            "entier": "integer",
            "EL": "bigint",
            "el": "bigint",
            "entier_long": "bigint",
            "D": "timestamp",
            "d": "timestamp",
            "N": "numeric",
            "n": "numeric",
            "H": "hstore",
            "h": "hstore",
            "hstore": "hstore",
            "F": "float",
            "reel": "float",
            "float": "float",
            "flottant": "float",
            "f": "float",
            "date": "timestamp",
            "booleen": "boolean",
            "B": "boolean",
            "b": "boolean",
            "S": "serial NOT NULL",
            "BS": "bigserial NOT NULL",
        }

        self.stdtriggers = set(["auteur"])

        if basic:
            self.types_db["S"] = "integer"
            self.types_db["BS"] = "bigint"
            self.stdtriggers = set()
        self.typenum = {
            "1": "POINT",
            "2": "LIGNE",
            "3": "POLYGONE",
            "-1": "GEOMETRIE",
            "0": "ALPHA",
            "indef": "ALPHA",
        }

        self.reserves = RESERVES  # mots reserves et leur remplacement
        if self.connection:
            self.gtypes_disc = connection.gtypes_disc
            self.gtypes_curve = connection.gtypes_curve
            self.types_base.update(connection.types_base)
        self.connection = connection
        self.basic = basic
        self.maj = maj
        self.dialecte = "postgres"
        self.defaut_schema = "public"
        self.role = None

    def _setrole(self):
        """permets de faire un setrole au debut poutr choisir l'utilisateur"""

        return 'SET ROLE "' + self.role + '";' if self.role is not None else ""

    def setbasic(self, mode):
        """mode basic pour les bases de consultation"""
        self.basic = mode
        self.types_db["S"] = "integer"
        self.types_db["BS"] = "bigint"
        if self.schema is not None:
            self.schema.setbasic(mode)

    def conf_en_base(self, conf):
        """valide si une conformite existe en base"""
        return False, False

    def ajuste_nom(self, nom):
        """ sort les caracteres speciaux des noms"""
        nom = re.sub(
            "[" + "".join(sorted(self.remplace.keys())) + "]",
            lambda x: self.remplace[x.group(0)],
            nom,
        )
        nom = self.reserves.get(nom, nom)
        return nom

    def valide_base(self, conf):
        """valide un schema en base"""
        if self.connection:
            confs = self.connection.schemabase.conformites
            if conf in confs:  # la conformite existe en base #on la verifie
                confb = confs[conf.nombase]
                if confb.stock == conf.stock:  # les 2 sont identiques
                    return True, False
                return False, True
        return False, False

    def prepare_conformites(self, nom_conf, schema=None):
        """prepare une conformite et verifie qu'elle fait partie de la base sinon la cree"""
        #        raise
        if schema is None:
            schema = self.schema
        conf = schema.conformites.get(nom_conf)

        if conf is None:
            return False, ""

        conf.nombase = self.ajuste_nom(conf.nom)
        conflist = []
        ctrl = set()
        for j in sorted(list(conf.stock.values()), key=lambda v: v[2]):
            #            if conf.nom=='sig_ident_auteur':
            #                print (conf.nom,j[0],j[3])
            #            if j[3]==2:
            #                print(' mode 2', conf.stock)
            val = j[4].replace("'", "''")
            if len(val) > 62:
                print("postgres: valeur trop longue ", val, " : conformite ignoree", conf.nombase)
                del schema.conformites[nom_conf]
                return False, ""
            if val not in ctrl:
                conflist.append(val)
                ctrl.add(val)
            else:
                print("attention valeur ", val, "en double dans", conf.nombase)

        valide, supp = self.valide_base(conf)
        req = ""

        if supp:
            req = "DROP TYPE " + self.schema_conf + "." + conf.nombase + ";\n"

        req = (
            req
            + "CREATE TYPE "
            + self.schema_conf
            + "."
            + conf.nombase
            + " AS ENUM ('"
            + "','".join(conflist)
            + "');"
        )
        #        print ("preparation",conf.nombase,req)
        return True, req

    def cree_indexes(self, schemaclasse, groupe, nom):
        """creation des indexes"""
        ctr = []
        idx = ["-- ###### creation des indexes #######"]
        # clef primaire:
        #        ctr.append('\tCONSTRAINT '+nom+'_pkey PRIMARY KEY ('+classe.getpkey+'),')
        table = groupe + "." + nom
        if schemaclasse.haspkey:
            ctr.append("\tCONSTRAINT " + nom + "_pkey PRIMARY KEY (" + schemaclasse.getpkey + "),")
        # print ('pkey', '\tCONSTRAINT '+nom+'_pkey PRIMARY KEY ('+schemaclasse.getpkey+'),',schemaclasse.indexes)
        dicindexes = schemaclasse.dicindexes()
        #        if len(dicindexes) > 1:
        #            print("indexes a generer",schemaclasse.nom, sorted(dicindexes.items()))
        for type_index in sorted(dicindexes):
            champs = dicindexes[type_index]
            #            print ('postgres: definition indexes', schemaclasse.nom, type_index,
            #                   '->', champs, schemaclasse.getpkey)
            if type_index[0] == "U":
                ctr.append(
                    "\tCONSTRAINT "
                    + table.replace(".", "_")
                    + "_"
                    + champs.replace(",", "_")
                    + "_key UNIQUE("
                    + champs
                    + "),"
                )
            elif type_index[0] == "K":
                idx.append(
                    "CREATE INDEX fki_"
                    + table.replace(".", "_")
                    + "_"
                    + champs.replace(",", "_")
                    + "_fkey"
                )
                idx.append("\tON " + table)
                idx.append("\tUSING btree (" + champs + ");")
            elif type_index[0] == "I" or type_index[0] == "X":
                idx.append(
                    "CREATE INDEX idx_"
                    + table.replace(".", "_")
                    + "_"
                    + champs.replace(",", "_")
                    + "_key"
                )
                idx.append("\tON " + table)
                idx.append("\tUSING btree (" + champs + ");")
        return ctr, idx

    def cree_fks(self, ident):
        """ cree les definitions des foreign keys """
        if self.basic == "basic":
            return []
        classe = self.schema.classes[ident]

        groupe, nom = self.get_nom_base(ident)
        table = groupe + "." + nom
        fkeys = classe.fkeys
        fkprops = classe.fkprops
        fks = []
        for i in fkeys:
            props = fkprops[i]
            deffk = fkeys[i].split(".")
            #            print('%-40s clef fk:'%(nom), nom+'.'+i, '->', deffk)
            idfk = (deffk[0], deffk[1])
            #            print('identifiant clef etrangere :', idfk)
            if idfk not in self.schema.classes:
                if (
                    self.connection
                    and self.connection.schemabase
                    and idfk not in self.connection.schemabase.classes
                ):
                    print("contrainte externe ignoree ", idfk)
                    continue
            if not fks:
                fks.append("-- ###### definition des clefs etrangeres ####")
            fks.append("ALTER TABLE IF EXISTS " + table)
            fks.append("\tDROP CONSTRAINT IF EXISTS " + nom + "_" + i + ";")
            fks.append("ALTER TABLE IF EXISTS " + table)
            fks.append("\tADD CONSTRAINT " + nom + "_" + i + "_fkey FOREIGN KEY (" + i + ")")
            fks.append(
                "\t\tREFERENCES "
                + deffk[0].replace("FK:", "")
                + "."
                + deffk[1]
                + " ("
                + deffk[2]
                + ") "
                + ("MATCH FULL" if "mf" in props else "MATCH SIMPLE")
            )
            fks.append("\t\tON UPDATE CASCADE" if "uc" in props else "\t\tON UPDATE NO ACTION")
            fks.append("\t\tON DELETE CASCADE" if "dc" in props else "\t\tON DELETE NO ACTION")
            fks.append(
                "\t\tDEFERRABLE INITIALLY DEFERRED; " if "defer" in props else "\t\tNOT DEFERRABLE;"
            )

        return fks

    def cree_comments(self, classe, groupe, nom):
        """ cree les definitions commentaires """
        table = groupe + "." + nom
        # creation des commentaires :
        comments = ["-- ###### definition des commentaires ####"]

        if self.basic == "basic":
            type_table = "T"
        else:
            type_table = classe.type_table.upper()

        al2 = classe.alias.replace("'", "''")
        if al2:
            if type_table == "V":
                comments.append("COMMENT ON VIEW " + table + " IS '" + al2 + "';")
            elif type_table == "M":
                comments.append("COMMENT ON MATERIALIZED VIEW " + table + " IS '" + al2 + "';")
            else:
                comments.append("COMMENT ON TABLE " + table + " IS '" + al2 + "';")

        for j in classe.get_liste_attributs():
            attribut = classe.attributs[j]
            atname = attribut.nom.lower()
            atname = self.reserves.get(atname, atname)
            alias = attribut.alias.replace("'", "''")
            #            print('creation commentaire',atname, alias )
            if alias and alias != al2:
                comments.append(
                    "COMMENT ON COLUMN " + table + "." + atname + " IS '" + alias + "';"
                )
        return comments

    def cree_triggers(self, classe, groupe, nom):
        """ cree les triggers """
        evs = {"B": "BEFORE ", "A": "AFTER ", "I": "INSTEAD "}
        evs2 = {"I": "INSERT ", "D": "DELETE ", "U": "UPDATE ", "T": "TRUNCATE"}
        table = groupe + "." + nom
        if self.basic:
            return []
        trig = ["-- ###### definition des triggers ####"]
        if self.maj:
            atts = {i.lower() for i in classe.get_liste_attributs()}
            trig_std = "auteur" in atts and "date_maj" in atts
            #       for i in atts:
            #           if i.defaut[0:1]=='A:': # definition d'un trigger
            #               liste_triggers[i.nom]=i.defaut[2:]
            if trig_std:
                trig.append("CREATE TRIGGER tr_auteur")
                trig.append("\tBEFORE UPDATE")
                trig.append("\tON " + table)
                trig.append("\tFOR EACH ROW")
                trig.append("\tEXECUTE PROCEDURE admin_sigli.auteur();")
        liste_triggers = classe.triggers
        for i in liste_triggers:
            props = liste_triggers[i].split(",")
            quand = props[0]
            event = props[1]
            if "," in event:
                event = " OR ".join((evs2[e] for e in event.split(",")))
            r_s = props[2]
            pars = props[3:]

            trig.append("CREATE TRIGGER " + i)
            trig.append("\t" + evs[quand] + evs2[event])
            trig.append("\tON " + table)
            trig.append("\tFOR EACH " + "ROW" if r_s == "R" else "STATEMENT")
            trig.append(
                "\tEXECUTE PROCEDURE admin_sigli."
                + i
                + "("
                + ",".join(["'" + j + "'" for j in pars])
                + ");"
            )
        return trig

    def basetriggers(self, ident):
        """ genere automatiquement les triggers a partir des defs en base"""
        groupe, nom = self.get_nom_base(ident)
        deffoncs = dict()
        trig = []
        schema = self.schema
        schemabase =  None
        if self.connection and self.connection.schemabase:
            schemabase = self.connection.schemabase
        specs = schema.elements_specifiques
        if "def_triggers" in specs:
            table = groupe + "." + nom
            ident = (groupe, nom)
            #            print ('definition triggers',schema.elements_specifiques['def_triggers'])
            if ident in specs["def_triggers"]:
                table_trigs = specs["def_triggers"][ident]
                for i in table_trigs:
                    condition, action, declencheur, timing, event = table_trigs[i]
                    fonction = action.replace("EXECUTE PROCEDURE ", "").split("(")[0]
                    if "." in fonction:
                        scf, nomf = fonction.split(".")
                    else:
                        nomf = fonction
                        scf = self.defaut_schema
                        # schema d'admin comprenant routes les fonctions standard
                        fonction_2 = scf + "." + nomf
                        action = action.replace(fonction, fonction_2, 1)
                    idfonc = (scf, nomf)
                    try:
                        deffoncs[idfonc] = specs["def_fonctions_trigger"][idfonc]
                    except KeyError:
                        print("gsql fonction trigger manquante", idfonc)
                        if schemabase:
                            print ("recup def en base")
                            try:
                                deffoncs[idfonc] = schemabase.elements_specifiques[
                                    "def_fonctions_trigger"
                                ][idfonc]
                            except KeyError:
                                print("gsql fonction trigger manquante en base", idfonc)
                    #                        stdnom = "tr_"+nomf+"_"+nom
                    if nomf not in self.stdtriggers:
                        #                            print("detection fonction", nomf, stdnom)
                        if not trig:
                            trig.append(
                                "\n-- ###### definition des triggers" + " en base pour " + table
                            )
                        trig.append("\nDROP TRIGGER IF EXISTS " + i + " ON " + table + ";")
                        trig.append("\nCREATE TRIGGER " + i)
                        trig.append(timing + " " + event)
                        trig.append("ON " + table)
                        trig.append("FOR EACH " + declencheur)
                        if condition:
                            trig.append("WHEN " + condition)
                        trig.append(action + ";")
        return trig, deffoncs

    def get_nom_base(self, ident):
        """ adapte les noms a la base de donnees """
        classe = self.schema.classes[ident]
        nom = self.ajuste_nom(classe.nom.lower())
        groupe = self.ajuste_nom(classe.groupe.lower())
        return groupe, nom

    def get_type_geom(self, schemaclasse):
        """ retourne le type geometrique de la classe precis """
        type_geom = schemaclasse.info["type_geom"]
        if type_geom == "0" or type_geom ==  'indef':
            return "0", False
        arc = schemaclasse.info["courbe"]
        geomt = type_geom
        if geomt in self.typenum:
            geomt = self.typenum[geomt]  # traitement des types numeriques
        if schemaclasse.multigeom:
            geomt = geomt + " MULTIPLE"
        if schemaclasse.info["dimension"] == "3":
            geomt = geomt + " 3D"
        return geomt, arc

    def cretable_dist(self, ident, type_courbes="disc"):
        """ genere le sql de creation des tables distantes """
        schema = self.schema
        classe = schema.classes[ident]
        groupe, nom = self.get_nom_base(ident)
        table = groupe + "." + nom
        atts = classe.get_liste_attributs()
        cretable = []
        cretable.append("\n-- ############## creation table " + table + "###############\n")

        cretable.append("CREATE FOREIGN TABLE " + table + "\n(")
        geomt, arc = self.get_type_geom(classe)
        for j in atts:
            deftype = "text"
            attribut = classe.attributs[j]
            attname = attribut.nom.lower()
            attname = self.reserves.get(attname, attname)
            attype = attribut.type_att
            #            print ('lecture type_attribut',an,at)
            cretable.append("\t" + attname + " " + self.types_db.get(attype, deftype) + ",")
        if geomt and geomt != "ALPHA":
            if type_courbes == "curve" and arc:
                cretable.append("\tgeometrie public." + self.gtypes_curve[geomt])
            else:
                cretable.append("\tgeometrie public." + self.gtypes_disc[geomt])
        if cretable[-1][-1] == ",":
            cretable[-1] = cretable[-1][:-1]  # on degage la virgule en trop
        cretable.append(")")
        serveur, options = "", ""
        if self.connection and self.connection.schemabase:
            schemabase = self.connection.schemabase
            serveur, options = schemabase.elements_specifiques["def_ftables"].get(table)

        cretable.append("SERVER " + serveur)
        opt = [i.replace("=", " '") + "'" for i in options]
        cretable.append("OPTIONS (" + ",".join(opt) + ");")
        return "\n".join(cretable)

    def getgeomsql(self, classe):
        """retourne la definition de la geometrie ici du texre"""
        return "\tgeometrie text,"

    def cree_tables(self, ident, creconf, type_courbes="disc", autopk=False):
        """ genere le sql de creation de table """
        schema = self.schema
        # contraintes de clef etrangeres : on les fait a la fin pour que toutes les tables existent

        classe = schema.classes[ident]
        pkey = classe.getpkey
        groupe, nom = self.get_nom_base(ident)
        #        print("traitement classe ", groupe, nom, 'mode basic :',self.basic)

        table = groupe + "." + nom
        atts = classe.get_liste_attributs()
        geomt, arc = self.get_type_geom(classe)
        cretable = []

        cretable.append(
            "\n-- ############## creation table postgres " + table + "###############\n"
        )

        cretable.append("CREATE TABLE IF NOT EXISTS " + table + "\n(")
        for j in atts:
            seq = False
            deftype = "text"
            nomconf = ""
            sql_conf = ""
            attribut = classe.attributs[j]
            attname = attribut.nom.lower()
            attname = self.reserves.get(attname, attname)
            attype = attribut.type_att
            defaut = None
            if (
                attribut.defaut == "S"
                or attribut.defaut == "BS"
                or (attribut.defaut and attribut.defaut.startswith("S."))
                or attype == "S"
                or attype == "BS"
            ):
                # on est en presence d'un serial'
                defaut = ""
                seq = True
                if self.types_db.get(attype) == "integer":
                    attype = "S"  # sequence
                elif self.types_db.get(attype) == "bigint":
                    attype = "BS"  # sequence
                if attype not in {"S", "BS"}:
                    print("type serial incompatible avec le type", attype, attribut.defaut)
                    seq = False
            conf = attribut.conformite
            #            print ('lecture type_attribut',attname,attype,conf.nom if conf else '')

            if conf:
                conf.nombase = self.ajuste_nom(conf.nom)
                attype = conf.nom
                #                attype = self.ajuste_nom(conf.nom)
                if self.basic == "basic":
                    attype = "T"
            #            print ('conv type_attribut',attname,attype,schema.conformites.keys())

            if re.search(r"^t[0-9]+$", attype):
                attype = "T"
            if re.search(r"^e[1-6]s*$", attype):
                attype = "E"
            if re.search(r"^e[0-9]+_[0-9]+$", attype):
                attype = "E"
            if re.search(r"^e[7-9]s*$", attype):
                attype = "EL"
            # on essaye de gerer les clefs et les sequences les types et les defauts:
            #            print ("gensql, attribut ",an,at,conf)

            if attname == "gid" and not pkey:
                # on a pas defini la clef par defaut c'est le gid
                if autopk:
                    classe.setpkey([attname])
                    pkey = classe.getpkey

                    if (
                        self.types_db.get(attype) == "integer"
                        or self.types_db.get(attype) == "bigint"
                    ):
                        seq = True

            if pkey == attname:
                if self.types_db.get(attype) == "integer" or self.types_db.get(attype) == "bigint":
                    seq = True
            if attname == "auteur":
                if not attype:
                    attype = "T"
                if attype == "T" and not self.basic:
                    defaut = " DEFAULT current_user"
            if attname == "date_creation" or attname == "date_maj":
                if not attype:
                    attype = "D"
                if attype == "D" and not self.basic:
                    defaut = " DEFAULT current_timestamp"
            elif attype in schema.conformites and self.basic != "basic":

                schema.conformites.get(attype).nombase = self.ajuste_nom(attype)
                nomconf = schema.conformites.get(
                    attype
                ).nombase  # on a pu adapter le nom a postgres
                #                nomconf = self.ajuste_nom(nomconf)
                #                print ('detection conformite', attname, attype, nomconf)

                if attype not in creconf:
                    valide, sql_conf = self.prepare_conformites(attype, schema=schema)
                    if valide:
                        deftype = self.schema_conf + "." + nomconf
                    else:
                        print("conformite non trouvee", attype)
                else:
                    deftype = self.schema_conf + "." + nomconf
            #                    raise
            elif (
                self.connection
                and self.connection.schemabase
                and attype in self.connection.schemabase.conformites
            ):
                valide, sql_conf = self.prepare_conformites(attype)
                if valide:
                    nomconf = schema.conformites.get(attype).nombase
                    # on a pu adapter le nom a postgres
                    deftype = self.schema_conf + "." + nomconf
            else:
                pass
            # gestion des defauts
            if defaut is None:
                if attype == "T":
                    if attribut.defaut and attribut.defaut.startswith("="):
                        predef = attribut.defaut[1:].replace('"', "'")
                        defaut = " DEFAULT " + predef
            if defaut is None:
                defaut = ""
            if self.types_db.get(attype) == "integer":
                #                print ('test pk',attribut.nom, classe.getpkey)
                if seq or pkey == attribut.nom and not self.basic:
                    attype = "S"
                    defaut = ""
            elif self.types_db.get(attype) == "bigint":
                if seq or pkey == attribut.nom and not self.basic:
                    attype = "BS"
                    defaut = ""
            if attype not in self.types_db and not nomconf:
                print("type inconnu", attype, deftype, "defaut", attype in self.schema.conformites)
            type_sortie = self.types_db.get(attype, deftype)
            if type_sortie == "numeric" and attribut.taille:
                type_sortie = "numeric" + "(" + str(attribut.taille) + "," + str(attribut.dec) if attribut.dec is not None else '0' + ")"
            elif type_sortie == "text" and attribut.taille:
                type_sortie = "varchar" + "(" + str(attribut.taille) + ")"
            cretable.append("\t" + attname + " " + type_sortie + defaut + ",")
            if sql_conf and self.basic != "basic":
                creconf[nomconf] = sql_conf
        if geomt != "0":
            cretable.append(self.getgeomsql(classe))  # la on est pas geometrique on gere en texte

        # contraintes et indexes
        ctr, idx = self.cree_indexes(classe, groupe, nom)

        if ctr:
            cretable.extend(ctr)

        if cretable[-1].endswith(","):
            cretable[-1] = cretable[-1][:-1]
        cretable.append(")")
        cretable.append("WITH (OIDS=FALSE);")
        # on choisit les bons indexes:
        cretable.extend(idx)
        if not self.basic:
            cretable.extend(self.cree_triggers(classe, groupe, nom))
        cretable.extend(self.cree_comments(classe, groupe, nom))

        # creation des commentaires :

        return "\n".join(cretable)

    def get_vues_base(self, liste):
        """ retourne la liste des vues dont on a la definition en base"""
        try:
            vues_schema = self.schema.elements_specifiques["def_vues"]
            vues_utilisees = {i: vues_schema[i] for i in liste if i in vues_schema}
            #                    and self.schema.classes[i].type_table in 'mv'}
            print(
                "get_vues_base: ",
                len(vues_utilisees),
                " definies dans le schema",
                self.schema.nom,
                len(vues_schema),
            )
            return vues_utilisees
        except (AttributeError, KeyError):
            print("get_vues_base: pas de vues definies dans le schema", self.schema.nom)
            pass
        try:
            vues_base = self.connection.schemabase.elements_specifiques["def_vues"]
        except (AttributeError, KeyError):
            return set()
        if self.connection and self.connection.schemabase and not self.basic:
            return {
                i: vues_base[i]
                for i in liste
                if i in vues_base and self.schema.classes[i].type_table in "mv"
            }
        return set()

    def creschemas(self, liste):
        """creation des schemas"""
        schemas = set()
        for ident in liste:
            groupe, _ = self.get_nom_base(ident)
            schemas.add(groupe)
        creschema = ["CREATE SCHEMA IF NOT EXISTS " + i + ";" for i in schemas]
        dropschema = ["DROP SCHEMA IF EXISTS " + i + ";" for i in schemas]
        dropschemac = ["DROP SCHEMA IF EXISTS " + i + " CASCADE;" for i in schemas]
        creschema.insert(0, self._setrole())
        dropschema.insert(0, self._setrole())
        dropschemac.insert(0, self._setrole())
        return creschema, dropschema, dropschemac

    def droptables(self, liste):
        """ nettoyage """
        drop = []
        for ident in liste:
            groupe, nom = self.get_nom_base(ident)
            table = groupe + "." + nom
            drop.append("DROP TABLE IF EXISTS " + table + ";")
        drop.reverse() # on inverse l'ordre de destruction par rapport a la creation
        return drop

    def dropvues(self, liste):
        """ nettoyage """
        drop = []
        if self.connection and self.connection.schemabase:
            listevues = [self.get_nom_base(ident) for ident in liste]
            schemabase = self.connection.schemabase
            schemabase.elements_specifiques["postgres"].viewsorter(listevues)
            listevues.reverse()  # on detruit a l'envers de la creation
            for ident in listevues:
                drop.append(schemabase.elements_specifiques["postgres"].dropvue(ident))
        return drop

    def dropf_tables(self, liste):
        """suppression de foreign tables"""
        drop = []
        for ident in liste:
            groupe, nom = self.get_nom_base(ident)
            table = groupe + "." + nom
            drop.append("DROP FOREIGN TABLE IF EXISTS " + table + ";")
        return drop

    def dropconf(self, liste_confs):
        """sql de suppression des types """
        return ["DROP TYPE IF EXISTS " + self.schema_conf + "." + i + ";" for i in liste_confs]

    # scripts de creation de tables
    def sio_crestyle(self, liste=None):
        """ genere les styles de saisie"""
        return []

    def sio_cretable(self, cod="utf-8", liste=None, autopk=False, role=None):
        """sortie des sql pour la creation des tables"""
        creconf = dict()
        #        dbcod = cod
        #        if self.connection:
        #            dbcod = self.connection.codecinfo.get(cod, cod)
        #        codecinfo = "--########### encodage fichier "+cod+'->'+dbcod+' ###(controle éèàç)####\n'
        idschema = (
            "-- ############ nom:"
            + self.schema.nom
            + " ## type_base:"
            + self.dialecte
            + " ## mode:"
            + ("basique" if self.basic else "std")
            + " ###############\n"
        )
        self.role = role
        if liste is None:
            liste = sorted([i for i in self.schema.classes if self.schema.classes[i].a_sortir])
        vues_base = self.get_vues_base(liste)
        def_speciales = set(vues_base)
        liste_ftables = [
            i for i in liste if self.schema.classes[i].type_table.upper() == "F" and not self.basic
        ]
        def_speciales |= set(liste_ftables)
        liste_tables = [i for i in liste if i not in def_speciales]

        #       for i in liste_tables:
        #            print('type :',i,self.schema.classes[i].type_table)
        print(
            "postgres definition de tables a sortir:",
            self.schema.nom,
            len(liste_tables),
            self.dialecte,
        )
        cretables = [
            idschema,
            self._setrole(),
            "\n-- ########### definition des tables ###############\n",
        ]
        cretables.extend(
            list([self.cree_tables(ident, creconf, autopk=autopk) for ident in liste_tables])
        )
        if not self.basic:
            if liste_ftables:
                cretables.append("\n-- ########### definition des tables distantes ############\n")
                cretables.extend(list([self.cretable_dist(ident) for ident in liste_ftables]))
            if vues_base:
                cretables.append("\n-- ########### definition des vues ###############\n")
                cretables.extend(self.def_vues(liste, vues_base))

            else:
                print("pas de vues a sortir")
            for ident in liste:
                cretables.extend(self.cree_fks(ident))
            foncdefs = dict()
            trigdefs = []
            for ident in liste:
                trigs, foncs = self.basetriggers(ident)
                #                print ('definition triggers ', ident,len(trigs),len(foncs))
                trigdefs.extend(trigs)
                foncdefs.update(foncs)
            cretables.append("\n-- ########### definition des fonctions triggers ###############\n")
            cretables.extend([i.replace("\r", "") + ";" for i in foncdefs.values()])
            cretables.append("\n-- ########### definition des triggers ###############\n")

            cretables.extend(trigdefs)
        droptables = [self._setrole()]
        droptables.extend(self.drop_vues(liste, vues_base))
        droptables.extend(self.dropf_tables(liste_ftables))
        droptables.extend(self.droptables(liste_tables))

        creconfs = list(creconf.values())
        dropconfs = self.dropconf(creconf.keys())
        creconfs.insert(0, self._setrole())
        dropconfs.insert(0, self._setrole())
        #        creconfs.insert(0, codecinfo)
        return cretables, droptables, creconfs, dropconfs

    def sio_creschema(self, cod="utf-8", liste=None):
        """sortie des sql pour la creation des schemas de base"""
        if liste is None:
            liste = [i for i in self.schema.classes if self.schema.classes[i].a_sortir]
        #        print ('------------------------------sio creschema',liste)
        return self.creschemas(liste)

    #  ===============traitement deselements specifiques================

    def referenced(self, liste, vues_base, niveau, niv_ref):
        """determine si une vue est referencee"""
        trouve = 0
        for ident in liste:  # on essaye de savoir si elle est referencee
            if niveau[ident] == niv_ref:
                schema, table = ident
                for j in liste:
                    #                    if j == ident: # on evite le pb des vues recursives
                    #                        continue
                    if (
                        niveau[j] >= niv_ref
                        and j != ident
                        and j in vues_base
                        and table in vues_base[j][0]
                    ):
                        niveau[ident] += 1
                        trouve = 1
                        break
        return trouve

    def viewsorter(self, liste, vues_base):
        """trie la liste des vues pour tenir compte des references"""
        niveau = {i: 0 for i in liste}
        niv_ref = 0
        while self.referenced(liste, vues_base, niveau, niv_ref):
            niv_ref += 1
        #                print("niveau atteint", niv_ref)
        liste.sort(key=niveau.get, reverse=True)
        return niveau

    def dropvue(self, ident, is_mat):
        """ nettoyage """
        if is_mat:
            return "DROP MATERIALIZED VIEW IF EXISTS " + ".".join(ident) + ";"
        return "DROP VIEW IF EXISTS " + ".".join(ident) + ";"

    def drop_vues(self, liste, vues_base):
        """script de suppression de vues"""
        vues_sql = ["--gestion des vues en base \n", "--menage---"]
        self.viewsorter(liste, vues_base)
        liste_d = liste[::-1]
        for ident in liste_d:
            if ident in vues_base:
                vues_sql.append(self.dropvue(ident, vues_base[ident][1]))
        return vues_sql

    def vue_to_sql(self, ident, definition, is_mat):
        """creation des vues """
        if is_mat:
            return (
                "CREATE MATERIALIZED VIEW "
                + ".".join(ident)
                + " AS\n"
                + definition[:-1]
                + "\n WITH NO DATA;\n"
            )
        return "CREATE OR REPLACE VIEW " + ".".join(ident) + " AS\n" + definition

    def def_vues(self, liste, vues_base):
        """fournit les definitione de vues lues en base"""
        vues_sql = ["--gestion des vues en base \n", "--menage"]
        niveau = self.viewsorter(liste, vues_base)
        liste_d = liste[::-1]
        for ident in liste_d:
            if ident in vues_base:
                vues_sql.append(self.dropvue(ident, vues_base[ident][1]))
        vues_sql.append
        for ident in liste:
            if ident in vues_base:
                vues_sql.append(
                    "\n-- "
                    + str(ident)
                    + str(niveau[ident])
                    + " definition vue generee a partir de la base\n"
                )
                vues_sql.append(self.vue_to_sql(ident, *vues_base[ident]))
                groupe, nom = ident
                classe = self.schema.classes[ident]
                vues_sql.extend(self.cree_comments(classe, groupe, nom))

        print("definition de vues generees", len(vues_base), "->", len(vues_sql))
        #        print ('liste vues','\n'.join([str(i)+':'+str(niveau[i]) for i in listevues]))

        return vues_sql

    def def_fonction_triggers(self, ident, ftrigs):
        """ cree les fonctions trigger necessaires """

        return ftrigs.get(ident, "")

    # ============== gestionnaire de reinitialisation de la base===============

    @staticmethod
    def _commande_geom_strict(niveau, classe, strict, gtyp="0", dim="2", courbe=False):
        """ manipulation de la geometrie pour la discretisation des courbes """
        return ""

    @staticmethod
    def _commande_geom_courbe(niveau, classe, gtyp="0", dim="2", courbe=False):
        """ manipulation de la geometrie pour la discretisation des courbes """
        return ""

    @staticmethod
    def _commande_index_gist(niveau, classe, drop):
        """ suppression des index geometriques pour accelerer le chargement"""
        return ""

    @staticmethod
    def _commande_reinit(niveau, classe, delete):
        """commande de reinitialisation de la table"""

        #        prefix = 'TRUNCATE TABLE "'+niveau.lower()+'"."'+classe.lower()+'";\n'
        return (
            ("DELETE FROM " if delete else "TRUNCATE TABLE ")
            + niveau.lower()
            + "."
            + classe.lower()
            + ";\n"
        )

    @staticmethod
    def _commande_sequence(niveau, classe):
        """ cree une commande de reinitialisation des sequences
            pour le moment necessite la fonction dans admin_sigli"""
        # TODO remplacer la fonction qui fait le job par du SQL basique
        return (
            "SELECT admin_sigli.ajuste_sequence('"
            + niveau.lower()
            + "','"
            + classe.lower()
            + "');\n"
        )

    @staticmethod
    def _commande_trigger(niveau, classe, valide):
        """ cree une commande de reinitialisation des sequences"""
        return (
            "ALTER TABLE "
            + niveau.lower()
            + "."
            + classe.lower()
            + (" ENABLE " if valide else " DISABLE ")
            + "TRIGGER USER;\n"
        )

    def prefix_charge(self, niveau, classe, reinit, gtyp="0", dim="2"):
        """ grere toutes les reinitialisations eventuelles
        G: devalide les triggers T: Truncate D: delete S: ajuste les sequences
        I: gere les indices geometriques C: passe en courbe L: discretise"""
        prefix = ""
        if reinit is None:
            reinit = ""
        if "G" in reinit:  # on devalide les triggers
            prefix = prefix + self._commande_trigger(niveau, classe, False)
        if "T" in reinit:  # on reinitialise les tables
            prefix = prefix + self._commande_reinit(niveau, classe, False)
        if "D" in reinit:  # on reinitialise les tables
            prefix = prefix + self._commande_reinit(niveau, classe, True)
        if "S" in reinit:
            prefix = prefix + self._commande_sequence(niveau, classe)
        if "I" in reinit and gtyp > "0":
            prefix = prefix + self._commande_index_gist(niveau, classe, True)
        if ("L" in reinit or "C" in reinit) and gtyp in "23":  # ouverture de la geometrie'
            prefix = prefix + self._commande_geom_strict(niveau, classe, False, dim=dim)
        return prefix

    def tail_charge(self, niveau, classe, reinit, gtyp="0", dim="2", courbe=False):
        """ menage de fin de chargement """
        prefix = ""
        if "L" in reinit and gtyp in "23":  # discretisation'
            prefix = prefix + self._commande_geom_strict(niveau, classe, True, gtyp=gtyp, dim=dim)
        if "C" in reinit and gtyp in "23":  # discretisation'
            prefix = prefix + self._commande_geom_strict(
                niveau, classe, True, gtyp=gtyp, dim=dim, courbe=courbe
            )
        if "S" in reinit:
            prefix = prefix + self._commande_sequence(niveau, classe)
        if "I" in reinit and gtyp > "0":
            prefix = prefix + self._commande_index_gist(niveau, classe, False)
        if "G" in reinit:
            prefix = prefix + self._commande_trigger(niveau, classe, True)

        return prefix
