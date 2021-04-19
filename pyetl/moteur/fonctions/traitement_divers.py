# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de structurelles diverses
"""
import os
import re
import logging
from collections import defaultdict, OrderedDict, namedtuple

try:
    import psutil
except ImportError:
    psutil = None
from .outils import renseigne_attributs_batch


# LOGGER = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)


def store_traite_stock(regle):
    """ relache les objets """
    store = regle.tmpstore

    reverse = regle.params.cmp2.val == "rsort"
    #    print ("tri inverse ",reverse)
    if isinstance(store, list):
        if regle.params.cmp2.val:
            keyval = lambda obj: "|".join(
                obj.attributs.get(i, "") for i in regle.params.att_entree.liste
            )
            store.sort(key=keyval, reverse=reverse)
        for obj in store:
            # print("store: relecture objet ", obj)
            regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["end"])
    else:
        for clef in (
            sorted(store.keys(), reverse=reverse) if regle.params.cmp2.val else store
        ):
            obj = store[clef]
            regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["end"])
    h_stocke(regle)  # on reinitialise


def h_stocke(regle):
    """marque la regle comme stockante"""
    #    print ('stockage tmpstore ', regle.params.att_entree.liste)
    regle.store = True
    regle.stocke_obj = True  # on stocke les objets et pas que la clef
    regle.nbstock = 0
    regle.traite_stock = store_traite_stock
    regle.tmpstore = dict() if regle.params.cmp1.val else list()
    # mode comparaison : le stock est reutilise ailleurs (direct_reuse)=False
    regle.direct_reuse = not "cmp" in regle.params.cmp1.val
    if regle.direct_reuse:
        regle.tmpstore = dict() if regle.params.cmp1.val else list()
    else:
        if regle.params.cmp2.val not in regle.stock_param.store:
            regle.stock_param.store[regle.params.cmp2.val] = dict()
        regle.tmpstore = regle.stock_param.store[regle.params.cmp2.val]
    regle.fold = regle.params.cmp1.val == "cmpf"
    regle.cnt = regle.params.cmp1.val == "cnt"
    if regle.params.cmp2.val == "clef":
        regle.stocke_obj = False
        regle.tmpstore = set()


def f_stocke(regle, obj):
    """#aide||stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie
     #aide_spec||liste de clefs,tmpstore;uniq;sort|rsort : stockage avec option de tri
    #aide_spec2||liste de clefs,tmpstore;cmp;nom : prechargement pour comparaisons
      #pattern1||;;?L;tmpstore;?=uniq;?=sort;||cmp1
      #pattern2||;;?L;tmpstore;?=uniq;?=rsort;||cmp1
      #pattern3||;;?L;tmpstore;=cmp;#C||cmp1
      #pattern4||;;?L;tmpstore;=cmpf;#C||cmp1
      #pattern5||S;;?L;tmpstore;=cnt;?=clef||cmp1
          #test||obj;point;4||^;;V0;tmpstore;uniq;rsort||^;;C1;unique||atv;V0;3;
         #test2||obj;point;4||^V2;;;cnt;-1;4;||^;;V2;tmpstore;uniq;sort||^;;C1;unique;||atv;V2;1;
    """
    #    regle.stock.append(obj)
    # if obj.virtuel:
    #     return True
    # print("store: stockage objet ", obj)

    if regle.direct_reuse:
        regle.nbstock += 1

    if regle.params.cmp1.val:
        if len(regle.params.att_entree.liste) > 1:
            clef = "|".join(
                obj.attributs.get(i, "") for i in regle.params.att_entree.liste
            )
        else:
            clef = obj.attributs.get(regle.params.att_entree.val, "")
        if regle.stocke_obj:
            if regle.cnt:
                cnt = 1
                if clef in regle.tmpstore:
                    obj = regle.tmpstore[clef]
                    cnt += int(obj.attributs[regle.params.att_sortie.val])
                obj.attributs[regle.params.att_sortie.val] = str(cnt)
            regle.tmpstore[clef] = obj
        else:
            regle.tmpstore.add(clef)
        return True
    # print("store: stockage objet ", regle.nbstock, obj)
    regle.tmpstore.append(obj)
    return True


def h_uniq(regle):
    """ stocke les clefs pour l'unicite """
    regle.tmpstore = set()


