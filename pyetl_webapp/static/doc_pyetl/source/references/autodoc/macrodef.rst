reference macros
----------------

===========================================================   ========
                           macro                              fonction
===========================================================   ========
:ref:`#2d`                                                    convertit des coordonees 2d
:ref:`#2p` x;y;srid                                           convertit des coordonees x,y en attribut en point
:ref:`#adquery` condition;element;clef                        passe une requete LDAP
:ref:`#aduser` nom;clef                                       recupere un nom d utilisateur sur active directory ou LDAP
:ref:`#analyse` force                                         analyse d'un jeu de donnees
:ref:`#att_sigli` modif                                       ajoute les attributs standard a un schema
:ref:`#att_sigli_modif`                                       ajoute les attributs standard + date_maj et auteur 
:ref:`#att_sigli_std`                                         ajoute les attributs standard  date_maj / date_creation et le gid
:ref:`#attsave` att;nom;ext                                   stocke le contenu d'un attribut
:ref:`#autoload` dest                                         charge les derniers resultats en base de donnees
:ref:`#batch_rt`                                              
:ref:`#bdiff` acces                                           sort un objet s il n existe pas en base
:ref:`#cc2cus`                                                reprojette des donnees cus en rgf93
:ref:`#cc482ll`                                               reprojette des donnees cus en rgf93
:ref:`#change` att;old;new                                    
:ref:`#classe` classe;att                                     force la classe
:ref:`#cmd` cmd;v1;v2;v3;v4;v5                                passe une commande a la sauvage
:ref:`#cmin`                                                  passe les noms de classe et de groupe en minuscule
:ref:`#cree_schema` nom;dialecte;modif                        conversion de fichiers de structure en schema sql
:ref:`#cree_sql` nom;dialecte                                 conversion de schemas en sql
:ref:`#cus2cc48`                                              reprojette des donnees cus en rgf93
:ref:`#db_batch` nom_batch;famille_batch;force                passe les batchs actifs
:ref:`#db_batch_rt` bdef                                      lance le scheduler sur une liste de taches en base lecture unique
:ref:`#db_batch_suivi` bdef                                   lance le scheduler sur une liste de taches modifiables en base
:ref:`#db_list_batch` bdef;sortie                             liste des batchs definis en base 
:ref:`#dbaccess` acces;base;serveur;type;user;pass            positionne des elements d'acces a une base de donnees en direct
:ref:`#dbclean` acces;niveau;classe;nom;mod                   cree un script de reset de la base de donnees
:ref:`#dbdump` acces;niveau;classe;rep_sortie;log             extraction d'un jeu de donnees d'une base de donnees avec un programme externe
:ref:`#dbextract` acces;niveau;classe;attribut;valeur;ordre   extraction d'un jeu de donnees d'une base de donnÃ©es
:ref:`#dbextract+gid` acces;niveau;classe;attribut;valeur     lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe
:ref:`#dblist` acces;requete                                  affichage d'un jeu de donnees par requete directe dans une variable
:ref:`#dbrequest` acces;requete;niveau;classe                 recuperation d'un jeu de donnees par requete directe
:ref:`#dbschema` acces;niveau;classe;nom                      analyse une base de donnees
:ref:`#dbwrite` dest;niveau;classe;attributs                  chargement dans une base de donnees d'une base de donnÃ©es
:ref:`#debug`                                                 
:ref:`#dir`                                                   affichage d une liste recursive de fichiers
:ref:`#editparams` perso                                      
:ref:`#extract` niveau;classe                                 extraction de niveaux ou de classes a partir de fichiers
:ref:`#extract+gid` niveau;classe                             lecture d'un jeu de donnees d un repertoire avec ajout d un gid si necessaire
:ref:`#extractm`                                              extraction en mode multiprocesseur
:ref:`#fanout`                                                positionne le fanout a classe avec un mode de traitement par classe
:ref:`#fileschema` acces                                      
:ref:`#filter` champ;filtre                                   mange tous les objets qui ne satisfont pas la condition 
:ref:`#filtre` exp                                            filtrage d un fichier texte avec une regex
:ref:`#find` res;att;val;pat                                  
:ref:`#ftpdownload` fich;acces;accdir                         charge des elements par ftp
:ref:`#fusion_schema` nom                                     fusion de schemas issus de traitements paralleles p:schema: racine des schemas a lire (*) lecture multiple >nom: nom du schema a creer
:ref:`#g2p` lon;lat                                           convertit des coordonees lat long en attribut en point cc48
:ref:`#garder` atts                                           ne conserver que certains champs
:ref:`#geocode` adresse;filtres                               geocode des elements
:ref:`#geocode2cus` adresse;filtres                           geocode des elements et sort des points en cc48 cus
:ref:`#geoextract` acces;niveau;classe;rel_geo;buffer;champ   extraction d'un jeu de donnees d'une base par contour(le contour est l objet d entree)
:ref:`#geomfilter`                                            filtre les geometries pour eviter les erreurs
:ref:`#gid`                                                   ajout d un gid si necessaire
:ref:`#grid` x_orig;y_orig;pas;cases                          repartit les objets selon une grille
:ref:`#groupe` groupe                                         force le groupe
:ref:`#httpdownload` url;dest;rep                             charge des elements en http
:ref:`#ident` groupe;classe                                   force le groupe et la classe
:ref:`#indb` acces                                            precharge des donnees depuis une base pour comparaison
:ref:`#init_mp`                                               initialise un module en mode multiprocessing (ne fait rien et attends)
:ref:`#initdb` acces;nomfich                                  positionne des elements d'acces a une base de donnees
:ref:`#jette`                                                 mange tous les objets
:ref:`#linefilter`                                            filtre les lignes pour eviter les erreurs
:ref:`#liste_params` clef;val                                 liste les parametres d acces aux bases
:ref:`#ll2cus`                                                reprojette des donnees cus en rgf93
:ref:`#log` message;level                                     
:ref:`#low` al                                                passe une liste d attributs en minuscule
:ref:`#mastercrypt` val                                       crypte un element avec la masterkey
:ref:`#md5` source                                            calcule une somme md5 sur le fichier
:ref:`#mod` att;val;repl                                      modif conditionelle de valeurs dans un champs
:ref:`#moi`                                                   affiche le nom de l utilisateur courant
:ref:`#ora2pg`                                                passage de oracle vers postgis
:ref:`#pass`                                                  placeholdermacro: s'il faut une macro qui ne fait rien(ne fait rien et passe les objets)
:ref:`#prefix` prefix                                         prefixe la classe
:ref:`#print`                                                 
:ref:`#printparams`                                           affichage
:ref:`#printvar` var                                          affichage variable
:ref:`#pwcrypt` clef                                          crypte les mots de passe
:ref:`#pyetl_init_db`                                         initialise le schema pyetl pour travailler en base de donnees
:ref:`#regroupe` groupe;stocke_groupe                         force le groupe et le transfere sur un attribut
:ref:`#rename` old;new                                        
:ref:`#reproj` orig;dest;grille                               convertit des coordonees du systeme orig vers dest
:ref:`#run` prog;params                                       execute une commande externe
:ref:`#runproc` nom;dest;params                               lancement fonction_sql
:ref:`#runsql` nom;dest                                       lancement script_sql
:ref:`#s3upload` fich;acces;dest                              charge des elements en s3
:ref:`#schema_sigli` nom_schema                               ajoute les attributs standard a un schema
:ref:`#scriptodb` nom;dest                                    charge un script en base
:ref:`#set` atts;vals;defaut                                  affectation  absolue de champs
:ref:`#sigli2elyx`                                            passage de sigli vers elyx : sortie asc suppression GID renommage attributs modifies
:ref:`#site_params` key;fin                                   affichage des parametres de connection stockes
:ref:`#sleep` duree                                           
:ref:`#stdvar`                                                variables de base appele par tous les autres elements
:ref:`#supp` atts                                             suppression de champs
:ref:`#test` n1;n2;a                                          test des variables
:ref:`#timeselect` var                                        determine si un batch est executable en fonction de l'heure
:ref:`#to_sigli`                                              preparation d'un jeu de donnees formatage standard sigli p:format parametres serveur base chaine_connection niveau classe
:ref:`#upload` fich;dest;destdir                              charge des elements par ftp
:ref:`#valide` niveau;classe                                  validation de niveaux ou de classes par rapport a un schema
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

