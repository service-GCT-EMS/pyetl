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

   arrete le traitement

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

   change un chemin relatif en chemin absolu



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
|        |   ?C   |   ?L   | addgeom  |   N    |        |
+--------+--------+--------+----------+--------+--------+

   cree une geometrie pour l'objet

ex: A;addgeom  avec A = (1,2),(3,3) -> (1,2),(3,3)
   cree une geometrie pour l'objet

  X,Y;addgeom avec X=1,2,3,4 et Y=6,7,8,9 -> (1,6),(2,7),(3,8),(4,9)


adquery
-------

extait des information de active_directory

syntaxes acceptees
..................

+--------+--------+--------+----------+----------+--------+
| sortie | defaut | entree | commande |  param1  | param2 |
+========+========+========+==========+==========+========+
|   S    |   ?C   |   ?A   | adquery  | =groupe  |   ?C   |
+--------+--------+--------+----------+----------+--------+
|   S    |   ?C   |   ?A   | adquery  | =machine |   ?C   |
+--------+--------+--------+----------+----------+--------+
|   S    |   ?C   |   ?A   | adquery  |  =user   |   ?C   |
+--------+--------+--------+----------+----------+--------+

   extait des information de active_directory

   extait des information de active_directory

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

   calcule un angle de reference de l'objet



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

   zippe les fichiers ou les repertoires de sortie



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

   traite un attribut d'un objet comme une source de donnees

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

   traite un attribut d'un objet comme une sortie cree un objet pas fanout

pour le conserver positionner la variable keepdata a 1


batch
-----

execute un traitement batch a partir des parametres de l'objet

syntaxes acceptees
..................

+--------+--------+--------+----------+----------------+--------+
| sortie | defaut | entree | commande |     param1     | param2 |
+========+========+========+==========+================+========+
|   A    |   ?C   |   ?A   |  batch   |    =boucle     |   C    |
+--------+--------+--------+----------+----------------+--------+
|   A    |   ?C   |   ?A   |  batch   |     =init      |        |
+--------+--------+--------+----------+----------------+--------+
|   A    |   ?C   |   ?A   |  batch   |     =load      |   C    |
+--------+--------+--------+----------+----------------+--------+
|   A    |   ?C   |   ?A   |  batch   | =parallel_init |        |
+--------+--------+--------+----------+----------------+--------+
|   A    |   ?C   |   ?A   |  batch   |     ?=run      |        |
+--------+--------+--------+----------+----------------+--------+

   execute un traitement batch a partir des parametres de l'objet

demarre a l'initialisation du script
   execute un traitement batch a partir des parametres de l'objet

 en mode parallel_init le traitement demarre a l'initialisation de chaque worker
   execute un traitement batch a partir des parametres de l'objet

 en mode boucle le traitement reprend le jeu de donnees en boucle
   execute un traitement batch a partir des parametres de l'objet

 en mode load le traitement passe une fois le jeu de donnees
   execute un traitement batch a partir des parametres de l'objet

s'autodeclenche dans tous les cas
      A
         attribut_resultat
      ?C
         commandes (optionnel)
      ?A
         attribut_commandes (optionnel)
      batch
         batch
      ?=run
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

   execute un traitement batch en boucle a partir des parametres de l'objet

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

      ?A
         largeur buffer (optionnel)
      ?N
         attribut contenant la largeur (optionnel)
      ?A
         buffer (optionnel)

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
|   ?A   |   ?C   |   ?A   |  charge  |  [A]   |   ?N   |
+--------+--------+--------+----------+--------+--------+

   chargement d objets en fichier

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

   creation des compteurs

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

   compare a un element precharge

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

   compare a un element precharge

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
|   C    |   C    |        | compare_schema |        |        |
+--------+--------+--------+----------------+--------+--------+

   compare un nouveau schema en sortant les differences

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

   extrait les coordonnees d'un point en attributs



creobj
------

cree des objets de test pour les tests fonctionnels

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   L    |   LC   |        |  creobj  |   C    |   ?N   |
+--------+--------+--------+----------+--------+--------+
|   L    |   LC   |   ?L   |  creobj  |   C    |   ?N   |
+--------+--------+--------+----------+--------+--------+

   cree des objets de test pour les tests fonctionnels

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

   decoupage conditionnel de lignes en points



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

   lancement d'une extraction par une extracteur externe



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

   lancement d'un chargement de base par un loader externe



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

   recuperation d'objets depuis la base de donnees



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
|   A    |        |        |  dblast  |        |        |
+--------+--------+--------+----------+--------+--------+

   recupere les derniers enregistrements d 'une couche (superieur a une valeur min)

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

   recuperation d'objets depuis une requete sur la base de donnees