def f_uniq(regle, obj):
    """#aide||unicite de la sortie laisse passer le premier objet et filtre le reste
    #aide_spec||liste des attibuts devant etre uniques si #geom : test geometrique
    #pattern||;?=#geom;?L;unique;;;
    #test||obj;point;2||^;;C1;unique||+fail:;;;;;;;pass>;;||^;;;pass;||cnt;1
    #test2||obj;point;2||^;;C1;unique-||cnt;1
    #test3||obj;point;2||^;#geom;;unique-||cnt;1
    #test4||obj;point;2||^;#geom;C1;unique-||cnt;1
    """
    #    regle.stock.append(obj)
    clef = (
        str(tuple(tuple(i) for i in obj.geom_v.coords))
        if regle.params.val_entree.val == "#geom"
        else ""
    )
    clef = clef + "|".join(
        obj.attributs.get(i, "") for i in regle.params.att_entree.liste
    )

    #    print ('uniq ',clef, regle.params.att_entree.val )
    if clef in regle.tmpstore:
        return False
    regle.tmpstore.add(clef)
    return True


def h_uniqcnt(regle):
    """ stocke les clefs pour l'unicite """
    regle.maxobj = regle.params.cmp1.num if regle.params.cmp1.num else 1
    regle.cnt = regle.maxobj != 1
    regle.tmpstore = defaultdict(int)


def f_uniqcnt(regle, obj):
    """#aide||unicite de la sortie laisse passer les N premiers objet et filtre le reste
    #pattern||A;?=#geom;?L;unique;?N;||sortie
     #schema||ajout_attribut
       #test||obj;point;4||^X;;C1;unique;2;||+fail:;;;;;;;pass>;;||cnt;2
      #test2||obj;point;4||^X;;C1;unique-;2;||cnt;2
      #test3||obj;point;4||^X;#geom;;unique-;2;||cnt;2
      #test4||obj;point;4||^X;#geom;C1;unique-;2;||cnt;2
      #test4||obj;point;4||V0;1;;;V0;2;;set;;;||^X;#geom;V0;unique>;1;;||cnt;1
    """
    #    regle.stock.append(obj)
    clef = (
        str(tuple(tuple(i) for i in obj.geom_v.coords))
        if regle.params.val_entree.val == "#geom"
        else ""
    )
    clef = clef + "|".join(
        obj.attributs.get(i, "") for i in regle.params.att_entree.liste
    )
    regle.tmpstore[clef] += 1
    obj.attributs[regle.params.att_sortie.val] = str(regle.tmpstore[clef])
    if regle.tmpstore[clef] > regle.maxobj:
        return False
    return True


def sortir_traite_stock(regle):
    """ecriture finale"""
    if regle.final:
        try:
            #            print('ecriture finale', regle.output.ecrire_objets)
            regle.output.ecrire_objets(regle, True)
        except IOError as err:
            LOGGER.error("erreur d'ecriture: " + repr(err))
        regle.nbstock = 0
        return
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recup_objets(groupe):
            regle.output.ecrire_objets_stream(obj, regle, False)
            regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["end"])
    regle.nbstock = 0


