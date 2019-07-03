# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de structurelles diverses
"""
import os
import re
import logging
import subprocess
from collections import defaultdict
import psutil


from pyetl.formats.mdbaccess import dbaccess
from pyetl.formats.generic_io import Writer
from .outils import charge_mapping, remap, prepare_elmap, renseigne_attributs_batch


LOGGER = logging.getLogger("pyetl")


def map_struct(regle):
    """mappe la structure clef etrangeres et fonctions"""
    charge_mapping(regle, mapping=regle.schema.mapping)


def _map_schemas(regle, obj):
    """essaye de trouver un mapping pour une classe"""
    # print ('appel map_schema', regle,obj)
    if obj is None:
        if regle.getvar("schema_entree"):
            schema_origine = regle.stock_param.schemas[regle.getvar("schema_entree")]
            print("-------------------------mapping", schema_origine)
        regle.schema = None
        #        else:
        #            return
        #        if regle.params.val_entree.val:
        #            schema2 = regle.stock_param.init_schema(regle.params.val_entree.val,
        #                                                    modele=schema_origine, origine='B')
        #        else:
        return
    else:
        schema_origine = obj.schema.schema
        if regle.params.val_entree.val:
            schema2 = regle.stock_param.init_schema(
                regle.params.val_entree.val, modele=schema_origine, origine="B"
            )
        else:
            schema2 = obj.schema.schema
    regle.schema = schema2
    if schema2.elements_specifiques:
        for i in schema2.elements_specifiques:
            #            print('mapping specifique', i)
            spec = schema2.elements_specifiques[i]
            mapped = remap(spec, regle.elmap)
            #            print('mapping specifique', i, len(spec), '->', len(mapped))
            schema2.elements_specifiques[i] = mapped
    else:
        LOGGER.info("pas d'elements specifiques")

        # print("-----------------------------pas d'elements specifiques")

    for i in schema_origine.classes:
        schema2.get_classe(i, modele=schema_origine.classes[i], cree=True)
    for i in list(schema_origine.classes.keys()):
        #        print ('map_schemas ',schema_origine.nom,i,regle.mapping.get(i))
        if i in regle.mapping:
            schema2.renomme_classe(i, regle.mapping[i])

        # mapping foreign keys :

    # print("-------------------------------------------------mapping effectue", schema2.nom, len(schema2.classes))
    for clef in schema2.classes:
        if clef in regle.mapping_attributs:

            for dest, orig in regle.mapping_attributs[clef].items():
                schema2.classes[clef].rename_attribut(orig, dest)
                # print ('-----------------------------mappin attributs', clef, orig,dest)

def applique_mapping(regle):
    """gere les clefs etrangeres et les elements speciaux dans les mappings"""
    mapping = regle.schema.mapping
    regle.elmap = prepare_elmap(mapping)
    _map_schemas(regle, None)
    regle.nbstock = 0
    for i in mapping:
        for scl in regle.schema.classes.values():
            scl.renomme_cible_classe(i, mapping[i])


def h_map2(regle):
    """ prepare le mapping des structures"""
    regle.store = True
    regle.blocksize = 1
    regle.nbstock = 0
    regle.traite_stock = applique_mapping


def f_map2(regle, obj):
    """#aide||mapping en fonction d'une creation dynamique de schema
  #aide_spec||parametres: mappe les structures particulieres
   #pattern2||;;;map;=#struct;;
    """
    regle.schema = obj.schema.schema
    regle.nbstock = 1


def h_map(regle):
    """ precharge le fichier de mapping et prepare les dictionnaires"""
    regle.dynlevel = 0  # les noms de mapping dependent ils des donnees d entree
    regle.mapping = None
    regle.schema = None
    #    if regle.params.att_sortie.val == '#schema': # mapping d un schema existant
    #        schema2 =
    regle.changeschema = True
    fich = regle.params.cmp1.val
    if "[F]" in fich:
        regle.dynlevel = 2
    elif "[C]" in fich:
        regle.dynlevel = 1
    if regle.dynlevel:
        regle.clefdyn = ""
    else:
        charge_mapping(regle)
        _map_schemas(regle, None)


def f_map(regle, obj):
    """#aide||mapping en fonction d'un fichier
  #aide_spec||parametres: map; nom du fichier de mapping
 #aide_spec2||si #schema est indique les objets changent de schema
    #pattern||?=#schema;?C;;map;C;;
  #test||obj||^#schema;test;;map;%testrep%/refdata/map.csv;;||^;;;pass;;;||atv;toto;AB
 #!test2||obj||^#schema;test;;map+-;%testrep%/refdata/map.csv;;||^;;;pass;;;debug||cnt;2
    """
    #    print ("dans map ===============",obj)
    if regle.dynlevel:  # attention la regle est dynamique
        clef_dyn = (
            regle.stock_param.chemin_courant
            if regle.dynlevel == 1
            else regle.stock_param.fichier_courant
        )
        if clef_dyn != regle.clef_dyn:
            charge_mapping(regle)
    if not regle.schema:
        _map_schemas(regle, obj)
    clef = obj.ident
    schema2 = regle.schema
    if clef in regle.mapping:
        nouv = regle.mapping.get(clef)
        obj.setidentobj(nouv, schema2=schema2)
        if clef in regle.mapping_attributs:
            for orig, dest in regle.mapping_attributs[clef].items():
                try:
                    obj.attributs[dest] = obj.attributs[orig]
                    del obj.attributs[orig]
                except KeyError:
                    obj.attributs[dest] = ""
        return True
    #    print ('====================== mapping non trouve', clef)
    #    print ('definition mapping', '\n'.join([str(i)+':\t\t'+str(regle.mapping[i])
    #                                            for i in sorted(regle.mapping)]))
    return False


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
            #            print ('store: relecture objet ', obj, obj.schema.identclasse,obj.schema.info)
            regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["end"])
    else:
        for clef in sorted(store.keys(), reverse=reverse) if regle.params.cmp2.val else store:
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
    regle.fold = regle.params.cmp1.val == "cmpf"
    if regle.params.cmp2.val == "clef":
        regle.stocke_obj = False
        regle.tmpstore = set()


def f_stocke(regle, obj):
    """#aide||stockage temporaire d'objets pour assurer l'ordre dans les fichiers de sortie
  #aide_spec||liste de clefs,tmpstore;uniq;sort|rsort : stockage avec option de tri
  #aide_spec2||liste de clefs,tmpstore;cmp;nom : prechargement pour comparaisons
   #pattern1||;;?L;tmpstore;?=uniq;?=sort;||
   #pattern2||;;?L;tmpstore;?=uniq;?=rsort;||
   #pattern3||;;?L;tmpstore;=cmp;A;?=clef||
   #pattern4||;;?L;tmpstore;=cmpf;A;?=clef||
       #test||obj;point;4||^;;V0;tmpstore;uniq;rsort||^;;C1;unique||atv;V0;3;
      #test2||obj;point;4||^V2;;;cnt;-1;4;||^;;V2;tmpstore;uniq;sort||^;;C1;unique;||atv;V2;1;
    """
    #    regle.stock.append(obj)
    if obj.virtuel:
        return True
    if regle.direct_reuse:
        regle.nbstock += 1

    if regle.params.cmp1.val:
        if len(regle.params.att_entree.liste) > 1:
            clef = "|".join(obj.attributs.get(i, "") for i in regle.params.att_entree.liste)
        else:
            clef = obj.attributs.get(regle.params.att_entree.val, "")
        if regle.stocke_obj:
            regle.tmpstore[clef] = obj
        else:
            regle.tmpstore.add(obj)
        return True
    #    print ('store: stockage objet ', obj, obj.schema.identclasse,obj.schema.info)
    regle.tmpstore.append(obj)
    return True


def h_uniq(regle):
    """ stocke les clefs pour l'unicite """
    regle.tmpstore = set()


