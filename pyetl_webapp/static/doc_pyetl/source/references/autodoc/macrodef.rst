reference macros
----------------

=====================================================    ========
                           macro                         fonction
=====================================================    ========
#2d                                                      convertit des coordonees 2d
#2p x;y;srid                                             convertit des coordonees x,y en attribut en point
#aduser nom;clef                                         recupere un nom d utilisateur sur active directory ou LDAP
#analyse force                                           analyse d'un jeu de donnees p:format force 
#att_sigli modif                                         ajoute les attributs standard a un schema
#att_sigli_modif                                         ajoute les attributs standard  date_maj / date_creation et auteur 
#att_sigli_std                                           ajoute les attributs standard  date_maj / date_creation
#autoload dest                                           charge les derniers resultats en base de donnees
#batch_rt                                                
#bdiff acces                                             sort un objet s il n existe pas en base
#cc2cus                                                  reprojette des donnees cus en rgf93
#cc482ll                                                 reprojette des donnees cus en rgf93
#classe classe                                           force la classe p:classe: nouvelle classe
#cmd cmd;v1;v2;v3;v4;v5                                  
#cmin                                                    passe les noms de classe et de groupe en minuscule
#creclef                                                 
#cree_schema nom;dialecte;modif                          conversion de fichiers de structure en schema sql
#cree_sql nom;dialecte                                   conversion de schemas en sql
#crypt_site_params ref                                   prepare les acces personnalises aux bases
#cus2cc48                                                reprojette des donnees cus en rgf93
#db_batch nom_batch;famille_batch;force                  passe les batchs actifs
#db_batch_rt bdef                                        lance le scheduler sur une liste de taches en base lecture unique
#db_batch_suivi bdef                                     lance le scheduler sur une liste de taches modifiables en base
#db_list_batch bdef;sortie                               liste des batchs definis en base 
#dbaccess acces;base;serveur;type;user;pass              positionne des elements d'acces a une base de donnees en direct
#dbclean acces;niveau;classe;nom                         cree un script de reset de la base de donnees
#dbdump acces;niveau;classe;rep_sortie;log               extraction d'un jeu de donnees d'une base de donnees avec un programme externe
#dbextract acces;niveau;classe;attribut;valeur;ordre     extraction d'un jeu de donnees d'une base de donnÃ©es
#dbextract+gid acces;niveau;classe;attribut;valeur       lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe
#dblist acces;requete                                    recuperation d'un jeu de donnees par requete directe dans une variable
#dbrequest acces;requete;niveau;classe                   recuperation d'un jeu de donnees par requete directe
#dbschema acces;niveau;classe;nom                        analyse une base de donnees
#debug                                                   
#editparams perso                                        
#extract niveau;classe                                   extraction de niveaux ou de classes
#extract+gid niveau;classe                               lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe
#extractm                                                extraction en mode multiprocesseur
#fakelist valeur;n                                       genere une liste d'items numerotes pour les tests
#fanout                                                  
#fileschema acces                                        
#filter champ;filtre                                     mange tous les objets qui ne satisfont pas la condition 
#filtre exp                                              filtrage d un fichier texte
#ftpdownload fich;acces;accdir                           charge des elements par ftp
#fusion_schema nom                                       fusion de schemas issus de traitements paralleles p:schema: racine des schemas a lire (*) lecture multiple >nom: nom du schema a creer
#g2p lon;lat                                             convertit des coordonees lat long en attribut en point cc48
#geocode adresse;filtres                                 geocode des elements
#geocode2cus adresse;filtres                             geocode des elements et sort des points en cc48 cus
#geoextract acces;niveau;classe;mode_geo;buffer          extraction d'un jeu de donnees d' une base par emprise p:format parametres serveur base chaine_connection niveau classe
#gid                                                     ajout d un gid si necessaire
#grid x_orig;y_orig;pas;cases                            repartit les objets selon une grille
#groupe groupe                                           force le groupe p:groupe: nouveau groupe
#httpdownload url;dest                                   charge des elements par ftp
#ident groupe;classe                                     force le groupe et la classe p:groupe: nouveau groupe, classe:nouvelle classe
#indb acces                                              precharge des donnees depuis une base pour comparaison
#init_mp                                                 initialise un module en mode multiprocessing (ne fait rien et attends)

#initdb acces;nomfich                                    positionne des elements d'acces a une base de donnees
#ll2cus                                                  reprojette des donnees cus en rgf93
#log message;level                                       
#low al                                                  
#mastercrypt val                                         crypte un element avec la masterkey

#mkcrypt user                                            
#mod att;val;repl                                        
#moi                                                     
#ora2pg                                                  passage de oracle vers postgis
#pass                                                    placeholdermacro: s il faut une macro qui ne fait rien(ne fait rien et passe les objets)

#prefix prefix                                           prefixe la classe p:prefix: prefixe a ajouter a la classe
#print                                                   
#printparams                                             affichage
#printvar var                                            affichage variable
#pwcrypt clef                                            crypte les mots de passe
#pwdecrypt key                                           decrypte les mots de passe
#pwprepare ref                                           
#pyetl_init_db                                           initialise le schema pyetl pour travailler en base de donnees
#regroupe groupe;stocke_groupe                           force le groupe et le transfere sur un attribut

#rename old;new                                          modifie la classe p:old: partie a remplacer >new: partie de remplacement
#reproj orig;dest;grille                                 convertit des coordonees du systeme orig vers dest
#run prog;params                                         execute une commande externe
#runproc nom;dest;params                                 lancement fonction_sql
#runsql nom;dest                                         lancement script_sql
#schema_sigli nom_schema                                 ajoute les attributs standard a un schema

#scriptodb nom;dest                                      charge un script en base
#set atts;vals;defaut                                    
#sigli2elyx                                              passage de sigli vers elyx : sortie asc suppression GID renommage attributs modifies
#site_params key;fin                                     affichage des parametres de connection stockes
#sleep duree                                             
#stdvar                                                  variables de base appele par tous les autres elements

#supp atts                                               
#test n1;n2;a                                            test des variables
#testpourluc                                             aide speciale pour luc
#timeselect var                                          determine si un batch est executable en fonction de l'heure
#to_sigli                                                preparation d'un jeu de donnees formatage standard sigli p:format parametres serveur base chaine_connection niveau classe
#ukcrypt                                                 
#ukdecrypt                                               
#upload fich;dest;destdir                                charge des elements par ftp
#valide niveau;classe                                    validation de niveaux ou de classes
#version full                                            affiche la version de pyetl
#zip source;destination                                  zippe les resultats
=====================================================    ========



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



#classe
.......


force la classe p:classe: nouvelle classe

parametres positionnels

* classe:



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


parametres positionnels

* ref:fichier de parametres de sites commun a traiter




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



#geoextract
...........


extraction d'un jeu de donnees d' une base par emprise p:format parametres serveur base chaine_connection niveau classe

parametres positionnels

* acces:
* niveau:
* classe:
* mode_geo:
* buffer:



#gid
....


ajout d un gid si necessaire



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


force le groupe p:groupe: nouveau groupe

parametres positionnels

* groupe:



#httpdownload
.............


charge des elements par ftp

parametres positionnels

* url:
* dest:



#ident
......


force le groupe et la classe p:groupe: nouveau groupe, classe:nouvelle classe

parametres positionnels

* groupe:
* classe:



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



#pass
.....


placeholdermacro: s il faut une macro qui ne fait rien(ne fait rien et passe les objets)




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

* format: format de sortie>acces: acces base de donnees si necessaire:



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