def h_sortir(regle):
    """preparation sortie"""
    regle.writerparms = dict()
    regle.ressource = None
    regle.writerparms["newlines"] = None
    if regle.getvar("newlines"):
        regle.writerparms["newlines"] = regle.getvar("newlines")
    regle.writerparms["fanout"] = regle.context.getvar("fanout", "groupe")
    if (
        regle.params.att_sortie.val == "#schema"
    ):  # on force les noms de schema pour l'ecriture
        regle.nom_fich_schema = regle.params.val_entree.val
    else:
        regle.nom_fich_schema = regle.params.cmp2.val
    regle.nom_base = os.path.basename(
        regle.params.cmp2.val if regle.params.cmp2.val else regle.nom_fich_schema
    )

    if regle.debug:
        print("nom de schema ", regle.nom_fich_schema)

    if "[" in regle.params.cmp1.val:  # on a defini un fanout
        tmplist = regle.params.cmp1.val.find("[")
        # print("valeur ii ", regle.params.cmp1,ii)
        regle.writerparms["fanout"] = regle.params.cmp1.val[tmplist + 1 : -1]
        # regle.setlocal("fanout", regle.params.cmp1.val[tmplist + 1 : -1])
        regle.params.cmp1.val = regle.params.cmp1.val[:tmplist]
    fich_sortie = ""
    if regle.params.cmp2.val != "#print":
        rep_base = regle.getvar("_sortie")
        #   print('positionnement sortie', rep_base, os.path.join(rep_base, regle.params.cmp2.val))
        if regle.params.cmp2.val and os.path.isabs(regle.params.cmp2.val):
            # si absolu on ignore le rep de sortie
            rep_base = ""
        fich_sortie = os.path.join(rep_base, regle.params.cmp2.val)

    outformat = (
        "#print"
        if (
            regle.params.cmp2.val == "#print"
            or regle.getvar("_sortie") == "#print"
            or fich_sortie == ""
        )
        else regle.params.cmp1.val
    )
    regle.output = regle.stock_param.getoutput(outformat, regle)
    if outformat != "#print":
        regle.output.writerparms["destination"] = regle.params.cmp2.val
    if regle.debug:
        print("creation output", regle.output.writerparms)

    if regle.output.nom_format == "sql":
        # gestion des dialectes sql et du mode connecté
        destination = regle.output.writerparms.get("base_dest")
        dialecte = regle.output.writerparms.get("dialecte")
        regle.output.writerparms["reinit"] = regle.getvar("reinit")
        regle.output.writerparms["nodata"] = regle.getvar("nodata")
        if destination:  # on va essayer de se connecter
            connection = regle.stock_param.getdbaccess(regle, destination)
            if connection and connection.valide:
                regle.output.gensql = (
                    connection.gensql
                )  # la on a une instance connectee
        elif dialecte:
            regle.output.gensql = dialecte.gensql()
    #        print ('sortie',regle.ligne,regle.output.writerparms)
    elif regle.output.nom_format == "file":  # gestion de fichiers de texte generiques
        dialecte = regle.output.writerparms.get("dialecte")
        regle.ext = dialecte

    LOGGER.info("repertoire de sortie: %s", regle.output.writerparms["destination"])
    regle.setlocal("_sortie", regle.output.writerparms["destination"])

    regle.calcule_schema = regle.output.writerparms["force_schema"]
    regle.memlimit = int(regle.context.getvar("memlimit", 0))
    mode_sortie = regle.context.getvar("mode_sortie", "D")
    #    print("init stockage ", mode_sortie)
    regle.store = True if mode_sortie in {"A", "B"} else None
    regle.nbstock = 0
    regle.traite_stock = sortir_traite_stock
    #    regle.liste_attributs = regle.params.att_entree.liste
    if regle.stock_param.debug:
        print("sortir :", regle.params.att_entree.liste)
    regle.final = True
    regle.menage = True
    #     print ('icsv: sortir copy:',regle.copy,'stream:',regle.stock_param.stream)
    if regle.copy and mode_sortie == "D":
        # cette regle consomme les objets sauf si on est en mode copie et streaming
        regle.final = False
        regle.copy = False
    regle.valide = True


#    print ('fin preparation sortie ',regle.output.writerparms)


def setschemasortie(regle, obj):
    """positionne le schema de sortie pour l objet """
    if regle.nom_fich_schema:
        # on copie le schema pour ne plus le modifier apres ecriture
        regle.change_schema_nom(obj, regle.nom_fich_schema)

    if obj.schema and obj.schema.amodifier(regle):
        rep_sortie = regle.getvar("sortie_schema")
        if not rep_sortie:
            rep_sortie = os.path.join(
                regle.getvar("_sortie"), os.path.dirname(regle.params.cmp1.val)
            )
        obj.schema.setsortie(regle.output, rep_sortie)

        obj.schema.setminmaj(regle.output.writerparms.get("casse", ""))
        regle.output.minmajfunc = obj.schema.minmajfunc
    if regle.params.att_entree.liste:
        regle.output.liste_attributs = regle.params.att_entree.liste


