reference des commandes
=======================

ad
--

ad

.. index::
  double: .traitement_ad;adquery

adquery
.......

   extait des information de active_directory


**syntaxes acceptees**

+------+------+------+--------+--------+--------+
|sortie|defaut|entree|commande|param1  |param2  |
+======+======+======+========+========+========+
|M     |?C    |?A    |adquery |=user   |?C      |
+------+------+------+--------+--------+--------+
|M     |?C    |?A    |adquery |=machine|?C      |
+------+------+------+--------+--------+--------+
|M     |?C    |?A    |adquery |=groupe |?C      |
+------+------+------+--------+--------+--------+
|P     |C     |      |adquery |=user   |        |
+------+------+------+--------+--------+--------+
|      |?C    |?A    |adquery |C       |?C      |
+------+------+------+--------+--------+--------+



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





.. index::
  double: .traitement_alpha;extractbloc

extractbloc
...........

   extrait des blocs d un attribut texte

   chaque bloc est identifie par une clef (regex avec un groupe de capture)
   et une paire de caracteres debut/fin ex <> ou () {}...

**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|A     |?C    |?A    |extractbloc|re    |C       |
+------+------+------+-----------+------+--------+
|      |?C    |?A    |extractbloc|re    |C       |
+------+------+------+-----------+------+--------+




.. index::
  double: .traitement_alpha;format

format
......

   formatte un attribut utilise les formatages python standard

   en cas de conflit (motif de type variable %xxx%)
   il est possible de remplacer le % par un autre caractere (par defaut µ)
   si on souhaite des espaces avant ou apres le format il est possible de definir
   la variable espace pour remplacer les espaces
   exemple: °°µs%d°° avec espace=° devient '  %s%d  '

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

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |L     |garder  |      |        |
+------+------+------+--------+------+--------+
|L     |      |      |garder  |      |        |
+------+------+------+--------+------+--------+
|L     |?LC   |L     |garder  |      |        |
+------+------+------+--------+------+--------+





.. index::
  double: .traitement_alpha;infoatt

infoatt
.......

   affiche des infos sur un attribut

   donne recursivement les types d un attribut compexe

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |A     |infoatt |      |        |
+------+------+------+--------+------+--------+




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
|L      |?      |?A     |join     |C[]    |?C       |
+-------+-------+-------+---------+-------+---------+
| *sur un fichier dans le repertoire des donnees*   |
+-------+-------+-------+---------+-------+---------+
|A      |?      |A      |join     |?C     |?C       |
+-------+-------+-------+---------+-------+---------+
| *jointure statique*                               |
+-------+-------+-------+---------+-------+---------+
|M?     |?      |?L     |join     |#C     |?C       |
+-------+-------+-------+---------+-------+---------+




**autres variables utilisees**

debug,


.. index::
  double: .traitement_alpha;json

json
....

   transforme un objet complexe contenu dans un attribut en texte json

   gere les dictionnaires et les iterables imbriques

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |A     |json    |      |        |
+------+------+------+--------+------+--------+




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





.. index::
  double: .traitement_alpha;set

set
...

   remplacement d une valeur

   fonction de calcul libre (attention injection de code)
    les attributs doivent etre précédes de N: pour un traitement numerique
    ou C: pour un traitement alpha

**syntaxes acceptees**

+----------------+--------------+--------------+----------------+--------------+----------------+
|sortie          |defaut        |entree        |commande        |param1        |param2          |
+================+==============+==============+================+==============+================+
|=#geom          |?             |?A            |set             |C             |N               |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *cree une geometrie texte*                                                                    |
+----------------+--------------+--------------+----------------+--------------+----------------+
|S               |              |              |set             |=match        |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *remplacement d'une valeur d'attribut par les valeurs retenues dans la selection*             |
| *par expression regulieres (recupere toute la selection)*                                     |
+----------------+--------------+--------------+----------------+--------------+----------------+
|S               |?             |\|L           |set             |              |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *remplacement d'une valeur d'attribut par le premier non vide*                                |
| *d'une liste avec defaut*                                                                     |
+----------------+--------------+--------------+----------------+--------------+----------------+
|S               |              |              |set             |=UUID         |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *cree un uuid*                                                                                |
+----------------+--------------+--------------+----------------+--------------+----------------+
|S               |?             |?A            |set             |              |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *remplacement d'une valeur d'attribut avec defaut*                                            |
+----------------+--------------+--------------+----------------+--------------+----------------+
|P               |?             |?A            |set             |              |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *positionne une variable*                                                                     |
+----------------+--------------+--------------+----------------+--------------+----------------+
|M               |?LC           |?L            |set             |              |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *remplacement d'une liste de valeurs d'attribut avec defaut*                                  |
+----------------+--------------+--------------+----------------+--------------+----------------+
|=#schema        |?             |?A            |set             |=maj          |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *change le schema de reference d'un objet et passe en majuscule*                              |
+----------------+--------------+--------------+----------------+--------------+----------------+
|M               |              |              |set             |=match        |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *remplacement d'une liste de valeurs d'attribut par les valeurs retenues dans la selection*   |
| *par expression regulieres (recupere les groupes de selections)*                              |
+----------------+--------------+--------------+----------------+--------------+----------------+
|S               |              |NC:           |set             |              |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
|S               |?             |L             |set             |?C            |=text           |
+----------------+--------------+--------------+----------------+--------------+----------------+
|=#schema        |?             |?A            |set             |=min          |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *change le schema de reference d'un objet et passe en minuscule*                              |
+----------------+--------------+--------------+----------------+--------------+----------------+
|P               |NC2:          |              |set             |              |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
|S               |?             |L             |set             |              |=list           |
+----------------+--------------+--------------+----------------+--------------+----------------+
|=#schema        |?             |?A            |set             |              |                |
+----------------+--------------+--------------+----------------+--------------+----------------+
| *change le schema de reference d'un objet*                                                    |
+----------------+--------------+--------------+----------------+--------------+----------------+
|S               |?             |L             |set             |              |=set            |
+----------------+--------------+--------------+----------------+--------------+----------------+





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
|      |?     |A     |split   |      |?N:N    |
+------+------+------+--------+------+--------+
|LP    |C     |      |split   |.     |?N:N    |
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

   ? :  defaut (optionnel)
   A :  attribut
   split :  
   ?N:N :   (optionnel)



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
|P          |C          |           |sub          |re         |?re          |
+-----------+-----------+-----------+-------------+-----------+-------------+



