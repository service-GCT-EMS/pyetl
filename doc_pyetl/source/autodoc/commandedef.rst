commandes
=========

manipulation d'attributs
------------------------

manipulation d'attributs

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
|       |?      |A      |join     |#C     |?C       |
+-------+-------+-------+---------+-------+---------+


   L :  sortie
   ? :  defaut (optionnel)
   A :  entree
   join :  
   C[] :  fichier (dynamique)
   ?C :  position des champs dans le fichier (ordre) (optionnel)



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


db
--

db

dbalpha
.......

   recuperation d'objets depuis la base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?A    |?     |?     |dbalpha |?     |?       |
+------+------+------+--------+------+--------+




dbclean
.......

   vide un ensemble de tables


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbclean |?C    |?C      |
+------+------+------+--------+------+--------+




dbclose
.......

   recuperation d'objets depuis la base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbclose |      |        |
+------+------+------+--------+------+--------+




dbcount
.......

   nombre d'objets dans un groupe de tables


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |      |      |dbcount |?C    |        |
+------+------+------+--------+------+--------+




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




dbgeo
.....

   recuperation d'objets depuis la base de donnees

   db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;buffer

**syntaxes acceptees**

+-------------+-------------+-------------+---------------+-------------+---------------+
|sortie       |defaut       |entree       |commande       |param1       |param2         |
+=============+=============+=============+===============+=============+===============+
|?A           |?            |?L           |dbgeo          |?C           |?N             |
+-------------+-------------+-------------+---------------+-------------+---------------+
| *db:base;niveau;classe;fonction;att_sortie;valeur;champs a recuperer;dbgeo;buffer*    |
+-------------+-------------+-------------+---------------+-------------+---------------+




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




dbmaxval
........

   valeur maxi d une clef en base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|?P    |      |      |dbmaxval|?C    |        |
+------+------+------+--------+------+--------+




dbreq
.....

   recuperation d'objets depuis une requete sur la base de donnees

   db:base;niveau;classe;;att_sortie;valeurs;champ a integrer;dbreq;requete

**syntaxes acceptees**

+------------+------------+------------+--------------+------------+--------------+
|sortie      |defaut      |entree      |commande      |param1      |param2        |
+============+============+============+==============+============+==============+
|?A          |?           |?L          |dbreq         |C           |              |
+------------+------------+------------+--------------+------------+--------------+
| *db:base;niveau;classe;;att_sortie;valeurs;champ a integrer;dbreq;requete*      |
+------------+------------+------------+--------------+------------+--------------+




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




dbupdate
........

   chargement en base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbupdate|      |        |
+------+------+------+--------+------+--------+




dbwrite
.......

   chargement en base de donnees


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |dbwrite |      |        |
+------+------+------+--------+------+--------+




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




runsql
......

   lancement d'un script sql

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



geom
----

geom

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




aire
....

   calcule l'aire de l'objet


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |      |      |aire    |      |        |
+------+------+------+--------+------+--------+




change_couleur
..............

   remplace une couleur par une autre


**syntaxes acceptees**

+------+------+------+--------------+------+--------+
|sortie|defaut|entree|commande      |param1|param2  |
+======+======+======+==============+======+========+
|      |      |      |change_couleur|C     |C       |
+------+------+------+--------------+------+--------+




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




force_ligne
...........

   force la geometrie en ligne


**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|      |      |      |force_ligne|      |        |
+------+------+------+-----------+------+--------+




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




forcepoly
.........

   force la geometrie en polygone


**syntaxes acceptees**

+------+------+------+---------+-------+--------+
|sortie|defaut|entree|commande |param1 |param2  |
+======+======+======+=========+=======+========+
|      |      |      |forcepoly|?=force|        |
+------+------+------+---------+-------+--------+




geom
....

   force l'interpretation de la geometrie


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |geom    |?N    |?=S     |
+------+------+------+--------+------+--------+




geom2D
......

   passe la geometrie en 2D


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |geom2D  |      |        |
+------+------+------+--------+------+--------+




