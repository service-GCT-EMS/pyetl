# -*- coding: utf-8 -*-
"""
@author: claude
"""

import os
from os import error
import logging
import time
from collections import namedtuple
from flask import render_template, flash, redirect, session, url_for, request
from pyetl_webapp import app
from pyetl import pyetl
from pyetl.vglobales import getmainmapper
from pyetl_webapp.forms import LoginForm, BasicForm, formbuilder

fichinfo = namedtuple("fichinfo", ("nom", "url", "date_maj", "description"))

LOGGER = logging.getLogger(__name__)


def url_to_nom(url):
    return "#" + url[1:] if url.startswith("_") else url


def url_to_fich(url):
    nom = url_to_nom(url)
    return nom if nom.startswith("#") else os.path.join(scriptlist.scriptdir, nom)


class ScriptList(object):
    """cache de la liste de scripts"""

    def __init__(self) -> None:
        self.liste = []
        self.descriptif = dict()
        self.mapper = getmainmapper()
        self.mapper.url_for = url_for
        print(
            "initialisation mainmapper",
            self.mapper.version,
            self.mapper.getvar("mode", "interactif"),
        )
        self.scriptdir = os.path.join(self.mapper.getvar("workdir", "."), "scripts")
        self.scripts = dict()
        self.is_api = dict()
        # self.refresh()

    def refresh(self, script=None):
        """rafraichit la liste de scripts"""
        if script is None:
            self.liste = []
            self.descriptif = dict()
        try:
            filelist = os.listdir(self.scriptdir)
        except FileNotFoundError:
            LOGGER.error("repertoire %s introuvable", self.scriptdir)
            filelist = []
        n = 0
        for fichier in filelist:
            fpath = os.path.join(self.scriptdir, fichier)

            if os.path.isdir(fpath):
                # statinfo = os.stat(fpath)
                # modif = time.ctime(statinfo.st_mtime)
                # self.liste.append(
                #     fichinfo._make((fichier, fichier, modif, "repertoire"))
                # )
                continue
            desc = self.refreshscript(fichier)
            self.liste.append(desc)
            n += 1
        print("scripts analyses", n)
        # print("liste fichiers", self.liste)

    def getlignes(self, nom_script):
        """recupere la description du script"""
        infos = dict()
        if nom_script.startswith("#"):
            macro = self.mapper.getmacro(nom_script)
            script = [i[1] for i in macro.get_commands()]
            params = macro.parametres_pos
            variables = macro.vars_utilisees
            infos["variables"] = variables
            infos["parametres"] = params
            infos["no_in"] = macro.no_in
        else:
            fpath = os.path.join(self.scriptdir, nom_script)
            script = open(fpath, "r").readlines()
            for ligne in script:
                if ligne.startswith("!#"):
                    tmp = ligne[2:].split(":", 1)
                    if len(tmp) == 1:
                        continue
                    clef, contenu = tmp
                    if clef not in infos:
                        infos[clef] = dict() if clef=="variables" else []
                    if clef=="variables":
                        tmp=contenu.split(";",1)
                        nom,question = tmp if len(tmp)==2 else (contenu,contenu)
                        infos[clef][nom]=question
                    else:
                        infos[clef].append(contenu)
        self.descriptif[nom_script] = infos
        self.scripts[nom_script] = script
        self.is_api[nom_script] = infos.get("api", False)
        # print("infos", infos)

    def refreshscript(self, nom_script):
        """rafraichit un script"""
        self.getlignes(nom_script)
        infos = dict()
        ismacro = nom_script.startswith("#")
        if ismacro:
            url = "_" + nom_script[1:]
            modif = ""
        else:
            url = nom_script
            fpath = os.path.join(self.scriptdir, nom_script)
            statinfo = os.stat(fpath)
            modif = time.ctime(statinfo.st_mtime)
        return fichinfo._make(
            (nom_script, url, modif, self.descriptif[nom_script].get("help"))
        )

    def getnom(self, url):
        nomscript = url_to_nom(url)
        self.refreshscript(nomscript)
        return nomscript


scriptlist = ScriptList()
# filemanager_link = url_for("flaskfilemanager.index")
# file_download_link = url_for(
#     "flaskfilemanager.userfile", filename="/my_folder/uploaded_file.txt"
# )


@app.route("/")
@app.route("/index")
def index():
    scriptlist.refresh()
    return render_template(
        "index.html",
        text="acces simplifie aux fonctions mapper",
        title="mapper interface web",
    )


@app.route("/fmgr")
def fmgr():
    print("url ", url_for("flaskfilemanager.index"))
    return redirect(url_for("flaskfilemanager.index"))


@app.route("/folderselect/<fichier>")
def foldeselector(fichier):
    current = session.get("folder", "S:/")
    if fichier and os.path.isfile(os.path.join(current, fichier)):
        session["entree"] = os.path.join(current, fichier)
    else:
        filelist = os.listdir(current)
        fdef = [(i, os.path.isdir(os.path.join(current, i))) for i in filelist]
        return render_template("fileselect.html")


@app.route("/scripts")
def scripts():
    return render_template(
        "scriptlist.html", liste=sorted(scriptlist.liste), mode="exec"
    )


@app.route("/macros")
def macros():
    macrolist = sorted(
        [
            fichinfo._make((i, i.replace("#", "_"), "", ""))
            for i in scriptlist.mapper.getmacrolist()
        ]
    )
    return render_template("scriptlist.html", liste=macrolist, mode="exec")


