# -*- coding: utf-8 -*-
"""
Acces aux bases de donnees elyx

commandes disponibles :

    * lecture des structures et des droits
    * multi extraction en parallele par programme externe
    * chargement par programme externe

necessite la librairie cxOracle et un client oracle 64 bits

l'utilisation des loaders et extracteurs necessite les programmes FEA2ORA et ORA2FEA et un client oraccle 32 bits

il est necessaire de positionner les parametres suivant:


"""
import os
import subprocess
import tempfile
import time
from . import base_oraclespatial as ora


class ElyConnect(ora.OrwConnect):
    """connecteur de la base de donnees oracle"""

    def __init__(
        self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None
    ):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.confs = dict()
        self.compos_id = dict()
        self.tables = dict()
        self.attributs = dict()
        self.type_base = "ELYX"
        self.accept_sql = "non"
        self.load_helper = "prog_fea2ora"
        self.load_ext = "asc"
        self.dump_helper = "prog_ora2fea"
        self.dump_paramwriter = None
        self.sys_fields = {
            "#_sys_date_cre": ("APIC_CDATE", "D"),
            "#_sys_date_mod": ("APIC_MDATE", "D"),
            "#_sys_etat": ("APIC_STATE", "T"),
            "#gid": ("GID", "E"),
        }
        self.adminschema = "ELYX_ADMIN_P"
        self.modelschema = "ELYX_MODELE"
        self.types_base["REEL"] = "F"
        self.debuglog = ""
        # print("code de la base", code, params)
        if params and code:
            self.adminschema = params.getvar(
                "elyx_adminschema_" + code, defaut=self.adminschema
            )
            self.modelschema = params.getvar(
                "elyx_modelschema_" + code, defaut=self.modelschema
            )

    def extsql(self, prog, file, logfile=None, outfile=None):
        """execute un programme chargement de donnees """
        serveur = " --".join(self.serveur.split(" "))
        chaine_connect = serveur + " --dbname=" + self.base
        if self.user:
            chaine_connect = chaine_connect + " --user=" + self.user
        if self.passwd:
            chaine_connect = chaine_connect + " --password=" + self.passwd
        if outfile:
            chaine_connect = chaine_connect + " --outfile=" + outfile

        chaine = " --".join((prog, chaine_connect, "file=" + file))
        #        print ('loader ', chaine)
        env = dict(os.environ) if self.params is None else self.params.env
        if not logfile:
            fini = subprocess.run(chaine, env=env, stderr=subprocess.STDOUT)
        else:
            fini = subprocess.run(
                chaine, env=env, stdout=logfile, stderr=subprocess.STDOUT
            )
        if fini.returncode:
            print("sortie en erreur ", fini.returncode, fini.args, fini.stderr)

    def setenv(self, hdir=None):
        """positionne les variables d'environnement pour les programmes externes """
        orahome = self.regle.getvar("feaora_oracle_home_" + self.code)
        env = dict(os.environ)
        #        print('modif_environnement ',env)
        if orahome:  # on manipule les variables d'environnement
            env["ORACLE_HOME"] = orahome
            if os.path.isdir(orahome + "\\bin"):
                # full client
                env["PATH"] = orahome + "\\bin;" + env["PATH"]
            else:
                # minimal client
                env["PATH"] = orahome + ";" + env["PATH"]
        if hdir:  # on positionne le path pour le chargeur
            env["PATH"] = hdir + ";" + env["PATH"]
        return env

    def fearunner(self, parms):
        """ gere les programmes elyx externe """
        helper, paramfile, size, outfile = parms
        helperdir = os.path.dirname(helper)
        chaine = helper + " -c " + paramfile
        env = self.setenv(helperdir)
        if self.regle.getvar("noload") == "1":  # simulation de chargement pour debug
            print("fearunner elyx: mode simulation -------->", chaine)
            print(
                "extrunner elyx: param_file \n",
                "".join(open(paramfile, "r", encoding="cp1252").readlines()),
            )
            print("oracle_home:", env["ORACLE_HOME"])
            print("environnement", env)
            return None

        outdesc = open(outfile, mode="w", encoding="cp1252")
        #        print('elyx: traitement externe', chaine)
        process = subprocess.Popen(
            chaine,
            env=env,
            stdout=outdesc,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        return process

    def lanceur(self, helper, xml, paramfile, outfile, wait=True):
        """gere le programme externe """
        chaine = helper + " -c " + paramfile
        helperdir = os.path.dirname(helper)
        encoding = "cp1252"
        env = self.setenv(helperdir)
        if self.regle.getvar("noload") == "1":  # simulation de chargement pour debug
            print("lanceur elyx: mode simulation -------->", chaine)
            print("lanceur elyx: param_file \n", "\n".join(xml))
            print("oracle_home:", env["ORACLE_HOME"])
            print("environnement", env)
            return None

        with open(paramfile, mode="w", encoding=encoding) as tmpf:
            tmpf.write("\n".join(xml))
        outdesc = open(outfile, mode="w", encoding="cp1252")
        #        print('elyx: traitement externe', chaine)
        if wait:
            fini = subprocess.run(
                chaine,
                env=env,
                stdout=outdesc,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            outdesc.close()
            if fini.returncode:
                print("sortie en erreur ", fini.returncode, fini.args, fini.stderr)
                return False
            return True
        else:
            process = subprocess.Popen(
                chaine,
                env=env,
                stdout=outdesc,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            return process

    #            time.sleep(10000)

    def singlerunner(self, helper, xml, nom, classes):
        """lance les exports ou les imports a partir du fichier xml"""
        with tempfile.TemporaryDirectory() as tmpdir:
            paramfile = os.path.join(str(tmpdir), "param_FEA.xml")
            outfile = os.path.join(str(tmpdir), nom + "_out_FEA.txt")
            resultats, size, _ = self.stat_classes(classes, "no")
            dinit = time.time()
            if self.lanceur(helper, xml, paramfile, outfile):
                self.export_statprint(
                    None, ((nom,), outfile, size, resultats), time.time() - dinit
                )
            print("traitement externe %10.1f secondes" % (time.time() - dinit))
            return resultats

    def gen_importxml(self, helper, file, logdir, reinit, vgeom="1"):
        """prepare le fichier xml pour l'import elyx"""
        csystem = os.path.join(str(os.path.dirname(helper)), r"syscoord\sysgeo.dat")
        logobject = os.path.join(logdir, "log_import.txt")
        rejectdir = os.path.join(logdir, "erreurs")
        os.makedirs(rejectdir, exist_ok=True)
        print("generation import", file, logdir, rejectdir)
        loadxml = [
            "<Fea2OraConfig>",
            '<oraCnx cnx="'
            + self.serveur
            + '" user="'
            + self.user
            + '" pwd="'
            + self.passwd
            + '" role=""/>',
            '<apicBase name="' + self.base + '" version="5"/>',
            "<filePath>",
            '<srcFile path="' + file + '"/>',
            '<reportDir path="' + logdir + '"/>',
            '<logDir path="' + logdir + '"/>',
            '<coordinateSystem sysgeoPath="' + csystem + '" sysgeoValue=""/>',
            '<logObject path="' + logobject + '"/>',
            '<rejectDir path="' + rejectdir + '"/>',
            "</filePath>",
            '<logSql value="0"/>' "<checkOption>",
            '<creationDate value="1"/>',
            '<attribute value="1"/>',
            '<commitDelay value="1000"/>',
            '<geomInSpace value="1"/>',
            '<doublePoints value="1"/>',
            '<dimension value="1"/>',
            '<section value="1"/>',
            '<replaceObj value="' + reinit + '"/>',
            '<conformNbCar value="0"/>',
            '<conformEnum  value="2"/>',
            '<validateGeometry value="'
            + vgeom
            + '" allowSelfIntersectSurface="0"'
            + ' allowDoublePoints="1" />',
            "</checkOption>",
            "</Fea2OraConfig>",
        ]
        return loadxml

    def genexportxml(self, destination, log, classes):
        """prepare les fichiers de confix xml pour l'export"""
        return [
            "<Ora2FeaConfig>",
            '<oraCnx cnx="'
            + self.serveur
            + '" user="'
            + self.user
            + '" pwd="'
            + self.passwd
            + '" role=""/>',
            '<apicBase name="' + self.base + '" version="5"/>',
            "<filePath>",
            '<dstFile path="' + destination + '"/>',
            '<logDir path="' + log + '"/>',
            "</filePath>",
            '<classes list="' + ",".join([i[1] for i in classes]) + '"/>',
            '<coordinateSystem value="0"/>',
            "</Ora2FeaConfig>",
        ]

    def log_decoder(self, idexport, params, runtime):
        """decode un fichier log de ORA2FEA"""

        outfile = params[1]
        resultats = params[3]
        size = params[2]
        nbobjs = dict()
        # print("analyse log", idexport, outfile, size, resultats)
        fich = os.path.basename(resultats)
        nbfichs = 0
        try:
            for i in open(
                resultats, "r", encoding="cp1252", errors="backslashreplace"
            ).readlines():
                # print("lu:", ascii(i[:-1]))
                if "Nombre d'objets export" in i:
                    tmp = i.split(":")
                    nomclasse = tmp[-2].split(" ")[-1]
                    classe = self.schemabase.get_classe(("", nomclasse))
                    idclasse = classe.identclasse
                    exportes = int(tmp[-1])
                    theoriques = int(classe.getinfo("objcnt_init", "0"))
                    nbobjs[idclasse] = (exportes, theoriques, runtime)
                    nbfichs = 0

                    # if len(idexport) == 1:
                    #     print(
                    #         "%-45s objets exportes: %10d / %10d en %.2f s"
                    #         % (".".join(idclasse), exportes, theoriques, runtime)
                    #     )
                if "Nombre total d'objets export" in i:
                    #                print ('analyse log',idexport,ascii(i))
                    theoriques = int(i.split(":")[-1])
                    exportes = size
                    # print(
                    #     "%-45s objets exportes: %10d / %10d en %.2f s"
                    #     % (
                    #         ".".join(idexport),
                    #         theoriques,
                    #         exportes,
                    #         runtime,
                    #     )
                    # )

                    nbobjs["total"] = (size, theoriques, runtime)
                if ": error :" in i:
                    self.regle.stock_param.logger.error(
                        " export elyx %s : %s", fich, i[:-1]
                    )
                    # print("detection erreur", i)
                if ": warning :" in i:
                    self.regle.stock_param.logger.warning(
                        " export elyx %s : %s", fich, i[:-1]
                    )
                    # print("detection warning", i)
            # print("fin anlalyse log:", exportes)
            nbfichs = len(nbobjs)
            self.regle.stock_param.aff.send(("exp", nbfichs, exportes))
            return 0
        except Exception as err:
            print("fichier non pret", err)
            # raise
            time.sleep(0.1)  # on est alle trop vite le fichier n'est pas pret
            return 1

    def export_statprint(self, idexport, params, runtime):
        """affiche une stat d'export
        appel :(None, ((nom,), outfile, size, resultats), time.time() - dinit)
        """
        # print( 'appel log_decoder ',idexport,params)
        retour = self.log_decoder(idexport, params, runtime)
        if retour:  # petit truc pour eviter les problemes de fichier non ferme
            self.log_decoder(idexport, params, runtime)

    def stat_classes(self, classes, fanout):
        """retourne les stats d export"""
        schemabase = self.schemabase
        resultats = dict()
        size = dict()
        blocks = dict()
        nom = ""
        if fanout not in {"classe", "groupe", "no"}:
            print("mode de fanout non géré", fanout)
            fanout = "no"
        if schemabase:
            if fanout == "no":
                nom = (classes[0][1],) if len(classes) == 1 else ("export",)
            for i in classes:
                if fanout == "classe":
                    nom = i
                elif fanout == "groupe":
                    nom = (i[0],)
                nbobjs = int(schemabase.classes[i].getinfo("objcnt_init", "0"))
                if nbobjs == 0:
                    resultats[i] = 0
                    continue
                if (nom) in blocks:
                    blocks[nom].append(i)
                    size[nom] += nbobjs
                else:
                    blocks[nom] = [i]
                    size[nom] = nbobjs

        return resultats, size, blocks

    def get_blocks(self, helper, classes, dest, log, fanout, nbworkers):
        """ decoupe les classes a sortir en blocs pour traitement en parallele"""
        self.resultats, self.size, blocks = self.stat_classes(classes, fanout)
        subcode = 0
        retour = []
        for subcode, nom in enumerate(blocks):
            destination = os.path.join(dest, *nom)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            logdir = os.path.join(log, nom[0], str(subcode % nbworkers))
            os.makedirs(logdir, exist_ok=True)
            # print("get_blocks preparation xml", destination, logdir)
            xml = self.genexportxml(destination, logdir, blocks[nom])
            paramfile = os.path.join(self.tmpdir, "_".join(nom) + "_param_FEA.xml")
            if self.debuglog:
                xmllogfile = os.path.join(log, "_".join(nom) + "_param_FEA.xml")
                with open(xmllogfile, mode="w", encoding="cp1252") as logf:
                    logf.write("\n".join(xml))
            with open(paramfile, mode="w", encoding="cp1252") as tmpf:
                tmpf.write("\n".join(xml))
            outfile = os.path.join(logdir, "_".join(nom) + "_out_FEA.txt")
            retour.append(
                (
                    nom,
                    (helper, paramfile, self.size[nom], outfile),
                    (dest, nom, "asc"),
                    self.size[nom],
                )
            )

        # optimiseur de blocks : on sait qu'il faut commencer par les plus longs mais pas tout de suite
        tmp = sorted(retour, reverse=True, key=lambda x: x[3])
        if len(tmp) > nbworkers * 2:
            retour = (
                tmp[nbworkers : nbworkers * 2] + tmp[:nbworkers] + tmp[nbworkers * 2 :]
            )
            # attention logique mongolienne inverse : on commence par la fin ...
            retour.reverse()

        return retour

    def extalpha(self, regle_courante, helper, classes, dest, log, nbworkers=(1, 1)):
        """extrait des donnees par ORA2FEA"""
        self.check_helper(helper)

        # mise en place de l'environnement:
        #        print ('elyx extalpha',classes)
        #        tmpdirstore = tempfile.TemporaryDirectory()
        #        tmpdir = tmpdirstore.name
        #        print ('tmpdir',tmpdir)
        self.debuglog = regle_courante.getvar("debuglog")
        if self.debuglog:
            print("---------------------------- generation log debug-----------")
        nbtrait, nbdump = nbworkers
        fanout = regle_courante.getvar("fanout", "classe")
        with tempfile.TemporaryDirectory() as tmpdir:
            #        if True:
            self.tmpdir = str(tmpdir)

            blocks = self.get_blocks(helper, classes, dest, log, fanout, nbdump)
            regle_courante.stock_param.logger.info(
                "calcule blocs %d (%s) %s",
                len(blocks),
                regle_courante.getvar("_wid"),
                fanout,
            )
            # print("calcule blocs ", len(blocks), regle_courante.getvar("_wid"), fanout)
            fileiter = self.params.iterparallel_ext(
                blocks, nbdump, self.fearunner, patience=self.export_statprint
            )
            regle_courante.listgen = fileiter
            regle_courante.parallelmode = "process"
            # print ('elyx : extalpha ', regle_courante)
            if nbtrait > 1 and len(blocks) > 1:
                try:
                    self.params.traite_parallel(regle_courante)
                except Exception as err:
                    print("erreur traitement parallele", err)
                    raise
            else:  # traitement standard
                for retour in fileiter:
                    if retour is not None:
                        # print("elyx extalpha,recu", retour)
                        nb, infos = retour
                        clef, pars = infos
                        rep, chemin, classe, ext = pars
                        # chemin, classe = idclasse
                        fichier = os.path.join(rep, chemin, classe)
                        regle_courante.stock_param.logger.debug(
                            "fichier a traiter : %s", str(fichier)
                        )
                        # print(
                        #     "fichier a traiter :",
                        #     fichier,
                        #     regle_courante.getvar("_sortie"),
                        # )
                        try:
                            self.params.lecture(
                                classe,
                                regle=regle_courante,
                                parms=(rep, chemin, classe, ext),
                            )
                        except Exception as err:
                            print("erreur traitement base", err)

            print("fin traitement extalpha", flush=True)
            # time.sleep(10)
        return self.resultats

    def extdump(
        self, helper, classes, dest, log, fanout="classe", workers=1, mode="dump"
    ):
        """extrait des donnees par ORA2FEA"""
        # mise en place de l'environnement:
        print("dump elyx", log)
        self.check_helper(helper)

        with tempfile.TemporaryDirectory() as tmpdir:
            self.tmpdir = str(tmpdir)
            blocks = self.get_blocks(helper, classes, dest, log, fanout, workers)
            self.params.execparallel_ext(
                blocks, workers, self.fearunner, patience=self.export_statprint
            )

        return self.resultats

    def extload(self, helper, files, logfile=None, reinit="0", vgeom="1"):
        """charge un fichier par FEA2ORA"""
        self.check_helper(helper)
        retour = False
        if len(files) == 1:
            file = files[0]
            loadxml = self.gen_importxml(
                helper, file, logfile, reinit=reinit, vgeom=vgeom
            )
            nom = os.path.splitext(os.path.basename(file))[0]

            retour = self.singlerunner(helper, loadxml, nom, [])
            return retour
        for file in files:
            loadxml = self.gen_importxml(
                helper, file, logfile, reinit=reinit, vgeom=vgeom
            )
            nom = os.path.splitext(os.path.basename(file))[0]
            retour = self.singlerunner(helper, loadxml, nom, [])
            print("retour chargement asc", retour)
        return retour
        # TODO gestion des retours

    def traite_defaut(self, nom_att, defaut):
        """analyse les defauts et les convertit en fonctions internes"""
        if defaut is None:
            return defaut
        resultat = defaut
        if defaut.startswith("!GENNUM"):
            compteur = defaut[9:-2]
            resultat = "S." + compteur
            self.schemabase.compteurs[compteur] += 1
            return resultat
        elif defaut.startswith("!GENSUR"):
            resultat = "TIN." + defaut[8:-2]
            return resultat
        elif defaut.startswith("!AUTEUR"):
            resultat = "F.AUTEUR"
            return resultat
        elif defaut.startswith("!CALDAT"):
            resultat = "now()"
            return resultat
        elif defaut.startswith('="') and defaut.endswith('"') and not "+" in defaut:
            resultat = defaut[1:].replace("'", "''").replace('"', "'")
            return resultat
        #        print(nom_att, 'valeur defaut', defaut, '->', resultat)
        resultat = None
        return resultat

    def traite_enums_en_table(self):
        """ fait le menage dans les enums speciales"""
        for nom in self.schemabase.conformites:
            if self.schemabase.conformites.special:
                print("traitement ", nom)

    def get_type(self, nom_type):
        if nom_type.upper() not in self.types_base:
            print("elyx:type inconnu ", nom_type)
        return self.types_base.get(nom_type.upper(), "?")

    def get_tables(self):
        return list(self.tables.values())

    def get_enums(self):
        """ recupere la description de toutes les enums depuis la base de donnees """
        #        print("conformites")
        schema = self.adminschema
        enums_en_table = dict()
        requete = self.constructeur(
            schema,
            "APICD_CONFORMITE",
            [
                "NUMERO_AD",
                "ACTION",
                "VERSION",
                "NUMERO_MODELE",
                "NOM",
                "ENUM_OBJCLASS",
                "ENUM_KEY_ATTRIBUTE",
                "ENUM_VALUE_ATTRIBUTE",
                "ENUM_ORDER_ATTRIBUTE",
                "ENUM_FILTER",
            ],
        )

        dict_conf = self.menage_version(self.request(requete, ()), 1, 0, 2)
        self.get_attributs()

        # liste_conf=menage_version(liste_conf.values(),1,4,2)
        def_enums = dict()
        for i in dict_conf.values():
            self.confs[i[0]] = i[4]
            if i[5]:  # attention c'est un truc_special
                noms_schema, nom_table = self.compos_id[i[5]]
                filtredef = i[9].split("=")
                champ_filtre = filtredef[0]
                val_filtre = filtredef[1].strip("'")
                champ_clef = self.attributs[i[6]][2]
                champ_val = self.attributs[i[7]][2]
                champ_ordre = self.attributs[i[8]][2]
                enums_en_table[i[4]] = (
                    noms_schema,
                    nom_table,
                    champ_filtre,
                    val_filtre,
                    champ_clef,
                    champ_val,
                    champ_ordre,
                )
                def_enums[
                    (
                        noms_schema,
                        nom_table,
                        champ_filtre,
                        val_filtre,
                        champ_clef,
                        champ_val,
                        champ_ordre,
                    )
                ] = None

        requete = self.constructeur(
            schema,
            "APICD_CONFORMITEVALEUR",
            [
                "NUMERO_AD",
                "NUMERO_MODELE",
                "NOM",
                "NUMERO_CONF",
                "TEXTE",
                "ORDRE",
                "ACTION",
                "VERSION",
            ],
        )
        vals = self.menage_version(self.request(requete, ()), 6, 0, 7)
        vals = self.menage_version(list(vals.values()), 6, 2, 7, 3)
        enums = []

        for i in list(vals.values()):
            num_conf = i[3]
            nom = self.confs[num_conf]
            #            num_val = i[0]
            valeur = str(i[2]).replace("\n", ":")
            alias = str(i[4]).replace("\n", ":")
            ordre = i[5]
            enums.append((nom, ordre, valeur, alias, 1))

        if enums_en_table:
            if (
                def_enums
            ):  # cas particulier des enums en tables : il faut lire la table des enums:
                for description in def_enums:
                    (
                        noms_schema,
                        nom_table,
                        champ_filtre,
                        val_filtre,
                        champ_clef,
                        champ_val,
                        champ_ordre,
                    ) = description
                    #                    print('traitement table', table)
                    requete = self.constructeur(
                        noms_schema,
                        nom_table,
                        [champ_filtre, champ_clef, champ_val, champ_ordre],
                    )
                    if val_filtre:
                        requete = (
                            requete
                            + " WHERE "
                            + champ_filtre
                            + " = '"
                            + val_filtre
                            + "'"
                        )
                    #                    print('requete base', requete)
                    def_enums[description] = self.request(requete)
            #                    print ('valeurs en table',table,  valtable)

            for nom in enums_en_table:
                (
                    noms_schema,
                    nom_table,
                    champ_filtre,
                    val_filtre,
                    champ_clef,
                    champ_val,
                    champ_ordre,
                ) = enums_en_table[nom]
                table = def_enums[
                    noms_schema,
                    nom_table,
                    champ_filtre,
                    val_filtre,
                    champ_clef,
                    champ_val,
                    champ_ordre,
                ]
                enum = {i[1]: i for i in table if i[0] == val_filtre}
                for i in enum:
                    _, clef, val, ordre = enum[i]
                    #                    print ('enum_en_table',nom, ordre, clef, val)
                    enums.append((nom, int(ordre) if ordre else 0, clef, val, 1))

            # print "stockage_conformite",valeur,alias
        #        print ('confs',self.confs)
        for i in self.attributs:
            enum = self.confs.get(self.attributs[i].enum)
            self.attributs[i] = self.attributs[i]._replace(enum=enum)
        #                    if conf is None:
        #                        print (nomschema, nomtable, nom_att,i[13], len(self.confs))
        #            if i[4] == "BOOLEEN":
        #                # (cas particulier des booleens on en fait une enum)
        #                conf = self.confs.get("BOOLEEN")
        #                i[4] = 'TEXT'
        #            i[9] = conf
        return enums

    def get_attributs(self):
        """recupere le schema complet
        nomschema,nomtable,attribut,alias,type_attribut,graphique,multiple,defaut,obligatoire
        enum,dimension,num_attribut,index,uniq,clef_primaire,clef_etrangere,parametres_clef,cible_clef"""
        schema = self.adminschema
        if self.attributs:
            return self.attributs.values()
        requete = self.constructeur(
            schema,
            "APICD_COMPOSANT",
            [
                "NOM",
                "ACTION",
                "VERSION",
                "NUMERO_AD",
                "ALIAS",
                "NATURE",
                "FERMETURE",
                "TRAIT",
                "ABSTRAIT",
                "ECHELLE_LIMITE",
                "ECHELLE_DISPARITION",
            ],
        )
        # print("composants", len(self.confs))
        compos = self.menage_version(self.request(requete, ()), 1, 0, 2)
        compos = self.menage_version(list(compos.values()), 1, 3, 2)
        compos_id = dict()

        requete = self.constructeur(
            schema,
            "APICD_BASE_COMPOSANT",
            ["TALIAS", "ACTION", "VERSION", "NUMERO_AD", "NOMBREDIM", "SCHEMA"],
        )
        # dimensions

        #        print("dimensions")
        liste_dims = self.menage_version(self.request(requete, ()), 1, 0, 2)
        liste_dims = self.menage_version(list(liste_dims.values()), 1, 3, 2)

        nom_schema_elyx = dict()
        dimensions = dict()
        for i in liste_dims.values():
            nom = i[0]
            nom_schema_elyx[nom] = i[5]
            dimensions[nom] = i[4]

        requete_tables = """      SELECT tab.owner as nomschema,
                                tab.table_name as nomtable,
                                 tab.num_rows as nb_enreg

                FROM all_tables tab
                where owner<> 'SYS'
                      AND owner<> 'CTXSYS'
                      AND owner<> 'SYSTEM'
                      AND owner<> 'XDB'
                      AND owner<> 'WMSYS'
                      AND owner<> 'MDSYS'
                      AND owner<> 'EXFSYS'
                      AND owner<> 'CUS_DBA'
                      """
        taille_tables = self.request(requete_tables, ())
        dict_tailles = {(i[0], i[1]): i[2] for i in taille_tables}
        # print("tailles", sorted(taille_tables))

        self.tables = dict()
        for i in compos.values():
            abstrait = i[8]
            if abstrait:
                continue
            geom_type = i[5] - 1
            dimens = 2
            nom = i[0].replace("-", "_")
            groupe = nom_schema_elyx.get(nom, "inconnu")
            if groupe != "inconnu":
                dimens = dimensions[nom]
            else:
                print("error: elyx : groupe inconnu", i[0])
            if geom_type < 0:
                print("info : elyx :composant generique", i[0])
            else:
                ident = (groupe, nom)
                alias = i[4]
                nbobj = dict_tailles.get(ident, -1)
                self.tables[ident] = (
                    groupe,
                    nom,
                    alias,
                    geom_type,
                    dimens,
                    nbobj,
                    "r",
                    "",
                    "",
                    "",
                    "",
                )

                compos_id[i[3]] = ident  # lien numero nom
                # print "association ",i[3],i[0]
            # print cl.nom,cl.type_geom,cl.fermeture
        # print sorted(compos_nom)
        # print("info : elyx : tables/composants trouves", len(self.tables), len(compos))

        requete = self.constructeur(
            schema,
            "APICD_ATTRIBUT",
            [
                "NUMERO_AD",
                "ACTION",
                "VERSION",
                "NUMERO_MODELE",
                "NUMERO_COMPOSANT",
                "NOM",
                "ALIAS",
                "NATURE",
                "MODIFICATION",
                "MULTIPLICITE",
                "TYPE",
                "OBLIGATOIRE",
                "DEFAUT",
                "NUMERO_CONF",
                "ORDRE",
            ],
        )

        #        print("attributs")

        liste_atts = self.menage_version(self.request(requete, ()), 1, 0, 2)
        code_type = {1: "E", 2: "F", 3: "T", 4: "B", 5: "D"}

        indexdefs = dict()

        for i in liste_atts.values():
            #            print ('num_table',i[4])
            id_compo = compos_id.get(i[4])
            table = self.tables[id_compo]
            if id_compo:
                nomschema, nomtable = id_compo
                if id_compo in self.tables:
                    if id_compo not in indexdefs:
                        req_indexes = (
                            """SELECT LISTAGG(index_name||':'||column_position,' ') WITHIN GROUP (order by index_name) as indexes,
                                column_name from all_ind_columns ic """
                            + "WHERE ic.table_owner='"
                            + nomschema
                            + "' AND ic.table_name='"
                            + nomtable
                            + """' GROUP BY table_owner,table_name,column_name"""
                        )
                        indexes = dict()
                        for ligne in self.request(req_indexes, ()):
                            liste, nom_att = ligne
                            indexes[nom_att] = liste
                        indexdefs[id_compo] = indexes

                    nom_att = i[5]
                    type_att = code_type[i[10]]
                    #                    if traite_enums:
                    ind_def = indexdefs[id_compo].get(nom_att, "")
                    conf = i[13]
                    if conf and type_att != "T":
                        #                       print (id_compo, nom_att, 'type attribut_conformite ', type_att, '->', conf)
                        conf = ""  # on ne sait pas gerer les conformites non texte
                    #                        conf = self.confs.get(i[13])
                    #    #                    if conf is None:
                    #    #                        print (nomschema, nomtable, nom_att,i[13], len(self.confs))
                    #                        if type_att == "BOOLEEN":
                    #                            # (cas particulier des booleens on en fait une enum)
                    #                            conf = self.confs.get("BOOLEEN")
                    #                            type_att = "TEXTE"
                    defaut = self.traite_defaut(nom_att, i[12])

                    graphique = i[7] == 2
                    obligatoire = i[11] == 1
                    ordre = i[14]
                    if ordre <= 0:
                        print(
                            "elyx:ordre incoherent detecte ",
                            nomschema,
                            nomtable,
                            nom_att,
                            ordre,
                        )
                        ordre = 0.01
                    alias = i[6]
                    multiple = i[9]
                    dimension = table[4]

                    attdef = self.attdef(
                        nomschema,
                        nomtable,
                        nom_att,
                        alias,
                        type_att,
                        graphique,
                        multiple,
                        defaut,
                        obligatoire,
                        conf,
                        dimension,
                        ordre,
                        ind_def,
                        "",
                        "",
                        "",
                        "",
                        "",
                        0,
                        0,
                    )
                    # print("attribut", i[0], nomschema, nomtable, nom_att, conf)
                    self.attributs[i[0]] = attdef
                    if graphique:
                        attdef = self.attdef(
                            nomschema,
                            nomtable,
                            nom_att + "_X",
                            "X " + str(alias),
                            "F",
                            "False",
                            multiple,
                            "",
                            obligatoire,
                            "",
                            dimension,
                            ordre + 0.1,
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            0,
                            0,
                        )
                        # print ('attribut',attdef)
                        self.attributs[i[0] + 0.1] = attdef
                        attdef = self.attdef(
                            nomschema,
                            nomtable,
                            nom_att + "_Y",
                            "Y " + str(alias),
                            "F",
                            "False",
                            multiple,
                            "",
                            obligatoire,
                            "",
                            dimension,
                            ordre + 0.2,
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            0,
                            0,
                        )
                        self.attributs[i[0] + 0.2] = attdef
                        attdef = self.attdef(
                            nomschema,
                            nomtable,
                            nom_att + "_O",
                            "orientation " + str(alias),
                            "F",
                            "False",
                            multiple,
                            "",
                            obligatoire,
                            "",
                            dimension,
                            ordre + 0.2,
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            0,
                            0,
                        )
                        self.attributs[i[0] + 0.3] = attdef
                else:
                    print(
                        "error: elyx : attribut de composant inconnu", i, compos_id[0]
                    )
            else:
                print("error: elyx : nom_non trouve", i[4], i)
        self.compos_id = compos_id
        self.ajout_att_std()
        return list(self.attributs.values())

    def ajout_att_std(self):
        """ ajoute les attributs standards gid et geometrie pour chaque table"""
        n = 0
        for id_compo, definition in self.tables.items():
            n += 1
            nomschema, nomtable = id_compo
            attdef = self.attdef(
                nom_groupe=nomschema,
                nom_classe=nomtable,
                nom_attr="GID",
                alias="identifiant interne",
                type_attr="S",
                clef_primaire="1",
                num_attribut=0,
            )
            attkey = "K" + str(n)
            self.attributs[attkey] = attdef
            attdef = self.attdef(
                nom_groupe=nomschema,
                nom_classe=nomtable,
                nom_attr="geometrie",
                alias="geometrie",
                type_attr=str(definition[3]),
                dimension=str(definition[4]),
                num_attribut=-1,
            )
            attkey = "G" + str(n)
            self.attributs[attkey] = attdef

    def constructeur(self, schema, table, attributs):
        """constructeur de requetes de lecture de tables de donnees"""
        return (
            ' SELECT "'
            + '","'.join(attributs)
            + '" FROM "'
            + schema
            + '"."'
            + table
            + '"'
        )

    def menage_version(self, liste, n_action, n_clef, n_version, n_groupe=-1, debug=0):
        """extrait la bonne version d'un objet des tables systeme d'exlyx"""
        retour = dict()
        #        d = len(liste)
        for i in liste:
            #        if i[n_action]!=3:
            code = (i[n_clef], i[n_groupe]) if n_groupe != -1 else i[n_clef]
            vers_num = i[n_version]
            if code in retour:
                vers_e = retour[code][n_version]
                if vers_e > vers_num:
                    continue
            retour[code] = i
        #        print("menage", d, "->", len(retour))
        for i in list(retour.keys()):
            if n_action != -1 and retour[i][n_action] == 3:
                if debug:
                    print("menage code 3 ->", retour[i])
                del retour[i]

        return retour

    # ---------------------------elements specifiques elyx--------------------------

    def select_droits_old(self):
        """ recupere les droits old style """
        schema_oracle = self.adminschema

        requete = self.constructeur(
            schema_oracle,
            "APICD_ROLE",
            ["NUMERO_AD", "ACTION", "VERSION", "NUMERO_MODELE", "NOM", "COMMENTAIRE"],
        )
        liste_roles = self.menage_version(self.request(requete, ()), 1, 0, 2, debug=0)
        print("roles valides", len(liste_roles))
        #        print (liste_roles[2])

        requete = self.constructeur(
            schema_oracle,
            "APICD_ROLE_SOUSMODELE",
            ["NUMERO_AD", "ACTION", "VERSION", "NUMERO_MODELE", "NUMERO_ROLE_B"],
        )

        liste_roles_sm = self.menage_version(
            self.request(requete, ()), 1, 0, 2, debug=0
        )

        requete = self.constructeur(
            schema_oracle,
            "APICD_ROLE_COMPOSANT",
            [
                "NUMERO_AD",
                "ACTION",
                "VERSION",
                "NUMERO_MODELE",
                "NUMERO_ROLE_SM",
                "NUMERO_COMPOSANT",
                "DROIT",
            ],
        )

        liste_atts = self.menage_version(self.request(requete, ()), 1, 0, 2)
        liste = []
        print("definitions valides ", len(liste_atts))
        for i in liste_atts.values():
            num_role_sm = i[4]
            role_sm = liste_roles_sm.get(num_role_sm)
            nom_role = ""
            if role_sm:
                num_role = role_sm[4]
                role = liste_roles.get(num_role)
                if role:
                    nom_role = role[4]
                else:
                    print("role inconnu", num_role)
                    nom_role = "indefini"
                    continue
            else:
                print("role sm inconnu", num_role_sm)
                continue  # le role a saute on ignore les droits
            num_compo = i[5]
            nom_compo = self.compos_id.get(num_compo)
            droit = "consult" if i[6] == 2 else "admin"
            if nom_compo:
                groupe, classe = nom_compo
                liste.append(
                    ";".join((nom_role, str(droit), groupe, classe, str(i[6])))
                )
                #            print (nom_compo,nom_role,droit)

        entete = "nomrole;fonction;nomschema;nomtable"
        print("droits trouves ", len(liste))
        return (entete, liste)

    def select_droits(self, liste_tables=None):
        """ recupere les droits nouvelle formule"""
        requete = (
            '''SELECT "ROLE_NAME", "RIGHTS", "SCHEMA", "ORIGIN_TABLE_NAME"
                        FROM "'''
            + self.modelschema
            + '"."LXMD_OBJCLASS_VIEW"'
        )

        if liste_tables:
            liste = []
            ref = set(liste_tables)
            # infos = list(self.request(requete, ()))
            # print("recup droits", "\n".join(infos))
            liste = [
                ";".join([j if j is not None else "" for j in i])
                for i in self.request(requete, ())
                if (i[2], i[3]) in ref
            ]
        else:
            liste = [
                ";".join([j if j is not None else "" for j in i])
                for i in self.request(requete, ())
            ]
        if self.debug:
            print("db_elyx---------selection droits elyx ", len(liste))
        entete = "nomrole;fonction;nomschema;nomtable"
        # print("recup droits", "\n".join(liste))

        return (entete, liste)

    def droits_attributaires(self, liste_tables=None):
        """ recupere les droits sur les attributs"""
        requete = (
            '''     SELECT r."NAME" as "ROLE",
                                ar."RIGHTS" AS "DROITS",
                                os."SCHEMA" as "SCHEMA",
                                o."NAME" as "CLASSE",
                                a."NAME" as "ATTRIBUT",
                                ro."RIGHTS" AS "DROITS_CLASSE"

        FROM "'''
            + self.modelschema
            + '''"."LXMD_ATTRIBUTE_ROLE" ar
        LEFT JOIN "'''
            + self.modelschema
            + '''"."LXMD_ROLE" r
            ON r."GID"=ar."ROLE"
        LEFT JOIN "'''
            + self.modelschema
            + '''"."LXMD_ATTRIBUTE" a
            on ar."KEY_ATTRIBUTE" = a."GID"
        LEFT JOIN "'''
            + self.modelschema
            + '''"."LXMD_ATTRIBUTE_STORAGE" ats
            on ar."KEY_ATTRIBUTE" = ats."KEY_ATTRIBUTE"
        LEFT JOIN "'''
            + self.modelschema
            + '''"."LXMD_OBJCLASS" o on
            ats."KEY_OBJCLASS_STORAGE"=o."GID"
        LEFT JOIN "'''
            + self.modelschema
            + '''"."LXMD_OBJCLASS_STORAGE" os
            on os."KEY_OBJCLASS"=ats."KEY_OBJCLASS_STORAGE"
        LEFT JOIN "'''
            + self.modelschema
            + """"."LXMD_OBJCLASS_ROLE" ro
            on  ro."KEY_OBJCLASS_STORAGE"=os."GID" AND ro."ROLE"=ar."ROLE"
                """
        )
        if liste_tables:
            liste = []
            ref = set(liste_tables)
            liste = [
                ";".join([j if j is not None else "" for j in i])
                for i in self.request(requete, ())
                if (i[2], i[3]) in ref
            ]
        else:
            liste = [
                ";".join([j if j is not None else "" for j in i])
                for i in self.request(requete, ())
            ]
        if self.debug:
            print("db_elyx---------selection droits attributs elyx ", len(liste))
        entete = "nom_role;type_droit;schema;table;attribut;droits_classe"
        return (entete, liste)

    def complement_table(self, liste_tables=None):
        """recupere des informations complementaires sur les tables elyx notamment le theme"""
        requete = (
            '''SELECT n."SCHEMA" as niveau,
                            oc."NAME" as classe,
                            t."NAME" as theme,
                            t."ALIAS" as alias_theme,
                            oc."MIN_SCALE" as ech_min,
                            oc."MAX_SCALE" as ech_max

        FROM "'''
            + self.modelschema
            + '''"."LXMD_OBJCLASS" oc
        LEFT JOIN "'''
            + self.modelschema
            + '''"."LXMD_THEME" t  on t."GID" = oc."THEME"
        LEFT JOIN "'''
            + self.modelschema
            + """"."LXMD_OBJCLASS_STORAGE" n
        on oc."GID" = n."KEY_OBJCLASS"

        """
        )
        if liste_tables:
            liste = []
            ref = set(liste_tables)
            liste = [
                ";".join([str(j) if j is not None else "" for j in i])
                for i in self.request(requete, ())
                if (i[0], i[1]) in ref
            ]
        else:
            liste = [
                ";".join([str(j) if j is not None else "" for j in i])
                for i in self.request(requete, ())
            ]
        if self.debug:
            print("db_elyx---------selection complements table elyx ", len(liste))
        entete = "niveau;classe;theme;alias_theme;ech_min;ech_max"
        return (entete, liste)

    def get_elements_specifiques(self, schema):
        """ recuperation initialse des elements specifiques"""
        self.select_elements_specifiques(schema)

    def select_elements_specifiques(self, schema, liste_tables=None):
        """recupere des elements specifiques a un format et les stocke
        dans une structure du schema"""

        schema.elements_specifiques["roles"] = self.select_droits(liste_tables)
        # print("info schema elyx", schema.elements_specifiques["roles"])
        schema.elements_specifiques["droits_attributs"] = self.droits_attributaires(
            liste_tables
        )
        schema.elements_specifiques["complements_table"] = self.complement_table(
            liste_tables
        )
        # on mappe les roles sur le schema initial
        droits_table = dict()
        for i in schema.elements_specifiques["roles"][1]:
            nom_role, type_droit, nomschema, table = i.split(";")
            ident = (nomschema, table)
            if ident not in droits_table:
                droits_table[ident] = [(nom_role, type_droit)]
            else:
                droits_table[ident].append((nom_role, type_droit))
        for i in droits_table:
            if i in schema.classes:
                schema.classes[i].specifique["roles"] = droits_table[i]
        #        schema.specifique['roles_old']=self.select_droits_old()
        if self.debug:
            print(
                "db_elyx---------specifique droits elyx ",
                schema.elements_specifiques.keys(),
            )


class ElyGenSql(ora.OrwGenSql):
    """generation d'ordres sql directs"""

    pass


DBDEF = {"elyx": (ElyConnect, ElyGenSql, "server", "", "", "base elyx sur oracle")}
