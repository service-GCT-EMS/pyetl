================
demarrage rapide
================

**demarrage et test de l installation**



**affichage de l aide**

``mapper #help``

aide detaille sur un element

``mapper #help element``

**autotest**

``mapper #autotest``

commandes utiles
................

structure generale d un appel:

``mapper commande entree sortie parametres``

    commande   : nom de script ou de macro (obligatoire)
    entree     : repertoire ou fichier d entree ( facultatif: certaines commandes ne prennent pas d entree)
    sortie     : repertoire de sortie ( peut etre precise dans le script )
    parametres : groupes de la forme nom=valeur si la valeut contient des blancs il faut l entourer de "

**conversion de fichers**

``mapper #extract rep_entree rep_sortie format=shp``

convertit tous les fichier du repertoire rep_entree en shp et les stocke dans rep_sortie

**analyse de fichiers**

``mapper #analyse rep_entree rep_sortie``

analyse tous les fichier du repertoire rep_entree et genere la structure dans rep_sortie
en csv et xml

``mapper #analyse rep_entree rep_sortie format_schema=sql:postgis``

analyse tous les fichier du repertoire rep_entree et genere la structure dans rep_sortie
en sql : l'execution des fichiers generes cree une base postgis capable d acceuillir les donnees

**extraction de bases de donnees**

``mapper #dbextract acces=base format=shp``
