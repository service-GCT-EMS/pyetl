reference formats
-----------------

====================        ==========    ===========
format                         lecture      ecriture
====================        ==========    ===========
#comptage                          non           oui
#dir                               oui           non
#poubelle                          non           oui
#print                             non           oui
#store                             non           oui
accdb                              oui           non
asc                                oui           oui
csv                                oui           oui
csvj                               non           oui
dbf                                oui           non
dxf                                oui           oui
fixed                              oui           non
geo                                non           oui
geojson                            oui           oui
gpkg                               oui           oui
gy                                 oui           non
interne                            oui           non
interne+s                          oui           non
json                               oui           oui
ligne                              oui           non
mdb                                oui           non
mif                                oui           oui
osm                                oui           non
pbf                                oui           non
qgs                                oui           non
qgz                                oui           non
qlr                                oui           non
shp                                oui           oui
sjson                              non           oui
spatialite                         oui           non
sql                                non           oui
sqlite                             oui           non
texte                              oui           oui
txt                                oui           oui
xlsm                               oui           non
xlsx                               oui           oui
xml                                oui           oui
====================        ==========    ===========

reference bases de donnees
--------------------------

====================        ==========    ===========
format                         lecture      ecriture
====================        ==========    ===========
csw                                oui           oui
elyx                               oui           oui
gpkg                               oui           oui
mem_sqlite                         oui           oui
ms_access                          oui           oui
ms_access_old                      oui           oui
mysql                              oui           oui
oracle                             oui           oui
oracle_spatial_ewkt                oui           oui
postgis                            oui           oui
postgres                           oui           oui
sigli                              oui           oui
spatialite                         oui           oui
sql                                oui           oui
sqlalc                             oui           oui
sqlite                             oui           oui
wfs                                oui           oui
wfs2                               oui           oui
====================        ==========    ===========

csw
...


Acces aux services web wfs

commandes disponibles :

    * requete getcapabilities et analyse des donnees disponibles


necessite la librairie owslib

il est necessaire de positionner les parametres suivant:



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



gpkg
....


Created on Wed Sep  7 08:33:53 2016

@author: 89965
acces gdal en mode base de donnees

mem_sqlite
..........


bases de donnees sqlite en memoire pour l execution directe de requetes sql

module experimental 

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

necessite la librairie cx_Oracle ou oracledb et un client oracle 64 bits

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



sqlalc
......


Acces aux bases de donnees via sqlalchemy

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


Acces aux services web wfs

commandes disponibles :

    * requete getcapabilities et analyse des donnees disponibles


necessite la librairie requests et l acces au loader psql pour le chargement de donnees

il est necessaire de positionner les parametres suivant:



wfs2
....


Acces aux services web wfs

commandes disponibles :

    * requete getcapabilities et analyse des donnees disponibles


necessite la librairie owslib

il est necessaire de positionner les parametres suivant:





format #comptage
................



poubelle avec comptage

format #dir
...........


lit des objets a partir d'un fichier csv


format #poubelle
................



pseudowriter ne fait rien :  poubelle

format #print
.............



poubelle avec comptage

format #store
.............



ecrit des objets dans le stockage interne

format accdb
............


prepare l objet virtuel declencheur pour la lecture en base access ou sqlite


format asc
..........


lecture d'un fichier asc et stockage des objets en memoire


format csv
..........


format csv en lecture


format csvj
...........




format dbf
..........


lit des objets a partir d'un fichier csv


format dxf
..........


lecture d'un fichier reconnu et stockage des objets en memoire


format fixed
............


 lecture d'un fichier decodage positionnel


format geo
..........




format geojson
..............


lecture d'un fichier json et stockage des objets en memoire


format gpkg
...........


lecture d'un fichier reconnu et stockage des objets en memoire


format gy
.........


boucle de lecture principale -> attention methode de reader


format interne
..............




format interne+s
................




format json
...........


lecture d'un fichier json et stockage des objets en memoire


format ligne
............


 lecture d'un fichier et creation d un objet par ligne


format mdb
..........


prepare l objet virtuel declencheur pour la lecture en base access ou sqlite


format mif
..........


lecture d'un fichier reconnu et stockage des objets en memoire


format osm
..........


lit des objets a partir d'un fichier xml osm


format pbf
..........


lit des objets a partir d'un fichier xml osm


format qgs
..........


lit les datasources des fichiers qgis


format qgz
..........


lit les datasources des fichiers qgs


format qlr
..........


lit les datasources des fichiers qgis


format shp
..........


lecture d'un fichier reconnu et stockage des objets en memoire


format sjson
............




format spatialite
.................


prepare l objet virtuel declencheur pour la lecture en base access ou sqlite


format sql
..........




format sqlite
.............


prepare l objet virtuel declencheur pour la lecture en base access ou sqlite


format texte
............


 lecture d'un fichier et stockage des objets en memoire de l'ensemble du texte en memmoire

ecrit un fichier dont le contenu est dans un attribut
    a partir d'un stockage memoire ou temporaire

format txt
..........


format sans entete le schema doit etre fourni par ailleurs


format xlsm
...........


lit des objets a partir d'un fichier csv


format xlsx
...........


lit des objets a partir d'un fichier csv

 ecrit des objets csv a partir du stockage interne

format xml
..........


lecture xml non implemente

ecrit un ensemble de fichiers xml a partir d'un stockage memoire ou temporaire