# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:20:44 2015

@author: Claude unger

compilateur de regles : cree les enchainements de regles

"""


def _affiche_debug(regles, debug):
    """affichages de debug"""
    for regle in regles:
        if debug or regle.debug:
            regle.affiche_debug()
            print("fonction", regle.f_init)
            liens_num = regle.branchements.liens_num()
            liens_pos = regle.branchements.liens_pos()
            print(
                "   compile: liens",
                str(regle.index),
                "(",
                regle.numero,
                ")",
                "-->",
                [(i, liens_pos[i], liens_num[i]) for i in sorted(liens_num)],
            )
            print(
                "flags",
                "final" if regle.final else "",
                "nonext" if regle.nonext else "",
            )
            if "+" in regle.v_nommees["debug"]:
                print(
                    "\n".join(
                        [
                            str((i, regle.branchements.brch[i]))
                            for i in sorted(regle.branchements.brch)
                        ]
                    )
                )
            if regle.selstd is not None:
                print(
                    "   compile: select",
                    regle.selstd.__name__ if regle.selstd else "None",
                    ("sel1:", regle.sel1.fonction.__name__)
                    if hasattr(regle, "sel1") and regle.sel1
                    else "",
                    ("sel2:", regle.sel2.fonction.__name__)
                    if hasattr(regle, "sel2") and regle.sel2
                    else "",
                )


def _branche(regle1, regle2):
    """branche une regle a la place de l'autre"""
    for brc in regle2.branchements.brch:
        regle1.branchements.brch[brc] = regle2.branchements.brch[brc]


def _finalise(regle, debug):
    """ gere les modifieurs de comportement"""
    if regle.store:  # regle demandant un stockage de l'ensemble des entrees
        regle.setstore()
    if regle.final:
        regle.branchements.brch["ok"] = None
    if regle.filter:
        regle.branchements.brch["sinon"] = None
        regle.branchements.brch["fail"] = None
        if debug:
            print("regle filtrante ", regle.ligne)
    if regle.call:  # c est un appel de procedure / macro
        if not regle.liste_regles:
            raise SyntaxError("macro non definie:" + repr(regle))
        for brc in regle.branchements.brch:
            regle.liste_regles[-1].branchements.brch[brc] = regle.branchements.brch[brc]
        for rmacro in regle.liste_regles:
            if rmacro._return:
                #                print ('gestionnaire de retour', rmacro, '->' , regle)
                _branche(rmacro, regle)
        regle.branchements.brch["ok"] = regle.liste_regles[0]


def _gestion_branchements(regles, position, debug):
    """ positionne les branchements entre les regles """
    niveau_courant = regles[position + 1].niveau
    regle = regles[position]
    if debug:
        print(
            "compil : regles liees niveaux: ",
            position,
            regles[position].niveau,
            regles[position + 1].niveau,
        )
    if regles[position + 1].enchainement == "ok":
        regle.branchements.brch["ok"] = regles[position + 1]
    if debug:
        print("calcul enchainements ", regle)
    j = 0
    for j in range(position + 1, len(regles)):
        if regles[j].niveau > niveau_courant:
            continue  # niveaux superieurs on ne s'en occupe pas
        if regles[j].niveau < niveau_courant:
            regle.branchements.setclink(regles[j])
            break  # on a atteint un niveau inferieur : c est fini
        #        regle.branchements.brch.update({i:regles[j] for i in regles[j].enchainements
        #                                 if regles[j].enchainement == i})
        if debug:
            print("examen", regles[j], regles[j].enchainement)
        for i in regle.branchements.brch:

            if i != "ok" and regles[j].enchainement == i:
                regle.branchements.brch[i] = regles[j]
    if debug:
        print("recherche", j, sorted(regle.branchements.liens_num()))


def _valide_blocs(regles, position, bloc):
    """ validation de la structure en blocs """
    bloc_courant = bloc
    regle = regles[position]
    #    print("validation blocs", bloc)
    for regle_courante in regles[position + 1 :]:
        if regle_courante.mode == "fin_bloc":
            if bloc == bloc_courant:
                regle.branchements.brch["sinon"] = regles[regle_courante.index + 1]
                break
            else:
                bloc_courant -= 1
        if regle_courante.mode == "bloc":
            bloc_courant += 1
    if not regle.branchements.brch["sinon"]:
        print("cmp:erreur structure de blocs:", regle.ligne, bloc)
        return False


