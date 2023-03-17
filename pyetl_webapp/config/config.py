# -*- coding: utf-8 -*-
"""
@author: claude
"""
import os


class Config(object):
    SECRET_KEY = (
        os.environ.get("PYEYL_WEB_KEY")
        or "quand il n'y a pas de solution il n'y a pas de problème"
    )
    FLASKFILEMANAGER_FILE_PATH = "C:/dev/test_mapper"
    
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

appconfig = Config()
