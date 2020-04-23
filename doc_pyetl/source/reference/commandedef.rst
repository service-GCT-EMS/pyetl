commandes
=========


abort
-----

arrete le traitement

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  abort   |   ?N   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   usage: abort,niveau,message

1 arret du traitement de l'objet
2 arret du traitment de la classe
3 arret du traitement pour le module
4 sortie en catastrophe


abspath
-------

change un chemin relatif en chemin absolu

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   C?   |   A?   | abspath  |   C?   |        |
+--------+--------+--------+----------+--------+--------+

   le point de depart est le chemin ou cmp1



addgeom
-------

cree une geometrie pour l'objet

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   ?A   | addgeom  |   N    |        |
+--------+--------+--------+----------+--------+--------+

   N:type geometrique

ex: A;addgeom  avec A = (1,2),(3,3) -> (1,2),(3,3)
+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   ?L   | addgeom  |   N    |        |
+--------+--------+--------+----------+--------+--------+

   N:type geometrique

  X,Y;addgeom avec X=1,2,3,4 et Y=6,7,8,9 -> (1,6),(2,7),(3,8),(4,9)


adquery
-------

extait des information de active_directory

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?C   |   ?A   | adquery  | =user  |   ?C   |
+--------+--------+--------+----------+--------+--------+

   extait des information de active_directory

+--------+--------+--------+----------+----------+--------+
| sortie | defaut | entree | commande |  param1  | param2 |
+========+========+========+==========+==========+========+
|   S    |   ?C   |   ?A   | adquery  | =machine |   ?C   |
+--------+--------+--------+----------+----------+--------+

   extait des information de active_directory

+--------+--------+--------+----------+---------+--------+
| sortie | defaut | entree | commande | param1  | param2 |
+========+========+========+==========+=========+========+
|   S    |   ?C   |   ?A   | adquery  | =groupe |   ?C   |
+--------+--------+--------+----------+---------+--------+

   extait des information de active_directory



aire
----

calcule l'aire de l'objet

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |        |   aire   |        |        |
+--------+--------+--------+----------+--------+--------+

   calcule l'aire de l'objet



angle
-----

calcule un angle de reference de l'objet

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |        |  angle   |  ?N:N  |  ?=P   |
+--------+--------+--------+----------+--------+--------+

   N:N indices des point a utiliser, P creation d'un point au centre



archive
-------

zippe les fichiers ou les repertoires de sortie

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   ?A   | archive  |   C    |        |
+--------+--------+--------+----------+--------+--------+

    parametres:liste de noms de fichiers(avec *...);attribut contenant le nom;archive;nom



attreader
---------

traite un attribut d'un objet comme une source de donnees

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |   ?C   |   A    | attreader |   C    |   ?C   |
+--------+--------+--------+-----------+--------+--------+

   par defaut attreader supprime le contenu de l attribut source

pour le conserver positionner la variable keepdata a 1


attwriter
---------

traite un attribut d'un objet comme une sortie cree un objet pas fanout

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   A    |        |        | attwriter |   C    |   ?C   |
+--------+--------+--------+-----------+--------+--------+

   par defaut attreader supprime le contenu de l attribut source

pour le conserver positionner la variable keepdata a 1


batch
-----

execute un traitement batch a partir des parametres de l'objet

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   ?A   |  batch   | =init  |        |
+--------+--------+--------+----------+--------+--------+

   

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

 en mode init le traitement demarre a l'initialisation du script
      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =init
         batch

+--------+--------+--------+----------+----------------+--------+
| sortie | defaut | entree | commande |     param1     | param2 |
+========+========+========+==========+================+========+
|   A    |   ?C   |   ?A   |  batch   | =parallel_init |        |
+--------+--------+--------+----------+----------------+--------+

   execute un traitement batch a partir des parametres de l'objet

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =parallel_init
         batch

+--------+--------+--------+----------+---------+--------+
| sortie | defaut | entree | commande | param1  | param2 |
+========+========+========+==========+=========+========+
|   A    |   ?C   |   ?A   |  batch   | =boucle |   C    |
+--------+--------+--------+----------+---------+--------+

   execute un traitement batch a partir des parametres de l'objet

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =boucle
         batch
      C
         mode_batch

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   ?A   |  batch   | =load  |   C    |
+--------+--------+--------+----------+--------+--------+

   execute un traitement batch a partir des parametres de l'objet

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      =load
         batch
      C
         mode_batch

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   ?A   |  batch   | ?=run  |   ?N   |
+--------+--------+--------+----------+--------+--------+

   

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

 en mode load le traitement passe une fois le jeu de donnees
      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      batch
         attribut_commandes
      ?=run
         batch (optionnel)
      ?N
         mode_batch (optionnel)



bloc
----

definit un bloc d'instructions qui reagit comme une seule et genere un contexte

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   bloc   |        |        |
+--------+--------+--------+----------+--------+--------+

   definit un bloc d'instructions qui reagit comme une seule et genere un contexte



boucle
------

execute un traitement batch en boucle a partir des parametres de l'objet

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   ?A   |  boucle  |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      boucle
         attribut_commandes
      C
         batch
      ?C
         mode_batch (optionnel)

 en mode run le traitement s'autodeclenche sans objet
      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      boucle
         attribut_commandes
      C
         batch
      ?C
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      boucle
         attribut_commandes
      C
         batch
      ?C
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      boucle
         attribut_commandes
      C
         batch
      ?C
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      boucle
         attribut_commandes
      C
         batch
      ?C
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      boucle
         attribut_commandes
      C
         batch
      ?C
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      boucle
         attribut_commandes
      C
         batch
      ?C
         mode_batch (optionnel)

      A
         
      ?C
         attribut_resultat (optionnel)
      ?A
         commandes (optionnel)
      boucle
         attribut_commandes
      C
         batch
      ?C
         mode_batch (optionnel)



branch
------

genere un branchement

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  branch  |   C    |        |
+--------+--------+--------+----------+--------+--------+

   genere un branchement



buffer
------

calcul d'un buffer

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   ?N   |   ?A   |  buffer  |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   calcul d'un buffer

resolution:16,cap_style:1,join_style:1,mitre_limit:5
resolution:16,cap_style:1,join_style:1,mitre_limit:5
      ?A
         largeur buffer (optionnel)
      ?N
         attribut contenant la largeur (optionnel)
      ?A
         buffer (optionnel)

resolution:16,cap_style:1,join_style:1,mitre_limit:5
resolution:16,cap_style:1,join_style:1,mitre_limit:5
resolution:16,cap_style:1,join_style:1,mitre_limit:5
resolution:16,cap_style:1,join_style:1,mitre_limit:5
resolution:16,cap_style:1,join_style:1,mitre_limit:5
resolution:16,cap_style:1,join_style:1,mitre_limit:5
resolution:16,cap_style:1,join_style:1,mitre_limit:5
resolution:16,cap_style:1,join_style:1,mitre_limit:5


call
----

appel de macro avec gestion de variables locales

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   call   |   C    |  ?LC   |
+--------+--------+--------+----------+--------+--------+

   appel de macro avec gestion de variables locales



change_couleur
--------------

remplace une couleur par une autre

syntaxes acceptees
..................

+--------+--------+--------+----------------+--------+--------+
| sortie | defaut | entree |    commande    | param1 | param2 |
+========+========+========+================+========+========+
|        |        |        | change_couleur |   C    |   C    |
+--------+--------+--------+----------------+--------+--------+

   remplace une couleur par une autre



charge
------

chargement d objets en fichier

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   ?C   |   ?A   |  charge  |   ?C   |   ?N   |
+--------+--------+--------+----------+--------+--------+

   cette fonction est l' équivalent du chargement initial

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   ?C   |   ?A   |  charge  |  [A]   |   ?N   |
+--------+--------+--------+----------+--------+--------+

   chargement d objets en fichier



cnt
---

