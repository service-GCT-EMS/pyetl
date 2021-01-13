reference des commandes
=======================

manipulation d'attributs
------------------------

manipulation d'attributs

.. index::
  double: .traitement_alpha;cnt

cnt
...

   creation des compteurs

   le comteur est global s'il a un nom, local s'il n'en a pas

**syntaxes acceptees**

+---------+---------+---------+-----------+---------+-----------+
|sortie   |defaut   |entree   |commande   |param1   |param2     |
+=========+=========+=========+===========+=========+===========+
|S        |?        |?A       |cnt        |?N       |?N         |
+---------+---------+---------+-----------+---------+-----------+
| *le comteur est global s'il a un nom, local s'il n'en a pas*  |
+---------+---------+---------+-----------+---------+-----------+


   S :  attribut de sortie
   ? :  nom fixe (optionnel)
   ?A :  attribut contenant le nom du compteur (optionnel)
   cnt :  
   ?N :  pas (optionnel)
   ?N :  origine (optionnel)



.. index::
  double: .traitement_alpha;format

format
......

   formatte un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |?LC   |?LC   |format  |C     |?C      |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_alpha;garder

garder
......

   suppression de tous les attributs sauf ceux de la liste

   avec renommage de la liste et eventuellemnt valeur par defaut

**syntaxes acceptees**

+----------+----------+----------+------------+----------+------------+
|sortie    |defaut    |entree    |commande    |param1    |param2      |
+==========+==========+==========+============+==========+============+
|L         |?L        |L         |garder      |          |            |
+----------+----------+----------+------------+----------+------------+
| *avec renommage de la liste et eventuellemnt valeur par defaut*     |
+----------+----------+----------+------------+----------+------------+
|          |          |L         |garder      |          |            |
+----------+----------+----------+------------+----------+------------+
|L         |          |          |garder      |          |            |
+----------+----------+----------+------------+----------+------------+


   L :  nouveaux noms
   ?L :  liste val defauts (optionnel)
   L :  attributs a garder



.. index::
  double: .traitement_alpha;join

join
....

   jointures

   sur un fichier dans le repertoire des donnees

**syntaxes acceptees**

+-------+-------+-------+---------+-------+---------+
|sortie |defaut |entree |commande |param1 |param2   |
+=======+=======+=======+=========+=======+=========+
|L      |?      |A      |join     |C[]    |?C       |
+-------+-------+-------+---------+-------+---------+
| *sur un fichier dans le repertoire des donnees*   |
+-------+-------+-------+---------+-------+---------+
|A      |?      |A      |join     |?C     |?C       |
+-------+-------+-------+---------+-------+---------+
| *jointure statique*                               |
+-------+-------+-------+---------+-------+---------+
|M?     |?      |A      |join     |#C     |?C       |
+-------+-------+-------+---------+-------+---------+


   L :  sortie
   ? :  defaut (optionnel)
   A :  entree
   join :  
   C[] :  fichier (dynamique)
   ?C :  position des champs dans le fichier (ordre) (optionnel)



.. index::
  double: .traitement_alpha;len

len
...

   calcule la longueur d un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |?     |A     |len     |      |        |
+------+------+------+--------+------+--------+


   S :  attribut resultat
   ? :  defaut (optionnel)
   A :  attribut d'entree



.. index::
  double: .traitement_alpha;lower

lower
.....

    passage en minuscule

    passage en minuscule d'une valeur d'attribut avec defaut

**syntaxes acceptees**

+-----------+-----------+-----------+-------------+-----------+-------------+
|sortie     |defaut     |entree     |commande     |param1     |param2       |
+===========+===========+===========+=============+===========+=============+
|S          |?          |A          |lower        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| * passage en minuscule d'une valeur d'attribut avec defaut*               |
+-----------+-----------+-----------+-------------+-----------+-------------+
|M          |?          |L          |lower        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *remplacement d'une valeur d'attribut avec defaut passage en minuscule*   |
+-----------+-----------+-----------+-------------+-----------+-------------+
|L          |?          |           |lower        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
|A          |?          |           |lower        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
|           |?          |L          |lower        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
|           |?          |A          |lower        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+


   L :  liste attributs
   ? :  defaut (optionnel)

   ? :  defaut (optionnel)
   L :  liste attributs

   A :  attribut
   ? :  defaut (optionnel)

   ? :  attribut resultat (optionnel)
   A :  defaut
   lower :  attribut d'entree

   S :  attribut resultat
   ? :  defaut (optionnel)
   A :  attribut d'entree



.. index::
  double: .traitement_alpha;ren

ren
...

   renommage d'un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |A     |ren     |      |        |
+------+------+------+--------+------+--------+
|L     |      |L     |ren     |      |        |
+------+------+------+--------+------+--------+


   A :  nouveau nom
   A :  ancien nom



.. index::
  double: .traitement_alpha;round

round
.....

   arrondit une valeur d attribut à n decimales


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |?N    |A     |round   |?N    |        |
+------+------+------+--------+------+--------+
|P     |?N    |A     |round   |?N    |        |
+------+------+------+--------+------+--------+


   S :  sortie
   ?N :  defaut (optionnel)
   A :  entree
   round :  
   ?N :  decimales (optionnel)



.. index::
  double: .traitement_alpha;set

set
...

   remplacement d une valeur

   fonction de calcul libre (attention injection de code)
    les attributs doivent etre précédes de N: pour un traitement numerique
    ou C: pour un traitement alpha

**syntaxes acceptees**

+--------------+------------+------------+--------------+------------+--------------+
|sortie        |defaut      |entree      |commande      |param1      |param2        |
+==============+============+============+==============+============+==============+
|=#geom        |?           |?A          |set           |C           |N             |
+--------------+------------+------------+--------------+------------+--------------+
| *cree une geometrie texte*                                                        |
+--------------+------------+------------+--------------+------------+--------------+
|S             |            |            |set           |=match      |              |
+--------------+------------+------------+--------------+------------+--------------+
| *remplacement d'une valeur d'attribut par les valeurs retenues dans la selection* |
| *par expression regulieres (recupere toute la selection)*                         |
+--------------+------------+------------+--------------+------------+--------------+
|S             |?           |\|L         |set           |            |              |
+--------------+------------+------------+--------------+------------+--------------+
| *remplacement d'une valeur d'attribut par le premier non vide*                    |
| *d'une liste avec defaut*                                                         |
+--------------+------------+------------+--------------+------------+--------------+
|S             |?           |?A          |set           |            |              |
+--------------+------------+------------+--------------+------------+--------------+
| *remplacement d'une valeur d'attribut avec defaut*                                |
+--------------+------------+------------+--------------+------------+--------------+
|P             |?           |?A          |set           |            |              |
+--------------+------------+------------+--------------+------------+--------------+
| *positionne une variable*                                                         |
+--------------+------------+------------+--------------+------------+--------------+
|M             |?LC         |?L          |set           |            |              |
+--------------+------------+------------+--------------+------------+--------------+
| *remplacement d'une liste de valeurs d'attribut avec defaut*                      |
+--------------+------------+------------+--------------+------------+--------------+
|M             |            |            |set           |=match      |              |
+--------------+------------+------------+--------------+------------+--------------+
| *remplacement d'une valeur d'attribut par les valeurs retenues dans la selection* |
| *par expression regulieres (recupere les groupes de selections)*                  |
+--------------+------------+------------+--------------+------------+--------------+
|S             |            |NC:         |set           |            |              |
+--------------+------------+------------+--------------+------------+--------------+
| *fonction de calcul libre (attention injection de code)*                          |
| * les attributs doivent etre précédes de N: pour un traitement numerique*         |
| * ou C: pour un traitement alpha*                                                 |
+--------------+------------+------------+--------------+------------+--------------+
|=#schema      |?           |?A          |set           |?=maj       |              |
+--------------+------------+------------+--------------+------------+--------------+
| *passe en majuscule*                                                              |
+--------------+------------+------------+--------------+------------+--------------+
|=#schema      |?           |?A          |set           |?=min       |              |
+--------------+------------+------------+--------------+------------+--------------+
| *passe en minuscule*                                                              |
+--------------+------------+------------+--------------+------------+--------------+


   S :  attribut resultat
   NC: :  formule de calcul



.. index::
  double: .traitement_alpha;split

split
.....

   decoupage d'un attribut en fonction d'un separateur

   s'il n'y a pas d'attributs de sortie on cree un objet pour chaque element

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|M     |?     |A     |split   |.     |?N:N    |
+------+------+------+--------+------+--------+
|      |?     |A     |split   |.     |?N:N    |
+------+------+------+--------+------+--------+


   M :  liste attributs sortie
   ? :  defaut (optionnel)
   A :  attribut
   split :  
   . :  caractere decoupage
   ?N:N :  nombre de morceaux:debut (optionnel)

   ? :  defaut (optionnel)
   A :  attribut
   split :  
   . :  caractere decoupage
   ?N:N :  nombre de morceaux:debut (optionnel)



.. index::
  double: .traitement_alpha;strip

strip
.....

   supprime des caracteres aux extremites


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |?     |A     |strip   |?C    |        |
+------+------+------+--------+------+--------+
|      |?     |A     |strip   |?C    |        |
+------+------+------+--------+------+--------+
|A     |?     |      |strip   |?C    |        |
+------+------+------+--------+------+--------+


   ? :   (optionnel)
   A :  defaut
   strip :  attribut
   ?C :  caractere a supprimer blanc par defaut (optionnel)

   A :  attribut
   ? :  defaut (optionnel)
   strip :  caractere a supprimer blanc par defaut

   S :  sortie
   ? :  defaut (optionnel)
   A :  attribut
   strip :  
   ?C :  caractere a supprimer blanc par defaut (optionnel)



