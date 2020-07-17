# -*- coding: utf-8 -*-
"""
@author: claude
"""

import os
from flask import render_template
from pyetl_webapp import app


@app.route("/")
@app.route("/index")
def index():
    return render_template(
        "index.html", text="Hello, World!", title="mapper interface web"
    )


@app.route("/scripts")
def scripts():
    return render_template("scriptlist.html", liste=os.listdir("scripts"))
