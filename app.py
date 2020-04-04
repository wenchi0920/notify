#!/usr/bin/env python3

import base64
import importlib

from flask import Flask
from flask_restful import Resource, Api
from flask_restful import reqparse

from libs import *
from libs import NotifyInterface

app = Flask(__name__)
api = Api(app)


class NotiyApi(Resource, NotifyInterface):

    dateStr = datetime.datetime.now().strftime("%Y-%m-%d")

    loggerFile = ""

    config = {}

    def __init__(self):

        self.logger = self.getLogger()
        self.logger.info("__init__")

        configFile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "config/config.json"
        )

        if not os.path.isfile(configFile):
            msg = "config is not found."
            self.logger.error(msg)
            raise Exception(msg)

        try :
            fp = open(configFile, "r")
            self.config = json.loads(fp.read())
            fp.close()
        except Exception as e :
            self.logger.error(e)
            raise Exception(e)


    def post(self):

        self.logger.info("[POST].")

        # see   https://blog.yorkxin.org/2013/09/30/oauth2-6-bearer-token.html
        # see   https://ithelp.ithome.com.tw/articles/10197166
        parser = reqparse.RequestParser()
        parser.add_argument('User-Agent', location='headers')
        parser.add_argument('Authorization', location='headers')
        parser.add_argument('message', location='form')

        args = parser.parse_args()

        self.logger.info("args %s " % args)

        res = self.auth(
            args.get("Authorization", "")
        )

        self.logger.info("res %s" % res.get("res", False))

        #return res
        if res.get("res", False) is not True :
            return res["response"]

        config = res["config"]

        # do notify api
        mod = getattr(
            importlib.import_module("libs"),
            "%sNotify" % config.get("action").title()
        )()

        response = mod.processing(
            token = config.get("api", {}).get("token", ""),
            channel = config.get("api", {}).get("channel", ""),
            message = args.get("message", "")
        )

        self.logger.info("response %s" % response)

        return response


    def decode(self, Authorization):

        if not Authorization or Authorization == "" :
            return False

        code = base64.b64decode(Authorization)
        code = code.decode()
        code = code.split("::")

        return {
            "key" : code[0],
            "token" : code[1]
        }

    def auth(self, Authorization):

        Authorization = Authorization.replace("Bearer", "").strip() if Authorization else ""
        auth = self.decode(Authorization)

        if not auth :
            return {
                "res" : False,
                "response" : NotifyInterface.returnMessage("ERROR: Unauthorized", 401)
            }

        authKey = auth['key']
        authToken = auth['token']

        if not self.config.get(authKey):
            return {
                "res" : False,
                "response" : NotifyInterface.returnMessage("ERROR: Forbidden[key]", 403)
            }

        elif self.config.get(authKey,{}).get("token", "") != authToken:
            return {
                "res" : False,
                "response" : NotifyInterface.returnMessage("ERROR: Forbidden[token]", 403)
            }

        elif not self.config.get(authKey, {}).get("enable", False) :
            return {
                "res" : False,
                "response" : NotifyInterface.returnMessage("ERROR: Forbidden[status]", 403)
            }

        return {
            "res" : True,
            "config" : self.config.get(authKey)
        }



    def getLogger(loggeLevel=logging.DEBUG):

        loggeLevel = logging.DEBUG

        logFile = os.path.join(
            os.path.dirname(__file__),
            "logs/%s.log" % datetime.datetime.now().strftime("%Y-%m-%d")
        )
        logger = logging.getLogger(__name__)
        logger.setLevel(loggeLevel)

        logFormat = "%(asctime)s [pid:%(process)d][line:%(lineno)d][%(levelname)s][%(name)s] : %(message)s"
        formatter = logging.Formatter(logFormat, datefmt="%Y-%m-%d %H:%M:%S")

        now = datetime.datetime.now()

        dirname = os.path.dirname(logFile)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        for hdlr in logger.handlers[:]:  # remove all old handlers
            logger.removeHandler(hdlr)

        fh = logging.FileHandler(logFile)
        fh.setLevel(loggeLevel)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(loggeLevel)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

api.add_resource(NotiyApi, '/')

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=80, debug=True)