dbschema
--------

recupere les schemas des base de donnees

syntaxes acceptees
..................

+----------------+--------+--------+----------+--------+--------+
|     sortie     | defaut | entree | commande | param1 | param2 |
+================+========+========+==========+========+========+
|                |   C?   |   A?   | dbschema |   ?    |        |
+----------------+--------+--------+----------+--------+--------+
|    =#schema    |   C?   |   A?   | dbschema |   ?    |        |
+----------------+--------+--------+----------+--------+--------+
| =schema_entree |   C?   |        | dbschema |   ?    |        |
+----------------+--------+--------+----------+--------+--------+
| =schema_sortie |   C?   |        | dbschema |   ?    |        |
+----------------+--------+--------+----------+--------+--------+

   recupere les schemas des base de donnees

   recupere les schemas des base de donnees

   recupere les schemas des base de donnees

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



download
--------



syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?C   |   ?A   | download |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+
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

   decoupe la geometrie selon la couleur



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

   filtre en fonction d un attribut



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

   transforme un objet en point en recuperant le n eme point

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
|        |   ?C   |   ?A   | ftp_download |        |        |
+--------+--------+--------+--------------+--------+--------+
|        |   ?C   |   ?A   | ftp_download |   C    |   ?C   |
+--------+--------+--------+--------------+--------+--------+
|   A    |   ?C   |   ?A   | ftp_download |        |        |
+--------+--------+--------+--------------+--------+--------+
|   A    |   ?C   |   ?A   | ftp_download |   C    |   ?C   |
+--------+--------+--------+--------------+--------+--------+

   charge un fichier sur ftp

   charge un fichier sur ftp

   charge un fichier sur ftp

   charge un fichier sur ftp



ftp_upload
----------

charge un fichier sur ftp

syntaxes acceptees
..................

+--------+--------+--------+------------+--------+--------+
| sortie | defaut | entree |  commande  | param1 | param2 |
+========+========+========+============+========+========+
|        | =#att  |   A    | ftp_upload |   ?C   |   C    |
+--------+--------+--------+------------+--------+--------+
|        |   ?C   |   ?A   | ftp_upload |   ?C   |   ?C   |
+--------+--------+--------+------------+--------+--------+

   charge un fichier sur ftp

   charge un fichier sur ftp



garder
------

suppression de tous les attributs sauf ceux de la liste

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   L    |  garder  |        |        |
+--------+--------+--------+----------+--------+--------+
|   L    |        |        |  garder  |        |        |
+--------+--------+--------+----------+--------+--------+
|   L    |   ?L   |   L    |  garder  |        |        |
+--------+--------+--------+----------+--------+--------+

   suppression de tous les attributs sauf ceux de la liste

   suppression de tous les attributs sauf ceux de la liste

   suppression de tous les attributs sauf ceux de la liste

      L
         nouveaux noms
      ?L
         liste val defauts (optionnel)
      L
         attributs a garder



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

   geocode des objets en les envoyant au gecocodeur addict

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

   applique une macro sur une copie de la geometrie et recupere des attributs



geoselect
---------

intersection geometrique par reapport a une couche stockee

syntaxes acceptees
..................

+--------+--------+--------+-----------+--------+--------+
| sortie | defaut | entree | commande  | param1 | param2 |
+========+========+========+===========+========+========+
|   ?L   |  ?LC   |   ?L   | geoselect |  =in   |   C    |
+--------+--------+--------+-----------+--------+--------+

   intersection geometrique par reapport a une couche stockee

l 'objet contenu recupere une liste d attributs de l objet contenant
      ?L
         attributs recuperes (optionnel)
      ?LC
         valeurs recuperees (optionnel)
      ?L
         attributs contenant (optionnel)
      geoselect
         
      =in
         
      C
         nom memoire



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

   retourne une clef numerique incrementale correspondant a une valeur



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
|   D    |   ?    |   A    |   hget   |   ?L   |        |
+--------+--------+--------+----------+--------+--------+
|   M    |   ?    |   A    |   hget   |   L    |        |
+--------+--------+--------+----------+--------+--------+
|   S    |   ?    |   A    |   hget   |   A    |        |
+--------+--------+--------+----------+--------+--------+

   eclatement d un hstore

   eclatement d un hstore

   eclatement d un hstore