maxsub: nombre maxi de substitutions (variable locale)


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





.. index::
  double: .traitement_alpha;supp_classe

supp_classe
...........

   suppression d'elements

   suppression de la classe d objets avec tous ses objets et son schema

**syntaxes acceptees**

+----------+----------+----------+---------------+----------+------------+
|sortie    |defaut    |entree    |commande       |param1    |param2      |
+==========+==========+==========+===============+==========+============+
|          |          |          |supp_classe    |          |            |
+----------+----------+----------+---------------+----------+------------+
| *suppression de la classe d objets avec tous ses objets et son schema* |
+----------+----------+----------+---------------+----------+------------+




.. index::
  double: .traitement_alpha;to_date

to_date
.......

   convertit un texte en date en utilisant un formattage prdefini

   en cas de conflit (motif de type variable %xxx%)
   il est possible de remplacer le % par un autre caractere (par defaut µ)
   si on souhaite des espaces avant ou apres le format il est possible de definir
   la variable espace pour remplacer les espaces
   exemple: °°µs%d°° avec espace=° devient '  %s%d  '

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |?C    |?A    |to_date |C     |?C      |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_alpha;txtstruct

txtstruct
.........

   transforme un objet complexe contenu dans un attribut en structures de texte

   gere les dictionnaires et les iterables imbriques

**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|A     |      |A     |txtstruct|      |        |
+------+------+------+---------+------+--------+




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



archives
--------

archives

.. index::
  double: .traitement_archives;archive

archive
.......

   zippe les fichiers ou les repertoires de sortie


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |?C    |A     |archive |C     |?C      |
+------+------+------+--------+------+--------+
|      |C     |      |archive |C     |?C      |
+------+------+------+--------+------+--------+




**autres variables utilisees**

_sortie,


.. index::
  double: .traitement_archives;checksum

checksum
........

   cree un hash md5 ou sha64


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |?C    |A     |checksum|=md5  |        |
+------+------+------+--------+------+--------+
|?P    |C     |      |checksum|=md5  |        |
+------+------+------+--------+------+--------+





.. index::
  double: .traitement_archives;zip

zip
...

   zippe les fichiers ou les repertoires de sortie


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |?C    |A     |zip     |C     |?C      |
+------+------+------+--------+------+--------+
|      |C     |      |zip     |C     |?C      |
+------+------+------+--------+------+--------+




**autres variables utilisees**

_sortie,


.. index::
  double: .traitement_archives;zipdir

zipdir
......

   liste les fichiers d un zip


**syntaxes acceptees**

+--------+--------+--------+----------+--------+----------+
|sortie  |defaut  |entree  |commande  |param1  |param2    |
+========+========+========+==========+========+==========+
|?A      |?C      |?A      |zipdir    |        |          |
+--------+--------+--------+----------+--------+----------+
| *cree la liste de contenus dans l'attribut de sortie*   |
+--------+--------+--------+----------+--------+----------+
|?A      |?C      |?A      |zipdir    |=split  |          |
+--------+--------+--------+----------+--------+----------+
| *cree un objet par element du fichier zip*              |
+--------+--------+--------+----------+--------+----------+




**autres variables utilisees**

_entree,


.. index::
  double: .traitement_archives;zipextract

zipextract
..........

   extrait des fichiers d'un zip


**syntaxes acceptees**

+------+------+------+----------+------+--------+
|sortie|defaut|entree|commande  |param1|param2  |
+======+======+======+==========+======+========+
|?C    |?C    |?A    |zipextract|C     |?=all   |
+------+------+------+----------+------+--------+




**autres variables utilisees**