def f_sortir(regle, obj):
    """#aide||sortir dans differents formats
    #aide_spec||parametres:?(#schema;nom_schema);?liste_attributs;sortir;format[fanout]?;?nom
      #pattern||?=#schema;?C;?L;sortir;?C;?C||sortie
         #test||redirect||obj||^Z;ok;;set||^;;;sortir;csv;#print||out
    """
    if regle.output is None:
        return False
    if obj.virtuel:  # on ne traite pas les virtuels
        # print("======================sortie objet virtuel", regle, obj)
        # raise
        return True
    setschemasortie(regle, obj)
    # print("======================sortie objet", regle.output)
    if regle.store is None:  # on decide si la regle est stockante ou pas
        regle.store = regle.calcule_schema and (not obj.schema or not obj.schema.stable)
        if regle.store:  # on ajuste les branchements
            regle.setstore()
            print("f_sortir: passage en mode stockant")

    if regle.store:
        regle.nbstock += 1
        groupe = obj.attributs["#groupe"]
        #        print("stockage", obj.ido, groupe, regle)
        if groupe != "#poubelle":
            nom_base = regle.nom_base
            # regle.stock_param.nb_obj+=1
            if regle.stock_param.stream:  # sortie classe par classe
                if groupe not in regle.stockage:
                    regle.output.ecrire_objets(
                        regle, False
                    )  # on sort le groupe precedent
                    regle.compt_stock = 0
            regle.endstore(nom_base, groupe, obj)
        return True

    regle.output.ecrire_objets_stream(obj, regle, False)

    if regle.final:
        obj.schema = None
    return True


def valreplace(chaine, obj):
    """remplace les elements provenant de l objet,
    cas particulier du parametre en [nom]"""
    vdef = r"\[(#?[a-zA-Z_][a-zA-Z0-9_]*)\]"
    repl = lambda x: obj.attributs.get(x.group(1), "")
    return re.sub(vdef, repl, chaine)


def preload(regle, obj):
    """prechargement"""
    vrep = lambda x: regle.resub.sub(regle.repl, x)
    chaine_comm = vrep(regle.params.cmp1.val)
    regle.setvar("nocomp", False)
    # =================surveillance de la consommation mémoire================
    if psutil:
        process = psutil.Process(os.getpid())
        mem1 = process.memory_info()[0]
    # =========================================
    if obj and regle.params.att_entree.val:
        entree = obj.attributs.get(regle.params.att_entree.val, regle.fich)
    else:
        entree = regle.entree if regle.entree else regle.fich
    print(
        "------- preload commandes:(",
        chaine_comm,
        ") f:",
        entree,
        "clef",
        regle.params.att_sortie.val,
    )
    if chaine_comm:  # on precharge via une macro
        nomdest = (
            regle.params.cmp2.val
            if regle.params.cmp2.val.startswith("#")
            else "#" + regle.params.cmp2.val
        )
        processor = regle.stock_param.getpyetl(
            chaine_comm, entree=entree, rep_sortie=nomdest, context=regle.context
        )
        if not processor:
            return False
        processor.process()
        if obj:
            renseigne_attributs_batch(regle, obj, processor.retour)

        print("------- preload objets", processor.store)
        nb_total = processor.getvar("_st_lu_objs", "0")
        regle.stock_param.store.update(
            processor.store
        )  # on rappatrie les dictionnaires de stockage
        regle.setvar("storekey", processor.retour)  # on stocke la clef

    else:
        #        racine = regle.stock_param.racine
        chemin = os.path.dirname(entree)
        fichier = os.path.basename(entree)
        ext = os.path.splitext(fichier)[1]
        lecteur = regle.stock_param.reader(ext)
        regle.reglestore.tmpstore = dict()
        try:
            regle.stock_param.store[regle.params.cmp2.val] = regle.reglestore.tmpstore
            lecteur.lire_objets(
                "", chemin, fichier, regle.stock_param, regle.reglestore
            )
        except FileNotFoundError:
            regle.stock_param.store[regle.params.cmp2.val] = None
            print("fichier inconnu", os.path.join(chemin, fichier))
        except StopIteration:
            pass
        nb_total = lecteur.lus_fich
    # =================surveillance de la consommation mémoire================
    if psutil:
        mem2 = process.memory_info()[0]
        mem = mem2 - mem1
        print(
            "------- preload info memoire ",
            nb_total,
            mem,
            "--------",
            int(mem / (nb_total + 1)),
        )
    # =============================
    return True


