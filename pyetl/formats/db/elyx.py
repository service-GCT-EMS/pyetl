# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
import os
import subprocess
import tempfile
import time
from  . import oraclespatial as ora
#from ..xml import XmlWriter
def get_slot(pool):
    '''surveille un pool de process et determine s'il y a une disponibilité'''
    while True:
        for i in pool:
            if pool[i] is None or pool[i].poll() is not None:
                return i
#            if pool[i].poll() is not None:
#                if pool[i].returncode != 0:
#                    print('erreur process ', pool[i].args(), pool[i].returncode)
##                pool[i] = None
#                return i
    time.sleep(0.1)

def wait_end(pool):
    '''attend que le dernier process d'un pool ait terminé'''
    actifs = [pool[i] for i in pool if pool[i] is not None]
    while actifs:
#        print('attente ',len(actifs), actifs[0].poll(), actifs[0].args)
        reste = []
        for process in actifs:
            if process.poll() is None:
                reste.append(process)
            else:
                if process.returncode != 0:
                    print('erreur process ', process.args(), process.returncode)
        actifs = reste
        time.sleep(1)
    return


class ElyConnect(ora.OraConnect):
    '''connecteur de la base de donnees oracle'''
    def __init__(self, serveur, base, user, passwd, debug=0, system=False,
                 params=None, code=None):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.idconnect = 'elyx'
        self.confs = dict()
        self.compos_id = dict()
        self.tables = dict()
        self.attributs = dict()
        self.load_helper = 'prog_fea2ora'
        self.load_ext = 'asc'
        self.dump_helper = 'prog_ora2fea'
        self.dump_paramwriter = None
        self.sys_fields = {'#_sys_date_cre':('APIC_CDATE', 'D'),
                           '#_sys_date_mod':('APIC_MDATE', 'D'),
                           '#_sys_E_ETAT':('APIC_STATE', 'T'),
                           '#gid':('GID', 'E')}
        self.adminschema = "ELYX_ADMIN_P"
        self.modelschema = "ELYX_MODELE"
#        print ('code de la base', code, params)
        if params and code:
            self.adminschema = params.get_param("elyx_adminschema_",
                                                defaut=self.adminschema, groupe=code)
            self.modelschema = params.get_param("elyx_modelschema",
                                                defaut=self.modelschema, groupe=code)



    def runsql(self, prog, file, logfile=None, outfile=None):
        '''execute un programme chargement de donnees '''
        serveur = ' --'.join(self.serveur.split(' '))
        chaine_connect = serveur + ' --dbname=' + self.base
        if self.user:
            chaine_connect = chaine_connect + ' --user=' + self.user
        if self.passwd:
            chaine_connect = chaine_connect + ' --password=' + self.passwd
        if outfile:
            chaine_connect = chaine_connect + ' --outfile='+outfile

        chaine = " --".join((prog, chaine_connect, 'file='+file))
#        print ('loader ', chaine)
        env = os.environ
        if not logfile:
            fini = subprocess.run(chaine, env=env, stderr=subprocess.STDOUT)
#        else:
#            fini = subprocess.run(chaine, env=env, stdout=logfile, stderr=subprocess.STDOUT)
        if fini.returncode:
            print('sortie en erreur ', fini.returncode, fini.args, fini.stderr)

    def setenv(self):
        '''positionne les variables d'nevironnement pour les programmes externes '''
        orahome = self.params.get_param("feaora_oracle_home", groupe=self.code)
        env = dict(os.environ)
#        print('modif_environnement ',env)
        if orahome: # on manipule les variables d'environnement
            env['ORACLE_HOME'] = orahome
            env['PATH'] = orahome+'\\bin;'+env['PATH']
        return env

    def lanceur(self, helper, xml, paramfile, outfile, wait=True):
        '''gere le programme externe '''
        chaine = helper + ' -c '+paramfile
        encoding = 'cp1252'
        if self.params.get_param('noload') == '1': #simulation de chargement pour debug
            print('extrunner elyx: mode simulation -------->', chaine)
            print('extrunner elyx: param_file \n', '\n'.join(xml))
            return True

        with open(paramfile, mode='w', encoding=encoding) as tmpf:
            tmpf.write('\n'.join(xml))

        env = self.setenv()
        if wait:
            fini = subprocess.run(chaine, env=env)
            if fini.returncode:
                print('sortie en erreur ', fini.returncode, fini.args, fini.stderr)
                return False
            return True
        else:
            outdesc = open(outfile, mode='w', encoding='cp1252')
            process = subprocess.Popen(chaine, env=env, stdout=outdesc,
                                       stderr=subprocess.STDOUT, universal_newlines=True)
            return process