_entree,
_sortie,

fonctions auxiliaires
---------------------

fonctions auxiliaires

.. index::
  double: .traitement_aux;stat

stat
....

   fonctions statistiques

   la colonne a analyser est definie dans la premiere colonne de test
   fonctions disponibles
   cnt : comptage
   val : liste des valeurs
   val_uniq: valeurs distinctes
   cnt_val_uniq: nbre de valeurs distinctes
   min : minimum numerique
   max : maximum numerique
   somme : somme
   moy : moyenne

**syntaxes acceptees**

+------------+------------+------------+--------------+------------+--------------+
|sortie      |defaut      |entree      |commande      |param1      |param2        |
+============+============+============+==============+============+==============+
|C           |?           |?A          |stat          |C           |?C            |
+------------+------------+------------+--------------+------------+--------------+
| *nom de la colonne de stat;val;col entree;stat;fonction stat;prefixe_colonne*   |
+------------+------------+------------+--------------+------------+--------------+



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




dataviz
-------

dataviz

.. index::
  double: .traitement_dataviz;dfgraph

dfgraph
.......

   cree un graphique a partir d 'un tableau contenu dans un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |C?    |A     |dfgraph |C     |?LC     |
+------+------+------+--------+------+--------+
|=mws: |      |A     |dfgraph |C     |?LC     |
+------+------+------+--------+------+--------+
|=mws: |P     |      |dfgraph |C     |?LC     |
+------+------+------+--------+------+--------+


   ?A :  attribut de sortie (optionnel)
   C? :  fichier (optionnel)
   A :  attribut contenant les donnees
   dfgraph :  type de graphique
   C :  parametres

   =mws: :  mws: (mot_clef)
   A :  
   dfgraph :  attribut contenant les donnees
   C :  type de graphique
   ?LC :  parametres (optionnel)

   =mws: :  mws: (mot_clef)
   P :  variable contenant les donnees
   dfgraph :  
   C :  type de graphique
   ?LC :  parametres (optionnel)



.. index::
  double: .traitement_dataviz;dfload

dfload
......

   charge un tableau pandas dans un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?C    |?A    |dfload  |C     |        |
+------+------+------+--------+------+--------+





.. index::
  double: .traitement_dataviz;dfset

dfset
.....

 
 
 


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |L     |dfset   |      |        |
+------+------+------+--------+------+--------+





.. index::
  double: .traitement_dataviz;dfwrite

dfwrite
.......

   charge un tableau dans pandas dans un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |?C    |A     |dfwrite |?C    |        |
+------+------+------+--------+------+--------+




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
|=#    |?     |?L    |dbalpha |?     |?       |
+------+------+------+--------+------+--------+



traitement_virtuel;se declenche pour un objet virtuel
dest;repertoire temporaire si extracteur externe

**autres variables utilisees**

_sortie,
dest,
log,
traitement_virtuel,


.. index::
  double: .traitement_db;dbcheck

dbcheck
.......

   verifie la presence de classesd un selecteur en base
   sert a controler la compatibilite des fichiers qgis ou des listes de classes avec une base


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbcheck |C?    |        |
+------+------+------+--------+------+--------+





.. index::
  double: .traitement_db;dbclean

dbclean
.......

   cree un script pour vider un ensemble de tables

   commande de base sde donnees (debut de ligne en db:base;schema;table...)

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



**autres variables utilisees**

_sortie,


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

   db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;type_tables;buffer

**syntaxes acceptees**

+---------------+---------------+---------------+-----------------+---------------+-----------------+
|sortie         |defaut         |entree         |commande         |param1         |param2           |
+===============+===============+===============+=================+===============+=================+
|?L             |?              |?L             |dbgeo            |?C             |?N               |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
| *db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;type_tables;buffer*    |
+---------------+---------------+---------------+-----------------+---------------+-----------------+




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
  double: .traitement_db;dblist

dblist
......

   cree des objets virtuels ou reels a partir d un selecteur (1 objet par classe)

   cree des objets reels par defaut sauf si on mets la variable virtuel a 1

**syntaxes acceptees**

+----------+----------+----------+------------+----------+------------+
|sortie    |defaut    |entree    |commande    |param1    |param2      |
+==========+==========+==========+============+==========+============+
|A.C       |          |          |dblist      |?C        |?C          |
+----------+----------+----------+------------+----------+------------+
|=#obj     |          |          |dblist      |?C        |?C          |
+----------+----------+----------+------------+----------+------------+
| *cree un objet par classe avec l identifiant de l objet d entree*   |
+----------+----------+----------+------------+----------+------------+
|          |          |          |dblist      |?C        |?C          |
+----------+----------+----------+------------+----------+------------+
| *cree un objet par classe avec l'identifiant de la classe*          |
+----------+----------+----------+------------+----------+------------+


   A.C :  idclasse resultante
   dblist :  
   ?C :  #1 (optionnel)
   ?C :  #2 (optionnel)

   =#obj :  #obj (mot_clef)
   dblist :  
   ?C :  #1 (optionnel)
   ?C :  #2 (optionnel)

   dblist :  
   ?C :  #1 (optionnel)
   ?C :  #2 (optionnel)