def h_preload(regle):
    """prechargement"""
    obj = None
    mapper = regle.stock_param
    tstor = (
        ";;;;;;"
        + regle.params.att_sortie.val
        + ";tmpstore;cmp;"
        + regle.params.cmp2.val
    )
    reglestore = mapper.interpreteur(tstor, "", 99999)
    regle.reglestore = reglestore
    regle.repl = lambda x: obj.attributs.get(x.group(1), "")
    regle.resub = re.compile(r"\[(#?[a-zA-Z_][a-zA-Z0-9_]*)\]")
    fich = regle.params.val_entree.val
    fich = fich.replace("[R]", regle.stock_param.racine)
    regle.fich = fich
    regle.dynlevel = 0
    if "[F]" in fich:
        regle.dynlevel = 2
    elif "[G]" in fich:
        regle.dynlevel = 1
    elif "[" in fich:
        regle.dynlevel = 3
    regle.entree = None
    regle.loaded = False
    if regle.dynlevel == 0:  # pas de selecteur on precharge avant de lire
        regle.entree = regle.params.val_entree.val
        regle.fich = regle.entree
        regle.valide = "done" if preload(regle, None) else False

    print("==================h_preload===", regle.dynlevel, regle.valide)


def f_preload(regle, obj):
    """#aide||precharge un fichier en appliquant une macro
     #aide_spec||parametres clef;fichier;attribut;preload;macro;nom
    #aide_spec1||les elements entre [] sont pris dans l objet courant
    #aide_spec2||sont reconnus[G] pour #groupe et [F] pour #classe pour le nom de fichier
       #pattern||A;?C;?A;preload;?C;C
         #!test||rien||^clef;%testrep%/refdata/lecture/t1.csv;;preload;;test||
               ||^;%testrep%/refdata/lecture/t1.csv;;charge;;;||
    """
    fich = regle.fich

    if regle.dynlevel > 0:
        fich = fich.replace("[G]", obj.attributs["#groupe"])
        fich = fich.replace("[F]", obj.attributs["#classe"])
        if fich != regle.entree:
            regle.entree = fich
            print(
                "==================f_preload===", regle.stock_param.racine, regle.entree
            )

            regle.loaded = preload(regle, obj)
    #            print ('chargement ',regle.params.cmp2.val,
    #                   regle.stock_param.store[regle.params.cmp2.val])
    return regle.loaded


def compare_traite_stock(regle):
    """ sort les objets detruits"""
    for obj in regle.comp.values():
        obj.attributs[regle.params.att_sortie.val] = "supp"
        obj.setidentobj(regle.precedent)
        regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["supp:"])
    regle.comp = None
    regle.nbstock = 0


def h_compare(regle):
    """comparaison a une reference"""
    regle.branchements.addsortie("new")
    regle.branchements.addsortie("supp")
    regle.branchements.addsortie("diff")
    regle.branchements.addsortie("orig")
    #    regle.taites = set()
    regle.store = True
    regle.nbstock = 0
    regle.comp = None
    regle.precedent = None
    regle.traite_stock = compare_traite_stock


