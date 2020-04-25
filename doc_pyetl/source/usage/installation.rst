=====================
installation de pyetl
=====================

environnement python
====================
    pyetl fonctionne sous python > 3.6

modules complementaires
=======================
    pyetl peut demarrer dans un environnement de base sans modules complementaires
    neanmoins de nombreuses fonctionnalites ne seront pas disponibles sans installer des librairies tierces

    pour l'installation des librairies:

    * creer une environnement python specifique (recommandé)
    * dezipper le paquet mapper.zip
    * utiliser le gestionnaire de paquets de votre environnement pour installer les librairies manquantes
    * la liste est disponible grace à la commande ``mapper #missinglibs``

le ficher mapper.bat contient la commande
 python mapper.py %*

ce fichier peut etre completé avec des variables d environnement specifiques au site


    * test de l installation :
      ``mapper #unittest``