creation des compteurs

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?    |   ?A   |   cnt    |   ?N   |   ?N   |
+--------+--------+--------+----------+--------+--------+

   le comteur est global s'il a un nom, local s'il n'en a pas

      S
         attribut de sortie
      ?
         nom fixe (optionnel)
      ?A
         attribut contenant le nom du compteur (optionnel)
      cnt
         
      ?N
         pas (optionnel)
      ?N
         origine (optionnel)

      S
         attribut de sortie
      ?
         nom fixe (optionnel)
      ?A
         attribut contenant le nom du compteur (optionnel)
      cnt
         
      ?N
         pas (optionnel)
      ?N
         origine (optionnel)

      S
         attribut de sortie
      ?
         nom fixe (optionnel)
      ?A
         attribut contenant le nom du compteur (optionnel)
      cnt
         
      ?N
         pas (optionnel)
      ?N
         origine (optionnel)

      S
         attribut de sortie
      ?
         nom fixe (optionnel)
      ?A
         attribut contenant le nom du compteur (optionnel)
      cnt
         
      ?N
         pas (optionnel)
      ?N
         origine (optionnel)

      S
         attribut de sortie
      ?
         nom fixe (optionnel)
      ?A
         attribut contenant le nom du compteur (optionnel)
      cnt
         
      ?N
         pas (optionnel)
      ?N
         origine (optionnel)

      S
         attribut de sortie
      ?
         nom fixe (optionnel)
      ?A
         attribut contenant le nom du compteur (optionnel)
      cnt
         
      ?N
         pas (optionnel)
      ?N
         origine (optionnel)

      S
         attribut de sortie
      ?
         nom fixe (optionnel)
      ?A
         attribut contenant le nom du compteur (optionnel)
      cnt
         
      ?N
         pas (optionnel)
      ?N
         origine (optionnel)

      S
         attribut de sortie
      ?
         nom fixe (optionnel)
      ?A
         attribut contenant le nom du compteur (optionnel)
      cnt
         
      ?N
         pas (optionnel)
      ?N
         origine (optionnel)



compare
-------

compare a un element precharge

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |   ?L   | compare  |   A    |   C    |
+--------+--------+--------+----------+--------+--------+

   parametres clef;fichier;attribut;preload;macro;nom

sort en si si egal en sinon si different
si les elements entre [] sont pris dans l objet courant


compare2
--------

compare a un element precharge

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |   ?L   | compare2 |   A    |   C    |
+--------+--------+--------+----------+--------+--------+

   parametres clef;fichier;attribut;preload;macro;nom

sort en si si egal en sinon si different
si les elements entre [] sont pris dans l objet courant


compare_schema
--------------

compare un nouveau schema en sortant les differences

syntaxes acceptees
..................

+--------+--------+--------+----------------+--------+--------+
| sortie | defaut | entree |    commande    | param1 | param2 |
+========+========+========+================+========+========+
|        |   ?C   |        | compare_schema |   C    |   ?N   |
+--------+--------+--------+----------------+--------+--------+

   compare un nouveau schema en sortant les differences

+--------+--------+--------+----------------+--------+--------+
| sortie | defaut | entree |    commande    | param1 | param2 |
+========+========+========+================+========+========+
|   C    |   C    |        | compare_schema |        |        |
+--------+--------+--------+----------------+--------+--------+

   compare un nouveau schema en sortant les differences



coordp
------

extrait les coordonnees d'un point en attributs

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?M   |   ?N   |   ?A   |  coordp  |        |        |
+--------+--------+--------+----------+--------+--------+

   les coordonnees sont sous #x,#y,#z



creobj
------

cree des objets de test pour les tests fonctionnels

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   LC   |   ?L   |  creobj  |   C    |   ?N   |
+--------+--------+--------+----------+--------+--------+

   parametres:liste d'attributs,liste valeurs,nom(niv,classe),nombre

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   LC   |        |  creobj  |   C    |   ?N   |
+--------+--------+--------+----------+--------+--------+

   cree des objets de test pour les tests fonctionnels



crypt
-----

crypte des valeurs dans un fichier en utilisant une clef

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |   A    |  crypt   |   C?   |        |
+--------+--------+--------+----------+--------+--------+

   crypte des valeurs dans un fichier en utilisant une clef

      A
         attribut resultat crypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      crypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat crypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      crypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat crypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      crypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat crypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      crypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat crypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      crypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat crypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      crypt
         
      C?
         clef de cryptage (optionnel)



csplit
------

decoupage conditionnel de lignes en points

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |        |        |  csplit  |   C    |        |
+--------+--------+--------+----------+--------+--------+

   expression sur les coordonnes : x y z



dbalpha
-------

recuperation d'objets depuis la base de donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   ?    |   ?    | dbalpha  |   ?    |   ?    |
+--------+--------+--------+----------+--------+--------+

   recuperation d'objets depuis la base de donnees



dbclean
-------

vide un ensemble de tables

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | dbclean  |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   vide un ensemble de tables



dbclose
-------

recuperation d'objets depuis la base de donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | dbclose  |        |        |
+--------+--------+--------+----------+--------+--------+

   recuperation d'objets depuis la base de donnees



dbcount
-------

nombre d'objets dans un groupe de tables

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |        | dbcount  |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   nombre d'objets dans un groupe de tables



dbextdump
---------

lancement d'une extraction par une extracteur externe

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |        |        | dbextdump |   ?C   |   ?C   |
+--------+--------+--------+-----------+--------+--------+

   parametres:base;;;;;;dbextdump;dest;?log



dbextload
---------

lancement d'un chargement de base par un loader externe

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |   ?C   |   ?A   | dbextload |   C    |        |
+--------+--------+--------+-----------+--------+--------+

   parametres:base;;;;?nom;?variable contenant le nom;dbextload;log;



dbgeo
-----

recuperation d'objets depuis la base de donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   ?    |   ?L   |  dbgeo   |   ?C   |   ?N   |
+--------+--------+--------+----------+--------+--------+

   db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;buffer



dblast
------

recupere les derniers enregistrements d 'une couche (superieur a une valeur min)

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  dblast  |   C    |        |
+--------+--------+--------+----------+--------+--------+

   recupere les derniers enregistrements d 'une couche (superieur a une valeur min)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |        |  dblast  |        |        |
+--------+--------+--------+----------+--------+--------+

   recupere les derniers enregistrements d 'une couche (superieur a une valeur min)



dbmaxval
--------

valeur maxi d une clef en base de donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?P   |        |        | dbmaxval |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   valeur maxi d une clef en base de donnees



dbreq
-----

recuperation d'objets depuis une requete sur la base de donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   ?    |   ?L   |  dbreq   |   C    |        |
+--------+--------+--------+----------+--------+--------+

   db:base;niveau;classe;;att_sortie;valeurs;champ a integrer;dbreq;requete



dbschema
--------

recupere les schemas des base de donnees

syntaxes acceptees
..................

+----------------+--------+--------+----------+--------+--------+
|     sortie     | defaut | entree | commande | param1 | param2 |
+================+========+========+==========+========+========+
| =schema_entree |   C?   |        | dbschema |   ?    |        |
+----------------+--------+--------+----------+--------+--------+

   recupere les schemas des base de donnees

+----------------+--------+--------+----------+--------+--------+
|     sortie     | defaut | entree | commande | param1 | param2 |
+================+========+========+==========+========+========+
| =schema_sortie |   C?   |        | dbschema |   ?    |        |
+----------------+--------+--------+----------+--------+--------+

   recupere les schemas des base de donnees

+----------+--------+--------+----------+--------+--------+
|  sortie  | defaut | entree | commande | param1 | param2 |
+==========+========+========+==========+========+========+
| =#schema |   C?   |   A?   | dbschema |   ?    |        |
+----------+--------+--------+----------+--------+--------+

   recupere les schemas des base de donnees

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   C?   |   A?   | dbschema |   ?    |        |
+--------+--------+--------+----------+--------+--------+

   recupere les schemas des base de donnees



dbupdate
--------

chargement en base de donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | dbupdate |        |        |
+--------+--------+--------+----------+--------+--------+

   chargement en base de donnees



dbwrite
-------

chargement en base de donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | dbwrite  |        |        |
+--------+--------+--------+----------+--------+--------+

   chargement en base de donnees



decrypt
-------

decrypte des valeurs dans un fichier en utilisant une clef

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |   A    | decrypt  |   C?   |        |
+--------+--------+--------+----------+--------+--------+

   decrypte des valeurs dans un fichier en utilisant une clef

      A
         attribut resultat decrypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      decrypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat decrypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      decrypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat decrypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      decrypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat decrypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      decrypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat decrypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      decrypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat decrypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      decrypt
         
      C?
         clef de cryptage (optionnel)

      A
         attribut resultat decrypte
      ?
         defaut (optionnel)
      A
         attribut d'entree
      decrypt
         
      C?
         clef de cryptage (optionnel)



download
--------



syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   ?A   | download |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   ?A   | download |        |        |
+--------+--------+--------+----------+--------+--------+

   



end
---

finit un traitement sans stats ni ecritures

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   end    |        |        |
+--------+--------+--------+----------+--------+--------+

   finit un traitement sans stats ni ecritures



extract_couleur
---------------

decoupe la geometrie selon la couleur

syntaxes acceptees
..................

+--------+--------+--------+-----------------+--------+--------+
| sortie | defaut | entree |    commande     | param1 | param2 |
+========+========+========+=================+========+========+
|        |        |        | extract_couleur |   LC   |        |
+--------+--------+--------+-----------------+--------+--------+

    ne garde que les couleurs precisees



fail
----

ne fait rien mais plante. permet un branchement distant

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   fail   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   ne fait rien mais plante. permet un branchement distant



filter
------

filtre en fonction d un attribut

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?S   |   ?C   |   A    |  filter  |   LC   |  ?LC   |
+--------+--------+--------+----------+--------+--------+

   sortie;defaut;attribut;filter;liste sorties;liste valeurs



fin_bloc
--------

definit la fin d'un bloc d'instructions

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | fin_bloc |        |        |
+--------+--------+--------+----------+--------+--------+

   definit la fin d'un bloc d'instructions



force_alias
-----------

remplace les valeurs par les alias

syntaxes acceptees
..................

+--------+--------+--------+-------------+--------+--------+
| sortie | defaut | entree |  commande   | param1 | param2 |
+========+========+========+=============+========+========+
|        |        |        | force_alias |   ?C   |        |
+--------+--------+--------+-------------+--------+--------+

   remplace les valeurs par les alias



force_ligne
-----------

force la geometrie en ligne

syntaxes acceptees
..................

+--------+--------+--------+-------------+--------+--------+
| sortie | defaut | entree |  commande   | param1 | param2 |
+========+========+========+=============+========+========+
|        |        |        | force_ligne |        |        |
+--------+--------+--------+-------------+--------+--------+

   force la geometrie en ligne



force_pt
--------

transforme un objet en point en recuperant le n eme point

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   ?A   | force_pt |        |        |
+--------+--------+--------+----------+--------+--------+

   les points sont comptes a partir de 0 negatif pour compter depuis la fin

si il n'y a pas de position donnee on prends le centre de l'emprise


forcepoly
---------

force la geometrie en polygone

syntaxes acceptees
..................

+--------+--------+--------+-----------+---------+--------+
| sortie | defaut | entree | commande  | param1  | param2 |
+========+========+========+===========+=========+========+
|        |        |        | forcepoly | ?=force |        |
+--------+--------+--------+-----------+---------+--------+

   force la geometrie en polygone



ftp_download
------------

charge un fichier sur ftp

syntaxes acceptees
..................

+--------+--------+--------+--------------+--------+--------+
| sortie | defaut | entree |   commande   | param1 | param2 |
+========+========+========+==============+========+========+
|        |   ?C   |   ?A   | ftp_download |   C    |   ?C   |
+--------+--------+--------+--------------+--------+--------+

   charge un fichier sur ftp

+--------+--------+--------+--------------+--------+--------+
| sortie | defaut | entree |   commande   | param1 | param2 |
+========+========+========+==============+========+========+
|        |   ?C   |   ?A   | ftp_download |        |        |
+--------+--------+--------+--------------+--------+--------+

   charge un fichier sur ftp

+--------+--------+--------+--------------+--------+--------+
| sortie | defaut | entree |   commande   | param1 | param2 |
+========+========+========+==============+========+========+
|   A    |   ?C   |   ?A   | ftp_download |        |        |
+--------+--------+--------+--------------+--------+--------+

   charge un fichier sur ftp

+--------+--------+--------+--------------+--------+--------+
| sortie | defaut | entree |   commande   | param1 | param2 |
+========+========+========+==============+========+========+
|   A    |   ?C   |   ?A   | ftp_download |   C    |   ?C   |
+--------+--------+--------+--------------+--------+--------+

   charge un fichier sur ftp



ftp_upload
----------

charge un fichier sur ftp

syntaxes acceptees
..................

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|        |   ?C   |   ?A   | ftp_upload |   ?C   |   ?C   |
+--------+--------+--------+------------+--------+--------+

   charge un fichier sur ftp

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|        | =#att  |   A    | ftp_upload |   ?C   |   C    |
+--------+--------+--------+------------+--------+--------+

   charge un fichier sur ftp



garder
------

suppression de tous les attributs sauf ceux de la liste

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   ?L   |   L    |  garder  |        |        |
+--------+--------+--------+----------+--------+--------+

   avec renommage de la liste et eventuellemnt valeur par defaut

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   L    |  garder  |        |        |
+--------+--------+--------+----------+--------+--------+

   suppression de tous les attributs sauf ceux de la liste

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |        |        |  garder  |        |        |
+--------+--------+--------+----------+--------+--------+

   suppression de tous les attributs sauf ceux de la liste

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder

      L
         liste des attributs a garder



geocode
-------

geocode des objets en les envoyant au gecocodeur addict

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   L    | geocode  |   ?C   |  ?LC   |
+--------+--------+--------+----------+--------+--------+

   en entree clef et liste des champs adresse a geocoder score min pour un succes

      L
         liste attributs adresse
      geocode
         
      ?C
         confiance mini (optionnel)
      ?LC
         liste filtres (optionnel)

      L
         liste attributs adresse
      geocode
         
      ?C
         confiance mini (optionnel)
      ?LC
         liste filtres (optionnel)

      L
         liste attributs adresse
      geocode
         
      ?C
         confiance mini (optionnel)
      ?LC
         liste filtres (optionnel)

      L
         liste attributs adresse
      geocode
         
      ?C
         confiance mini (optionnel)
      ?LC
         liste filtres (optionnel)

      L
         liste attributs adresse
      geocode
         
      ?C
         confiance mini (optionnel)
      ?LC
         liste filtres (optionnel)

      L
         liste attributs adresse
      geocode
         
      ?C
         confiance mini (optionnel)
      ?LC
         liste filtres (optionnel)

      L
         liste attributs adresse
      geocode
         
      ?C
         confiance mini (optionnel)
      ?LC
         liste filtres (optionnel)

      L
         liste attributs adresse
      geocode
         
      ?C
         confiance mini (optionnel)
      ?LC
         liste filtres (optionnel)



geom
----

force l'interpretation de la geometrie

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   geom   |   ?N   |  ?=S   |
+--------+--------+--------+----------+--------+--------+

   force l'interpretation de la geometrie



geom2D
------

passe la geometrie en 2D

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  geom2D  |        |        |
+--------+--------+--------+----------+--------+--------+

   passe la geometrie en 2D



geom3D
------

passe la geometrie en 2D

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   N    |   ?A   |  geom3D  |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   passe la geometrie en 2D



geomprocess
-----------

applique une macro sur une copie de la geometrie et recupere des attributs

syntaxes acceptees
..................

+--------+--------+--------+-------------+--------+--------+
| sortie | defaut | entree |  commande   | param1 | param2 |
+========+========+========+=============+========+========+
|        |        |        | geomprocess |   C    |  ?LC   |
+--------+--------+--------+-------------+--------+--------+

   permet d'appliquer des traitements destructifs sur la geometrie sans l'affecter



geoselect
---------

recupere des attributs par selection geometrique

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   L    |   ?C   |   L    | geoselect |  =in   |   C    |
+--------+--------+--------+-----------+--------+--------+

   liste des attributs a recuperer

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |        |        | geoselect |  =in   |   C    |
+--------+--------+--------+-----------+--------+--------+

   recupere des attributs par selection geometrique



getkey
------

retourne une clef numerique incrementale correspondant a une valeur

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?C   |   ?A   |  getkey  |   ?A   |        |
+--------+--------+--------+----------+--------+--------+

   attribut qui recupere le resultat, valeur de reference a coder , getkey , nom de la clef



grid
----

decoupage en grille

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |        |        |   grid   |   LC   |   N    |
+--------+--------+--------+----------+--------+--------+

   decoupage en grille



gridx
-----

decoupage grille en x

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |        |  gridx   |   N    |   N    |
+--------+--------+--------+----------+--------+--------+

   decoupage grille en x



gridy
-----

decoupage grille en x

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |        |  gridy   |   N    |   N    |
+--------+--------+--------+----------+--------+--------+

   decoupage grille en x



hdel
----

supprime une valeur d un hstore

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |   A    |   hdel   |   L    |   ?    |
+--------+--------+--------+----------+--------+--------+

   supprime une valeur d un hstore



hget
----

eclatement d un hstore

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?    |   A    |   hget   |   A    |        |
+--------+--------+--------+----------+--------+--------+

   destination;defaut;hstore;hget;clef;

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   M    |   ?    |   A    |   hget   |   L    |        |
+--------+--------+--------+----------+--------+--------+

   destination;defaut;hstore;hget;liste clefs;

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   D    |   ?    |   A    |   hget   |   ?L   |        |
+--------+--------+--------+----------+--------+--------+

   destination;defaut;clef;hget;hstore;



hset
----

transforme des attributs en hstore

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |   L    |   hset   |        |        |
+--------+--------+--------+----------+--------+--------+

   liste d attributs en entree

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |   re   |   hset   |        |        |
+--------+--------+--------+----------+--------+--------+

   expression reguliere

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |        |   hset   |        |        |
+--------+--------+--------+----------+--------+--------+

   tous les attributs visibles

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |        |   hset   | =lower |        |
+--------+--------+--------+----------+--------+--------+

   tous les attributs visibles passe les noma en minuscule

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |        |   hset   | =upper |        |
+--------+--------+--------+----------+--------+--------+

   tous les attributs visibles passe les noma en majuscule



