# -*- coding: utf-8 -*-
"""acces services web mapper"""
import time

STARTTIME = time.time()
import sys
import requests


def wscaller(command, args, port=5000):
    url = "http://127.0.0.1:" + str(port) + "/mws" + "/" + command
    try:
        retour = requests.get(url, params=args)
    except requests.RequestException as err:
        print("erreur mws", args, err)
        retour = ""
    if retour:
        description = retour.text
        con_type = retour.headers.get("Content-Type")
        print(
            "retour web:",
            description,
            # retour.json(),
            retour.content.decode("utf-8"),
            con_type,
        )
    else:
        print("url", retour.url)
        print("pas de retour")


if __name__ == "__main__":
    # execute only if run as a script
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    args = dict((i.split("=", 1) for i in sys.argv if "=" in i))
    port = int(args.get("port", 5000))
    print("args", command, args)
    wscaller(command, args, port)