hset
----

transforme des attributs en hstore

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   A    |        |        |   hset   |        |        |
+--------+--------+--------+----------+--------+--------+
|   A    |        |        |   hset   | =lower |        |
+--------+--------+--------+----------+--------+--------+
|   A    |        |        |   hset   | =upper |        |
+--------+--------+--------+----------+--------+--------+
|   A    |   ?    |   L    |   hset   |        |        |
+--------+--------+--------+----------+--------+--------+
|   A    |   ?    |   re   |   hset   |        |        |
+--------+--------+--------+----------+--------+--------+

   transforme des attributs en hstore

   transforme des attributs en hstore

   transforme des attributs en hstore

   transforme des attributs en hstore

   transforme des attributs en hstore



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

+--------+-----------+--------+-------------+--------+--------+
| sortie |  defaut   | entree |  commande   | param1 | param2 |
+========+===========+========+=============+========+========+
|   A    | =attribut |   C    | info_schema |   ?C   |   ?C   |
+--------+-----------+--------+-------------+--------+--------+
|   A    |     C     |        | info_schema |   ?C   |   ?C   |
+--------+-----------+--------+-------------+--------+--------+

   recupere des infos du schema de l'objet

   recupere des infos du schema de l'objet

      A
         attribut qui recupere le resultat
      C
         parametre a recuperer
      info_schema
         nom de l'attribut
      ?C
         commande,schema,classe (optionnel)



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

   ajoute les informations du fichier sur les objets



join
----

jointures

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |   join   |   #C   |   ?C   |
+--------+--------+--------+----------+--------+--------+
|   A    |   ?    |   A    |   join   |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+
|   L    |   ?    |   A    |   join   |  C[]   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   jointures

   jointures

   jointures

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



lire_schema
-----------

associe un schema lu dans un ficher a un objet

syntaxes acceptees
..................

+-----------------+--------+--------+-------------+--------+--------+
|     sortie      | defaut | entree |  commande   | param1 | param2 |
+=================+========+========+=============+========+========+
|    ?=#schema    |   ?C   | ?=map  | lire_schema |   ?C   |   ?C   |
+-----------------+--------+--------+-------------+--------+--------+
| ?=schema_entree |   ?C   | ?=map  | lire_schema |   ?C   |   ?C   |
+-----------------+--------+--------+-------------+--------+--------+
| ?=schema_sortie |   ?C   | ?=map  | lire_schema |   ?C   |   ?C   |
+-----------------+--------+--------+-------------+--------+--------+

   associe un schema lu dans un ficher a un objet

   associe un schema lu dans un ficher a un objet

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

   cree des objets virtuels ou reels a partir des schemas (1 objet par classe)

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
|   S    |   ?C   |        | listefich |   ?C   |   ?C   |
+--------+--------+--------+-----------+--------+--------+
|   S    |   ?C   |   A    | listefich |   ?C   |   ?C   |
+--------+--------+--------+-----------+--------+--------+

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

   charge des definitions et/ou des macros



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
|        |   ?    |   A    |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+
|        |   ?    |   L    |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+
|   A    |   ?    |        |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+
|   L    |   ?    |        |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+
|   M    |   ?    |   L    |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+
|   S    |   ?    |   A    |  lower   |        |        |
+--------+--------+--------+----------+--------+--------+

    passage en minuscule

    passage en minuscule

    passage en minuscule

      L
         liste attributs
      ?
         defaut (optionnel)

    passage en minuscule

      ?
         defaut (optionnel)
      L
         liste attributs

    passage en minuscule

      A
         attribut
      ?
         defaut (optionnel)

    passage en minuscule

      ?
         attribut resultat (optionnel)
      A
         defaut
      lower
         attribut d'entree

      S
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree



map
---

mapping en fonction d'un fichier

syntaxes acceptees
..................

+-----------+--------+--------+----------+----------+--------+
|  sortie   | defaut | entree | commande |  param1  | param2 |
+===========+========+========+==========+==========+========+
|           |        |        |   map    | =#struct |        |
+-----------+--------+--------+----------+----------+--------+
| ?=#schema |   ?C   |        |   map    |    C     |        |
+-----------+--------+--------+----------+----------+--------+

   mapping en fonction d'un fichier

