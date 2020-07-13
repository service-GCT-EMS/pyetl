
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
    sans_entree                      1 si le traitement n'utilise pas de ficher ou repertoire d entree
    nbaffich            100000       affichage de la progression du traitement 0 = pas d affichage
    filtre_entree                    filtre de selection des fichiers dans le repertoire d'entree
    sans_sortie                      1 si le traitement n'utilise pas de ficher ou repertoire d entree
    _st_lu_objs         0            statistiques de fonctionnement (usage interne ne pas modifier)
    _st_lu_fichs        0
    _st_lu_tables       0
    _st_wr_objs         0
    _st_wr_fichs        0
    _st_wr_tables       0
    _st_obj_duppliques  0
    _st_obj_supprimes   0
    tmpdir              ./tmp        repertoire temporaire
    F_entree                         forcage format entree: dans ce cas l interpretation des fichiers ignore l extension
    racine              .            origine des chemins relatifs
    job_control         no           ecrit un fichier pour signaler la fin du traitement
    aujourdhui          now()        horodatage du debut du traitement %Y/%m/%d 00:00:00
    annee               now()        annee
    mois                now()        mois
    jour                now()        jour
    jour_a              now()        numero de jour dans l annee
    jour_m              now()        numero de jour du mois
    jour_s              now()        numero de jour dans la semaine
    stat_defaut        affiche       affichage de stats finales en l abscence de fichier
    fstat                            fichier de stockage des stats
    force_schema       util          filtre d'ecriture des schemas: seul les schemas utilises sont ecrits
    epsg               3948          datum par defaut des objets
    _pv                 ;            contient un pointvirgule (le ; etant un separateur facilite l usage du  ; comme donnée
    F_sortie                         format de sortie si vide: egal au format d entree
    xmldefaultheader                 header xml pour les schemas: '<?xml-stylesheet href="xsl/dico.xsl" type="text/xsl"?>'
    codec_sortie       DEFCODEC       encoding fichier de sortie : defaut systeme
    codec_entree       DEFCODEC       encodinf fichiers d entree : defaut systeme
    _paramdir                        repertoire contenant les parametres de site : variable environnement PYETL_SITE_PARAMS
    _paramperso        .pyetl         repertoire contenant les parametres personnels
    _version           version        version courante de pyetl
    _progdir                         repertoire contenant pyetl (ne pas modifier sauf si l ons sait vraiment ce qu'on fait)
    lire_maxi                        nombre maxi d objets a lire par table ou par fichier 0 = tous les objets
    ================== ============  ============================================================


chaque script ou macro peut definir ses propres variables

les variables sont statiques elles sont remplacees par leur valeur a l interpretation initiale du script
seule la macro finale peut utiliser les variables de stats internes

contextes
---------

chaque variable appartient à un contexte, les contextes sont hierarchiques:
 chaue script bloc macro ou regle cree un contexte,
 les variables definies dans un script ne sont visibles que dans celui ci (cas de l'execution de scripts multiples)
 les variables locales definies dans une macro ou un bloc ne sont visible que dans celle ci
 les variables definies dans une regle ne sont visibles que dans celle ci et toutes celles qui en dependent

a la lecture d une variable la chaine de contexte est explorée pour trouver la valeur
par defaut l'affectation d une variable par set modifie la valeur

    dans le contexte local si la variable existe dans le contexte local
    dans le contexte parent sinon

il est possible de forcer l affectation dans la commande d affectation:

    ´´$nom=valeur´´
        affectation standard
    ´´$$nom=valeur´´
        affectation au contexte racine
    ´´$-nom=valeur´´
        affectation forcée au contexte local (cree la variable locale)
    ´´$*nom=valeur´´
        variable retour recuperee depuis un process parallele ou un script lance en batch
    ´´$!nom=valeur´´
        positionne une variable d environnement
