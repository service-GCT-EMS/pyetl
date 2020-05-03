
parametres
==========

Les parametres permettent d enregistre les caracteristiques des connections pour les
    * bases de donnees
    * sites web
    * serveurs ftp

et plus globalement tout groupe de variables a utiliser conjointement.

Les parametres peuvent etre partages ou individuels.
les parametre personnels sont prioritaires sur les parametres partagés
si des parametres incluent des mots de passe il est possible de les crypter

un fichier de parametre est un fichier csv a 2 colonnes variables et valeurs

chaque groupe de parametre debute par l instruction

``&&#set;nom``

il est suivi par une ensemble d afffectations:

``variable;valeur``

puis par la commande

``##&end;``

il est possible de completer un groupe de parametres avec la commande

``&&#add;nom``
``variable;valeur``
``...``
``##&end;``


le groupe nomme init est lu automatiquement au lancement de Pyetl
