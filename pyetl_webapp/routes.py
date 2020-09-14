# -*- coding: utf-8 -*-
"""
@author: claude
"""

import os
import time
from collections import namedtuple
from flask import render_template, flash, redirect
from pyetl_webapp import app
from pyetl import pyetl
from pyetl.vglobales import getmainmapper
from pyetl_webapp.forms import LoginForm, BasicForm

fichinfo = namedtuple("fichinfo", ("nom", "date_maj", "description"))


class ScriptList(object):
    """cache de la liste de scripts"""

    def __init__(self) -> None:
        self.liste = []
        self.scriptdir = "scripts"
        self.descriptif = []
        self.refresh()
        self.mapper = getmainmapper()
        print(
            "initialisation mainmapper",
            self.mapper,
            self.mapper.getvar("mode", "interactif"),
        )

    def refresh(self, script=None):
        """rafraichit la liste de scripts"""
        if script is None:
            self.liste = []
            self.descriptif = dict()
        liste = os.listdir(self.scriptdir)
        n = 0
        for fichier in liste:
            fpath = os.path.join(self.scriptdir, fichier)

            if os.path.isdir(fpath):
                statinfo = os.stat(fpath)
                modif = time.ctime(statinfo.st_mtime)
                self.liste.append(fichinfo._make((fichier, modif, "repertoire")))
                continue
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
        "index.html",
        text="acces simplifie aux fonctions mapper",
        title="mapper interface web",
    )


@app.route("/scripts")
def scripts():
    return render_template("scriptlist.html", liste=sorted(scriptlist.liste))


@app.route("/macros")
def macros():
    macrolist = sorted(
        [fichinfo._make((i, "", "")) for i in scriptlist.mapper.getmacrolist()]
    )
    return render_template("scriptlist.html", liste=sorted(macrolist))


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
    n = 0
    for i in lignes:
        n += 1
        if i.startswith("!#"):
            continue
        elif i.startswith("!"):
            if n == 1:
                continue
            colspan = 13
            contenu = [i.replace(";", " ")]
        elif i.startswith("$"):
            tmp = (i.split(";") + fill)[:13]
            contenu = [" ".join(tmp[:12]), tmp[12]]
            colspan = 12
        else:
            contenu = (i.split(";") + fill)[:13]
            colspan = 1
            if not any(contenu):
                continue
        code.append((n, colspan, contenu))
    # print("scriptview,", code)
    return render_template("scriptview.html", code=code, nom=script)


@app.route("/exec/<script>", methods=["GET", "POST"])
def execscript(script):
    scriptlist.refreshscript(script)
    fich_script = os.path.join(scriptlist.scriptdir, script)
    form = BasicForm()
    if form.validate_on_submit():
        entree = form.entree.data
        rep_sortie = form.sortie.data
        processor = scriptlist.mapper.getpyetl(
            fich_script, entree=entree, rep_sortie=rep_sortie, mode="web"
        )
        if processor:
            processor.process()
            wstats = processor.get_work_stats()
        return redirect("/result")
    return render_template("prep_exec.html", nom=script, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            "Login requested for user {}, remember_me={}".format(
                form.username.data, form.remember_me.data
            )
        )
        return redirect("/index")
    return render_template("login.html", title="Sign In", form=form)
