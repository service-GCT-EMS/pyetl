
macros
======

Pyetl dispose de nombreuses macros préinstallées qui étendent les capacités de commandes de base
il est possible de définir des macros au niveau d un groupe d utilisateurs ou au niveau personnel
les macros peuvent aussi etre définies localement dans un script

definition d'une macros

&&#define;#nom;variable....
commandes
commandes
...
&&#end


import d une macros

<#nom;valeur;...

import d une macro avec execution immédiate

<<#nom;valeur...

une macro peut importer d autres macros

macros intégrées:
-----------------

.. toctree::
    :maxdepth: 1
    :caption: Contents:

    autodoc/macrodef
