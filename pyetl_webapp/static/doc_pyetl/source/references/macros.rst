
macros
======

Pyetl dispose de nmbreuses macros preinstallees qui etendent les capacites de commandes de base
il est possible de definir des macros au niveau d un groupe d utilisateurs ou au niveau personnel
les macros peuvent aussi etre définies localement dans un script

definition d'une macros

&&#define;#nom;variable....
commandes
commandes
...
&&#end


import d une macros

<#nom;valeur;...

import d une macro avec execution immediate

<<#nom;valeur...

une macro peut importer d autres macros

macros integrees:
-----------------

.. toctree::
    :maxdepth: 1
    :caption: Contents:

    autodoc/macrodef