* x:x
* y:y
* srid:srid



#adquery
........


passe une requete LDAP

parametres positionnels

* condition:clause de recherche
* element:element recherche
* clef:items a recuperer



#aduser
.......


recupere un nom d utilisateur sur active directory ou LDAP

parametres positionnels

* nom:nom de l utilisateur
* clef:



#analyse
........


analyse d'un jeu de donnees

parametres positionnels

* force:force

variables utilisées

* max_conf:nombre de classes maxi d une enum



#att_sigli
..........


ajoute les attributs standard a un schema

parametres positionnels

* modif:0/1 ou f/t indique si la classe doit etre modifiee



#att_sigli_modif
................


ajoute les attributs standard + date_maj et auteur 



#att_sigli_std
..............


ajoute les attributs standard  date_maj / date_creation et le gid



#attsave
........


stocke le contenu d'un attribut

parametres positionnels

* att:att
* nom:nom
* ext:ext



#autoload
.........


charge les derniers resultats en base de donnees

parametres positionnels

* dest:dest



#batch_rt
.........




#bdiff
......


sort un objet s il n existe pas en base

parametres positionnels

* acces:acces



#cc2cus
.......


reprojette des donnees cus en rgf93



#cc482ll
........


reprojette des donnees cus en rgf93



#change
.......