hsplit
------

decoupage d'un attribut hstore

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   M    |   ?    |   A    |  hsplit  |   ?L   |        |
+--------+--------+--------+----------+--------+--------+

   decoupage d'un attribut hstore

      M
         

      M
         

      M
         

      M
         

      M
         

      M
         

      M
         



idle
----

ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   idle   |        |        |
+--------+--------+--------+----------+--------+--------+

   ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)



info_schema
-----------

recupere des infos du schema de l'objet

syntaxes acceptees
..................

+--------+--------+--------+-------------+--------+--------+
| sortie | defaut | entree |  commande   | param1 | param2 |
+========+========+========+=============+========+========+
|   A    |   C    |        | info_schema |   ?C   |   ?C   |
+--------+--------+--------+-------------+--------+--------+

   recupere des infos du schema de l'objet

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)

+--------+-----------+--------+-------------+--------+--------+
| sortie |  defaut   | entree |  commande   | param1 | param2 |
+========+===========+========+=============+========+========+
|   A    | =attribut |   C    | info_schema |   ?C   |   ?C   |
+--------+-----------+--------+-------------+--------+--------+

   recupere des infos du schema de l'objet

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe

      A
         attribut qui recupere le resultat
      =attribut
         parametre a recuperer
      C
         nom de l'attribut
      info_schema
         commande,schema,classe



infofich
--------

ajoute les informations du fichier sur les objets

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   ?C   |   ?A   | infofich |        |        |
+--------+--------+--------+----------+--------+--------+

   usage prefix;defaut;attribut;infofich;;;
   prefixe par defaut:#, si pas d'entree s'applique au fichier courant
   cree les attributs: #chemin, #nom, #ext,
        #domaine, #proprietaire, #creation, #modif, #acces



join
----

