
variables
=========


les variables permettent de modifier le comportement de pyetl ou des scripts

les variables globales
----------------------

    ================== ============  ============================================================
    variable             defaut                                     defintion
    ================== ============  ============================================================
    mode_sortie         D            mode de traitement A global B par groupe C par classe D par objet
    memlimit            100000       nombre d objets en memoire avant de stocker sur disque (mode A a C)
    sans_entree                      1 si le traitement n'utilise pas de ficher ou répertoire d entre
    nbaffich            100000       affichage de la progression du traitement 0 = pas d affichage
    filtre_entree                    filtre de selection des fichiers dans le répertoire d'entrée
    sans_sortie                      1 si le traitement n'utilise pas de ficher ou répertoire d entre
    _st_lu_objs         0            statistiques de fonctionnement (usage interne ne pas modifier)
    _st_lu_fichs        0
    _st_lu_tables       0
    _st_wr_objs         0
    _st_wr_fichs        0
    _st_wr_tables       0
    _st_obj_duppliques  0
    _st_obj_supprimes   0
    tmpdir              ./tmp        répertoire temporaire
    F_entree                         forcage format entrée: dans ce cas l interprétation des fichiers ignore l extension
    racine              .            origine des chemins relatifs
    job_control         no           écrit un fichier pour signaler la fin du traitement
    aujourdhui          now()        horodatage du début du traitement %Y/%m/%d 00:00:00
    annee               now()        année
    mois                now()        mois
    jour                now()        jour
    jour_a              now()        numéro de jour dans l'année
    jour_m              now()        numéro de jour du mois
    jour_s              now()        numéro de jour dans la semaine
    stat_defaut        affiche       affichage de stats finales en l'absence de fichier
    fstat                            fichier de stockage des stats
    force_schema       util          filtre d'écriture des schemas: seul les schemas utilises sont écrits
    epsg               3948          code projection par défaut des objets
    _pv                 ;            contient un point-virgule (le ; étant un séparateur facilite l usage du  ; comme donnée
    F_sortie                         format de sortie si vide: égal au format d entrée
    xmldefaultheader                 header xml pour les schemas: '<?xml-stylesheet href="xsl/dico.xsl" type="text/xsl"?>'
    codec_sortie       DEFCODEC      encodage fichier de sortie : défaut système
    codec_entree       DEFCODEC      encodage fichiers d'entree : défaut système
    _paramdir                        répertoire contenant les paramètres de site : variable environnement PYETL_SITE_PARAMS
    _paramperso        .pyetl        répertoire contenant les paramètres personnels
    _version           version        version courante de pyetl
    _progdir                         répertoire contenant pyetl (ne pas modifier sauf si l ons sait vraiment ce qu'on fait)
    lire_maxi                        nombre maxi d objets a lire par table ou par fichier 0 = tous les objets
    ================== ============  ============================================================


chaque script ou macro peut définir ses propres variables

les variables sont statiques elles sont remplacées par leur valeur a l interprétation initiale du script
seule la macro finale peut utiliser les variables de stats internes

contextes
---------

chaque variable appartient à un contexte, les contextes sont hiérarchiques:
 chaque script bloc macro ou règle crée un contexte,
 les variables définies dans un script ne sont visibles que dans celui ci (cas de l'execution de scripts multiples)
 les variables locales définies dans une macro ou un bloc ne sont visible que dans celle ci
 les variables définies dans une règle ne sont visibles que dans celle ci et toutes celles qui en dépendent

a la lecture d une variable la chaîne de contexte est explorée pour trouver la valeur
par défaut l'affectation d une variable par set modifie la valeur

    dans le contexte local si la variable existe dans le contexte local
    dans le contexte parent sinon

il est possible de forcer l affectation dans la commande d affectation:

    ´´$nom=valeur´´
        affectation standard
    ´´$$nom=valeur´´
        affectation au contexte racine
    ´´$-nom=valeur´´
        affectation forcée au contexte local (crée la variable locale)
    ´´$*nom=valeur´´
        variable retour récupérée depuis un process parallèle ou un script lance en batch
    ´´$!nom=valeur´´
        positionne une variable d environnement
