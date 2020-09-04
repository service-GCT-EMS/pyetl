# -*- coding: utf-8 -*-
"""
@author: claude
"""

import os
import time
from collections import namedtuple
from flask import render_template
from pyetl_webapp import app

fichinfo = namedtuple("fichinfo", ("nom", "date_maj", "description"))


class ScriptList(object):
    def __init__(self) -> None:
        self.liste = []
        self.scriptdir = "scripts"
        self.descriptif = []
        self.refresh()

    def refresh(self):
        self.liste = []
        self.descriptif = dict()
        liste = os.listdir(self.scriptdir)
        nb=0
        for fichier in liste:
            fpath = os.path.join(self.scriptdir, fichier)
            statinfo = os.stat(fpath)
            modif = time.ctime(statinfo.st_mtime)
            desc = ""
            infos = dict()
            if os.path.isdir(fpath):
                self.liste.append(fichinfo._make((fichier, modif, 'repertoire')))
                continue
            nb+=1
            for ligne in open(fpath, "r").readlines():
                if ligne.startswith("!#"):
                    tmp = ligne[2:].split(":", 1)
                    if len(tmp) == 1:
                        continue
                    clef, contenu = tmp
                    if clef == "description":
                        desc = contenu.split(";", 1)[-1]
                    infos[clef] = contenu
            self.liste.append(fichinfo._make((fichier, modif, desc)))
            self.descriptif[fichier] = infos

        print("scripts analyses", nb)


scriptlist = ScriptList()


@app.route("/")
@app.route("/index")
def index():
    return render_template(
        "index.html", text="Hello, World!", title="mapper interface web"
    )


@app.route("/scripts")
def scripts():
    return render_template("scriptlist.html", liste=sorted(scriptlist.liste))


@app.route("/refresh")
def refresh():
    scriptlist.refresh()
    return render_template("scriptlist.html", liste=sorted(scriptlist.liste))


@app.route("/scriptdesc/<script>")
def scriptdesc(script):
    scriptlist.refresh()
    return render_template(
        "scriptdesc.html", descriptif=scriptlist.descriptif[script], nom=script
    )
