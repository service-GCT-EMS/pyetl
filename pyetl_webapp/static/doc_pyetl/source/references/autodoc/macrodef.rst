reference macros
----------------

=========================  ========
     nom de la macro       fonction
=========================  ========
#2d                        convertit des coordonees 2
#2p                        convertit des coordonees x,y en attribut en poin
#aduser                    
#analyse                   analyse d'un jeu de donnees p:format force
#asc_upload                chargement vers ely
#att_sigli                 ajoute les attributs standard a un schema
#att_sigli_modif           ajoute les attributs standard  date_maj / date_creation et auteur
#att_sigli_std             ajoute les attributs standard  date_maj / date_creatio
#autoload                  charge les derniers resultats en base de donnee
#batch_rt                  
#bdiff                     sort un objet s il n existe pas en bas
#cc2cus                    reprojette des donnees cus en rgf9
#cc482ll                   reprojette des donnees cus en rgf9
#charge_osm                
#classe                    force la classe p:classe: nouvelle class
#cmd                       
#cmin                      passe les noms de classe en minuscules
#convert_sigli             
#creclef                   
#cree_schema               conversion de fichiers de structure en schema sql
#cree_sql                  conversion de schemas en sql
#crypt_site_params         prepare les acces personnalises aux base
#cus2cc48                  reprojette des donnees cus en rgf9
#db_batch                  passe les batchs actif
#db_batch_rt               lance le scheduler sur une liste de taches en base lecture uniqu
#db_batch_suivi            lance le scheduler sur une liste de taches modifiables en bas
#db_list_batch             liste des batchs definis en base
#dbaccess                  positionne des elements d'acces a une base de donnees en direc
#dbclean                   cree un script de reset de la base de donnee
#dbdump                    extraction d'un jeu de donnees d'une base de donnees avec un programme extern
#dbextract                 extraction d'un jeu de donnees d'une base de donnÃ©e
#dbextract+gid             lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau class
#dblist                    recuperation d'un jeu de donnees par requete directe dans une variabl
#dbrequest                 recuperation d'un jeu de donnees par requete direct
#dbschema                  analyse une base de donnee
#debug                     
#editparams                
#extract                   extraction de niveaux ou de classe
#extract+gid               lecture d'un jeu de donnees d' une base avec ajout d un gid si necessaire p:format parametres serveur base chaine_connection niveau class
#extract_donnees           scripts de passage en pro
#extractm                  extraction en mode multiprocesseu
#fakelist                  genere une liste d'items numerotes
#fanout                    
#fileschema                
#filter                    mange tous les objets qui ne satisfont pas la condition
#filtre                    filtrage d un fichier text
#ftpdownload               charge des elements par ft
#fusion_schema             fusion de schemas issus de traitements paralleles p:schema: racine des schemas a lire (*) lecture multiple >nom: nom du schema a cree
#g2p                       convertit des coordonees lat long en attribut en point cc4
#geocode                   geocode des element
#geocode_csv               geocodage d'un fichier cs
#geoextract                extraction d'un jeu de donnees d' une base par emprise p:format parametres serveur base chaine_connection niveau class
#getosm                    telecharge le fichier osm de l'alsac
#gid                       ajout d un gid si necessair
#grantsitr                 generation des scripts de gran
#grid                      repartit les objets selon une grill
#groupe                    force le groupe p:groupe: nouveau group
#histo_cmp                 
#histor                    convertit des bases en format historiqu
#httpdownload              charge des elements par ft
#ident                     force le groupe et la classe p:groupe: nouveau groupe, classe:nouvelle class
#indb                      precharge des donnees depuis une base pour comparaiso
#init_mp                   initialise un module en mode multiprocessing (ne fait rien et attends)
#initdb                    positionne des elements d'acces a une base de donnee
#ll2cus                    reprojette des donnees cus en rgf9
#log                       
#low                       
#mastercrypt               crypte un element avec la masterkey
#mkcrypt                   
#mod                       
#moi                       
#ora2pg                    passage de oracle vers postgi
#ora2pg2                   passage de oracle vers postgis version local
#passage_dev               
#passage_prod              
#passage_schema            scripts de passage en pro
#prefix                    prefixe la classe p:prefix: prefixe a ajouter a la class
#print                     
#printparams               affichag
#printvar                  affichage variabl
#pwcrypt                   crypte les mots de pass
#pwdecrypt                 decrypte les mots de pass
#pwprepare                 
#pyetl_init_db             
#regroupe                  force le groupe et le transfere sur un attribut p:groupe: nom du nouveau groupe>attribut: nom de l'attribut contenant l'ancie
#rename                    modifie la classe p:old: partie a remplacer >new: partie de remplacemen
#reproj                    convertit des coordonees du systeme orig vers des
#retour_elyx               retour des donnees vers elyx pour toutes les classes definires dans ELYP
#run                       execute une commande extern
#runproc                   lancement fonction_sq
#runsql                    lancement script_sq
#schema_sigli              ajoute les attributs standard a un schema
#scriptodb                 charge un script en bas
#set                       
#sigli2elyx                passage de sigli vers elyx : sortie asc suppression GID renommage attributs modifie
#site_params               affichage des parametres de connection stocke
#sleep                     
#stdvar                    variables de base appele par tous les autres elements
#store                     
#supp                      
#test                      test des variable
#testpourluc               aide speciale pour lu
#timeselect                determine si un batch est executable en fonction de l'heur
#to_sigli                  preparation d'un jeu de donnees formatage standard sigli p:format parametres serveur base chaine_connection niveau class
#ukcrypt                   
#ukdecrypt                 
#upload                    charge des elements par ft
#valide                    validation de niveaux ou de classe
#version                   affiche la version de pyet
#zip                       zippe les resultat
=========================  ========