#            time.sleep(10000)


    def singlerunner(self, helper, xml, nom):
        '''lance les exports ou les imports a partitr du fichier xml'''
        with tempfile.TemporaryDirectory() as tmpdir:
            paramfile = os.path.join(tmpdir, 'param_FEA.xml')
            outfile = os.path.join(tmpdir, '_'.join(nom)+'_out_FEA.txt')
            return self.lanceur(helper, xml, paramfile, outfile)


    def extload(self, helper, file, logfile=None):
        '''charge un fichier par FEA2ORA'''
        reinit = self.params.get_param('reinit', '0') if self.params else '0'
#        print('valeur de reinit',self.params.nompyetl, self.params.get_param('reinit'))
        nom = os.path.splitext(os.path.basename(file))[0]
        csystem = os.path.join(os.path.dirname(helper), r'syscoord\sysgeo.dat')
        logobject = os.path.join(logfile, 'log_import.txt')
        loadxml = ['<Fea2OraConfig>',
                   '<oraCnx cnx="'+self.serveur+'" user="'+self.user+'" pwd="'
                   +self.passwd+'" role=""/>',
                   '<apicBase name="'+self.base+'" version="5"/>',
                   '<filePath>',
                   '<srcFile path="'+file+'"/>',
                   '<reportDir path="'+logfile+'"/>',
                   '<logDir path="'+logfile+'"/>',
                   '<coordinateSystem sysgeoPath="'+csystem+'" sysgeoValue=""/>',
                   '<logObject path="'+logobject+'"/>',
                   '</filePath>',
                   '<checkOption>',
                   '<creationDate value="1"/>',
                   '<attribute value="1"/>',
                   '<commitDelay value="1000"/>',
                   '<geomInSpace value="1"/>',
                   '<doublePoints value="1"/>',
                   '<dimension value=""/>',
                   '<section value="1"/>',
                   '<replaceObj value="'+reinit+'"/>',
                   '<conformNbCar value="0"/>',
                   '<conformEnum  value="2"/>',
                   '<validateGeometry value="1" allowSelfIntersectSurface="0"'+
                   ' allowDoublePoints="0" />',
                   '</checkOption>',
                   '</Fea2OraConfig>']

        retour = self.singlerunner(helper, loadxml, nom)
        return retour

    def genexportxml(self, destination, log, classes):
        '''prepare les fichiers de confix xml pour l'export'''
        return ['<Ora2FeaConfig>',
                '<oraCnx cnx="'+self.serveur+'" user="'+self.user+'" pwd="'+
                self.passwd+'" role=""/>',
                '<apicBase name="'+self.base+'" version="5"/>',
                '<filePath>',
                '<dstFile path="'+destination+'"/>',
                '<logDir path="'+log+'"/>',
                '</filePath>',
                '<classes list="'+','.join([i[1] for i in classes])+'"/>',
                '<coordinateSystem value="0"/>',
                '</Ora2FeaConfig>']


    def log_decoder(self, idexport, outfile, size, resultats):
        '''decode un fichier log de ORA2FEA'''

        for i in open(outfile, 'r', encoding='cp1252').readlines():
#                print('lu:', i)
            if "Nombre d'objets export" in i:
                tmp = i.split(':')
                classe = tmp[-2].split(' ')[-1]
                niveau = idexport[0]
                idclasse = (niveau, classe)
                exportes = int(tmp[-1][:-1])
                resultats[idclasse] = exportes
                if len(idexport) == 1:
                    print('%-45s objets exportes: %10d ' %
                          ('.'.join(idclasse), exportes))
            if "Nombre total d'objets export" in i:
                print('%-33s objets: %10d exportes: %10d '
                      % ('.'.join(idexport), size[idexport], int(i.split(':')[-1][:-1])))



    def export_statprint(self, slot, pool, runcode, size, resultats):
        '''affiche une stat d'export'''

        if pool[slot] is not None:
#                    print('fini', slot, pool[slot].returncode, pool[slot].args)
            idexport, outfile = runcode[slot]
            self.log_decoder(idexport, outfile, size, resultats)
            pool[slot] = None



    def multidump(self, helper, base, classes, dest, log, fanout):
        '''prepare une extraction multiple '''
        blocks = dict()
        size = dict()
        runcode = dict()
        resultats = dict()
        maxworkers = self.params.get_param('max_export_workers', 1)
        if maxworkers < 0:
            nprocs = os.cpu_count()
            if nprocs is None:
                nprocs = 1
            maxworkers = -nprocs*maxworkers
        pool = {i:None for i in range(maxworkers)}
        schemabase = self.schemabase
        for i in classes:
            print('traitement classe', i, schemabase.classes[i].info['objcnt_init'])
            if schemabase.classes[i].info['objcnt_init'] == '0':
                print('classe vide ', i)
                resultats[i] = 0
                continue
            if fanout == 'niveau':
                if (i[0], ) in blocks:
                    blocks[(i[0], )].append(i)
                    size[(i[0], )] += int(schemabase.classes[i].getinfo('objcnt_init', '0'))
                else:
                    blocks[(i[0], )] = [i]
                    size[(i[0], )] = int(schemabase.classes[i].getinfo('objcnt_init', '0'))
            else:
                blocks[i] = [i]
                size[i] = int(schemabase.classes[i].getinfo('objcnt_init', '0'))
        with tempfile.TemporaryDirectory() as tmpdir:
#            total = len(blocks)
            for nom in blocks:
#                print('traitement', nom, size[nom], blocks[nom])
                destination = os.path.join(dest, *nom)
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                logdir = os.path.join(log, nom[0])
                os.makedirs(logdir, exist_ok=True)
                xml = self.genexportxml(destination, logdir, blocks[nom])
                paramfile = os.path.join(tmpdir, '_'.join(nom)+'_param_FEA.xml')
                outfile = os.path.join(tmpdir, '_'.join(nom)+'_out_FEA.txt')
                slot = get_slot(pool) # on cherche une place
                self.export_statprint(slot, pool, runcode, size, resultats)

                runcode[slot] = (nom, outfile)
                pool[slot] = self.lanceur(helper, xml, paramfile, outfile, wait=False)
                time.sleep(0.1)
            wait_end(pool)
            for slot in pool:
                self.export_statprint(slot, pool, runcode, size, resultats)
        return resultats


    def extdump(self, helper, base, classes, dest, log):
        '''extrait des donnees par ORA2FEA'''
        # mise en place de l'environnement:
        fanout = self.params.get_param('fanout', 'no')
        if fanout == 'no' or len(classes) == 1:
            noms = {i[1] for i in classes}
            nom = noms.pop() if len(noms) == 1 else 'export'
            destination = os.path.join(dest, nom)
            exportxml = self.genexportxml(destination, log, classes)
            if self.singlerunner(helper, exportxml, nom):
                retour = []
        else:
            retour = self.multidump(helper, base, classes, dest, log, fanout)
        return retour



    def traite_defaut(self, nom_att, defaut):
        '''analyse les defauts et les convertit en fonctions internes'''
        if defaut is None:
            return defaut
        resultat = defaut
        if defaut.startswith('!GENNUM'):
            compteur = defaut[9:-2]
            resultat = 'S.'+compteur
            self.schemabase.compteurs[compteur] += 1
            return resultat
        elif defaut.startswith('!GENSUR'):
            resultat = 'TIN.'+defaut[8:-2]
            return resultat
        elif defaut.startswith('!AUTEUR'):
            resultat = 'F.AUTEUR'
            return resultat
        elif defaut.startswith('!CALDAT'):
            resultat = 'now()'
            return resultat
        elif defaut.startswith('="') and defaut.endswith('"') and not '+' in defaut:
            resultat = defaut[1:].replace("'", "''").replace('"', "'")
            return resultat
