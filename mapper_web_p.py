# -*- coding: utf-8 -*-
"""modification d'attributs en fonction d'un fichier de parametrage avec
prise en charge des expressions regulieres"""
import time

STARTTIME = time.time()
import sys

from pyetl_webapp import app

# print ('mapper: fin import modules',int(time.time()-t1))
# import cProfile as profile
# ---------------debut programme ---------------
# lancement flask run mapper_web

if __name__ == "__main__":
    # execute only if run as a script
    from waitress import serve

    args = dict((i.split("=", 1) for i in sys.argv if "=" in i))
    port = int(args.get("port", 5500))
    host=args.get("host", "127.0.0.1")

    print("essai serveur host:",host,"port:", port)
    # app.run(port=port)
    # serve(app, host="127.0.0.1", port=port,threads=10)
    if "http" in args:
        serve(app, host=host, port=port,threads=10)
    else:
        serve(app, host=host, port=port,threads=10, url_scheme='https')
