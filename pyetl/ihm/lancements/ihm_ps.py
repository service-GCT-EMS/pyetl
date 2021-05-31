# -*- coding: utf-8 -*-
"""creation d ihm poweshell a partir d un fichier de definition"""
import itertools
import os


class Ihm(object):
    def __init__(self, nom=None, interpreteur=None):
        self.nom = nom if nom else "ihm"
        self.id = "ihm"
        self.main = None
        self.elements = []

    @property
    def colonnes(self):
        return self.main.colonnes

    @property
    def lignes(self):
        return self.main.lignes

    def genps(self):
        """genere le code ps pour l´ihm"""
        nbcols = self.colonnes
        nblignes = self.lignes
        self.lcols = int((self.main.largeur - 40) / nbcols)

        code = [
            "# genere automatiquement par le generateur d ihm de mapper",
            "",
            "",
            "Add-Type -AssemblyName System.Windows.Forms",
            "[System.Windows.Forms.Application]::EnableVisualStyles()",
            "$font=New-Object System.Drawing.Font('Microsoft Sans Serif',10)",
            "$startx=20",
        ]
        code.extend(self.main.genps())
        for el in self.elements:
            code.extend(el.genps())
        return code

    def struct(self):
        """affiche la structure de l ihm avec les imbrications"""
        print("ihm ", self.nom)
        self.main.struct(1)
        for el in self.elements:
            el.struct(1)


class Fenetre(object):
    _ido = itertools.count(1)

    def __init__(self, parent, titre, largeur=None) -> None:
        self.id = "Form" + str(next(self._ido))
        self.parent = parent
        self.largeur = largeur
        self.hauteur = 0
        self.messages = None
        self.titre = titre
        self.elements = []
        self.statusbar = None

    @property
    def colonnes(self):
        return max((i.colonne for i in self.elements))

    @property
    def lignes(self):
        maxlin = 0
        cour = 0
        for i in self.elements:
            if i.ligne == "+":
                cour += 1
                i.ligne = cour
            elif isinstance(i.ligne, int) or i.ligne.isnumeric():
                cour = int(i.ligne)
                i.ligne = cour
            elif i.ligne == "=":
                i.ligne = cour
        maxlin = max(maxlin, cour)
        if self.statusbar:
            maxlin += 1
        return maxlin

    def genps(self):
        self.lcols = int((self.largeur - 40) / self.colonnes)
        vref = "$" + self.id
        code = [
            vref + " = New-Object system.Windows.Forms.Form",
            vref
            + ".ClientSize  = New-Object System.Drawing.Point(%d,%d)"
            % (self.largeur, self.lignes * 40),
            vref + '.text  = "%s"' % (self.titre,),
            vref + ".TopMost  = $false",
            "",
        ]
        vlist = []
        for el in self.elements:
            vslist, vbcode = el.genps()
            code.extend(vbcode)
            vlist.extend(vslist)

        if self.statusbar:
            statusbar = Label(self, self.lignes, 1, "", id="statusbar")
            vslist, scode = statusbar.genps()
            code.extend(scode)
            vlist.extend(vslist)

        code.append(vref + ".controls.AddRange(@(" + ",".join(vlist) + "))")
        code.append(vref + ".ShowDialog()")
        return code

    def struct(self, niveau):
        """affiche la structure de l ihm avec les imbrications"""
        print(
            "    " * niveau, self.id, "fenetre ", self.titre, "(", self.parent.id, ")"
        )
        for el in self.elements:
            el.struct(niveau + 1)


