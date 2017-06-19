import os
import json
from collections import namedtuple


class EnvironmentalSettingException(Exception):

    def __init__(self, message):
        super(EnvironmentalSettingException, self).__init__(message)


def get_slack_token():
    return _get_env("SLACK_TOKEN")


def get_lang():
    lang = _get_env("KARURA_LANG")
    lang = lang if lang else "ja"
    return lang


kintoneEnv = namedtuple("kintoneEnv", ["domain", "login_id", "password"])


def get_kintone_env():
    domain = _get_env("KINTONE_DOMAIN")
    login_id = _get_env("KINTONE_ID")
    password = _get_env("KINTONE_PASSWORD")
    env = kintoneEnv(domain, login_id, password)

    if env.domain == "" or env.login_id == "" or env.password == "":
        raise EnvironmentalSettingException("Can not get the information to Access the kintone")

    return env


def _get_env(key):
    value = os.environ.get(key, "")
    if not value:
        keys = _get_key_info()
        _key = key.lower()
        if _key in keys:
            value = keys[_key]
    return value
    

def _get_key_info():
    key_file = os.path.join(os.path.dirname(__file__), "../keys.json")
    keys = ()
    if os.path.isfile(key_file):
        with open(key_file, encoding="utf-8") as f:
            keys = json.load(f)
    return keys