def f_compare2(regle, obj):
    """#aide||compare a un element precharge
     #aide_spec||parametres clef;fichier;attribut;preload;macro;nom
    #aide_spec2||sort en si si egal en sinon si different
    #aide_spec3||si les elements entre [] sont pris dans l objet courant
       #pattern||A;;?L;compare2;A;C
        #helper||compare
        #schema||ajout_attribut
         #!test||
    """
    if regle.precedent != obj.ident:
        comp = regle.stock_param.store[regle.params.cmp2.val]
        if regle.comp and comp is not regle.comp:
            compare_traite_stock(regle)
            regle.nbstock = 1
        regle.comp = comp
        if regle.comp:
            if regle.params.att_entree.liste:
                regle.comp2 = {
                    i: ([i.attributs[j] for j in regle.params.att_entree.liste])
                    for i in regle.comp
                }
            else:
                regle.comp2 = {
                    i: (
                        [
                            i.attributs[j]
                            for j in sorted([k for k in i.attributs if k[0] != "#"])
                        ]
                    )
                    for i in regle.comp
                }
    #    print ('comparaison ', len(regle.comp), regle.comp)
    try:
        if len(regle.params.cmp1.liste) > 1:
            clef = "|".join(
                obj.attributs.get(i, "") for i in regle.params.att_entree.liste
            )
        else:
            clef = obj.attributs[regle.params.cmp1.val]
        ref = regle.comp2[clef]
        regle.ref.add(clef)
    except KeyError:
        obj.redirect = "new"
        obj.attributs[regle.params.att_sortie.val] = "new"
        return False
    if regle.params.att_entree.liste:
        compare = all(
            [
                obj.attributs[i] == ref.attributs[i]
                for i in regle.params.att_entree.liste
            ]
        )
    else:
        atts = {i for i in obj.attributs if i[0] != "#" or i == "#geom"}
        kref = {i for i in ref.attributs if i[0] != "#" or i == "#geom"}
        #    id_att = atts == kref
        compare = atts == kref and all(
            [obj.attributs[i] == ref.attributs[i] for i in atts]
        )
    if compare:
        return True
    obj.redirect = "diff"
    obj.attributs[regle.params.att_sortie.val] = "diff"
    ref.attributs[regle.params.att_sortie.val] = "orig"
    regle.stock_param.moteur.traite_objet(ref, regle.branchements.brch["orig:"])
    # on remet l'original dans le circuit
    return False


def f_compare(regle, obj):
    """#aide||compare a un element precharge
     #aide_spec||parametres clef;fichier;attribut;preload;macro;nom
    #aide_spec2||sort en si si egal en sinon si different
    #aide_spec3||si les elements entre [] sont pris dans l objet courant
       #pattern||A;;?L;compare;A;C
        #schema||ajout_attribut
         #!test||
    """
    if regle.precedent != obj.ident:  # on vient de changer de classe
        if regle.comp:
            compare_traite_stock(regle)
            regle.nbstock = 1
        regle.comp = regle.stock_param.store[regle.params.cmp2.val]
        regle.precedent = obj.ident
    #    print ('comparaison ', len(regle.comp), regle.comp)
    if regle.comp is None:
        return False

    try:
        if len(regle.params.cmp1.liste) > 1:
            clef = "|".join(
                obj.attributs.get(i, "") for i in regle.params.att_entree.liste
            )
        else:
            clef = obj.attributs[regle.params.cmp1.val]
        ref = regle.comp.pop(clef)
    except KeyError:

        obj.redirect = "new"
        obj.attributs[regle.params.att_sortie.val] = "new"
        return False
    if regle.params.att_entree.liste:
        compare = all(
            [
                obj.attributs[i] == ref.attributs[i]
                for i in regle.params.att_entree.liste
            ]
        )
    else:
        atts = {i for i in obj.attributs if i[0] != "#" or i == "#geom"}
        kref = {i for i in ref.attributs if i[0] != "#" or i == "#geom"}
        #    id_att = atts == kref
        compare = atts == kref and all(
            [obj.attributs[i] == ref.attributs[i] for i in atts]
        )
    if compare:
        return True
    obj.redirect = "diff"
    obj.attributs[regle.params.att_sortie.val] = "diff"
    ref.attributs[regle.params.att_sortie.val] = "orig"
    ref.setidentobj(obj.ident)  # on force l'identite de l'original
    regle.stock_param.moteur.traite_objet(ref, regle.branchements.brch["orig:"])
    # on remet l'original dans le circuit
    return False


def sortir_cles(regle):
    """genere les clefs etrangers"""
    # TODO: generer les clefs etrangeres
    for clef, valeurs in regle.keystore.items():
        pass
    regle.store = False


def h_getkey(regle):
    """prepare les stockages"""
    if regle.params.cmp1.val not in regle.stock_param.keystore:
        regle.stock_param.keystore[regle.params.cmp1.val] = dict()
    regle.keystore = regle.stock_param.keystore[regle.params.cmp1.val]
    if regle.params.cmp2.val:
        # on veut recuperer les cles sous forme d objets
        regle.store = True
        regle.traite_stock = sortir_cles


def f_getkey(regle, obj):
    """#aide||retourne une clef numerique incrementale correspondant a une valeur
    #aide_spec||attribut qui recupere le resultat, valeur de reference a coder , getkey , nom de la clef
    #pattern||S;?C;?A;getkey;?A;?A;;
    """
    ref = regle.get_entree(obj)
    if ref not in regle.keystore:
        regle.keystore[ref] = len(regle.keystore) + 1
    regle.setval_sortie(obj, regle.keystore[ref])
    return True


