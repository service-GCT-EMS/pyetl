=========================
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