**autres variables utilisees**

base\_,
db\_,
server\_,
user\_,
virtuel,


.. index::
  double: .traitement_db;dbmap_qgs

dbmap_qgs
.........

   remappe des fichiers qgis pour un usage en local en prenant en comte un selecteur


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |?C    |      |dbmap_qgs|C     |?C      |
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

   si la requete contient %#niveau ou %#classe la requete est passee sur chaque
   classe du selecteur en substituant les variables par la classe courante
   sinon elle est passee une fois pour chaque base du selecteur
   les variables %#base et %#attr sont egalement substituees
   autres variables:
   %#info : acces a des informations sur la classe
   (nom_geometrie,dimension,type_geom,objcnt_init,courbe,alias,type_table)
   %#metas : acces a des informations sur la requete
   (script_ref,filtre_niveau,filtre_classe,origine,restrictions,tables)

**syntaxes acceptees**

+---------+---------+---------+-----------+---------+-----------+
|sortie   |defaut   |entree   |commande   |param1   |param2     |
+=========+=========+=========+===========+=========+===========+
|?A       |?        |?L       |dbreq      |C        |A.C        |
+---------+---------+---------+-----------+---------+-----------+
|?A       |?        |?L       |dbreq      |C        |A          |
+---------+---------+---------+-----------+---------+-----------+
|         |         |=#       |dbreq      |C        |?A         |
+---------+---------+---------+-----------+---------+-----------+
|         |         |=#       |dbreq      |C        |?A.C       |
+---------+---------+---------+-----------+---------+-----------+
|         |         |=#       |dbreq      |C        |=#         |
+---------+---------+---------+-----------+---------+-----------+
|         |         |         |dbreq      |C        |=#         |
+---------+---------+---------+-----------+---------+-----------+
|LP       |         |         |dbreq      |C        |?L         |
+---------+---------+---------+-----------+---------+-----------+
|=mws:    |         |         |dbreq      |C        |?LC        |
+---------+---------+---------+-----------+---------+-----------+
| *mode webservice: renvoie le resultat brut de la requete*     |
+---------+---------+---------+-----------+---------+-----------+





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



**autres variables utilisees**

groupe_bases,


.. index::
  double: .traitement_db;dbselect

dbselect
........

   creation d un selecteur: ce selecteur peut etre reutilise pour des operations
   sur les bases de donnees


**syntaxes acceptees**

+------+------+------+--------+-----------+--------+
|sortie|defaut|entree|commande|param1     |param2  |
+======+======+======+========+===========+========+
|A     |?     |?     |dbselect|?          |?       |
+------+------+------+--------+-----------+--------+
|A     |L     |      |dbselect|=merge     |        |
+------+------+------+--------+-----------+--------+
|A     |C     |      |dbselect|=deletebase|        |
+------+------+------+--------+-----------+--------+




.. index::
  double: .traitement_db;dbset

dbset
.....

   renseigne des champs par requete en base

   cree des objets si multiple est specifie
   renseigne le champ #nb_lignes avec le nombre d'objets crees
   les champs d'entree sont fournis a la requete et remplacent les %s
   si les tables de la requete ou le nom des attributs dependent de l objet
   il faut les ecrire sous la forme %#[nom_attribut]

**syntaxes acceptees**

+------+------+------+--------+------+----------+
|sortie|defaut|entree|commande|param1|param2    |
+======+======+======+========+======+==========+
|M     |?     |?L    |dbset   |C     |?=multiple|
+------+------+------+--------+------+----------+





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

   chargement en base de donnees en bloc


**syntaxes acceptees**

+------+------+------+--------+---------+--------+
|sortie|defaut|entree|commande|param1   |param2  |
+======+======+======+========+=========+========+
|?L    |      |?L    |dbwrite |?=#nogeom|        |
+------+------+------+--------+---------+--------+




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
   si le nom du script commence par # c'est un script interne predefini

**syntaxes acceptees**

+-----------+-----------+-----------+-------------+-----------+-------------+
|sortie     |defaut     |entree     |commande     |param1     |param2       |
+===========+===========+===========+=============+===========+=============+
|           |?C         |?A         |runsql       |?C         |?C           |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *parametres:base;;;;?nom;?variable contenant le nom;runsql;?log;?sortie*  |
| *si le nom du script commence par # c'est un script interne predefini*    |
+-----------+-----------+-----------+-------------+-----------+-------------+



**autres variables utilisees**

_progdir,

divers
------

divers

.. index::
  double: .traitement_divers;attwriter

attwriter
.........

   traite un attribut d'un objet comme une sortie cree un objet par fanout


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|A     |      |      |attwriter|C     |?C      |
+------+------+------+---------+------+--------+




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
|A       |        |?L      |compare   |L       |C         |
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
|S             |?C            |?A            |getkey          |?A            |?A              |
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

 
 
 


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |?C    |?A    |log     |C     |?C      |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_divers;merge

