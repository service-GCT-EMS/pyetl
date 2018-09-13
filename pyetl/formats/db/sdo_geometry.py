# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 16:45:47 2017

@author: 89965
"""

def geom_from_sdo(obj):
    '''convertit une geometrie sdo en geometrie interne'''
    if obj.geom is None:
        obj.geom = []
    else:
        geom = obj.geom
        gtype = geom.SDO_GTYPE
        obj.geom_v.type = gtype
        obj.geom_v.srid = geom.SDO_SRID

    if not obj.geom:
        obj.attributs['#type_geom'] = '0'
#        obj.is_3d = False
        obj.dimension = 0
        obj.geom_v.type = '0'
        obj.geom_v.valide = True
        return True
    geom_v = obj.geom_v
    if obj.schema: # s'il y a un schema : on force le type de geometrie demandees
        geom_demandee = obj.schema.info["type_geom"]
#    _parse_ewkt(geom_v,obj.geom[0])
#    _parse_ewkt(geom_v,obj.geom[0],type_geom_demande=geom_demandee)
