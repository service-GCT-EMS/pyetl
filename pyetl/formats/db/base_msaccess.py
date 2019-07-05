# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 11:49:29 2016

@author: 89965
acces a la base de donnees
"""
import os

# import sys
from pyodbc import connect as OdbcConnect, Error as OdbcError

# from pyetl.formats.csv import geom_from_ewkt, ecrire_geom_ewkt
from .database import DbConnect, DbGenSql


TYPES_A = {
    "T": "T",
    "VARCHAR": "T",
    "VARCHAR2": "T",
    "CLOB": "T",
    "CHAR": "T",
    "LONGCHAR": "T",
    "F": "F",
    "NUMBER": "F",
    "H": "H",
    "HSTORE": "H",
    "BLOB": "X",
    "LONGBINARY": "X",
    "SDO_GEOMETRY": "geometry",
    "DATETIME": "D",
    "ROWID": "E",
    "DOUBLE PRECISION": "F",
    "NUMERIC": "N",
    "DOUBLE": "F",
    "CURRENCY": "N",
    "BOOLEEN": "B",
    "BOOLEAN": "B",
    "S": "S",
    "SEQUENCE": "S",
    "SEQ": "S",
    "SERIAL": "S",
    "BYTE": "E",
    "BIT": "E",
    "COUNTER": "S",
    "INTERVALLE": "I",
    "OID": "I",
    "INTEGER": "E",
}


class AccConnect(DbConnect):
    """connecteur de la base de donnees """

    def __init__(self, serveur, base, user, passwd, debug=0, system=False, params=None, code=None):
        super().__init__(serveur, base, user, passwd, debug, system, params, code)
        self.types_base = TYPES_A
        #        print ('connection base access', serveur,base, user, passwd )
        self.connect()
        #        if self.connection is None:
        #            self.connection = dbaccess2(chembase, user, passwd)

        self.nombase = os.path.splitext(os.path.basename(base))[0]
        self.tables = set()
        self.set_tablelist()

    def connect(self):
        """ouvre l'acces a la base de donnees et lit le schema"""
        base = os.path.join(self.serveur, self.base)

        print("info : access: connection access", self.user, "*" * len(self.passwd), self.base)
        try:
            #        base = r"C:\outils\projet_mapper\test_mapper\entree\access\test.access"
            #        drv = 'DRIVER={Microsoft Access Driver (*.mdb,*.accdb)};'
            #        file = 'DBQ='+base+";"
            #        pwd = 'PWD='+passwd+";" if passwd else ""
            conn_str = r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};" r"DBQ=" + base + ";"

            self.connection = OdbcConnect(conn_str)

            #        connection = odbc.win_connect_mdb(base)
            return self.connection
        except OdbcError as exp:
            print("error: access pyodbc: utilisateur ou mot de passe errone sur la base access")
            print("error: access:", base, self.passwd)
            print(exp)
            #        sys.exit(1)
            #        raise
            return None

    def get_type(self, nom_type):
        """recupere un type a partir de son code"""
        return self.types_base.get(nom_type, "T")

    def dbclose(self):
        """ferme la base"""
        if self.connection:
            self.connection.close()

    def db_get_schemas(self):
        return ()

    def set_tablelist(self):
        """ produit la liste des tables pour definir les tables a recuperer (systeme ou pas) """
        if self.valide:
            cur = self.connection.cursor()
            for table in cur.tables():
                schema = table.table_schem if table.table_schem else ""
                nom = table.table_name
                if table.table_type == "SYSTEM TABLE" and not self.system:
                    continue
                self.tables.add((schema, nom))
        else:
            self.tables = set()

    def get_tables(self):
        """produit les objets issus de la base de donnees"""
        #        nom_groupe,nom_classe,alias_classe,type_geometrique,dimension,nb_obj,type_table,\
        #        index_geometrique,clef_primaire,index,clef_etrangere = i
        # selection de la liste des niveaux et classes
        cur = self.connection.cursor()
        #        cur2 = self.connection.cursor()
        #        print ('msaccess tables:')
        #        for i in cur.tables():
        #            print (i)
        tables = []
        for table in cur.tables():
            schema = table.table_schem if table.table_schem else ""
            nom = table.table_name
            if (schema, nom) in self.tables:
                rem = table.remarks if table.remarks else ""
                if table.table_type == "TABLE":
                    type_t = "r"
                elif table.table_type == "VIEW":
                    type_t = "v"
                elif table.table_type == "SYSTEM TABLE":
                    type_t = "s"
                else:
                    type_t = "x"
                taille = 0
                idt = ".".join((schema, nom)) if schema else nom
#                print ('calcul taille',self.request("select count(*) from "+idt,()))
                taille = self.request('select count(*) from "' + idt + '"', ())
