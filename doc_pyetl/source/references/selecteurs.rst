
sélecteurs
==========


utilité du sélecteur
--------------------

La première étape fondamentales d un traitement est la sélection des objets auxquels on
applique ce traitement. Un des points fors de Pyetl est de pouvoir appliquer un traitement
à une sélection complexe de classes d objets. cette sélection peur couvrir différentes bases de données

on distingue 2 type de sélections: les selections monobases et les selections multibase
Les selections monobase ne necessitent pas le creation explicite d un selecteur de tables
dans la pratique le selecteur est cree en direct


Selections monobases
--------------------

les selections monobases peuvet etre diecrites directement dans les commandes d acces aux bases:

La structure générale d une commande d acces aux bases:

db:base;niveau;classe;attribut;;valeur;[att];commande;

    db:b1
        sélectionne toutes les tables de la base b1

    db:b1;n1
        sélectionne toutes les tables du niveau n1 de la base b1

    db;b1;n1,n2,...
        sélectionne toutes les tables des niveau n1,n2,... de la base b1

    db:b1;n1;c1
        sélectionne la table n1.c1 de la base b1

    db:b1;n1,n2;c1
        sélectionne les table n1.c1 et n2.c1 de la base

    db:b1;n1,n2;c1,c2
        sélectionne les tables n1.c1,n1.c2,n2.c1,n2.c2 de la base

    db:b1;;c1,c2
        sélectionne les tables c1 et c2 dans tous les schemas

    db:b1;n1.c1,n2.c2;
        sélectionne les table n1.c1 et n2.c2 de la base

    db:b1;in:fichier;
        selectionne les tables decrites en :ref: 'fichiers de configuration'
        en cas de rpertoire tous les fichiers csv et qgs du repertoire sont examines

    db:b1;in:schema:nom
        selectionne les tables du schema

    db:b1;in:#stock:niveau,classe
        selectionne les tables decrites dans les objets stockes en #stock niveau et classe sont le nom des attributs
        contenant les niveaux et les classes

    db:b1;in:#selecteur
        selectionne les classes decrites dans le selecteur si la base nest pas precisee c est une selection multibase
        qui doit etre definie dans le selecteur



selection multibase et objet selecteur

un objet selecteur est crée par la commande select_table;#selecteur

la syntaxe est la meme que les commandes de selection directe
les differentes selectiosn s ajoutent dans le selecteur
