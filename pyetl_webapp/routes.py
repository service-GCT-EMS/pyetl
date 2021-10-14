# -*- coding: utf-8 -*-
"""
@author: claude
"""

import os
from os import error
from io import StringIO
from types import MethodType
import logging
import time
from collections import namedtuple
from requests import Request
from urllib.parse import urlencode

from flask import (
    render_template,
    flash,
    redirect,
    session,
    jsonify,
    url_for,
    request,
    Response,
    abort,
)

# from flask_gssapi import GSSAPI
from pyetl_webapp import app
from pyetl import pyetl
from pyetl.vglobales import getmainmapper
from pyetl_webapp.forms import LoginForm, BasicForm, formbuilder

fichinfo = namedtuple("fichinfo", ("nom", "url", "date_maj", "description"))
try:
    from flask_gssapi import GSSAPI

    gssapi = GSSAPI(app)
    require_auth = gssapi.require_auth
except (ImportError, OSError):
    gssapi = None

    def require_auth(func):
        return func

    pass
LOGGER = logging.getLogger(__name__)


def url_to_nom(url):
    return "#" + url[1:] if url.startswith("_") else url


def url_to_fich(url):
    nom = url_to_nom(url)
    return nom if nom.startswith("#") else os.path.join(scriptlist.scriptdir, nom)


def init_vue(vars):
    """initialise l objet vue """
    vuedict = {
        "el": "'#vm'",
        "delimiters": "['[[', ']]']",
        "data": {"message": "'Vue OK'", "x_ws": True},
    }
    vue = [
        "<script>",
        "const vm = new Vue({",
        "el: '#vm'",
        "delimiters: ['[[', ']]']",
        "data: {",
    ]
    vue = vue + ["message: 'Vue OK'", "x_ws: true", "}"]
    vue = vue + ["})", "</script>"]

    return "\n".join(vue)


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
        self.apis = dict()
        self.worker = ""
        # self.inited = "False"
        self.refresh(False)

    def loadws(self, worker=None):
        if worker is None:
            worker = self.mapper
        worker.charge_cmd_internes(
            direct=os.path.join(os.path.dirname(__file__), "config\webservices")
        )
        worker.charge_cmd_internes(site="webservices", opt=1)  # macros de site
        if worker.paramdir is not None:
            worker.charge_cmd_internes(
                direct=os.path.join(worker.paramdir, "webservices"), opt=1
            )  # macros perso

    def refresh(self, local, script=None):
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
        self.loadws()
        self.macroapis()

        print("scripts analyses", n)
        # print("liste fichiers", self.liste)
        if local:  # on raffraichit aussi le webworker
            nom = session.get("nompyetl", scriptlist.worker if local else "")
            webworker = self.mapper.getpyetl([], mode="web", nom=nom)
            if webworker:
                self.loadws(webworker)

    def macroapis(self):
        """ stocke les definitions des apis"""
        for i, m in self.mapper.getmacros():
            if m.apis:
                for nom, contenu in m.apis.items():
                    self.apis[nom] = contenu

    def getlignes(self, nom_script):
        """recupere la description du script"""
        infos = dict()
        if nom_script.startswith("#"):
            macro = self.mapper.getmacro(nom_script)
            if not macro:
                raise KeyError
            script = [i[1] for i in macro.get_commands()]
            params = macro.parametres_pos
            variables = macro.vars_utilisees
            infos["variables"] = variables
            infos["parametres"] = params
            infos["defauts"] = macro.vdef
            infos["no_in"] = {macro.no_in: "pas d entree"}
            infos["e_s"] = (macro.e_s.get("entree", ""), macro.e_s.get("sortie", ""))
            infos["help"] = macro.help
            infos["help_detaillee"] = macro.help_detaillee
            infos["api"] = macro.apis
        else:
            fpath = os.path.join(self.scriptdir, nom_script)
            try:
                script = open(fpath, "r").readlines()
            except FileNotFoundError:
                raise KeyError
            for ligne in script:
                if ligne.startswith("!#"):
                    if ligne.endswith("\n"):
                        ligne = ligne[:-1]
                    tmp = ligne[2:].split(":", 1)
                    if len(tmp) == 1:
                        continue
                    clef, contenu = tmp
                    if clef not in infos:
                        infos[clef] = dict() if clef == "variables" else []
                    if clef == "variables":
                        tmp = contenu.split(";", 1)
                        nom, question = tmp if len(tmp) == 2 else (contenu, contenu)
                        infos[clef][nom] = question
                    else:
                        infos[clef].append(contenu)
        self.descriptif[nom_script] = infos
        self.scripts[nom_script] = script
        apidef = infos.get("api", False)
        self.is_api[nom_script] = bool(apidef)
        if apidef:
            for i in apidef:
                nom, retour, template, *_ = i.split(";") + ["", "", ""]
                self.apis[nom] = (nom_script, retour, template)
            # print("apidef apis", self.apis, apidef)

    def refreshscript(self, nom_script):
        """rafraichit un script"""
        try:
            self.getlignes(nom_script)
        except KeyError:
            abort(404)
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

    def getapilist(self):
        # genere la liste des apis
        # apilist = [i for i in scriptlist.liste if scriptlist.is_api.get(i[0])]
        # print("getapilist", self.apis)
        apilist = [
            fichinfo._make(
                (
                    nom,
                    contenu[0].replace("#", "_"),
                    contenu[1],
                    scriptlist.descriptif.get(contenu[0], {}).get("help"),
                )
            )
            for nom, contenu in self.apis.items()
        ]
        return apilist