merge
.....

   fusionne des objets adjacents de la meme classe en fonction de champs communs


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |      |L     |merge   |?C    |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_divers;objgroup

objgroup
........

   accumule des attributs en tableaux


**syntaxes acceptees**

+-----------------+-----------------+-----------------+-------------------+-----------------+-------------------+
|sortie           |defaut           |entree           |commande           |param1           |param2             |
+=================+=================+=================+===================+=================+===================+
|?L               |?C               |L                |objgroup           |C                |?L                 |
+-----------------+-----------------+-----------------+-------------------+-----------------+-------------------+
| *cree un tableau par attribut autant de tableaux que de champs en entree/sortie*                              |
| *si un seul attribut en sortie cree un tableau contenant des champs nommes*                                   |
| *si aucun attribut en sortie : garde les noms des attributs d'entree*                                         |
| *sinon le nombre de sorties doit etre égal au nombre d'entrees sinon seul lees correspondances sont traitees* |
+-----------------+-----------------+-----------------+-------------------+-----------------+-------------------+


   ?L :  attributs en sortie (optionnel)
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
|L       |?C      |?A      |preload   |?C      |C         |
+--------+--------+--------+----------+--------+----------+
| *parametres clef;fichier;attribut;preload;macro;nom*    |
+--------+--------+--------+----------+--------+----------+




.. index::
  double: .traitement_divers;sortir

sortir
......

   sortir dans differents formats


**syntaxes acceptees**

+--------------+------------+------------+--------------+------------+--------------+
|sortie        |defaut      |entree      |commande      |param1      |param2        |
+==============+============+============+==============+============+==============+
|=#schema      |C           |?L          |sortir        |?C          |?C            |
+--------------+------------+------------+--------------+------------+--------------+
| *parametres:#schema;nom_schema;?liste_attributs;sortir;format[fanout]?;?nom*      |
+--------------+------------+------------+--------------+------------+--------------+
|              |            |?L          |sortir        |?C          |?C            |
+--------------+------------+------------+--------------+------------+--------------+
| *parametres:?liste_attributs;sortir;format[fanout]?;?nom*                         |
+--------------+------------+------------+--------------+------------+--------------+




.. index::
  double: .traitement_divers;tmpstore

tmpstore
........

   stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie


**syntaxes acceptees**

+---------------+---------------+---------------+-----------------+---------------+-----------------+
|sortie         |defaut         |entree         |commande         |param1         |param2           |
+===============+===============+===============+=================+===============+=================+
|               |               |?L             |tmpstore         |?=uniq         |?=sort           |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
| *liste de clefs;tmpstore;uniq;sort|rsort : stockage avec option de tri*                           |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
|               |               |?L             |tmpstore         |?=uniq         |?=rsort          |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
|               |               |?L             |tmpstore         |=cmp           |#C               |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
| *liste de clefs;tmpstore;cmp;nom : prechargement pour comparaisons*                               |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
|               |               |?L             |tmpstore         |=cmpf          |#C               |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
|?L             |               |?L             |tmpstore         |=clef          |#C               |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
| *champs a stocker;liste de clefs,tmpstore;cmp;nom : prechargement pour comparaisons ou jointures* |
+---------------+---------------+---------------+-----------------+---------------+-----------------+
|S              |               |?L             |tmpstore         |=cnt           |?=clef           |
+---------------+---------------+---------------+-----------------+---------------+-----------------+




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
|           |?C         |?A         |addgeom      |N          |?N           |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *ex: A;addgeom  avec A = (1,2),(3,3) -> (1,2),(3,3)*                      |
+-----------+-----------+-----------+-------------+-----------+-------------+
|           |?C         |?L         |addgeom      |N          |             |
+-----------+-----------+-----------+-------------+-----------+-------------+
| *  X,Y;addgeom avec X=1,2,3,4 et Y=6,7,8,9 -> (1,6),(2,7),(3,8),(4,9)*    |
+-----------+-----------+-----------+-------------+-----------+-------------+


   ?C :  defaut (optionnel)
   ?A :  variable contenant les coordonnees (optionnel)
   addgeom :  
   N :  type_geom
   ?N :  ordre des coordonnees(21 inverse x et y) (optionnel)

   ?C :  defaut (optionnel)
   ?L :  liste de variables contenant les coordonnees (optionnel)
   addgeom :  
   N :  type_geom



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
|      |      |      |change_couleur|N     |N       |
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
|      |?N    |?A    |coordp  |      |        |
+------+------+------+--------+------+--------+
|      |=C    |      |coordp  |      |        |
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
  double: .traitement_geom;emprise

emprise
.......

   retourne l emprise de la geometrie


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |emprise |      |        |
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
|P                   |                    |                    |run                   |C                   |?C                    |
+--------------------+--------------------+--------------------+----------------------+--------------------+----------------------+
| *execution en debut de process avec sans recuperation eventuelle d'un resultat dans une variable*                               |
+--------------------+--------------------+--------------------+----------------------+--------------------+----------------------+



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
|P     |C     |      |compare_schema|C     |?=full  |
+------+------+------+--------------+------+--------+
|A     |      |      |compare_schema|C     |        |
+------+------+------+--------------+------+--------+





