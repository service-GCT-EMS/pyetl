# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 10:29:10 2017

@author: 89965
"""

import pstats
pstats.Stats('schemamapper.profile').sort_stats('cumtime').print_stats()