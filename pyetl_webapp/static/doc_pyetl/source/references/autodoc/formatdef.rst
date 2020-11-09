reference formats
-----------------

============           ==========    ===========
format                    lecture      ecriture
============           ==========    ===========
#comptage                     non           oui
#dir                          oui           non
#poubelle                     non           oui
#print                        non           oui
#store                        non           oui
accdb                         oui           non
asc                           oui           oui
csv                           oui           oui
dbf                           oui           non
dxf                           oui           oui
geo                           non           oui
geojson                       oui           oui
gpkg                          oui           oui
gy                            oui           non
interne                       oui           non
json                          oui           oui
ligne                         oui           non
mdb                           oui           non
mif                           oui           oui
osm                           oui           non
qgs                           oui           non
shp                           oui           oui
spatialite                    oui           non
sql                           non           oui
sqlite                        oui           non
text                          oui           oui
txt                           oui           oui
xlsx                          oui           oui
xml                           oui           oui
============           ==========    ===========

reference bases de donnees
--------------------------

============           ==========    ===========
format                    lecture      ecriture
============           ==========    ===========

elyx
....


Acces aux bases de donnees elyx

commandes disponibles :

    * lecture des structures et des droits
    * multi extraction en parallele par programme externe
    * chargement par programme externe

necessite la librairie cxOracle et un client oracle 64 bits

l'utilisation des loaders et extracteurs necessite les programmes FEA2ORA et ORA2FEA et un client oraccle 32 bits

il est necessaire de positionner les parametres suivant:



mem_sqlite
..........


bases de donnees sqlite en memoire pour l execution directe de requetes sql

module experimental non disponible

commandes disponibles :

    * creation de structures
    * chargement de donnees
    * lecture des structures
    * extraction des donnees
    * passage de commandes sql

pas de dependances externes


ms_access
.........


Acces aux bases de donnees ms access

commandes disponibles

    * lecture des structures
    * extraction de donnees


necessite la librairie pyodbc et le runtime access de microsoft

il est necessaire de positionner les parametres suivant:


ms_access_old
.............


Acces aux bases de donnees ms access

commandes disponibles

    * lecture des structures
    * extraction de donnees


necessite la librairie pyodbc et le runtime access de microsoft

il est necessaire de positionner les parametres suivant:


mysql
.....


Acces aux bases de donnees mysql

commandes disponibles :

    * lecture des structures
    * extraction multitables et par selection sur un attribut

necessite la librairie mysql-connector-python :

    conda install -c anaconda mysql-connector-python

il est necessaire de positionner les parametres suivant:


oracle
......


Acces aux bases de donnees oracle

commandes disponibles :

    * lecture des structures
    * extraction multitables et par selection sur un attribut

necessite la librairie cx_Oracle et un client oracle 64 bits

il est necessaire de positionner les parametres suivant:



oracle_spatial_ewkt
...................


Acces aux bases de donnees oracle spatial (locator)

commandes disponibles :

    * lecture des structures
    * extraction multitables et par selection sur un attribut ou geometrique

necessite la librairie cx_Oracle et un client oracle 64 bits

il est necessaire de positionner les parametres suivant:



postgis
.......


Acces aux bases de donnees postgis

commandes disponibles :

    * lecture des structures et de droits
    * lecture des fonctions et des triggers et tables distantes gestion des clefs etrangeres
    * extraction multitables et par selection sur un attribut et par geometrie
    * ecriture de structures en fichier sql
    * ecritures de donnees au format copy et chargment en base par psql
    * passage de requetes sql
    * insert et updates en base '(beta)'

necessite la librairie psycopg2 et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:



postgres
........


Acces aux bases de donnees postgis

commandes disponibles :

    * lecture des structures et de droits
    * lecture des fonctions et des triggers et tables distantes gestion des clefs etrangeres
    * extraction multitables et par selection sur un attribut et par geometrie
    * ecriture de structures en fichier sql
    * ecritures de donnees au format copy et chargment en base par psql
    * passage de requetes sql
    * insert et updates en base '(beta)'

necessite la librairie psycopg2 et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:



sigli
.....


Acces aux bases de donnees postgis

commandes disponibles :

    * lecture des structures et de droits
    * lecture des fonctions et des triggers et tables distantes gestion des clefs etrangeres
    * extraction multitables et par selection sur un attribut et par geometrie
    * ecriture de structures en fichier sql
    * ecritures de donnees au format copy et chargment en base par psql
    * passage de requetes sql
    * insert et updates en base '(beta)'
    * cree des styles qgis pqs defaut pour les classes en sortie

necessite la librairie psycopg2 et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:



spatialite
..........


Created on Wed Sep  7 08:33:53 2016

@author: 89965
acces a la base de donnees

sql
...


Acces aux bases de donnees postgis

commandes disponibles :

    * lecture des structures et de droits
    * lecture des fonctions et des triggers et tables distantes gestion des clefs etrangeres
    * extraction multitables et par selection sur un attribut et par geometrie
    * ecriture de structures en fichier sql
    * ecritures de donnees au format copy et chargment en base par psql
    * passage de requetes sql
    * insert et updates en base '(beta)'

necessite la librairie psycopg2 et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:



sqlite
......


Created on Wed Sep  7 08:33:53 2016

@author: 89965
acces a la base de donnees

wfs
...


acces services wfs pour extraction de donnees

@author: 89965
acces a la base de donnees

wfs2
....


acces services wfs pour extraction de donnees

@author: 89965
acces a la base de donnees