si #schema est indique les objets changent de schema
   mapping en fonction d'un fichier



map_data
--------

applique un mapping complexe aux donnees

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   *    |   ?C   |   T:   | map_data |   C    |        |
+--------+--------+--------+----------+--------+--------+
|   A    |   ?C   |   A    | map_data |   C    |        |
+--------+--------+--------+----------+--------+--------+
|   L    |   ?C   |   L    | map_data |   C    |        |
+--------+--------+--------+----------+--------+--------+

   applique un mapping complexe aux donnees

   applique un mapping complexe aux donnees

   applique un mapping complexe aux donnees



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

   modifie la 3D  en fonction de criteres sur le Z



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

   decoupe un nom de fichier en chemin,nom,extention

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
|   A    |   ?C   |   A    | os_copy  |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   copie un fichier

execution unique au demarrage
      os_copy
         nom destination
      C
         nom d origine

   copie un fichier

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
|        |   ?C   |   A    |  os_del  |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   supprime un fichier

execution unique au demarrage
      os_del
         
      C
         nom du fichier a supprimer

   supprime un fichier

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
|   A    |   ?C   |   A    | os_move  |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   deplace un fichier

execution unique au demarrage
      os_move
         nom destination
      C
         nom d origine

   deplace un fichier

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
|   A    |   ?C   |   A    |  os_ren  |   ?C   |   ?C   |
+--------+--------+--------+----------+--------+--------+

   renomme un fichier

execution unique au demarrage
      os_ren
         nom destination
      C
         nom d origine

   renomme un fichier

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

   precharge un fichier en appliquant une macro

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
|        |   C?   |   L?   |  print   |   C?   | =noms? |
+--------+--------+--------+----------+--------+--------+

   affichage d elements de l objet courant

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

   prolongation de la ligne d'appui pour les textes



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
|   L    |        |   L    |   ren    |        |        |
+--------+--------+--------+----------+--------+--------+

   renommage d'un attribut

   renommage d'un attribut

      A
         nouveau nom
      A
         ancien nom



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

   reprojette la geometrie



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
|   P    |   ?N   |   A    |  round   |   ?N   |        |
+--------+--------+--------+----------+--------+--------+
|   S    |   ?N   |   A    |  round   |   ?N   |        |
+--------+--------+--------+----------+--------+--------+

   arrondit une valeur d attribut à n decimales

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
|   ?P   |        |        |   run    |   C    |   C    |
+--------+--------+--------+----------+--------+--------+
|   ?P   |   =^   |        |   run    |   C    |        |
+--------+--------+--------+----------+--------+--------+

   execute une commande externe

execution a chaque objet avec recuperation d'un resultat (l'attribut d'entree ou la valeur par defaut doivent etre remplis)
   execute une commande externe

   execute une commande externe

execution en debut de process avec sans recuperation eventuelle d'un resultat dans une variable
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

   lancement d'un procedure stockeee



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

   lancement d'un script sql



sample
------

recupere un objet sur x

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |        |   ?A   |  sample  |   N    |   ?N   |
+--------+--------+--------+----------+--------+--------+
|        |        |   ?A   |  sample  |   N    |  N:N   |
+--------+--------+--------+----------+--------+--------+

   recupere un objet sur x

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

+----------+--------+--------+----------+--------+--------+
|  sortie  | defaut | entree | commande | param1 | param2 |
+==========+========+========+==========+========+========+
|  =#geom  |   ?    |   ?A   |   set    |   C    |   N    |
+----------+--------+--------+----------+--------+--------+
| =#schema |   ?    |   ?A   |   set    | ?=maj  |        |
+----------+--------+--------+----------+--------+--------+
| =#schema |   ?    |   ?A   |   set    | ?=min  |        |
+----------+--------+--------+----------+--------+--------+
|    M     |        |        |   set    | =match |        |
+----------+--------+--------+----------+--------+--------+
|    M     |  ?LC   |   ?L   |   set    |        |        |
+----------+--------+--------+----------+--------+--------+
|    P     |   ?    |   ?A   |   set    |        |        |
+----------+--------+--------+----------+--------+--------+
|    S     |        |        |   set    | =match |        |
+----------+--------+--------+----------+--------+--------+
|    S     |        |  NC:   |   set    |        |        |
+----------+--------+--------+----------+--------+--------+
|    S     |   ?    |   ?A   |   set    |        |        |
+----------+--------+--------+----------+--------+--------+
|    S     |   ?    |   |L   |   set    |        |        |
+----------+--------+--------+----------+--------+--------+

   remplacement d une valeur

   remplacement d une valeur

