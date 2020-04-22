===============
reference pyetl
===============

structure generale
==================

toutes les commandes pyetl sont structurees de la meme facon sous forme d une ligne de 13 colonnes
toutes les colonnes ne sont pas utilisees systematiquement
la position est importante


types de lignes de commande
===========================
il y a 5 types de lignes de commandes

affectation de variables
------------------------

    une ligne d affectation se presente sous la forme suivante:

        $nom=valeur;fallback;....
            affecte la valeur au nom
            si la valeur est une variable et qu elle n'est pas definie la premiere valeurs fallback non vide est utilisee

import de groupes
-----------------
        $#nom
            importe un groupe de variable depuis les fichiers de parametres

commande
--------

        * colonnes 1 a 4: determinent l'execution de la commande sous forme de 2 conditions

            * att_tri1
            * valeur_tri1
            * att_tri2
            * valeur_tri2

        * colonnes 5 a 7: sortie et entrees

            * att_sortie
            * defaut
            * att_entree

        * colonne 8: nom de la commande
        * colonnes 9 et 10: parametres

            * param1
            * param2

        * colonne 11 flag de debug
        * colonne 12 definition de variables locales
        * colonne 13 commentaires

commandes standard
==================

.. automodule:: moteur.fonctions.traitement_alpha
   :members:
