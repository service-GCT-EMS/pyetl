===================
Le programme mapper
===================

La librairie Pyetl est accompagnée du programme Mapper

Mapper est une interface en ligne de commande permettant d'utiliser la bibliothèque Pyetl


modes de fonctionnement
=======================

mode ligne de commandes
-----------------------

``mapper commande entree sortie parametres``

    commande   : nom de script ou de macro (obligatoire)
    entree     : repertoire ou fichier d entree ( facultatif: certaines commandes ne prennent pas d entree)
    sortie     : repertoire de sortie ( peut etre precise dans le script )
    parametres : groupes de la forme nom=valeur si la valeut contient des blancs il faut l entourer de "

    Le programme applique les commandes contenues dans un script ou une macro
    aux element d un repertoire ou d un fichier d'entrée et ecrit les resultats
    dans un répertoire de sortie

    les scripts sont stockés sous forme de fichier csv ou de table de base de donnée
    les macros peuvent etre

        * des macros internes fournies avec pyetl
        * des macros partagées dans un ficher ``macros.csv`` dans un répertoire
          indique par la variable d environnement ``PYETL_SITE_PARAMS``
        * des macros stockées en base de données
        * des macros personnelles dans le ficher macros.csv du répertoire ``.pyetl``
          dans le répertoire de l'utilisateur

mode batch
----------

    ``mapper #batch fichier_desriptif``

    ``mapper #db_batch``

    mapper execute un ensemble de scripts decrits dans un fichier csv ou une table de base de données

mode temps réel
---------------

    ``mapper #tpr fichier_desriptif``

    ``mapper #db_tpr``

    mapper execute en boucle a intervalle variable un ensemble de scripts decrits dans un fichier csv
    ou une table de base de données les intervalles sont geres directement dans le fichier de description

mode webservice
---------------

    ``pyetl_fcgi``

    cree un serveur fcgi pour fournir des services web