passe en majuscule
   remplacement d une valeur

passe en minuscule
   remplacement d une valeur

   remplacement d une valeur

   remplacement d une valeur

   remplacement d une valeur

   remplacement d une valeur

   remplacement d une valeur

   remplacement d une valeur

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
|   C    |   ?C   |   A    | set_schema |        |        |
+--------+--------+--------+------------+--------+--------+

   positionne des parametres de schema (statique)

   positionne des parametres de schema (statique)

      C
         nom du parametre a positionner
      ?C
         valeur (optionnel)



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
|        |   N?   |   L    | setpoint |   ?N   |        |
+--------+--------+--------+----------+--------+--------+

   ajoute une geometrie point a partir des coordonnes en attribut

   ajoute une geometrie point a partir des coordonnes en attribut

defauts, liste d' attribut (x,y,z) contenant les coordonnees
      LC
         defauts
      ?A
         attribut contenant les coordonnees separees par des , (optionnel)
      setpoint
         numero de srid



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

   sortir dans differents formats



split
-----

decoupage d'un attribut en fonction d'un separateur

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |  split   |   .    |  ?N:N  |
+--------+--------+--------+----------+--------+--------+
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

   decoupe la geometrie selon la couleur

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

   fonctions statistiques

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

   affiche les stats a travers une macro eventuelle



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

   retraite les stats en appliquant une macro



strip
-----

supprime des caracteres aux extremites

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |  strip   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+
|   A    |   ?    |        |  strip   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+
|   S    |   ?    |   A    |  strip   |   ?C   |        |
+--------+--------+--------+----------+--------+--------+

   supprime des caracteres aux extremites

   supprime des caracteres aux extremites

      ?
          (optionnel)
      A
         defaut
      strip
         attribut
      ?C
         caractere a supprimer blanc par defaut (optionnel)

   supprime des caracteres aux extremites

      A
         attribut
      ?
         defaut (optionnel)
      strip
         caractere a supprimer blanc par defaut

      S
         sortie
      ?
         defaut (optionnel)
      A
         attribut
      strip
         
      ?C
         caractere a supprimer blanc par defaut (optionnel)



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

   remplacement d une valeur

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

+----------+--------+----------+----------+--------+--------+
|  sortie  | defaut |  entree  | commande | param1 | param2 |
+==========+========+==========+==========+========+========+
|          |        |          |   supp   |        |        |
+----------+--------+----------+----------+--------+--------+
|          |        |  =#geom  |   supp   |        |        |
+----------+--------+----------+----------+--------+--------+
|          |        | =#schema |   supp   |        |        |
+----------+--------+----------+----------+--------+--------+
|          |        |    L     |   supp   |        |        |
+----------+--------+----------+----------+--------+--------+
|  =#geom  |        |          |   supp   |        |        |
+----------+--------+----------+----------+--------+--------+
| =#schema |        |          |   supp   |        |        |
+----------+--------+----------+----------+--------+--------+
|    L     |        |          |   supp   |        |        |
+----------+--------+----------+----------+--------+--------+

   suppression d'elements

   suppression d'elements

   suppression d'elements

   suppression d'elements

   suppression d'elements

   suppression d'elements

   suppression d'elements

      =#geom
         #geom (mot clef)



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

   cree des objets de test pour les tests fonctionnels



tmpstore
--------

stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+---------+
| sortie | defaut | entree | commande | param1 | param2  |
+========+========+========+==========+========+=========+
|        |        |   ?L   | tmpstore |  =cmp  |   #C    |
+--------+--------+--------+----------+--------+---------+
|        |        |   ?L   | tmpstore | =cmpf  |   #C    |
+--------+--------+--------+----------+--------+---------+
|        |        |   ?L   | tmpstore | ?=uniq | ?=rsort |
+--------+--------+--------+----------+--------+---------+
|        |        |   ?L   | tmpstore | ?=uniq | ?=sort  |
+--------+--------+--------+----------+--------+---------+
|   S    |        |   ?L   | tmpstore |  =cnt  | ?=clef  |
+--------+--------+--------+----------+--------+---------+

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

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
|        |  ?LN   |   L    | translate |        |        |
+--------+--------+--------+-----------+--------+--------+

   translate un objet

   translate un objet



