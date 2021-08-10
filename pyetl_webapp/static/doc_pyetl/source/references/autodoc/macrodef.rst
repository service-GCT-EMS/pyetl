reference macros
----------------

===========================================================   ========
                           macro                              fonction
===========================================================   ========
:ref:`#2d`                                                    convertit des coordonees 2d
:ref:`#2p` x;y;srid                                           convertit des coordonees x,y en attribut en point
:ref:`#aduser` nom;clef                                       recupere un nom d utilisateur sur active directory ou LDAP
:ref:`#analyse` force                                         analyse d'un jeu de donnees p:format force 
:ref:`#asc_upload` nom;dest_final;reinit;vgeom                chargement vers elyx
:ref:`#att_sigli` modif                                       ajoute les attributs standard a un schema
:ref:`#att_sigli_modif`                                       ajoute les attributs standard  date_maj / date_creation et auteur 
:ref:`#att_sigli_std`                                         ajoute les attributs standard  date_maj / date_creation
:ref:`#autoload` dest                                         charge les derniers resultats en base de donnees
:ref:`#batch_rt`                                              
:ref:`#bdiff` acces                                           sort un objet s il n existe pas en base
:ref:`#cc2cus`                                                reprojette des donnees cus en rgf93
:ref:`#cc482ll`                                               reprojette des donnees cus en rgf93
:ref:`#charge_osm`                                            
:ref:`#classe` classe                                         force la classe
:ref:`#cmd` cmd;v1;v2;v3;v4;v5                                
:ref:`#cmin`                                                  passe les noms de classe et de groupe en minuscule
:ref:`#convert_sigli` rep                                     
:ref:`#creclef`                                               
:ref:`#cree_schema` nom;dialecte;modif                        conversion de fichiers de structure en schema sql
:ref:`#cree_sql` nom;dialecte                                 conversion de schemas en sql
:ref:`#crypt_site_params`                                     prepare les acces personnalises aux bases
:ref:`#cus2cc48`                                              reprojette des donnees cus en rgf93
:ref:`#db_batch` nom_batch;famille_batch;force                passe les batchs actifs
:ref:`#db_batch_rt` bdef                                      lance le scheduler sur une liste de taches en base lecture unique
:ref:`#db_batch_suivi` bdef                                   lance le scheduler sur une liste de taches modifiables en base
:ref:`#db_list_batch` bdef;sortie                             liste des batchs definis en base 
:ref:`#dbaccess` acces;base;serveur;type;user;pass            positionne des elements d'acces a une base de donnees en direct
:ref:`#dbclean` acces;niveau;classe;nom                       cree un script de reset de la base de donnees
:ref:`#dbdump` acces;niveau;classe;rep_sortie;log             extraction d'un jeu de donnees d'une base de donnees avec un programme externe
:ref:`#dbextract` acces;niveau;classe;attribut;valeur;ordre   extraction d'un jeu de donnees d'une base de donnÃ©es
:ref:`#dbextract+gid` acces;niveau;classe;attribut;valeur     lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe
:ref:`#dblist` acces;requete                                  recuperation d'un jeu de donnees par requete directe dans une variable
:ref:`#dbrequest` acces;requete;niveau;classe                 recuperation d'un jeu de donnees par requete directe
:ref:`#dbschema` acces;niveau;classe;nom                      analyse une base de donnees
:ref:`#debug`                                                 
:ref:`#editparams` perso                                      
:ref:`#extract` niveau;classe                                 extraction de niveaux ou de classes
:ref:`#extract+gid` niveau;classe                             lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe
:ref:`#extract_donnees` schema                                scripts de passage en prod
:ref:`#extractm`                                              extraction en mode multiprocesseur
:ref:`#fakelist` valeur;n                                     genere une liste d'items numerotes pour les tests
:ref:`#fanout`                                                
:ref:`#fileschema` acces                                      
:ref:`#filter` champ;filtre                                   mange tous les objets qui ne satisfont pas la condition 
:ref:`#filtre` exp                                            filtrage d un fichier texte
:ref:`#ftpdownload` fich;acces;accdir                         charge des elements par ftp
:ref:`#fusion_schema` nom                                     fusion de schemas issus de traitements paralleles p:schema: racine des schemas a lire (*) lecture multiple >nom: nom du schema a creer
:ref:`#g2p` lon;lat                                           convertit des coordonees lat long en attribut en point cc48
:ref:`#geocode` adresse;filtres                               geocode des elements
:ref:`#geocode2cus` adresse;filtres                           geocode des elements et sort des points en cc48 cus
:ref:`#geocode_csv` adresse;scoremin;filtre;prefix            geocodage d'un fichier csv
:ref:`#geoextract` acces;niveau;classe;mode_geo;buffer        extraction d'un jeu de donnees d' une base par emprise p:format parametres serveur base chaine_connection niveau classe
:ref:`#getosm` dest                                           telecharge le fichier osm de l'alsace
:ref:`#gid`                                                   ajout d un gid si necessaire
:ref:`#grantsitr` schema                                      generation des scripts de grant
:ref:`#grid` x_orig;y_orig;pas;cases                          repartit les objets selon une grille
:ref:`#groupe` groupe                                         force le groupe
:ref:`#histo_cmp` rep_histo;traitement                        
:ref:`#histor` rep;date;workers                               convertit des bases en format historique
:ref:`#httpdownload` url;dest;rep                             charge des elements par ftp
:ref:`#ident` groupe;classe                                   force le groupe et la classe
:ref:`#indb` acces                                            precharge des donnees depuis une base pour comparaison
:ref:`#init_mp`                                               initialise un module en mode multiprocessing (ne fait rien et attends)

