"""interface web pour pyetl"""


from flask import Flask

# from flask_bootstrap import Bootstrap
import flaskfilemanager
from .config import config


app = Flask(__name__.split(".")[0],static_url_path="/mw")
# Bootstrap(app)
app.config.from_object(config.appconfig)

# You'll obviously do some more Flask stuff here!

# Initialise the filemanager
flaskfilemanager.init(app)
from pyetl_webapp import routes

# from .flaskfilemanager import filemanager

# filemanager.init(app)