def f_uniq(regle, obj):
    """#aide||unicite de la sortie laisse passer le premier objet et filtre le reste
    #aide_spec||liste des attibuts devant etre uniques si #geom : test geometrique
    #pattern||;?=#geom;?L;unique;;;
    #test||obj;point;2||^;;C1;unique||+fail:;;;;;;;pass>;;||cnt;1
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
    clef = clef + "|".join(obj.attributs.get(i, "") for i in regle.params.att_entree.liste)

    #    print ('uniq ',clef, regle.params.att_entree.val )
    if clef in regle.tmpstore:
        return False
    regle.tmpstore.add(clef)
    return True


def h_uniqcnt(regle):
    """ stocke les clefs pour l'unicite """
    regle.maxobj = regle.params.cmp1.num if regle.params.cmp1.num else 1
    regle.cnt = regle.maxobj > 1
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
    clef = clef + "|".join(obj.attributs.get(i, "") for i in regle.params.att_entree.liste)
    regle.tmpstore[clef] += 1
    obj.attributs[regle.params.att_sortie.val] = str(regle.tmpstore[clef])
    if regle.tmpstore[clef] > regle.maxobj:
        return False
    return True


def sortir_traite_stock(regle):
    """ecriture finale"""
    if regle.final:
        try:
            #            print('ecriture finale', regle.f_sortie.ecrire_objets)
            regle.f_sortie.ecrire_objets(regle, True)
        except IOError as err:
            LOGGER.error("erreur d'ecriture: " + repr(err))
        regle.nbstock = 0
        return
    for groupe in list(regle.stockage.keys()):
        for obj in regle.recup_objets(groupe):
            regle.f_sortie.ecrire_objets_stream(obj, regle, False)
            regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["end"])
    regle.nbstock = 0