@app.route("/apis")
def apis():
    # print("isapi", scriptlist.liste)
    mapper = scriptlist.mapper
    apilist = [i for i in scriptlist.liste if scriptlist.is_api.get(i[0])]
    macroapilist = [
        (mapper.getmacro(i).apiname, i, mapper.getmacro(i).retour)
        for i in mapper.getmacrolist()
        if mapper.getmacro(i).apiname
    ]
    apilist.extend(
        [fichinfo._make((i[0], i[1].replace("#", "_"), "", "")) for i in macroapilist]
    )
    print("apilist", macroapilist)
    return render_template("scriptlist.html", liste=sorted(apilist), mode="api")


@app.route("/refresh/<mode>")
def refresh(mode):
    scriptlist.refresh()
    return render_template("scriptlist.html", liste=sorted(scriptlist.liste), mode=mode)


@app.route("/scriptdesc/<script>")
def scriptdesc(script):
    nomscript = scriptlist.getnom(script)
    return render_template(
        "scriptdesc.html",
        descriptif=scriptlist.descriptif[nomscript],
        nom=nomscript,
        url=script,
    )


@app.route("/scriptview/<script>")
def scriptview(script):
    nomscript = scriptlist.getnom(script)
    fich_script = os.path.join(scriptlist.scriptdir, nomscript)
    lignes = scriptlist.scripts[nomscript]
    fill = [""] * 13
    code = []
    n = 0
    for i in lignes:
        n += 1
        if i.startswith("!#") or i.startswith("!"):
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
    return render_template("scriptview.html", code=code, nom=nomscript, url=script)


@app.route("/api/<script>")
def execapi(script):
    """interface webservice"""
    parametres = request.args
    print("parametres requete", parametres)
    rep_sortie = "#webservice"
    nom = url_to_nom(script)
    fich = url_to_fich(script)
    scriptparams = request.args
    processor = scriptlist.mapper.getpyetl(
        fich,
        entree=None,
        rep_sortie="#web",
        liste_params=scriptparams,
        mode="web",
    )
    if processor:
        try:
            processor.process()
            wstats = processor.get_work_stats()
            result = processor.get_results()
            wstats["nom"] = nom
            session["stats"] = wstats
            session["retour"] = result
            print("resultats traitement api", result)
            return redirect("/retour_api/" + script)
        except error as err:
            LOGGER.exception("erreur script", exc_info=err)
            return redirect("/plantage/" + script)
    return redirect("/plantage/" + script)


@app.route("/retour_api/<script>")
def retour_api(script):
    stats = session.get("stats")
    retour = session.get("retour")
    nom = url_to_nom(script)
    if stats:
        return render_template(
            "script_result.html", stats=stats, retour=retour, url=script, nom=nom
        )
    return render_template("noresult.html", url=script, nom=nom)










@app.route("/exec/<script>/<mode>", methods=["GET", "POST"])
# @app.route("/exec/<script>")
def execscript(script, mode):
    nomscript = "#" + script[1:] if script.startswith("_") else script
    scriptlist.refreshscript(nomscript)
    fich_script = (
        nomscript
        if nomscript.startswith("#")
        else os.path.join(scriptlist.scriptdir, nomscript)
    )
    infos = scriptlist.descriptif[nomscript]
    infos["__mode__"] = mode
    print("appel formbuilder", nomscript, infos)
    formclass, varlist = formbuilder(infos)
    form = formclass()
    if form.validate_on_submit():
        if mode != "api":
            entree = form.entree.data[0]
            rep_sortie = form.sortie.data
        else:
            rep_sortie = "#web"
            entree = ""
        scriptparams = dict()
        for desc in varlist:
            nom, definition = desc
            scriptparams[nom] = form.__getattribute__(nom).data

        print("recup form", entree, rep_sortie, infos, scriptparams)
        processor = scriptlist.mapper.getpyetl(
            fich_script,
            entree=entree,
            rep_sortie=rep_sortie,
            liste_params=scriptparams,
            mode="web",
        )
        if processor:
            try:
                processor.process()
                wstats = processor.get_work_stats()
                result = processor.get_results()
                wstats["nom"] = nomscript
                wstats["result"] = result
                session["stats"] = wstats
                # session["retour"] = result
                print("resultats traitement", list(result.keys()))
                if wstats:
                    return render_template(
                        "script_result.html",
                        stats=wstats,
                        retour=result,
                        url=script,
                        nom=nomscript,
                    )
                return render_template("noresult.html", url=script, nom=nomscript)
            except error as err:
                LOGGER.exception("erreur script", exc_info=err)
                return redirect("/plantage/" + script)
        return redirect("/plantage/" + script)

    return render_template(
        "prep_exec.html", nom=nomscript, form=form, varlist=varlist, url=script
    )


@app.route("/plantage/<script>")
def fail(script):
    nom = url_to_nom(script)
    return render_template(
        "plantage.html", text="erreur d'execution", nom=nom, url=script
    )


@app.route("/result/<script>")
def showresult(script):
    stats = session.get("stats")
    retour = session.get("retour")
    nom = url_to_nom(script)
    if stats:
        return render_template(
            "script_result.html", stats=stats, retour=retour, url=script, nom=nom
        )
    return render_template("noresult.html", url=script, nom=nom)


@app.route("/login", methods=["GET", "POST"])
@app.route("/login/<script>", methods=["GET", "POST"])
def login(script=""):
    nom = url_to_nom(script)
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            "Login requested for user {}, remember_me={}".format(
                form.username.data, form.remember_me.data
            )
        )
        return redirect("/index")
    return render_template(
        "login.html", title="Sign In", form=form, nom=nom, url=script
    )


@app.route("/help")
def show_help():
    return render_template("help.html")


@app.route("/fm")
def fileman():
    return redirect("/fm/index.html")
