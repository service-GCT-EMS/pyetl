# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 11:44:40 2017
module d'aide
@author: 89965
"""
# def get_help_texts(mapper):
#    '''analyse du code pour sortir les textes d'aide'''
#    return


def print_help(mapper, nom):
    """ affiche l'aide de base"""
    if nom:
        if nom in mapper.macros:
            macro = mapper.macros[nom]
            print("aide macro ", nom, "(", macro.file, ")")
            print("%-15s: %s" % (nom, macro.help[:-1]))
            if macro.vpos:
                print("parametres:", macro.vpos[0])
                for i in macro.vpos[1:]:
                    print("            %s" % (i))
            for i in macro.help_detaillee:
                print("%16s   %s" % ("", i[:-1]))

        elif nom in mapper.commandes:
            print("aide commande :", nom)
            commande = mapper.commandes[nom]
            print("%-20s: %s" % (commande.nom, commande.description.get("#aide")[0]))
            print("------- syntaxes acceptees ----------")
            for variante in commande.subfonctions:
                if variante.description:
                    print(
                        "%-20s: %s"
                        % (
                            variante.pattern,
                            variante.description.get("#aide_spec", [""])[0],
                        )
                    )
                    print("%s" % (variante.description.get("#parametres",[""])))
                    for i in variante.description.get("#aide_spec", [""])[1:]:
                        print("%-20s: %s" % ("", i))
                for i in sorted(variante.description):
                    pnum = variante.patternnum
                    if "#aide_spec" + pnum in i and i != "#aide_spec":
                        print("%-20s: %s" % ("", variante.description.get(i)[0]))

        elif nom == "selecteurs":
            print_aide_selecteurs(mapper)
        elif nom == "macros":
            print_aide_macros(mapper)
        elif nom == "commandes":
            print_aide_commandes(mapper)
        elif nom == "formats":
            print_aide_formats(mapper)
        elif nom:
            print("aide: commande inconnue")
    else:
        print(
            "-------------------mapper version",
            mapper.version,
            "----------------------------",
        )
        print("                    aide générique")
        print("taper help commande pour l'aide détaillée sur une commande")
        print_aide_commandes(mapper)
        print_aide_selecteurs(mapper)
        print_aide_macros(mapper)


#    exit(0)
def print_aide_commandes(mapper):
    """affiche la aide des commandes """
    print("-----------------------------------------------------------------")
    print("---commandes standard--------------------------------------------")
    print("-----------------------------------------------------------------")
    for i in sorted(mapper.commandes):
        commande = mapper.commandes[i]
        print(
            "%-20s: %s"
            % (commande.nom, "\n".join(commande.description.get("#aide", [])))
        )


def print_aide_selecteurs(mapper):
    """affiche l'aide des selecteurs """
    print("-----------------------------------------------------------------")
    print("---selecteurs-----------------------------------------------")
    print("-----------------------------------------------------------------")
    for i in sorted(mapper.selecteurs):
        sel = mapper.selecteurs[i]
        print("%-20s: %s" % (i, "\n".join(sel.description.get("#aide", []))))


def print_aide_macros(mapper):
    """affiche l'aide des macros """
    print("-----------------------------------------------------------------")
    print("---macros internes-----------------------------------------------")
    print("-----------------------------------------------------------------")
    for nom_macro in sorted(mapper.macros.keys()):
        print(
            "%-20s: %s"
            % (
                nom_macro,
                "\n".join(
                    [
                        i
                        for i in mapper.macros[nom_macro].help[:-1].split(";")
                        if i.strip()
                    ]
                ),
            )
        )


def print_aide_formats(mapper):
    """affiche l'aide des formats """
    print("-----------------------------------------------------------------")
    print("---formats connus------------------------------------------------")
    print("-----------------------------------------------------------------")
    print("nom-------------------lecture----ecriture------------------------")
    formats_connus = set(mapper.formats_connus_lecture.keys()) | set(
        mapper.formats_connus_ecriture.keys()
    )
    for nom_format in sorted(formats_connus):
        lect = "oui" if nom_format in mapper.formats_connus_lecture else "non"
        ecrit = "oui" if nom_format in mapper.formats_connus_ecriture else "non"
        print("%-20s:   %s    :   %s" % (nom_format, lect, ecrit))


def autodoc(mapper):
    """genere une documentation automatique du programme"""
    pass
