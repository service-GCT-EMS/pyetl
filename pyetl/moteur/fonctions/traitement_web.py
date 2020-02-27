# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de structurelles diverses
"""
import logging
import os
import io
import requests
import ftplib

try:
    import pysftp

    SFTP = True
except ImportError:
    SFTP = False
import time

LOGGER = logging.getLogger("pyetl")


def geocode_traite_stock(regle, final=True):
    """libere les objets geocodes """
    if regle.nbstock == 0:
        return
    flist = list(regle.filtres.values())
    adlist = regle.params.att_entree.liste
    prefix = regle.params.cmp1.val
    outcols = 2 + len(flist)
    header = []
    suite = regle.branchements.brch["end"]
    fail = regle.branchements.brch["fail"]
    traite = regle.stock_param.moteur.traite_objet
    geocodeur = regle.getvar("url_geocodeur")
    data = {"columns": "_adresse"}.update(regle.filtres)
    buffer = (
        ";".join(["ident", "_adresse"] + flist)
        + "\n"
        + "\n".join(
            [
                str(n)
                + ";"
                + " ".join([obj.attributs.get(i, "") for i in adlist])
                + (
                    (";" + ";".join([obj.attributs.get(i, "") for i in flist]))
                    if flist
                    else ""
                )
                for n, obj in enumerate(regle.tmpstore)
            ]
        )
    ).encode("utf-8")

    # print('geocodage', regle.nbstock, adlist,flist, data)

    files = {"data": io.BytesIO(buffer)}
    res = requests.post(geocodeur, files=files, data=data)
    # print ('retour', res.text)

    #        print ('retour ',buf)
    for ligne in res.text.split("\n"):
        # print ('traitement sortie',ligne)
        if not ligne:
            continue
        attributs = ligne[:-1].split(";")
        # attributs = ligne.split(";")
        if attributs[0].isnumeric():
            numero = int(attributs[0])
            obj = regle.tmpstore[numero]
            obj.attributs.update(
                [(nom, contenu) for nom, contenu in zip(header, attributs[outcols:])]
            )
            # print ('retour',obj)
            score = obj.attributs.get("result_score", "")
            if not score:
                print("erreur geocodage", attributs)
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
                print("geocodeur: recu truc etrange ", ligne)
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
    """ prepare les espaces de stockage et charge le geocodeur addok choisi"""
    if not regle.getvar("_testmode"):
        print("geocodeur utilise ", regle.getvar("url_geocodeur"))
        print("liste_filtres demandes", regle.params.cmp2.liste)
    regle.blocksize = int(regle.getvar("geocodeur_blocks", 1000))
    regle.store = True
    regle.nbstock = 0
    regle.traite = 0
    regle.traite_stock = geocode_traite_stock
    regle.tmpstore = []
    regle.liste_atts = []
    regle.scoremin = 0
    regle.filtres = dict(i.split(":") for i in regle.params.cmp2.liste)
    #    regle.ageocoder = dict()
    regle.tinit = time.time()
    return True


def f_geocode(regle, obj):
    """#aide||geocode des objets en les envoyant au gecocodeur addict
    #aide_spec||en entree clef et liste des champs adresse a geocoder score min pour un succes
    #parametres||liste attributs adresse;;confiance mini;liste filtres
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
    regle.chargeur = True
    codeftp = regle.params.cmp1.val
    regle.ftp = None
    if codeftp:
        serveur = regle.context.getvar("server_" + codeftp, "")
        servertyp = regle.context.getvar("ftptyp_" + codeftp, "")
        user = regle.context.getvar("user_" + codeftp, "")
        passwd = regle.context.getvar("passwd_" + codeftp, regle.params.cmp2.val)
        regle.setlocal("acces_ftp", (codeftp, serveur, servertyp, user, passwd))
        regle.servertyp = servertyp
    else:  # connection complete dans l'url
        regle.servertyp = "direct"
    regle.destdir = regle.params.cmp2.val


def getftpinfo(regle, fichier):
    """extrait l'info ftp de l'url"""
    if fichier.startswith("ftp://"):
        servertyp = "ftp"
        fichier = fichier[6:]
    elif fichier.startswith("sftp://"):
        servertyp = "sftp"
        fichier = fichier[7:]
    else:
        print("service FTP inconnu", fichier)
        raise ftplib.error_perm
    acces, elem = fichier.split("@", 1)
    user, passwd = acces.split(":", 1)
    serveur, fich = elem.split("/", 1)
    codeftp = "tmp"
    regle.setlocal("acces_ftp", (codeftp, serveur, servertyp, user, passwd))
    return fich


