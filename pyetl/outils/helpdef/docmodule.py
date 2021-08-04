# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 11:44:40 2017
module d'aide
@author: 89965
# =================================================================================
# ====================generation automatique de la doc sphynx======================
# =================================================================================
"""


from pyetl.formats.generic_io import DATABASES, READERS, WRITERS, getdb

# from pyetl.moteur.fonctions import loadmodules as load_commands
# from pyetl.formats.fichiers import loadformats
# from pyetl.formats.db import loaddbmodules
from pyetl.outils.pack import cache


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
        if i.startswith("="):
            j = (j or i[1:]) + " (mot_clef)"
        val = " :  ".join((i, j + (" (optionnel)" if "?" in i else "")))
        retour.append(indent(val, 1))
        # retour.append(indent(i, 2))
        # retour.append(indent(j + (" (optionnel)" if "?" in i else ""), 3))
    retour.append("")
    return retour


def docgen(mapper, nom, nommodule):
    """genere la doc sphinx d une commande"""
    doc = [".. index::"]
    doc.append("  double: " + nommodule + ";" + nom)
    doc.append("")
    doc.append(nom)
    souligne(doc, ".")
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
        vals = ["\\" + i if i.startswith("|") else i for i in vals]
        pattern = ";".join(vals)
        patterns.append(pattern)
        aides = v.description.get("#aide_spec" + v.patternnum)
        if not aides:
            continue
        for i in aides:
            explication = ":" + i
            patterns.append(explication)

    doc.extend(tableau(patterns))
    doc.append("")
    for variante in commande.subfonctions:
        if variante.description:
            # doc.extend(tableau(variante.pattern))
            # doc.append(indent(variante.pattern,1))
            # aide = variante.description.get("#aide_spec")
            for i in sorted(variante.description):
                pnum = variante.patternnum
                # if ("#aide_spec" + pnum) in i and i != "#aide_spec":
                #     doc.append(variante.description.get(i)[0])
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
    # load_commands(force=True)
    doc = ["reference des commandes"]
    souligne(doc, "=")
    # print(" modules de commande", mapper.modules)
    for nommodule in sorted(mapper.modules):
        print("traitement module", nommodule, "->", mapper.modules[nommodule].titre)
        # print("commandes", mapper.modules[nommodule].commandes)
        if mapper.modules[nommodule].commandes:
            doc.append(mapper.modules[nommodule].titre)
            souligne(doc, "-")
            doc.append(mapper.modules[nommodule].titre)
            for nom in sorted(mapper.modules[nommodule].commandes):
                doc.append("")
                doc.extend(docgen(mapper, nom, nommodule))
    return doc


def doc_macros(mapper):
    """genere la doc sphinx des commandes"""
    doc = ["reference macros"]
    souligne(doc, "-")
    ftab = "%-55s  %s"
    doc.append(ftab % ("=" * 53, "========"))
    doc.append(
        ftab % ("                           macro                       ", "fonction")
    )
    doc.append(ftab % ("=" * 53, "========"))
    for nom_macro in sorted(mapper.getmacrolist()):
        macro = mapper.getmacro(nom_macro)
        appel = nom_macro + " " + ";".join(macro.vpos)
        doc.append(
            ftab
            % (
                appel,
                macro.help,
            ),
        )

    doc.append(ftab % ("=" * 53, "========"))

    doc.append("")
    doc.append("")
    doc.append("")
    return doc


def detail_macro(mapper):
    """genere les detail de description de macro"""
    doc = ["detail macros"]
    souligne(doc, "-")

    for nom_macro in sorted(mapper.getmacrolist()):
        macro = mapper.getmacro(nom_macro)
        help = macro.help
        help_detaillee = macro.help_detaillee
        parametres = macro.vpos
        defpars = macro.parametres_pos
        variables = macro.vars_utilisees
        api = macro.apiname
        apiformat = macro.retour
        doc.append("")
        doc.append(nom_macro)
        souligne(doc, ".")
        doc.append("")
        if help:
            doc.append(help)
            doc.append("")
        if help_detaillee:
            doc.extend([" * " + i for i in help_detaillee])
            doc.append("")
        if parametres:
            doc.append("parametres positionnels")
            doc.append("")
            for nom in parametres:
                defp = defpars.get(nom, "")
                doc.append("* " + nom + ":" + defp)
            doc.append("")
        if variables:
            doc.append("variables utilisées")
            doc.append("")
            for nomp, defp in variables.items():
                doc.append("* " + nomp + ":" + defp)
            doc.append("")
        if api:
            doc.append("macro utilisabe en service web")
            doc.append("")
            doc.append("* url          : ws/" + api)
            doc.append("* format retour:" + apiformat)
            doc.append("")
        doc.append("")
    # print("detail macros", doc)
    return doc


def rwheader(doc, titre):
    """genere les entetes du tableau"""
    doc.append(titre)
    souligne(doc, "-")
    doc.append(
        "%-25s   %10s    %10s" % ("====================", "==========", "===========")
    )
    doc.append("%-25s   %10s    %10s" % ("format", "lecture", "ecriture"))
    doc.append(
        "%-25s   %10s    %10s" % ("====================", "==========", "===========")
    )


def doc_formats(mapper):
    """genere la doc sphinx des commandes"""
    # loadformats(force=True)
    doc = []
    rwheader(doc, "reference formats")

    formats_connus = set(mapper.formats_connus_lecture.keys()) | set(
        mapper.formats_connus_ecriture.keys()
    )
    for nom_format in sorted(formats_connus):
        lect = "oui" if nom_format in mapper.formats_connus_lecture else "non"
        ecrit = "oui" if nom_format in mapper.formats_connus_ecriture else "non"
        doc.append("%-25s   %10s    %10s" % (nom_format, lect, ecrit))
    doc.append(
        "%-25s   %10s    %10s" % ("====================", "==========", "===========")
    )
    doc.append("")
    rwheader(doc, "reference bases de donnees")
    for nombase in sorted(DATABASES):
        doc.append("%-25s   %10s    %10s" % (nombase, "oui", "oui"))
    doc.append(
        "%-25s   %10s    %10s" % ("====================", "==========", "===========")
    )
    doc.append("")

    # loaddbmodules(force=True)
    for nombase in sorted(DATABASES):
        doc.append(nombase)
        souligne(doc, ".")
        doc.append(getdb(nombase).doc)
    doc.append("")

    # doc detaillee des formats
    for nom_format in sorted(formats_connus):
        doc.append("")
        doc.append("format %s" % (nom_format,))
        souligne(doc, ".")
        doc.append("")
        if nom_format in mapper.formats_connus_lecture:
            readfunc = READERS[nom_format].reader
            if readfunc.__doc__:
                doc.append(readfunc.__doc__)
        doc.append("")
        if nom_format in mapper.formats_connus_ecriture:
            wfunc = WRITERS[nom_format].writer
            if not wfunc:
                continue
            if wfunc.__doc__:
                doc.append(wfunc.__doc__)

    return doc


def doc_select(mapper):
    """genere la doc sphinx des selecteurs"""
    """affiche l'aide des selecteurs """
    doc = ["reference sélecteurs"]
    souligne(doc, "-")

    result = dict()
    for i in mapper.selecteurs:
        sel = mapper.selecteurs[i]
        clef = sel.work.__name__
        if clef in result:
            result[clef]["patterns"].append(i)
        else:
            result[clef] = {"patterns": [i], "aide": sel.description.get("#aide", [])}

    for i in sorted(result):
        sel = result[i]
        doc.extend(["   * " + j for j in sel["patterns"]])
        doc.extend(["       - " + j for j in sel.get("aide", [])])
        doc.append("")
    return doc


def autodoc(mapper):
    cache(mapper)
    doc = dict()
    doc["commande"] = doc_commandes(mapper)
    doc["macro"] = doc_macros(mapper) + detail_macro(mapper)
    doc["format"] = doc_formats(mapper)
    doc["select"] = doc_select(mapper)
    return doc