.. index::
  double: .traitement_alpha;sub

sub
...

   remplacement d une valeur

   application d'une fonction de transformation par expression reguliere

**syntaxes acceptees**

+-----------+-----------+-----------+-------------+-----------+-------------+
|sortie     |defaut     |entree     |commande     |param1     |param2       |
+===========+===========+===========+=============+===========+=============+
|S          |?          |A          |sub          |re         |?re          |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *application d'une fonction de transformation par expression reguliere*   |
+-----------+-----------+-----------+-------------+-----------+-------------+


   S :  resultat
   ? :  defaut (optionnel)
   A :  entree
   sub :  
   re :  expression de selection
   ?re :  expression de substitution (optionnel)

maxsub:nombre maxi de substitutions


.. index::
  double: .traitement_alpha;supp

supp
....

   suppression d'elements

   suppression de la geometrie

**syntaxes acceptees**

+--------+------+--------+--------+------+--------+
|sortie  |defaut|entree  |commande|param1|param2  |
+========+======+========+========+======+========+
|        |      |=#geom  |supp    |      |        |
+--------+------+--------+--------+------+--------+
| *suppression de la geometrie*                   |
+--------+------+--------+--------+------+--------+
|        |      |L       |supp    |      |        |
+--------+------+--------+--------+------+--------+
| *suppression d une liste d'attributs*           |
+--------+------+--------+--------+------+--------+
|        |      |        |supp    |      |        |
+--------+------+--------+--------+------+--------+
| *suppression d l objet complet*                 |
+--------+------+--------+--------+------+--------+
|        |      |=#schema|supp    |      |        |
+--------+------+--------+--------+------+--------+
|=#geom  |      |        |supp    |      |        |
+--------+------+--------+--------+------+--------+
|=#schema|      |        |supp    |      |        |
+--------+------+--------+--------+------+--------+
|L       |      |        |supp    |      |        |
+--------+------+--------+--------+------+--------+


   =#geom :  #geom (mot clef)



.. index::
  double: .traitement_alpha;upper

upper
.....

   remplacement d une valeur

   remplacement d'une valeur d'attribut avec defaut passage en majuscule

**syntaxes acceptees**

+-----------+-----------+-----------+-------------+-----------+-------------+
|sortie     |defaut     |entree     |commande     |param1     |param2       |
+===========+===========+===========+=============+===========+=============+
|A          |?          |A          |upper        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *remplacement d'une valeur d'attribut avec defaut passage en majuscule*   |
+-----------+-----------+-----------+-------------+-----------+-------------+
|M          |?          |L          |upper        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *remplacement d'une valeur d'attribut avec defaut passage en minuscule*   |
+-----------+-----------+-----------+-------------+-----------+-------------+
|A          |?          |           |upper        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
|L          |?          |           |upper        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
|           |?          |A          |upper        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
|           |?          |L          |upper        |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+


   A :  attribut
   ? :  defaut (optionnel)

   L :  liste attributs
   ? :  defaut (optionnel)

   ? :  defaut,attribut (optionnel)

   ? :  defaut (optionnel)
   L :  liste attributs

   A :  attribut resultat
   ? :  defaut (optionnel)
   A :  attribut d'entree


fonctions auxiliaires
---------------------

fonctions auxiliaires

.. index::
  double: .traitement_aux;stat

stat
....

   fonctions statistiques

   nom de la colonne de stat;val;col entree;stat;fonction stat

**syntaxes acceptees**

+---------+---------+---------+-----------+---------+-----------+
|sortie   |defaut   |entree   |commande   |param1   |param2     |
+=========+=========+=========+===========+=========+===========+
|C        |?        |?A       |stat       |C        |?C         |
+---------+---------+---------+-----------+---------+-----------+
| *nom de la colonne de stat;val;col entree;stat;fonction stat* |
+---------+---------+---------+-----------+---------+-----------+



fonctions de cryptage
---------------------

fonctions de cryptage

.. index::
  double: .traitement_crypt;crypt

crypt
.....

   crypte des valeurs dans un fichier en utilisant une clef


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?     |A     |crypt   |C?    |        |
+------+------+------+--------+------+--------+


   A :  attribut resultat crypte
   ? :  defaut (optionnel)
   A :  attribut d'entree
   crypt :  
   C? :  clef de cryptage (optionnel)



.. index::
  double: .traitement_crypt;decrypt

decrypt
.......

   decrypte des valeurs dans un fichier en utilisant une clef


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?     |A     |decrypt |C?    |        |
+------+------+------+--------+------+--------+


   A :  attribut resultat decrypte
   ? :  defaut (optionnel)
   A :  attribut d'entree
   decrypt :  
   C? :  clef de cryptage (optionnel)


accés aux bases de données
--------------------------

accés aux bases de données

.. index::
  double: .traitement_db;dbalpha

dbalpha
.......

   recuperation d'objets depuis la base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |?     |?     |dbalpha |?     |?       |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbclean

dbclean
.......

   vide un ensemble de tables


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbclean |?C    |?C      |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbclose

dbclose
.......

   recuperation d'objets depuis la base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbclose |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbcount

dbcount
.......

   nombre d'objets dans un groupe de tables


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |      |      |dbcount |?C    |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbextdump

dbextdump
.........

   lancement d'une extraction par une extracteur externe

   parametres:base;;;;;;dbextdump;dest;?log

**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |      |      |dbextdump|?C    |?C      |
+------+------+------+---------+------+--------+
| *parametres:base;;;;;;dbextdump;dest;?log*   |
+------+------+------+---------+------+--------+




.. index::
  double: .traitement_db;dbextload

dbextload
.........

   lancement d'un chargement de base par un loader externe

   parametres:base;;;;?nom;?variable contenant le nom;dbextload;log;

**syntaxes acceptees**

+----------+----------+----------+-------------+----------+------------+
|sortie    |defaut    |entree    |commande     |param1    |param2      |
+==========+==========+==========+=============+==========+============+
|          |?C        |?A        |dbextload    |C         |            |
+----------+----------+----------+-------------+----------+------------+
| *parametres:base;;;;?nom;?variable contenant le nom;dbextload;log;*  |
+----------+----------+----------+-------------+----------+------------+




.. index::
  double: .traitement_db;dbgeo

dbgeo
.....

   recuperation d'objets depuis la base de donnees

   db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;buffer

**syntaxes acceptees**

+-------------+-------------+-------------+---------------+-------------+---------------+
|sortie       |defaut       |entree       |commande       |param1       |param2         |
+=============+=============+=============+===============+=============+===============+
|?L           |?            |?L           |dbgeo          |?C           |?N             |
+-------------+-------------+-------------+---------------+-------------+---------------+
| *db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;buffer*    |
+-------------+-------------+-------------+---------------+-------------+---------------+




.. index::
  double: .traitement_db;dblast

dblast
......

   recupere les derniers enregistrements d 'une couche (superieur a une valeur min)


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dblast  |C     |        |
+------+------+------+--------+------+--------+
|A     |      |      |dblast  |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbmap_qgs

dbmap_qgs
.........

   remappe des fichiers qgis pour un usage en local en prenant en comte un selecteur


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |C     |      |dbmap_qgs|C     |C       |
+------+------+------+---------+------+--------+




.. index::
  double: .traitement_db;dbmaxval

dbmaxval
........

   valeur maxi d une clef en base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|P     |      |      |dbmaxval|?C    |        |
+------+------+------+--------+------+--------+
|A     |      |      |dbmaxval|?C    |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbreq

dbreq
.....

   recuperation d'objets depuis une requete sur la base de donnees

   db:base;niveau;classe;attr;att_sortie;valeurs;champ a integrer;dbreq;requete;destination
   si la requete contient %#niveau ou %#classe la requete est passee sur chaque
   classe du selecteur en substituant les variables par la classe courante
   sinon elle est passee une fois pour chaque base du selecteur
   les variables %#base et %#attr sont egalement substituees

**syntaxes acceptees**

+--------------+--------------+--------------+----------------+--------------+----------------+
|sortie        |defaut        |entree        |commande        |param1        |param2          |
+==============+==============+==============+================+==============+================+
|?A            |?             |?L            |dbreq           |C             |?A.C            |
+--------------+--------------+--------------+----------------+--------------+----------------+
| *db:base;niveau;classe;attr;att_sortie;valeurs;champ a integrer;dbreq;requete;destination*  |
| *si la requete contient %#niveau ou %#classe la requete est passee sur chaque*              |
| *classe du selecteur en substituant les variables par la classe courante*                   |
| *sinon elle est passee une fois pour chaque base du selecteur*                              |
| *les variables %#base et %#attr sont egalement substituees*                                 |
+--------------+--------------+--------------+----------------+--------------+----------------+
|?A            |?             |?L            |dbreq           |C             |?A              |
+--------------+--------------+--------------+----------------+--------------+----------------+




.. index::
  double: .traitement_db;dbschema

dbschema
........

   recupere les schemas des base de donnees

   db:base;niveau;classe;;destination;nom_schema;;dbschema;select_tables;

**syntaxes acceptees**

+--------------+------+------+--------+------+--------+
|sortie        |defaut|entree|commande|param1|param2  |
+==============+======+======+========+======+========+
|=schema_entree|C?    |      |dbschema|?     |        |
+--------------+------+------+--------+------+--------+
|=schema_sortie|C?    |      |dbschema|?     |        |
+--------------+------+------+--------+------+--------+
|=#schema      |C?    |A?    |dbschema|?     |        |
+--------------+------+------+--------+------+--------+
|              |C?    |A?    |dbschema|?     |        |
+--------------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbselect

