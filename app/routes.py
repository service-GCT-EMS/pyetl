

import os
from app import app


@app.route("/")
@app.route("/index")
def index():
    return "Hello, World!"

@app.route("/scripts")
def scripts():
    return "\n".join((i for i in os.listdir("scripts")))
