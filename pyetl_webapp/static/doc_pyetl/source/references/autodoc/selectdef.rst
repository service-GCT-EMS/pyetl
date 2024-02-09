reference conditions
--------------------

   * A;[A]
       - selection sur la valeur d un attribut egalite stricte avec un attribut

   * A;
       - teste si un attribut existe

   * re:re;
       - teste si un attribut existe

   * L;
       - teste si des attributs existent

   * A;NC2:
       - evaluation d une expression avec un attribut

   * ;NC:
       - evaluation d une expression libre

   * C:C;
       -  existance de constantes sert a customiser des scripts

   * A;=<>:
       - vrai si l'attribut a change d'un objet au suivant

   * C:C;C
       - egalite de constantes sert a customiser des scripts

   * A;=:
       - selection sur la valeur d un attribut egalite stricte

   * =has:couleur;C
       - objet possedant un schema

   * ;=has:geom
   * =has:geom
       - vrai si l'objet a un attribut geometrique natif

   * ;=has:geomV
   * =has:geomV
       - vrai si l'objet a une geometrique en format interne

   * ;=has:pk
   * ;=has:PK
       - vrai si on a defini un des attributs comme clef primaire

   * ;=has:schema
   * =has:schema
       - objet possedant un schema

   * H:A;haskey:A
       - selection si une clef de hstore existe

   * H:A;hasval:C
       - selection si une clef de hstore n'est pas vide

   * H:A;A:C
       - selection sur une valeur d'un hstore

   * =ident:;in:fich
       - vrai si l identifiant de classe est dans un fichier

   * =ident:;re
       - vrai si l identifiant de classe verifie une expression

   * L;in:fich(re)
       - valeur dans un fichier sous forme d'expressions regulieres

   * schema:A;re
       - teste la valeur d un parametre de schema

   * schema:A:;C
       - test sur un parametre de schema

   * schema:T:;
   * ;schema:T:;
       - vrai si un attribut de type donne existe dans le schema de l'objet

   * L;schema:T:
       - vrai si des attributs nommes sont de type dmand

   * =schema:(.*);
       - test sur un parametre de schema

   * A;in:list
       - valeur dans une liste

   * L;in:list(re)
       - valeur dans une liste sous forme d'expressions regulieres

   * L;in:mem
       - valeur dans une liste en memoire (chargee par preload)

   * A;=in:schema
   * A;=in_schema
       - vrai si un attribut est defini dans le schema

   * ;=is:2d
   * ;=is:2D
       - vrai si l'objet est de dimension 2

   * ;=is:3d
   * ;=is:3D
       - vrai si l'objet est de dimension 3

   * =is:valid_date;C
   * =is:valid_date;[A]
   * (is:valid_date:)A;C
   * (is:valid_date:)A;[A]
       - vrai si la date est compatible avec la description ( sert dans les declecnheurs de batch)

   * =is:valid_time;C
   * =is:valid_time;[A]
   * (is:valid_time:)A;C
   * (is:valid_time:)A;[A]
       - vrai si l'heure est compatible avec la description ( sert dans les declencheurs de batch)

   * =type_geom:;N
       - vrai si l'objet est de dimension 3

   * =is:dir;C
       - teste si un repertoire existe

   * =is:file;C
       - teste si un fichier existe

   * ;=is:ko
   * ;=is:KO
       - operation precedente en echec

   * A;=is:not_null
   * A;=is:NOT_NULL
       - vrai si l'attribut existe et n est pas nul

   * A;=is:null
   * A;=is:NULL
       - vrai si l'attribut existe et est null

   * ;=is:ok
   * ;=is:OK
       - operation precedente correcte

   * A;=is:pk
   * A;=is:PK
       - vrai si l'attribut est une clef primaire

   * ;=is:reel
   * =is:reel;
       - objet virtuel

   * ;=is:virtuel
   * =is:virtuel;
       - objet virtuel

   * P;
       - teste si un parametre est non vide

   * P;re
       - teste la valeur d un parametre

   * A;re
   * A;re:re
       - selection sur la valeur d un attribut

   * =%;N
       - garde un objet tous les N

   * A;in:fich
       - valeur dans un fichier
