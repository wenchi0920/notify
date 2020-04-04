
import json
import os

import logging
import datetime
import requests

from flask import Flask

from flask import jsonify

from slackclient import SlackClient

class NotifyInterface :

    logger = ""

    def __init__(self):

        self.logger = logging.getLogger("Notify")
        logFormat = "%(asctime)s [%(levelname)s][%(name)s] : %(message)s"
        formatter = logging.Formatter(logFormat, datefmt="%Y-%m-%d %H:%M:%S")

        now = datetime.datetime.now()

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def processing(self, **kwargs):
        pass

    def returnMessage(self, msg, statusCode = 200):
        response = jsonify({
            "message": msg,
            "status": statusCode,
        })
        response.status_code = statusCode
        return response

    def postProcess(self, **kwargs):

        try:
            max = 3
            while max > 0 :
                res = requests.post(
                    kwargs.get("url"),
                    headers=kwargs.get("headers", {}),
                    data=kwargs.get("postData", {})
                )
                msg = json.loads(res.text)

                if res.status_code == 200:
                    return self.returnMessage("ok")

                max -= 1

            return self.returnMessage("Error status_code %s[%s] " % (res.status_code, msg))

        except Exception as e:
            return self.returnMessage("Exception %s " % e)


class LineNotify(NotifyInterface) :

    headers = {
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    postData = {}

    url = "https://notify-api.line.me/api/notify"

    def __init__(self, **kwargs):
        super(LineNotify, self).__init__(**kwargs)

    def processing(self, **kwargs):

        #   for teat
        #   curl -vvv -X POST -H "Authorization: Bearer xxxxxxxxxxxxxxxx" -H "Content-Type: application/json;charset=UTF-8" -H "Content-Type: application/x-www-form-urlencoded" --data 'message=testsssss' http://localhost

        self.headers.update({
            "Authorization" : "Bearer %s" % kwargs.get("token")
        })

        self.postData["message"] = kwargs.get("message")

        res = self.postProcess(
            url=self.url,
            headers=self.headers,
            postData=self.postData
        )
        return res


class SlackNotify(NotifyInterface) :

    def __init__(self, **kwargs):
        super(SlackNotify, self).__init__(**kwargs)

    def processing(self, **kwargs):

        #   for teat
        #   curl -vvv -X POST -H "Authorization: Bearer xxxxxxxxxxxxxxxxxx" -H "Content-Type: application/json;charset=UTF-8" -H "Content-Type: application/x-www-form-urlencoded" --data 'message=testss3sss' http://localhost

        channel = kwargs.get("channel", "")
        token = kwargs.get("token", "")
        message = kwargs.get("message")

        sc = SlackClient(token)

        res = sc.api_call(
                "chat.postMessage",
                channel = channel,
                text    = message ,
        )

        if res.get("ok") :
            return self.returnMessage("ok")

        else :
            return self.returnMessage(res.get("error"), 401)

        return res
