================
démarrage rapide
================

**démarrage et test de l installation**



**affichage de l aide**

``mapper #help``

aide détaillée sur un élément

``mapper #help element``

**autotest**

``mapper #autotest``

commandes utiles
................

structure générale d un appel:

``mapper commande entree sortie parametres``

    commande   : nom de script ou de macro (obligatoire)
    entree     : repertoire ou fichier d entree ( facultatif: certaines commandes ne prennent pas d entree)
    sortie     : repertoire de sortie ( peut etre precise dans le script )
    parametres : groupes de la forme nom=valeur si la valeut contient des blancs il faut l entourer de "

**conversion de fichiers**

``mapper #extract rep_entree rep_sortie format=shp``

convertit tous les fichier du répertoire rep_entree en shp et les stocke dans rep_sortie

**analyse de fichiers**

``mapper #analyse rep_entree rep_sortie``

analyse tous les fichier du répertoire rep_entree et génère la structure dans rep_sortie
en csv et xml

``mapper #analyse rep_entree rep_sortie format_schema=sql:postgis``

analyse tous les fichier du répertoire rep_entree et génère la structure dans rep_sortie
en sql : l'exécution des fichiers générés crée une base postgis capable d accueillir les donnees

**extraction de bases de données**

``mapper #dbextract acces=base format=shp``
