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
# from flask_sspi import authenticate

from flask import (
    render_template,render_template_string,
    flash,
    redirect,
    session,
    jsonify,
    url_for,
    request,
    Response,
    abort,
    g
)

# from flask_gssapi import GSSAPI
from pyetl_webapp import app
from pyetl import pyetl
from pyetl.vglobales import getmainmapper
from pyetl_webapp.forms import LoginForm, BasicForm, formbuilder

fichinfo = namedtuple("fichinfo", ("nom", "url", "date_maj", "description"))
LOGGER = logging.getLogger(__name__)
# try:
#     from flask_gssapi import GSSAPI

#     gssapi = GSSAPI(app)
#     require_auth = gssapi.require_auth
# except (ImportError, OSError):
#     gssapi = None
#     LOGGER.error("systeme d'authentification non activé")
#     def require_auth(func):
#         return func

#     pass



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
                self.is_api[i] =True
                for nom, contenu in m.apis.items():
                    self.apis[nom] = contenu
                    print("apidef apis", contenu, self.apis[nom])
            else:
                self.is_api[i] = False
        # if apidef:
        #     for i in apidef:
        #         nom, retour, template,no_in, *_ = i.split(";") + ["", "", "",""]
        #         self.apis[nom] = (nom_script, retour, template, no_in)
        #     print("apidef apis", apidef, self.apis[nom])




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
            infos["lignes"] =  macro.lignes
            # print ("lecture macro", nom_script, infos)
        else:
            fpath = os.path.join(self.scriptdir, nom_script)
            try:
                script = open(fpath, "r",encoding='cp1252').readlines()
                nomscript=os.path.splitext(nom_script)[0]
            except FileNotFoundError:
                print ("fichier introuvable",fpath)
                raise KeyError
            except UnicodeDecodeError:
                print ("erreur d 'encodage",fpath)
                raise KeyError
            for ligne in script:
                if ligne.startswith("!#api"):
                    self.is_api[nom_script] = True
                    apidef = ligne.split(";")
                    apiname = apidef[1] if len(apidef)>1 else nomscript
                    retour = apidef[2] if len(apidef)>2 else "text"
                    template = apidef[3] if (len(apidef)>3 and apidef[3]!="no_in") else ""
                    no_in = "1" if "no_in" in ligne else "0"
                    infos["no_in"]=no_in
                    auxv=apidef[-1] if '=' in apidef[-1] else ""
                    aux=dict()
                    if auxv:
                        vars=auxv.split(',')
                        aux=[i.split("=") for i in vars]
                    self.apis[apiname] = (nom_script, retour, template, no_in, aux)
                elif ligne.startswith("!#"):
                    if ligne.endswith("\n"):
                        ligne = ligne[:-1]
                    tmp = ligne[2:].split(";",1)
                    if len(tmp) == 1:
                        continue
                    clef, contenu = tmp
                    if clef not in infos:
                        infos[clef] = dict() if clef == "variables" else []
                    if clef == "variables":
                        tmp = contenu.split(";", 2)
                        nom=tmp[0]
                        question=tmp[1] if len(tmp) > 1 else nom
                        defaut=tmp[2] if len(tmp) > 2 else ""
                        infos[clef][nom] = (question,defaut)
                    else:
                        infos[clef].append(contenu)
        self.descriptif[nom_script] = infos
        self.scripts[nom_script] = script
        

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

@app.route("/mw")
@app.route("/mw/")
@app.route("/mw/index")
# @authenticate
def index():

    local = request.host.startswith("127.0.0.1:")
    local=False
    scriptlist.refresh(local)
    current_user=getattr(g,"current_user","non identifié")
    return render_template(
        "index.html",
        text="acces simplifie aux fonctions mapper pour " + current_user,
        title="mapper interface web",
    )


@app.route("/mw/fmgr")
def fmgr():
    print("url ", url_for("flaskfilemanager.index"))
    return redirect(url_for("flaskfilemanager.index"))


@app.route("/mw/folderselect/<fichier>")
def foldeselector(fichier):
    current = session.get("folder", "S:/")
    if fichier and os.path.isfile(os.path.join(current, fichier)):
        session["entree"] = os.path.join(current, fichier)
    else:
        filelist = os.listdir(current)
        fdef = [(i, os.path.isdir(os.path.join(current, i))) for i in filelist]
        return render_template("fileselect.html")


