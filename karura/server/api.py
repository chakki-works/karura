# -*- coding: utf-8 -*-
import os
from functools import wraps
from urllib.parse import urlparse
import tornado.web
import tornado.escape
from karura.env import EnvironmentalSettingException
from karura.server.message import ErrorMessage
from karura.core.kintone.kintone_request import kintoneRequest
from karura.default_config import make_autorun
from karura.core.predictor import Predictor
from karura.database_api import DatabaseAPI


def validate_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        origin = self.request.headers.get("Origin")
        error = None
        if not origin:
            self.set_status(403)
            error = ErrorMessage.create("送信元が不明なリクエストです")
        else:
            source = urlparse(origin)
            if source.scheme != "https":
                self.set_status(403)
                error = ErrorMessage.create("セキュアな送信元ではありません")
            else:
                hostname = source.hostname
                if not hostname.endswith("cybozu.com"):
                    self.set_status(403)
                    error = ErrorMessage.create("kintoneからのリクエストではありません")
        if error is not None:
            self.write(error)
        else:
            domain = hostname.split(".")[0]
            try:
                func(domain=domain, *args, **kwargs)
            except EnvironmentalSettingException as eex:
                self.set_status(400)
                error = ErrorMessage.create("kintone/Slackにアクセスするための環境変数が設定されていません")
                self.write(error)
            except kintoneException as kex:
                self.set_status(400)
                error = ErrorMessage.create(str(kex))            
                self.write(error)
            except Exception as ex:
                import traceback
                self.set_status(500)
                ex = traceback.format_exc()
                error = ErrorMessage.create(ex)
                self.write(error)

    return wrapper


class APIHandler(tornado.web.RequestHandler):

    def check_xsrf_cookie(self):
        pass


class TrainingHandler(APIHandler):

    @validate_request
    def post(self, domain):
        body = tornado.escape.json_decode(self.request.body)
        app_id = body["app_id"]
        api = DatabaseAPI()
        krequest = kintoneRequest(env=api.get_kintone_env(domain))
        dfe = krequest.request_to_dfe(body)
        autorun = make_autorun(dfe, feature_type_estimation=False)
        descriptions = autorun.execute()
        model = autorun.result()

        score = 0 if model is None else model.score
        messages = []
        for i, d in enumerate(descriptions):
            if i == len(descriptions) -1 and model is None:
                message = {"error": 1, "message": d.desc}
            else:
                message = {"error": 0, "message": d.desc}
            messages.append(message)
        
        image = b"" if model is None else model.describe().picture.to_base64()

        result = {
            "score": score,
            "messages": messages,
            "image": image.decode("utf-8")
        }

        predictor = autorun.to_predictor()
        predictor.save_to_env(krequest.env, app_id)

        self.write(result)


class PredictionHandler(APIHandler):

    @validate_request
    def post(self, domain):
        body = tornado.escape.json_decode(self.request.body)

        app_id = body["app_id"]
        values = body["values"]
        api = DatabaseAPI()
        krequest = kintoneRequest(env=api.get_kintone_env(domain))
        df = krequest.record_to_df(body)
        predictor = Predictor.load_from_env(krequest.env, app_id)
        pred = predictor.predict(df)

        result = {
            "prediction": "{}".format(pred[0])
        }
        self.write(result)