#        print(nom_att, 'valeur defaut', defaut, '->', resultat)
        resultat = None
        return resultat

    def traite_enums_en_table(self):
        ''' fait le menage dans les enums speciales'''
        for nom in self.schemabase.conformites:
            if self.schemabase.conformites.special:
                print('traitement ', nom)


    def get_type(self, nom_type):

        return self.types_base.get(nom_type.upper(), 'T')

    def get_tables(self):
        return list(self.tables.values())

    def get_enums(self):
        ''' recupere la description de toutes les enums depuis la base de donnees '''
#        print("conformites")
        schema = self.adminschema
        enums_en_table = dict()
        requete = self.constructeur(schema, "APICD_CONFORMITE",
                                    ["NUMERO_AD", "ACTION", "VERSION", "NUMERO_MODELE", "NOM",
                                     "ENUM_OBJCLASS", "ENUM_KEY_ATTRIBUTE",
                                     "ENUM_VALUE_ATTRIBUTE", "ENUM_ORDER_ATTRIBUTE", "ENUM_FILTER"])


        dict_conf = self.menage_version(self.request(requete, ()), 1, 0, 2)
        self.get_attributs()

        #liste_conf=menage_version(liste_conf.values(),1,4,2)
        def_enums = dict()
        for i in dict_conf.values():
            self.confs[i[0]] = i[4]
            if i[5]: # attention c'est un truc_special
                noms_schema, nom_table = self.compos_id[i[5]]
                filtredef = i[9].split('=')
                champ_filtre = filtredef[0]
                val_filtre = filtredef[1].strip("'")
                champ_clef = self.attributs[i[6]][2]
                champ_val = self.attributs[i[7]][2]
                champ_ordre = self.attributs[i[8]][2]
                enums_en_table[i[4]] = (noms_schema, nom_table, champ_filtre, val_filtre,
                                        champ_clef, champ_val, champ_ordre)
                def_enums[(noms_schema, nom_table, champ_filtre, champ_clef,
                           champ_val, champ_ordre)] = None




        requete = self.constructeur(schema, "APICD_CONFORMITEVALEUR",
                                    ["NUMERO_AD", "NUMERO_MODELE", "NOM", "NUMERO_CONF",
                                     "TEXTE", "ORDRE", "ACTION", "VERSION"])
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
            if def_enums: # cas particulier des enums en tables : il faut lire la table des enums:
                for table in def_enums:
                    noms_schema, nom_table, champ_filtre, champ_clef, champ_val, champ_ordre = table
#                    print('traitement table', table)
                    requete = self.constructeur(noms_schema, nom_table,
                                                [champ_filtre, champ_clef, champ_val, champ_ordre])
#                    print('requete base', requete)
                    def_enums[table] = self.request(requete)
#                    print ('valeurs en table',table,  valtable)

            for nom in enums_en_table:
                noms_schema, nom_table, champ_filtre, val_filtre, champ_clef, champ_val,\
                    champ_ordre = enums_en_table[nom]
                table = def_enums[noms_schema, nom_table, champ_filtre, champ_clef,
                                  champ_val, champ_ordre]
                enum = {i[1]: i for i in table if i[0] == val_filtre}
                for i in enum:
                    filtre, clef, val, ordre = enum[i]
#                    print ('enum_en_table',nom, ordre, clef, val)
                    enums.append((nom, int(ordre) if ordre else 0, clef, val, 1))

            #print "stockage_conformite",valeur,alias
#        print ('confs',self.confs)
        for i in self.attributs.values():
            conf = self.confs.get(i[9])
    #                    if conf is None:
    #                        print (nomschema, nomtable, nom_att,i[13], len(self.confs))
            if i[4] == "BOOLEEN":
                # (cas particulier des booleens on en fait une enum)
                conf = self.confs.get("BOOLEEN")
                i[4] = 'TEXT'
            i[9] = conf
        return enums

    def get_attributs(self):
        '''recupere le schema complet
            nomschema,nomtable,attribut,alias,type_attribut,graphique,multiple,defaut,obligatoire
            enum,dimension,num_attribut,index,uniq,clef_primaire,clef_etrangere,cible_clef'''
        schema = self.adminschema
        if self.attributs:
            return list(self.attributs.values())
        requete = self.constructeur(schema, "APICD_COMPOSANT",
                                    ["NOM", "ACTION", "VERSION", "NUMERO_AD", "ALIAS",
                                     "NATURE", "FERMETURE", "TRAIT", "ABSTRAIT",
                                     "ECHELLE_LIMITE", "ECHELLE_DISPARITION"])

        print("composants", len(self.confs))
        compos = self.menage_version(self.request(requete, ()), 1, 0, 2)
        compos = self.menage_version(list(compos.values()), 1, 3, 2)
        compos_id = dict()

        requete = self.constructeur(schema, "APICD_BASE_COMPOSANT",
                                    ["TALIAS", 'ACTION', 'VERSION', "NUMERO_AD",
                                     "NOMBREDIM", "SCHEMA"])
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
        #print ('tableau des dimensions',dimensions)
        #    cl=schema_oracle.setdefault_classe(nom)
        #    if i[4]==3 : cl.G3D=True
        #
        #    cl.groupe=i[5]
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
        dict_tailles = {(i[0], i[1]):i[2] for i in taille_tables}
