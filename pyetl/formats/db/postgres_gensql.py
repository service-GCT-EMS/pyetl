# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 10:00:04 2018
''' generateur de sql pour la base postgres '''
@author: 89965
"""
# import os
import re
import logging
from time import strftime, time

# import subprocess
from .gensql import DbGenSql

# from .postgres import RESERVES, GTYPES_DISC, GTYPES_CURVE, TYPES_A
RESERVES = {"analyse": "analyse_pb", "type": "type_entite", "as": "ass"}
SCHEMA_CONF = "public"

LOGGER = logging.getLogger(__name__)


def _nomsql(niveau, classe):
    """retourne un identifiant standard sql"""
    return niveau.lower() + "." + classe.lower()


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
            "DS": "date",
            "ds": "date",
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
            "J": "json",
            "XML": "XML",
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
        """sort les caracteres speciaux des noms"""
        nom = re.sub(
            "[" + "".join(sorted(self.remplace.keys())) + "]",
            lambda x: self.remplace[x.group(0)],
            nom,
        )
        nom = self.reserves.get(nom, nom)
        return nom.lower()

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
                LOGGER.warning(
                    "conformite %s ignoree: valeur trop longue %s", conf.nombase, val
                )
                # print(
                #     "postgres: valeur trop longue ",
                #     val,
                #     " : conformite ignoree",
                #     conf.nombase,
                # )
                del schema.conformites[nom_conf]
                return False, ""
            if val not in ctrl:
                conflist.append(val)
                ctrl.add(val)
            else:
                LOGGER.warning(
                    "attention valeur %s en double dans %s", val, conf.nombase
                )
                # print("attention valeur ", val, "en double dans", conf.nombase)

        valide, supp = self.valide_base(conf)
        req = ""

        if supp:
            req = "DROP TYPE " + self.schema_conf + "." + conf.nombase + ";\n"

        req = (
            req
            + ("--" if len(conflist) == 1 and conflist[0] == "" else "")
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
            ctr.append(
                "\tCONSTRAINT "
                + nom
                + "_pkey PRIMARY KEY ("
                + schemaclasse.getpkey.lower()
                + "),"
            )
        # print ('pkey', '\tCONSTRAINT '+nom+'_pkey PRIMARY KEY ('+schemaclasse.getpkey+'),',schemaclasse.indexes)
        dicindexes = schemaclasse.dicindexes()
        #        if len(dicindexes) > 1:
        #            print("indexes a generer",schemaclasse.nom, sorted(dicindexes.items()))
        for type_index in sorted(dicindexes):
            champs = dicindexes[type_index].lower()
            #            print ('postgres: definition indexes', schemaclasse.nom, type_index,
            #                   '->', champs, schemaclasse.getpkey)
            if type_index[0] == "U":
                if schemaclasse.type_table == "t":
                    ctr.append(
                        "\tCONSTRAINT "
                        + nom.replace(".", "_")
                        + "_"
                        + (champs.replace(",", "_"))
                        + "_key UNIQUE("
                        + champs
                        + "),"
                    )
                else:
                    idx.append(
                        "CREATE UNIQUE INDEX uid_"
                        + nom.replace(".", "_")
                        + "_uniq_"
                        + (champs.replace(",", "_"))
                    )
                    idx.append("\tON " + table)
                    idx.append("\tUSING btree (" + champs + ");")

            elif type_index[0] == "K":
                idx.append(
                    "CREATE INDEX fki_"
                    + nom.replace(".", "_")
                    + "_"
                    + (champs.replace(",", "_"))
                    + "_fkey"
                )
                idx.append("\tON " + table)
                idx.append("\tUSING btree (" + champs + ");")
            elif type_index[0] == "I" or type_index[0] == "X":
                idx.append(
                    "CREATE INDEX idx_"
                    + nom.replace(".", "_")
                    + "_"
                    + champs.replace(",", "_")
                    + "_key"
                )
                idx.append("\tON " + table)
                idx.append("\tUSING btree (" + champs + ");")
        return ctr, idx

    def cree_fks(self, ident):
        """cree les definitions des foreign keys"""
        if self.basic == "basic":
            return []
        classe = self.schema.classes[ident]

        groupe, nom = self.get_nom_base(ident)
        table = groupe + "." + nom
        fkeys = classe.fkeys if classe.fkeys else []
        fkprops = classe.fkprops
        fks = []
        for i in fkeys:
            props = fkprops[i] or []
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
            fks.append("ALTER TABLE IF EXISTS " + table.lower())
            fks.append(
                "\tDROP CONSTRAINT IF EXISTS " + nom.lower() + "_" + i.lower() + ";"
            )
            fks.append("ALTER TABLE IF EXISTS " + table.lower())
            fks.append(
                "\tADD CONSTRAINT "
                + nom.lower()
                + "_"
                + i.lower()
                + "_fkey FOREIGN KEY ("
                + i.lower()
                + ")"
            )
            fks.append(
                "\t\tREFERENCES "
                + (deffk[0].replace("FK:", "")).lower()
                + "."
                + deffk[1].lower()
                + " ("
                + deffk[2].lower()
                + ") "
                + ("MATCH FULL" if "mf" in props else "MATCH SIMPLE")
            )
            if "uc" in props:
                fks.append("\t\tON UPDATE CASCADE")
            elif "un" in props:
                fks.append("\t\tON UPDATE SET NULL")
            elif "ud" in props:
                fks.append("\t\tON UPDATE SET DEFAULT")
            elif "ur" in props:
                fks.append("\t\tON UPDATE RESTRICT")
            elif "ua" in props:
                fks.append("\t\tON UPDATE NO ACTION")
            if "dc" in props:
                fks.append("\t\tON DELETE CASCADE")
            elif "dn" in props:
                fks.append("\t\tON DELETE SET NULL")
            elif "dd" in props:
                fks.append("\t\tON DELETE SET DEFAULT")
            elif "dr" in props:
                fks.append("\t\tON DELETE RESTRICT")
            elif "da" in props:
                fks.append("\t\tON DELETE NO ACTION")
            fks.append(
                "\t\tDEFERRABLE INITIALLY DEFERRED; "
                if "defer" in props
                else "\t\tNOT DEFERRABLE;"
            )

        return fks

    def cree_comments(self, classe, groupe, nom):
        """cree les definitions commentaires"""
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
                comments.append(
                    "COMMENT ON VIEW " + table.lower() + " IS '" + al2 + "';"
                )
            elif type_table == "M":
                comments.append(
                    "COMMENT ON MATERIALIZED VIEW "
                    + table.lower()
                    + " IS '"
                    + al2
                    + "';"
                )
            else:
                comments.append(
                    "COMMENT ON TABLE " + table.lower() + " IS '" + al2 + "';"
                )

        for j in classe.get_liste_attributs():
            attribut = classe.attributs[j]
            atname = attribut.nom.lower()
            atname = self.reserves.get(atname, atname)
            alias = attribut.alias.replace("'", "''")
            #            print('creation commentaire',atname, alias )
            if alias and alias != al2:
                comments.append(
                    "COMMENT ON COLUMN "
                    + table.lower()
                    + "."
                    + atname.lower()
                    + " IS '"
                    + alias
                    + "';"
                )
        return comments

    def cree_sql_trigger(self, nom, table, trigdef):
        """genere le sql d'un trigger"""
        (
            type_trigger,
            action,
            declencheur,
            timing,
            event,
            colonnes,
            condition,
            sql,
        ) = trigdef
        fonction = action
        trig = []
        # print ('sql_trigger',fonction)
        if "." in action:
            scf, nomf = fonction.split(".", 1)
        else:
            nomf = fonction
            scf = self.defaut_schema
            # schema d'admin comprenant routes les fonctions standard
            fonction_2 = scf + "." + nomf
            action_2 = action.replace(fonction, fonction_2, 1)
            sql = sql.replace(action, action_2)
            action = action_2
        if nomf not in self.stdtriggers:
            trig = [
                '\nDROP TRIGGER IF EXISTS "'
                + nom.lower()
                + '" ON "'
                + table.lower()
                + '";'
            ]
            if sql:
                trig.append(sql + ";")
            else:
                trig.append("\nCREATE " + type_trigger + ' "' + nom.lower() + '" ')
                trig.append(
                    timing + " " + event + (" OF " + colonnes.lower())
                    if colonnes
                    else ""
                )
                trig.append("ON " + table.lower())
                trig.append("FOR EACH " + declencheur)
                if condition:
                    trig.append("WHEN " + condition)
                trig.append("EXECUTE PROCEDURE" + action + ";")
        idfonc = (scf, nomf.split("(")[0])
        return idfonc, trig

    def cree_triggers(self, classe, groupe, nom):
        """cree les triggers"""
        evs = {"B": "BEFORE ", "A": "AFTER ", "I": "INSTEAD OF"}
        evs2 = {"I": "INSERT ", "D": "DELETE ", "U": "UPDATE ", "T": "TRUNCATE"}
        ttype = {"T": "TRIGGER", "C": "CONSTRAINT"}
        decl = {"R": "ROW", "S": "STATEMENT"}
        table = groupe + "." + nom
        if self.basic:
            return []
        trig = ["-- ###### definition des triggers ####"]

        # liste_triggers = classe.triggers
        # for i in liste_triggers:
        #     (
        #         type_trigger,
        #         action,
        #         declencheur,
        #         timing,
        #         event,
        #         colonnes,
        #         condition,
        #         sql,
        #     ) = liste_triggers[i].split(",")
        #     trigdef = (
        #         ttype[type_trigger],
        #         action,
        #         decl[declencheur],
        #         evs[timing],
        #         evs2[event],
        #         colonnes,
        #         condition,
        #         sql,
        #     )
        #     idfonc, trigsql = self.cree_sql_trigger(i, table, trigdef)
        #     trig.extend(trigsql)
        return trig

    def basetriggers(self, ident):
        """genere automatiquement les triggers a partir des defs en base"""
        groupe, nom = self.get_nom_base(ident)
        deffoncs = dict()
        trig = []
        schema = self.schema
        schemabase = None
        if self.connection and self.connection.schemabase:
            schemabase = self.connection.schemabase
        specs = schema.elements_specifiques
        if "def_triggers" in specs:
            table = groupe + "." + nom
            ident = (groupe, nom)
            # print ('definition triggers',schema.elements_specifiques['def_triggers'])
            # print ("recherche trigger", ident,specs["def_triggers"].keys() )
            if ident in specs["def_triggers"][1]:
                table_trigs = specs["def_triggers"][1][ident]
                print("traitement trigger", table_trigs)
                for i in table_trigs:
                    idfonc, trigsql = self.cree_sql_trigger(i, table, table_trigs[i])
                    try:
                        deffoncs[idfonc] = specs["def_fonctions_trigger"][1][idfonc]
                    except KeyError:
                        print(
                            "gsql fonction trigger manquante en base",
                            idfonc,
                            sorted(deffoncs.keys()),
                        )
                        if schemabase:
                            print("recup def en base")
                            try:
                                deffoncs[idfonc] = schemabase.elements_specifiques[
                                    "def_fonctions_trigger"
                                ][idfonc]
                            except KeyError:
                                print(
                                    "gsql fonction trigger manquante en base",
                                    idfonc,
                                    sorted(deffoncs.keys()),
                                )
                    #                        stdnom = "tr_"+nomf+"_"+nom
                    trig.extend(trigsql)
        return trig, deffoncs

    def get_nom_base(self, ident):
        """adapte les noms a la base de donnees"""
        classe = self.schema.classes[ident]
        nom = self.ajuste_nom(classe.nom.lower())
        groupe = self.ajuste_nom(classe.groupe.lower())
        return groupe, nom

    def get_type_geom(self, schemaclasse):
        """retourne le type geometrique de la classe precis"""
        type_geom = schemaclasse.info["type_geom"]
        if type_geom == "0" or type_geom == "indef":
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
        """genere le sql de creation des tables distantes"""
        schema = self.schema
        classe = schema.classes[ident]
        groupe, nom = self.get_nom_base(ident)
        table = groupe + "." + nom
        atts = classe.get_liste_attributs()
        cretable = []
        cretable.append(
            "\n-- ############## creation table " + table + "###############\n"
        )

        cretable.append("CREATE FOREIGN TABLE " + table + "\n(")
        geomt, arc = self.get_type_geom(classe)
        for j in atts:
            deftype = "text"
            attribut = classe.attributs[j]
            attname = attribut.nom.lower()
            attname = self.reserves.get(attname, attname)
            attype = attribut.type_att
            #            print ('lecture type_attribut',an,at)
            cretable.append(
                "\t" + attname + " " + self.types_db.get(attype, deftype) + ","
            )
        if geomt and geomt != "ALPHA" and geomt != "0":
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
            entete, ftables = schemabase.elements_specifiques["def_ftables"]
            serveur, options = ftables.get(table)
        print("tables_distantes", serveur, options)
        cretable.append("SERVER " + serveur)
        opt = [i.replace("=", " '") + "'" for i in options.split(",")]
        print("tables_distantes", serveur, opt)

        cretable.append("OPTIONS (" + ",".join(opt) + ");")
        return "\n".join(cretable)

    def getgeomsql(self, classe):
        """retourne la definition de la geometrie ici du texre"""
        return "\tgeometrie text,"

    def cree_tables(self, ident, creconf, type_courbes="disc", autopk=False):
        """genere le sql de creation de table"""
        schema = self.schema
        # contraintes de clef etrangeres : on les fait a la fin pour que toutes les tables existent
        autoserial = True
        refcontext = self.regle_ref if self.regle_ref else self.stock_param
        if refcontext:
            autoserial = not refcontext.getvar("autoserial") == "0"
        classe = schema.classes[ident]
        pkey = classe.getpkey
        groupe, nom = self.get_nom_base(ident)
        #        print("traitement classe ", groupe, nom, 'mode basic :',self.basic)

        table = groupe + "." + nom
        atts = classe.get_liste_attributs()
        geomt, arc = self.get_type_geom(classe)
        cretable = []
        if classe.type_table in {"vmf"} and not self.basic:
            return
            # c est une vue une vue materialisee ou une table etrangere

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
            defaut = attribut.defaut
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
                    print(
                        "type serial incompatible avec le type", attype, attribut.defaut
                    )
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

            if re.search(r"^t[0-9]+$", str(attype)):
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

            if pkey == attname and autoserial:
                if (
                    self.types_db.get(attype) == "integer"
                    or self.types_db.get(attype) == "bigint"
                ):
                    seq = True
            if attname == "auteur":
                if not attype:
                    attype = "T"
                if attype == "T" and not self.basic:
                    defaut = " DEFAULT current_user"
                # print("cretable auteur", attype, self.basic, defaut)
            if attname == "date_creation" or attname == "date_maj":
                if not attype:
                    attype = "D"
                if attype == "D" and not self.basic:
                    defaut = " DEFAULT current_timestamp"
            elif attype in schema.conformites and self.basic != "basic":
                schema.conformites.get(attype).nombase = self.ajuste_nom(attype)
                nomconf = schema.conformites.get(attype).nombase
                # on a pu adapter le nom a postgres
                #                nomconf = self.ajuste_nom(nomconf)
                #                print ('detection conformite', attname, attype, nomconf)

                if attype not in creconf:
                    valide, sql_conf = self.prepare_conformites(attype, schema=schema)
                    if valide:
                        deftype = self.schema_conf + "." + nomconf
                    else:
                        LOGGER.warning("conformite non trouvee %s", attype)
                        # print("conformite non trouvee", attype)
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
            # if attribut.defaut:
            # print ('gestion des defauts',defaut,attype,nomconf,attribut.defaut)
            if defaut:
                if attype == "T":
                    if defaut.startswith("="):
                        predef = defaut[1:].replace('"', "'")
                        if "::" in predef:  # il y a un typecast, on force le schema
                            nom, typedef = predef.split("::", 1)
                            if "." in typedef:
                                typedef = (
                                    self.schema_conf + "." + typedef.split(".", 1)[1]
                                )
                            if nom.startswith("'") or nom.startswith('"'):
                                nom = nom[1:]
                            if nom.endswith("'") or nom.endswith('"'):
                                nom = nom[:1]
                            predef = "'" + nom + "'::" + typedef
                        defaut = " DEFAULT " + predef
                if nomconf:
                    if "::" in defaut:  # il y a un typecast
                        val, typedef = defaut.split("::", 1)
                        if "." in typedef:
                            ts, tn = typedef.split(".")
                            if ts != classe.identclasse[0]:
                                ts = self.schema_conf
                            typedef = ts + "." + tn
                        else:
                            typedef = self.schema_conf + "." + typedef
                    else:
                        typedef = self.schema_conf + "." + nomconf
                    defaut = " DEFAULT " + defaut + "::" + typedef
                else:
                    if defaut.startswith("'") or defaut.startswith('"'):
                        defaut = defaut[1:]
                    if defaut.endswith("'") or defaut.endswith('"'):
                        defaut = defaut[:1]
                    if defaut.startswith(" DEFAULT"):
                        pass
                    elif defaut=='curent_user' or defaut=='current_timestamp':
                        defaut = " DEFAULT " + defaut
                    else:
                        defaut = " DEFAULT '" + defaut + "'"
            elif defaut is None:
                defaut = ""
            if self.types_db.get(attype) == "integer":
                #                print ('test pk',attribut.nom, classe.getpkey)
                if seq and not self.basic:
                    attype = "S"
                    defaut = ""
            elif self.types_db.get(attype) == "bigint":
                if seq and not self.basic:
                    attype = "BS"
                    defaut = ""
            if attype not in self.types_db and not nomconf:
                LOGGER.warning(
                    "postgres: %s:%s.%s type inconnu %s defaut %s",
                    self.schema.nom,
                    table,
                    attname,
                    attype,
                    deftype,
                )
                # print(
                #     "type inconnu",
                #     attype,
                #     deftype,
                #     "defaut",
                #     attype in self.schema.conformites,
                # )
            type_sortie = self.types_db.get(attype, deftype)
            if type_sortie == "numeric" and attribut.taille > 0:
                type_sortie = (
                    "numeric"
                    + "("
                    + str(attribut.taille)
                    + ("," + str(attribut.dec) if attribut.dec is not None else "0")
                    + ")"
                )
            elif type_sortie == "text" and (
                attribut.taille > 0
                and self.regle_ref
                and self.regle_ref.istrue("keepvarchar")
            ):
                type_sortie = "varchar" + "(" + str(attribut.taille) + ")"
            # print("creation attribut", attname, type_sortie, attribut.multiple)
            if attribut.multiple:
                type_sortie = type_sortie + "[]"
            cretable.append("\t" + attname + " " + type_sortie + defaut + ",")
            # if defaut:
            #     print('sql_genere',cretable[-1])
            if sql_conf and self.basic != "basic":
                creconf[nomconf] = sql_conf
        if geomt != "0":
            cretable.append(
                self.getgeomsql(classe)
            )  # la on est pas geometrique on gere en texte

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
        """retourne la liste des vues dont on a la definition en base"""
        # self.schema.printelements_specifiques()
        try:
            vues_schema = self.schema.elements_specifiques["def_vues"][1]
            vues_utilisees = {i: vues_schema[i] for i in liste if i in vues_schema}
            #                    and self.schema.classes[i].type_table in 'mv'}
            LOGGER.info(
                "%d vues utilisees definies dans le schema %s sur %d",
                len(vues_utilisees),
                self.schema.nom,
                len(vues_schema),
            )
            # print(
            #     "get_vues_base: ",
            #     len(vues_utilisees),
            #     " definies dans le schema",
            #     self.schema.nom,
            #     len(vues_schema),
            # )
            return vues_utilisees
        except (AttributeError, KeyError):
            LOGGER.info("pas de vues definies dans le schema %s", self.schema.nom)
            # print("get_vues_base: pas de vues definies dans le schema", self.schema.nom)
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
        """nettoyage"""
        drop = []
        for ident in liste:
            groupe, nom = self.get_nom_base(ident)
            table = groupe + "." + nom
            drop.append("DROP TABLE IF EXISTS " + table + ";")
        drop.reverse()  # on inverse l'ordre de destruction par rapport a la creation
        return drop

    def dropvues(self, liste):
        """nettoyage"""
        drop = []
        tmplist = list(liste)
        if self.connection and self.connection.schemabase:
            listevues = [self.get_nom_base(ident) for ident in liste]
            schemabase = self.connection.schemabase
            self.viewsorter(tmplist, listevues)
            tmplist.reverse()  # on detruit a l'envers de la creation
            for ident in tmplist:
                drop.append(self.dropvue(ident))
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
        """sql de suppression des types"""
        return [
            "DROP TYPE IF EXISTS " + self.schema_conf + "." + i + ";"
            for i in liste_confs
        ]

    # scripts de creation de tables
    def sio_crestyle(self, liste=None):
        """genere les styles de saisie"""
        return []

    def sio_cretable(self, cod="utf-8", liste=None, autopk=False, role=None):
        """sortie des sql pour la creation des tables"""
        creconf = dict()
        #        dbcod = cod
        #        if self.connection:
        #            dbcod = self.connection.codecinfo.get(cod, cod)
        #        codecinfo = "--########### encodage fichier "+cod+'->'+dbcod+' ###(controle éèàç)####\n'
        refcontext = self.regle_ref if self.regle_ref else self.stock_param
        idschema = (
            "-- ############ nom:"
            + self.schema.nom
            + " ## type_base:"
            + self.dialecte
            + " ## mode:"
            + ("basique" if self.basic else "std")
            + " ###############\n"
        )
        # self.schema.printelements_specifiques()
        self.role = role
        if liste is None:
            liste = sorted(
                [i for i in self.schema.classes if self.schema.classes[i].a_sortir]
            )
            LOGGER.debug(
                "tables non sorties %s",
                ",".join(
                    [
                        str(i)
                        for i in self.schema.classes
                        if not self.schema.classes[i].a_sortir
                    ]
                ),
            )

        vues_base = self.get_vues_base(liste)
        def_speciales = set(vues_base)
        liste_ftables = [
            i
            for i in liste
            if self.schema.classes[i].type_table.upper() == "F" and not self.basic
        ]
        def_speciales |= set(liste_ftables)
        liste_tables = list([i for i in liste if i not in def_speciales])

        #       for i in liste_tables:
        #            print('type :',i,self.schema.classes[i].type_table)
        LOGGER.info(
            "%s definition de %d tables a sortir:(%s)",
            self.schema.nom,
            len(liste_tables),
            self.dialecte,
        )

        cretables = [idschema, self._setrole()]
        if self.basic or (
            refcontext
            and (refcontext.istrue("sql_nofunc") or refcontext.istrue("nofunc"))
        ):
            LOGGER.info(
                "pas de sortie des fonctions %s", refcontext.getvar("sql_nofunc")
            )
            pass
        else:
            cretables.append(
                "\n-- ########### definition des fonctions ###############\n"
            )
            LOGGER.info("sortie des fonctions %s", refcontext.getvar("sql_nofunc"))

            cretables.extend([i + ";" for i in self.def_fonctions().values()])
        cretables.append("\n-- ########### definition des tables ###############\n")
        cretables.extend(
            list(
                [
                    self.cree_tables(ident, creconf, autopk=autopk)
                    for ident in liste_tables
                ]
            )
        )
        if not self.basic:
            if liste_ftables:
                cretables.append(
                    "\n-- ########### definition des tables distantes ############\n"
                )
                cretables.extend(
                    list([self.cretable_dist(ident) for ident in liste_ftables])
                )
            if vues_base:
                cretables.append(
                    "\n-- ########### definition des vues ###############\n"
                )
                cretables.extend(self.cre_vues(liste, vues_base))

            else:
                LOGGER.info("pas de vues a sortir %s", self.schema.nom)
                # print("pas de vues a sortir")
            for ident in liste:
                cretables.extend(self.cree_fks(ident))
            foncdefs = dict()
            trigdefs = []
            for ident in liste:
                trigs, foncs = self.basetriggers(ident)
                # print("definition triggers ", ident, len(trigs), len(foncs))
                trigdefs.extend(trigs)
                foncdefs.update(foncs)
            cretables.append(
                "\n-- ########### definition des fonctions triggers ###############\n"
            )
            cretables.extend([i.replace("\r", "") + ";" for i in foncdefs.values()])
            cretables.append(
                "\n-- ########### definition des triggers ###############\n"
            )

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
        """nettoyage"""
        # print("dropview", ident, is_mat)
        if is_mat == "True":
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
        """creation des vues"""
        if is_mat == "True":
            return (
                "CREATE MATERIALIZED VIEW "
                + ".".join(ident)
                + " AS\n"
                + definition[:-1]
                + "\n WITH NO DATA;\n"
            )
        return "CREATE OR REPLACE VIEW " + ".".join(ident) + " AS\n" + definition

    def cre_vues(self, liste, vues_base):
        """fournit les definitione de vues lues en base"""
        vues_sql = ["--gestion des vues en base \n", "--menage"]
        niveau = self.viewsorter(liste, vues_base)
        # liste_d = liste[::-1]
        # for ident in liste_d:
        #     if ident in vues_base:
        #         # print(
        #         #     "drop_vues", ident, vues_base[ident][1], type(vues_base[ident][1])
        #         # )
        #         vues_sql.append(self.dropvue(ident, vues_base[ident][1]))
        #         # print("recu ", self.dropvue(ident, vues_base[ident][1]))
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

                if classe.type_table == "m":
                    ctr, idx = self.cree_indexes(classe, groupe, nom)

                    vues_sql.extend(ctr)
                    vues_sql.extend(idx)

                vues_sql.extend(self.cree_comments(classe, groupe, nom))

        print("definition de vues generees", len(vues_base), "->", len(vues_sql))
        #        print ('liste vues','\n'.join([str(i)+':'+str(niveau[i]) for i in listevues]))

        return vues_sql

    def def_fonction_triggers(self, ident, ftrigs):
        """cree les fonctions trigger necessaires"""

        return ftrigs.get(ident, "")

    def def_fonctions(self):
        """retourne les definitions de fonctions"""
        entete, fonctions = self.schema.elements_specifiques.get(
            "def_fonctions", (None, dict())
        )
        print("---------------------------fonctions a creer ", fonctions)
        return fonctions

    # ============== gestionnaire de reinitialisation de la base===============

    @staticmethod
    def _commande_geom_strict(niveau, classe, strict, gtyp="0", dim="2", courbe=False):
        """manipulation de la geometrie pour la discretisation des courbes"""
        return ""

    @staticmethod
    def _commande_geom_courbe(niveau, classe, gtyp="0", dim="2", courbe=False):
        """manipulation de la geometrie pour la discretisation des courbes"""
        return ""

    @staticmethod
    def _commande_index_gist(niveau, classe, drop):
        """suppression des index geometriques pour accelerer le chargement"""
        return ""

    @staticmethod
    def _commande_reinit(niveau, classe, delete):
        """commande de reinitialisation de la table"""

        #        prefix = 'TRUNCATE TABLE "'+niveau.lower()+'"."'+classe.lower()+'";\n'
        return (
            ("DELETE FROM " if delete else "TRUNCATE TABLE ")
            + _nomsql(niveau, classe)
            + ";\n"
        )

    @staticmethod
    def _commande_sequence(niveau, classe):
        """cree une commande de reinitialisation des sequences
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
        """cree une commande de reinitialisation des sequences"""
        return (
            "ALTER TABLE "
            + _nomsql(niveau, classe)
            + (" ENABLE " if valide else " DISABLE ")
            + "TRIGGER USER;\n"
        )

    @staticmethod
    def _commande_monitoring(*args):
        """cree une commande de stockage de stats"""
        return ""

    def prefix_charge(self, niveau, classe, reinit, gtyp="0", dim="2"):
        """#aide||#tag:variables:reinit
        #aide||gere toutes les reinitialisations eventuelles par table
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
        if (
            "L" in reinit or "C" in reinit
        ) and gtyp in "23":  # ouverture de la geometrie'
            prefix = prefix + self._commande_geom_strict(niveau, classe, False, dim=dim)
        return prefix

    def tail_charge(
        self, niveau, classe, reinit, gtyp="0", dim="2", courbe=False, schema=None
    ):
        """menage de fin de chargement"""
        prefix = ""
        if "L" in reinit and gtyp in "23":  # discretisation'
            prefix = prefix + self._commande_geom_strict(
                niveau, classe, True, gtyp=gtyp, dim=dim
            )
        if "C" in reinit and gtyp in "23":  # discretisation'
            prefix = prefix + self._commande_geom_strict(
                niveau, classe, True, gtyp=gtyp, dim=dim, courbe=courbe
            )
            print ('tail_charge: traitement courbes:' , courbe,'->', prefix)
        if "S" in reinit:
            prefix = prefix + self._commande_sequence(niveau, classe)
        if "I" in reinit and gtyp > "0":
            prefix = prefix + self._commande_index_gist(niveau, classe, False)
        if "G" in reinit:
            prefix = prefix + self._commande_trigger(niveau, classe, True)
        if "M" in reinit:
            prefix = prefix + self._commande_monitoring(niveau, classe, schema, reinit)
        return prefix
