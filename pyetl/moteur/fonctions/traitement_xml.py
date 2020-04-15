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
import re
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
      #test3||obj||^V4;<g><pp p1="toto" p2="titi">text</pp></g>;;set||^XX;;V4;xmlextract;pp._T;||atv;XX;text
       """
    trouve = False
    cadres, xml = getcadre(regle, obj)
    for cadre in cadres:
        for elem in cadre.iter(regle.recherche):
            if regle.item == "_T":
                contenu = elem.text
            else:
                contenu = elem.get(regle.item, "") if regle.item else dict(elem.items())
            regle.setval_sortie(obj, contenu)
            obj.attributs[regle.params.att_entree.val] = xml
            return True
    return trouve


def h_xmlsplit(regle):
    """helper decoupage"""
    h_xmlextract(regle)
    # regle.reader = regle.stock_param.getreader("interne", regle)
    regle.changeschema = False


def f_xmlsplit(regle, obj):
    """#aide||decoupage d'un attribut xml en objets
  #aide_spec||on cree un objet pour chaque element
   #pattern1||S;;A;xmlsplit;C;?C||sortie
   #pattern2||H;;A;xmlsplit;C;?C||sortie
   #pattern3||D;;A;xmlsplit;C;?C||sortie
   #pattern4||S;;A;xmlsplit;A.C;?C||sortie
#parametres1||attribut sortie(hstore);defaut;attribut xml;;tag a extraire;groupe de recherche
      #test1||obj||^V4;<g><pp p1="toto"/><pp p1="titi"/></g>;;set||^X;;V4;xmlsplit;pp;||#xmltag;pp;;;;;;pass-;;||cnt;2
     #test1b||obj||^V4;<g><pp p1="titi"/></g>;;set||^H:X;;V4;xmlsplit;pp;||#xmltag;pp;;;;;;pass-;;||ath;X;p1;titi
       """
    trouve = False
    cadres, xml = getcadre(regle, obj)
    groupe, oclasse = obj.ident
    nat = regle.params.att_entree.val
    if nat.startswith("#"):
        nat = nat[1:]
    classe = oclasse + "_" + nat
    # regle.reader.prepare_lecture_att(obj, "interne")
    for cadre in cadres:
        # print("traitement", cadre)
        for elem in cadre.iter(regle.recherche):
            # obj2 = regle.reader.getobj(niveau=groupe, classe=classe)
            obj2 = obj.dupplique()
            obj2.virtuel = False
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
            # print("xmlsplit traitement", obj2)
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
            trouve = True
    obj.attributs[regle.params.att_entree.val] = xml
    return trouve


def h_xmledit(regle):
    """helper edition"""
    h_xmlextract(regle)
    if regle.params.pattern == 1:
        regle.reselect = re.compile(regle.params.att_sortie.val)
    # regle.reader = regle.stock_param.getreader("interne", regle)
    regle.changeschema = False


def f_xmledit(regle, obj):
    """#aide||modification en place d elements xml
   #pattern1||re;re;A;xmledit;C;?C||sortie
 #aide_spec1||remplacement de texte
#parametres1||expression de sortie;selection;attribut xml;xmledit;tag a modifier;groupe de recherche
   #pattern2||;C;A;xmledit;A.C;?C||sortie
 #aide_spec2||remplacement ou ajout d un tag
#parametres2||;valeur;attribut xml;xmledit;tag a modifier.parametre;groupe de recherche
   #pattern3||;[A];A;xmledit;A.C;?C||sortie
 #aide_spec3||remplacement ou ajout d un tags
#parametres3||;attribut contenant la valeur;attribut xml;xmledit;tag a modifier.parametre;groupe de recherche
   #pattern4||?=\\*;H;A;xmledit;C;?C||sortie
 #aide_spec4||remplacement ou ajout d un ensemble de tags * conserve la valeur
#parametres4||* : remplacement total;attribut hstore contenant clefs/valeurs;attribut xml;xmledit;tag a modifier;groupe de recherche
   #pattern5||;L;A;xmledit;C;?C||sortie
 #aide_spec5||suppression d un ensemble de tags
#parametres5||;liste de clefs a supprimer;attribut xml;xmledit;tag a modifier;groupe de recherche
      #test1||obj||^V4;<g><pp p1="toto" p2="titi">essai</pp></g>;;set||^ss;xx;V4;xmledit;pp;||^XX;;V4;xmlextract;pp._T;||atv;XX;exxai
      #test2||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^*;;V4;xmledit;pp;||atv;p2;titi
      #test3||obj||^V4;<g><pp p1="toto" p2="titi"/></g>;;set||^XX;;V4;xmlextract;pp.p1;||atv;XX;toto
       """
    cadres, xml = getcadre(regle, obj)
    groupe, oclasse = obj.ident
    nat = regle.params.att_entree.val
    if nat.startswith("#"):
        nat = nat[1:]
    classe = oclasse + "_" + nat
    # regle.reader.prepare_lecture_att(obj, "interne")
    for cadre in cadres:
        # print("traitement", cadre)
        for elem in cadre.iter(regle.recherche):
            if regle.params.pattern == "1":  # regex sur texte
                contenu = elem.text
                contenu = re.sub(
                    regle.params.att_sortie.val, regle.params.val_entree.val, contenu
                )
                elem.text = contenu
            elif regle.params.pattern == "2":
                elem.set(regle.item, regle.params.val_entree.val)
            elif regle.params.pattern == "3":
                vals = obj.gethdict(regle.params.val_entree.val)
                for i, j in vals.items():
                    elem.set(i, j)


def f_xmlload(regle, obj):
    """#aide||lecture d un fichier xml dans un attribut
   #pattern1||A;?;?A;xml_load;;;
#parametres1||attribut de sortie;defaut;attribut contenant le nom de fichier;
    """
    nom = regle.getval_entree(obj)
    # print("xmlload traitement ", nom)

    obj.attributs[regle.params.att_sortie.val] = "".join(
        open(nom, "r", encoding="utf-8").readlines()
    )


def f_xmlsave(regle, obj):
    """#aide||stockage dans un fichier d un xml contenu dans un attribut
   #pattern1||A;?C;A;xml_save;?C;?C;
#parametres1||nom fichier;;attribut contenant le xml;;nom du rep
    """
    sortie = obj.attributs.get(regle.params.att_sortie.val)
    rep = regle.params.cmp1.getval(obj)
    if rep:
        sortie = os.path.join(rep, sortie)
    print("ecriture xml", sortie)
    open(sortie, "w", encoding="utf-8").write(regle.getval_entree(obj))