geom3D
......

   passe la geometrie en 2D


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |N     |?A    |geom3D  |?C    |        |
+------+------+------+--------+------+--------+




grid
....

   decoupage en grille


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|L     |      |      |grid    |LC    |N       |
+------+------+------+--------+------+--------+




gridx
.....

   decoupage grille en x


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |      |gridx   |N     |N       |
+------+------+------+--------+------+--------+




gridy
.....

   decoupage grille en x


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |      |gridy   |N     |N       |
+------+------+------+--------+------+--------+




longueur
........

   calcule la longueur de l'objet


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|S     |      |      |longueur|      |        |
+------+------+------+--------+------+--------+




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




multigeom
.........

   definit la geometrie comme multiple ou non


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |N     |      |multigeom|      |        |
+------+------+------+---------+------+--------+




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




resetgeom
.........

   annulle l'interpretation de la geometrie


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|      |      |      |resetgeom|      |        |
+------+------+------+---------+------+--------+




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




splitgeom
.........

   decoupage inconditionnel des lignes en points


**syntaxes acceptees**

+------+------+------+---------+------+--------+
|sortie|defaut|entree|commande |param1|param2  |
+======+======+======+=========+======+========+
|?A    |      |      |splitgeom|      |        |
+------+------+------+---------+------+--------+




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

hdel
....

   supprime une valeur d un hstore


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |A     |hdel    |L     |?       |
+------+------+------+--------+------+--------+




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




listefich
.........

 
 
 


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

schema
------

schema

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




force_alias
...........

   remplace les valeurs par les alias


**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|      |      |      |force_alias|?C    |        |
+------+------+------+-----------+------+--------+




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




liste_tables
............

   recupere la liste des tables d un schema a la fin du traitement


**syntaxes acceptees**

+------+------+------+------------+------+--------+
|sortie|defaut|entree|commande    |param1|param2  |
+======+======+======+============+======+========+
|      |      |      |liste_tables|C     |?=reel  |
+------+------+------+------------+------+--------+




map_schema
..........

   effectue des modifications sur un schema en gerant les correspondances


**syntaxes acceptees**

+--------+------+------+----------+------+--------+
|sortie  |defaut|entree|commande  |param1|param2  |
+========+======+======+==========+======+========+
|=#schema|C     |      |map_schema|C     |        |
+--------+------+------+----------+------+--------+




match_schema
............

   associe un schema en faisant un mapping au mieux


**syntaxes acceptees**

+------+------+------+------------+------+--------+
|sortie|defaut|entree|commande    |param1|param2  |
+======+======+======+============+======+========+
|      |?C    |      |match_schema|C     |?N      |
+------+------+------+------------+------+--------+




ordre
.....

   ordonne les champs dans un schema


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|L     |      |      |ordre   |      |        |
+------+------+------+--------+------+--------+




sc_add_attr
...........

   ajoute un attribut a un schema sans toucher aux objets


**syntaxes acceptees**

+------+------+------+-----------+------+--------+
|sortie|defaut|entree|commande   |param1|param2  |
+======+======+======+===========+======+========+
|A     |      |      |sc_add_attr|C?    |L?      |
+------+------+------+-----------+------+--------+




sc_supp_attr
............

   supprime un attribut d un schema sans toucher aux objets


**syntaxes acceptees**

+------+------+------+------------+------+--------+
|sortie|defaut|entree|commande    |param1|param2  |
+======+======+======+============+======+========+
|A     |      |      |sc_supp_attr|C?    |L?      |
+------+------+------+------------+------+--------+




schema
......

   cree un schema par analyse des objets et l'associe a un objet


**syntaxes acceptees**

+---------+------+------+--------+------+--------+
|sortie   |defaut|entree|commande|param1|param2  |
+=========+======+======+========+======+========+
|=#schema?|      |      |schema  |C?    |?N      |
+---------+------+------+--------+------+--------+




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



selecteurs
----------

selecteurs
shapely
-------

shapely

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