:ref:`#initdb` acces;nomfich                                  positionne des elements d'acces a une base de donnees
:ref:`#ll2cus`                                                reprojette des donnees cus en rgf93
:ref:`#log` message;level                                     
:ref:`#low` al                                                
:ref:`#mastercrypt` val                                       crypte un element avec la masterkey

:ref:`#mkcrypt` user                                          
:ref:`#mod` att;val;repl                                      
:ref:`#moi`                                                   
:ref:`#ora2pg`                                                passage de oracle vers postgis
:ref:`#ora2pg2` base;schema;classe                            passage de oracle vers postgis version locale
:ref:`#pass`                                                  placeholdermacro: s'il faut une macro qui ne fait rien(ne fait rien et passe les objets)

:ref:`#passage_dev` schema                                    
:ref:`#passage_prod` schema                                   
:ref:`#passage_schema` schema                                 scripts de passage en prod
:ref:`#prefix` prefix                                         prefixe la classe p:prefix: prefixe a ajouter a la classe
:ref:`#print`                                                 
:ref:`#printparams`                                           affichage
:ref:`#printvar` var                                          affichage variable
:ref:`#pwcrypt` clef                                          crypte les mots de passe
:ref:`#pwdecrypt` key                                         decrypte les mots de passe
:ref:`#pwprepare` ref                                         
:ref:`#pyetl_init_db`                                         initialise le schema pyetl pour travailler en base de donnees
:ref:`#regroupe` groupe;stocke_groupe                         force le groupe et le transfere sur un attribut

:ref:`#rename` old;new                                        modifie la classe p:old: partie a remplacer >new: partie de remplacement
:ref:`#reproj` orig;dest;grille                               convertit des coordonees du systeme orig vers dest
:ref:`#retour_elyx` dest;clef;orig                            retour des donnees vers elyx pour toutes les classes definires dans ELYPG
:ref:`#run` prog;params                                       execute une commande externe
:ref:`#runproc` nom;dest;params                               lancement fonction_sql
:ref:`#runsql` nom;dest                                       lancement script_sql
:ref:`#schema_sigli` nom_schema                               ajoute les attributs standard a un schema

:ref:`#scriptodb` nom;dest                                    charge un script en base
:ref:`#set` atts;vals;defaut                                  
:ref:`#sigli2elyx`                                            passage de sigli vers elyx : sortie asc suppression GID renommage attributs modifies
:ref:`#site_params` key;fin                                   affichage des parametres de connection stockes
:ref:`#sleep` duree                                           
:ref:`#stdvar`                                                variables de base appele par tous les autres elements