.. index::
  double: .traitement_schema;cree_schema

cree_schema
...........

   cree un schema a partir d objets contenant la structure

   ;nom;;cree_schema;classe table;classe enums

**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|      |?C    |      |cree_schema|C     |C       |
+------+------+------+-----------+------+--------+




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
  double: .traitement_schema;sc_change_type

sc_change_type
..............

   change le type d'attributs attribut d un schema sans toucher aux objets


**syntaxes acceptees**

+-----------+-----------+-----------+-------------------+-----------+-------------+
|sortie     |defaut     |entree     |commande           |param1     |param2       |
+===========+===========+===========+===================+===========+=============+
|C          |?C         |?L         |sc_change_type     |           |             |
+-----------+-----------+-----------+-------------------+-----------+-------------+
| *change le type d'une liste d'attributs*                                        |
+-----------+-----------+-----------+-------------------+-----------+-------------+
|C          |?C         |?L         |sc_change_type     |C          |?L           |
+-----------+-----------+-----------+-------------------+-----------+-------------+
| *cas statique change un type en un autre sur une liste de classes d'un schema*  |
+-----------+-----------+-----------+-------------------+-----------+-------------+




.. index::
  double: .traitement_schema;sc_ordre

sc_ordre
........

   ordonne les champs dans un schema


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|L     |      |      |sc_ordre|      |        |
+------+------+------+--------+------+--------+




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

   la variable taux_conformite permet de definir me taux minimum d'objets renseignes

**syntaxes acceptees**

+----------------+-------------+-------------+---------------+-------------+---------------+
|sortie          |defaut       |entree       |commande       |param1       |param2         |
+================+=============+=============+===============+=============+===============+
|=#schema?       |             |             |schema         |C?           |?N             |
+----------------+-------------+-------------+---------------+-------------+---------------+
| *la variable taux_conformite permet de definir me taux minimum d'objets renseignes*      |
+----------------+-------------+-------------+---------------+-------------+---------------+




**autres variables utilisees**

force_analyse,
taux_conformite,


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
    stable : declare un schema stable
    instable declare un schema instable

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
| * stable : declare un schema stable*                            |
| * instable declare un schema instable*                          |
+---------+---------+---------+-------------+---------+-----------+
|C        |?C       |A        |set_schema   |         |           |
+---------+---------+---------+-------------+---------+-----------+





.. index::
  double: .traitement_schema;supp_enums

supp_enums
..........

   transforme un schema en mode basique (supprime des enums)

   ;;attributs a traiter(tous);;

**syntaxes acceptees**

+------+------+------+----------+------+--------+
|sortie|defaut|entree|commande  |param1|param2  |
+======+======+======+==========+======+========+
|      |      |?L    |supp_enums|      |        |
+------+------+------+----------+------+--------+




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



log;err ou warn par defaut no;

**autres variables utilisees**

log,

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
  double: .traitement_shapely;centre

centre
......

 
 
 


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |centre  |?=in  |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_shapely;geomerge

geomerge
........

   fusionne des objets adjacents de la meme classe en fonction de champs communs


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?L    |      |?L    |geomerge|?LC   |?C      |
+------+------+------+--------+------+--------+





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
   =in :  in (mot_clef)
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

   telecharge un fichier via http

   l'entete du retour est stocke dans l'attribut #http_header

**syntaxes acceptees**

+---------+---------+---------+-----------+---------+-----------+
|sortie   |defaut   |entree   |commande   |param1   |param2     |
+=========+=========+=========+===========+=========+===========+
|         |?C       |?A       |download   |?C       |?C         |
+---------+---------+---------+-----------+---------+-----------+
| *telecharge un element vers un fichier ou un repertoire*      |
+---------+---------+---------+-----------+---------+-----------+
|A        |?C       |?A       |download   |         |           |
+---------+---------+---------+-----------+---------+-----------+
| *telecharge un element vers un attribut*                      |
+---------+---------+---------+-----------+---------+-----------+
|A        |?C       |?A       |download   |=#B      |           |
+---------+---------+---------+-----------+---------+-----------+
| *telecharge un element vers un attribut en mode binaire*      |
+---------+---------+---------+-----------+---------+-----------+
|         |?C       |?A       |download   |=#json   |?LC        |
+---------+---------+---------+-----------+---------+-----------+
| *telecharge un element json et genere un objet par element*   |
+---------+---------+---------+-----------+---------+-----------+


   A :  attribut de sortie
   ?C :  url (optionnel)
   ?A :  attribut contenant l'url (optionnel)
   download :  
   =#B :  #B (mot_clef)

   ?C :  url (optionnel)
   ?A :  attribut contenant l'url (optionnel)
   download :  
   =#json :  #json (mot_clef)
   ?LC :   (optionnel)

   ?C :  url (optionnel)
   ?A :  attribut contenant l'url (optionnel)
   download :  
   ?C :  repertoire (optionnel)
   ?C :  nom (optionnel)

   A :  attribut de sortie
   ?C :  url (optionnel)
   ?A :  attribut contenant l'url (optionnel)
   download :  

