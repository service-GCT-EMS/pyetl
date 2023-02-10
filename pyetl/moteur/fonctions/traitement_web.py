# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de chargement web up/download http et ftp + acces web services
"""
import logging
import os
import io
import csv
import json
import re

import requests as RQ
from requests.auth import HTTPBasicAuth
import ftplib as FTP

try:
    import pysftp as SFTP

except ImportError:
    SFTP = None


# def importftp():
#     """import ftp"""
#     global SFTP, FTP
#     import ftplib as FTP

#     try:
#         import pysftp as SFTP

#     except ImportError:
#         SFTP = None


import time

LOGGER = logging.getLogger(__name__)


def geocode_traite_stock(regle, final=True):
    """libere les objets geocodes"""
    # global RQ
    if regle.nbstock == 0:
        return
    flist = list(regle.filtres.values())
    adlist = regle.params.att_entree.liste
    prefix = regle.params.cmp1.val
    outcols = 2 + len(flist)
    header = []
    suite = regle.branchements.brch["endstore"]
    fail = regle.branchements.brch["fail"]
    traite = regle.stock_param.moteur.traite_objet
    geocodeur = regle.getvar("url_geocodeur")
    data={"columns": "_adresse"}
    data.update(regle.filtres)
    buffer = (
        ";".join(["ident", "_adresse"] + flist)
        + "\n"
        + "\n".join(
            [
                str(n)
                + ";"
                + " ".join(
                    [
                        str(obj.attributs.get(i, "")).replace("\n", " ").replace('"', "")
                        for i in adlist
                    ]
                )
                + (
                    (
                        ";"
                        + ";".join(
                            [
                                obj.attributs.get(i, "")
                                .replace("\n", " ")
                                .replace('"', "")
                                for i in flist
                            ]
                        )
                    )
                    if flist
                    else ""
                )
                for n, obj in enumerate(regle.tmpstore)
            ]
        )
    ).encode("utf-8")

    print('geocodage', regle.nbstock, "adlist",adlist,"flist",flist,"data", data)

    files = {"data": io.BytesIO(buffer)}
    try:
        res = RQ.post(geocodeur, files=files, data=data)
    except RQ.RequestException as prob:
        regle.stock_param.logger.error("geocodeur non accessible %s", geocodeur)
        regle.stock_param.logger.exception("erreur", exc_info=prob)
        # print("url geocodeur defectueuse", geocodeur)
        # print("exception levee", prob)

        raise StopIteration(2)
    # print ('retour', res.text)

    #        print ('retour ',buf)
    for row in csv.reader(res.text.split("\n"), delimiter=";"):
        attributs = row
        if not attributs:
            continue

        if attributs[0].isnumeric():
            numero = int(attributs[0])
            obj = regle.tmpstore[numero]
            obj.attributs.update(
                [(nom, contenu) for nom, contenu in zip(header, attributs[outcols:])]
            )
            # print ('retour',obj)
            score = obj.attributs.get(prefix+"result_score", "")
            if not score:
                regle.stock_param.logger.error(
                    "erreur geocodage %s", ",".join(attributs)
                )
                # print("erreur geocodage", attributs)
            traite(obj, suite if score else fail)
        elif not header:
            header = [prefix + i for i in attributs[outcols:]]
            # print ('calcul header', header)
            obj = regle.tmpstore[0]
            if obj.schema:
                # print ('geocodage action schema',regle.action_schema, header)
                obj.schema.force_modif(regle)
                regle.liste_atts = header
                regle.action_schema(regle, obj)
                # print ('schema :', obj.schema)
        else:
            if not final:
                regle.stock_param.logger.warning(
                    "recu truc etrange %s", ",".join(attributs)
                )
                # print("geocodeur: recu truc etrange ", attributs)
                # print("retry")
                # geocode_traite_stock(regle, final=True)
                return

    # and regle in obj.schema.regles_modif
    regle.traite += regle.nbstock
    regle.nbstock = 0
    if not regle.getvar("_testmode"):
        print(
            "geocodage %d objets en %d secondes (%d obj/sec)"
            % (
                regle.traite,
                int(time.time() - regle.tinit),
                regle.traite / (time.time() - regle.tinit),
            )
        )
    regle.tmpstore = []


def h_geocode(regle):
    """prepare les espaces de stockage et charge le geocodeur addok choisi"""
    LOGGER.info("geocodeur utilise  %s", regle.getvar("url_geocodeur"))
    LOGGER.info("liste_filtres demandes %s", regle.params.cmp2.liste)
    # importrequest()

    regle.blocksize = int(regle.getvar("geocodeur_blocks", 1000))
    regle.store = True
    regle.nbstock = 0
    regle.traite = 0
    regle.traite_stock = geocode_traite_stock
    regle.tmpstore = []
    regle.liste_atts = []
    regle.scoremin = 0
    regle.filtres = dict(i.split("=") for i in regle.params.cmp2.liste)
    regle.tinit = time.time()
    return True


def f_geocode(regle, obj):
    """#aide||geocode des objets en les envoyant au gecocodeur addict
    #aide_spec||en entree clef et liste des champs adresse a geocoder score min pour un succes
    #parametres||liste attributs adresse;;prefixe;liste filtres
    #pattern||;;L;geocode;?C;?LC
    #schema||ajout_att_from_liste
    #req_test||url_geocodeur
    #test||obj||^X;1 parc de l'etoile Strasbourg;;set||^;;X;geocode;;||atv:result_housenumber:1
    """
    #    clef = obj.attributs.get(regle.params.cmp1.val)
    #    print("avant geocodeur", regle.nbstock)
    regle.tmpstore.append(obj)
    #    regle.ageocoder[clef] = ";".join([obj.attributs.get(i,"")
    #                                      for i in regle.params.att_entree.liste])
    #    print("geocodeur", regle.nbstock)
    regle.nbstock += 1
    if regle.nbstock >= regle.blocksize:
        regle.traite_stock(regle, final=False)
    return True


def h_ftpupload(regle):
    """prepare les parametres ftp"""
    # importftp()
    if regle.params.pattern == "1":
        regle.chargeur = True
    codeftp = regle.params.cmp1.val
    regle.ftp = None
    if codeftp:
        serveur = regle.context.getvar("server_" + codeftp, "")
        servertyp = regle.context.getvar("ftptyp_" + codeftp, "")
        port = regle.context.getvar("port_" + codeftp, "")
        user = regle.context.getvar("user_" + codeftp, "")
        passwd = regle.context.getvar("passwd_" + codeftp, regle.params.cmp2.val)
        regle.setlocal("acces_ftp", (codeftp, serveur, servertyp, user, passwd,port))
        regle.servertyp = servertyp
        regle.destdir = regle.params.cmp2.val
    else:  # connection complete dans l'url
        regle.servertyp = "direct"
        # regle.destdir = getftpinfo(regle, regle.params.cmp2.val)


def getftpinfo(regle, fichier):
    """extrait l'info ftp de l'url"""
    if fichier.startswith("ftp://"):
        servertyp = "ftp"
        fichier = fichier[6:]
    elif fichier.startswith("sftp://"):
        servertyp = "sftp"
        fichier = fichier[7:]
    else:
        regle.stock_param.logger.error("service FTP inconnu %s", fichier)
        # print("service FTP inconnu", fichier, regle)
        raise FTP.error_perm
    acces, elem = fichier.split("@", 1)
    user, passwd = acces.split(":", 1)
    serveur, fich = elem.split("/", 1)
    codeftp = "tmp"
    regle.setlocal("acces_ftp", (codeftp, serveur, servertyp, user, passwd))
    return fich


def ftpconnect(regle):
    """connection ftp"""
    # global FTP,SFTP
    _, serveur, servertyp, user, passwd,port = regle.getvar("acces_ftp")
    if regle.debug:
        regle.stock_param.logger.info("ouverture acces %s", regle.getvar("acces_ftp"))
        # print("ouverture acces ", regle.getvar("acces_ftp"))
    try:
        if servertyp == "tls":
            regle.ftp = FTP.FTP_TLS(host=serveur, user=user, passwd=passwd)
            return True
        elif servertyp == "ftp":
            regle.ftp = FTP.FTP(host=serveur, user=user, passwd=passwd)
            return True
    except FTP.error_perm as err:
        regle.stock_param.logger.error(
            "erreur ftp: acces non autorisé %s %s %s", serveur, servertyp, user
        )
        # print("!!!!! erreur ftp: acces non autorisé", serveur, servertyp, user, passwd)
        regle.stock_param.logger.exception("retour_erreur", exc_info=err)
        # print("retour_erreur", err)
        return False
    if servertyp == "sftp" and SFTP:
        try:
            cno = SFTP.CnOpts()
            cno.hostkeys = None
            if port=="":
                port=22
            else:
                port=int(port)
            regle.ftp = SFTP.Connection(
                serveur, username=user, password=passwd, cnopts=cno, port=port
            )
            return True
        except (SFTP.ConnectionException,SFTP.AuthenticationException) as err:

            print(
                "!!!!! erreur ftp: acces non autorisé", serveur, port, servertyp, user, passwd
            )
            print("retour_erreur", err)
            return False
    else:

        print("mode ftp non disponible", servertyp)
        return False


def uploadfile(regle, filename):
    # upload un fichier
    destname = regle.destdir + "/" + str(os.path.basename(filename))
    localfile = open(filename, "rb")
    regle.ftp.storbinary("STOR " + destname, localfile)
    localfile.close()
    # print("transfert effectue", filename, "->", destname)


def f_ftpupload(regle, obj):
    """#aide||charge un fichier sur ftp
    #aide_spec||;nom fichier; (attribut contenant le nom);ftp_upload;ident ftp;chemin ftp
      #pattern1||;?C;?A;ftp_upload;?C;?C
      #pattern2||;=#att;A;ftp_upload;?C;C
         #test||notest
    """

    filename = regle.getval_entree(obj)
    destname = regle.destdir + "/" + str(os.path.basename(filename))

    # destname = regle.destdir
    if not regle.ftp:
        retour = ftpconnect(regle)
        if not retour:
            return False
        if regle.debug:
            print("connection ftp etablie")

    try:
        # print ('envoi fichier',filename,'->',destname)
        if regle.servertyp == "sftp":
            regle.ftp.cwd(regle.destdir)
            regle.ftp.put(filename)
            if regle.debug:
                print("transfert effectue", filename, "->", destname)
        else:
            if regle.params.pattern == "2":
                input = io.BytesIO()
                input = obj.attributs[regle.params.att_entree.val].encode("utf8")
                regle.ftp.storbinary("STOR " + destname, input.read)
                input.close()
            else:
                if os.path.isdir(filename):
                    for fich in os.listdir(filename):
                        uploadfile(regle, os.path.join(filename, fich))
                else:
                    uploadfile(regle, filename)
                    # localfile = open(filename, "rb")
                    # regle.ftp.storbinary("STOR " + destname, localfile)
                    # localfile.close()
            if regle.debug:
                print("transfert effectue", filename, "->", destname)
        return True

    except FTP.all_errors as err:
        print("!!!!! erreur ftp:", err)
        LOGGER.error(
            "ftp upload error: Houston, we have a %s", "major problem", exc_info=True
        )
        return False


def f_ftpdownload(regle, obj):
    """#aide||charge un fichier sur ftp
    #aide_spec||;nom fichier; (attribut contenant le nom);ftp_download;ident ftp;repertoire
     #pattern1||;?C;?A;ftp_download;C;?C
     #pattern2||;?C;?A;ftp_download;;
     #pattern3||A;?C;?A;ftp_download;;
     #pattern4||A;?C;?A;ftp_download;C;?C
       #helper||ftpupload
         #test||notest
    """
    filename = regle.getval_entree(obj)
    if regle.servertyp == "direct":
        filename = getftpinfo(regle, regle.getval_entree(obj))
    if not regle.ftp:
        retour = ftpconnect(regle)
        if not retour:
            return False
        if regle.debug:
            print("connection ftp etablie")
    if not regle.params.att_sortie.val:
        localdir = regle.getvar("localdir", os.path.join(regle.getvar("_sortie", ".")))
        if filename.startswith('/'):
            localname = os.path.join(localdir, filename[1:])
        else:
            localname = os.path.join(localdir, filename)
        os.makedirs(os.path.dirname(localname), exist_ok=True)
        if regle.debug:
            print("creation repertoire", os.path.dirname(localname))
    else:
        localname = "[" + regle.params.att_sortie.val + "]"
        localdir = "."

    try:
        if regle.servertyp == "sftp":
            if regle.debug:
                print("choix repertoire", regle.destdir)
            regle.ftp.cwd(regle.destdir)
            if filename == "*":
                regle.ftp.get_d(".", localdir, preserve_mtime=True)
            elif filename == "*/*":
                regle.ftp.get_r(".", localdir, preserve_mtime=True)
            else:
                regle.ftp.get(filename, localpath=localname, preserve_mtime=True)
        else:
            if regle.params.att_sortie.val:
                output = io.BytesIO()
                regle.ftp.retrbinary("RETR " + filename, output.write)
                obj.attributs[regle.params.att_sortie.val] = output.getvalue().decode(
                    "utf8"
                )
                output.close()
            else:
                localfile = open(localname, "wb")
                regle.ftp.retrbinary("RETR " + filename, localfile.write)
                localfile.close()
        if regle.debug:
            print("transfert effectue", filename, "->", localname)
        return True

    except FTP.all_errors as err:
        print("!!!!! erreur ftp:", err,filename,localdir,localname)
        LOGGER.error("erreur transfert ftp: %s -> %s %s\n%s",filename,localdir,localname
            , exc_info=True

        )
        return False


def _to_dict(parms):
    """transforme un texte de type aa:yy,tt:vv en dictionnaire"""
    if not parms:
        return dict()
    if "'" in parms:
        # il y a des cotes
        cot = False
        groups = []
        group = ""
        for i in parms:
            if i == "'":
                cot = not cot
            elif i == "," and not cot:
                groups.append(group)
                group = ""
            else:
                group += i
        if group:
            groups.append(group)
        return dict([k.split(":", 1) for k in groups])
    return dict([k.split(":", 1) for k in parms.split(",")])


def httpconnect(regle):
    """connection http"""
    # global FTP,SFTP
    acces = regle.getvar("site")
    if acces:
        regle.stock_param.load_paramgroup(acces, nom=acces)
    regle.authtyp = regle.getvar("authtyp_" + acces)
    regle.user = regle.getvar("user_" + acces)
    regle.passwd = regle.getvar("passwd_" + acces)
    regle.racinesite = regle.getvar("server_" + acces)
    if regle.authtyp == "ntlm":
        if regle.user:
            from requests_ntlm import HttpNtlmAuth

            regle.auth = HttpNtlmAuth(regle.user, regle.passwd)
            regle.stock_param.logger.info(
                "connection ntlm: %s en t tant que %s", acces, regle.user
            )
            # from requests_negotiate_sspi import HttpNegotiateAuth

            # regle.auth = HttpNegotiateAuth(
            #     username=regle.user, password=regle.passwd, domain="cus.fr"
            # )
        else:
            from requests_negotiate_sspi import HttpNegotiateAuth

            regle.auth = HttpNegotiateAuth()
            regle.stock_param.logger.info("connection ntlm sso windows sur %s", acces)
    elif regle.authtyp == "basic":
        regle.auth = HTTPBasicAuth(regle.user, regle.passwd)
        print("authent", regle.auth)


def h_httpdownload(regle):
    """prepare les parametres http"""
    # importrequest()
    regle.racinesite = ""
    regle.auth = None
    regle.agents = {
        "chrome": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1",
        "firefox": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "opera": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41",
        "edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        "safari": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1",
    }
    regle.chargeur = True
    if regle.getvar("site") or regle.getvar("authtyp_"):
        httpconnect(regle)
        print("connection", regle.authtyp)

    if regle.params.pattern == "1":
        path = (
            regle.params.cmp1.val if regle.params.cmp1.val else regle.getvar("_sortie")
        )
        if path:
            os.makedirs(path, exist_ok=True)
        regle.path = path
        if regle.params.cmp2.val:
            name = os.path.join(path, regle.params.cmp2.val)
            regle.fichier = name
        else:
            regle.fichier = None
    regle.checkssl = not regle.istrue("trust")
    regle.httparams = _to_dict(regle.getvar("http_params"))
    regle.httheaders = _to_dict(regle.getvar("http_header"))
    agentcode = regle.getvar("#agent")
    if agentcode:
        agent = regle.agents.get(agentcode, agentcode)
        regle.httheaders["User-Agent"] = agent
        regle.stock_param.logger.log("agent utilise: %s", agentcode)
    #
    # print("preparation parametres", regle.httparams, regle.httheaders)
    regle.valide = True
    if regle.params.pattern=='4': #decodage json
        regle.reader = regle.stock_param.getreader("json", regle)
    # regle.debug = regle.istrue("debug")
    # print("h_httpdownload valeur de debug", regle.debug)
    return True


def _jsonsplitter(regle, obj, jsonbloc):
    """decoupe une collection json en objets"""
    verbose=regle.istrue("verbose")
    try:
        struct = json.loads(jsonbloc)
    except json.JSONDecodeError as err:
        regle.stock_param.logger.error("erreur decodage json %s %s", err, repr(jsonbloc))
        return
    nom=""
    if len(struct)==1:
        #il y a in titre
        
        for nom,contenu in struct.items():
            pass
        
        struct=contenu
    selected=regle.params.cmp2.liste
    if verbose:
        regle.stock_param.logger.info('recup contenu %s', nom)
    if isinstance (contenu,dict):
        if verbose:
            regle.stock_param.logger.info('contenu %s', repr(list(contenu.keys())))
        for classe,elem in struct.items():
            if selected and classe not in selected:
                if verbose:
                    regle.stock_param.logger.info('non selectionne %s',classe)
                    # print ('jsonsplitter non selectionne',classe)
                continue
            # print ('traitement elem', classe,type(elem))
            if isinstance(elem, list):
                #c est une liste d objets
                if obj.virtuel:
                    regle.reader.setidententree(nom,classe)
                    # print ('presence schema', regle.reader.cree_schema)
                for objdef in elem:
                    if isinstance(objdef,dict):
                        if obj.virtuel:
                            obj2=regle.getobj((nom,classe))
                            # print ("jsonsplitter: cree",nom,classe,"->",obj2)
                        else:
                            obj2 = obj.dupplique()
                            obj2.attributs['#classe']=classe
                            obj2.attributs['#groupe']=nom
                        #c est une definition d objet
                        for att, val in objdef.items():
                            if isinstance(val, str) or regle.istrue("keepjson"):
                                obj2.attributs[att] = val
                            elif isinstance(val, dict):
                                hdict = {
                                    i: json.dumps(j, separators=(",", ":")) for i, j in val.items()
                                }
                                obj2.sethtext(att, dic=hdict)
                            elif isinstance(val, list):
                                jlist = [json.dumps(j, separators=(",", ":")) for j in val]
                                obj2.setmultiple(att, liste=jlist)
                            if obj2.schema:
                                if att not in obj2.schema.attributs:
                                    if regle.istrue("keepjson"):
                                        type_att="J"
                                    else:
                                        type_att = "H" if isinstance(val, dict) else "T"
                                    obj2.schema.stocke_attribut(att, type_att)

                        regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])
            else:
                regle.stock_param.logger.error("element incompatible %s : %s", repr(elem), type(elem))


def f_httpdownload(regle, obj):
    """#aide||telecharge un fichier via http
    #aide_spec||l'entete du retour est stocke dans l'attribut #http_header
    #parametres1||url;attribut contenant l'url;;repertoire;nom
    #aide_spec1||telecharge un element vers un fichier ou un repertoire
      #pattern1||;?C;?A;download;?C;?C
    #aide_spec2||telecharge un element vers un attribut
    #parametres2||attribut de sortie;url;attribut contenant l'url;;
      #pattern2||A;?C;?A;download;
    #aide_spec3||telecharge un element vers un attribut en mode binaire
    #parametres3||attribut de sortie;url;attribut contenant l'url;;
      #pattern3||A;?C;?A;download;=#B||cmp1
    #aide_spec4||telecharge un element json et genere un objet par element
    #parametres4||url;attribut contenant l'url;;;
      #pattern4||;?C;?A;download;=#json;?LC||cmp1
    #variables||trust;si vrai(1,t,true...) les certificats ssl du site ne sont pas verifies
              ||http_encoding;force l encoding du rettour par defaut c est celui de l entete http
         #test||notest
    """
    url = regle.racinesite + regle.getval_entree(obj)
    # if regle.debug:
    # print("telechargement", url, "-->", regle.fichier)
    # if regle.httparams:
    retour = None
    # auth = regle.auth
    # if regle.auth:
    #     auth = regle.auth(regle.user, regle.passwd) if regle.user else regle.auth()
    # print("trouve auth", regle.auth)
    try:
        retour = RQ.get(
            url,
            stream=regle.params.pattern == "1",
            params=regle.httparams,
            headers=regle.httheaders,
            verify=regle.checkssl,
            auth=regle.auth,
        )

        # retour = RQ.get(
        #     url,
        #     auth=regle.auth(regle.user, regle.passwd),
        #     headers=regle.httheaders,
        # )
    except Exception as err:
        print(err)
        LOGGER.error("connection impossible:->%s<-", retour.url if retour else url)
        return False

    if regle.debug:
        print("telechargement", url, retour.url if retour else url)
        print("info", retour.headers)
    obj.sethtext("#http_header", dic=retour.headers)
    taille = int(retour.headers.get("Content-Length", 0))

    if regle.params.pattern == "2":  # retour dans un attribut
        if regle.getvar("http_encoding"):
            retour.encoding = regle.getvar("http_encoding")

        regle.setval_sortie(obj, retour.text)
        # print("lu http", retour.text)
        return True
    elif regle.params.pattern == "3":
        regle.setval_sortie(obj, retour.content)
        return True
    elif regle.params.pattern == "4":
        # print("recu", retour.text)
        _jsonsplitter(regle, obj, retour.text)
        return True
    if regle.fichier is None:
        fichier = os.path.join(regle.path, os.path.basename(url))
    else:
        fichier = regle.fichier

    decile = taille / 10 if taille else 100000
    recup = 0
    bloc = 4096
    nb_pts = 0
    nblocs = 0
    debut = time.time()
    if retour.status_code == 200:
        with open(fichier, "wb") as fich:
            for chunk in retour.iter_content(bloc):
                nblocs += 1
                recup += bloc  # ca c'est la deco avec des petits points ....
                if recup > decile:
                    recup = recup - decile
                    nb_pts += 1
                    print(".", end="", flush=True)
                fich.write(chunk)
        if nblocs * bloc > taille:
            taille = nblocs * bloc
        print(
            "    ",
            taille,
            "octets télecharges en ",
            int(time.time() - debut),
            "secondes vers ",
            fichier,
        )
        return True
    LOGGER.error("erreur requete %s", retour.url)
    LOGGER.error("headers %s", str(retour.request.headers))
    # print ("==========erreur requete==========")
    # print ("request url", retour.url)
    # print ("request headers", retour.request.headers)
    LOGGER.error("retour statut %s", retour.status_code)
    LOGGER.error("headers %s", str(retour.headers))
    LOGGER.error("text %s", str(retour.text))

    # print ("============retour================")
    # print ("statuscode", retour.status_code)
    # print ("headers", retour.headers)
    # print ("text", retour.text)
    return False


def h_wfsdownload(regle):
    """prepare les parametres http"""
    # importrequest()

    regle.chargeur = True
    regle.path = None
    if regle.params.pattern == "1":
        path = regle.params.att_sortie.val
        if not os.path.isabs(path):
            path = os.path.join(regle.getvar("_sortie"), path)
        regle.path = path

    regle.wfsparams = {"SERVICE": "WFS"}
    regle.wfsparams["OUTPUTFORMAT"] = "text/xml"
    if regle.params.cmp2.val == "json":
        regle.wfsparams["OUTPUTFORMAT"] = "json"


def f_wfsdownload(regle, obj):
    """#aide||recupere une couche wfs
    #aide_spec||; classe;  attribut contenant la classe;wfs;url;format
      #pattern1||F;?C;?A;wfsload;C;?C
      #pattern2||A;?C;?A;wfsload;C;?C
         #test||notest
    """
    # https://data.strasbourg.eu/api/wfs?
    # TYPENAME=ods%3Asections_cadastrales&REQUEST=GetFeature
    # &RESULTTYPE =RESULTS
    # &OUTPUTFORMAT=text%2Fxml%3B+suntype%3Dgml%2F3.1.1
    # &VESRION=1.1&SERVICE=WFS
    url = regle.params.cmp1.val
    params = regle.wfsparams
    params["TYPENAME"] = regle.getval_entree(obj)
    print("wfs", url, params)
    retour = RQ.get(url, params, stream=regle.params.pattern == "1")
    print("info", retour.headers)
    obj.sethtext("#wfs_header", dic=retour.headers)
    taille = int(retour.headers["Content-Length"])

    if regle.params.pattern == "2":  # retour dans un attribut
        regle.setval_sortie(obj, retour.text)
        if obj.virtuel and obj.attributs["#classe"] == "_chargement":  # mode chargement
            regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["gen"])
        # print("apres", obj)
        return True
    if regle.fichier is None:
        fichier = os.path.join(regle.path, os.path.basename(url))
    else:
        fichier = regle.fichier

    decile = taille / 10
    recup = 0
    bloc = 4096
    nb_pts = 0
    debut = time.time()
    if retour.status_code == 200:
        with open(fichier, "wb") as fich:
            for chunk in retour.iter_content(bloc):
                recup += bloc  # ca c'est la deco avec des petits points ....
                if recup > decile:
                    recup = recup - decile
                    nb_pts += 1
                    print(".", end="", flush=True)
                fich.write(chunk)
        print(
            "    ",
            taille,
            "octets télecharges en ",
            int(time.time() - debut),
            "secondes",
        )
        return True
    return False

def h_ssoconnect(regle):
    """aide realise une connection sso"""
    pass

def f_ssoconnect(regle, obj):
    """aide||realise une connection sso uniquement en mode serveur
    pattern||;;;ssoconnect;;;
    """



def h_geom2url(regle):
    """convertit un point en bout d'url pour appel wms/wfs"""
    if regle.params.pattern=="2":
        geom=regle.params.val_entree
        match=re.find('.*\(([0-9]+)\.?[0-9]*,([0-9]+)', geom)
        if match:
            x=match.groups(1)
            y=match.groups(2)
            urlfrag='&c='+x+"%2C"+y
            regle.setvar(regle.params.att_sortie.val,urlfrag)
        else:
            regle.valide=False
            return False



def f_geom2url(regle,obj):
    """aide||convertit un point en bout d'url pour appel wms/wfs
    pattern1||;;;pt2url;;
    pattern2||P;C;pt2url;;
    """
    if obj.initgeom():
        pass