def ftpconnect(regle):
    """connection ftp"""
    _, serveur, servertyp, user, passwd = regle.getvar("acces_ftp")
    # print ('ouverture acces ',regle.getvar('acces_ftp'))
    try:
        if servertyp == "tls":
            regle.ftp = ftplib.FTP_TLS(host=serveur, user=user, passwd=passwd)
            return True
        elif servertyp == "ftp":
            regle.ftp = ftplib.FTP(host=serveur, user=user, passwd=passwd)
            return True
    except ftplib.error_perm as err:
        print("!!!!! erreur ftp: acces non autorisé", serveur, servertyp, user, passwd)
        print("retour_erreur", err)
        return False
    if servertyp == "sftp" and SFTP:
        try:
            cno = pysftp.CnOpts()
            cno.hostkeys = None
            regle.ftp = pysftp.Connection(
                serveur, username=user, password=passwd, cnopts=cno
            )
            return True
        except pysftp.ConnectionException as err:
            print(
                "!!!!! erreur ftp: acces non autorisé", serveur, servertyp, user, passwd
            )
            print("retour_erreur", err)
            return False
    else:
        print("mode ftp non disponible", servertyp)
        return False


def f_ftpupload(regle, obj):
    """#aide||charge un fichier sur ftp
  #aide_spec||;nom fichier; (attribut contenant le nom);ftp_upload;ident ftp;
    #pattern||;?C;?A;ftp_upload;C;?C
       #test||notest
    """
    filename = regle.getval_entree(obj)
    destname = regle.destdir + "/" + str(os.path.basename(filename))

    # destname = regle.destdir
    if not regle.ftp:
        retour = ftpconnect(regle)
        if not retour:
            return False
        print("connection ftp etablie")

    try:
        # print ('envoi fichier',filename,'->',destname)
        if regle.servertyp == "sftp":
            regle.ftp.cwd(regle.destdir)
            regle.ftp.put(filename)
            print("transfert effectue", filename, "->", destname)
        else:
            localfile = open(filename, "rb")
            regle.ftp.storbinary("STOR " + destname, localfile)
            localfile.close()
            print("transfert effectue", filename, "->", destname)
        return True

    except ftplib.all_errors as err:
        print("!!!!! erreur ftp:", err)
        LOGGER.error(
            "ftp upload error: Houston, we have a %s", "major problem", exc_info=True
        )
        return False


def f_ftpdownload(regle, obj):
    """#aide||charge un fichier sur ftp
  #aide_spec||;nom fichier; (attribut contenant le nom);ftp_download;ident ftp;repertoire
    #pattern1||;?C;?A;ftp_download;C;?C
    #pattern2||;C;;ftp_download;;
    #pattern3||A;C;;ftp_download;;
     #helper||ftpupload
       #test||notest
    """
    filename = regle.getval_entree(obj)
    if regle.servertyp == "direct":
        filename = getftpinfo(regle, regle.getval_entree(obj))
    if not regle.ftp:
        if not regle.ftp:
            retour = ftpconnect(regle)
            if not retour:
                return False
        print("connection ftp etablie")

    localdir = regle.getvar("localdir", os.path.join(regle.getvar("_sortie", ".")))
    localname = os.path.join(localdir, filename)
    os.makedirs(os.path.dirname(localname), exist_ok=True)
    print("creation repertoire", os.path.dirname(localname))

    try:
        if regle.servertyp == "sftp":
            print("choix repertoire", regle.destdir)
            regle.ftp.cwd(regle.destdir)
            if filename == "*":
                regle.ftp.get_d(".", localdir, preserve_mtime=True)
            elif filename == "*/*":
                regle.ftp.get_r(".", localdir, preserve_mtime=True)
            else:
                regle.ftp.get(filename, localpath=localname, preserve_mtime=True)
        else:
            if regle.params.att_sortie:
                output = io.BytesIO()
                regle.ftp.retrbinary("RETR " + filename, output.write)
                obj.attributs[regle.params.att_sortie] = str(output.getvalue())
                output.close()
            else:
                localfile = open(localname, "wb")
                regle.ftp.retrbinary("RETR " + filename, localfile.write)
                localfile.close()
        print("transfert effectue", filename, "->", localname)
        return True

    except ftplib.all_errors as err:
        print("!!!!! erreur ftp:", err)
        LOGGER.error(
            "ftp download error: Houston, we have a %s", "major problem", exc_info=True
        )
        return False


def h_httpdownload(regle):
    """prepare les parametres http"""
    regle.chargeur = True
    path = regle.params.cmp1.val if regle.params.cmp1.val else regle.getvar("_sortie")
    os.makedirs(path, exist_ok=True)
    regle.path = path
    if regle.params.cmp2.val:
        name = os.path.join(path, regle.params.cmp2.val)
        regle.fichier = name
    else:
        regle.fichier = None


def f_httpdownload(regle, obj):
    """aide||telecharge un fichier via http
 #aide_spec||; url; (attribut contenant le url);http_download;repertoire;nom
   #pattern1||;?C;?A;download;?C;?C
   #pattern2||S;?C;?A;download
      #test||notest
      """
    url = regle.getval_entree(obj)
    print("telechargement", url)
    retour = requests.get(url, stream=regle.params.pattern == "1")
    print("info", retour.headers)
    obj.sethtext("#http_header", dic=retour.headers)
    taille = int(retour.headers["Content-Length"])

    if regle.params.pattern == "2":  # retour dans un attribut
        regle.setval_sortie(obj, retour.text)
        if obj.virtuel and obj.attributs["#classe"] == "_chargement":  # mode chargement
            regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["next"])
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
