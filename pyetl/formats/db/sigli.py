# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
from . import postgis
#from . import database

SCHEMA_CONF = "public"



class SgConnect(postgis.PgConnect):
    '''connecteur de la base de donnees postgres'''
    def __init__(self, serveur, base, user, passwd, debug=0, system=False,
                 params=None, code=None):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.gensql = GenSql(self)
        self.idconnect = 'sigli:'+base
        self.type_base = 'sigli'
        self.sys_cre = 'date_creation'
        self.sys_mod = 'date_maj'
        self.dialecte = 'sigli'
        self.schema_conf = SCHEMA_CONF


    @property
    def req_schemas(self):
        """sort la liste des schemas"""
        return''' select nomschema,commentaire from admin_sigli.info_schemas'''

    @property
    def req_tables(self):
        '''produit la liste des tables de la base de donnees'''
        return 'SELECT nomschema,nomtable,commentaire,type_geometrique,dimension,\
                nb_enreg,type_table,index_geometrique,clef_primaire,index,\
                clef_etrangere FROM admin_sigli.info_tables', None

    @property
    def req_enums(self):
        ''' recupere la description de toutes les enums depuis la base de donnees '''
        return 'SELECT nom_enum,ordre,valeur,alias,mode from admin_sigli.info_enums', None

    @property
    def req_attributs(self):
        '''recupere le schema complet'''
        return 'SELECT nomschema,nomtable,attribut,alias,type_attribut,graphique,\
                multiple,defaut,obligatoire,\
            enum,dimension,num_attribut,index,uniq,clef_primaire,clef_etrangere,cible_clef,0,0 \
            FROM admin_sigli.info_attributs order by nomschema,nomtable,num_attribut', None


    def spec_def_vues(self):
        '''recupere des informations sur la structure des vues
           (pour la reproduction des schemas en sql'''
        requete = '''SELECT nomschema,nomtable,definition,materialise
                     from admin_sigli.info_vues_utilisateur
                     '''
        vues = dict()
        vues_mat = dict()
        for i in self.request(requete, ()):
            ident = (i[0], i[1])
            if i[3]:
                vues_mat[ident] = i[2]
            else:
                vues[ident] = i[2]

#        print('sigli --------- selection info vues ', len(vues), len(vues_mat))
        return vues, vues_mat


    def prepare_conformites(self, schem, nom_conf, creation=False):
        '''prepare une conformite et verifie qu'elle fait partie de la base sinon la cree'''
#        raise
        conf = schem.conformites[nom_conf]
        if conf.valide_base:
            return True, ''
#        print ('preparation conformite sigli',nom_conf)
#        raise
        conf.nombase = self.gensql.ajuste_nom(conf.nom)
        contenu = []
        ctrl = set()
        for j in sorted(list(conf.stock.values()), key=lambda v: v[2]):
            #print (nom,j[0])
            valeur = j[0].replace("'", "''")
            if len(j[0]) > 62:
                print("valeur trop longue ", valeur, " : conformite ignoree", conf.nombase)
                return False, ''
            if valeur not in ctrl:
                contenu.append(valeur)
                ctrl.add(valeur)
            else: print("attention valeur ", valeur, "en double dans", conf.nombase)

        req = ''
        conf.valide_base = False
        if self.connection:
            if conf.nombase in self.connection.schemabase.conformites:
                # si elle existe on verifie qu'elle est bonne
                conf_base = self.schemabase.conformites[conf.nombase]
                conf_base = {j[0] for j in conf.stock.values()}
                if conf_base == ctrl:
                    conf.valide_base = True
                else:
                    req = "DROP TYPE "+self.schema_conf+"."+ conf.nombase +";\n"
            if conf.valide_base:
                return True, ''
            if creation:
                req += "CREATE TYPE "+self.schema_conf+"."+conf.nombase+\
                       " AS ENUM ('"+"','".join(contenu)+"');"
#                conf.valide_base = self.execrequest(self, req, ())
#TODO reinitialiser le schema de la base en memoire apres modif
        return conf.valide_base, req



class GenSql(postgis.GenSql):
    """classe de generation des structures sql"""
    def __init__(self, connection=None, basic=False):
        super().__init__(connection=connection, basic=basic)
        self.geom = True
        self.courbes = False
        self.schemas = True

        self.dialecte = 'sigli'
        self.defaut_schema = 'admin_sigli'
        self.schema_conf = SCHEMA_CONF



    def conf_en_base(self, conf):
        """valide si uneconformiteexisteen base"""
        return False, False


    def ajuste_nom(self, nom):
        ''' sort les caracteres speciaux des noms'''
#        nom=re.sub('['+"".join(self.remplace.keys())+"]",
#                     lambda x:self.remplace[x.group(0)],nom)
        nom = self.reserves.get(nom, nom)
        return nom

    def valide_base(self, conf):
        """valide un schema en base"""
        return False


    def prepare_conformite(self, schem, nom_conf, valide=False):
        '''prepare une conformite et verifie qu'elle fait partie de la base sinon la cree'''

        conf = schem.conformites[nom_conf]
        if valide and conf.valide_base:
            return True

        conf.nombase = self.ajuste_nom(conf.nom)

        req = ''
        valide, supp = self.conf_en_base(conf)
        if supp:
            req = "DROP TYPE "+self.schema_conf+"."+ conf.nombase +";\n"
        if not valide:
            req = req + "CREATE TYPE "+self.schema_conf+"."+conf.nombase +\
            " AS ENUM ('" + "','".join(conf.cc) +"');"
            conf.valide_base = self.connection.request(req, ())
        return conf.valide_base

# scripts de creation de tables


    def db_cree_table(self, schema, ident):
        '''creation d' une tables en direct '''
        req = self.cree_tables(schema, ident)
        if self.connection:
            return self.connection.request(req, ())

    def db_cree_tables(self, schema, liste):
        '''creation d'une liste de tables en direct'''
        if not liste:
            liste = [i for i in self.schema.classes if self.schema.classes[i].a_sortir]
        for ident in liste:
            self.db_cree_table(schema, ident)


# structures specifiques pour stocker les scrips en base
# cree 4 tables: Macros scripts batchs logs

    def init_pyetl_script(self, nom_schema):
        ''' cree les structures standard'''
        pass

    @staticmethod
    def _commande_reinit(niveau, classe, delete):
        '''commande de reinitialisation de la table'''
#        prefix = 'TRUNCATE TABLE "'+niveau.lower()+'"."'+classe.lower()+'";\n'

        if delete:
            return 'DELETE FROM "'+niveau.lower()+'"."'+\
                 classe.lower()+'";\n'
        return "SELECT admin_sigli.truncate_table('"+niveau.lower()+"','"+\
                 classe.lower()+"');\n"


    @staticmethod
    def _commande_sequence(niveau, classe):
        ''' cree une commande de reinitialisation des sequences'''
        return  "SELECT admin_sigli.ajuste_sequence('"+niveau.lower()+\
                              "','"+classe.lower()+"');\n"


    @staticmethod
    def _commande_trigger(niveau, classe, valide):
        ''' cree une commande de reinitialisation des sequences'''
        if valide:
            return  "SELECT admin_sigli.valide_triggers('"+niveau.lower()+\
                              "','"+classe.lower()+"');\n"
        return  "SELECT admin_sigli.devalide_triggers('"+niveau.lower()+\
                  "','"+classe.lower()+"');\n"