def h_loadconfig(regle):
    """charge des definitions et/ou des macros"""
    regle.stock_params.loadconfig(regle.params.cmp1, regle.params.cmp2)
    regle.valide = "done"


def f_loadconfig(regle, obj):
    """#aide||charge des definitions et/ou des macros
    #aide_spec||repertoire des parametres et des macros
      #pattern||;;;loadconfig;C;C
    """
    return True


def sortir_objets(regle):
    """sort les objets"""
    for obj in regle.objets.values():
        regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["gen"])
    regle.nbstock = 0


def h_objgroup(regle):
    """regle stockante pour les objets crees"""
    regle.store = True
    regle.objets = OrderedDict()
    regle.attlist = set(regle.params.att_sortie.liste) | set(regle.params.cmp2.liste)
    if (
        len(regle.params.att_sortie.liste) == 1
        and len(regle.params.att_entree.liste) > 1
    ):
        regle.params.pattern = "2"
        regle.record = namedtuple(
            regle.params.att_sortie.val, regle.params.att_entree.liste
        )
    regle.nbstock = 0
    regle.traite_stock = sortir_objets


def f_objgroup(regle, obj):
    """#aide||accumule des attributs en un tableau
    #aide_spec1||cree un tableau par attribut autant de tableaux que de champs en entree
               ||si un seul attribut en sortie cree un tableau contenant des champs nommes
    #pattern1||L;?C;L;objgroup;C;?L;
    #parametres1||attributs en sortie;defaut;attributs en entree;;nom de la classe en sortie;attributs de groupage
    """
    clef = tuple(obj.attributs.get(i) for i in regle.params.cmp2.liste)
    # print("regroupement", regle.params.cmp2.liste, "->", clef)
    if clef in regle.objets:
        obj2 = regle.objets.get(clef)
    else:
        # on cree un objet
        obj2 = obj.dupplique()
        ident = obj.ident
        ident2 = (ident[0], regle.params.cmp1.val)
        obj2.setidentobj(ident2)
        # on supprime les attributs non communs
        for i in list(obj2.attributs.keys()):
            if i.startswith("#") or i in regle.attlist:
                continue
            del obj2.attributs[i]
        # on cree les attributs d accumulation
        for i in regle.params.att_sortie.liste:
            obj2.attributs[i] = []
        # la premiere fois on ajuste le schema
        if regle.nbstock == 0:
            obj2.ajuste_schema()
        regle.objets[clef] = obj2
        regle.nbstock += 1
    if regle.params.pattern == "1":
        for i, j in zip(regle.params.att_sortie.liste, regle.params.att_entree.liste):
            obj2.attributs[i].append(obj.attributs.get(j, regle.params.val_entree.val))
    elif regle.params.pattern == "2":
        obj2.attributs[regle.params.att_sortie.val].append(
            regle.record._make(
                obj.attributs.get(i) for i in regle.params.att_entree.liste
            )
        )
    return True


def h_log(regle):
    """messages uniques"""
    if regle.params.att_entree.val == "":
        if regle.params.pattern == "3":
            LOGGER.info(regle.params.cmp1.val)
        elif regle.params.pattern == "2":
            LOGGER.error(regle.params.cmp1.val)
        elif regle.params.pattern == "1":
            LOGGER.warning(regle.params.cmp1.val)
        regle.valide = "done"
    return True


def f_log(regle,obj):
    """genere une entree de log
    #pattern||;?C;?A;log;C;?C;
    """
    if regle.params.cmp2.val=="debug":
        regle.stock_param.logger.debug(regle.params.cmp1.val,regle.getval_entree(obj))
    elif regle.params.cmp2.val=="warn":
        regle.stock_param.logger.warning(regle.params.cmp1.val,regle.getval_entree(obj))
    elif regle.params.cmp2.val=="err":
        regle.stock_param.logger.error(regle.params.cmp1.val,regle.getval_entree(obj))
    else:
        regle.stock_param.logger.info(regle.params.cmp1.val,regle.getval_entree(obj))