parametres positionnels

* att:att
* old:chaine a remplacer
* new:chaine de remplacement



#classe
.......


force la classe

parametres positionnels

* classe:nouvelle classe
* att:att



#cmd
....


passe une commande a la sauvage

parametres positionnels

* cmd:cmd
* v1:v1
* v2:v2
* v3:v3
* v4:v4
* v5:v5



#cmin
.....


passe les noms de classe et de groupe en minuscule



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

 * schema: racine des schemas a lire (*) lecture multiple

parametres positionnels

* nom:nom
* dialecte:dialecte



#cus2cc48
.........


reprojette des donnees cus en rgf93



#db_batch
.........


passe les batchs actifs

parametres positionnels

* nom_batch:nom_batch
* famille_batch:famille_batch
* force:force



#db_batch_rt
............


lance le scheduler sur une liste de taches en base lecture unique

parametres positionnels

* bdef:bdef



#db_batch_suivi
...............


lance le scheduler sur une liste de taches modifiables en base

parametres positionnels

* bdef:bdef



#db_list_batch
..............


liste des batchs definis en base 

parametres positionnels

* bdef:bdef
* sortie:sortie



#dbaccess
.........


positionne des elements d'acces a une base de donnees en direct

 * cree un l equivalent d une entree site_params a la volee
 * non stocke dans site_params
 * cette macro s utilise en complement d une autre

parametres positionnels

* acces:nom du groupe
* base:nom de la base de donnees
* serveur:serveur et port
* type:type de la base de donnees
* user:utilisateur de connection
* pass:mot de passe



#dbclean
........


cree un script de reset de la base de donnees

parametres positionnels

* acces:acces
* niveau:niveau
* classe:classe
* nom:nom
* mod:mod



#dbdump
.......


extraction d'un jeu de donnees d'une base de donnees avec un programme externe

parametres positionnels

* acces:acces
* niveau:niveau
* classe:classe
* rep_sortie:rep_sortie
* log:log



#dbextract
..........


extraction d'un jeu de donnees d'une base de donnÃ©es

parametres positionnels

* acces:acces
* niveau:niveau
* classe:classe
* attribut:attribut
* valeur:valeur
* ordre:ordre



#dbextract+gid
..............


lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe

parametres positionnels

* acces:acces
* niveau:niveau
* classe:classe
* attribut:attribut
* valeur:valeur



#dblist
.......


affichage d'un jeu de donnees par requete directe dans une variable

