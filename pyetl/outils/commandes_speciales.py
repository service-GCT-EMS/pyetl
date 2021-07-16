# commandes speciales
# gestionnaire de commandes speciales tests doc aide etc
import os
from pyetl.ihm.lancements.ihm_ps import creihm

COMMANDES_SPECIALES = {
    "help",
    "autodoc",
    "autotest",
    "unittest",
    "formattest",
    "pack",
    "commandlist",
    "cache",
    "paramgroups",
    "genihm",
}


def is_special(commandes):
    "determine si une commande est speciale"
    if not commandes:
        return False
    c1 = commandes.split(";")
    commande, *pars = c1[0].split(":")
    commande = commande.replace("#", "")
    commande = commande.replace("-", "")
    # print("is_special", commande, commande in COMMANDES_SPECIALES)
    return commande in COMMANDES_SPECIALES


def gendoc(mapper, nom):
    from .helpdef.docmodule import autodoc
    from distutils.dir_util import copy_tree

    print(" generation documentation ", nom)
    doc = autodoc(mapper)
    print("apres generation documentation ", doc.keys())
    build = mapper.getvar("_autobuild", "1") == "1"
    sourcedir = os.path.join(
        mapper.getvar("_progdir"), "../pyetl_webapp/static/doc_pyetl"
    )
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
        builderhtml = os.path.join(sourcedir, "make") + " html "
        # builderpdf = os.path.join(sourcedir, "make") + " pdf "

        os.system(builderhtml)
        print("generation format html dans", os.path.join(sourcedir, "build/html"))
        # os.system(builderpdf)
        # print("generation format pdf dans", os.path.join(sourcedir, "build/pdf"))


def commandes_speciales(mapper, commandes, args):
    """commandes speciales"""
    #        print("commandes speciales: ", self.fichier_regles)

    # on ne lit pas de regles mais on prends les commandes predefinies
    if not commandes:
        return False
    c1 = commandes.split(";")
    commande, *pars = c1[0].split(":")
    commande = commande.replace("#", "")
    commande = commande.replace("-", "")
    # if mapper.fichier_regles is None:
    #     return
    # liste_commandes = mapper.fichier_regles.split(",")
    # commande, *pars = liste_commandes[0].split(":")
    # commande = commande.replace("#", "")
    # if commande not in COMMANDES_SPECIALES:
    #     return
    mapper.is_special = True
    mapper._traite_params(args)
    # nom = mapper.getvar("_sortie")
    nom = pars[0] if pars else (c1[1] if len(c1) > 1 else (args[0] if args else ""))
    # print ("commandes speciales",commandes, args)
    mapper.setvar("_sortie", "")
    mapper.setvar("_testmode", commande)
    if commande == "help":
        if not nom:
            import subprocess

            start = (
                'start /D "'
                + os.path.join(
                    mapper.getvar("_progdir"),
                    r"..\pyetl_webapp\static\doc_pyetl\build\html",
                )
                + '" index.html'
            )

            print("lancement ", start)
            fini = subprocess.run(start, shell=True)
        else:
            from .helpdef.helpmodule import print_help

            if nom == "*":
                nom = ""
            print_help(mapper, nom)

    elif commande == "autodoc":
        gendoc(mapper, nom)

    elif commande == "autotest":
        #            print("detecte autotest ", self.fichier_regles, self.posparm)
        from .tests.testmodule import full_autotest

        liste_regles = full_autotest(mapper, pars[0] if pars else nom)
        if liste_regles:
            mapper.fichier_regles = ""
            mapper.liste_regles = liste_regles
            # on a charge les commandes on neutralise l autotest

    elif commande == "unittest":
        from .tests.testmodule import unittests

        unittests(mapper, nom=nom, debug=mapper.getvar("debug"))

    elif commande == "#formattest" or commande == "formattest":
        from .tests.testmodule import formattests

        formattests(mapper, nom=nom, debug=mapper.getvar("debug"))

    elif commande == "pack":
        # import magic
        from . import pack

        place = os.path.dirname(mapper.getvar("_progdir"))
        print("preparation version", mapper.version, place)
        nv = "_" + mapper.version.replace(" (build:", ".").replace(")", "")
        gendoc(mapper, "")
        pack.zipall(place, nv)
        newb = pack.update_build(build="BUILD =", file="vglobales.py", orig=place)
        print("modification build", mapper.version, "->(build", newb, ")")

    elif commande == "commandlist":
        from . import pack

        pack.commandlist(mapper)

    elif commande == "cache":
        from . import pack

        pack.cache(mapper)

    elif commande == "paramgroups":
        """ affichage des groupes de parametres connus"""
        if nom:
            key = mapper.getvar("key")
            decode = key == mapper.getvar("masterkey")
            if nom in mapper.site_params:
                print("groupe", nom)
                for i, j in mapper.site_params.get(nom):
                    if i == "passwd" and not decode:
                        j = "***"
                    print(i, "->", j)
            else:
                print("groupe inconnu", nom)
        else:
            print("groupes connus:")
            print(sorted(mapper.site_params.keys()))

    elif commande == "genihm":
        """generation d ihm"""
        from ..ihm.lancements.ihm_ps import creihm

        creihm(nom)

    mapper.done = True