scriptlist = ScriptList()
# filemanager_link = url_for("flaskfilemanager.index")
# file_download_link = url_for(
#     "flaskfilemanager.userfile", filename="/my_folder/uploaded_file.txt"
# )


@app.route("/")
@app.route("/index")
@require_auth
def index(username=""):
    local = request.host.startswith("127.0.0.1:")
    scriptlist.refresh(local)
    return render_template(
        "index.html",
        text="acces simplifie aux fonctions mapper pour" + username,
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
        "scriptlist.html",
        liste=sorted(scriptlist.liste),
        mode="exec",
        c2="Date de Mise a Jour",
    )


@app.route("/macros")
def macros():
    macrolist = sorted(
        [
            fichinfo._make((i, i.replace("#", "_"), "****" if m.apis else "", m.help))
            for i, m in scriptlist.mapper.getmacros()
        ]
    )
    return render_template(
        "scriptlist.html", liste=macrolist, mode="exec", c2="mode api"
    )


@app.route("/apis")
def apis():
    # print("isapi", scriptlist.liste)
    apilist = scriptlist.getapilist()
    return render_template("scriptlist.html", liste=sorted(apilist), mode="api", c2="")


@app.route("/refresh/<mode>")
def refresh(mode):
    local = request.host.startswith("127.0.0.1:")
    scriptlist.refresh(local)
    return render_template(
        "scriptlist.html",
        liste=sorted(scriptlist.liste),
        mode=mode,
        c2="Date de Mise a Jour",
    )


# @app.route("/statictest/<script>")
# def statictest(script):
#     return url_for("static", filename="statictest/" + script)


@app.route("/scriptdesc/<script>")
def scriptdesc(script):
    nomscript = scriptlist.getnom(script)
    print("appel scriptdesc", scriptlist.descriptif[nomscript])
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
    typem = ""
    for i in lignes:
        type_ligne = "ltype_inst"
        n += 1
        if n == 1 and i.startswith("!"):
            continue
        if i.startswith("!#") or i.startswith("!"):
            type_ligne = "ltype_comment"
            colspan = 13
            contenu = [i.replace(";", " ")]
        elif i.startswith("$"):
            type_ligne = "ltype_group" if i.startswith("$#") else "ltype_affect"
            tmp = (i.split(";") + fill)[:13]
            contenu = [" ".join(tmp[:12]), tmp[12]]
            colspan = 12
        else:
            type_ligne = "ltype_inst"
            if i.startswith("&&#"):
                type_ligne = "ltype_macro"
                typem = " levelm"
            if i.startswith("&&#end"):
                type_ligne = "ltype_macro"
                typem = ""
            if "<#" in i:
                type_ligne = "ltype_charge"
            contenu = (i.split(";") + fill)[:13]
            colspan = 1
            if not any(contenu):
                continue
        type_ligne = type_ligne + typem
        if i.startswith("|||"):
            type_ligne = type_ligne + " level3"
        elif i.startswith("||"):
            type_ligne = type_ligne + " level2"
        elif i.startswith("|"):
            type_ligne = type_ligne + " level1"

        code.append((n, colspan, contenu, type_ligne))
    # print("scriptview,", code)
    return render_template("scriptview.html", code=code, nom=nomscript, url=script)


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


@app.route("/mws")
def webservicelist():
    apilist = scriptlist.getapilist()
    return jsonify(apilist)


def process_script(nomscript, entree, rep_sortie, scriptparams, mode, local):
    """execute un traitement"""
    stime = time.time()
    fich_script = (
        nomscript
        if nomscript.startswith("#")
        else os.path.join(scriptlist.scriptdir, nomscript)
    )
    nom = session.get("nompyetl", scriptlist.worker if local else "")

    processor = scriptlist.mapper.getpyetl(
        fich_script,
        entree=entree,
        rep_sortie=rep_sortie,
        liste_params=scriptparams,
        mode=mode,
        nom=nom,
    )
    wstats = None
    # print(
    #     "recup processeur", mode, processor.idpyetl if processor else None, fich_script
    # )
    result = None
    tmpdir = ""
    if processor:
        try:
            processor.process()
            wstats = processor.get_work_stats()
            result, tmpdir = processor.get_results()
            wstats["tmpdir"] = tmpdir
            wstats["result"] = list(result.keys())
            wstats["nom"] = nomscript
            session["stats"] = wstats
            session["nompyetl"] = processor.nompyetl
            if local:
                scriptlist.worker = processor.nompyetl
        except error as err:
            LOGGER.exception("erreur script", exc_info=err)
    else:
        failedworker = scriptlist.mapper.getpyetl([], mode="web", nom=nom)
        if failedworker:
            result, tmpdir = failedworker.get_results()
    return (wstats, result, tmpdir)