parametres positionnels

* acces:acces
* requete:requete



#dbrequest
..........


recuperation d'un jeu de donnees par requete directe

parametres positionnels

* acces:acces
* requete:requete
* niveau:niveau
* classe:classe



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

* url          : mws/dbschema
* format retour:xml



#dbwrite
........


chargement dans une base de donnees d'une base de donnÃ©es

parametres positionnels

* dest:dest
* niveau:niveau
* classe:classe
* attributs:attributs



#debug
......




#dir
....


affichage d une liste recursive de fichiers



#editparams
...........


parametres positionnels

* perso:perso



#extract
........


extraction de niveaux ou de classes a partir de fichiers

 * effectue un filtrage apres lecture : peu efficace preferer les filtres de fichier si possible

parametres positionnels

* niveau:groupe a selectionner si vide pas de filtrage
* classe:classe a selectionner si vide pas de filtrage

variables utilisées

* schema:schema d entree sous forme de ficher de description csv
* multigeom:force les geometries en multiple si vrai(1 ou t)



#extract+gid
............


lecture d'un jeu de donnees d un repertoire avec ajout d un gid si necessaire

parametres positionnels

* niveau:groupe a selectionner si vide pas de filtrage
* classe:classe a selectionner si vide pas de filtrage

variables utilisées

* schema:schema d entree sous forme de ficher de description csv
* multigeom:force les geometries en multiple si vrai(1 ou t)



#extractm
.........


extraction en mode multiprocesseur



#fanout
.......


positionne le fanout a classe avec un mode de traitement par classe

variables utilisées

* format:format de sortie (asc par defaut)



#fileschema
...........


parametres positionnels

* acces:acces



#filter
.......


mange tous les objets qui ne satisfont pas la condition 

parametres positionnels

* champ:champ
* filtre:filtre



#filtre
.......


filtrage d un fichier texte avec une regex

parametres positionnels

* exp:regex de filtrage



#find
.....


parametres positionnels

* res:res
* att:att
* val:chaine a trouver
* pat:pat



#ftpdownload
............


charge des elements par ftp

parametres positionnels

* fich:fich
* acces:acces
* accdir:accdir=.



#fusion_schema
..............


fusion de schemas issus de traitements paralleles p:schema: racine des schemas a lire (*) lecture multiple >nom: nom du schema a creer

parametres positionnels

* nom:nom



#g2p
....


convertit des coordonees lat long en attribut en point cc48

parametres positionnels

* lon:lon
* lat:lat



#garder
.......


ne conserver que certains champs

parametres positionnels

* atts:liste d'attributs a conserver



#geocode
........


geocode des elements

parametres positionnels

* adresse:adresse
* filtres:filtres



#geocode2cus
............


geocode des elements et sort des points en cc48 cus

parametres positionnels

* adresse:adresse
* filtres:filtres



#geoextract
...........


extraction d'un jeu de donnees d'une base par contour(le contour est l objet d entree)

parametres positionnels

* acces:acces
* niveau:schema des classes a extraire (exp reg ou in:nom de fichier)
* classe:classes a extraire (exp reg)
* rel_geo:relation geometrique: dans_emprise,dans,intersecte,contient ou inverse en commencant par ! (!dans...)
* buffer:taille du buffer
* champ:champ



#geomfilter
...........


filtre les geometries pour eviter les erreurs



#gid
....


ajout d un gid si necessaire

 * le gid n est ajoute que si la classe n'a pas de clef primaire



#grid
.....


repartit les objets selon une grille

parametres positionnels

* x_orig:x_orig
* y_orig:y_orig
* pas:pas
* cases:cases



#groupe
.......


force le groupe

parametres positionnels

* groupe:nouveau groupe



#httpdownload
.............


charge des elements en http

parametres positionnels

* url:url
* dest:dest
* rep:rep



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

* acces:acces



#init_mp
........


initialise un module en mode multiprocessing (ne fait rien et attends)



#initdb
.......


positionne des elements d'acces a une base de donnees

parametres positionnels

* acces:acces
* nomfich:nomfich