def h_sortir(regle):
    """preparation sortie"""

    if regle.params.att_sortie.val == "#schema":  # on force les noms de schema pour l'ecriture
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

        regle.context.setlocal("fanout", regle.params.cmp1.val[tmplist + 1 : -1])
        regle.params.cmp1.val = regle.params.cmp1.val[:tmplist]
    regle.f_sortie = Writer(regle.params.cmp1.val, regle)  # tout le reste
    #    print ('positionnement writer ',regle, regle.params.cmp1.val)
    if regle.f_sortie.nom_format == "sql":  # gestion des dialectes sql et du mode connecté
        destination = regle.f_sortie.writerparms.get("base_dest")
        dialecte = regle.f_sortie.writerparms.get("dialecte")
        regle.f_sortie.writerparms["reinit"] = regle.getvar("reinit")
        regle.f_sortie.writerparms["nodata"] = regle.getvar("nodata")
        if destination:  # on va essayer de se connecter
            connection = dbaccess(regle.stock_param, destination)
            if connection and connection.valide:
                regle.f_sortie.gensql = connection.gensql  # la on a une instance connectee
        elif dialecte:
            regle.f_sortie.gensql = dialecte.gensql()
    #        print ('sortie',regle.ligne,regle.f_sortie.writerparms)
    elif regle.f_sortie.nom_format == "file":  # gestion de fichiers de texte generiques
        dialecte = regle.f_sortie.writerparms.get("dialecte")
        regle.ext = dialecte

    regle.fanout = (
        regle.context.getvar("fanout", "groupe") if regle.f_sortie.multiclasse else "classe"
    )

    if regle.params.cmp2.val and regle.params.cmp2.val != "#print":
        rep_base = regle.context.getvar("_sortie")
        #   print('positionnement sortie', rep_base, os.path.join(rep_base, regle.params.cmp2.val))
        if os.path.isabs(regle.params.cmp2.val): # si absolu on ignore le rep de sortie
            rep_base = ''
        if regle.fanout == 'no': # sans fanout pas de sous repertoires
            regle.context.setlocal("_sortie", os.path.join(rep_base, os.path.dirname(regle.params.cmp2.val)))
            regle.f_sortie.writerparms["destination"] = os.path.basename(regle.params.cmp2.val)
        else:
            regle.context.setlocal("_sortie", os.path.join(rep_base, regle.params.cmp2.val))

    #    print("fanout de sortie",regle.fanout)
    regle.calcule_schema = regle.f_sortie.calcule_schema
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


#    print ('fin preparation sortie ',regle.f_sortie.writerparms)


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
        obj.schema.setsortie(regle.f_sortie, rep_sortie)

        obj.schema.setminmaj(regle.f_sortie.minmaj)
    if regle.params.att_entree.liste:
        obj.liste_atttributs = regle.params.att_entree.liste


def f_sortir(regle, obj):
    """#aide||sortir dans differents formats
  #aide_spec||parametres:?(#schema;nom_schema);?liste_attributs;sortir;format[fanout]?;?nom
    #pattern||?=#schema;?C;?L;sortir;?C;?C||sortie
       #test||redirect||obj||^Z;ok;;set||^;;;sortir;csv;#print||end
    """
    if regle.f_sortie is None:
        return False
    if obj.virtuel:  # on ne traite pas les virtuels
        return True
    listeref = obj.liste_attributs
    schemaclasse_ref = obj.schema

    setschemasortie(regle, obj)
    #    print ('stockage ',regle.f_sortie.calcule_schema, regle.store)
    if regle.store is None:  # on decide si la regle est stockante ou pas
        regle.store = regle.f_sortie.calcule_schema and (not obj.schema or not obj.schema.stable)
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
                    regle.f_sortie.ecrire_objets(regle, False)  # on sort le groupe precedent
                    regle.compt_stock = 0
            regle.endstore(
                nom_base,
                groupe,
                obj,
            )
            return True

    regle.f_sortie.ecrire_objets_stream(obj, regle, False)
    obj.schema = None

    if regle.final:
        return True
    # la on regenere l'objet et on l'envoie dans le circuit poutr la suite
    obj.setschema(schemaclasse_ref)
    obj.liste_attributs = listeref
    # on reattribue le schema pour la sortie en simulant une copie
    return True