jointures

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   ?    |   A    |   join   |  C[]   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   sur un fichier dans le repertoire des donnees

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      L
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      C[]
         fichier (dynamique)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |   join   |   #C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   jointures

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

      ?
         sortie (optionnel)
      A
         defaut
      join
         entree
      #C
         
      ?C
         fichier (dynamique) (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |   A    |   join   |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   jointure statique

      A
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      ?C
         fichier (optionnel)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      A
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      ?C
         fichier (optionnel)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      A
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      ?C
         fichier (optionnel)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      A
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      ?C
         fichier (optionnel)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      A
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      ?C
         fichier (optionnel)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      A
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      ?C
         fichier (optionnel)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      A
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      ?C
         fichier (optionnel)
      ?C
         position des champs dans le fichier (ordre) (optionnel)

      A
         sortie
      ?
         defaut (optionnel)
      A
         entree
      join
         
      ?C
         fichier (optionnel)
      ?C
         position des champs dans le fichier (ordre) (optionnel)



lasfilter
---------

decoupage d'un attribut xml en objets

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   A    |   ?    |   ?A   | lasfilter |   C    |  ?=D   |
+--------+--------+--------+-----------+--------+--------+

   decoupage d'un attribut xml en objets

      A
         repertoire de sortie
      ?
         defaut (optionnel)
      ?A
         attribut (optionnel)
      lasfilter
         
      C
         json de traitement
      ?=D
         D: dynamique (optionnel)



lasreader
---------

defineit les fichiers las en entree

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   C    |   ?    |   A    | lasreader |   C    |  ?=D   |
+--------+--------+--------+-----------+--------+--------+

   defineit les fichiers las en entree



len
---

calcule la longueur d un attribut

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?    |   A    |   len    |        |        |
+--------+--------+--------+----------+--------+--------+

   calcule la longueur d un attribut

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree



lire_schema
-----------

associe un schema lu dans un ficher a un objet

syntaxes acceptees
..................

+-----------------+--------+--------+-------------+--------+--------+
|     sortie      | defaut | entree |  commande   | param1 | param2 |
+=================+========+========+=============+========+========+
| ?=schema_entree |   ?C   | ?=map  | lire_schema |   ?C   |   ?C   |
+-----------------+--------+--------+-------------+--------+--------+

   associe un schema lu dans un ficher a un objet

+-----------------+--------+--------+-------------+--------+--------+
|     sortie      | defaut | entree |  commande   | param1 | param2 |
+=================+========+========+=============+========+========+
| ?=schema_sortie |   ?C   | ?=map  | lire_schema |   ?C   |   ?C   |
+-----------------+--------+--------+-------------+--------+--------+

   associe un schema lu dans un ficher a un objet

+-----------+--------+--------+-------------+--------+--------+
|  sortie   | defaut | entree |  commande   | param1 | param2 |
+===========+========+========+=============+========+========+
| ?=#schema |   ?C   | ?=map  | lire_schema |   ?C   |   ?C   |
+-----------+--------+--------+-------------+--------+--------+

   associe un schema lu dans un ficher a un objet



liste_schema
------------

cree des objets virtuels ou reels a partir des schemas (1 objet par classe)

syntaxes acceptees
..................

+-----------+--------+--------+--------------+--------+--------+
|  sortie   | defaut | entree |   commande   | param1 | param2 |
+===========+========+========+==============+========+========+
| ?=#schema |   ?C   |   ?A   | liste_schema |   C    | ?=reel |
+-----------+--------+--------+--------------+--------+--------+

   liste_schema;nom;?reel

cree des objets virtuels par defaut sauf si on precise reel


liste_tables
------------

recupere la liste des tables d un schema a la fin du traitement

syntaxes acceptees
..................

+--------+--------+--------+--------------+--------+--------+
| sortie | defaut | entree |   commande   | param1 | param2 |
+========+========+========+==============+========+========+
|        |        |        | liste_tables |   C    | ?=reel |
+--------+--------+--------+--------------+--------+--------+

   recupere la liste des tables d un schema a la fin du traitement



listefich
---------



syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   S    |   ?C   |   A    | listefich |   ?C   |   ?C   |
+--------+--------+--------+-----------+--------+--------+

   

dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
      S
         attribut de sortie
      ?C
         defaut (optionnel)
      A
         selecteur de fichiers
      listefich
         
      ?C
         repertoire (optionnel)
      ?C
         extension (optionnel)

dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   S    |   ?C   |        | listefich |   ?C   |   ?C   |
+--------+--------+--------+-----------+--------+--------+

   

dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere
dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere


loadconfig
----------

charge des definitions et/ou des macros

syntaxes acceptees
..................

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|        |        |        | loadconfig |   C    |   C    |
+--------+--------+--------+------------+--------+--------+

   repertoire des parametres et des macros



longueur
--------

calcule la longueur de l'objet

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |        | longueur |        |        |
+--------+--------+--------+----------+--------+--------+

   calcule la longueur de l'objet



lower
-----

 passage en minuscule

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?    |   A    |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+

    passage en minuscule d'une valeur d'attribut avec defaut

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   M    |   ?    |   L    |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d'une valeur d'attribut avec defaut passage en minuscule

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   ?    |        |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+

   passage en minuscule d'une lister de valeurs avec defaut

      L
         liste attributs
      ?
         defaut (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   L    |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+

   passage en minuscule d'une lister de valeurs avec defaut

      ?
         defaut (optionnel)
      L
         liste attributs

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |        |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+

    passage en minuscule

      A
         attribut
      ?
         defaut (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+

    passage en minuscule

      ?
         attribut resultat (optionnel)
      A
         defaut
      lower
         attribut d'entree



map
---

mapping en fonction d'un fichier

syntaxes acceptees
..................

+-----------+--------+--------+----------+--------+--------+
|  sortie   | defaut | entree | commande | param1 | param2 |
+===========+========+========+==========+========+========+
| ?=#schema |   ?C   |        |   map    |   C    |        |
+-----------+--------+--------+----------+--------+--------+

   parametres: map; nom du fichier de mapping

si #schema est indique les objets changent de schema
+--------+--------+--------+----------+----------+--------+
| sortie | defaut | entree | commande |  param1  | param2 |
+========+========+========+==========+==========+========+
|        |        |        |   map    | =#struct |        |
+--------+--------+--------+----------+----------+--------+

   mapping en fonction d'une creation dynamique de schema



map_data
--------

applique un mapping complexe aux donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   A    | map_data |   C    |        |
+--------+--------+--------+----------+--------+--------+

   C: fichier de mapping

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   ?C   |   L    | map_data |   C    |        |
+--------+--------+--------+----------+--------+--------+

   C: fichier de mapping

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   *    |   ?C   |   T:   | map_data |   C    |        |
+--------+--------+--------+----------+--------+--------+

   T: definition de type de donnees (T:)



map_schema
----------

effectue des modifications sur un schema en gerant les correspondances

syntaxes acceptees
..................

+----------+--------+--------+------------+--------+--------+
|  sortie  | defaut | entree |  commande  | param1 | param2 |
+==========+========+========+============+========+========+
| =#schema |   C    |        | map_schema |   C    |        |
+----------+--------+--------+------------+--------+--------+

   effectue des modifications sur un schema en gerant les correspondances



match_schema
------------

associe un schema en faisant un mapping au mieux

syntaxes acceptees
..................

+--------+--------+--------+--------------+--------+--------+
| sortie | defaut | entree |   commande   | param1 | param2 |
+========+========+========+==============+========+========+
|        |   ?C   |        | match_schema |   C    |   ?N   |
+--------+--------+--------+--------------+--------+--------+

   associe un schema en faisant un mapping au mieux



mod3D
-----

modifie la 3D  en fonction de criteres sur le Z

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   N    |        |  mod3D   |   C    |        |
+--------+--------+--------+----------+--------+--------+

    valeur de remplacement att/val cond cmp1



multigeom
---------

definit la geometrie comme multiple ou non

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |   N    |        | multigeom |        |        |
+--------+--------+--------+-----------+--------+--------+

   definit la geometrie comme multiple ou non



namejoin
--------

combine des element en nom de fichier en chemin,nom,extention

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   C?   |   L?   | namejoin |        |        |
+--------+--------+--------+----------+--------+--------+

   combine des element en nom de fichier en chemin,nom,extention

      S
         sortie
      C?
         defaut (optionnel)
      L?
         liste d'attributs (optionnel)
      namejoin
         namesjoin

      S
         sortie
      C?
         defaut (optionnel)
      L?
         liste d'attributs (optionnel)
      namejoin
         namesjoin

      S
         sortie
      C?
         defaut (optionnel)
      L?
         liste d'attributs (optionnel)
      namejoin
         namesjoin

      S
         sortie
      C?
         defaut (optionnel)
      L?
         liste d'attributs (optionnel)
      namejoin
         namesjoin

      S
         sortie
      C?
         defaut (optionnel)
      L?
         liste d'attributs (optionnel)
      namejoin
         namesjoin

      S
         sortie
      C?
         defaut (optionnel)
      L?
         liste d'attributs (optionnel)
      namejoin
         namesjoin



namesplit
---------

decoupe un nom de fichier en chemin,nom,extention

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   ?A   |   C?   |   A?   | namesplit |        |        |
+--------+--------+--------+-----------+--------+--------+

   genere les attributs prefix_chemin,prefix_nom,prefix_ext avec un prefixe

      ?A
         prefixe (optionnel)
      C?
         defaut (optionnel)
      A?
         attr contenant le nom (optionnel)
      namesplit
         namesplit

      ?A
         prefixe (optionnel)
      C?
         defaut (optionnel)
      A?
         attr contenant le nom (optionnel)
      namesplit
         namesplit

      ?A
         prefixe (optionnel)
      C?
         defaut (optionnel)
      A?
         attr contenant le nom (optionnel)
      namesplit
         namesplit

      ?A
         prefixe (optionnel)
      C?
         defaut (optionnel)
      A?
         attr contenant le nom (optionnel)
      namesplit
         namesplit

      ?A
         prefixe (optionnel)
      C?
         defaut (optionnel)
      A?
         attr contenant le nom (optionnel)
      namesplit
         namesplit

      ?A
         prefixe (optionnel)
      C?
         defaut (optionnel)
      A?
         attr contenant le nom (optionnel)
      namesplit
         namesplit

      ?A
         prefixe (optionnel)
      C?
         defaut (optionnel)
      A?
         attr contenant le nom (optionnel)
      namesplit
         namesplit



next
----

force la sortie next

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   next   |        |        |
+--------+--------+--------+----------+--------+--------+

   force la sortie next



ordre
-----

ordonne les champs dans un schema

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |        |        |  ordre   |        |        |
+--------+--------+--------+----------+--------+--------+

   ordonne les champs dans un schema



os_copy
-------

copie un fichier

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | os_copy  |   C    |   C    |
+--------+--------+--------+----------+--------+--------+

   attribut qui recupere le resultat, parametres , run , nom, parametres

execution unique au demarrage
      os_copy
         nom destination
      C
         nom d origine

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   A    | os_copy  |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   attribut qui recupere le resultat, parametres , run , nom, parametres

execution pour chaque objet
      A
         nom destination,nom d origine
      ?C
         chemin destination (optionnel)
      A
         chemin origine



os_del
------

supprime un fichier

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  os_del  |   C    |        |
+--------+--------+--------+----------+--------+--------+

   suppression d'un fichier

execution unique au demarrage
      os_del
         
      C
         nom du fichier a supprimer

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   A    |  os_del  |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   suppression d'un fichier

execution pour chaque objet
      ?C
         defaut (optionnel)
      A
         nom du fichier a supprimer
      os_del
         
      ?C
         chemin (optionnel)



os_move
-------

deplace un fichier

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | os_move  |   C    |   C    |
+--------+--------+--------+----------+--------+--------+

   attribut qui recupere le resultat, parametres , run , nom, parametres

execution unique au demarrage
      os_move
         nom destination
      C
         nom d origine

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   A    | os_move  |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   attribut qui recupere le resultat, parametres , run , nom, parametres

execution pour chaque objet
      A
         nom destination,defaut,nom d origine
      ?C
         chemin destination (optionnel)
      A
         chemin origine



os_ren
------

renomme un fichier

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  os_ren  |   C    |   C    |
+--------+--------+--------+----------+--------+--------+

   

execution unique au demarrage
      os_ren
         nom destination
      C
         nom d origine

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   A    |  os_ren  |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

execution pour chaque objet
      A
         nom destination,nom d origine
      ?C
         chemin destination (optionnel)
      A
         chemin origine



pass
----

ne fait rien et passe. permet un branchement distant

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   pass   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   ne fait rien et passe. permet un branchement distant



preload
-------

precharge un fichier en appliquant une macro

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   ?A   | preload  |   ?C   |   C    |
+--------+--------+--------+----------+--------+--------+

   parametres clef;fichier;attribut;preload;macro;nom

les elements entre [] sont pris dans l objet courant
sont reconnus[G] pour #groupe et [F] pour #classe pour le nom de fichier


print
-----

affichage d elements de l objet courant

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   *    |  print   |   C?   | =noms? |
+--------+--------+--------+----------+--------+--------+

   affichage d elements de l objet courant

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   C?   |   L?   |  print   |   C?   | =noms? |
+--------+--------+--------+----------+--------+--------+

   affichage d elements de l objet courant



printv
------

affichage des parametres nommes

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  printv  |   C?   | =noms? |
+--------+--------+--------+----------+--------+--------+

   affichage des parametres nommes



prolonge
--------

prolongation de la ligne d'appui pour les textes

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?N   |   ?A   | prolonge |   ?N   |        |
+--------+--------+--------+----------+--------+--------+

   longueur;[attibut contenant la  longueur];prolonge;code_prolongation



quitter
-------

sort d une macro

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | quitter  |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   sort d une macro



r_min
-----

calcul du rectangle oriente minimal

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  r_min   |        |        |
+--------+--------+--------+----------+--------+--------+

   calcul du rectangle oriente minimal



reel
----

transforme un objet virtuel en objet reel

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   reel   |        |        |
+--------+--------+--------+----------+--------+--------+

   transforme un objet virtuel en objet reel



ren
---

renommage d'un attribut

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |   A    |   ren    |        |        |
+--------+--------+--------+----------+--------+--------+

   renommage d'un attribut

      A
         nouveau nom
      A
         ancien nom

      A
         nouveau nom
      A
         ancien nom

      A
         nouveau nom
      A
         ancien nom

      A
         nouveau nom
      A
         ancien nom

      A
         nouveau nom
      A
         ancien nom

      A
         nouveau nom
      A
         ancien nom

      A
         nouveau nom
      A
         ancien nom

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |        |   L    |   ren    |        |        |
+--------+--------+--------+----------+--------+--------+

   renommage d'une liste d attributs

      L
         liste nouveaux noms
      L
         liste ancien noms

      L
         liste nouveaux noms
      L
         liste ancien noms

      L
         liste nouveaux noms
      L
         liste ancien noms

      L
         liste nouveaux noms
      L
         liste ancien noms

      L
         liste nouveaux noms
      L
         liste ancien noms

      L
         liste nouveaux noms
      L
         liste ancien noms

      L
         liste nouveaux noms
      L
         liste ancien noms



reproj
------

reprojette la geometrie

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   C    |        |  reproj  |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   attribut pour la grille utilisee;systeme d'entree;reproj;systeme de sortie;
   [grilles personnalisées] NG: pas de grilles cus



resetgeom
---------

annulle l'interpretation de la geometrie

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |        |        | resetgeom |        |        |
+--------+--------+--------+-----------+--------+--------+

   annulle l'interpretation de la geometrie



retour
------

ramene les elements apres l execution

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   C?   |   L?   |  retour  |   C?   | =noms? |
+--------+--------+--------+----------+--------+--------+

   ramene les elements apres l execution



retry
-----

relance un traitement a intervalle regulier

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |        |  retry   |   C    |        |
+--------+--------+--------+----------+--------+--------+

   relance un traitement a intervalle regulier



round
-----

arrondit une valeur d attribut à n decimales

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?N   |   A    |  round   |   ?N   |        |
+--------+--------+--------+----------+--------+--------+

   arrondit une valeur d attribut à n decimales

      S
         sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      S
         sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      S
         sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      S
         sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      S
         sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      S
         sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      S
         sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   P    |   ?N   |   A    |  round   |   ?N   |        |
+--------+--------+--------+----------+--------+--------+

    arrondit une variable a n decimales

      P
         variable de sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      P
         variable de sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      P
         variable de sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      P
         variable de sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      P
         variable de sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      P
         variable de sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      P
         variable de sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)

      P
         variable de sortie
      ?N
         defaut (optionnel)
      A
         entree
      round
         
      ?N
         decimales (optionnel)



run
---

execute une commande externe

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?A   |   ?C   |   ?A   |   run    |   C    |        |
+--------+--------+--------+----------+--------+--------+

   

      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
execution a chaque objet avec recuperation d'un resultat (l'attribut d'entree ou la valeur par defaut doivent etre remplis)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?A
         attribut qui recupere le resultat (optionnel)
      ?C
         parametres par defaut (optionnel)
      ?A
         attribut contenant les parametres (optionnel)
      run
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?P   |   =^   |        |   run    |   C    |        |
+--------+--------+--------+----------+--------+--------+

   execute une commande externe

      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      =^
         parametres par defaut
      run
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   ?P   |        |        |   run    |   C    |   C    |
+--------+--------+--------+----------+--------+--------+

   

      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
execution en debut de process avec sans recuperation eventuelle d'un resultat dans une variable
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)
      ?P
         attribut qui recupere le resultat (optionnel)
      run
         parametres par defaut
      C
         attribut contenant les parametres
      C
         commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)


