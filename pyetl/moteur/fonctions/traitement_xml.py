# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions traitement xml
"""
import logging
import os
import io
from xml.etree.ElementTree import ParseError
import xml.etree.cElementTree as ET


def h_xmlextract(regle):
    """extraction d'element xml"""
    regle.cadre = regle.params.cmp2.val
    tmp = regle.params.cmp1.val.split(":")
    regle.recherche = tmp[0]


def f_xmlextract(regle, obj):
    """#aide||decoupage d'un attribut xml en objets
  #aide_spec||on cree un objet pour chaque element
   #pattern1||;;A;xmlextract;C;?C||sortie
   #pattern2||H;;A;xmlextract;C;?C||sortie
   #pattern3||S;;A;xmlextract;C:C;?C||sortie
#parametres1||attribut sortie(hstore);defaut;attribut xml;;tag a extraire;groupe de recherche
      #test1||obj||^V4;<g><pp p1="toto"/><pp p1="titi"/></g>;;set||^;;V4;xmlextract;pp;||#xmltag;pp;;;;;;pass-;;||cnt;2
     #test1b||obj||^V4;<g><pp p1="titi"/></g>;;set||^;;V4;xmlextract;pp;||#xmltag;pp;;;;;;pass-;;||ath;#xmlextract;p1;titi
      #test2||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^XX;;V4;xmlextract;pp;||ath;XX;p2;titi
      #test3||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^XX;;V4;xmlextract;pp:p1;||atv;XX;toto
       """
    trouve = False
    xml = obj.attributs.get(regle.params.att_entree.val)
    if not xml:
        return False
    try:
        tree = ET.fromstring(xml)
    except ParseError as err:
        print("erreur xml mal formé", err, obj)
        return False
    cadres = tree.iter(regle.cadre) if regle.cadre else [tree]
    # print("xmlextract", cadres, regle.recherche)
    if regle.getvar("noxml"):  # on evite du duppliquer des gros xml
        obj.attributs[regle.params.att_entree.val] = ""
    for cadre in cadres:
        # print("traitement", cadre)
        for elem in cadre.iter(regle.recherche):
            contenu = ", ".join(
                [
                    '"'
                    + i
                    + '" => "'
                    + j.replace("\\", "\\\\").replace('"', r"\"")
                    + '"'
                    for i, j in elem.items()
                ]
            )
            if regle.params.att_sortie.val:
                regle.setval_sortie(obj, contenu)
                obj.attributs[regle.params.att_entree.val] = xml
                print("apres xml", obj.attributs)
                return True
            obj2 = obj.dupplique()
            # print("detecte element", elem.items())
            obj2.attributs["#xmlextract"] = contenu
            # obj2.attributs.update(((regle.prefix + i, j) for i, j in elem.items()))
            obj2.attributs["#xmltag"] = regle.recherche
            if regle.cadre:
                obj2.attributs["#xmlgroup"] = regle.cadre
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["next"])
            trouve = True
    obj.attributs[regle.params.att_entree.val] = xml
    return trouve