#        print ('tailles',taille_tables)


        self.tables = dict()
        for i in compos.values():
            abstrait = i[8]
            if abstrait:
                continue
            geom_type = i[5]-1
            dimens = 2
            nom = i[0].replace("-", "_")
            groupe = nom_schema_elyx.get(nom, 'inconnu')
            if groupe != 'inconnu':
                dimens = dimensions[nom]
            else:
                print("error: elyx : groupe inconnu", i[0])
            if geom_type < 0:
                print("info : elyx :composant generique", i[0])
            else:
                ident = (groupe, nom)
                alias = i[4]
                nbobj = dict_tailles.get(ident, -1)
                self.tables[ident] = (groupe, nom, alias, geom_type, dimens, nbobj,
                                      'r', '', '', '', '')


                compos_id[i[3]] = ident  #lien numero nom
                #print "association ",i[3],i[0]
            #print cl.nom,cl.type_geom,cl.fermeture
        #print sorted(compos_nom)
        print(len(self.tables), "info : elyx : composants trouves", len(compos))

        requete = self.constructeur(schema, "APICD_ATTRIBUT",
                                    ["NUMERO_AD", "ACTION", "VERSION", "NUMERO_MODELE",
                                     "NUMERO_COMPOSANT", "NOM", "ALIAS", "NATURE",
                                     "MODIFICATION", "MULTIPLICITE", "TYPE",
                                     "OBLIGATOIRE", "DEFAUT", "NUMERO_CONF", "ORDRE"])

#        print("attributs")

        liste_atts = self.menage_version(self.request(requete, ()), 1, 0, 2)
        code_type = {1:"E", 2:"F", 3:"T", 4:"B", 5:"D"}

        for i in liste_atts.values():
#            print ('num_table',i[4])
            id_compo = compos_id.get(i[4])
            table = self.tables[id_compo]
            if id_compo:
                nomschema, nomtable = id_compo
                if id_compo in self.tables:
                    nom_att = i[5]
                    type_att = code_type[i[10]]
#                    if traite_enums:
                    conf = i[13]
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
                        print('elyx:ordre incoherent detecte ', nomschema, nomtable,
                              nom_att, ordre)
                        ordre = 0.01
                    alias = i[6]
                    multiple = i[9]
                    dimension = table[4]
#                    print (dimension,dimension==3)
#                    if defaut and 'S.' in defaut :
#                        print (nomtable,"attribut",nom,type_att, defaut)
#                    composant.stocke_attribut(nom, type_att, defaut, type_base,
#                                              True, ordre = ordre) # on force
#                    print ("nom_att ",nom_att)
                    attdef = [nomschema, nomtable, nom_att, alias, type_att, graphique,
                              multiple, defaut, obligatoire, conf, dimension, ordre, '',
                              '', '', '', '', 0, 0]
#                    print ('attribut',nomschema, nomtable, nom_att,conf)
                    self.attributs[i[0]] = attdef
                    if graphique:
                        attdef = [nomschema, nomtable, nom_att+'_X', 'X '+str(alias),
                                  'REEL', 'False', multiple, '', obligatoire, '',
                                  dimension, ordre+0.1, '', '', '', '', '', 0, 0]
                        self.attributs[i[0]+0.1] = attdef
                        attdef = [nomschema, nomtable, nom_att+'_Y', 'Y '+str(alias),
                                  'REEL', 'False', multiple, '', obligatoire, '',
                                  dimension, ordre+0.2, '', '', '', '', '', 0, 0]
                        self.attributs[i[0]+0.2] = attdef

                else:
                    print("error: elyx : attribut de composant inconnu", i, compos_id[0])
            else:
                print("error: elyx : nom_non trouve", i[4], i)
        self.compos_id = compos_id

        return list(self.attributs.values())