dbselect
........

   creation d un selecteur: ce selecteur peut etre reutilise pour des operations
   sur les bases de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?     |?     |dbselect|?     |?       |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbtmp

dbtmp
.....

   creation de structures temporaires dans la base de donnees permets de preparer les requetes


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |?     |?     |dbtmp   |?     |?       |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbupdate

dbupdate
........

   chargement en base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbupdate|      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;dbwrite

dbwrite
.......

   chargement en base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbwrite |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_db;runproc

runproc
.......

   lancement d'un procedure stockeee

   parametres:base;;;;?arguments;?variable contenant les arguments;runsql;?log;?sortie

**syntaxes acceptees**

+-------------+-------------+-------------+---------------+-------------+---------------+
|sortie       |defaut       |entree       |commande       |param1       |param2         |
+=============+=============+=============+===============+=============+===============+
|             |?LC          |?L           |runproc        |C            |               |
+-------------+-------------+-------------+---------------+-------------+---------------+
| *parametres:base;;;;?arguments;?variable contenant les arguments;runsql;?log;?sortie* |
+-------------+-------------+-------------+---------------+-------------+---------------+




.. index::
  double: .traitement_db;runsql

runsql
......

   lancement d'un script sql via un loader externe

   parametres:base;;;;?nom;?variable contenant le nom;runsql;?log;?sortie

**syntaxes acceptees**

+-----------+-----------+-----------+-------------+-----------+-------------+
|sortie     |defaut     |entree     |commande     |param1     |param2       |
+===========+===========+===========+=============+===========+=============+
|           |?C         |?A         |runsql       |?C         |?C           |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *parametres:base;;;;?nom;?variable contenant le nom;runsql;?log;?sortie*  |
+-----------+-----------+-----------+-------------+-----------+-------------+



divers
------

divers

.. index::
  double: .traitement_divers;compare

compare
.......

   compare a un element precharge

   parametres clef;fichier;attribut;preload;macro;nom

**syntaxes acceptees**

+--------+--------+--------+----------+--------+----------+
|sortie  |defaut  |entree  |commande  |param1  |param2    |
+========+========+========+==========+========+==========+
|A       |        |?L      |compare   |A       |C         |
+--------+--------+--------+----------+--------+----------+
| *parametres clef;fichier;attribut;preload;macro;nom*    |
+--------+--------+--------+----------+--------+----------+




.. index::
  double: .traitement_divers;compare2

compare2
........

   compare a un element precharge

   parametres clef;fichier;attribut;preload;macro;nom

**syntaxes acceptees**

+--------+--------+--------+----------+--------+----------+
|sortie  |defaut  |entree  |commande  |param1  |param2    |
+========+========+========+==========+========+==========+
|A       |        |?L      |compare2  |A       |C         |
+--------+--------+--------+----------+--------+----------+
| *parametres clef;fichier;attribut;preload;macro;nom*    |
+--------+--------+--------+----------+--------+----------+




.. index::
  double: .traitement_divers;getkey

getkey
......

   retourne une clef numerique incrementale correspondant a une valeur

   attribut qui recupere le resultat, valeur de reference a coder , getkey , nom de la clef

**syntaxes acceptees**

+--------------+--------------+--------------+----------------+--------------+----------------+
|sortie        |defaut        |entree        |commande        |param1        |param2          |
+==============+==============+==============+================+==============+================+
|S             |?C            |?A            |getkey          |?A            |                |
+--------------+--------------+--------------+----------------+--------------+----------------+
| *attribut qui recupere le resultat, valeur de reference a coder , getkey , nom de la clef*  |
+--------------+--------------+--------------+----------------+--------------+----------------+




.. index::
  double: .traitement_divers;loadconfig

loadconfig
..........

   charge des definitions et/ou des macros

   repertoire des parametres et des macros

**syntaxes acceptees**

+------+------+------+----------+------+--------+
|sortie|defaut|entree|commande  |param1|param2  |
+======+======+======+==========+======+========+
|      |      |      |loadconfig|C     |C       |
+------+------+------+----------+------+--------+
| *repertoire des parametres et des macros*     |
+------+------+------+----------+------+--------+




.. index::
  double: .traitement_divers;log

log
...

   affichie un message dans le log


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |?C    |?L    |log     |C     |=WARN   |
+------+------+------+--------+------+--------+
|      |?C    |?L    |log     |C     |=ERROR  |
+------+------+------+--------+------+--------+
|      |?C    |?L    |log     |C     |        |
+------+------+------+--------+------+--------+


   ?C :  defaut (optionnel)
   ?L :  attributs en entree (optionnel)
   log :  
   C :  message
   =WARN :  niveau



.. index::
  double: .traitement_divers;objgroup

objgroup
........

   accumule des attributs en un tableau


**syntaxes acceptees**

+------------+------------+------------+--------------+------------+--------------+
|sortie      |defaut      |entree      |commande      |param1      |param2        |
+============+============+============+==============+============+==============+
|L           |?C          |L           |objgroup      |C           |?L            |
+------------+------------+------------+--------------+------------+--------------+
| *cree un tableau par attribut autant de tableaux que de champs en entree*       |
| *si un seul attribut en sortie cree un tableau contenant des champs nommes*     |
+------------+------------+------------+--------------+------------+--------------+


   L :  attributs en sortie
   ?C :  defaut (optionnel)
   L :  attributs en entree
   objgroup :  
   C :  nom de la classe en sortie
   ?L :  attributs de groupage (optionnel)



.. index::
  double: .traitement_divers;preload

preload
.......

   precharge un fichier en appliquant une macro

   parametres clef;fichier;attribut;preload;macro;nom

**syntaxes acceptees**

+--------+--------+--------+----------+--------+----------+
|sortie  |defaut  |entree  |commande  |param1  |param2    |
+========+========+========+==========+========+==========+
|A       |?C      |?A      |preload   |?C      |C         |
+--------+--------+--------+----------+--------+----------+
| *parametres clef;fichier;attribut;preload;macro;nom*    |
+--------+--------+--------+----------+--------+----------+




.. index::
  double: .traitement_divers;sortir

