# commandes speciales
# gestionnaire de commandes speciales tests doc aide etc
import os


def commandes_speciales(mapper):
    """commandes speciales"""
    #        print("commandes speciales: ", self.fichier_regles)
    commandes_speciales = {"help", "autodoc", "autotest", "unittest", "formattest"}
    # on ne lit pas de regles mais on prends les commandes predefinies
    if mapper.fichier_regles is None:
        return
    liste_commandes = mapper.fichier_regles.split(",")
    commande, *pars = liste_commandes[0].split(":")
    commande = commande.replace("#", "")
    if commande not in commandes_speciales:
        return
    nom = mapper.getvar("_sortie")
    mapper.setvar("_sortie", "")
    mapper.setvar("_testmode", commande)
    if commande == "help":
        from .helpdef.helpmodule import print_help

        print_help(mapper, nom)

    elif commande == "autodoc":
        from .helpdef.docmodule import autodoc
        from distutils.dir_util import copy_tree

        print(" generation documentation ", nom)
        doc = autodoc(mapper)
        print("apres generation documentation ", doc.keys())
        build = mapper.getvar("_autobuild", "1") == "1"
        sourcedir = os.path.join(mapper.getvar("_progdir"), "../doc_pyetl")
        if nom:
            os.makedirs(nom, exist_ok=True)
            copy_tree(sourcedir, nom, update=1)
            sourcedir = nom
        autodocdir = os.path.join(sourcedir, "source/references/autodoc")
        os.makedirs(autodocdir, exist_ok=True)
        for nomdoc, contenu in doc.items():
            ref = os.path.join(autodocdir, nomdoc + "def.rst")
            print("ecriture doc", nomdoc, ref)
            with open(ref, "w", encoding="utf-8") as dest:
                dest.write("\n".join(contenu))
        if build:
            builder = os.path.join(sourcedir, "make") + " html "

            os.system(builder)
            print("generation format html dans", os.path.join(sourcedir, "build/html"))

    elif commande == "#autotest" or commande == "autotest":
        #            print("detecte autotest ", self.fichier_regles, self.posparm)
        from .tests.testmodule import full_autotest

        liste_regles = full_autotest(mapper, pars[0] if pars else nom)
        if liste_regles:
            mapper.fichier_regles = ""
            mapper.liste_regles = liste_regles
            # on a charge les commandes on neutralise l autotest

    elif commande == "#unittest" or commande == "unittest":
        from .tests.testmodule import unittests

        unittests(mapper, nom=nom, debug=mapper.getvar("debug"))

    elif commande == "#formattest" or commande == "formattest":
        from .tests.testmodule import formattests

        formattests(mapper, nom=nom, debug=mapper.getvar("debug"))

    mapper.done = True
