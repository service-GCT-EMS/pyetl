# -*- coding: utf-8 -*-
"""
@author: claude
"""

import os
import time
from collections import namedtuple
from flask import render_template
from pyetl_webapp import app
from pyetl import pyetl
from pyetl.vglobales import getmainmapper


fichinfo = namedtuple("fichinfo", ("nom", "date_maj", "description"))


class ScriptList(object):
    """cache de la liste de scripts"""

    def __init__(self) -> None:
        self.liste = []
        self.scriptdir = "scripts"
        self.descriptif = []
        self.refresh()
        self.mapper = getmainmapper()
        print("initialisation mainmapper", self.mapper)

    def refresh(self, script=None):
        """rafraichit la liste de scripts"""
        if script is None:
            self.liste = []
            self.descriptif = dict()
        liste = os.listdir(self.scriptdir)
        n = 0
        for fichier in liste:
            desc = self.refreshscript(fichier)
            self.liste.append(desc)
            n += 1
        print("scripts analyses", n)

    def refreshscript(self, nom_script):
        """rafraichit un script"""
        fpath = os.path.join(self.scriptdir, nom_script)
        statinfo = os.stat(fpath)
        modif = time.ctime(statinfo.st_mtime)
        desc = ""
        infos = dict()
        for ligne in open(fpath, "r").readlines():
            if ligne.startswith("!#"):
                tmp = ligne[2:].split(":", 1)
                if len(tmp) == 1:
                    continue
                clef, contenu = tmp
                if clef == "description":
                    desc = contenu.split(";", 1)[-1]
                infos[clef] = contenu
        self.descriptif[nom_script] = infos
        return fichinfo._make((nom_script, modif, desc))


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
    scriptlist.refreshscript(script)
    return render_template(
        "scriptdesc.html", descriptif=scriptlist.descriptif[script], nom=script
    )


@app.route("/scriptview/<script>")
def scriptview(script):
    scriptlist.refreshscript(script)
    fich_script = os.path.join(scriptlist.scriptdir, script)
    lignes = open(fich_script, "r").readlines()
    fill = [""] * 13
    code = []
    for i in lignes:
        if i.startswith("!#"):
            continue
        elif i.startswith("!"):
            code.append(tuple(i.replace(";", "")))
        elif i.startswith("$"):
            tmp = ";".join([x for x in i.split(";") if x])
            code.append(tmp)
        else:
            tmp = (i.split(",") + fill)[:13]
            if any(tmp):
                code.append(tuple(tmp))

    code = [tuple((i.split(";") + fill)[:13]) for i in lignes if not i.startswith("!#")]
    return render_template("scriptview.html", code=code, nom=script)


@app.route("/exec/<script>")
def execscript(script):
    scriptlist.refreshscript(script)
    fich_script = os.path.join(scriptlist.scriptdir, script)
    processor = scriptlist.mapper.getpyetl(fich_script)
    if processor:
        processor.process()
    return render_template(
        "scriptdesc.html", descriptif=scriptlist.descriptif[script], nom=script
    )
