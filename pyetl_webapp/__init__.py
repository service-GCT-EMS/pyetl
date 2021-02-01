"""interface web pour pyetl"""


from flask import Flask
from flask_bootstrap import Bootstrap
from .config import config

app = Flask(__name__.split(".")[0])
Bootstrap(app)
app.config.from_object(config.appconfig)

from pyetl_webapp import routes

# from .flaskfilemanager import filemanager

# filemanager.init(app)