@app.route("/mw/scripts")
def scripts():
    return render_template(
        "scriptlist.html",
        liste=sorted(scriptlist.liste),
        mode="exec",
        c2="Date de Mise a Jour",
    )


@app.route("/mw/macros")
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


@app.route("/mw/apis")
def apis():
    # print("isapi", scriptlist.liste)
    apilist = scriptlist.getapilist()
    return render_template("scriptlist.html", liste=sorted(apilist), mode="api", c2="")


@app.route("/mw/refresh/<mode>")
def refresh(mode):
    local = request.host.startswith("127.0.0.1:")
    local=False
    scriptlist.refresh(local)
    return render_template(
        "scriptlist.html",
        liste=sorted(scriptlist.liste),
        mode=mode,
        c2="Date de Mise a Jour",
    )


@app.route("/mw/statictest/<script>")
def statictest(script):
    return( render_template(url_for("static", filename="statictest/" + script)))


@app.route("/mw/scriptdesc/<script>")
def scriptdesc(script):
    nomscript = scriptlist.getnom(script)
    print("appel scriptdesc", scriptlist.descriptif[nomscript])
    return render_template(
        "scriptdesc.html",
        descriptif=scriptlist.descriptif[nomscript],
        nom=nomscript,
        url=script,
    )


@app.route("/mw/scriptview/<script>")
def scriptview(script):
    nomscript = scriptlist.getnom(script)
    fich_script = os.path.join(scriptlist.scriptdir, nomscript)
    lignes = scriptlist.scripts[nomscript]
    lignes = scriptlist.descriptif[nomscript].get("lignes", lignes)
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
            if i.startswith("!#api"):
                type_ligne = "ltype_api"
            elif i.startswith("!#ihm"):
                type_ligne = "ltype_ihm"
            elif i.startswith("!#help"):
                type_ligne = "ltype_help"

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


@app.route("/mw/edit/<script>")
def edit_script(script):
    nomscript = scriptlist.getnom(script)
    fich_script = os.path.join(scriptlist.scriptdir, nomscript)
    lignes = scriptlist.scripts[nomscript]
    lignes = scriptlist.descriptif[nomscript].get("lignes", lignes)
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
            if i.startswith("!#api"):
                type_ligne = "ltype_api"
            elif i.startswith("!#ihm"):
                type_ligne = "ltype_ihm"
            elif i.startswith("!#help"):
                type_ligne = "ltype_help"

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
    return render_template("scriptview2.html", code=code, nom=nomscript, url=script)










@app.route("/mw/retour_api/<script>")
def retour_api(script):
    stats = session.get("stats")
    retour = session.get("retour")
    nom = url_to_nom(script)
    print ("retour api",stats,retour)
    if stats:
        return render_template(
            "script_result.html", stats=stats, retour=retour, url=script, nom=nom
        )
    return render_template("noresult.html", url=script, nom=nom)


@app.route("/mw/mws")
@app.route("/mws")
def webservicelist():
    apilist = scriptlist.getapilist()
    return jsonify(apilist)


def process_script(nomscript, entree, rep_sortie, scriptparams, mode, local):
    """execute un traitement"""
    stime = time.time()
    print ("process_script", nomscript,scriptparams, mode)
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

def autotemplate(data): # genere un template basique pour l affichage
    pass




@app.route("/mws/<api>", methods=["GET", "POST"])
def webservice(api):
    local = request.host.startswith("127.0.0.1:")
    local=False
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
    # print ("ajout infoscript", infoscript,scriptlist.apis)
    scriptparams.extend(["F_sortie="+infoscript[1],"template="+infoscript[2],"sans_entree="+infoscript[3]])
    retour = process_script(
        nomscript, entree, rep_sortie, scriptparams, "webservice", local
    )
    wstats, result, tmpdir = retour
    print ("-----------retour script",infoscript)
    if result:
        if infoscript[1]=="link": #retour url
            url=result["print"][0] if result["print"] else ""
            if url:
                return redirect(url)
        elif infoscript[1]=="html": #retour html direct
                data=result["print"] if result["print"] else ""
                
                if infoscript[2]: #(template)
                    template=open(infoscript[2].readlines())
                    return render_template_string(template,data)
                else:
                    return render_template_string(autotemplate(data),data)
        elif infoscript[1]=="json": #retour json
                # print ("retour web ", [i._asdict() for i in result["print"]])
                if "print" in result and result["print"]:
                    return jsonify([i._asdict() for i in result["print"]])
                elif "log" in result:
                    return jsonify(result["log"])
                else:
                    return redirect(code=404)


        elif "print" in result:
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