def valreplace(chaine, obj):
    """remplace les elements provenant de l objet """
    vdef = r"\[(#?[a-zA-Z_][a-zA-Z0-9_]*)\]"
    repl = lambda x: obj.attributs.get(x.group(1), "")
    return re.sub(vdef, repl, chaine)


def preload(regle, obj):
    """prechargement"""
    vrep = lambda x: regle.resub.sub(regle.repl, x)
    chaine_comm = vrep(regle.params.cmp1.val)
    regle.context.setvar("nocomp", False)
    process = psutil.Process(os.getpid())

    mem1 = process.memory_info()[0]
    if obj and regle.params.att_entree.val:
        entree = obj.attributs.get(regle.params.att_entree.val, regle.fich)
    else:
        entree = regle.entree if regle.entree else valreplace(regle.fich, obj)

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
        processor = regle.stock_param.getpyetl(chaine_comm, entree=entree, rep_sortie=nomdest)
        processor.process()
        renseigne_attributs_batch(regle, obj, processor.retour)

        print("------- preload ", processor.store)
        regle.stock_param.store.update(
            processor.store
        )  # on rappatrie les dictionnaires de stockage
        regle.context.setvar("storekey", processor.retour)  # on stocke la clef

    else:
        #        racine = regle.stock_param.racine
        chemin = os.path.dirname(entree)
        fichier = os.path.basename(entree)
        ext = os.path.splitext(fichier)[1]
        lecteur = regle.stock_param.reader(ext)
        regle.reglestore.tmpstore = dict()
        try:
            regle.stock_param.store[regle.params.cmp2.val] = regle.reglestore.tmpstore
            lecteur.lire_objets("", chemin, fichier, regle.stock_param, regle.reglestore)
        except FileNotFoundError:
            regle.stock_param.store[regle.params.cmp2.val] = None
            print("fichier inconnu", os.path.join(chemin, fichier))
        except StopIteration:
            pass
        nb_total = lecteur.lus_fich

    mem2 = process.memory_info()[0]
    mem = mem2 - mem1
    print("------- preload ", nb_total, mem, "--------", int(mem / (nb_total + 1)))


def h_preload(regle):
    """prechargement"""
    obj = None
    mapper = regle.stock_param
    tstor = ";;;;;;" + regle.params.att_sortie.val + ";tmpstore;cmp;" + regle.params.cmp2.val
    reglestore = mapper.interpreteur(tstor, "", 99999)
    regle.reglestore = reglestore
    regle.repl = lambda x: obj.attributs.get(x.group(1), "")
    regle.resub = re.compile(r"\[(#?[a-zA-Z_][a-zA-Z0-9_]*)\]")
    fich = regle.params.val_entree.val
    #    fich = fich.replace('[R]', regle.stock_param.racine)
    regle.fich = fich
    regle.dynlevel = 0
    if "[R]" in fich:
        regle.dynlevel = 1
    if "[F]" in fich:
        regle.dynlevel = 2
    elif "[G]" in fich:
        regle.dynlevel = 1
    elif "[" in fich:
        regle.dynlevel = 3
    regle.entree = None

    if regle.dynlevel == 0:  # pas de selecteur on precharge avant de lire
        regle.entree = regle.params.val_entree.val
        regle.fich = regle.entree
        preload(regle, None)
        regle.valide = "done"

    print("==================h_preload===", regle.dynlevel, regle.valide)