sortir
......

   sortir dans differents formats

   parametres:?(#schema;nom_schema);?liste_attributs;sortir;format[fanout]?;?nom

**syntaxes acceptees**

+---------------+------------+------------+--------------+------------+--------------+
|sortie         |defaut      |entree      |commande      |param1      |param2        |
+===============+============+============+==============+============+==============+
|?=#schema      |?C          |?L          |sortir        |?C          |?C            |
+---------------+------------+------------+--------------+------------+--------------+
| *parametres:?(#schema;nom_schema);?liste_attributs;sortir;format[fanout]?;?nom*    |
+---------------+------------+------------+--------------+------------+--------------+




.. index::
  double: .traitement_divers;tmpstore

tmpstore
........

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie

   liste de clefs,tmpstore;uniq;sort|rsort : stockage avec option de tri

**syntaxes acceptees**

+----------+----------+----------+------------+----------+------------+
|sortie    |defaut    |entree    |commande    |param1    |param2      |
+==========+==========+==========+============+==========+============+
|          |          |?L        |tmpstore    |?=uniq    |?=sort      |
+----------+----------+----------+------------+----------+------------+
|          |          |?L        |tmpstore    |?=uniq    |?=rsort     |
+----------+----------+----------+------------+----------+------------+
| *liste de clefs,tmpstore;cmp;nom : prechargement pour comparaisons* |
+----------+----------+----------+------------+----------+------------+
|          |          |?L        |tmpstore    |=cmp      |#C          |
+----------+----------+----------+------------+----------+------------+
|          |          |?L        |tmpstore    |=cmpf     |#C          |
+----------+----------+----------+------------+----------+------------+
|S         |          |?L        |tmpstore    |=cnt      |?=clef      |
+----------+----------+----------+------------+----------+------------+




.. index::
  double: .traitement_divers;unique

unique
......

   unicite de la sortie laisse passer le premier objet et filtre le reste

   liste des attibuts devant etre uniques si #geom : test geometrique

**syntaxes acceptees**

+----------+-----------+----------+------------+----------+------------+
|sortie    |defaut     |entree    |commande    |param1    |param2      |
+==========+===========+==========+============+==========+============+
|A         |?=#geom    |?L        |unique      |?N        |            |
+----------+-----------+----------+------------+----------+------------+
|          |?=#geom    |?L        |unique      |          |            |
+----------+-----------+----------+------------+----------+------------+
| *liste des attibuts devant etre uniques si #geom : test geometrique* |
+----------+-----------+----------+------------+----------+------------+



fonctions géometriques
----------------------

fonctions géometriques

.. index::
  double: .traitement_geom;addgeom

addgeom
.......

   cree une geometrie pour l'objet

   N:type geometrique

**syntaxes acceptees**

+-----------+-----------+-----------+-------------+-----------+-------------+
|sortie     |defaut     |entree     |commande     |param1     |param2       |
+===========+===========+===========+=============+===========+=============+
|           |?C         |?A         |addgeom      |N          |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *ex: A;addgeom  avec A = (1,2),(3,3) -> (1,2),(3,3)*                      |
+-----------+-----------+-----------+-------------+-----------+-------------+
|           |?C         |?L         |addgeom      |N          |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *  X,Y;addgeom avec X=1,2,3,4 et Y=6,7,8,9 -> (1,6),(2,7),(3,8),(4,9)*    |
+-----------+-----------+-----------+-------------+-----------+-------------+




.. index::
  double: .traitement_geom;aire

aire
....

   calcule l'aire de l'objet


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |      |      |aire    |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;change_couleur

change_couleur
..............

   remplace une couleur par une autre


**syntaxes acceptees**

+------+------+------+--------------+------+--------+
|sortie|defaut|entree|commande      |param1|param2  |
+======+======+======+==============+======+========+
|      |      |      |change_couleur|C     |C       |
+------+------+------+--------------+------+--------+




.. index::
  double: .traitement_geom;coordp

coordp
......

   extrait les coordonnees d'un point en attributs

   les coordonnees sont sous #x,#y,#z

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?M    |?N    |?A    |coordp  |      |        |
+------+------+------+--------+------+--------+
| *les coordonnees sont sous #x,#y,#z*        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;csplit

csplit
......

   decoupage conditionnel de lignes en points

   expression sur les coordonnes : x y z

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |      |      |csplit  |C     |        |
+------+------+------+--------+------+--------+
| *expression sur les coordonnes : x y z*     |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;extract_couleur

extract_couleur
...............

   decoupe la geometrie selon la couleur

    ne garde que les couleurs precisees

**syntaxes acceptees**

+------+------+------+---------------+------+--------+
|sortie|defaut|entree|commande       |param1|param2  |
+======+======+======+===============+======+========+
|      |      |      |extract_couleur|LC    |        |
+------+------+------+---------------+------+--------+
| * ne garde que les couleurs precisees*             |
+------+------+------+---------------+------+--------+




.. index::
  double: .traitement_geom;force_ligne

force_ligne
...........

   force la geometrie en ligne


**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|      |      |      |force_ligne|      |        |
+------+------+------+-----------+------+--------+




.. index::
  double: .traitement_geom;force_pt

force_pt
........

   transforme un objet en point en recuperant le n eme point

   les points sont comptes a partir de 0 negatif pour compter depuis la fin

**syntaxes acceptees**

+------------+------------+------------+--------------+------------+--------------+
|sortie      |defaut      |entree      |commande      |param1      |param2        |
+============+============+============+==============+============+==============+
|            |?C          |?A          |force_pt      |            |              |
+------------+------------+------------+--------------+------------+--------------+
| *les points sont comptes a partir de 0 negatif pour compter depuis la fin*      |
+------------+------------+------------+--------------+------------+--------------+




.. index::
  double: .traitement_geom;forcepoly

forcepoly
.........

   force la geometrie en polygone


**syntaxes acceptees**

+------+------+------+---------+-------+--------+
|sortie|defaut|entree|commande |param1 |param2  |
+======+======+======+=========+=======+========+
|      |      |      |forcepoly|?=force|        |
+------+------+------+---------+-------+--------+




.. index::
  double: .traitement_geom;geom

geom
....

   force l'interpretation de la geometrie


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |geom    |?N    |?=S     |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;geom2D

geom2D
......

   passe la geometrie en 2D


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |geom2D  |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;geom3D

geom3D
......

   passe la geometrie en 2D


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |N     |?A    |geom3D  |?C    |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;grid

grid
....

   decoupage en grille


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|L     |      |      |grid    |LC    |N       |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;gridx

gridx
.....

   decoupage grille en x


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |      |gridx   |N     |N       |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;gridy

gridy
.....

   decoupage grille en x


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |      |gridy   |N     |N       |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;longueur

longueur
........

   calcule la longueur de l'objet


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |      |      |longueur|      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;mod3D

mod3D
.....

   modifie la 3D  en fonction de criteres sur le Z

    valeur de remplacement att/val cond cmp1

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |N     |      |mod3D   |C     |        |
+------+------+------+--------+------+--------+
| * valeur de remplacement att/val cond cmp1* |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_geom;multigeom

multigeom
.........

   definit la geometrie comme multiple ou non


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |N     |      |multigeom|      |        |
+------+------+------+---------+------+--------+




.. index::
  double: .traitement_geom;prolonge

prolonge
........

   prolongation de la ligne d'appui pour les textes

   longueur;[attibut contenant la  longueur];prolonge;code_prolongation

**syntaxes acceptees**

+-----------+-----------+-----------+-------------+-----------+-------------+
|sortie     |defaut     |entree     |commande     |param1     |param2       |
+===========+===========+===========+=============+===========+=============+
|           |?N         |?A         |prolonge     |?N         |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *longueur;[attibut contenant la  longueur];prolonge;code_prolongation*    |
+-----------+-----------+-----------+-------------+-----------+-------------+




.. index::
  double: .traitement_geom;reproj

reproj
......

   reprojette la geometrie

   attribut pour la grille utilisee;systeme d'entree;reproj;systeme de sortie;
   [grilles personnalisées] NG: pas de grilles cus

**syntaxes acceptees**

+------------+------------+------------+--------------+------------+--------------+
|sortie      |defaut      |entree      |commande      |param1      |param2        |
+============+============+============+==============+============+==============+
|?A          |C           |            |reproj        |C           |?C            |
+------------+------------+------------+--------------+------------+--------------+
| *attribut pour la grille utilisee;systeme d'entree;reproj;systeme de sortie;*   |
| *[grilles personnalisées] NG: pas de grilles cus*                               |
+------------+------------+------------+--------------+------------+--------------+




.. index::
  double: .traitement_geom;resetgeom

resetgeom
.........

   annulle l'interpretation de la geometrie


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |      |      |resetgeom|      |        |
+------+------+------+---------+------+--------+




.. index::
  double: .traitement_geom;setpoint

setpoint
........

   ajoute une geometrie point a partir des coordonnes en attribut


**syntaxes acceptees**

+----------+----------+----------+------------+----------+------------+
|sortie    |defaut    |entree    |commande    |param1    |param2      |
+==========+==========+==========+============+==========+============+
|          |LC        |?A        |setpoint    |?N        |            |
+----------+----------+----------+------------+----------+------------+
|          |N?        |L         |setpoint    |?N        |            |
+----------+----------+----------+------------+----------+------------+
| *defauts, liste d' attribut (x,y,z) contenant les coordonnees*      |
+----------+----------+----------+------------+----------+------------+


   LC :  defauts
   ?A :  attribut contenant les coordonnees separees par des , (optionnel)
   setpoint :  numero de srid



.. index::
  double: .traitement_geom;split_couleur

split_couleur
.............

   decoupe la geometrie selon la couleur

     une liste de couleurs ou par couleur si aucune couleur n'est precisee

**syntaxes acceptees**

+-----------+-----------+-----------+------------------+-----------+-------------+
|sortie     |defaut     |entree     |commande          |param1     |param2       |
+===========+===========+===========+==================+===========+=============+
|A          |           |           |split_couleur     |?LC        |             |
+-----------+-----------+-----------+------------------+-----------+-------------+
| *  une liste de couleurs ou par couleur si aucune couleur n'est precisee*      |
+-----------+-----------+-----------+------------------+-----------+-------------+




.. index::
  double: .traitement_geom;splitgeom

splitgeom
.........

   decoupage inconditionnel des lignes en points


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|?A    |      |      |splitgeom|      |        |
+------+------+------+---------+------+--------+




.. index::
  double: .traitement_geom;translate

translate
.........

   translate un objet

   translation d un objet par une liste de coordonnees (dans un attribut)

**syntaxes acceptees**

+-----------+-----------+-----------+--------------+-----------+-------------+
|sortie     |defaut     |entree     |commande      |param1     |param2       |
+===========+===========+===========+==============+===========+=============+
|           |?LN        |?A         |translate     |           |             |
+-----------+-----------+-----------+--------------+-----------+-------------+
| *translation d un objet par une liste de coordonnees (dans un attribut)*   |
+-----------+-----------+-----------+--------------+-----------+-------------+
|           |?LN        |L          |translate     |           |             |
+-----------+-----------+-----------+--------------+-----------+-------------+
| *translation d un objet par une liste de coordonnees(liste d attributs)*   |
+-----------+-----------+-----------+--------------+-----------+-------------+



hstore
------

hstore

.. index::
  double: .traitement_hstore;hdel

hdel
....

   supprime une valeur d un hstore


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |A     |hdel    |L     |?       |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_hstore;hget

hget
....

   eclatement d un hstore

   destination;defaut;hstore;hget;clef;

**syntaxes acceptees**

+-------+-------+-------+---------+-------+---------+
|sortie |defaut |entree |commande |param1 |param2   |
+=======+=======+=======+=========+=======+=========+
|S      |?      |A      |hget     |A      |         |
+-------+-------+-------+---------+-------+---------+
| *destination;defaut;hstore;hget;clef;*            |
+-------+-------+-------+---------+-------+---------+
|M      |?      |A      |hget     |L      |         |
+-------+-------+-------+---------+-------+---------+
| *destination;defaut;hstore;hget;liste clefs;*     |
+-------+-------+-------+---------+-------+---------+
|D      |?      |A      |hget     |?L     |         |
+-------+-------+-------+---------+-------+---------+
| *destination;defaut;clef;hget;hstore;*            |
+-------+-------+-------+---------+-------+---------+




.. index::
  double: .traitement_hstore;hset

hset
....

   transforme des attributs en hstore

   liste d attributs en entree

**syntaxes acceptees**

+---------+---------+---------+-----------+---------+-----------+
|sortie   |defaut   |entree   |commande   |param1   |param2     |
+=========+=========+=========+===========+=========+===========+
|A        |?        |L        |hset       |         |           |
+---------+---------+---------+-----------+---------+-----------+
| *liste d attributs en entree*                                 |
+---------+---------+---------+-----------+---------+-----------+
|A        |?        |re       |hset       |         |           |
+---------+---------+---------+-----------+---------+-----------+
| *expression reguliere*                                        |
+---------+---------+---------+-----------+---------+-----------+
|A        |         |         |hset       |         |           |
+---------+---------+---------+-----------+---------+-----------+
| *tous les attributs visibles*                                 |
+---------+---------+---------+-----------+---------+-----------+
|A        |         |         |hset       |=lower   |           |
+---------+---------+---------+-----------+---------+-----------+
| *tous les attributs visibles passe les noma en minuscule*     |
+---------+---------+---------+-----------+---------+-----------+
|A        |         |         |hset       |=upper   |           |
+---------+---------+---------+-----------+---------+-----------+
| *tous les attributs visibles passe les noma en majuscule*     |
+---------+---------+---------+-----------+---------+-----------+




.. index::
  double: .traitement_hstore;hsplit

hsplit
......

   decoupage d'un attribut hstore


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|M     |?     |A     |hsplit  |?L    |        |
+------+------+------+--------+------+--------+


   M :  


las
---

las

.. index::
  double: .traitement_las;lasfilter

lasfilter
.........

   decoupage d'un attribut xml en objets

   s'il n'y a pas d'attributs de sortie on cree un objet pour chaque element

**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|A     |?     |?A    |lasfilter|C     |?=D     |
+------+------+------+---------+------+--------+


   A :  repertoire de sortie
   ? :  defaut (optionnel)
   ?A :  attribut (optionnel)
   lasfilter :  
   C :  json de traitement
   ?=D :  D: dynamique (optionnel)



.. index::
  double: .traitement_las;lasreader

lasreader
.........

   defineit les fichiers las en entree


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|C     |?     |A     |lasreader|C     |?=D     |
+------+------+------+---------+------+--------+



mapping
-------

mapping

.. index::
  double: .traitement_mapping;map

map
...

   mapping en fonction d'un fichier

   parametres: map; nom du fichier de mapping

**syntaxes acceptees**

+---------+------+------+--------+--------+--------+
|sortie   |defaut|entree|commande|param1  |param2  |
+=========+======+======+========+========+========+
|?=#schema|?C    |      |map     |C       |        |
+---------+------+------+--------+--------+--------+
| *parametres: map; nom du fichier de mapping*     |
+---------+------+------+--------+--------+--------+
|         |      |      |map     |=#struct|        |
+---------+------+------+--------+--------+--------+




.. index::
  double: .traitement_mapping;map_data

map_data
........

   applique un mapping complexe aux donnees

   C: fichier de mapping

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?C    |A     |map_data|C     |        |
+------+------+------+--------+------+--------+
| *C: fichier de mapping*                     |
+------+------+------+--------+------+--------+
|L     |?C    |L     |map_data|C     |        |
+------+------+------+--------+------+--------+
| *C: fichier de mapping*                     |
+------+------+------+--------+------+--------+
|*     |?C    |T:    |map_data|C     |        |
+------+------+------+--------+------+--------+
| *T: definition de type de donnees (T:)*     |
+------+------+------+--------+------+--------+



os
--

os

.. index::
  double: .traitement_os;abspath

abspath
.......

   change un chemin relatif en chemin absolu

   le point de depart est le chemin ou cmp1

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |C?    |A?    |abspath |C?    |        |
+------+------+------+--------+------+--------+
| *le point de depart est le chemin ou cmp1*  |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_os;adquery

adquery
.......

   extait des information de active_directory


**syntaxes acceptees**

+------+------+------+--------+--------+--------+
|sortie|defaut|entree|commande|param1  |param2  |
+======+======+======+========+========+========+
|S     |?C    |?A    |adquery |=user   |?C      |
+------+------+------+--------+--------+--------+
|S     |?C    |?A    |adquery |=machine|?C      |
+------+------+------+--------+--------+--------+
|S     |?C    |?A    |adquery |=groupe |?C      |
+------+------+------+--------+--------+--------+




.. index::
  double: .traitement_os;infofich

infofich
........

   ajoute les informations du fichier sur les objets

   usage prefix;defaut;attribut;infofich;;;
   prefixe par defaut:#, si pas d'entree s'applique au fichier courant
   cree les attributs: #chemin, #nom, #ext,
   #domaine, #proprietaire, #creation, #modif, #acces

**syntaxes acceptees**

+-----------+-----------+-----------+-------------+-----------+-------------+
|sortie     |defaut     |entree     |commande     |param1     |param2       |
+===========+===========+===========+=============+===========+=============+
|?A         |?C         |?A         |infofich     |           |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *usage prefix;defaut;attribut;infofich;;;*                                |
| *prefixe par defaut:#, si pas d'entree s'applique au fichier courant*     |
| *cree les attributs: #chemin, #nom, #ext,*                                |
| *#domaine, #proprietaire, #creation, #modif, #acces*                      |
+-----------+-----------+-----------+-------------+-----------+-------------+




.. index::
  double: .traitement_os;listefich

listefich
.........

   genere un objet par fichier repondant aux criteres d'entree


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|S     |?C    |A     |listefich|?C    |?C      |
+------+------+------+---------+------+--------+
|S     |?C    |      |listefich|?C    |?C      |
+------+------+------+---------+------+--------+


   S :  attribut de sortie
   ?C :  defaut (optionnel)
   A :  selecteur de fichiers
   listefich :  
   ?C :  repertoire (optionnel)
   ?C :  extension (optionnel)

dirselect:selecteur de repertoires
filtre_entree:filtrage noms par expression reguliere


.. index::
  double: .traitement_os;namejoin

namejoin
........

   combine des element en nom de fichier en chemin,nom,extention


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |C?    |L?    |namejoin|      |        |
+------+------+------+--------+------+--------+


   S :  sortie
   C? :  defaut (optionnel)
   L? :  liste d'attributs (optionnel)
   namejoin :  namesjoin



.. index::
  double: .traitement_os;namesplit

namesplit
.........

   decoupe un nom de fichier en chemin,nom,extention

   genere les attributs prefix_chemin,prefix_nom,prefix_ext avec un prefixe

**syntaxes acceptees**

+-----------+-----------+-----------+--------------+-----------+-------------+
|sortie     |defaut     |entree     |commande      |param1     |param2       |
+===========+===========+===========+==============+===========+=============+
|?A         |C?         |A?         |namesplit     |           |             |
+-----------+-----------+-----------+--------------+-----------+-------------+
| *genere les attributs prefix_chemin,prefix_nom,prefix_ext avec un prefixe* |
+-----------+-----------+-----------+--------------+-----------+-------------+


   ?A :  prefixe (optionnel)
   C? :  defaut (optionnel)
   A? :  attr contenant le nom (optionnel)
   namesplit :  namesplit



.. index::
  double: .traitement_os;os_copy

os_copy
.......

   copie un fichier

   attribut qui recupere le resultat, parametres , run , nom, parametres

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |os_copy |C     |C       |
+------+------+------+--------+------+--------+
| *execution unique au demarrage*             |
+------+------+------+--------+------+--------+
|A     |?C    |A     |os_copy |?C    |?C      |
+------+------+------+--------+------+--------+
| *execution pour chaque objet*               |
+------+------+------+--------+------+--------+


   os_copy :  nom destination
   C :  nom d origine

   A :  nom destination,nom d origine
   ?C :  chemin destination (optionnel)
   A :  chemin origine



.. index::
  double: .traitement_os;os_del

os_del
......

   supprime un fichier

   suppression d'un fichier

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |os_del  |C     |        |
+------+------+------+--------+------+--------+
| *execution unique au demarrage*             |
+------+------+------+--------+------+--------+
|      |?C    |A     |os_del  |?C    |        |
+------+------+------+--------+------+--------+
| *execution pour chaque objet*               |
+------+------+------+--------+------+--------+


   os_del :  
   C :  nom du fichier a supprimer

   ?C :  defaut (optionnel)
   A :  nom du fichier a supprimer
   os_del :  
   ?C :  chemin (optionnel)



.. index::
  double: .traitement_os;os_move

os_move
.......

   deplace un fichier

   attribut qui recupere le resultat, parametres , run , nom, parametres

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |os_move |C     |C       |
+------+------+------+--------+------+--------+
| *execution unique au demarrage*             |
+------+------+------+--------+------+--------+
|A     |?C    |A     |os_move |?C    |?C      |
+------+------+------+--------+------+--------+
| *execution pour chaque objet*               |
+------+------+------+--------+------+--------+


   os_move :  nom destination
   C :  nom d origine

   A :  nom destination,defaut,nom d origine
   ?C :  chemin destination (optionnel)
   A :  chemin origine



.. index::
  double: .traitement_os;os_ren

os_ren
......

   renomme un fichier


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |os_ren  |C     |C       |
+------+------+------+--------+------+--------+
| *execution unique au demarrage*             |
+------+------+------+--------+------+--------+
|A     |?C    |A     |os_ren  |?C    |?C      |
+------+------+------+--------+------+--------+
| *execution pour chaque objet*               |
+------+------+------+--------+------+--------+


   os_ren :  nom destination
   C :  nom d origine

   A :  nom destination,nom d origine
   ?C :  chemin destination (optionnel)
   A :  chemin origine



.. index::
  double: .traitement_os;run

run
...

   execute une commande externe


**syntaxes acceptees**

+--------------------+--------------------+--------------------+----------------------+--------------------+----------------------+
|sortie              |defaut              |entree              |commande              |param1              |param2                |
+====================+====================+====================+======================+====================+======================+
|?A                  |?C                  |?A                  |run                   |C                   |                      |
+--------------------+--------------------+--------------------+----------------------+--------------------+----------------------+
| *execution a chaque objet avec recuperation d'un resultat (l'attribut d'entree ou la valeur par defaut doivent etre remplis)*   |
+--------------------+--------------------+--------------------+----------------------+--------------------+----------------------+
|?P                  |=^                  |                    |run                   |C                   |                      |
+--------------------+--------------------+--------------------+----------------------+--------------------+----------------------+
|?P                  |                    |                    |run                   |C                   |C                     |
+--------------------+--------------------+--------------------+----------------------+--------------------+----------------------+
| *execution en debut de process avec sans recuperation eventuelle d'un resultat dans une variable*                               |
+--------------------+--------------------+--------------------+----------------------+--------------------+----------------------+


   ?A :  attribut qui recupere le resultat (optionnel)
   ?C :  parametres par defaut (optionnel)
   ?A :  attribut contenant les parametres (optionnel)
   run :  commande,parametres

process:conditions d'execution (all: toujours execute, main: process de base child: chaque sous process
		 en mode parallele: worker: pour chaque process esclave , master: uniquement process maitre)

manipulation de schemas
-----------------------

manipulation de schemas

.. index::
  double: .traitement_schema;compare_schema

compare_schema
..............

   compare un nouveau schema en sortant les differences


**syntaxes acceptees**

+------+------+------+--------------+------+--------+
|sortie|defaut|entree|commande      |param1|param2  |
+======+======+======+==============+======+========+
|      |?C    |      |compare_schema|C     |?N      |
+------+------+------+--------------+------+--------+
|C     |C     |      |compare_schema|      |        |
+------+------+------+--------------+------+--------+




.. index::
  double: .traitement_schema;force_alias

force_alias
...........

   remplace les valeurs par les alias


**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|      |      |      |force_alias|?C    |        |
+------+------+------+-----------+------+--------+




.. index::
  double: .traitement_schema;info_schema

info_schema
...........

   recupere des infos du schema de l'objet


**syntaxes acceptees**

+------+---------+------+-----------+------+--------+
|sortie|defaut   |entree|commande   |param1|param2  |
+======+=========+======+===========+======+========+
|A     |C        |      |info_schema|?C    |?C      |
+------+---------+------+-----------+------+--------+
|A     |=attribut|C     |info_schema|?C    |?C      |
+------+---------+------+-----------+------+--------+


   A :  attribut qui recupere le resultat
   C :  parametre a recuperer
   info_schema :  nom de l'attribut
   ?C :  commande,schema,classe (optionnel)



.. index::
  double: .traitement_schema;lire_schema

lire_schema
...........

   associe un schema lu dans un ficher a un objet

   type du schema (entree, sortie ou autre);nom;;lire_schema;nom du fichier;extension

**syntaxes acceptees**

+---------------+------+------+-----------+------+--------+
|sortie         |defaut|entree|commande   |param1|param2  |
+===============+======+======+===========+======+========+
|?=schema_entree|?C    |?=map |lire_schema|?C    |?C      |
+---------------+------+------+-----------+------+--------+
|?=schema_sortie|?C    |?=map |lire_schema|?C    |?C      |
+---------------+------+------+-----------+------+--------+
|?=#schema      |?C    |?=map |lire_schema|?C    |?C      |
+---------------+------+------+-----------+------+--------+




.. index::
  double: .traitement_schema;liste_tables

liste_tables
............

   recupere la liste des tables d un schema a la fin du traitement


**syntaxes acceptees**

+------+------+------+------------+------+--------+
|sortie|defaut|entree|commande    |param1|param2  |
+======+======+======+============+======+========+
|      |      |      |liste_tables|C     |?=reel  |
+------+------+------+------------+------+--------+




.. index::
  double: .traitement_schema;map_schema

map_schema
..........

   effectue des modifications sur un schema en gerant les correspondances


**syntaxes acceptees**

+--------+------+------+----------+------+--------+
|sortie  |defaut|entree|commande  |param1|param2  |
+========+======+======+==========+======+========+
|=#schema|C     |      |map_schema|C     |        |
+--------+------+------+----------+------+--------+




.. index::
  double: .traitement_schema;match_schema

match_schema
............

   associe un schema en faisant un mapping au mieux


**syntaxes acceptees**

+------+------+------+------------+------+--------+
|sortie|defaut|entree|commande    |param1|param2  |
+======+======+======+============+======+========+
|      |?C    |      |match_schema|C     |?N      |
+------+------+------+------------+------+--------+




.. index::
  double: .traitement_schema;ordre

ordre
.....

   ordonne les champs dans un schema


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|L     |      |      |ordre   |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_schema;sc_add_attr

sc_add_attr
...........

   ajoute un attribut a un schema sans toucher aux objets


**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|A     |      |      |sc_add_attr|C?    |L?      |
+------+------+------+-----------+------+--------+




.. index::
  double: .traitement_schema;sc_supp_attr

sc_supp_attr
............

   supprime un attribut d un schema sans toucher aux objets


**syntaxes acceptees**

+------+------+------+------------+------+--------+
|sortie|defaut|entree|commande    |param1|param2  |
+======+======+======+============+======+========+
|A     |      |      |sc_supp_attr|C?    |L?      |
+------+------+------+------------+------+--------+




.. index::
  double: .traitement_schema;schema

schema
......

   cree un schema par analyse des objets et l'associe a un objet


**syntaxes acceptees**

+---------+------+------+--------+------+--------+
|sortie   |defaut|entree|commande|param1|param2  |
+=========+======+======+========+======+========+
|=#schema?|      |      |schema  |C?    |?N      |
+---------+------+------+--------+------+--------+




.. index::
  double: .traitement_schema;set_schema

set_schema
..........

   positionne des parametres de schema (statique)

   parametres positionnables:
    pk : nom de la clef primaire
    alias : commentaire de la table
    dimension : dimension geometrique
    no_multiple : transforme les attributs multiples en simple

**syntaxes acceptees**

+---------+---------+---------+-------------+---------+-----------+
|sortie   |defaut   |entree   |commande     |param1   |param2     |
+=========+=========+=========+=============+=========+===========+
|C        |?C       |         |set_schema   |         |           |
+---------+---------+---------+-------------+---------+-----------+
| *parametres positionnables:*                                    |
| * pk : nom de la clef primaire*                                 |
| * alias : commentaire de la table*                              |
| * dimension : dimension geometrique*                            |
| * no_multiple : transforme les attributs multiples en simple*   |
+---------+---------+---------+-------------+---------+-----------+
|C        |?C       |A        |set_schema   |         |           |
+---------+---------+---------+-------------+---------+-----------+


   C :  nom du parametre a positionner
   ?C :  valeur (optionnel)



.. index::
  double: .traitement_schema;valide_schema

valide_schema
.............

   verifie si des objets sont compatibles avec un schema


**syntaxes acceptees**

+---------+------+------+-------------+----------+--------+
|sortie   |defaut|entree|commande     |param1    |param2  |
+=========+======+======+=============+==========+========+
|?=#schema|?C    |      |valide_schema|?=strict  |        |
+---------+------+------+-------------+----------+--------+
|?=#schema|?C    |      |valide_schema|=supp_conf|        |
+---------+------+------+-------------+----------+--------+


log_level;err ou warn par defaut no;

shapely
-------

shapely

.. index::
  double: .traitement_shapely;angle

angle
.....

   calcule un angle de reference de l'objet

   N:N indices des point a utiliser, P creation d'un point au centre

**syntaxes acceptees**

+----------+----------+----------+------------+----------+------------+
|sortie    |defaut    |entree    |commande    |param1    |param2      |
+==========+==========+==========+============+==========+============+
|S         |          |          |angle       |?N:N      |?=P         |
+----------+----------+----------+------------+----------+------------+
| *N:N indices des point a utiliser, P creation d'un point au centre* |
+----------+----------+----------+------------+----------+------------+




.. index::
  double: .traitement_shapely;buffer

buffer
......

   calcul d'un buffer


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |?N    |?A    |buffer  |?C    |        |
+------+------+------+--------+------+--------+


   ?A :  largeur buffer (optionnel)
   ?N :  attribut contenant la largeur (optionnel)
   ?A :  buffer (optionnel)

resolution:16,cap_style:1,join_style:1,mitre_limit:5


.. index::
  double: .traitement_shapely;geoselect

geoselect
.........

   intersection geometrique par reapport a une couche stockee


**syntaxes acceptees**

+-----------+-----------+-----------+--------------+-----------+-------------+
|sortie     |defaut     |entree     |commande      |param1     |param2       |
+===========+===========+===========+==============+===========+=============+
|?L         |?LC        |?L         |geoselect     |=in        |C            |
+-----------+-----------+-----------+--------------+-----------+-------------+
| *l 'objet contenu recupere une liste d attributs de l objet contenant*     |
+-----------+-----------+-----------+--------------+-----------+-------------+


   ?L :  attributs recuperes (optionnel)
   ?LC :  valeurs recuperees (optionnel)
   ?L :  attributs contenant (optionnel)
   geoselect :  
   =in :  
   C :  nom memoire



.. index::
  double: .traitement_shapely;r_min

r_min
.....

   calcul du rectangle oriente minimal


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |r_min   |      |        |
+------+------+------+--------+------+--------+



web
---

web

.. index::
  double: .traitement_web;download

download
........

 
 
 

   ; url; (attribut contenant le url);http_download;racine;nom

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |?C    |?A    |download|?C    |?C      |
+------+------+------+--------+------+--------+
|A     |?C    |?A    |download|      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_web;ftp_download

ftp_download
............

   charge un fichier sur ftp

   ;nom fichier; (attribut contenant le nom);ftp_download;ident ftp;repertoire

**syntaxes acceptees**

+------+------+------+------------+------+--------+
|sortie|defaut|entree|commande    |param1|param2  |
+======+======+======+============+======+========+
|      |?C    |?A    |ftp_download|C     |?C      |
+------+------+------+------------+------+--------+
|      |?C    |?A    |ftp_download|      |        |
+------+------+------+------------+------+--------+
|A     |?C    |?A    |ftp_download|      |        |
+------+------+------+------------+------+--------+
|A     |?C    |?A    |ftp_download|C     |?C      |
+------+------+------+------------+------+--------+




.. index::
  double: .traitement_web;ftp_upload

ftp_upload
..........

   charge un fichier sur ftp

   ;nom fichier; (attribut contenant le nom);ftp_upload;ident ftp;chemin ftp

**syntaxes acceptees**

+------+------+------+----------+------+--------+
|sortie|defaut|entree|commande  |param1|param2  |
+======+======+======+==========+======+========+
|      |?C    |?A    |ftp_upload|?C    |?C      |
+------+------+------+----------+------+--------+
|      |=#att |A     |ftp_upload|?C    |C       |
+------+------+------+----------+------+--------+




.. index::
  double: .traitement_web;geocode

geocode
.......

   geocode des objets en les envoyant au gecocodeur addict

   en entree clef et liste des champs adresse a geocoder score min pour un succes

**syntaxes acceptees**

+-------------+-------------+-------------+---------------+-------------+---------------+
|sortie       |defaut       |entree       |commande       |param1       |param2         |
+=============+=============+=============+===============+=============+===============+
|             |             |L            |geocode        |?C           |?LC            |
+-------------+-------------+-------------+---------------+-------------+---------------+
| *en entree clef et liste des champs adresse a geocoder score min pour un succes*      |
+-------------+-------------+-------------+---------------+-------------+---------------+


   L :  liste attributs adresse
   geocode :  
   ?C :  confiance mini (optionnel)
   ?LC :  liste filtres (optionnel)



.. index::
  double: .traitement_web;wfsload

wfsload
.......

 
 
 

   ; classe;  attribut contenant la classe;wfs;url;format

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|F     |?C    |?A    |wfsload |C     |?C      |
+------+------+------+--------+------+--------+
|A     |?C    |?A    |wfsload |C     |?C      |
+------+------+------+--------+------+--------+



workflow
--------

workflow

.. index::
  double: .traitement_workflow;abort

abort
.....

   arrete le traitement

   arrete l operation en cours et renvoie un message
   
   niveaux d arret
   
   * 1 arret du traitement de l'objet (defaut)
   * 2 arret du traitment de la classe
   * 3 arret du traitement pour le module
   * 4 sortie en catastrophe du programme

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |abort   |?N    |?C      |
+------+------+------+--------+------+--------+


   abort :  
   ?N :  niveau (optionnel)
   ?C :  message (optionnel)



.. index::
  double: .traitement_workflow;archive

archive
.......

   zippe les fichiers ou les repertoires de sortie

    parametres:liste de noms de fichiers(avec \*...);attribut contenant le nom;archive;nom

**syntaxes acceptees**

+--------------+--------------+--------------+----------------+--------------+----------------+
|sortie        |defaut        |entree        |commande        |param1        |param2          |
+==============+==============+==============+================+==============+================+
|              |?C            |?A            |archive         |C             |                |
+--------------+--------------+--------------+----------------+--------------+----------------+
| * parametres:liste de noms de fichiers(avec *...);attribut contenant le nom;archive;nom*    |
+--------------+--------------+--------------+----------------+--------------+----------------+




.. index::
  double: .traitement_workflow;attreader

attreader
.........

   traite un attribut d'un objet comme une source de donnees

   par defaut attreader supprime le contenu de l attribut source

**syntaxes acceptees**

+----------+----------+----------+-------------+----------+------------+
|sortie    |defaut    |entree    |commande     |param1    |param2      |
+==========+==========+==========+=============+==========+============+
|          |?C        |A         |attreader    |C         |?C          |
+----------+----------+----------+-------------+----------+------------+
| *par defaut attreader supprime le contenu de l attribut source*      |
+----------+----------+----------+-------------+----------+------------+




.. index::
  double: .traitement_workflow;attwriter

attwriter
.........

   traite un attribut d'un objet comme une sortie cree un objet pas fanout

   par defaut attreader supprime le contenu de l attribut source

**syntaxes acceptees**

+----------+----------+----------+-------------+----------+------------+
|sortie    |defaut    |entree    |commande     |param1    |param2      |
+==========+==========+==========+=============+==========+============+
|A         |          |          |attwriter    |C         |?C          |
+----------+----------+----------+-------------+----------+------------+
| *par defaut attreader supprime le contenu de l attribut source*      |
+----------+----------+----------+-------------+----------+------------+




.. index::
  double: .traitement_workflow;batch

batch
.....

   execute un traitement batch a partir des parametres de l'objet
   s'il n y a pas de commandes en parametres elle sont prises dans l objet
   les attribut utilise sont: commandes,entree,sortie et parametres


**syntaxes acceptees**

+--------+--------+--------+----------+----------------+----------+
|sortie  |defaut  |entree  |commande  |param1          |param2    |
+========+========+========+==========+================+==========+
|A       |?C      |?A      |batch     |?=run           |          |
+--------+--------+--------+----------+----------------+----------+
| *execute pour chaque objet, demarre toujours, meme sans objets* |
+--------+--------+--------+----------+----------------+----------+
|A       |?C      |?A      |batch     |=init           |          |
+--------+--------+--------+----------+----------------+----------+
| *demarre a l'initialisation du script maitre*                   |
+--------+--------+--------+----------+----------------+----------+
|A       |?C      |?A      |batch     |=parallel_init  |          |
+--------+--------+--------+----------+----------------+----------+
| *demarre a l'initialisation de chaque process parallele*        |
+--------+--------+--------+----------+----------------+----------+
|A       |?C      |?A      |batch     |=boucle         |C         |
+--------+--------+--------+----------+----------------+----------+
| *reprend le jeu de donnees en boucle*                           |
+--------+--------+--------+----------+----------------+----------+
|A       |?C      |?A      |batch     |=load           |C         |
+--------+--------+--------+----------+----------------+----------+
| *passe une fois le jeu de donnees*                              |
+--------+--------+--------+----------+----------------+----------+


   A :  attribut_resultat
   ?C :  commandes (optionnel)
   ?A :  attribut_commandes (optionnel)
   batch :  batch
   ?=run :  mode_batch (optionnel)



.. index::
  double: .traitement_workflow;bloc

bloc
....

   definit un bloc d'instructions qui reagit comme une seule et genere un contexte


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |bloc    |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;boucle

boucle
......

   execute un traitement batch en boucle a partir des parametres de l'objet


**syntaxes acceptees**

+--------+--------+--------+----------+--------+----------+
|sortie  |defaut  |entree  |commande  |param1  |param2    |
+========+========+========+==========+========+==========+
|A       |?C      |?A      |boucle    |C       |?C        |
+--------+--------+--------+----------+--------+----------+
| * en mode run le traitement s'autodeclenche sans objet* |
+--------+--------+--------+----------+--------+----------+


   A :  
   ?C :  attribut_resultat (optionnel)
   ?A :  commandes (optionnel)
   boucle :  attribut_commandes
   C :  batch
   ?C :  mode_batch (optionnel)



.. index::
  double: .traitement_workflow;call

call
....

   appel de macro avec gestion de variables locales


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |call    |C     |?LC     |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;charge

charge
......

   chargement d objets en fichier

   cette fonction est l' équivalent du chargement initial

**syntaxes acceptees**

+---------+---------+---------+-----------+---------+-----------+
|sortie   |defaut   |entree   |commande   |param1   |param2     |
+=========+=========+=========+===========+=========+===========+
|?A       |?C       |?A       |charge     |?C       |?N         |
+---------+---------+---------+-----------+---------+-----------+
| *cette fonction est l' équivalent du chargement initial*      |
+---------+---------+---------+-----------+---------+-----------+
|?A       |?C       |?A       |charge     |[A]      |?N         |
+---------+---------+---------+-----------+---------+-----------+




.. index::
  double: .traitement_workflow;creobj

creobj
......

   cree des objets de test pour les tests fonctionnels

   parametres:liste d'attributs,liste valeurs,nom(niv,classe),nombre

**syntaxes acceptees**

+----------+----------+----------+------------+----------+------------+
|sortie    |defaut    |entree    |commande    |param1    |param2      |
+==========+==========+==========+============+==========+============+
|L         |LC        |?L        |creobj      |C         |?N          |
+----------+----------+----------+------------+----------+------------+
| *parametres:liste d'attributs,liste valeurs,nom(niv,classe),nombre* |
+----------+----------+----------+------------+----------+------------+
|L         |LC        |          |creobj      |C         |?N          |
+----------+----------+----------+------------+----------+------------+




.. index::
  double: .traitement_workflow;end

end
...

   finit un traitement sans stats ni ecritures


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |end     |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;fail

fail
....

   ne fait rien mais plante. permet un branchement distant


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |fail    |?C    |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;filter

filter
......

   filtre en fonction d un attribut

   sortie;defaut;attribut;filter;liste sorties;liste valeurs

**syntaxes acceptees**

+---------+---------+---------+-----------+---------+-----------+
|sortie   |defaut   |entree   |commande   |param1   |param2     |
+=========+=========+=========+===========+=========+===========+
|?S       |?C       |A        |filter     |LC       |?LC        |
+---------+---------+---------+-----------+---------+-----------+
| *sortie;defaut;attribut;filter;liste sorties;liste valeurs*   |
+---------+---------+---------+-----------+---------+-----------+




.. index::
  double: .traitement_workflow;fin_bloc

fin_bloc
........

   definit la fin d'un bloc d'instructions


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |fin_bloc|      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;geomprocess

geomprocess
...........

   applique une macro sur une copie de la geometrie et recupere des attributs

   permet d'appliquer des traitements destructifs sur la geometrie sans l'affecter

**syntaxes acceptees**

+------------+------------+------------+-----------------+------------+--------------+
|sortie      |defaut      |entree      |commande         |param1      |param2        |
+============+============+============+=================+============+==============+
|            |            |            |geomprocess      |C           |?LC           |
+------------+------------+------------+-----------------+------------+--------------+
| *permet d'appliquer des traitements destructifs sur la geometrie sans l'affecter*  |
+------------+------------+------------+-----------------+------------+--------------+




.. index::
  double: .traitement_workflow;idle

idle
....

   ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |idle    |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;liste_schema

liste_schema
............

   cree des objets virtuels ou reels a partir des schemas (1 objet par classe)

   liste_schema;nom;?reel

**syntaxes acceptees**

+---------+------+------+------------+------+--------+
|sortie   |defaut|entree|commande    |param1|param2  |
+=========+======+======+============+======+========+
|?=#schema|?C    |?A    |liste_schema|C     |?=reel  |
+---------+------+------+------------+------+--------+
| *liste_schema;nom;?reel*                           |
+---------+------+------+------------+------+--------+




.. index::
  double: .traitement_workflow;next

next
....

   force la sortie next


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |next    |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;pass

pass
....

   ne fait rien et passe. permet un branchement distant


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |pass    |?C    |?C      |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;print

print
.....

   affichage d elements de l objet courant


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |C?    |L?    |print   |C?    |=noms?  |
+------+------+------+--------+------+--------+
|      |      |*     |print   |C?    |=noms?  |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;printv

printv
......

   affichage des parametres nommes


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |printv  |C?    |=noms?  |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;quitter

quitter
.......

   sort d une macro


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |quitter |?C    |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;reel

reel
....

   transforme un objet virtuel en objet reel


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |reel    |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;retour

retour
......

   ramene les elements apres l execution


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |C?    |L?    |retour  |C?    |=noms?  |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;retry

retry
.....

   relance un traitement a intervalle regulier


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |      |retry   |C     |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;sample

sample
......

   recupere un objet sur x


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |?A    |sample  |N     |N:N     |
+------+------+------+--------+------+--------+
|      |      |?A    |sample  |N     |?N      |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;sleep

sleep
.....

   attends;;


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |?C    |?A    |sleep   |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;start

start
.....

   ne fait rien mais envoie un objet virtuel dans le circuit


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |start   |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;statprint

statprint
.........

   affiche les stats a travers une macro eventuelle

   statprint;macro

**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |      |      |statprint|?C    |        |
+------+------+------+---------+------+--------+
| *statprint;macro*                            |
+------+------+------+---------+------+--------+




.. index::
  double: .traitement_workflow;statprocess

statprocess
...........

   retraite les stats en appliquant une macro

   statprocess;macro de traitement;sortie

**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|      |      |      |statprocess|C     |?C      |
+------+------+------+-----------+------+--------+
| *statprocess;macro de traitement;sortie*       |
+------+------+------+-----------+------+--------+




.. index::
  double: .traitement_workflow;sync

sync
....

   finit un traitement en parallele et redonne la main sans stats ni ecritures


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |sync    |?C    |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;testobj

testobj
.......

   cree des objets de test pour les tests fonctionnels

   parametres:liste d'attributs,liste valeurs,nom(niv,classe),nombre

**syntaxes acceptees**

+----------+----------+----------+------------+----------+------------+
|sortie    |defaut    |entree    |commande    |param1    |param2      |
+==========+==========+==========+============+==========+============+
|L         |LC        |          |testobj     |C         |?N          |
+----------+----------+----------+------------+----------+------------+
| *parametres:liste d'attributs,liste valeurs,nom(niv,classe),nombre* |
+----------+----------+----------+------------+----------+------------+




.. index::
  double: .traitement_workflow;version

version
.......

   affiche la version du logiciel et les infos


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |version |?=full|        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;virtuel

virtuel
.......

   transforme un objet reel en objet virtuel


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |virtuel |      |        |
+------+------+------+--------+------+--------+



xml
---

xml

.. index::
  double: .traitement_xml;formated_save

formated_save
.............

   stockage de l objet dans un fichier en utilisant un template jinja2


**syntaxes acceptees**

+------+------+------+-------------+------+--------+
|sortie|defaut|entree|commande     |param1|param2  |
+======+======+======+=============+======+========+
|A     |      |      |formated_save|C     |?C      |
+------+------+------+-------------+------+--------+
|A     |C?    |A     |formated_save|C     |?C      |
+------+------+------+-------------+------+--------+


   A :  nom fichier
   formated_save :  
   C :  nom du template
   ?C :  nom du repertoire de sortie (optionnel)

   A :  nom fichier
   C? :  defaut (optionnel)
   A :  attribut nom du template
   formated_save :  
   C :  nom du repertoire de template
   ?C :  nom du repertoire de sortie (optionnel)



.. index::
  double: .traitement_xml;xml_load

xml_load
........

   lecture d un fichier xml dans un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?     |?A    |xml_load|      |        |
+------+------+------+--------+------+--------+


   A :  attribut de sortie
   ? :  defaut (optionnel)
   ?A :  attribut contenant le nom de fichier (optionnel)
   xml_load :  



.. index::
  double: .traitement_xml;xml_save

xml_save
........

   stockage dans un fichier d un xml contenu dans un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?C    |A     |xml_save|?C    |        |
+------+------+------+--------+------+--------+


   A :  nom fichier
   ?C :   (optionnel)
   A :  attribut contenant le xml
   xml_save :  
   ?C :  nom du repertoire (optionnel)



.. index::
  double: .traitement_xml;xmledit

xmledit
.......

   modification en place d elements xml


**syntaxes acceptees**

+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
|sortie                  |defaut                  |entree                  |commande                  |param1                  |param2                    |
+========================+========================+========================+==========================+========================+==========================+
|re                      |re                      |A                       |xmledit                   |C                       |?C                        |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
| *remplacement de texte*                                                                                                                                 |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
|                        |C                       |A                       |xmledit                   |A.C                     |?C                        |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
| *remplacement ou ajout d un tag*                                                                                                                        |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
|                        |[A]                     |A                       |xmledit                   |A.C                     |?C                        |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
| *remplacement ou ajout d un tags*                                                                                                                       |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
|?=\*                    |H                       |A                       |xmledit                   |C                       |?C                        |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
| *remplacement ou ajout d un en: remplacement total;attribut hstore contenant clefs/valeurs;attribut xml;xmledit;tag a modifier;groupe de recherche*     |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
|                        |                        |A                       |xmledit                   |A.C                     |?C                        |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+
| *suppression d un ensemble de tags*                                                                                                                     |
+------------------------+------------------------+------------------------+--------------------------+------------------------+--------------------------+


   re :  expression de sortie
   re :  selection
   A :  attribut xml
   xmledit :  xmledit
   C :  tag a modifier
   ?C :  groupe de recherche (optionnel)

   C :  
   A :  valeur
   xmledit :  attribut xml
   A.C :  xmledit
   ?C :  tag a modifier.parametre (optionnel)

   [A] :  
   A :  attribut contenant la valeur
   xmledit :  attribut xml
   A.C :  xmledit
   ?C :  tag a modifier.parametre (optionnel)

   A :  
   xmledit :  liste de clefs a supprimer
   A.C :  attribut xml
   ?C :  xmledit (optionnel)



.. index::
  double: .traitement_xml;xmlextract

xmlextract
..........

   extraction de valeurs d un xml

   retourne le premier element trouve

**syntaxes acceptees**

+------+------+------+----------+------+--------+
|sortie|defaut|entree|commande  |param1|param2  |
+======+======+======+==========+======+========+
|H     |?C    |A     |xmlextract|C     |?C      |
+------+------+------+----------+------+--------+
|D     |?C    |A     |xmlextract|C     |?C      |
+------+------+------+----------+------+--------+
|S     |?C    |A     |xmlextract|A.C   |?C      |
+------+------+------+----------+------+--------+


   H :  attribut sortie(hstore)
   ?C :  defaut (optionnel)
   A :  attribut xml
   xmlextract :  
   C :  tag a extraire
   ?C :  groupe de recherche (optionnel)



.. index::
  double: .traitement_xml;xmlsplit

xmlsplit
........

   decoupage d'un attribut xml en objets

   on cree un objet pour chaque element

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |      |A     |xmlsplit|C     |?C      |
+------+------+------+--------+------+--------+
|H     |      |A     |xmlsplit|C     |?C      |
+------+------+------+--------+------+--------+
|D     |      |A     |xmlsplit|C     |?C      |
+------+------+------+--------+------+--------+
|M     |      |A     |xmlsplit|C     |?C      |
+------+------+------+--------+------+--------+
|S     |      |A     |xmlsplit|A.C   |?C      |
+------+------+------+--------+------+--------+


   S :  attribut sortie(hstore)
   A :  defaut
   xmlsplit :  attribut xml
   C :  
   ?C :  tag a extraire (optionnel)



.. index::
  double: .traitement_xml;xmlstruct

xmlstruct
.........

   affiche la structure de tags d un xml


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |?C    |A     |xmlstruct|?C    |?C      |
+------+------+------+---------+------+--------+


   ?C :   (optionnel)
   A :  defaut
   xmlstruct :  attribut xml
   ?C :   (optionnel)
   ?C :  tag a extraire (optionnel)

