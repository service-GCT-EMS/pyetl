# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:34:04 2015

@author: 89965
fonctions de structurelles diverses
"""

from collections import namedtuple

from numpy import iterable
import ldap
from win32com.client import Dispatch, GetObject


from inspect import getmembers


def print_members(obj, obj_name="placeholder_name"):
    """Print members of given COM object"""
    fields = []
    try:
        fields = list(obj._prop_map_get_.keys())
    except AttributeError:
        print("Object has no attribute '_prop_map_get_'")
        print(
            "Check if the initial COM object was created with"
            "'win32com.client.gencache.EnsureDispatch()'"
        )
        print(dir(obj))
    methods = [
        m[0]
        for m in getmembers(obj)
        if (not m[0].startswith("_") and "clsid" not in m[0].lower())
    ]

    if len(fields) + len(methods) > 0:
        print("Members of '{}' ({}):".format(obj_name, obj))
    else:
        print("!!!!!!\tObject has no members to print")

    print("\tFields:")
    if fields:
        for field in fields:
            print(f"\t\t{field}")
    else:
        print("\t\tObject has no fields to print")

    print("\tMethods:")
    if methods:
        for method in methods:
            print(f"\t\t{method}")
    else:
        print("\t\tObject has no methods to print")


def dict_decode(attdict, encoding="utf-8"):
    """decode un dictionnaide byte vers str"""
    for i in attdict:
        if isinstance(attdict[i], list):
            attdict[i] = ",".join(
                (
                    (j.decode(encoding) if isinstance(j, bytes) else j)
                    for j in attdict[i]
                )
            )
        elif isinstance(attdict[i], bytes):
            attdict[i] = attdict[i].decode(encoding)


def find_ldapuser(regle, nom):
    """recupere des utilisateurs dans une base ldap"""
    adcode = regle.getvar("ADserver")
    base_dn = regle.getvar("base_dn_" + adcode)
    filter = "(|(CN=%s)(sAMAccountName=%s)(displayName='%s'))" % (nom, nom, nom)
    attrs = regle.a_recuperer
    retour = regle.connect.search_s(base_dn, ldap.SCOPE_SUBTREE, filter, attrs)
    if regle.debug:
        print("adquery", base_dn, filter, attrs)
        print("retour adquery", retour)
    result = list()
    if retour:
        for ligne in retour:
            ref, attdict = ligne
            dict_decode(attdict)
            attdict["clef"] = ref
            # print("stockage attdict", attdict)
            item = regle.sortie(**attdict)
        result.append(item)
    return result


def getADnames(regle, elems, *args, **kwargs):
    """recupere des utilisateurs dans la base active directory courante"""
    # print("recup", elems)
    sql_string = []
    sql_string.append("SELECT %s " % ",".join(elems))
    sql_string.append("FROM '%s'" % regle.AD.root().path())
    filters = []
    if kwargs:
        filters.append(
            regle.AD._and(*("%s='%s'" % (k, v) for (k, v) in kwargs.items()))
        )
    final = [regle.AD._and(i, *filters) for i in args]
    if final:
        where_clause = regle.AD._or(*final)
    else:
        where_clause = regle.AD._and(*filters)
    if where_clause:
        sql_string.append("WHERE %s" % where_clause)

    print("requete ad", "\n".join(sql_string))
    adreponse=regle.AD.query("\n".join(sql_string), Page_size=50)
    # print ("reponse adquery", adreponse) 
    found=0
    for result in adreponse:
        print("retour ad:", result, type(result))
        found=1
        if isinstance(result, regle.AD.ADO_record):
            print("retour", result.fields)
            if elems == ["*"]:
                valeur = result.fields["ADsPath"]
                # print("retour", valeur, type(valeur), result.fields)
                # valeur.dump()
                yield valeur
            else:
                retour = list()
                for i in elems:
                    elem = result.fields.get(i)
                    # print("analyse", i, elem, type(elem), print_members(elem)),
                    try:
                        val = [j for j in elem]
                        if len(val) == 1:
                            val = val[1]
                    except TypeError:
                        val = str(elem)
                    retour.append(val)
                    print ('retour AD', retour)
                yield retour
    if not found:
        print ('ad: iterateur vide')

def find_ADuser(regle, elems, name=None):
    if not name or name == "*":
        yield from getADnames(
            regle,
            elems,
            objectCategory="Person",
            objectClass="User",
        )
    elif "=" in name:  # condition
        yield from getADnames(
            regle,
            elems,
            name,
            objectCategory="Person",
            objectClass="User",
        )
    else:
        yield from getADnames(
            regle,
            elems,
            "sAMAccountName='%s'" % (name),
            "displayName='%s'" % (name),
            "cn='%s'" % (name),
            objectCategory="Person",
            objectClass="User",
        )


def h_adquery(regle):
    """initialise l'acces active_directory"""

    # print("acces LDAP", ACD.root(), regle)
    regle.a_recuperer = regle.params.cmp2.liste if regle.params.cmp2.liste else ["CN"]
    adcode = regle.getvar("ADserver")
    if adcode:
        # connection specifique a un autre serveur AD
        # on charge le groupe de parametres

        regle.stock_param.load_paramgroup(adcode, nom=adcode)

        server = regle.getvar("server_" + adcode)
        user = regle.getvar("user_" + adcode)
        passwd = regle.getvar("passwd_" + adcode)
        print("adconnect ", user, passwd, server)
        try:
            regle.connect = ldap.initialize("ldap://" + server)
            regle.connect.bind_s(user, passwd, ldap.AUTH_SIMPLE)
        except Exception as err:
            print("erreur connection LDAP", adcode, "->", server, err)
            regle.valide = False
            return False
        # print("connecteur LDAP sur ", server)
        # print("champs", ["clef"] + regle.a_recuperer)
        regle.sortie = namedtuple(
            "ldapreturn", ["clef"] + [i for i in regle.a_recuperer]
        )
        if regle.params.pattern == "1" or regle.params.pattern == "4":
            regle.queryfonc = find_ldapuser
    else:
        # connection serveur par defaut
        from . import active_directory as ACD

        try:
            regle.AD = ACD
            print ('connection active directory par defaut (com object)')
        except ACD.pywintypes.com_error:
            regle.stock_param.logger.error("connection active directory impossible")
            regle.valide = False
            return False

        def find_computer(regle, elems, name=None):
            yield from regle.AD.search(objectCategory="Computer", cn=name)

        def find_group(regle, elems, name=None):
            yield from regle.AD.search(objectCategory="group", cn=name)

        # regle.a_recuperer = regle.params.cmp2.val if regle.params.cmp2.val else "CN"
        # print("----AD", regle.params.pattern, regle)
        if regle.params.pattern == "1" or regle.params.pattern == "4":
            regle.queryfonc = regle.AD.find_user
            regle.mqueryfonc = find_ADuser
            regle.ad_objectclass = "User"
        elif regle.params.pattern == "2":
            regle.ad_objectclass = "computer"
            regle.queryfonc = regle.AD.find_computer
            regle.mqueryfonc = find_computer
        elif regle.params.pattern == "3":
            regle.ad_objectclass = "group"
            regle.queryfonc = regle.AD.find_group
            regle.mqueryfonc = find_group
        elif regle.params.pattern=='5':
            regle.ad_objectclass=regle.params.cmp1.val
            regle.queryfonc = regle.AD.search
            regle.mqueryfonc = find_group


    if regle.params.pattern == "4":  # variable

        items = regle.queryfonc(regle.params.val_entree.val)
        if items is None:
            regle.stock_param.logger.error(
                "element introuvable: %s", regle.params.val_entree.val
            )
            regle.valide = "done"
            return True
        print ('recup query ', items)
        if iterable(items):
            item=next(items)
        else:
            item=items
        # item = items[0] if isinstance(items, list) else items
        val = getattr(item, regle.a_recuperer[0])
        regle.setvar(regle.params.att_sortie.val, val)
        if regle.debug:
            print(
                "AD setvar",
                regle.params.att_sortie.val,
                regle.params.val_entree.val,
                item,
                items,
            )
        regle.valide = "done"
    else:
        regle.chargeur = True


