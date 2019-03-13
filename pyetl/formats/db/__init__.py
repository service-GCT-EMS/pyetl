# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 17:37:44 2016

@author: 89965
description des formats de base de donnees connus
"""
import os
from collections import namedtuple
import importlib

DBDEF = namedtuple("database", ("acces", "gensql", "svtyp", "fileext", 'description',
                                'geomconverter', "geomwriter"))
#("acces", "gensql", "svtyp", "fileext", 'description')
def loadmodules():
    '''lit toutes les descriptions de format depuis le repertoire courant
    et enregistre les readers et writers'''
    databases = dict()

    for fich_module in os.listdir(os.path.dirname(__file__)):
        if fich_module.startswith("base_"):
            module = "."+os.path.splitext(fich_module)[0]
            try:
                format_def = importlib.import_module(module, package=__package__)
                for nom, desc in getattr(format_def, 'DBDEF').items():
                    if nom in databases:
                        print('attention : redefinition du format de base', nom)
                    databases[nom] = DBDEF(*desc, None, None)
                    # a ce stade les fonctions ne sont pas connues
            except (ImportError, AttributeError):
                print('module ', module[1:], 'non disponible')

    return databases

DATABASES = loadmodules()
#print ('chargement', READERS)









## declaration de bases de donnees'''
#from collections import namedtuple
#from . import database
#from . import postgres
#from . import postgres_gensql
#from . import postgis
#from . import oracle
#from . import oraclespatial
#from . import elyx
#from . import sigli
#from . import msaccess
#from . import base_sqlite
#
#DBDEF = namedtuple("database", ("acces", "gensql", "svtyp", "fileext", 'description'))
#
#DATABASES = {'postgres':DBDEF(postgres.PgConnect, postgres_gensql.GenSql,
#                              'server', '', 'base postgres générique'),
#             'postgis':DBDEF(postgis.PgConnect, postgis.GenSql,
#                             'server', '', 'base postgres avec postgis générique'),
#             'sigli':DBDEF(sigli.SgConnect, sigli.GenSql,
#                           'server', '', 'base postgres avec schema sigli'),
#             'oracle':DBDEF(oracle.OraConnect, oracle.GenSql,
#                            'server', '', 'base oracle générique'),
#             'oracle_s':DBDEF(oraclespatial.OraConnect, oraclespatial.GenSql,
#                              'server', '', 'base oracle spatial générique'),
#             'elyx':DBDEF(elyx.ElyConnect, elyx.GenSql,
#                          'server', '', 'base postgres générique'),
#             'access':DBDEF(msaccess.AccConnect, msaccess.GenSql,
#                            'file', '.mdb', 'base access générique'),
#             'access2016':DBDEF(msaccess.AccConnect, msaccess.GenSql,
#                                'file', '.accdb', 'base access 2016'),
#             'sqlite':DBDEF(base_sqlite.SqltConnect, base_sqlite.GenSql,
#                            'file', '.sqlite', 'base sqlite générique'),
#             'sl3':DBDEF(base_sqlite.SqltConnect, base_sqlite.GenSql,
#                         'file', '.sl3', 'base spatialite générique'),
#             'sql':DBDEF(database.DbConnect, database.GenSql, 'None', '', 'generique')
#            }
