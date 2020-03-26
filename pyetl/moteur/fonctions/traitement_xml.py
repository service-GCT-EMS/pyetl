# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions traitement xml
"""
import logging
import os
import io
import time
from xml.etree.ElementTree import ParseError
import xml.etree.cElementTree as ET

LOGGER = logging.getLogger("pyetl")


def h_xmlextract(regle):
    """extraction d'element xml"""
    regle.cadre = regle.params.cmp2.val
    regle.recherche = regle.params.cmp1.val
    regle.item = regle.params.cmp1.definition[0] if regle.params.cmp1.definition else ""
    regle.keepdata = regle.getvar("keepdata") == "1"
    regle.keeptree = regle.getvar("keeptree") == "1"


def getcadre(regle, obj):
    """"analyse un xml et livre le cadre de recherche"""

    xml = obj.attributs.get(regle.params.att_entree.val)
    if not xml:
        return (), ""
    if obj.attributs_speciaux and "__xmltree" in obj.attributs_speciaux:
        tree = obj.attributs_speciaux["__xmltree"]
        if not regle.keeptree:
            del obj.attributs_speciaux["__xmltree"]
    else:
        try:
            tree = ET.fromstring(xml)
        except ParseError as err:
            LOGGER.error("erreur xml mal formé", err, obj)
            # print("erreur xml mal formé", err, obj)
            return (), xml
    cadres = tree.iter(regle.cadre) if regle.cadre else [tree]
    if not regle.keepdata:  # on evite du duppliquer des gros xml
        obj.attributs[regle.params.att_entree.val] = ""
    if regle.keeptree:
        if obj.attributs_speciaux is None:
            obj.attributs_speciaux = {"__xmltree": tree}
        else:
            obj.attributs_speciaux["__xmltree"] = tree
        # print("on ne dupplique pas")
    return cadres, xml


def f_xmlextract(regle, obj):
    """#aide||extraction de valeurs d un xml
  #aide_spec||on cree un objet pour chaque element
   #pattern1||H;;A;xmlextract;C;?C||sortie
   #pattern2||D;;A;xmlextract;C;?C||sortie
   #pattern3||S;;A;xmlextract;A.C;?C||sortie
#parametres1||attribut sortie(hstore);defaut;attribut xml;;tag a extraire;groupe de recherche
      #test1||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^H:XX;;V4;xmlextract;pp;||ath;XX;p2;titi
      #test2||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^*;;V4;xmlextract;pp;||atv;p2;titi
      #test3||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^XX;;V4;xmlextract;pp.p1;||atv;XX;toto
       """
    trouve = False
    cadres, xml = getcadre(regle, obj)
    for cadre in cadres:
        for elem in cadre.iter(regle.recherche):
            contenu = elem.get(regle.item, "") if regle.item else dict(elem.items())
            regle.setval_sortie(obj, contenu)
            obj.attributs[regle.params.att_entree.val] = xml
            return True
    return trouve


def f_xmlsplit(regle, obj):
    """#aide||decoupage d'un attribut xml en objets
  #aide_spec||on cree un objet pour chaque element
   #pattern1||S;;A;xmlsplit;C;?C||sortie
   #pattern2||H;;A;xmlsplit;C;?C||sortie
   #pattern3||D;;A;xmlsplit;C;?C||sortie
   #pattern4||S;;A;xmlsplit;A.C;?C||sortie
   #helper||xmlextract
#parametres1||attribut sortie(hstore);defaut;attribut xml;;tag a extraire;groupe de recherche
      #test1||obj||^V4;<g><pp p1="toto"/><pp p1="titi"/></g>;;set||^X;;V4;xmlsplit;pp;||#xmltag;pp;;;;;;pass-;;||cnt;2
     #test1b||obj||^V4;<g><pp p1="titi"/></g>;;set||^H:X;;V4;xmlsplit;pp;||#xmltag;pp;;;;;;pass-;;||ath;X;p1;titi
       """
    trouve = False
    cadres, xml = getcadre(regle, obj)
    for cadre in cadres:
        # print("traitement", cadre)
        for elem in cadre.iter(regle.recherche):
            obj2 = obj.dupplique()
            if regle.params.pattern == "1":
                contenu = ET.tostring(elem)
            elif regle.params.pattern in "23":
                contenu = dict(elem.items())
            elif regle.item:
                contenu = elem.get(regle.item, "")
            else:
                contenu = ""
            regle.setval_sortie(obj2, contenu)
            obj2.attributs["#xmltag"] = regle.recherche
            obj2.attributs["#xmlgroup"] = regle.cadre
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
            trouve = True
    obj.attributs[regle.params.att_entree.val] = xml
    return trouve
