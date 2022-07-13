# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 11:44:40 2017
module d'aide
@author: 89965
"""
# def get_help_texts(mapper):
#    '''analyse du code pour sortir les textes d'aide'''
#    return
import re


def decription_pattern(pattern, description, commun=None):
    """formatte la description des parametres d'entree"""
    if commun:
        communs = ";".join(commun).split(";")
    patdef = pattern.split(";")
    commande = patdef[3]
    patdesc = ";".join(description).split(";")
    retour = []
    for i, j in zip([i for i in patdef if i], patdesc):
        if i.startswith("=") or i.startswith("?="):
            # j = (j or i[1:]) + " (mot clef)"
            j = "(mot clef)"
            i = i[1:] if i.startswith("=") else i[2:]
        if re.match("#[1-9]", str(j)) and commun:
            n = int(j[1])
            j = communs[n - 1]
        if i == commande:
            j = "(commande)"
        retour.append("%+20s: %s" % (i, j + (" (optionnel)" if "?" in i else "")))

    # retour = [
    #     "%+20s: %s" % (i, j + (" (optionnel)" if "?" in i else ""))
    #     for i, j in zip([i for i in patdef if i], patdesc)
    # ]
    # print ('description',[i for i in patdef if i], patdesc,retour)
    return retour


def print_help(mapper, nom):
    """ affiche l'aide de base"""
    if nom:
        if nom in mapper.getmacrolist():
            print_macrohelp_detail(mapper, nom)
        elif nom in mapper.commandes:
            print_help_detail(mapper, nom)
        elif nom == "conditions":
            print_aide_conditions(mapper)
        elif nom == "macros":
            print_aide_macros(mapper)
        elif nom == "commandes":
            print_aide_commandes(mapper)
        elif nom == "formats":
            print_aide_formats(mapper)
        else:
            # essais de noms partiels
            recherche = nom.replace("*", "")
            recherche = recherche.replace("#", "")
            recherche = recherche.replace("-", "")
            trouve = False
            macrolist = []
            commandlist = []
            for n1 in mapper.getmacrolist():
                if recherche in n1:
                    macrolist.append(n1)
            for n1 in mapper.commandes:
                if recherche in n1:
                    commandlist.append(n1)
            if macrolist:
                trouve = True
                if len(macrolist) == 1:
                    print_macrohelp_detail(mapper, macrolist.pop())
                else:
                    print_aide_macros(mapper, liste=macrolist)
            if commandlist:
                trouve = True
                if len(commandlist) == 1:
                    print_help_detail(mapper, commandlist.pop())
                else:
                    print_aide_commandes(mapper, liste=commandlist)
            if not trouve:

                print("aide: commande inconnue", nom)
    else:
        print(
            "-------------------mapper version",
            mapper.version,
            "----------------------------",
        )
        print("                    aide générique")
        print("taper help commande pour l'aide détaillée sur une commande")
        print_aide_commandes(mapper)
        print_aide_conditions(mapper)
        print_aide_macros(mapper)


def print_macrohelp_detail(mapper, nom):
    """ affiche l aide detaillee d une macro"""
    macro = mapper.getmacro(nom)
    debug = mapper.getvar("debug")
    if not macro:
        print(" macro introuvable", nom)
        return False
    print("%-15s: macro    (%s)" % (nom, macro.file))
    print("%-15s: %s" % ("", macro.help[:-1]))
    if macro.help_detaillee:
        print()
        for i in macro.help_detaillee:
            print("%16s   %s" % ("", i[:-1]))
        print()

    if macro.vpos:
        print(
            "    parametres : %s"
            % (";".join(macro.vpos) if not macro.parametres_pos else "")
        )
        for i in macro.vpos:
            if i in macro.parametres_pos:
                print("%14s : %s" % (i, macro.parametres_pos[i]))

    if macro.vars_utilisees:
        print("     variables :")
        for i in macro.vars_utilisees:
            print("%14s : %s" % (i, macro.vars_utilisees[i]))

    if macro.apis:
        for nom, contenu in macro.apis.items():
            print("    webservice : %s -> retour %s" % (nom, contenu[1]))
    return True


def print_help_detail(mapper, nom):
    """ affiche l'aide de base"""
    debug = mapper.getvar("debug")
    if nom not in mapper.commandes:
        return False

    print("aide commande :", nom, debug, "\n")
    commande = mapper.getcommande(nom)
    print("  %s" % (commande.description.get("#aide", [""])[0]))
    for i in commande.description.get("#aide_spec", []):
        print("   %s" % (i))
    print("")
    if commande.description.get("#variables"):
        print("-------variables-------")
        for i in commande.description.get("#variables", [""]):
            nom, aide = (i.split(";") + [""])[:2]
            print("%-20s: %s" % (nom, aide))
    print("------- syntaxes acceptees ----------")
    print("")
    for variante in commande.subfonctions:
        pnum = variante.patternnum
        if variante.description:
            print(
                "%-20s: %s"
                % (
                    variante.pattern,
                    variante.description.get("#aide_spec" + pnum, [""])[0],
                )
            )
            for i in variante.description.get("#aide_spec" + pnum, [""])[1:]:
                print("%-20s: %s" % ("", i))
            for i in sorted(variante.description):
                # if "#aide_spec" + pnum in i and i != "#aide_spec":
                #     print("%-20s: %s" % ("", variante.description.get(i)[0]))
                if "#parametres" + pnum in i and i != "#parametres":
                    print(
                        "\n".join(
                            decription_pattern(
                                variante.pattern,
                                variante.description.get("#parametres" + pnum),
                                commun=variante.description.get("#parametres_c"),
                            )
                        )
                    )
            if variante.description.get("#dbparams"):
                print(
                    "parametres d acces base :", variante.description.get("#dbparams")
                )
            if variante.description.get("#parametres"):
                print(
                    "\n".join(
                        decription_pattern(
                            variante.pattern,
                            variante.description.get("#parametres"),
                        )
                    )
                )
            if variante.description.get("#variables" + pnum):
                print("-------variables specifiques------")
                for i in variante.description.get("#variables" + pnum, [""]):
                    nom, aide = (i.split(";") + [""])[:2]
                    print("%-20s: %s" % (nom, aide))
            if debug:
                print("pattern", variante.pattern)
                print("fonction", variante.work)
                print("helper", variante.helper)
                print("shelper", variante.shelper)
                print("fsorties", tuple(i for i in variante.fonctions_sortie))
            print()
    return True


def print_aide_commandes(mapper, liste=None):
    """affiche la aide des commandes """
    print("-----------------------------------------------------------------")
    print("---commandes standard--------------------------------------------")
    print("-----------------------------------------------------------------")
    for i in sorted(mapper.commandes):
        if liste and i not in liste:
            continue
        commande = mapper.getcommande(i)
        print("%-20s: %s" % (i, "\n".join(commande.description.get("#aide", []))))


def print_aide_selectprint_aide_conditionseurs(mapper, liste=None):
    """affiche l'aide des conditions """
    print("-----------------------------------------------------------------")
    print("---conditions-----------------------------------------------")
    print("-----------------------------------------------------------------")
    for i in sorted(mapper.conditions):
        if liste and i not in liste:
            continue
        sel = mapper.conditions[i]
        print("%-20s: %s" % (i, "\n".join(sel.description.get("#aide", []))))


def print_aide_macros(mapper, liste=None):
    """affiche l'aide des macros """
    print("-----------------------------------------------------------------")
    print("---macros internes-----------------------------------------------")
    print("-----------------------------------------------------------------")
    for nom_macro in sorted(mapper.getmacrolist()):
        if liste and nom_macro not in liste:
            continue
        print(
            "%-20s: %s"
            % (
                nom_macro,
                "\n".join(
                    [
                        i
                        for i in mapper.getmacro(nom_macro).help[:-1].split(";")
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
