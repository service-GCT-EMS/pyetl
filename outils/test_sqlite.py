# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 22:35:51 2018

@author: claude
"""

import os

os.environ["PATH"] = (
    "C:/Users/89965/Mes Documents (local)/projet_mapper/mapper-0.8/mapper0_8/pyetl/bin;"
    + os.environ["PATH"]
)

# import apsw


def execrequest(connection, requete, data):

    cur = connection.cursor()
    #        print('sqlite:execution requete', requete)
    if data is not None:
        cur.execute(requete, data)
    else:
        cur.execute(requete)
    return cur.fetchall()


def spatialite_connect(*args, **kwargs):
    """returns a dbapi2.Connection to a SpatiaLite db
using the "mod_spatialite" extension (python3)"""
    import sqlite3

    con = sqlite3.dbapi2.connect(*args, **kwargs)
    con.enable_load_extension(True)
    cur = con.cursor()
    libs = [
        # SpatiaLite >= 4.2 and Sqlite >= 3.7.17, should work on all platforms
        ("mod_spatialite",),
        ("mod_spatialite", "sqlite3_modspatialite_init"),
        # SpatiaLite >= 4.2 and Sqlite < 3.7.17 (Travis)
        ("mod_spatialite.so", "sqlite3_modspatialite_init"),
        # SpatiaLite < 4.2 (linux)
        ("libspatialite.so", "sqlite3_extension_init"),
    ]
    found = False
    for lib, entry_point in libs:
        try:
            print("test", lib, entry_point)
            cur.execute("select load_extension('{}', '{}')".format(lib, entry_point))
        except sqlite3.OperationalError:
            continue
        else:
            found = True
            break
    if not found:
        raise RuntimeError("Cannot find any suitable spatialite module")
    cur.close()
    con.enable_load_extension(False)
    return con


connection = spatialite_connect(":memory:")
version = execrequest(connection, "select sqlite_version()", ())
print("ouverture sqlite memoire", version)
# execrequest(connection, 'SELECT load_extension("mod_spatialite");', None)
# execrequest(connection, "SELECT InitSpatialMetaData(1);", None)
# connection.commit()