wfs
...

 
 
 

   ; classe;  attribut contenant la classe;wfs;url;format

**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|F     |?C    |?A    |wfs     |C     |?C      |
+------+------+------+--------+------+--------+
|A     |?C    |?A    |wfs     |C     |?C      |
+------+------+------+--------+------+--------+



workflow
--------

workflow

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




batch
.....

   execute un traitement batch a partir des parametres de l'objet


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



bloc
....

   definit un bloc d'instructions qui reagit comme une seule et genere un contexte


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |bloc    |      |        |
+------+------+------+--------+------+--------+




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



branch
......

   genere un branchement


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |branch  |C     |        |
+------+------+------+--------+------+--------+




call
....

   appel de macro avec gestion de variables locales


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |call    |C     |?LC     |
+------+------+------+--------+------+--------+




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




end
...

   finit un traitement sans stats ni ecritures


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |end     |      |        |
+------+------+------+--------+------+--------+




fail
....

   ne fait rien mais plante. permet un branchement distant


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |fail    |?C    |        |
+------+------+------+--------+------+--------+




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




fin_bloc
........

   definit la fin d'un bloc d'instructions


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |fin_bloc|      |        |
+------+------+------+--------+------+--------+




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




idle
....

   ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |idle    |      |        |
+------+------+------+--------+------+--------+




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




next
....

   force la sortie next


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |next    |      |        |
+------+------+------+--------+------+--------+




pass
....

   ne fait rien et passe. permet un branchement distant


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |pass    |?C    |        |
+------+------+------+--------+------+--------+




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




printv
......

   affichage des parametres nommes


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |printv  |C?    |=noms?  |
+------+------+------+--------+------+--------+




quitter
.......

   sort d une macro


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |quitter |?C    |        |
+------+------+------+--------+------+--------+




reel
....

   transforme un objet virtuel en objet reel


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |reel    |      |        |
+------+------+------+--------+------+--------+




retour
......

   ramene les elements apres l execution


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |C?    |L?    |retour  |C?    |=noms?  |
+------+------+------+--------+------+--------+




retry
.....

   relance un traitement a intervalle regulier


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|A     |      |      |retry   |C     |        |
+------+------+------+--------+------+--------+




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




sleep
.....

   ne fait rien mais laisse le mainmapper en attente (initialisation en mode parallele)


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |?C    |?A    |sleep   |      |        |
+------+------+------+--------+------+--------+




start
.....

   ne fait rien mais envoie un objet virtuel dans le circuit


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |start   |      |        |
+------+------+------+--------+------+--------+




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




sync
....

   finit un traitement en parallele et redonne la main sans stats ni ecritures


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |sync    |?C    |        |
+------+------+------+--------+------+--------+




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




version
.......

   affiche la version du logiciel et les infos


**syntaxes acceptees**

+------+------+------+--------+------+--------+
|sortie|defaut|entree|commande|param1|param2  |
+======+======+======+========+======+========+
|      |      |      |version |?=full|        |
+------+------+------+--------+------+--------+




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
   ?C :  nom du rep (optionnel)



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



xmlextract
..........

   extraction de valeurs d un xml

   retourne le premier element trouve

**syntaxes acceptees**

+------+------+------+----------+------+--------+
|sortie|defaut|entree|commande  |param1|param2  |
+======+======+======+==========+======+========+
|H     |      |A     |xmlextract|C     |?C      |
+------+------+------+----------+------+--------+
|D     |      |A     |xmlextract|C     |?C      |
+------+------+------+----------+------+--------+
|S     |      |A     |xmlextract|A.C   |?C      |
+------+------+------+----------+------+--------+


   H :  attribut sortie(hstore)
   A :  defaut
   xmlextract :  attribut xml
   C :  
   ?C :  tag a extraire (optionnel)



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
|S     |      |A     |xmlsplit|A.C   |?C      |
+------+------+------+--------+------+--------+


   S :  attribut sortie(hstore)
   A :  defaut
   xmlsplit :  attribut xml
   C :  
   ?C :  tag a extraire (optionnel)

