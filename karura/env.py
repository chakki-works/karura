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


def get_database_uri():
    uri = _get_env("DATABASE_URI")
    if uri:
        return uri
    else:
        mongo = os.environ.get("MONGODB_URI", "")
        return mongo


def get_private_key():
    return _get_env("PRIVATE_KEY")


def get_store_path():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../trained_models"))
    if not os.path.exists(path):
        os.mkdir(path)
    return path


kintoneEnv = namedtuple("kintoneEnv", ["domain", "login_id", "password"])


def get_kintone_env():
    domain = _get_env("KINTONE_DOMAIN")
    login_id = _get_env("KINTONE_ID")
    password = _get_env("KINTONE_PASSWORD")
    env = kintoneEnv(domain, login_id, password)

    if env.domain == "" or env.login_id == "" or env.password == "":
        raise EnvironmentalSettingException("Can not get the information to Access the kintone")

    return env


def get_kintone_env_by_domain(domain):
    from karura.database_api import DatabaseAPI
    uri = get_database_uri()
    api = DatabaseAPI(database_uri=uri)
    

def _get_env(key):
    value = os.environ.get(key.lower(), "") or os.environ.get(key.upper(), "")

    if not value:
        keys = _get_key_info()
        _key = key.upper()
        for k in keys:
            if k.upper() == _key:
                value = keys[_key]
                break
    return value
    

def _get_key_info():
    key_file = os.path.join(os.path.dirname(__file__), "../keys.json")
    keys = ()
    if os.path.isfile(key_file):
        with open(key_file, encoding="utf-8") as f:
            keys = json.load(f)
            keys = dict((k.upper(), v) for k, v in keys.items())
    return keys