def _gestion_parallel(regles, position):
    """ validation de la structure parrallel / join """
    regle = regles[position]
    if regle.stock_param.worker:
        return
    for regle_courante in regles[position + 1 :]:
        if regle_courante.mode == "end_parallel":
            regle.branchements.brch["ok"] = regles[regle_courante.index + 1]
            break
        if regle_courante.mode == "parallel":
            print("cmp:impossible d imbriquer les appels parallele:", regle.ligne)
        return False


def propage_liens(regles, start):
    """propage les liens pour la gestion des indentations"""
    niveau_courant = regles[start + 1].niveau
    for j in range(start + 1, len(regles)):
        if regles[j].niveau < niveau_courant:
            #                        setclink(regle, j)
            regles[start].branchements.setclink(regles[j])
            break


def nextregle(regles, niveau):
    """applatissage recursif de la liste de regles"""
    for regle in regles:
        regle.niveau = niveau + regle.niveau
        yield regle
        if regle.call:
            # print("appel nextregle", niveau, regle)
            yield from nextregle(regle.liste_regles, regle.niveau)


def compile_regles(mapper, regles, debug=0, parent=None):
    """ prepare l'enchainement des regles sous forme de liens entre regles """
    # print("compile regles", parent, regles)
    if not regles:
        print("pas de regles a compiler", parent, parent.valide if parent else "")
        raise
        raise EOFError("pas de regles a compiler")
    # print ('compilateur:gestion sortie',mapper.getvar("F_sortie"))
    if not parent:
        if mapper.getvar("sans_sortie"):
            regle_sortir = mapper.interpreteur(
                ";;;;;;;pass;;;;;pas de sortie", "", 99999
            )
        else:
            regle_sortir = mapper.interpreteur(
                ";;;;;;;sortir;"
                + mapper.getvar("F_sortie")
                + ";"
                + mapper.getvar("nom_sortie")
                + ";;;sortie_defaut",
                "",
                99999,
                prec=regles[-1],
            )
        regle_sortir.final = True

    # print ('liste_regles',mapper.idpyetl,regles)
    else:  # cest un call il faut revenir
        # print("ajout retour call")
        regle_sortir = mapper.interpreteur(";;;;;;;pass;;;;;retour", "", 99000)
    regle_sortir.index = len(regles)
    regles.append(regle_sortir)  # on mets la regle de sortie pour finir
    bloc = 0
    for i in range(len(regles) - 1):
        regle = regles[i]
        if regles[i + 1].niveau > regle.niveau:  # ca se complique les regles sont liees
            _gestion_branchements(regles, i, debug)
        elif regles[i + 1].niveau == regle.niveau:
            if regles[i + 1].enchainement and regles[i + 1].enchainement != "ok":
                propage_liens(regles, i)
            elif regles[i + 1].nonext:  # c est une suite d'acces
                for j in range(i + 1, len(regles)):
                    if not regles[j].nonext:
                        regle.branchements.brch["next"] = regles[j]
                        regle.branchements.brch["gen"] = regles[j]
                        break
        regle.branchements.setclink(regles[i + 1])
        regle.suivante = True
        if regle.mode == "bloc":
            bloc += 1
            _valide_blocs(regles, i, bloc)

        if regle.mode == "fin_bloc":  # gestion de la structure
            bloc -= 1

        if regle.mode == "parallel" and not regle.stock_param.worker:
            _gestion_parallel(regles, i)
        if regle.mode == "return":
            if parent:
                # print("mode return", parent.branchements)
                parent.branchements.brch["end"] = None  # la sortie
                regle.branchements = parent.branchements
            else:
                raise SyntaxError("return en dehors d une macro")
        if regle.mode == "call":
            compile_regles(mapper, regle.liste_regles, debug=debug, parent=regle)
            # print(
            #     "compile regle call\n", "\n".join((repr(i) for i in regle.liste_regles))
            # )
            regle.moteur.setregles(regle.liste_regles)
        _finalise(regle, debug)
    # if liste_regles is None:  # applatissement des regles
    #     # print("applatissemeent")
    #     nliste = []
    #     for i in nextregle(regles, 0):
    #         i.index = len(nliste)
    #         nliste.append(i)
    #         # print("ajout regle", i.niveau, i)
    #     regles.clear()
    #     regles.extend(list(nliste))
    # print("fin compil\n", "\n".join(map(repr, regles)))
    _affiche_debug(regles, debug)
    return True
