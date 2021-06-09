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
        self.variables = dict()

    @property
    def colonnes(self):
        return self.main.colonnes

    @property
    def lignes(self):
        return self.main.lignes

    def genps(self, variables):
        """genere le code ps pour l´ihm"""
        self.variables = variables
        nbcols = self.colonnes
        nblignes = self.lignes
        self.lcols = int((self.main.largeur - 40) / nbcols)
        self.hlin = 60

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
        self.variables = parent.variables

    @property
    def colonnes(self):
        return max((i.colonne for i in self.elements))

    @property
    def lignes(self):
        maxlin = 0
        cour = 0
        for i in self.elements:
            print(type(i), "ligne", i.ligne)
            if i.ligne == "+":
                cour += i.hauteur
                i.ligne = cour
            elif isinstance(i.ligne, int) or i.ligne.isnumeric():
                cour = int(i.ligne)
                i.ligne = cour
            elif i.ligne == "=":
                i.ligne = cour
        maxlin = max(maxlin, cour)
        if self.statusbar:
            maxlin += 1
        print("lignes de l ihm", len(self.elements), maxlin)
        return maxlin

    def genps(self):
        self.lcols = int((self.largeur - 40) / (self.colonnes))
        self.hlin = 60
        vref = "$" + self.id
        code = [
            vref + " = New-Object system.Windows.Forms.Form",
            vref
            + ".ClientSize  = New-Object System.Drawing.Point(%d,%d)"
            % (self.largeur, (self.lignes + 2) * self.hlin),
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


class Element(object):
    """element generique d ihm"""

    def __init__(self, parent, lin, col, titre):
        self.parent = parent
        self.ligne = lin
        self.colonne = int(col)
        self.titre = titre
        self.hauteur = 1
        self.elements = []
        self.nature = "Element"
        self.variables = parent.variables

    def mkheader(self):
        return ["", "#============" + self.nature + "=============", ""]

    @property
    def px(self):
        return (self.colonne - 1) * self.parent.lcols + 20

    @property
    def py(self):
        return (self.ligne - 1) * self.parent.hlin + 40

    def position(self, dx=0, dy=0):
        return "New-Object System.Drawing.Point(%d,%d)" % (self.px + dx, self.py + dy)

    def mklab(self, lab, titre, dx=0, dy=0):
        return [
            lab + " = New-Object system.Windows.Forms.Label",
            lab + '.text = "%s"' % (titre,),
            lab + ".AutoSize = $true",
            lab + ".Font = $font",
            lab + ".location = " + self.position(dx, dy),
            "",
        ]

    def struct(self, niveau):
        """affiche la structure de l ihm avec les imbrications"""
        print(
            "    " * niveau,
            self.id,
            self.nature,
            self.titre,
            "(",
            self.parent.id,
            ")",
        )
        for el in self.elements:
            el.struct(niveau + 1)


class Fileselect(Element):

    _ido = itertools.count(1)

    def __init__(self, parent, lin, col, titre, selecteur, variable):
        super().__init__(parent, lin, col, titre)
        self.id = "Fsel" + str(next(self._ido))
        self.nature = "Fileselect"
        self.selecteur = selecteur
        self.variable = variable
        self.hauteur = 2
        self.ref = self.id + "TB.Text"
        self.variables = parent.variables

    def genps(self):
        lab = "$" + self.id + "L"
        tb = "$" + self.id + "TB"
        fbr = "$" + self.id + "FBR"
        fbt = "$" + self.id + "FBT"
        code = (
            self.mkheader()
            + self.mklab(lab, self.titre)
            + [
                "",
                tb + " = New-Object system.Windows.Forms.TextBox",
                tb + ".multiline = $false",
                tb + ".width = 300",
                tb + ".height = 20",
                tb + ".location = " + self.position(dy=40),
                tb + ".Font = $font",
                tb + ".AllowDrop = $true",
                "",
                tb + ".add_DragDrop(",
                "   {",
                "       $files = [string[]]$_.Data.GetData([Windows.Forms.DataFormats]::FileDrop)",
                "       if ($files){$textbox1.Text = $files[0]}",
                "   }",
                ")",
                tb + ".add_DragOver(",
                "   {",
                "       if ($_.Data.GetDataPresent([Windows.Forms.DataFormats]::FileDrop))",
                "       {$_.Effect = 'Copy'} else {$_.Effect = 'None'}",
                "   }",
                ")",
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
                fbt + ".location = " + self.position(dx=300, dy=40),
                fbt + ".Font = $font",
                "#===onclick====",
                fbt + ".Add_Click(",
                "   {",
                '       $sd="."',
                "       if (%s.Text -ne '') { $sd=Split-Path -Path %s.Text }"
                % (tb, tb),
                "       %s.InitialDirectory=$sd" % (fbr,),
                "       $null = %s.ShowDialog()" % (fbr,),
                "       %s.Text = %s.FileName" % (tb, fbr),
                "       %s.Update()" % (tb,),
                "   }",
                "   )",
            ]
        )
        return [lab, tb, fbt], code


class Droplist(Element):
    _ido = itertools.count(1)

    def __init__(self, parent, lin, col, titre, selecteur, variable):
        super().__init__(parent, lin, col, titre)
        self.id = "Dlist" + str(next(self._ido))
        self.selecteur = selecteur
        self.variable = variable
        self.nature = "Droplist"
        self.hauteur = 2
        self.ref = self.id + ".Text"

    def genps(self):
        dl = "$" + self.id
        dlb = dl + "L"
        seldef = '"' + '","'.join(self.selecteur.split(",")) + '"'
        code = (
            self.mkheader()
            + self.mklab(dlb, self.titre)
            + [
                dl + " = New-Object system.Windows.Forms.ComboBox",
                dl + ".Items.AddRange(@(%s))" % (seldef,),
                dl + ".location =" + self.position(dy=30),
                dl + ".width = 100",
                dl + ".height = 40",
                dl + ".Font = $font",
            ]
        )
        return [dl, dlb], code


class Checkbox(Element):
    _ido = itertools.count(1)

    def __init__(self, parent, lin, col, titre, etat, variable):
        super().__init__(parent, lin, col, titre)
        self.id = "Cbox" + str(next(self._ido))
        self.etat = etat
        self.variable = variable
        self.nature = "Checkbox"
        self.hauteur = 1
        self.ref = self.id + ".Checked"

    def genps(self):
        cb = "$" + self.id
        code = self.mkheader() + [
            cb + "= New-Object system.Windows.Forms.CheckBox",
            cb + '.text = "%s"' % (self.titre,),
            cb + ".AutoSize = $true",
            cb + ".Checked = %s" % (self.etat,),
            cb + ".location =" + self.position(),
            cb + ".Font = $font",
        ]
        return [cb], code


class Bouton(Element):

    _ido = itertools.count(1)

    def __init__(self, parent, lin, col, titre):
        super().__init__(parent, lin, col, titre)
        self.id = "Btn" + str(next(self._ido))
        self.nature = "Bouton"

    def genps(self):
        bt = "$" + self.id
        lcols = self.parent.lcols
        code = self.mkheader() + [
            bt + " = New-Object system.Windows.Forms.Button",
            bt + '.text = "%s"' % ((self.titre,)),
            bt + ".width =" + str(lcols),
            bt + ".height = 40",
            bt + ".location = " + self.position(),
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


class Label(Element):
    _ido = itertools.count(1)

    def __init__(self, parent, lin, col, titre):
        super().__init__(parent, lin, col, titre)
        self.id = "Lbl" + str(next(self._ido))
        self.nature = "label"

    def genps(self):
        lab = self.id
        code = self.header() + self.mklab(lab, self.titre)
        return [lab], code


class Commande(Element):
    def __init__(self, parent, texte):
        super().__init__(parent, "=", 1, "")
        self.commande = texte
        self.nature = "commande"
        self.ligne = "="
        self.colonne = 1

    def genps(self):
        commande = self.commande
        while "$[" in commande:
            variable = commande.split("$[")[1].split("]$")[0]
            if variable in self.variables:
                commande = commande.replace(
                    "$[" + variable + "]$", "$($" + self.variables[variable].ref + ")"
                )
            else:
                print("variable introuvable", variable, self.variables)
                break
        code = [commande]
        return [], code

    def struct(self, niveau):
        """affiche la structure de l ihm avec les imbrications"""
        print("    " * niveau, "commande ", self.commande)


# def getvariable(code):
#     """extrait la ou les variables de references"""
#     if '['in code:
#         variables=code.strip()[:-1].split('[')[1]
#     return variables


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
                code, position, commande = ligne[:-1].split(";", 2)
            except ValueError:
                print(" ligne mal formee", ligne)
                continue
            if code.startswith("!ihm"):
                if position == "init":
                    interpreteur = commande
                    nom_ihm = os.path.splitext(nom)[0]
                    if ihm:
                        "print erreur redefinition ihm "
                        raise StopIteration
                    ihm = Ihm(nom_ihm, interpreteur)
                    variables = ihm.variables
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
                fsel = Fileselect(courant, lin, col, titre, selecteur, variable)
                courant.elements.append(fsel)
                if variable:
                    variables[variable] = fsel

            elif code == "!ps":
                if commande and "$[]$" in commande:
                    commande = commande.replace("$[]$", "$($" + elem.ref + ")")
                if position:
                    if commande:
                        if position in sniplets:
                            sniplets[position].append(commande)
                        else:
                            sniplets[position] = [commande]
                    else:
                        courant.elements.extend(sniplets[position])
                else:
                    courant.elements.append(Commande(courant, commande))

            elif code == "!droplist":
                lin, col = position.split(",")
                titre, liste, variable = commande.split(";", 2)
                dlist = Droplist(courant, lin, col, titre, liste, variable)
                courant.elements.append(dlist)
                if variable:
                    variables[variable] = dlist

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

            elif code == "!case":
                lin, col = position.split(",")
                titre, init, variable = commande.split(";", 2)
                dlist = Checkbox(courant, lin, col, titre, init, variable)
                courant.elements.append(dlist)
                if variable:
                    variables[variable] = dlist

            elif code == "status":
                courant.parent.statusbar = True
                courant.elements.append(Commande("$statusbar.text=" + commande))
                courant.elements.append(Commande("$statusbar.Refresh()"))

    ihm.struct()

    sortie = ihm.nom + ".ps1"
    with open(sortie, "w") as f:
        f.write("\n".join(ihm.genps(variables)))
