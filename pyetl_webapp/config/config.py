# -*- coding: utf-8 -*-
"""
@author: claude
"""
import os


class Config(object):
    SECRET_KEY = (
        os.environ.get("SECRET_KEY")
        or "quand il n'y a pas de solution il n'y a pas de problème"
    )

appconfig = Config()
