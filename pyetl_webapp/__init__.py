"""interface web pour pyetl"""


from flask import Flask
from .config import config

app = Flask(__name__)
app.config.from_object(config.appconfig)

from pyetl_webapp import routes