#jette
......


mange tous les objets



#linefilter
...........


filtre les lignes pour eviter les erreurs



#liste_params
.............


liste les parametres d acces aux bases

parametres positionnels

* clef:clef
* val:val



#ll2cus
.......


reprojette des donnees cus en rgf93



#log
....


parametres positionnels

* message:message
* level:level



#low
....


passe une liste d attributs en minuscule

parametres positionnels

* al:param1liste de champs a passer en minuscule



#mastercrypt
............


crypte un element avec la masterkey

parametres positionnels

* val:val



#md5
....


calcule une somme md5 sur le fichier

parametres positionnels

* source:source



#mod
....


modif conditionelle de valeurs dans un champs

parametres positionnels

* att:att
* val:val
* repl:repl



#moi
....


affiche le nom de l utilisateur courant

variables utilisées

* ADserver:identification du serveur AD/LDAP a utiliser si pas de defaut systeme



#ora2pg
.......


passage de oracle vers postgis



#pass
.....


placeholdermacro: s'il faut une macro qui ne fait rien(ne fait rien et passe les objets)



#prefix
.......


prefixe la classe

parametres positionnels

* prefix: prefixe a ajouter a la classe



#print
......




#printparams
............


affichage



#printvar
.........


affichage variable

parametres positionnels

* var:var



#pwcrypt
........


crypte les mots de passe

parametres positionnels

* clef:clef



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


parametres positionnels

* old:chaine a remplacer
* new:chaine de remplacement



#reproj
.......


convertit des coordonees du systeme orig vers dest

parametres positionnels

* orig:orig
* dest:dest
* grille:grille



#run
....


execute une commande externe

parametres positionnels

* prog:prog
* params:params



#runproc
........


lancement fonction_sql

parametres positionnels

* nom:nom
* dest:dest
* params:params



#runsql
.......


lancement script_sql

parametres positionnels

* nom:nom
* dest:dest



#s3upload
.........


charge des elements en s3

parametres positionnels

* fich:fich
* acces:acces
* dest:dest



#schema_sigli
.............


ajoute les attributs standard a un schema

parametres positionnels

* nom_schema:nom_schema=#schemas



#scriptodb
..........


charge un script en base

parametres positionnels

* nom:nom
* dest:dest



#set
....


affectation  absolue de champs

parametres positionnels

* atts:atts
* vals:vals
* defaut:defaut



#sigli2elyx
...........


passage de sigli vers elyx : sortie asc suppression GID renommage attributs modifies



#site_params
............


affichage des parametres de connection stockes

parametres positionnels

* key:key
* fin:fin



#sleep
......


parametres positionnels

* duree:duree



#stdvar
.......


variables de base appele par tous les autres elements

variables utilisées

* format: format de sortie defaut csv
* acces: acces base de donnees si necessaire
* dest: acces base de donnees en sortie si necessaire



#supp
.....


suppression de champs

parametres positionnels

* atts:liste d'attributs a supprimer



#test
.....


test des variables

parametres positionnels

* n1:n1
* n2:n2=1
* a:a



#timeselect
...........


determine si un batch est executable en fonction de l'heure

parametres positionnels

* var:var



#to_sigli
.........


preparation d'un jeu de donnees formatage standard sigli p:format parametres serveur base chaine_connection niveau classe



#upload
.......


charge des elements par ftp

parametres positionnels

* fich:fich
* dest:dest
* destdir:destdir



#valide
.......


validation de niveaux ou de classes par rapport a un schema

 * si le niveau et la classe ne sont pas renseignes tout est traite

parametres positionnels

* niveau:niveau a traiter
* classe:classe a traiter

variables utilisées

* schema:schema a charger pour validation
* format: format de sortie defaut csv
* acces: acces base de donnees si necessaire
* dest: acces base de donnees en sortie si necessaire



#version
........


affiche la version de pyetl

parametres positionnels

* full:full

macro utilisabe en service web

* url          : mws/version
* format retour:text



#zip
....


zippe les resultats

parametres positionnels

* source:source
* destination:destination

