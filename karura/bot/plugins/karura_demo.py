# -*- coding: utf-8 -*-
import re
from io import StringIO
import requests
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import default_reply
import pandas as pd
from karura.core.kintone.application import Application
from karura.default_config import make_analyst
from karura.env import get_slack_token
from karura.core.description import Description


class Scope:
    Karura = None


@listen_to("\<(.*)\> uploaded .* \<(.*)\>")
def receive_file(message, user, url):
    body = message.body
    if not body["upload"]:
        return 0
    name = body["user_profile"]["name"] 
    file_url = body["file"]["url_private"]
    file_name = body["file"]["name"]
    
    #message.send("{} uploaded {}".format(name, file_url))
    key = get_slack_token()
    resp = requests.get(file_url, headers={"Authorization": "Bearer {}".format(key)})
    if resp.ok:
        df = pd.read_csv(StringIO(resp.content.decode(resp.encoding)))

    print(df.dtypes)
    Scope.Karura = make_analyst(df)
    print(Scope.Karura)
    talk(message)


def talk(message):
    if Scope.Karura is None:
        message.reply("karura is not found. please upload file first.")
    
    karura = Scope.Karura

    if not karura.has_done():
        d = karura.step()
        if not d:
            talk(message)
        else:
            send(message, d)

            if not karura.have_to_ask():
                print(d)
                talk(message)

    else:
        m = karura.result()
        send(message, m)


def send(message, description):
    print("say: {}".format(description))
    description.send_reply(message)


def get_reply(message, reply):
    print("reply: {}".format(reply))
    if Scope.Karura is not None and Scope.Karura.have_to_ask():
        Scope.Karura.get_reply(reply)
        return True
    else:
        return False


@respond_to(r"(.+)")
def refrection(message, reply):
    yes_ptn = r"はい|yes"
    no_ptn = r"いいえ|ない|no|not"

    if reply == "reset":
        Scope.Karura = None
    elif Scope.Karura is None:
        app = Application()
        app_id = app.get_app_id(reply)
        if app_id:
            dfe = app.load(app_id, limit_over=True)
            Scope.Karura = make_analyst(dfe)
            talk(message)
    else:
        replied = False
        if re.match(yes_ptn, reply):
            replied = get_reply(message, True)
        elif re.match(no_ptn, reply):
            replied = get_reply(message, False)
        else:
            replied = get_reply(message, reply)

        if replied:
            talk(message)
        else:
            message.reply("Can not understand your reply!")


@default_reply
def default_handler(message):
    message.reply("それな")
