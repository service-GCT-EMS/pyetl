# -*- coding: utf-8 -*-
"""acces services web mapper"""
import time

STARTTIME = time.time()
import sys
import requests


def wscaller(command, args, port=5000):
    url = "http://127.0.0.1:" + str(port) + "/ws/" + command.replace("#", "_")
    try:
        retour = requests.get(url, params=args)
    except requests.RequestException as err:
        print("erreur wfs", args, err)
        retour = ""
    if retour:
        description = retour.text
        print("retour web:", description)
    else:
        print("url", retour.url)
        print("pas de retour")


if __name__ == "__main__":
    # execute only if run as a script
    command = sys.argv[1]
    args = dict((i.split("=", 1) for i in sys.argv if "=" in i))
    port = int(args.get("port", 5000))
    print("args", command, args)
    wscaller(command, args, port)