runproc
-------

lancement d'un procedure stockeee

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |  ?LC   |   ?L   | runproc  |   C    |        |
+--------+--------+--------+----------+--------+--------+

   parametres:base;;;;?arguments;?variable contenant les arguments;runsql;?log;?sortie



runsql
------

lancement d'un script sql

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   ?A   |  runsql  |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   parametres:base;;;;?nom;?variable contenant le nom;runsql;?log;?sortie



sample
------

recupere un objet sur x

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   ?A   |  sample  |   N    |  N:N   |
+--------+--------+--------+----------+--------+--------+

   recupere un objet sur x

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   ?A   |  sample  |   N    |   ?N   |
+--------+--------+--------+----------+--------+--------+

   recupere un objet sur x



sc_add_attr
-----------

ajoute un attribut a un schema sans toucher aux objets

syntaxes acceptees
..................

+--------+--------+--------+-------------+--------+--------+
| sortie | defaut | entree |  commande   | param1 | param2 |
+========+========+========+=============+========+========+
|   A    |        |        | sc_add_attr |   C?   |   L?   |
+--------+--------+--------+-------------+--------+--------+

   ajoute un attribut a un schema sans toucher aux objets



sc_supp_attr
------------

supprime un attribut d un schema sans toucher aux objets

syntaxes acceptees
..................

+--------+--------+--------+--------------+--------+--------+
| sortie | defaut | entree |   commande   | param1 | param2 |
+========+========+========+==============+========+========+
|   A    |        |        | sc_supp_attr |   C?   |   L?   |
+--------+--------+--------+--------------+--------+--------+

   supprime un attribut d un schema sans toucher aux objets



schema
------

cree un schema par analyse des objets et l'associe a un objet

syntaxes acceptees
..................

+-----------+--------+--------+----------+--------+--------+
|  sortie   | defaut | entree | commande | param1 | param2 |
+===========+========+========+==========+========+========+
| =#schema? |        |        |  schema  |   C?   |   ?N   |
+-----------+--------+--------+----------+--------+--------+

   cree un schema par analyse des objets et l'associe a un objet



set
---

remplacement d une valeur

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
| =#geom |   ?    |   ?A   |   set    |   C    |   N    |
+--------+--------+--------+----------+--------+--------+

   cree une geometrie texte

      =#geom
         #geom (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      C
         format
      N
         dimension

      =#geom
         #geom (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      C
         format
      N
         dimension

      =#geom
         #geom (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      C
         format
      N
         dimension

      =#geom
         #geom (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      C
         format
      N
         dimension

      =#geom
         #geom (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      C
         format
      N
         dimension

      =#geom
         #geom (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      C
         format
      N
         dimension

      =#geom
         #geom (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      C
         format
      N
         dimension

      =#geom
         #geom (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      C
         format
      N
         dimension

+----------+--------+--------+----------+--------+--------+
|  sortie  | defaut | entree | commande | param1 | param2 |
+==========+========+========+==========+========+========+
| =#schema |   ?    |   ?A   |   set    | ?=maj  |        |
+----------+--------+--------+----------+--------+--------+

   change le schema de reference d'un objet

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

passe en majuscule
      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=maj
          (optionnel)

+----------+--------+--------+----------+--------+--------+
|  sortie  | defaut | entree | commande | param1 | param2 |
+==========+========+========+==========+========+========+
| =#schema |   ?    |   ?A   |   set    | ?=min  |        |
+----------+--------+--------+----------+--------+--------+

   change le schema de reference d'un objet

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

