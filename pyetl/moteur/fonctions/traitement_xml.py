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


def h_xmlextract(regle):
    """extraction d'element xml"""
    regle.cadre = regle.params.cmp2.val
    tmp = regle.params.cmp1.val.split(":")
    regle.recherche = tmp[0]
    regle.item = tmp[1] if len(tmp) == 2 else ""


def getcadre(regle, obj):
    """"analyse un xml et livre le cadre de recherche"""
    xml = obj.attributs.get(regle.params.att_entree.val)
    if not xml:
        return (), ""
    try:
        # pstart=time.time()
        tree = ET.fromstring(xml)
        # print ("parsetime",time.time()-pstart)
    except ParseError as err:
        print("erreur xml mal formé", err, obj)
        return (), ""
    cadres = tree.iter(regle.cadre) if regle.cadre else [tree]
    # print("xmlextract", cadres, regle.recherche)
    if regle.getvar("keepxml") != "1":  # on evite du duppliquer des gros xml
        obj.attributs[regle.params.att_entree.val] = ""
        print("on ne dupplique pas")
    return cadres, xml


def f_xmlextract(regle, obj):
    """#aide||decoupage d'un attribut xml en objets
  #aide_spec||on cree un objet pour chaque element
   #pattern1||H;;A;xmlextract;C;?C||sortie
   #pattern2||D;;A;xmlextract;C;?C||sortie
   #pattern3||S;;A;xmlextract;C:C;?C||sortie
#parametres1||attribut sortie(hstore);defaut;attribut xml;;tag a extraire;groupe de recherche
      #test1||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^H:XX;;V4;xmlextract;pp;||ath;XX;p2;titi
      #test2||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^*;;V4;xmlextract;pp;||atv;p2;titi
      #test3||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^XX;;V4;xmlextract;pp:p1;||atv;XX;toto
       """
    trouve = False
    cadres, xml = getcadre(regle, obj)
    for cadre in cadres:
        # print("traitement", cadre)
        for elem in cadre.iter(regle.recherche):

            # print("traitement", regle.params.att_sortie.val, contenu)
            contenu = elem.get(regle.item, "") if regle.item else elem
            print(
                "-------------------xmlextract",
                regle.params.att_sortie,
                contenu,
                regle.fstore,
            )
            regle.setval_sortie(obj, contenu)
            print("---obj", obj)
            obj.attributs[regle.params.att_entree.val] = xml
            # print("apres xml", obj.attributs)
            return True
    return trouve


def f_xmlsplit(regle, obj):
    """#aide||decoupage d'un attribut xml en objets
  #aide_spec||on cree un objet pour chaque element
   #pattern1||S;;A;xmlsplit;C;?C||sortie
   #pattern2||H;;A;xmlsplit;C;?C||sortie
   #pattern3||D;;A;xmlsplit;C;?C||sortie
#parametres1||attribut sortie(hstore);defaut;attribut xml;;tag a extraire;groupe de recherche
      #test1||obj||^V4;<g><pp p1="toto"/><pp p1="titi"/></g>;;set||^;;V4;xmlsplit;pp;||#xmltag;pp;;;;;;pass-;;||cnt;2
     #test1b||obj||^V4;<g><pp p1="titi"/></g>;;set||^;;V4;xmlsplit;pp;||#xmltag;pp;;;;;;pass-;;||ath;#xmlextract;p1;titi
       """
    trouve = False
    cadres, xml = getcadre(regle, obj)
    for cadre in cadres:
        # print("traitement", cadre)
        for elem in cadre.iter(regle.recherche):
            obj2 = obj.dupplique()
            # # print("detecte element", elem.items())
            contenu = elem.tostring() if regle.params.pattern == "1" else elem
            regle.setval_sortie(obj, contenu)
            obj2.attributs["#xmltag"] = regle.recherche
            obj2.attributs["#xmlgroup"] = regle.cadre
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
            trouve = True
    obj.attributs[regle.params.att_entree.val] = xml
    return trouve
