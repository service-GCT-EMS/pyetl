# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 09:45:40 2017

@author: 89965
"""
import sqlite3
import os

base='entree/test_sqlite/MAJ_voirie_equipements_rue_data.sqlite'
connect=sqlite3.connect(base)
curs=connect.cursor()
table = curs.execute('select* from sqlite_master')
print ('\n'.join([str(i) for i in curs.fetchall()]))