"""interface web pour pyetl"""


from flask import Flask

app = Flask(__name__)

from pyetl_webapp import routes