#import time

    def constructeur(self, schema, table, attributs):
        '''constructeur de requetes de lecture de tables de donnees'''
        return ' SELECT "'+'","'.join(attributs)+'" FROM "'+schema+'"."'+table+'"'

    def menage_version(self, liste, n_action, n_clef, n_version, n_groupe=-1, debug=0):
        '''extrait la bonne version d'un objet des tables systeme d'exlyx'''
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
        ''' recupere les droits old style '''
        schema_oracle = self.adminschema

        requete = self.constructeur(schema_oracle, "APICD_ROLE",
                                    ["NUMERO_AD", "ACTION", "VERSION", "NUMERO_MODELE",
                                     "NOM", "COMMENTAIRE"
                                    ])
        liste_roles = self.menage_version(self.request(requete, ()), 1, 0, 2, debug=0)
        print("roles valides", len(liste_roles))
#        print (liste_roles[2])

        requete = self.constructeur(schema_oracle, "APICD_ROLE_SOUSMODELE",
                                    ["NUMERO_AD", "ACTION", "VERSION", "NUMERO_MODELE",
                                     "NUMERO_ROLE_B"])


        liste_roles_sm = self.menage_version(self.request(requete, ()), 1, 0, 2, debug=0)



        requete = self.constructeur(schema_oracle, "APICD_ROLE_COMPOSANT",
                                    ["NUMERO_AD", "ACTION", "VERSION", "NUMERO_MODELE",
                                     "NUMERO_ROLE_SM", "NUMERO_COMPOSANT", "DROIT"
                                    ])

        liste_atts = self.menage_version(self.request(requete, ()), 1, 0, 2)
        liste = []
        print('definitions valides ', len(liste_atts))
        for i in liste_atts.values():
            num_role_sm = i[4]
            role_sm = liste_roles_sm.get(num_role_sm)
            if role_sm:
                num_role = role_sm[4]
                role = liste_roles.get(num_role)
                if role:
                    nom_role = role[4]
                else:
                    print('role inconnu', num_role)
                    continue
            else:
                print('role sm inconnu', num_role_sm)
                continue # le role a saute on ignore les droits
            num_compo = i[5]
            nom_compo = self.compos_id.get(num_compo)
            if nom_compo:
                groupe, classe = nom_compo
            else:
                continue
            droit = 'consult' if i[6] == 2 else 'admin'

