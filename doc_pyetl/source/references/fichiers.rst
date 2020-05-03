fichiers de configuration
=========================

Pyetl utilise divers types de fichiers pour les operations de test d inclusion de mapping ou de jointures

fichiers de mapping
-------------------

les operations de mapping (commande :ref:`map`)
permettent une modification en bloc de la structure des tables

ces operations sont realisees à partir de tables de mapping en format csv
    ces tables ont la forme suivante:

classe origine; classe destination; mapping attributs (optionnel)

    la classe origine peut prendre la forme niveau.classe ou base.niveau.classe
    la classe destination peut prendre la forme classe ou niveau.classe

ou

niveau origine; classe origine; niveau destination; classe destination ; mapping attributs (optionnel)
exemple:


fichier d'inclusion de classes
------------------------------

ces fichiers sont utilises dans les selections de type in:

ils se presentent sous la forme

niveau;classe

ou

niveau.classe

ou base.niveau.classe

fichier de conditions
---------------------

ces fichiers permettent de selectionner les objets dans les tables (selection de type in)
ils se presentent sous la forme

niveau;classe;attribut;valeur

ou

niveau.classe.attribut;valeur

ou

base.niveau.classe.attribut;valeur

fichiers listes
---------------

fichiers texte simple comprenant un item par ligne utilises par les condition in:

fichiers qgs
------------

des fichiers qgs peuvent etre utilises directement comme liste de definition de classes
toutes les classes contenues dans les definitions de type datasource du fichier qgs

une condition ``in:projet.qgs`` selectionne toutes les classes dóbjets utilisees dans le projet qgis

repertoires
-----------

Pyetl peut scanner des arborescences completes pour extraire l ensemble des classes referenceees
dans les fichiers qgs et csv. les doublons sont automatiquement géres

une condition de type ``in:repertoire`` va selectionner toutes les classes d'objets contenus dans au moins un des projets qgis
ou fichier csv ou texte du repertoire et de ses sous repertoires

fichiers de jointures
---------------------

tout fichier csv peut etre utilise comme fichierde jointure