:ref:`#store` clef;code                                       
:ref:`#supp` atts                                             
:ref:`#test` n1;n2;a                                          test des variables
:ref:`#testpourluc`                                           aide speciale pour luc
:ref:`#timeselect` var                                        determine si un batch est executable en fonction de l'heure
:ref:`#to_sigli`                                              preparation d'un jeu de donnees formatage standard sigli p:format parametres serveur base chaine_connection niveau classe
:ref:`#ukcrypt`                                               
:ref:`#ukdecrypt`                                             
:ref:`#upload` fich;dest;destdir                              charge des elements par ftp
:ref:`#valide` niveau;classe                                  validation de niveaux ou de classes
:ref:`#version` full                                          affiche la version de pyetl
:ref:`#zip` source;destination                                zippe les resultats
===========================================================   ========



detail macros
-------------


#2d
...


convertit des coordonees 2d



#2p
...


convertit des coordonees x,y en attribut en point

parametres positionnels

* x:
* y:
* srid:



#aduser
.......


recupere un nom d utilisateur sur active directory ou LDAP

parametres positionnels

* nom:nom de l utilisateur
* clef:



#analyse
........


analyse d'un jeu de donnees p:format force 

parametres positionnels

* force:



#asc_upload
...........


chargement vers elyx

parametres positionnels

* nom:
* dest_final:
* reinit:
* vgeom:



#att_sigli
..........


ajoute les attributs standard a un schema

parametres positionnels

* modif:0/1 indique si la classe doit etre modifiee



#att_sigli_modif
................


ajoute les attributs standard  date_maj / date_creation et auteur 



#att_sigli_std
..............


ajoute les attributs standard  date_maj / date_creation



#autoload
.........


charge les derniers resultats en base de donnees

parametres positionnels

* dest:



#batch_rt
.........




#bdiff
......


sort un objet s il n existe pas en base

parametres positionnels

* acces:



#cc2cus
.......


reprojette des donnees cus en rgf93



#cc482ll
........


reprojette des donnees cus en rgf93



#charge_osm
...........




#classe
.......


force la classe

parametres positionnels

* classe:nouvelle classe



#cmd
....


parametres positionnels

* cmd:
* v1:
* v2:
* v3:
* v4:
* v5:



#cmin
.....


passe les noms de classe et de groupe en minuscule



#convert_sigli
..............


parametres positionnels

* rep:



#creclef
........




#cree_schema
............


conversion de fichiers de structure en schema sql

parametres positionnels

* nom:racine des fichiers de structure
* dialecte:type de sql a creer
* modif: 0/1 indique si la classe doit etre modifiee



#cree_sql
.........


conversion de schemas en sql

 * schema: racine des schemas a lire (*) lecture multiple;


parametres positionnels

* nom:
* dialecte:



#crypt_site_params
..................


prepare les acces personnalises aux bases

 * permet de gerer les acces specifiques par utilisateurs

 * le point de depart est le fichier site_params commun

 * les utilisateurs sont definis avec le mot de passe sous la forme

 *    passwd;motdepasse#(user1,user2...,#groupe1,#groupe2)#

 * chaque utilisateur defini sur une base recoit une clef userkey personnelle

 * et eventuellement une liste de groupes

 * en sortie il y a 2 fichiers: le fichier site_patrams crypte et le fichier des cles




#cus2cc48
.........


reprojette des donnees cus en rgf93



#db_batch
.........


passe les batchs actifs

parametres positionnels

* nom_batch:
* famille_batch:
* force:



#db_batch_rt
............


lance le scheduler sur une liste de taches en base lecture unique

parametres positionnels

* bdef:



#db_batch_suivi
...............


lance le scheduler sur une liste de taches modifiables en base

parametres positionnels

* bdef:



#db_list_batch
..............


liste des batchs definis en base 

parametres positionnels

* bdef:
* sortie:



#dbaccess
.........


positionne des elements d'acces a une base de donnees en direct

parametres positionnels

* acces:
* base:
* serveur:
* type:
* user:
* pass:



#dbclean
........


cree un script de reset de la base de donnees

parametres positionnels

* acces:
* niveau:
* classe:
* nom:



#dbdump
.......


extraction d'un jeu de donnees d'une base de donnees avec un programme externe

