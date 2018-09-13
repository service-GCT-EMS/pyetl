# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 22:35:51 2018

@author: claude
"""
import requests
import io
infile="C:/Users/89965/Mes Documents (local)/projet_mapper/test_mapper/entree/ADICT_echantillons_geocodage/ADICT_echantillons_geocodage/1_geocodage/input_adresses_a_geocoder.csv"
url = 'http://adict.strasbourg.eu/addok/csv/'
buffer = '\n'.join(open(infile,'r').readlines()).encode('utf-8')
files = {'data': io.BytesIO(buffer)}
data = {'columns':'adresse'}
r = requests.post(url, files=files, data=data)
print(r.text)



