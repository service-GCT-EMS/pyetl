# -*- coding: utf-8 -*-
# formats d'entree sortie
"""gestion des formats d'entree et de sortie.
"""


import os
import codecs

# from dbfread import DBF
import dbf

# import dbf
# from numba import jit


def decode_entetes_dbf(reader, table):
    """prepare l'entete et les noma d'un fichier csv"""
    noms_attributs = table.field_names
    if reader.newschema:
        type_demande = "T"
        for i in table.structure:
            nom, type_att = i.split(" ")
            code_type = type_att[0]
            long = 0
            dec = 0
            if len(type_att > 1):
                taille = type_att[2:-1]
                if "," in taille:
                    tmp = taille.split(",")
                    long = int(tmp[0])
                    dec = int(tmp[1])
                else:
                    long = int(taille)
            if code_type == "N":
                type_demande = "F" if dec else "E"
            elif code_type == "L":
                type_demande = "B"
            elif code_type == "D":
                type_demande = "D"
            reader.schemaclasse.stocke_attribut(nom, type_demande)
    return noms_attributs


import time


def lire_objets_dbf(self, rep, chemin, fichier):
    """lit des objets a partir d'un fichier csv"""
    self.prepare_lecture_fichier(rep, chemin, fichier)
    # nom_schema, nom_groupe, nom_classe = getnoms(rep, chemin, fichier)
    try:
        with dbf.Table(os.path.join(rep, chemin, fichier)) as table:
            noms_attributs = decode_entetes_dbf(self, table)
            self.prepare_attlist(noms_attributs)
            print("structure", table.structure())
            # print(
            #     "attributs lus", "\n".join(i+':'+str(fich.type(i)) for i in fich.field_names)
            # )
            n = 0
            t0 = time.time()
            for record in table:
                n = n + 1
                if n % 100000 == 0:
                    print(n, time.time() - t0)
                # attributs = ((i,str(j)) for i,j in zip(noms_attributs,record))
                # print ("dbf: attributs", record)
                # print ("dbf: attributs", list(attributs))
                # print (dir(record))
                rdict = list(record)
                # rdict = {i: str(record[i]) for i in noms_attributs}
                print(rdict)
                raise
                # self.alphaprocess(rdict)
                # obj = self.getobj(attributs=record)
                # if obj:
                #     obj.attributs["#type_geom"] = '0'
                #     obj.attributs["#chemin"] = chemin
                #     self.process(obj)

    except UnicodeError:
        print("erreur encodage le fichier", fichier, "n'est pas en ", reader.encoding)
    return


#                  reader,geom,hasschema,auxfiles,initer
READERS = {"dbf": (lire_objets_dbf, None, True, (), None)}
WRITERS = {}
READERS = {}