parametres positionnels

* acces:
* niveau:
* classe:
* rep_sortie:
* log:



#dbextract
..........


extraction d'un jeu de donnees d'une base de donnÃ©es

parametres positionnels

* acces:
* niveau:
* classe:
* attribut:
* valeur:
* ordre:



#dbextract+gid
..............


lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe

parametres positionnels

* acces:
* niveau:
* classe:
* attribut:
* valeur:



#dblist
.......


recuperation d'un jeu de donnees par requete directe dans une variable

parametres positionnels

* acces:
* requete:



#dbrequest
..........


recuperation d'un jeu de donnees par requete directe

parametres positionnels

* acces:
* requete:
* niveau:
* classe:



#dbschema
.........


analyse une base de donnees

parametres positionnels

* acces:base a analyser
* niveau:schema a analyser (exp reg)
* classe:classe a analyser (exp reg)
* nom:nom du fichier de sortie (exp reg)

variables utilisées

* mod:selection (V T M =)


macro utilisabe en service web

* url          : ws/dbschema
* format retour:xml



#debug
......




#editparams
...........


parametres positionnels

* perso:



#extract
........


extraction de niveaux ou de classes

parametres positionnels

* niveau:
* classe:



#extract+gid
............


lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe

parametres positionnels

* niveau:
* classe:



#extract_donnees
................


scripts de passage en prod

parametres positionnels

* schema:



#extractm
.........


extraction en mode multiprocesseur



#fakelist
.........


genere une liste d'items numerotes pour les tests

parametres positionnels

* valeur:texte a reproduire

* n:nombre de lignes


macro utilisabe en service web

* url          : ws/fakelist
* format retour:json



#fanout
.......




#fileschema
...........


parametres positionnels

* acces:



#filter
.......


mange tous les objets qui ne satisfont pas la condition 

parametres positionnels

* champ:
* filtre:



#filtre
.......


filtrage d un fichier texte

parametres positionnels

* exp:



#ftpdownload
............


charge des elements par ftp

parametres positionnels

* fich:
* acces:
* accdir:



#fusion_schema
..............


fusion de schemas issus de traitements paralleles p:schema: racine des schemas a lire (*) lecture multiple >nom: nom du schema a creer

parametres positionnels

* nom:



#g2p
....


convertit des coordonees lat long en attribut en point cc48

parametres positionnels

* lon:
* lat:



#geocode
........


geocode des elements

parametres positionnels

* adresse:
* filtres:



#geocode2cus
............


geocode des elements et sort des points en cc48 cus

parametres positionnels

* adresse:
* filtres:



#geocode_csv
............


geocodage d'un fichier csv

 * adresse:liste des champs adresse;;;;;;;;;;;

 * scoremin : limite de l'echec;;;;;;;;;;;

 * filtre : liste des champs filtres;;;;;;;;;;;


parametres positionnels

* adresse:
* scoremin:
* filtre:
* prefix:



#geoextract
...........


extraction d'un jeu de donnees d' une base par emprise p:format parametres serveur base chaine_connection niveau classe

parametres positionnels

* acces:
* niveau:
* classe:
* mode_geo:
* buffer:



#getosm
.......


telecharge le fichier osm de l'alsace

parametres positionnels

* dest:



#gid
....


ajout d un gid si necessaire

 * le gid n est ajoute que si la classe n a pas de clef primaire;;;




#grantsitr
..........


generation des scripts de grant

parametres positionnels

* schema:



#grid
.....


repartit les objets selon une grille

parametres positionnels

* x_orig:
* y_orig:
* pas:
* cases:



#groupe
.......


force le groupe

parametres positionnels

* groupe:nouveau groupe



#histo_cmp
..........


parametres positionnels

* rep_histo:
* traitement:



#histor
.......


convertit des bases en format historique

parametres positionnels

* rep:
* date:
* workers:



#httpdownload
.............


charge des elements par ftp

parametres positionnels

* url:
* dest:
* rep:



#ident
......


force le groupe et la classe

parametres positionnels

* groupe:nouveau groupe
* classe:nouvelle classe



#indb
.....


precharge des donnees depuis une base pour comparaison

parametres positionnels

* acces:



#init_mp
........


initialise un module en mode multiprocessing (ne fait rien et attends)




#initdb
.......


positionne des elements d'acces a une base de donnees

parametres positionnels

* acces:
* nomfich:



#ll2cus
.......


reprojette des donnees cus en rgf93



#log
....


parametres positionnels

* message:
* level:



#low
....


parametres positionnels

* al:



#mastercrypt
............


crypte un element avec la masterkey


parametres positionnels

* val:



#mkcrypt
........


parametres positionnels

* user:



#mod
....


parametres positionnels

* att:
* val:
* repl:



#moi
....




#ora2pg
.......


passage de oracle vers postgis



#ora2pg2
........


passage de oracle vers postgis version locale

parametres positionnels

* base:
* schema:
* classe:



#pass
.....


placeholdermacro: s'il faut une macro qui ne fait rien(ne fait rien et passe les objets)




#passage_dev
............


parametres positionnels

* schema:



#passage_prod
.............


parametres positionnels

* schema:



#passage_schema
...............


scripts de passage en prod

parametres positionnels

* schema:



#prefix
.......


prefixe la classe p:prefix: prefixe a ajouter a la classe

parametres positionnels

* prefix:



#print
......




#printparams
............


affichage



#printvar
.........


affichage variable

parametres positionnels

* var:



#pwcrypt
........


crypte les mots de passe

parametres positionnels

* clef:



#pwdecrypt
..........


decrypte les mots de passe

parametres positionnels

* key:



#pwprepare
..........


parametres positionnels

* ref:



#pyetl_init_db
..............


initialise le schema pyetl pour travailler en base de donnees



#regroupe
.........


force le groupe et le transfere sur un attribut


parametres positionnels

* groupe:nom du nouveau groupe

* stocke_groupe:nom de l'attribut contenant l'ancien groupe



#rename
.......


modifie la classe p:old: partie a remplacer >new: partie de remplacement

parametres positionnels

* old:
* new:



#reproj
.......


convertit des coordonees du systeme orig vers dest

parametres positionnels

* orig:
* dest:
* grille:



#retour_elyx
............


retour des donnees vers elyx pour toutes les classes definires dans ELYPG

parametres positionnels

* dest:
* clef:
* orig:



#run
....


execute une commande externe

parametres positionnels

* prog:
* params:



#runproc
........


lancement fonction_sql

parametres positionnels

* nom:
* dest:
* params:



#runsql
.......


lancement script_sql

parametres positionnels

* nom:
* dest:



#schema_sigli
.............


ajoute les attributs standard a un schema


parametres positionnels

* nom_schema:



#scriptodb
..........


charge un script en base

parametres positionnels

* nom:
* dest:



#set
....


parametres positionnels

* atts:
* vals:
* defaut:



#sigli2elyx
...........


passage de sigli vers elyx : sortie asc suppression GID renommage attributs modifies



#site_params
............


affichage des parametres de connection stockes

parametres positionnels

* key:
* fin:



#sleep
......


parametres positionnels

* duree:



#stdvar
.......


variables de base appele par tous les autres elements


variables utilisées

* format: format de sortie

* acces: acces base de donnees si necessaire
* dest: acces base de donnees en sortie si necessaire



#store
......


parametres positionnels

* clef:
* code:



#supp
.....


parametres positionnels

* atts:



#test
.....


test des variables

parametres positionnels

* n1:
* n2:
* a:



#testpourluc
............


aide speciale pour luc



#timeselect
...........


determine si un batch est executable en fonction de l'heure

parametres positionnels

* var:



#to_sigli
.........


preparation d'un jeu de donnees formatage standard sigli p:format parametres serveur base chaine_connection niveau classe



#ukcrypt
........




#ukdecrypt
..........




#upload
.......


charge des elements par ftp

parametres positionnels

* fich:
* dest:
* destdir:



#valide
.......


validation de niveaux ou de classes

parametres positionnels

* niveau:
* classe:



#version
........


affiche la version de pyetl

parametres positionnels

* full:

macro utilisabe en service web

* url          : ws/version
* format retour:text



#zip
....


zippe les resultats

parametres positionnels

* source:
* destination:

