# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 11:44:40 2017
module d'aide
@author: 89965
"""
# def get_help_texts(mapper):
#    '''analyse du code pour sortir les textes d'aide'''
#    return


def decription_pattern(pattern, description):
    """formatte la description des parametres d'entree"""
    patdef = pattern.split(";")
    patdesc = ";".join(description).split(";")
    retour = [
        "%+20s: %s" % (i, j + (" (optionnel)" if "?" in i else ""))
        for i, j in zip([i for i in patdef if i], patdesc)
    ]
    # print ('description',[i for i in patdef if i], patdesc,retour)
    return retour


def print_help(mapper, nom):
    """ affiche l'aide de base"""
    if nom:
        macro = mapper.getmacro(nom)
        debug = mapper.getvar("debug")
        if macro:
            print("aide macro ", nom, "(", macro.file, ")")
            print("%-15s: %s" % (nom, macro.help[:-1]))
            if macro.vpos:
                print("parametres:", macro.vpos[0])
                desc_pp = ";".join(macro.parametres_pos).split(";")
                if desc_pp:
                    for i, j in zip(macro.vpos[1:], desc_pp):
                        print("            %10s :%s" % (i, j))
                else:
                    for i in zip(macro.vpos[1:], desc_pp):
                        print("            %s" % (i))
            for i in macro.help_detaillee:
                print("%16s   %s" % ("", i[:-1]))
            if macro.vars_utilisees:
                print("variables utilisees")
                for i in macro.vars_utilisees:
                    print("%16s   %s" % ("", i[:-1]))

        elif nom in mapper.commandes:
            print("aide commande :", nom, debug, "\n")
            commande = mapper.commandes[nom]
            print("  %s" % (commande.description.get("#aide", [""])[0]))
            for i in commande.description.get("#aide_spec", []):
                print("   %s" % (i))
            print("")
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
                                    )
                                )
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
                    if variante.description.get("#variables"):
                        for i in variante.description.get("#variables", [""]):
                            print("%-20s: %s" % ("", i))
                            # print("%s" % "\n".join(variante.description.get("#parametres")))
                    if debug:
                        print("pattern", variante.pattern)
                        print("fonction", variante.work)
                        print("helper", variante.helper)
                        print("shelper", variante.shelper)
                        print("fsorties", tuple(i for i in variante.fonctions_sortie))

        elif nom == "selecteurs":
            print_aide_selecteurs(mapper)
        elif nom == "macros":
            print_aide_macros(mapper)
        elif nom == "commandes":
            print_aide_commandes(mapper)
        elif nom == "formats":
            print_aide_formats(mapper)
        elif nom:
            # essais de noms partiels
            trouve = False
            for n1 in mapper.getmacrolist():
                if nom in n1:
                    trouve = True
                    print_help(mapper, n1)
            for n1 in mapper.commandes:
                if nom in n1:
                    trouve = True
                    print_help(mapper, n1)
            if not trouve:
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
    for nom_macro in sorted(mapper.getmacrolist()):
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


# =================================================================================
# ====================generation automatique de la doc sphynx======================
# =================================================================================


def souligne(doc, signe):
    doc.append(signe * len(doc[-1]))
    doc.append("")


def indent(val, n):

    if isinstance(val, list):
        return ["   " * n + i for i in val]
    return "   " * n + val


def delim_tableau(tailles, signe):
    ligne = "+" + "+".join([signe * i for i in tailles]) + "+"
    return ligne


def center(taille, contenu):
    return contenu + " " * (taille - len(contenu))


def contenu_tableau(tailles, vals):
    return "|" + "|".join([center(l, i) for l, i, in zip(tailles, vals)]) + "|"


def quote_etoile(ligne):
    if isinstance(ligne, list):
        return [i.replace(" *", r" \*") for i in ligne]
    return ligne.replace(" *", r" \*")