trust;si vrai(1,t,true...) les certificats ssl du site ne sont pas verifies
http_encoding;force l encoding du rettour par defaut c est celui de l entete http

**autres variables utilisees**

http_encoding,


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



**autres variables utilisees**

_sortie,
localdir,


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





.. index::
  double: .traitement_web;qwc2url

qwc2url
.......

 
 
 


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?C    |?A    |qwc2url |N     |C       |
+------+------+------+--------+------+--------+
|P     |C     |      |qwc2url |N     |C       |
+------+------+------+--------+------+--------+





.. index::
  double: .traitement_web;wfsload

wfsload
.......

   recupere une couche wfs

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
  double: .traitement_workflow;attdecode

attdecode
.........

   decode un attribut de type byte en texte


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|A     |?C    |A     |attdecode|?C    |?C      |
+------+------+------+---------+------+--------+





.. index::
  double: .traitement_workflow;attload

attload
.......

   stocke le contenu d un fichier dans un attribut


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?C    |A     |attload |?C    |?C      |
+------+------+------+--------+------+--------+





.. index::
  double: .traitement_workflow;attreader

attreader
.........

   traite un attribut d'un objet comme une source de donnees

   par defaut attreader supprime le contenu de l attribut source
   pour le conserver positionner la variable keepdata a 1

**syntaxes acceptees**

+----------+----------+----------+-------------+----------+------------+
|sortie    |defaut    |entree    |commande     |param1    |param2      |
+==========+==========+==========+=============+==========+============+
|?L        |?C        |A         |attreader    |C         |?C          |
+----------+----------+----------+-------------+----------+------------+
| *par defaut attreader supprime le contenu de l attribut source*      |
| *pour le conserver positionner la variable keepdata a 1*             |
+----------+----------+----------+-------------+----------+------------+





.. index::
  double: .traitement_workflow;attsave

attsave
.......

   stocke le contenu d un attribut comme un fichier


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |?C    |A     |attsave |?C    |?C      |
+------+------+------+--------+------+--------+





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
|      |      |      |call    |      |        |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;charge

charge
......

   chargement d objets en fichier

   cette fonction est l' équivalent du chargement initial
   peut fonctionner en parallele positionner multi a -1
   pour un nombre de process egal au nombre de processeurs

**syntaxes acceptees**

+---------+---------+---------+-----------+---------+-----------+
|sortie   |defaut   |entree   |commande   |param1   |param2     |
+=========+=========+=========+===========+=========+===========+
|?A       |?C       |?A       |charge     |?C       |           |
+---------+---------+---------+-----------+---------+-----------+
| *cette fonction est l' équivalent du chargement initial*      |
| *peut fonctionner en parallele positionner multi a -1*        |
| *pour un nombre de process egal au nombre de processeurs*     |
+---------+---------+---------+-----------+---------+-----------+
|?A       |?C       |?A       |charge     |[A]      |           |
+---------+---------+---------+-----------+---------+-----------+





.. index::
  double: .traitement_workflow;creobj

creobj
......

   cree des objets de test pour les tests fonctionnels


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|L     |LC    |?L    |creobj  |C     |?N      |
+------+------+------+--------+------+--------+


   L :  liste d'attributs
   LC :  liste valeurs
   ?L :  liste att valeurs (optionnel)
   creobj :  
   C :  nom(niv,classe)
   ?N :  nombre d'objets a creer (optionnel)


**autres variables utilisees**

schema_entree,


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
  double: .traitement_workflow;end_parallel

end_parallel
............

 
 
 


**syntaxes acceptees**

+------+------+------+------------+------+--------+
|sortie|defaut|entree|commande    |param1|param2  |
+======+======+======+============+======+========+
|      |      |      |end_parallel|      |        |
+------+------+------+------------+------+--------+




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

   sortie;defaut;attribut;filter;liste valeurs;liste sorties
   si la liste de sorties est vide c'est les valeurs qui font office de sortie

**syntaxes acceptees**

+------------+------------+------------+--------------+------------+--------------+
|sortie      |defaut      |entree      |commande      |param1      |param2        |
+============+============+============+==============+============+==============+
|?S          |?C          |A           |filter        |LC          |?LC           |
+------------+------------+------------+--------------+------------+--------------+
| *sortie;defaut;attribut;filter;liste valeurs;liste sorties*                     |
| *si la liste de sorties est vide c'est les valeurs qui font office de sortie*   |
+------------+------------+------------+--------------+------------+--------------+




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

+-----------+--------+--------+--------------+--------+----------+
|sortie     |defaut  |entree  |commande      |param1  |param2    |
+===========+========+========+==============+========+==========+
|?=#schema  |?C      |?A      |liste_schema  |C       |?=reel    |
+-----------+--------+--------+--------------+--------+----------+
|=mws:      |?C      |        |liste_schema  |C       |          |
+-----------+--------+--------+--------------+--------+----------+
| *cree des objets virtuels par defaut sauf si on precise reel*  |
+-----------+--------+--------+--------------+--------+----------+
|A          |?C      |        |liste_schema  |C       |          |
+-----------+--------+--------+--------------+--------+----------+




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
  double: .traitement_workflow;parallel