unique
------

unicite de la sortie laisse passer le premier objet et filtre le reste

syntaxes acceptees
..................

+--------+---------+--------+----------+--------+--------+
| sortie | defaut  | entree | commande | param1 | param2 |
+========+=========+========+==========+========+========+
|        | ?=#geom |   ?L   |  unique  |        |        |
+--------+---------+--------+----------+--------+--------+
|   A    | ?=#geom |   ?L   |  unique  |   ?N   |        |
+--------+---------+--------+----------+--------+--------+

   unicite de la sortie laisse passer le premier objet et filtre le reste

   unicite de la sortie laisse passer le premier objet et filtre le reste



upper
-----

remplacement d une valeur

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|        |   ?    |   A    |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+
|        |   ?    |   L    |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+
|   A    |   ?    |        |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+
|   A    |   ?    |   A    |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+
|   L    |   ?    |        |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+
|   M    |   ?    |   L    |  upper   |        |        |
+--------+--------+--------+----------+--------+--------+

   remplacement d une valeur

   remplacement d une valeur

      A
         attribut
      ?
         defaut (optionnel)

   remplacement d une valeur

   remplacement d une valeur

      L
         liste attributs
      ?
         defaut (optionnel)

   remplacement d une valeur

      ?
         defaut,attribut (optionnel)

   remplacement d une valeur

      ?
         defaut (optionnel)
      L
         liste attributs

      A
         attribut resultat
      ?
         defaut (optionnel)
      A
         attribut d'entree



valide_schema
-------------

verifie si des objets sont compatibles avec un schema

syntaxes acceptees
..................

+-----------+--------+--------+---------------+------------+--------+
|  sortie   | defaut | entree |   commande    |   param1   | param2 |
+===========+========+========+===============+============+========+
| ?=#schema |   ?C   |        | valide_schema | =supp_conf |        |
+-----------+--------+--------+---------------+------------+--------+
| ?=#schema |   ?C   |        | valide_schema |  ?=strict  |        |
+-----------+--------+--------+---------------+------------+--------+

   verifie si des objets sont compatibles avec un schema

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
|   A    |   ?C   |   ?A   |   wfs    |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+
|   F    |   ?C   |   ?A   |   wfs    |   C    |   ?C   |
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
|        |        |   A    | xmledit  |  A.C   |   ?C   |
+--------+--------+--------+----------+--------+--------+
|        |   C    |   A    | xmledit  |  A.C   |   ?C   |
+--------+--------+--------+----------+--------+--------+
|        |  [A]   |   A    | xmledit  |  A.C   |   ?C   |
+--------+--------+--------+----------+--------+--------+
|  ?=\*  |   H    |   A    | xmledit  |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+
|   re   |   re   |   A    | xmledit  |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+

   modification en place d elements xml

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

   modification en place d elements xml

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

   modification en place d elements xml

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

   modification en place d elements xml

remplacement ou ajout d un en: remplacement total;attribut hstore contenant clefs/valeurs;attribut xml;xmledit;tag a modifier;groupe de recherche
   modification en place d elements xml

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
|   D    |        |   A    | xmlextract |   C    |   ?C   |
+--------+--------+--------+------------+--------+--------+
|   H    |        |   A    | xmlextract |   C    |   ?C   |
+--------+--------+--------+------------+--------+--------+
|   S    |        |   A    | xmlextract |  A.C   |   ?C   |
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

   extraction de valeurs d un xml

   extraction de valeurs d un xml



xmlsplit
--------

decoupage d'un attribut xml en objets

syntaxes acceptees
..................

+--------+--------+--------+----------+--------+--------+
| sortie | defaut | entree | commande | param1 | param2 |
+========+========+========+==========+========+========+
|   D    |        |   A    | xmlsplit |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+
|   H    |        |   A    | xmlsplit |   C    |   ?C   |
+--------+--------+--------+----------+--------+--------+
|   S    |        |   A    | xmlsplit |  A.C   |   ?C   |
+--------+--------+--------+----------+--------+--------+
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

   decoupage d'un attribut xml en objets

   decoupage d'un attribut xml en objets

   decoupage d'un attribut xml en objets