class Fileselect(object):
    _ido = itertools.count(1)

    def __init__(self, parent, lin, col, titre, selecteur, variable):
        self.id = "Fsel" + str(next(self._ido))
        self.parent = parent
        self.ligne = lin
        self.colonne = int(col)
        self.titre = titre
        self.selecteur = selecteur
        self.variable = variable

    def genps(self):
        lab = "$" + self.id + "L"
        tb = "$" + self.id + "TB"
        fbr = "$" + self.id + "FBR"
        fbt = "$" + self.id + "FBT"
        px = self.colonne * self.parent.lcols
        py = self.ligne * 50
        self.ref = tb
        code = [
            lab + " = New-Object system.Windows.Forms.Label",
            lab + '.text = "%s"' % (self.titre,),
            lab + ".AutoSize = $true",
            lab + ".Font = $font",
            lab + ".location = New-Object System.Drawing.Point(%d,%d)" % (px, py),
            "",
            "",
            tb + " = New-Object system.Windows.Forms.TextBox",
            tb + ".multiline = $false",
            tb + ".width = 300",
            tb + ".height = 20",
            tb + ".location = New-Object System.Drawing.Point(%d,%d)" % (px, py + 40),
            tb + ".Font = $font",
            tb + ".AllowDrop = $true",
            "",
            "",
            fbr + " = New-Object System.Windows.Forms.OpenFileDialog",
            fbr + '.Title = "%s"' % (self.titre,),
            fbr + '.Filter = "%s"' % (self.selecteur,),
            "",
            "",
            fbt + " = New-Object system.Windows.Forms.Button",
            fbt + '.text = "f"',
            fbt + ".width = 24",
            fbt + ".height = 24",
            fbt
            + ".location = New-Object System.Drawing.Point(%d,%d)"
            % (px + 300, py + 40),
            fbt + ".Font = $font",
            "#onclick",
            fbt + ".Add_Click(",
            "   {",
            '       $sd="."',
            "       if (%s.Text -ne '') { $sd=Split-Path -Path %s.Text }" % (tb, tb),
            "       %s.InitialDirectory=$sd" % (fbr,),
            "       $null = %s.ShowDialog()" % (fbr,),
            "       %s.Update()" % (tb,),
            "   }",
            "   )",
        ]
        return [lab, tb, fbr, fbt], code

    def struct(self, niveau):
        """affiche la structure de l ihm avec les imbrications"""
        print(
            "    " * niveau,
            self.id,
            "fileselect ",
            self.titre,
            "(",
            self.parent.id,
            ")",
        )


class Droplist(object):
    _ido = itertools.count(1)

    def __init__(self, parent, lin, col, titre, selecteur, variable):
        self.id = "Dlist" + str(next(self._ido))
        self.parent = parent
        self.ligne = lin
        self.colonne = int(col)
        self.titre = titre
        self.selecteur = selecteur
        self.variable = variable

    def genps(self):
        dl = "$" + self.id
        seldef = '"' + '","'.join(self.selecteur.split(",")) + '"'
        code = [
            dl + " = New-Object system.Windows.Forms.ComboBox",
            dl + ".Items.AddRange(@(%s))" % (seldef,),
        ]
        return [dl], code

    def struct(self, niveau):
        """affiche la structure de l ihm avec les imbrications"""
        print("    " * niveau, "droplist ", self.titre, "(", self.parent.id, ")")


class Bouton(object):
    _ido = itertools.count(1)

    def __init__(self, parent, lin, col, titre):
        self.id = "Btn" + str(next(self._ido))
        self.parent = parent
        self.ligne = lin
        self.colonne = int(col)
        self.titre = titre
        self.elements = []

    def genps(self):
        bt = "$" + self.id
        lcols = self.parent.lcols
        code = [
            bt + " = New-Object system.Windows.Forms.Button",
            bt + '.text = "%s"' % ((self.titre,)),
            bt + ".width =" + str(lcols),
            bt + ".height = 40",
            bt
            + ".location = New-Object System.Drawing.Point(%d,%d)"
            % (self.ligne, self.colonne * lcols),
            bt + ".Font = $font",
            bt + ".UseWaitCursor = $true",
            "#---------onclick----------",
            bt + ".Add_Click(",
            "   {",
        ]
        for el in self.elements:
            se, sc = el.genps()
            code.extend(sc)
        code.extend(["   }", ")"])
        return [bt], code

    @property
    def lcols(self):
        return self.parent.lcols

    def struct(self, niveau):
        """affiche la structure de l ihm avec les imbrications"""
        print("    " * niveau, self.id, "bouton ", self.titre, "(", self.parent.id, ")")
        for el in self.elements:
            el.struct(niveau + 1)


