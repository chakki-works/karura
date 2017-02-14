# -*- coding: utf-8 -*-
import re
from io import StringIO
import requests
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import default_reply
import pandas as pd
from karura.default_analyst import make_analyst
from karura.env import get_slack_token


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
    karura.analyze()
    if karura.has_insight():
        message.reply(karura.describe_insight())
    else:
        print(karura.dfe.df.dtypes)
        message.reply("Done analyze!")


@respond_to(r"はい|yes", re.IGNORECASE)
def resolve_yes(message):
    if Scope.Karura is not None and Scope.Karura.has_insight():
        Scope.Karura.resolve(True)
        talk(message)


@respond_to(r"いいえ|no", re.IGNORECASE)
def resolve_no(message):
    if Scope.Karura is not None and Scope.Karura.has_insight():
        Scope.Karura.resolve(False)
        talk(message)


@default_reply
def default_handler(message):
    message.reply("それな")
