# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 22:35:51 2018

@author: claude
"""
import pycurl
infile="C:/Users/89965/Mes Documents (local)/projet_mapper/test_mapper/entree/ADICT_echantillons_geocodage/ADICT_echantillons_geocodage/1_geocodage/input_adresses_a_geocoder.csv"
with open('out.csv', 'wb') as f:
    c = pycurl.Curl()
    c.set_url('http://adict.strasbourg.eu/addok/csv/')
    c.setopt(c.URL, 'http://adict.strasbourg.eu/addok/csv/')
    c.setopt(c.HTTPPOST, [('data', (c.FORM_FILE, infile,))])
        # upload the contents of this file
    c.setopt(c.WRITEDATA, f)
    c.perform()
    c.close()