class Label(object):
    def __init__(self, parent, lin, col, text, id=None):
        self.id = "Lbl" + str(next(self._ido)) if id is None else id
        self.parent = parent
        self.ligne = lin
        self.colonne = int(col)
        self.titre = text

    def struct(self, niveau):
        """affiche la structure de l ihm avec les imbrications"""
        print("    " * niveau, self.id, "label ", self.titre, "(", self.parent.id, ")")

    def genps(self):
        px = self.colonne * self.parent.lcols
        py = self.ligne * 50
        lab = self.ref
        code = [
            lab + " = New-Object system.Windows.Forms.Label",
            lab + '.text = "%s"' % (self.titre,),
            lab + ".AutoSize = $true",
            lab + ".Font = $font",
            lab + ".location = New-Object System.Drawing.Point(%d,%d)" % (px, py),
        ]
        return [lab], code


class Commande(object):
    def __init__(self, texte):
        self.commande = texte
        self.ligne = 0
        self.colonne = 0

    def genps(self):
        code = [self.commande]
        return [], code

    def struct(self, niveau):
        """affiche la structure de l ihm avec les imbrications"""
        print("    " * niveau, "commande ", self.commande)


def creihm(nom):
    nbb = 0
    elem = None
    ihm = None
    courant = None
    sniplets = dict()
    with open(nom, "r") as f:
        for ligne in f:
            if not ligne or ligne.startswith("!#"):
                continue
            try:
                code, position, commande = ligne.split(";", 2)
            except ValueError:
                print(" ligne mal formee", ligne)
                continue
            if code == "!ihm":
                if position == "init":
                    interpreteur = commande
                    nom_ihm = os.path.splitext(nom)[0]
                    if ihm:
                        "print erreur redefinition ihm "
                        raise StopIteration
                    ihm = Ihm(nom_ihm, interpreteur)
            elif code == "!fenetre":
                largeur = int(position)
                titre = commande[:-1] if commande.endswith("\n") else commande
                if not ihm:
                    "print erreur cadre ihm non defini"
                    raise StopIteration
                if courant is None:
                    elem = Fenetre(ihm, titre, largeur)
                    ihm.main = elem
                elif isinstance(courant, (Bouton, Fenetre)):
                    courant.elements.append(elem)
                    elem = Fenetre(courant, titre, largeur)
                courant = elem

            elif code == "!fileselect":
                lin, col = position.split(",", 1)
                titre, selecteur, variable = commande.split(";", 2)
                courant.elements.append(
                    Fileselect(courant, lin, col, titre, selecteur, variable)
                )

            elif code == "!ps":
                if commande and "[]" in commande:
                    commande = commande.replace(elem.ref)
                if position:
                    if commande:
                        if position in sniplets:
                            sniplets[position].append(commande)
                        else:
                            sniplets[position].append(commande)
                    else:
                        courant.elements.extend(sniplets[position])
                else:
                    courant.elements.append(Commande(commande))

            elif code == "!droplist":
                lin, col = position.split(",")
                titre, liste, variable = commande.split(";", 2)
                courant.elements.append(
                    Droplist(courant, lin, col, titre, liste, variable)
                )

            elif code == "!button":
                lin, col = position.split(",")
                titre = commande[:-1] if commande.endswith("\n") else commande

                # print("bouton", type(courant), isinstance(courant, Bouton))
                if isinstance(courant, Bouton):
                    courant = ihm.elements[-1] if ihm.elements else ihm.main
                    # print(" courant apres", type(courant))
                elem = Bouton(courant, lin, col, titre)
                courant.elements.append(elem)
                courant = elem

            elif code == "status":
                courant.parent.statusbar = True
                courant.elements.append(Commande("$statusbar.text=" + commande))
                courant.elements.append(Commande("$statusbar.Refresh()"))

    ihm.struct()

    sortie = ihm.nom + ".ps1"
    with open(sortie, "w") as f:
        f.write("\n".join(ihm.genps()))