#                taille = cur2.execute('select count(*) from "'+idt+'"').fetchval()
#                print ("taille table ",idt,taille)
                taille = taille[0][0] if taille else "0"
                nouv_table = [schema, nom, rem, 0, 0, taille, type_t, "", "", "", ""]
                tables.append(nouv_table)
        return tables

    def iterreq(self, requete, data, attlist=None, has_geom=False, volume=0):
        """iteration sur le retour"""
        if has_geom:
            print("erreur requete geometrique impossible", requete)
            return iter(())
        cur = self.execrequest(requete, data, attlist=attlist)
        if cur:
            try:
                yield from cur
            except OdbcError as err:
                print("error: access:erreur recuperation donnees", requete)
                print("parametres", err.args)

            #                raise
            cur.close()
            raise StopIteration

        self.decile = 1
        return iter(())

    def get_enums(self):
        """ recupere la description de toutes les enums depuis la base de donnees """
        #        requete = 'SELECT nom_enum,ordre,valeur,alias,mode from admin_sigli.info_enums'
        #        data = ()
        return iter(())  # pour le moment on ne sait pas gerer des enums dans access

    #        return self.iterreq(requete, data)

    def get_attributs(self):
        """recupere le schema complet
        nomschema,nomtable,attribut,alias,type_attribut,graphique,multiple,
        defaut,obligatoire,enum,dimension,num_attribut,index,uniq,clef_primaire,
        clef_etrangere,cible_clef,taille,decimales"""

        cur = self.connection.cursor()
        #        print('msaccess tables:')
        #        for i in cur.tables(tableType=(('TABLE'))):
        #            print(i)
        cur2 = self.connection.cursor()
        pkeys = dict()
        #        fkeys=dict()

        for tabledef in cur.tables():
            if (
                tabledef.table_schem if tabledef.table_schem else "",
                tabledef.table_name,
            ) in self.tables:
                tablename = tabledef.table_name
                #                primaryKeys(table, catalog=None, schema=None)
                #                print("table", tablename, tabledef.table_schem)
                #                , schema=tabledef.table_schem
                for pkey in cur2.statistics(tablename):
                    print("valeurs stat", pkey)
                    if pkey.index_name == "PrimaryKey":
                        pkeys[(tablename, pkey.column_name)] = "P:" + str(pkey.ordinal_position)
        #                for fkey in cur2.foreignKeys(table=tablename):
        #                    print('info : access: detection fk:', fkey.pkcolumn_name+
        #                          ':'+fkey.fktable_schem+
        #                          '.'+fkey.fktable_name+'.'+fkey.fkcolumn_name)
        #    #                fclefs=','.join(fkeys)

        #        print ('msaccess ',[i for i in cur.columns()])
        return [self.attdef(
                cd.table_schem if cd.table_schem else "",
                cd.table_name,
                cd.column_name,
                cd.remarks if cd.remarks else "",
                cd.type_name,
                "non",
                "non",
                "",
                "non" if cd.nullable else "oui",
                "",
                0,
                cd.ordinal_position,
                "",
                "",
                pkeys.get((cd.table_name, cd.column_name), ""),
                "",
                "",
                "",
                cd.column_size,
                cd.decimal_digits,
            )
            for cd in cur.columns()
            if (cd.table_schem if cd.table_schem else "", cd.table_name) in self.tables
        ]

    def construction_champs(self, schema, surf=False, long=False):
        """ construit la liste de champs pour la requete"""
        attlist = schema.get_liste_attributs()
        attlist2 = []
        for i in attlist:
            att = schema.attributs[i]
            # print ('dbaccess:type_attribut ', i,att.type_att)
            if att.type_att == "X":
                continue  # on ne sait pas traiter
            #            if att.type_att == 'D':
            #                attlist2.append("to_char(%s,'DD/MM/YYYY HH24:MI:SS')" % i)
            else:
                #                attlist2.append('Cstr("'+i+'")')
                attlist2.append('"' + i + '"')
        atttext = ",".join(attlist2)
        return atttext, attlist

    def req_alpha(self, ident, schema, attribut, valeur, mods, maxi=0, ordre=None):
        """recupere les elements d'une requete alpha"""
        niveau, classe = ident
        if attribut:
            atttext, attlist = self.construction_champs(schema, "S" in mods, "L" in mods)

            if isinstance(valeur, list):
                requete = (
                    ' SELECT "'
                    + atttext
                    + '" FROM "'
                    + niveau
                    + '"."'
                    + classe
                    + '" WHERE "'
                    + attribut
                    + '" = ANY (%s)'
                )
                data = ("{" + ",".join(valeur) + "}",)
            else:
                requete = (
                    ' SELECT "'
                    + atttext
                    + '" FROM "'
                    + niveau
                    + '"."'
                    + classe
                    + '" WHERE "'
                    + attribut
                    + '" ~ %s'
                )
                data = (valeur,)
        else:
            atttext, attlist = self.construction_champs(schema, "S" in mods, "L" in mods)
            requete = " SELECT " + atttext + " FROM " + niveau + "." + classe
            data = ()

        if ordre:
            if isinstance(ordre, list):
                requete = requete + " ORDER BY " + ",".join(ordre)
            else:
                requete = requete + " ORDER BY " + ordre
        #        print ('parametres',data,valeur)
        #        print ('dbaccess:requete de selection alpha',
        #           curs.mogrify(requete,data), niveau, classe)
        self.attlist = attlist
        #        print ('acces alpha',requete)
        return self.iterreq(requete, data)

    def req_geom(self, *_, **__):
        """pas de requete geometrique possible sur access"""
        return iter(())

    def get_elements_specifiques(self, _):
        """ recupere des elements specifiques a un format et les stocke dans
        une structure du schema """
        return


class AccGenSql(DbGenSql):
    """generateur sql de creation de base"""

    pass


DBDEF = {
    "ms_access": (AccConnect, AccGenSql, "file", ".accdb", "", "base access apres 2007"),
    "ms_access_old": (AccConnect, AccGenSql, "file", ".mdb", "", "base access avant 2007"),
}