passe en minuscule
      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

      =#schema
         #schema (mot clef)
      ?
         valeur par defaut (optionnel)
      ?A
         attribut d'entree (optionnel)
      set
         
      ?=min
          (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |        |   set    | =match |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d'une valeur d'attribut par les valeurs retenues dans la selection
   par expression regulieres (recupere toute la selection)

      S
         attribut de sortie

      S
         attribut de sortie

      S
         attribut de sortie

      S
         attribut de sortie

      S
         attribut de sortie

      S
         attribut de sortie

      S
         attribut de sortie

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?    |   |L   |   set    |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d'une valeur d'attribut par le premier non vide
   d'une liste avec defaut

      S
         attribut resultat
      ?
         defaut (optionnel)
      |L
         liste d'attributs d'entree separes par |

      S
         attribut resultat
      ?
         defaut (optionnel)
      |L
         liste d'attributs d'entree separes par |

      S
         attribut resultat
      ?
         defaut (optionnel)
      |L
         liste d'attributs d'entree separes par |

      S
         attribut resultat
      ?
         defaut (optionnel)
      |L
         liste d'attributs d'entree separes par |

      S
         attribut resultat
      ?
         defaut (optionnel)
      |L
         liste d'attributs d'entree separes par |

      S
         attribut resultat
      ?
         defaut (optionnel)
      |L
         liste d'attributs d'entree separes par |

      S
         attribut resultat
      ?
         defaut (optionnel)
      |L
         liste d'attributs d'entree separes par |

      S
         attribut resultat
      ?
         defaut (optionnel)
      |L
         liste d'attributs d'entree separes par |

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?    |   ?A   |   set    |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d'une valeur d'attribut avec defaut

      S
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      S
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      S
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      S
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      S
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      S
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      S
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      S
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   P    |   ?    |   ?A   |   set    |        |        |
+--------+--------+--------+----------+--------+--------+

   positionne une variable

      P
         variable (sans les %)
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      P
         variable (sans les %)
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      P
         variable (sans les %)
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      P
         variable (sans les %)
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      P
         variable (sans les %)
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

      P
         variable (sans les %)
      ?
         defaut (optionnel)
      ?A
         attribut d'entree (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   M    |  ?LC   |   ?L   |   set    |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d'une liste de valeurs d'attribut avec defaut

      M
         liste de sortie
      ?LC
         liste de defauts (optionnel)
      ?L
         liste d'entree (optionnel)

      M
         liste de sortie
      ?LC
         liste de defauts (optionnel)
      ?L
         liste d'entree (optionnel)

      M
         liste de sortie
      ?LC
         liste de defauts (optionnel)
      ?L
         liste d'entree (optionnel)

      M
         liste de sortie
      ?LC
         liste de defauts (optionnel)
      ?L
         liste d'entree (optionnel)

      M
         liste de sortie
      ?LC
         liste de defauts (optionnel)
      ?L
         liste d'entree (optionnel)

      M
         liste de sortie
      ?LC
         liste de defauts (optionnel)
      ?L
         liste d'entree (optionnel)

      M
         liste de sortie
      ?LC
         liste de defauts (optionnel)
      ?L
         liste d'entree (optionnel)

      M
         liste de sortie
      ?LC
         liste de defauts (optionnel)
      ?L
         liste d'entree (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   M    |        |        |   set    | =match |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d'une valeur d'attribut par les valeurs retenues dans la selection
   par expression regulieres (recupere les groupes de selections)

      M
         liste de sortie

      M
         liste de sortie

      M
         liste de sortie

      M
         liste de sortie

      M
         liste de sortie

      M
         liste de sortie

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |  NC:   |   set    |        |        |
+--------+--------+--------+----------+--------+--------+

   fonction de calcul libre (attention injection de code)
    les attributs doivent etre précédes de N: pour un traitement numerique
    ou C: pour un traitement alpha

      S
         attribut resultat
      NC:
         formule de calcul

      S
         attribut resultat
      NC:
         formule de calcul

      S
         attribut resultat
      NC:
         formule de calcul

      S
         attribut resultat
      NC:
         formule de calcul

      S
         attribut resultat
      NC:
         formule de calcul

      S
         attribut resultat
      NC:
         formule de calcul

      S
         attribut resultat
      NC:
         formule de calcul



set_schema
----------

positionne des parametres de schema (statique)

syntaxes acceptees
..................

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|   C    |   ?C   |        | set_schema |        |        |
+--------+--------+--------+------------+--------+--------+

   parametres positionnables:
    pk : nom de la clef primaire
    alias : commentaire de la table
    dimension : dimension geometrique
    no_multiple : transforme les attributs multiples en simple

      C
         nom du parametre a positionner
      ?C
         valeur (optionnel)

      C
         nom du parametre a positionner
      ?C
         valeur (optionnel)

      C
         nom du parametre a positionner
      ?C
         valeur (optionnel)

      C
         nom du parametre a positionner
      ?C
         valeur (optionnel)

      C
         nom du parametre a positionner
      ?C
         valeur (optionnel)

      C
         nom du parametre a positionner
      ?C
         valeur (optionnel)

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|   C    |   ?C   |   A    | set_schema |        |        |
+--------+--------+--------+------------+--------+--------+

   positionne des valeurs de schema (dynamique)



setpoint
--------

ajoute une geometrie point a partir des coordonnes en attribut

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   LC   |   ?A   | setpoint |   ?N   |        |
+--------+--------+--------+----------+--------+--------+

   ajoute une geometrie point a partir des coordonnes en attribut

      LC
         defauts
      ?A
         attribut contenant les coordonnees separees par des , (optionnel)
      setpoint
         numero de srid

      LC
         defauts
      ?A
         attribut contenant les coordonnees separees par des , (optionnel)
      setpoint
         numero de srid

      LC
         defauts
      ?A
         attribut contenant les coordonnees separees par des , (optionnel)
      setpoint
         numero de srid

      LC
         defauts
      ?A
         attribut contenant les coordonnees separees par des , (optionnel)
      setpoint
         numero de srid

      LC
         defauts
      ?A
         attribut contenant les coordonnees separees par des , (optionnel)
      setpoint
         numero de srid

      LC
         defauts
      ?A
         attribut contenant les coordonnees separees par des , (optionnel)
      setpoint
         numero de srid

      LC
         defauts
      ?A
         attribut contenant les coordonnees separees par des , (optionnel)
      setpoint
         numero de srid

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   N?   |   L    | setpoint |   ?N   |        |
+--------+--------+--------+----------+--------+--------+

   N: numero de srid

defauts, liste d' attribut (x,y,z) contenant les coordonnees


sleep
-----

ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   ?A   |  sleep   |        |        |
+--------+--------+--------+----------+--------+--------+

   ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)



sortir
------

sortir dans differents formats

syntaxes acceptees
..................