def f_adquery(regle, obj):
    """#aide||extait des information de active_directory
    #pattern1||M;?C;?A;adquery;=user;?C;
    #pattern2||M;?C;?A;adquery;=machine;?C;
    #pattern3||M;?C;?A;adquery;=groupe;?C;
    #pattern4||P;C;;adquery;=user;;||sortie||2
    #pattern5||;?C;?A;adquery;C;?C;||sortie||1
    #req_test||adserver
    #test||obj||X;89965;adquery;user;||atv;X;UNGER Claude;
    #"""
    if regle.get_entree(obj):
        try:
            items = regle.mqueryfonc(regle, regle.a_recuperer, regle.get_entree(obj))
            if regle.debug:

                print("adquery", items)
                # print("contenu", list(items))
        except TypeError as err:
            print("erreur adquery", err, regle.get_entree(obj))
            items = []
        item = None
        if regle.a_recuperer == ["*"]:
            print("root", dir(regle.AD.root()))
            val = regle.queryfonc(regle.get_entree(obj))
            print("infos:", val)
            val.dump()
            regle.setval_sortie(obj, "")
            return True
        if regle.params.pattern == "1" and regle.a_recuperer == ["CN"]:
            if items:
                val = next(items, [""])
                # if regle.debug:
                # print("recup user", val)
                regle.setval_sortie(obj, val)
                return True
            return False
        for item in items:
            obj2 = obj.dupplique()
            if isinstance(item, (str, list)):
                val = item
            else:
                val = getattr(item, regle.a_recuperer[0])
            print("extraction adquey", item, val)
            regle.setval_sortie(obj2, val)
            regle.stock_param.moteur.traite_objet(obj2, regle.branchements.brch["gen"])

        if item:
            return True
    # print("pas d'entree adquery", regle.get_entree(obj))
    return False
