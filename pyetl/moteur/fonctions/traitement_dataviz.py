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
        "csv": pd.read_csv,
        "xls": pd.read_excel,
        "sql": pd.read_sql,
        "json": pd.read_json,
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
        regle.dataloader = lambda x: dataloaders[regle.params.cmp1.val](
            regle.getval_entree(x)
        )
    regle.dataloaders = dataloaders


def f_dfload(regle, obj):
    """#aide||charge un tableau pandas dans un attribut
    #parametres||attribut de sortie;nom du fichier;attribut contenant le nom;;format lecture
       #pattern||A;?C;?A;dfload;C;
          #test||notest
    """
    fich = regle.getvalentree(obj)
    dataloader = regle.dataloader
    try:
        df = dataloader(obj)
    except KeyError as err:
        regle.stock_param.logger.error("format inconnu %s", err)
        df = None
    if df:
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
    datawriters = {
        "csv": "to_csv",
        "xls": "to_excel",
        "sql": "to_sql",
        "json": "to_json",
    }
    if regle.params.cmp1.val in datawriters:
        regle.datawriter = datawriters[regle.params.cmp1.val]


def f_dfwrite(regle, obj):
    """#aide||charge un tableau dans pandas dans un attribut
    #parametres||fichier de sortie;;attribut contenant le nom;;format lecture
       #pattern||A;;A;dfwrite;C;
          #test||notest
    """
    fich = regle.params.att_sortie.val()
    datawriter = regle.datawriter
    df = obj.attributs.get(regle.params.att_entree.val())
    if df:
        df.getattr(datawriter)(fich)
        return True
    return False


def h_graph(regle):
    """preparation graphique"""
    regle.options = regle.params.cmp2.vdict()
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
    """#aide||cree un graphique
    #pattern1||C;;A;dfgraph;C;H
    #pattern2||=mws:;;A;dfgraph;C;H
    #pattern3||=mws:;P;;dfgraph;C;H
    """
    charttyp = regle.charttyp
    df = obj.attributs.get(regle.params.att_entree.val())
    chart = alt.Chart(df).getattr(charttyp)().encode(**regle.options)
    if regle.params.pattern == "1":
        obj.attributs[regle.params.att_sortie.val] = chart
    elif regle.params.pattern == "2":
        regle.sortie.append(chart.to_html())
    return True