+-----------+--------+--------+----------+--------+--------+
|  sortie   | defaut | entree | commande | param1 | param2 |
+===========+========+========+==========+========+========+
| ?=#schema |   ?C   |   ?L   |  sortir  |   ?C   |   ?C   |
+-----------+--------+--------+----------+--------+--------+

   parametres:?(#schema;nom_schema);?liste_attributs;sortir;format[fanout]?;?nom



split
-----

decoupage d'un attribut en fonction d'un separateur

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   M    |   ?    |   A    |  split   |   .    |  ?N:N  |
+--------+--------+--------+----------+--------+--------+

   decoupage d'un attribut en fonction d'un separateur

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      A
         attribut
      split
         
      .
         caractere decoupage
      ?N:N
         nombre de morceaux:debut (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |  split   |   .    |  ?N:N  |
+--------+--------+--------+----------+--------+--------+

   decoupage d'un attribut en fonction d'un separateur

      ?
         defaut (optionnel)
      A
         attribut
      split
         
      .
         caractere decoupage
      ?N:N
         nombre de morceaux:debut (optionnel)



split_couleur
-------------

decoupe la geometrie selon la couleur

syntaxes acceptees
..................

+--------+--------+--------+---------------+--------+--------+
| sortie | defaut | entree |   commande    | param1 | param2 |
+========+========+========+===============+========+========+
|   A    |        |        | split_couleur |  ?LC   |        |
+--------+--------+--------+---------------+--------+--------+

     une liste de couleurs ou par couleur si aucune couleur n'est precisee

  ajoute des sorties par couleur si une liste est donnee


splitgeom
---------

decoupage inconditionnel des lignes en points

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   ?A   |        |        | splitgeom |        |        |
+--------+--------+--------+-----------+--------+--------+

   decoupage inconditionnel des lignes en points



start
-----

ne fait rien mais envoie un objet virtuel dans le circuit

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |  start   |        |        |
+--------+--------+--------+----------+--------+--------+

   ne fait rien mais envoie un objet virtuel dans le circuit



stat
----

fonctions statistiques

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   C    |   ?    |   ?A   |   stat   |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   nom de la colonne de stat;val;col entree;stat;fonction stat

fonctions disponibles
cnt : comptage
val : liste des valeurs
min : minimum numerique
max : maximum numerique
somme : somme
moy : moyenne


statprint
---------

affiche les stats a travers une macro eventuelle

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |        |        | statprint |   ?C   |        |
+--------+--------+--------+-----------+--------+--------+

   statprint;macro



statprocess
-----------

retraite les stats en appliquant une macro

syntaxes acceptees
..................

+--------+--------+--------+-------------+--------+--------+
| sortie | defaut | entree |  commande   | param1 | param2 |
+========+========+========+=============+========+========+
|        |        |        | statprocess |   C    |   ?C   |
+--------+--------+--------+-------------+--------+--------+

   statprocess;macro de traitement;sortie



strip
-----

supprime des caracteres aux extremites

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?    |   A    |  strip   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   supprime des caracteres aux extremites

      S
         sortie
      ?
         defaut (optionnel)
      A
         attribut
      strip
         
      ?C
         caractere a supprimer blanc par defaut (optionnel)

      S
         sortie
      ?
         defaut (optionnel)
      A
         attribut
      strip
         
      ?C
         caractere a supprimer blanc par defaut (optionnel)

      S
         sortie
      ?
         defaut (optionnel)
      A
         attribut
      strip
         
      ?C
         caractere a supprimer blanc par defaut (optionnel)

      S
         sortie
      ?
         defaut (optionnel)
      A
         attribut
      strip
         
      ?C
         caractere a supprimer blanc par defaut (optionnel)

      S
         sortie
      ?
         defaut (optionnel)
      A
         attribut
      strip
         
      ?C
         caractere a supprimer blanc par defaut (optionnel)

      S
         sortie
      ?
         defaut (optionnel)
      A
         attribut
      strip
         
      ?C
         caractere a supprimer blanc par defaut (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |  strip   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   supprime des caracteres aux estremites

      ?
          (optionnel)
      A
         defaut
      strip
         attribut
      ?C
         caractere a supprimer blanc par defaut (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |        |  strip   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   supprime des caracteres aux estremites

      A
         attribut
      ?
         defaut (optionnel)
      strip
         caractere a supprimer blanc par defaut



sub
---

remplacement d une valeur

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |   ?    |   A    |   sub    |   re   |  ?re   |
+--------+--------+--------+----------+--------+--------+

   application d'une fonction de transformation par expression reguliere

      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions
      S
         resultat
      ?
         defaut (optionnel)
      A
         entree
      sub
         
      re
         expression de selection
      ?re
         expression de substitution (optionnel)

maxsub:nombre maxi de substitutions


supp
----

suppression d'elements

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        | =#geom |   supp   |        |        |
+--------+--------+--------+----------+--------+--------+

   suppression de la geometrie

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
| =#geom |        |        |   supp   |        |        |
+--------+--------+--------+----------+--------+--------+

   suppression d'elements

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

      =#geom
         #geom (mot clef)

+--------+--------+----------+----------+--------+--------+
| sortie | defaut |  entree  | commande | param1 | param2 |
+========+========+==========+==========+========+========+
|        |        | =#schema |   supp   |        |        |
+--------+--------+----------+----------+--------+--------+

   suppression d'elements

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

+----------+--------+--------+----------+--------+--------+
|  sortie  | defaut | entree | commande | param1 | param2 |
+==========+========+========+==========+========+========+
| =#schema |        |        |   supp   |        |        |
+----------+--------+--------+----------+--------+--------+

   suppression d'elements

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

      =#schema
         #schema (mot clef)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   L    |   supp   |        |        |
+--------+--------+--------+----------+--------+--------+

   suppression d une liste d'attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |        |        |   supp   |        |        |
+--------+--------+--------+----------+--------+--------+

   suppression d'elements

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

      L
         liste attributs

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   supp   |        |        |
+--------+--------+--------+----------+--------+--------+

   suppression d l objet complet



sync
----

finit un traitement en parallele et redonne la main sans stats ni ecritures

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        |   sync   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   finit un traitement en parallele et redonne la main sans stats ni ecritures



testobj
-------

cree des objets de test pour les tests fonctionnels

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   LC   |        | testobj  |   C    |   ?N   |
+--------+--------+--------+----------+--------+--------+

   parametres:liste d'attributs,liste valeurs,nom(niv,classe),nombre



tmpstore
--------

stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   ?L   | tmpstore |  =cmp  |   #C   |
+--------+--------+--------+----------+--------+--------+

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   ?L   | tmpstore | =cmpf  |   #C   |
+--------+--------+--------+----------+--------+--------+

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |   ?L   | tmpstore |  =cnt  | ?=clef |
+--------+--------+--------+----------+--------+--------+

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   ?L   | tmpstore | ?=uniq | ?=sort |
+--------+--------+--------+----------+--------+--------+

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

+--------+--------+--------+----------+--------+---------+
| sortie | defaut | entree | commande | param1 | param2  |
+========+========+========+==========+========+=========+
|        |        |   ?L   | tmpstore | ?=uniq | ?=rsort |
+--------+--------+--------+----------+--------+---------+

   liste de clefs,tmpstore;uniq;sort|rsort : stockage avec option de tri

liste de clefs,tmpstore;cmp;nom : prechargement pour comparaisons


translate
---------

translate un objet

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |  ?LN   |   ?A   | translate |        |        |
+--------+--------+--------+-----------+--------+--------+

   translation d un objet par une liste de coordonnees (dans un attribut)

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|        |  ?LN   |   L    | translate |        |        |
+--------+--------+--------+-----------+--------+--------+

   translation d un objet par une liste de coordonnees(liste d attributs)



unique
------

unicite de la sortie laisse passer le premier objet et filtre le reste

syntaxes acceptees
..................

+--------+---------+--------+----------+--------+--------+
| sortie | defaut  | entree | commande | param1 | param2 |
+========+=========+========+==========+========+========+
|   A    | ?=#geom |   ?L   |  unique  |   ?N   |        |
+--------+---------+--------+----------+--------+--------+

   unicite de la sortie laisse passer les N premiers objet et filtre le reste

+--------+---------+--------+----------+--------+--------+
| sortie | defaut  | entree | commande | param1 | param2 |
+========+=========+========+==========+========+========+
|        | ?=#geom |   ?L   |  unique  |        |        |
+--------+---------+--------+----------+--------+--------+

   liste des attibuts devant etre uniques si #geom : test geometrique



upper
-----

remplacement d une valeur

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |   A    |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d'une valeur d'attribut avec defaut passage en majuscule

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |        |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d une valeur

      A
         attribut
      ?
         defaut (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   M    |   ?    |   L    |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d'une valeur d'attribut avec defaut passage en minuscule

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

      M
         liste attributs sortie
      ?
         defaut (optionnel)
      L
         liste attributs entree

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   ?    |        |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+

   passage en majuscule d'une lister de valeurs

      L
         liste attributs
      ?
         defaut (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d une valeur

      ?
         defaut,attribut (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   L    |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+

   passage en majuscule d'une lister de valeurs

      ?
         defaut (optionnel)
      L
         liste attributs



valide_schema
-------------

verifie si des objets sont compatibles avec un schema

syntaxes acceptees
..................

+-----------+--------+--------+---------------+----------+--------+
|  sortie   | defaut | entree |   commande    |  param1  | param2 |
+===========+========+========+===============+==========+========+
| ?=#schema |   ?C   |        | valide_schema | ?=strict |        |
+-----------+--------+--------+---------------+----------+--------+

   verifie si des objets sont compatibles avec un schema

+-----------+--------+--------+---------------+------------+--------+
|  sortie   | defaut | entree |   commande    |   param1   | param2 |
+===========+========+========+===============+============+========+
| ?=#schema |   ?C   |        | valide_schema | =supp_conf |        |
+-----------+--------+--------+---------------+------------+--------+

   verifie si des objets sont compatibles avec un schema



version
-------

affiche la version du logiciel et les infos

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | version  | ?=full |        |
+--------+--------+--------+----------+--------+--------+

   affiche la version du logiciel et les infos



virtuel
-------

transforme un objet reel en objet virtuel

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |        | virtuel  |        |        |
+--------+--------+--------+----------+--------+--------+

   transforme un objet reel en objet virtuel



wfs
---



syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   F    |   ?C   |   ?A   |   wfs    |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   ?A   |   wfs    |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   



xml_load
--------

lecture d un fichier xml dans un attribut

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?    |   ?A   | xml_load |        |        |
+--------+--------+--------+----------+--------+--------+

   lecture d un fichier xml dans un attribut

      A
         attribut de sortie
      ?
         defaut (optionnel)
      ?A
         attribut contenant le nom de fichier (optionnel)
      xml_load
         



xml_save
--------

stockage dans un fichier d un xml contenu dans un attribut

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |   ?C   |   A    | xml_save |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   stockage dans un fichier d un xml contenu dans un attribut

      A
         nom fichier
      ?C
          (optionnel)
      A
         attribut contenant le xml
      xml_save
         
      ?C
         nom du rep (optionnel)



xmledit
-------

modification en place d elements xml

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   re   |   re   |   A    | xmledit  |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

remplacement de texte
      re
         expression de sortie
      re
         selection
      A
         attribut xml
      xmledit
         xmledit
      C
         tag a modifier
      ?C
         groupe de recherche (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   C    |   A    | xmledit  |  A.C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

remplacement ou ajout d un tag
      C
         
      A
         valeur
      xmledit
         attribut xml
      A.C
         xmledit
      ?C
         tag a modifier.parametre (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |  [A]   |   A    | xmledit  |  A.C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

remplacement ou ajout d un tags
      [A]
         
      A
         attribut contenant la valeur
      xmledit
         attribut xml
      A.C
         xmledit
      ?C
         tag a modifier.parametre (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|  ?=\*  |   H    |   A    | xmledit  |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

remplacement ou ajout d un en: remplacement total;attribut hstore contenant clefs/valeurs;attribut xml;xmledit;tag a modifier;groupe de recherche
+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   A    | xmledit  |  A.C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   

suppression d un ensemble de tags
      A
         
      xmledit
         liste de clefs a supprimer
      A.C
         attribut xml
      ?C
         xmledit (optionnel)



xmlextract
----------

extraction de valeurs d un xml

syntaxes acceptees
..................

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|   H    |        |   A    | xmlextract |   C    |   ?C   |
+--------+--------+--------+------------+--------+--------+

   extraction de valeurs d un xml

      H
         attribut sortie(hstore)
      A
         defaut
      xmlextract
         attribut xml
      C
         
      ?C
         tag a extraire (optionnel)

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|   D    |        |   A    | xmlextract |   C    |   ?C   |
+--------+--------+--------+------------+--------+--------+

   extraction de valeurs d un xml

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|   S    |        |   A    | xmlextract |  A.C   |   ?C   |
+--------+--------+--------+------------+--------+--------+

   extraction de valeurs d un xml



xmlsplit
--------

decoupage d'un attribut xml en objets

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |   A    | xmlsplit |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   decoupage d'un attribut xml en objets

      S
         attribut sortie(hstore)
      A
         defaut
      xmlsplit
         attribut xml
      C
         
      ?C
         tag a extraire (optionnel)

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   H    |        |   A    | xmlsplit |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   decoupage d'un attribut xml en objets

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   D    |        |   A    | xmlsplit |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   decoupage d'un attribut xml en objets

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   S    |        |   A    | xmlsplit |  A.C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   decoupage d'un attribut xml en objets