def f_preload(regle, obj):
    """#aide||precharge un fichier en appliquant une macro
  #aide_spec||parametres clef;fichier;attribut;preload;macro;nom
 #aide_spec1||les elements entre [] sont pris dans l objet courant
 #aide_spec2||sont reconnus[G] pour #groupe et [F] pour #classe pour le nom de fichier
    #pattern||A;?C;?A;preload;?C;C
      #!test||
    """
    fich = regle.fich

    if regle.dynlevel > 0:
        fich = fich.replace("[G]", obj.attributs["#groupe"])
        fich = fich.replace("[R]", regle.stock_param.racine)
        fich = fich.replace("[F]", obj.attributs["#classe"])
        if fich != regle.entree:
            regle.entree = fich
            print("==================f_preload===", regle.stock_param.racine, regle.entree)

            preload(regle, obj)
    #            print ('chargement ',regle.params.cmp2.val,
    #                   regle.stock_param.store[regle.params.cmp2.val])
    return True


def compare_traite_stock(regle):
    """ sort les objets detruits"""
    for obj in regle.comp.values():
        obj.attributs[regle.params.att_sortie.val] = "supp"
        obj.setidentobj(regle.precedent)
        regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["supp:"])
    regle.comp = None
    regle.nbstock = 0


# def compare_traite_stock(regle):
#    """ sort les objets detruits"""
#    for clef, obj in regle.comp.items():
#        if obj.redirect is None:
#            obj.attributs[regle.params.att_sortie.val]='supp'
#            regle.stock_param.moteur.traite_objet(obj, regle.branchements.brch["supp:"])
#        regle.comp[clef] = None
#    regle.comp = None
#    regle.nbstock = 0


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
                    i: ([i.attributs[j] for j in regle.params.att_entree.liste]) for i in regle.comp
                }
            else:
                regle.comp2 = {
                    i: ([i.attributs[j] for j in sorted([k for k in i.attributs if k[0] != "#"])])
                    for i in regle.comp
                }
    #    print ('comparaison ', len(regle.comp), regle.comp)
    try:
        if len(regle.params.cmp1.liste) > 1:
            clef = "|".join(obj.attributs.get(i, "") for i in regle.params.att_entree.liste)
        else:
            clef = obj.attributs[regle.params.cmp1.val]
        ref = regle.comp2[clef]
        regle.ref.add(clef)
    except KeyError:
        obj.redirect = "new"
        obj.attributs[regle.params.att_sortie.val] = "new"
        return False
    if regle.params.att_entree.liste:
        compare = all([obj.attributs[i] == ref.attributs[i] for i in regle.params.att_entree.liste])
    else:
        atts = {i for i in obj.attributs if i[0] != "#" or i=='#geom'}
        kref = {i for i in ref.attributs if i[0] != "#" or i=='#geom'}
        #    id_att = atts == kref
        compare = (
            atts == kref
            and all([obj.attributs[i] == ref.attributs[i] for i in atts])
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
            clef = "|".join(obj.attributs.get(i, "") for i in regle.params.att_entree.liste)
        else:
            clef = obj.attributs[regle.params.cmp1.val]
        ref = regle.comp.pop(clef)
    except KeyError:

        obj.redirect = "new"
        obj.attributs[regle.params.att_sortie.val] = "new"
        return False
    if regle.params.att_entree.liste:
        compare = all([obj.attributs[i] == ref.attributs[i] for i in regle.params.att_entree.liste])
    else:
        atts = {i for i in obj.attributs if i[0] != "#" or i=='#geom'}
        kref = {i for i in ref.attributs if i[0] != "#" or i=='#geom'}
        #    id_att = atts == kref
        compare = (
            atts == kref
            and all([obj.attributs[i] == ref.attributs[i] for i in atts])
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


def h_run(regle):
    """execution unique si pas d'objet dans la definition"""
    if regle.params.att_entree.val or regle.params.val_entree.val:
        return
    if regle.runscope():  # on voit si on doit l'executer
        chaine = " ".join((regle.params.cmp1.val, regle.params.cmp2.val))
        print("lancement ", chaine)
        fini = subprocess.run(chaine, stderr=subprocess.STDOUT, shell=True)
        if regle.params.att_sortie.val:
            regle.stock_param.set_param(regle.params.att_sortie.val, fini)
    regle.valide = "done"


def f_run(regle, obj):
    """#aide||execute un programme exterieur
  #aide_spec||attribut qui recupere le resultat, parametres , run , nom, parametres
    #pattern||?A;?C;?A;run;C;?C
   #pattern2||P;;;run;C;?C
     #schema||ajout_attribut
    """
    chaine = " ".join((regle.params.cmp1.val, regle.params.cmp2.val, regle.getval_entree(obj)))
    fini = subprocess.run(chaine, stderr=subprocess.STDOUT, shell=True)
    if regle.params.att_sortie.val:
        obj.attributs[regle.params.att_sortie.val] = str(fini)


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
