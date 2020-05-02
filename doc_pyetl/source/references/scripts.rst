
scripts
=======


Notions de base
---------------

Pyetl est concu pour traiter des objets.
Une classe d objets partage un meme schema
toute manipulation sur les objets fait evoluer les schemas
les schemas déterminent les structures des fichiers ou bases de donnees
il est possible egalement de manipuler directement les schemas (ce qui n'affecte pas les objets)

un traitement consiste a appliquer des commandes à un ensemble d entrées pour générer des sorties

un script Pyetl corresponds a un traitement

les scripts se présentent sous forme d'un fichier csv comprenant un ensemble de :ref:commandes


entrées
-------

Les scripts peuvent prendre des fichiers ou des repertoires en entrées.
les fichiers correspondants aux :ref:`formats d'entrée`
chaque fichier reconnu est lu et les commandes sont appliquées aux objets contenus

en l'abscence d entrée le script peut accéder à des bases de donnes ou des services web.
certains scripts peuvent gerer directement des schémas ou creer les objets

sorties
-------

sauf exception un script a besoin d'un repertoire de sortie
tous les fichiers generes serons stockes dans ce repertoire et ses sous répertoires
L'arborescence est crée automatiquement
en général la sortie comprend

    un ou plusieurs fichers de données dans un ou plusieurs :ref:`formats de sortie`
    des fichiers descriptifs de structure


fichier de commandes
--------------------

Un script est un ensemble de lignes de :ref:commandes
le script peut etre un fichier csv ou des lignes d une table en base de donnees


les commandes sont enchainees sequentiellement cependant il est possible de creer des structures de controle
pour lier des commandes entre elles:
chaque ligne de script peut contenir 2 tests et une commande elle
possede au moins 4 sorties et il est possble d affecter des lignes de script a chaqune d'elles:

    sortie ok:
        objets ayant passe les test et la commande
    sortie fail:
        objets ayant passe les test et genere une erreur dans la commande
    sortie sinon:
        objet n ayant pas passe les tests
    sortie next:
        sortie virtuelle ou tous les flux se rejoignent (la sortie next n est jamais mentionnée explicitement)

commandes générant des objets :
    sortie gen:
        objets crées par la commande
    sortie nogen:
        objets non crees par la commande (permets de passer les declencheurs à des générateurs successifs)

    sortie copy:
        objets non modifies crees par le filtre de copie sur une commande

commandes generant de filres: :ref:filter
        genere une sortie pour chaque valeur de filtre

les structures de controle peuvent etre imbriquées
