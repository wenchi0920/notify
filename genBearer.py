#!/usr/bin/env python3

import base64

from flask import Flask
from flask_restful import Api

from libs import *

app = Flask(__name__)
api = Api(app)



if __name__ == '__main__':

    configFile = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config/config.json"
    )

    if not os.path.isfile(configFile):
        msg = "config is not found."
        raise Exception(msg)

    try:
        fp = open(configFile, "r")
        config = json.loads(fp.read())
        fp.close()
    except Exception as e:
        raise Exception(e)

    for key, item in config.items():
        bearer = "%s::%s" % (key, item.get("api", {}).get("token", ""))
        bearer = base64.b64encode(bearer.encode())

        print("%s\t%s" % (key, bearer.decode()))

