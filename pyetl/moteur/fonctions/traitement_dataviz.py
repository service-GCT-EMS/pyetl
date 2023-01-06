# -*- coding: utf-8 -*-
"""

@author: 89965
fonctions s de selections : determine si une regle est eligible ou pas
"""
import os
import pandas as pd
import altair as alt


def h_dfload(regle):
    """definit la regle comme declenchable"""
    dataloaders = {
        "csv": (pd.read_csv,{'delimiter':';', 'encoding':'cp1252', 'decimal':','}),
        "xls": (pd.read_excel,{}),
        "sql": (pd.read_sql,{}),
        "json": (pd.read_json,{}), 
    }
    if regle.params.cmp1.val == "#auto":
        regle.dataloader = None
        regle.dataloader = lambda x: dataloaders[
            os.path.splitext(regle.getval_entree(x))[1]
        ](regle.getval_entree(x))
    elif regle.params.cmp1.val == "#demo":
        from vega_datasets import data

        regle.dataset = data.getattr(regle.params.val_entree.val)
        regle.dataloader = lambda x: alt.Data(regle.dataset)
    elif regle.params.cmp1.val == "#url":
        regle.dataloader = lambda x: alt.Data(regle.getval_entree(x))
    elif regle.params.cmp1.val in dataloaders:
        fonction=dataloaders[regle.params.cmp1.val][0]
        params=dataloaders[regle.params.cmp1.val][1]
        regle.dataloader = lambda x: fonction(
            regle.getval_entree(x), **params
        )
    regle.dataloaders = dataloaders


def f_dfload(regle, obj):
    """#aide||charge un tableau pandas dans un attribut
    #parametres||attribut de sortie;nom du fichier;attribut contenant le nom;;format lecture
       #pattern||A;?C;?A;dfload;C;
          #test||notest
    """
    fich = regle.getval_entree(obj)
    dataloader = regle.dataloader
    try:
        df = dataloader(obj)
    except KeyError as err:
        regle.stock_param.logger.error("format inconnu %s", err)
        df = None
    if df is not None:
        obj.attributs[regle.params.att_sortie.val] = df
        return True
    return False


def f_dfset(regle, obj):
    """transforme des attributs tableaux en dataframe
    #parametres||attribut de sortie;;liste colonnes contenant des tableaux de valeurs
    #pattern||A;;L;dfset;;
    """
    contenu = {i: obj.attributs.get(i) for i in regle.params.att_entree.liste}
    df = pd.DataFrame(contenu)
    obj.attributs[regle.aprams.att_sortie.val] = df
    return True


def h_dfwrite(regle):
    """definit la regle comme declenchable"""
    regle.datawriters = {
        "csv": "to_csv",
        "xls": "to_excel",
        "sql": "to_sql",
        "json": "to_json",
    }
    if regle.params.cmp1.val in regle.datawriters:
        regle.datawriter = regle.datawriters[regle.params.cmp1.val]


def f_dfwrite(regle, obj):
    """#aide||charge un tableau dans pandas dans un attribut
    #parametres||fichier de sortie;;attribut contenant le nom;;format ecriture
       #pattern||?A;?C;A;dfwrite;?C
          #test||notest
    """
    attnom=regle.params.att_sortie.val
    fichier_sortie = obj.attributs.get(attnom) if attnom else regle.params.val_entree.val
    nom,ext=regle.prepare_place(fichier_sortie)
    datawriter = regle.datawriters.get(ext,regle.datawriter)
    df = obj.attributs.get(regle.params.att_entree.val)
    if isinstance(df,pd.DataFrame) and datawriter:
        getattr(df,datawriter)(nom)
        return True
    return False


def h_graph(regle):
    """preparation graphique"""
    regle.graphwriters={'.html','.png','.svg','.pdf','.json'}
    regle.options = regle.params.cmp2.vdict if regle.params.cmp2.val else dict()
    regle.charttyp = regle.params.cmp1.val
    if regle.params.pattern >= "2":
        sortie = regle.stock_param.webstore.setdefault("#print", [])
        regle.sortie = sortie
    if regle.params.pattern == "3":
        df = regle.getvar(regle.params.val_entree.val)
        chart = alt.Chart(df).getattr(regle.charttyp)().encode(**regle.options)
        sortie.append(chart.to_html())
    return True


def f_graph(regle, obj):
    """#aide||cree un graphique a partir d 'un tableau contenu dans un attribut
    #parametres1||attribut de sortie;fichier;attribut contenant les donnees;type de graphique;parametres
    #parametres2||;;attribut contenant les donnees;type de graphique;parametres
    #parametres3||;variable contenant les donnees;;type de graphique;parametres
    #pattern1||?A;C?;A;dfgraph;C;?LC
    #pattern2||=mws:;;A;dfgraph;C;?LC
    #pattern3||=mws:;P;;dfgraph;C;?LC
    """
    charttyp = regle.charttyp
    df = obj.attributs.get(regle.params.att_entree.val)
    chart = getattr(alt.Chart(df),charttyp)().encode(**regle.options)
    if regle.params.pattern == "1":
        if regle.params.att_sortie.val:
            obj.attributs[regle.params.att_sortie.val] = chart
        else:
            fichier_sortie=regle.params.val_entree.val
            nom,ext=regle.prepare_place(fichier_sortie)
            print ('ecriture',fichier_sortie,nom,ext,regle.options,regle.params.cmp2.liste)
            if ext in regle.graphwriters:
                chart.save(nom)
            else:
                regle.stock_param.logger.error("format inconnu %s",ext)
                raise StopIteration(1)
    elif regle.params.pattern == "2":
        regle.sortie.append(chart.to_html())
    return True