def tableau(pattern):
    if isinstance(pattern, str):
        pattern = [pattern]
    tailles = [0, 0, 0, 0, 0, 0]
    tmax = 0
    lignes = []
    for ligne in pattern:
        if ligne.startswith(":"):
            tmax = max(tmax, len(ligne))
            lignes.append([" *" + ligne[1:] + "*"])
            continue
        vals = ligne.split(";")
        tailles = [max(len(i), j) for i, j in zip(vals, tailles)]
        lignes.append(vals)
    tmax = tmax + 3
    entetes = ["sortie", "defaut", "entree", "commande", "param1", "param2  "]
    tailles = [max(i, len(j)) for i, j in zip(tailles, entetes)]
    sommetaille = sum(tailles) + 5
    while sommetaille < tmax:
        tailles = [i + 1 for i in tailles]
        sommetaille = sum(tailles) + 5
    retour = [delim_tableau(tailles, "-")]
    retour.append(contenu_tableau(tailles, entetes))
    retour.append(delim_tableau(tailles, "="))
    prec = 0
    for vals in lignes:
        if prec == 6 or (prec == 1 and len(vals) != prec):
            retour.append(delim_tableau(tailles, "-"))

        retour.append(
            contenu_tableau(tailles if len(vals) > 1 else [sommetaille], vals)
        )
        prec = len(vals)
        # print(" taille prec", prec, vals)
    retour.append(delim_tableau(tailles, "-"))
    retour.append("")
    return retour


def doc_pattern(pattern, description):
    """formatte la description des parametres d'entree"""
    patdef = pattern.split(";")
    patdesc = ";".join(description).split(";")
    retour = []
    for i, j in zip([i for i in patdef if i], patdesc):
        retour.append(indent(i, 2))
        retour.append(indent(j + (" (optionnel)" if "?" in i else ""), 3))
    retour.append("")
    return retour


def docgen(mapper, nom):
    """genere la doc sphinx d une commande"""
    doc = [nom, "-" * len(nom), ""]
    commande = mapper.commandes[nom]
    aide = commande.description.get("#aide", "")
    aide_spec = commande.description.get("#aide_spec", "")
    doc.extend(indent(quote_etoile(aide), 1))
    doc.append("")
    doc.extend(indent(quote_etoile(aide_spec), 1) if aide_spec else [])
    doc.append("")
    doc.append("**syntaxes acceptees**")
    doc.append("")
    patterns = []
    for v in sorted(commande.subfonctions, key=lambda x: x.patternnum):
        pattern = v.pattern
        vals = pattern.split(";")
        if len(vals) < 6:
            vals = vals + [""] * (6 - len(vals))
        vals = vals[:6]
        pattern = ";".join(vals)
        patterns.append(pattern)
        aides = v.description.get("#aide_spec" + v.patternnum)
        if not aides:
            continue
        for i in aides:
            explication = ":" + i
            patterns.append(explication)

    doc.extend(tableau(patterns))
    for variante in commande.subfonctions:
        if variante.description:
            # doc.extend(tableau(variante.pattern))
            # doc.append(indent(variante.pattern,1))
            # aide = variante.description.get("#aide_spec")
            for i in sorted(variante.description):
                pnum = variante.patternnum
                if ("#aide_spec" + pnum) in i and i != "#aide_spec":
                    doc.append(variante.description.get(i)[0])
                if ("#parametres" + pnum) in i and i != "#parametres":
                    doc.extend(
                        doc_pattern(
                            variante.pattern,
                            variante.description.get("#parametres" + pnum),
                        )
                    )
    if commande.description.get("#parametres"):
        doc.extend(
            doc_pattern(commande.pattern, commande.description.get("#parametres"))
        )
    if commande.description.get("#variables"):
        for i in commande.description.get("#variables"):
            doc.append(i)
            # print("%s" % "\n".join(variante.description.get("#parametres")))
    doc.append("")
    return doc


def doc_commandes(mapper):
    """genere la doc sphinx des commandes"""
    doc = ["commandes"]
    souligne(doc, "=")
    for nom in sorted(mapper.commandes):
        doc.append("")
        doc.extend(docgen(mapper, nom))
    return doc


def autodoc(mapper):
    doc = []
    doc.extend(doc_commandes(mapper))
    return doc