@app.route("/mws/<api>", methods=["GET", "POST"])
def webservice(api):
    local = request.host.startswith("127.0.0.1:")
    # print("dans webservice", script, session, request.host, local, scriptlist.worker)
    infoscript = scriptlist.apis.get(api)
    if not infoscript:
        return "erreur script non trouve %s" % (api,)
    script = infoscript[0]
    nomscript = "#" + script[1:] if script.startswith("_") else script
    if not scriptlist.refreshscript(nomscript):
        abort(404)
    tmp = dict(request.args.items())
    # on recupere les parametres positionnels s il y en a
    pp = tmp.pop("_pp", "")
    if pp:
        nomscript = nomscript + ";" + pp
    entree = ""
    rep_sortie = ""
    scriptparams = [i + "=" + j for i, j in tmp.items()]

    retour = process_script(
        nomscript, entree, rep_sortie, scriptparams, "webservice", local
    )
    wstats, result, tmpdir = retour
    if result:
        if "print" in result:
            ret = tuple([i if len(i) > 1 else i[0] for i in result["print"] if i])
            # print("recup ", ret)
            if len(ret) == 0:
                ret = "no result"
            elif len(ret) == 1:
                ret = ret[0]

            # print("json", jsonify(ret))
            return jsonify(ret)
        for elem in result:
            if elem.startswith("schema"):
                xml = result[elem]
                print("xml", xml[0:10])
                return Response(result[elem], mimetype="text/xml")
        if "log" in result:
            return jsonify(result["log"])
        return "erreur rien a retourner"
    else:
        return "erreur pas de retour"


@app.route("/exec/<appel>/<mode>", methods=["GET", "POST"])
# @app.route("/exec/<script>")
def execscript(appel, mode):
    # print("dans exec", script)
    local = request.host.startswith("127.0.0.1:")
    ws = mode == "api"
    if ws:
        infoscript = scriptlist.apis.get(appel)
        if not infoscript:
            return "erreur script non trouve %s (%s)" % (
                appel,
                str(list(scriptlist.apis.keys())),
            )
        script = infoscript[0]
    else:
        script = appel
    nomscript = "#" + script[1:] if script.startswith("_") else script
    scriptlist.refreshscript(nomscript)
    fich_script = (
        nomscript
        if nomscript.startswith("#")
        else os.path.join(scriptlist.scriptdir, nomscript)
    )
    infos = scriptlist.descriptif[nomscript]
    infos["__mode__"] = mode
    # print("appel formbuilder", nomscript, infos)
    formclass, varlist = formbuilder(infos)
    form = formclass()
    rep_sortie = ""
    entree = ""
    if form.validate_on_submit():
        try:
            entree = form.entree.data
        except AttributeError:
            pass
        try:
            rep_sortie = form.sortie.data
        except AttributeError:
            pass
        scriptparams = dict()
        for desc in varlist:
            nom, definition = desc
            scriptparams[nom] = str(form.__getattribute__(nom).data)

        print("recup form", entree, rep_sortie, infos, scriptparams)
        # print("full url", request.base_url)
        x_ws = scriptparams.get("x_ws")
        if "x_ws" in scriptparams:
            del scriptparams["x_ws"]
        print("valeur xws", x_ws)
        if x_ws == "True":  # on appelle en mode webservice
            qstr = urlencode(scriptparams)
            # url = "http://mws/" + script
            wsurl = "/mws/" + appel + "?" + qstr
            # print("mode webservice ", "/mws/" + script + "?" + qstr)
            return redirect(wsurl)
        retour = process_script(
            nomscript, entree, rep_sortie, scriptparams, "web", local
        )
        wstats, result, tmpdir = retour
        if wstats:
            return render_template(
                "script_result.html",
                stats=wstats,
                retour=result,
                url=script,
                nom=nomscript,
            )
        else:
            # return render_template("noresult.html", url=script, nom=nomscript)

            return render_template(
                "plantage.html",
                text="erreur d'execution",
                nom=nom,
                url=script,
                retour=result,
            )

    return render_template(
        "prep_exec.html", nom=nomscript, form=form, varlist=varlist, url=script, ws=ws
    )


# @app.route("/plantage/<script>")
# def fail(script):
#     nom = url_to_nom(script)
#     return render_template(
#         "plantage.html", text="erreur d'execution", nom=nom, url=script
#     )


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
def login(script="", username=""):
    if username:
        print("utilisateur identifie", username)
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


@app.route("/favicon.ico")
def favicon():
    return url_for("static", filename="images/favicon.ico")


@app.route("/intro")
def show_intro():
    return render_template("intro.html")


@app.route("/fm")
def fileman():
    return redirect("/fm/index.html")
