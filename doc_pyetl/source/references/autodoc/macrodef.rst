reference macros
----------------

=========================  ========
     nom de la macro       fonction
=========================  ========
#2d                        convertit des coordonees 2d
#2p                        convertit des coordonees x,y en attribut en point cc48
#analyse                   analyse d'un jeu de donnees p:format force 
#att_sigli_modif           ajoute les attributs standard  date_maj / date_creation
#att_sigli_std             ajoute les attributs standard  date_maj / date_creation
#autoload                  charge les derniers resultats en base de donnees
#bdiff                     sort un objet s il n existe pas en base
#cc2cus                    reprojette des donnees cus en rgf93
#classe                    force la classe p:classe: nouvelle classe
#cmd                       passe une commande a la sauvage
#cmin                      passe les noms de classe en minuscules 
#cree_sql                  conversion de schemas en sql
#cus2cc48                  reprojette des donnees cus en rgf93
#db_batch                  passe les batchs actifs
#db_batch_rapid            lance le scheduler sur une liste de taches en base lecture unique
#db_batch_suivi            lance le scheduler sur une liste de taches modifiables en base
#db_list_batch             liste des batchs definis en base 
#dbaccess                  positionne des elements d'acces a une base de donnees en direct
#dbclean                   cree un script de reset de la base de donnees
#dbdump                    extraction d'un jeu de donnees d'une base de donnees avec un programme externe
#dbextract                 extraction d'un jeu de donnees d'une base de donnÃ©es
#dbextract+gid             lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe
#dbrequest                 recuperation d'un jeu de donnees par requete directe
#dbschema                  analyse une base de donnees
#debug                     
#editparams                
#extract                   extraction de niveaux ou de classes
#extract+gid               lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau classe
#fanout                    
#filter                    mange tous les objets qui ne satisfont pas la condition 
#ftpdownload               charge des elements par ftp
#fusion_schema             fusion de schemas issus de traitements paralleles p:schema: racine des schemas a lire (*) lecture multiple >nom: nom du schema a creer
#g2p                       convertit des coordonees lat long en attribut en point cc48
#geocode                   geocode des elements
commande
parametres
#geoextract                extraction d'un jeu de donnees d' une base par emprise p:format parametres serveur base chaine_connection niveau classe
#gid                       ajout d un gid si necessaire
#grid                      repartit les objets selon une grille
#groupe                    force le groupe p:groupe: nouveau groupe
#httpdownload              charge des elements par ftp
#ident                     force le groupe et la classe p:groupe: nouveau groupe, classe:nouvelle classe
#indb                      precharge des donnees depuis une base pour comparaison
#init_mp                   initialise un module en mode multiprocessing (ne fait rien et attends)
#initdb                    positionne des elements d'acces a une base de donnees
#ll2cus                    reprojette des donnees cus en rgf93
#low                       passe une liste d attributs en minuscule
#mod                       modif conditionelle de valeurs dans un champs
#ora2pg                    passage de oracle vers postgis
#prefix                    prefixe la classe p:prefix: prefixe a ajouter a la classe
#printparams               affichage
#printvar                  affichage variable
#pwcrypt                   crypte les mots de passe
#pyetl_init_db             
#regroupe                  force le groupe et le transfere sur un attribut p:groupe: nom du nouveau groupe>attribut: nom de l'attribut contenant l'ancien
#rename                    :modifie la classe p:old: partie a remplacer >new: partie de remplacement
#reproj                    convertit des coordonees du systeme orig vers dest
#run                       execute une commande externe
commande
parametres
#runproc                   lancement fonction_sql
#runsql                    lancement script_sql
#scriptodb                 charge un script en base
#set                       affectation  absolue de champs
#sigli2elyx                passage de sigli vers elyx : sortie asc suppression GID renommage attributs modifies
#site_params               affichage des parametres de connection stockes
fin
#stdvar                    variables de base appele par tous les autres elements
#test                      test des variables
#timeselect                determine si un batch est executable en fonction de l'heure
#to_sigli                  preparation d'un jeu de donnees formatage standard sigli p:format parametres serveur base chaine_connection niveau classe
#upload                    charge des elements par ftp
#valide                    validation de niveaux ou de classes
#version                   affiche la version de pyetl
#zip                       zippe les resultats
=========================  ========


