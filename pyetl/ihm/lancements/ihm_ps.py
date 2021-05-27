# -*- coding: utf-8 -*-
"""creation d ihm poweshell a partir d un fichier de definition"""
import itertools
import os


class Ihm(object):
    def __init__(self, nom=None, interpreteur=None):
        self.nom = nom if nom else "ihm"
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
        code = [
            "# genere automatiquement par le generateur d ihm de mapper",
            "",
            "",
            "Add-Type -AssemblyName System.Windows.Forms",
            "$font=New-Object System.Drawing.Font('Microsoft Sans Serif',10)",
            "$startx=20",
        ]
        for el in self.elements:
            code.extend(el.genps())
        return code


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
            elif i.ligne.isnumeric():
                cour = int(i.ligne)
        maxlin = max(maxlin, cour)
        return maxlin

    def genps(self):
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

        code.append(vref + ".controls.AddRange(@(" + ",".join(vlist) + "))")
        code.append(vref + ".ShowDialog())")
        return code


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
        px = self.colonne * self.parent.lcol
        py = self.ligne * 50
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
        dl = "$Dlist" + self.id
        code = [
            dl + " = New-Object system.Windows.Forms.ComboBox",
            dl + ".Items.AddRange(@(%s)" % (selecteur,),
        ]
        return [], code


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
        code = []
        return [], code


class Commande(object):
    def __init__(self, texte):
        self.commande = texte
        self.ligne = "="
        self.colonne = 0

    def genps(self):
        code = [self.commande]
        return [], code


def creihm(nom):
    nbb = 0
    elem = None
    ihm = None
    courant = None
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
                titre = commande
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
                courant.elements.append(Commande(commande))

            elif code == "!droplist":
                lin, col = position.split(",")
                titre, liste, variable = commande.split(";", 2)
                courant.elements.append(
                    Droplist(courant, lin, col, titre, liste, variable)
                )

            elif code == "!button":
                lin, col = position.split(",")
                titre = commande
                elem = Bouton(courant, lin, col, titre)
                if isinstance(courant, Bouton):
                    courant = ihm.elements[-1] if ihm.elements else ihm.main
                courant.elements.append(elem)
                courant = elem

    nbcols = ihm.colonnes
    nblignes = ihm.lignes
    lcols = int((largeur - 40) / nbcols)
    hauteur = lcols * 50
    sortie = ihm.nom + ".ps1"
    with open(sortie, "w") as f:
        f.writelines(ihm.genps())
