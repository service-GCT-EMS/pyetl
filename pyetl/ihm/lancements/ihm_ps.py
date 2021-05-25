"""creation d ihm poweshell a partir d un fichier de definition"""


def creihm(nom):
    nb = 0
    with open(nom, "r") as f:
        for ligne in f:
            code, position, commande = ligne.split(";", 3)
            if code == "!ihm":
                if position == "init":
                    interpreteur = commande
            elif code == "!fenetre":
                largeur = int(position)
                titre = commande
            elif code == "!fileselect":
                lin, col = position.split(",")
                titre, limites, variable = commande
            elif code == "!ps":
                commande_ps = commande
            elif code == "!droplist":
                lin, col = position.split(",")
                titre, liste, variable = commande
            elif code == "button":
                lin, col = position.split(",")
                titre = commande
                nb += 1
