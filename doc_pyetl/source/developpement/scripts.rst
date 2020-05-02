===================
Création de scripts
===================

Le script est le niveau de base de developpement de pyetl. pour tout traitement specifique qui ne
peut pas etre realise par un simple appel de macro, la solution la plus simple est de creer un scripts

un script est un fichier csv comportant des lignes de commandes et des inclusions de macros ou d autres scripts

la structure typique d un script comprend
une partie d affectation de variables
un ensemble de commandes

si le script definit ses propres macros elles doivent etre definies avant d etre utilisees.