#            print (nom_compo,nom_role,droit)
            liste.append(';'.join((nom_role, str(droit), groupe, classe, str(i[6]))))
        entete = 'nom_role;type_droit;schema;table'
        print("droits trouves ", len(liste))
        return (entete, liste)

    def select_droits(self, liste_tables=None):
        ''' recupere les droits nouvelle formule'''
        requete = '''SELECT "ROLE_NAME", "RIGHTS", "SCHEMA", "ORIGIN_TABLE_NAME"
                        FROM "''' + self.modelschema +'"."LXMD_OBJCLASS_VIEW"'

        if liste_tables:
            liste = []
            ref = set(liste_tables)
            liste = [';'.join([j if j is not None else '' for j in i])
                     for i in self.request(requete, ()) if (i[2], i[3]) in ref]
        else:
            liste = [';'.join([j if j is not None else '' for j in i])
                     for i in self.request(requete, ())]
        print('db_elyx---------selection droits elyx ', len(liste))
        entete = 'nom_role;type_droit;schema;table'
        return (entete, liste)

    def droits_attributaires(self, liste_tables=None):
        ''' recupere les droits sur les attributs'''
        requete = '''     SELECT r."NAME" as "ROLE",
                                ar."RIGHTS" AS "DROITS",
                                os.SCHEMA as "SCHEMA",
                                o."NAME"  as "CLASSE",
                                a."NAME" as "ATTRIBUT",
                                ro."RIGHTS" AS "DROITS_CLASSE"

        FROM "'''+self.modelschema+'''"."LXMD_ATTRIBUTE_ROLE" ar
        LEFT JOIN "'''+self.modelschema+'''."LXMD_ROLE" r
            ON r."GID"=ar."ROLE"
        LEFT JOIN "'''+self.modelschema+'''"."LXMD_ATTRIBUTE" a
            on ar."KEY_ATTRIBUTE" = a."GID"
        LEFT JOIN "'''+self.modelschema+'''"."LXMD_ATTRIBUTE_STORAGE" ats
            on ar."KEY_ATTRIBUTE" = ats."KEY_ATTRIBUTE"
        LEFT JOIN "'''+self.modelschema+'''"."LXMD_OBJCLASS" o on
            ats."KEY_OBJCLASS_STORAGE"=o."GID"
        LEFT JOIN "'''+self.modelschema+'''"."LXMD_OBJCLASS_STORAGE" os
            on os."KEY_OBJCLASS"=ats."KEY_OBJCLASS_STORAGE"
        LEFT JOIN "'''+self.modelschema+'''"."LXMD_OBJCLASS_ROLE" ro
            on  ro."KEY_OBJCLASS_STORAGE"=os."GID" AND ro."ROLE"=ar."ROLE"
                --WHERE ar."RIGHTS" != ro."RIGHTS" or ro.RIGHTS is NULL
                '''
        if liste_tables:
            liste = []
            ref = set(liste_tables)
            liste = [';'.join([j if j is not None else '' for j in i])
                     for i in self.request(requete, ()) if (i[2], i[3]) in ref]
        else:
            liste = [';'.join([j if j is not None else '' for j in i])
                     for i in self.request(requete, ())]

        print('db_elyx---------selection droits attributs elyx ', len(liste))
        entete = 'nom_role;type_droit;schema;table;attribut;droits_classe'
        return (entete, liste)



    def complement_table(self, liste_tables=None):
        '''recupere des informations complementaires sur les tables elyx notamment le theme'''
        requete = '''SELECT n."SCHEMA" as niveau,
                            oc."NAME" as classe,
                            t."NAME" as theme,
                            t."ALIAS" as alias_theme,
                            oc."MIN_SCALE" as ech_min,
                            oc."MAX_SCALE" as ech_max

        FROM "'''+self.modelschema+'''"."LXMD_OBJCLASS" oc
        LEFT JOIN "'''+self.modelschema+'''"."LXMD_THEME" t  on t."GID" = oc."THEME"
        LEFT JOIN "'''+self.modelschema+'''"."LXMD_OBJCLASS_STORAGE" n
        on oc."GID" = n."KEY_OBJCLASS"

        '''
        if liste_tables:
            liste = []
            ref = set(liste_tables)
            liste = [';'.join([j if j is not None else '' for j in i])
                     for i in self.request(requete, ()) if (i[0], i[1]) in ref]
        else:
            liste = [';'.join([str(j) if j is not None else '' for j in i])
                     for i in self.request(requete, ())]

        print('db_elyx---------selection complements table elyx ', len(liste))
        entete = 'niveau;classe;theme;alias_theme;ech_min;ech_max'
        return (entete, liste)

    def select_elements_specifiques(self, schema, liste_tables=None):
        ''' recupere des elements specifiques a un format et les stocke
        dans une structure du schema '''

        schema.elements_specifiques['roles'] = self.select_droits(liste_tables)
        schema.elements_specifiques['droits_attributs'] = self.droits_attributaires(liste_tables)
        schema.elements_specifiques['complements_table'] = self.complement_table(liste_tables)
        # on mappe les roles sur le schema initial
        droits_table = dict()
        for i in schema.elements_specifiques['roles'][1]:
            nom_role, type_droit, nomschema, table = i.split(';')
            ident = (nomschema, table)
            if ident not in droits_table:
                droits_table[ident] = [(nom_role, type_droit)]
            else:
                droits_table[ident].append((nom_role, type_droit))
        for i in droits_table:
            if i in schema.classes:
                schema.classes[i].specifique['roles'] = droits_table[i]
#        schema.specifique['roles_old']=self.select_droits_old()
        print('db_elyx---------specifique droits elyx ', schema.elements_specifiques.keys())




class GenSql(ora.GenSql):
    '''generation d'ordres sql directs'''
    pass