@app.route("/mw/exec/<appel>/<mode>", methods=["GET", "POST"])
def execscript(appel, mode):
    # print("dans exec", script)
    local = request.host.startswith("127.0.0.1:")
    local=False
    ws = mode == "api"
    if ws:
        infoscript = scriptlist.apis.get(appel)
        print ("recup script",appel, "->",infoscript)
        if not infoscript:
            return "erreur script non trouve %s (%s)" % (
                appel,
                str(list(scriptlist.apis.keys())),
            )
        script = infoscript[0]
        format_retour = infoscript[1]
    else:
        script = appel
        format_retour="auto"
    nomscript = "#" + script[1:] if script.startswith("_") else script
    scriptlist.refreshscript(nomscript)
    fich_script = (
        nomscript
        if nomscript.startswith("#")
        else os.path.join(scriptlist.scriptdir, nomscript)
    )
    infos = scriptlist.descriptif[nomscript]
    infos["__mode__"] = mode
    infos["__api_name__"] = appel
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
            print("mode webservice ", wsurl)
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
        "prep_exec.html", nom=nomscript, form=form, varlist=varlist, url=appel, ws=ws, format_retour=format_retour
    )


# @app.route("/mw/plantage/<script>")
# def fail(script):
#     nom = url_to_nom(script)
#     return render_template(
#         "plantage.html", text="erreur d'execution", nom=nom, url=script
#     )
@app.route("/mw/interacif/<appel>/<mode>", methods=["GET", "POST"])
def execscriptihm(appel, mode):
    # print("dans exec", script)
    local = request.host.startswith("127.0.0.1:")
    local=False
    ws = mode == "api"
    if ws:
        infoscript = scriptlist.apis.get(appel)
        print ("recup script",appel, "->",infoscript)
        if not infoscript:
            return "erreur script non trouve %s (%s)" % (
                appel,
                str(list(scriptlist.apis.keys())),
            )
        script = infoscript[0]
        format_retour = infoscript[1]
    else:
        script = appel
        format_retour="auto"
    nomscript = "#" + script[1:] if script.startswith("_") else script
    scriptlist.refreshscript(nomscript)
    fich_script = (
        nomscript
        if nomscript.startswith("#")
        else os.path.join(scriptlist.scriptdir, nomscript)
    )
    infos = scriptlist.descriptif[nomscript]
    infos["__mode__"] = mode
    infos["__api_name__"] = appel
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
            print("mode webservice ", wsurl)
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
        "prep_exec.html", nom=nomscript, form=form, varlist=varlist, url=appel, ws=ws, format_retour=format_retour
    )






@app.route("/mw/result/<script>")
def showresult(script):
    stats = session.get("stats")
    retour = session.get("retour")
    
    nom = url_to_nom(script)
    if stats:
        return render_template(
            "script_result.html", stats=stats, retour=retour, url=script, nom=nom
        )
    return render_template("noresult.html", url=script, nom=nom)


@app.route("/mw/login", methods=["GET", "POST"])
@app.route("/mw/login/<script>", methods=["GET", "POST"])
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
        return redirect("/mw/index")
    return render_template(
        "login.html", title="Sign In", form=form, nom=nom, url=script
    )


@app.route("/mw/srvcontrol/<cmd>")
def srvcontrol(cmd):
    """interface de controle du serveur"""
    if cmd=="shutdown":
        os._exit(99)

@app.route("/mw/help")
def show_help():
    return render_template("help.html")


@app.route("/mw/favicon.ico")
def favicon():
    return url_for("static", filename="images/favicon.ico")


@app.route("/mw/intro")
def show_intro():
    return render_template("intro.html")


@app.route("/mw/fm")
def fileman():
    return redirect("/mw/fm/index.html")