parallel
........

   passe le traitement en parralele les objets sont dispatches sur les workers


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |parallel|?N    |?N      |
+------+------+------+--------+------+--------+




.. index::
  double: .traitement_workflow;paramgroups

paramgroups
...........

   liste les groupes de parametres selon un critere


**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|A     |?C    |?A    |paramgroups|?C    |        |
+------+------+------+-----------+------+--------+
|=mws: |?LC   |      |paramgroups|?C    |        |
+------+------+------+-----------+------+--------+



**autres variables utilisees**

virtuel,


.. index::
  double: .traitement_workflow;pass

pass
....

   ne fait rien et passe. permet un branchement distant


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |pass    |?C    |        |
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
|      |C?    |L     |print   |C?    |=noms?  |
+------+------+------+--------+------+--------+
|      |      |*     |print   |C?    |=noms?  |
+------+------+------+--------+------+--------+
|=mws: |=P    |?L    |print   |C?    |=noms?  |
+------+------+------+--------+------+--------+
|      |C     |      |print   |C?    |=noms?  |
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
|      |      |?A    |printv  |C?    |=noms?  |
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
  double: .traitement_workflow;resetlog

resetlog
........

 
 
 


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |resetlog|=del  |C       |
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
  double: .traitement_workflow;return

return
......

   sort d une macro


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |return  |?C    |        |
+------+------+------+--------+------+--------+



**autres variables utilisees**

erreurs,


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

   ne fait rien mais envoie un objet virtuel ou reel dans le circuit avec un schema si defini


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |start   |?C    |=?reel  |
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


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|L     |LC    |      |testobj |C     |?N      |
+------+------+------+--------+------+--------+


   L :  liste d'attributs
   LC :  liste valeurs
   testobj :  
   C :  nom(niv,classe)
   ?N :  nombre d'objets a creer (optionnel)


**autres variables utilisees**

schema_entree,


.. index::
  double: .traitement_workflow;version

version
.......

   affiche la version du logiciel et les infos


**syntaxes acceptees**

+------+------+------+--------+-------+--------+
|sortie|defaut|entree|commande|param1 |param2  |
+======+======+======+========+=======+========+
|      |      |      |version |?=full |        |
+------+------+------+--------+-------+--------+
|      |      |      |version |?=True |        |
+------+------+------+--------+-------+--------+
|      |      |      |version |?=False|        |
+------+------+------+--------+-------+--------+




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

   stockage de l objet dans un fichier ou un attribut en utilisant un template jinja2


**syntaxes acceptees**

+------+------+------+-------------+------+--------+
|sortie|defaut|entree|commande     |param1|param2  |
+======+======+======+=============+======+========+
|A     |C?    |?A    |formated_save|C     |        |
+------+------+------+-------------+------+--------+
|[A]   |C?    |?A    |formated_save|C     |?C      |
+------+------+------+-------------+------+--------+


   A :  attribut
   C? :  defaut (optionnel)
   ?A :  attribut nom du template (optionnel)
   formated_save :  
   C :  repertoire de template

   [A] :  nom fichier
   C? :  defaut (optionnel)
   ?A :  attribut nom du template (optionnel)
   formated_save :  
   C :  repertoire de template
   ?C :  repertoire de sortie (optionnel)



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

   retourne le premier element trouve qui correspond aux criteres

**syntaxes acceptees**

+--------+--------+--------+------------+--------+----------+
|sortie  |defaut  |entree  |commande    |param1  |param2    |
+========+========+========+============+========+==========+
|H       |?C      |A       |xmlextract  |C       |?C        |
+--------+--------+--------+------------+--------+----------+
| *sort le parametre sezlectionne sous forme d'un attribut* |
+--------+--------+--------+------------+--------+----------+
|D       |?C      |A       |xmlextract  |C       |?C        |
+--------+--------+--------+------------+--------+----------+
| *sort tous les parametres sous forme d'un dictionnaire*   |
+--------+--------+--------+------------+--------+----------+
|S       |?C      |A       |xmlextract  |A.C     |?C        |
+--------+--------+--------+------------+--------+----------+


   H :  attribut sortie(hstore)
   ?C :  defaut (optionnel)
   A :  attribut xml
   xmlextract :  
   C :  tag a extraire
   ?C :  groupe de recherche (optionnel)

   D :  attribut sortie(dictionnaire)
   ?C :  defaut (optionnel)
   A :  attribut xml
   xmlextract :  
   C :  tag a extraire
   ?C :  groupe de recherche (optionnel)

   S :  attribut sortie
   ?C :  defaut (optionnel)
   A :  attribut xml
   xmlextract :  
   A.C :  element a extraire sous forme tag.attribut ou tag.#text
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

