# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 22:35:51 2018

@author: claude
"""

import os

os.environ['PATH'] ='C:/Users/89965/Mes Documents (local)/projet_mapper/mapper-0.8/mapper0_8/pyetl/bin;'+os.environ['PATH']

import sqlite3

def execrequest(connection, requete, data):

    cur = connection.cursor()
#        print('sqlite:execution requete', requete)
    if data is not None:
        cur.execute(requete, data)
    else:
        cur.execute(requete)
    return cur.fetchall()


connection = sqlite3.connect(":memory:")
version = execrequest(connection, 'select sqlite_version()', ())
print ('ouverture sqlite memoire', version)
connection.enable_load_extension(True)
connection.execute('SELECT load_extension("mod_spatialite");')
connection.execute('SELECT InitSpatialMetaData(1);')
connection.commit()




