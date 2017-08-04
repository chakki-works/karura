# -*- coding: utf-8 -*-
import os
from functools import wraps
from urllib.parse import urlparse
import tempfile
import tornado.web
import tornado.escape
import pandas as pd
from karura.env import EnvironmentalSettingException
from karura.server.message import ErrorMessage
from karura.core.predictor import Predictor
from karura.database_api import DatabaseAPI
from karura.core.dataframe_extension import FTypeNames
from karura.core.kintone.kintone_request import kintoneRequest
from karura.core.kintone.kintone_exception import kintoneException
from karura.default_config import make_autorun


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
        pred = predictor.predict(df).values

        result = {
            "prediction": "{}".format(pred[0])
        }
        self.write(result)


class DownloadHandler(APIHandler):

    def initialize(self):
        if self._transforms is None:
            self._transforms = [tornado.web.GZipContentEncoding]

    def download_file(self, df, file_name, additional_header=()):
        if len(additional_header) > 0:
            header_df = pd.DataFrame.from_dict(additional_header, orient="columns")
            header_df = header_df[df.columns.tolist()]
            df = header_df.append(df, ignore_index=True)

        with tempfile.TemporaryDirectory() as dir:
            path = os.path.join(dir, file_name)
            df.to_csv(path, encoding="utf-8", compression="gzip", columns=df.columns.tolist())
            with open(path, "rb") as f:
                self.set_header("Content-Encoding", "gzip")
                self.set_header("Content-Type", "text/csv")
                self.set_header("Content-Disposition", "attachment; filename=\"{}\"".format(file_name))
                self.set_header("Content-Length", os.path.getsize(path))
                self.write(f.read())

    def get(self):
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        self.download_file(df, "predictions.csv")

    @validate_request
    def post(self, domain):
        body = tornado.escape.json_decode(self.request.body)
        app_id = body["app_id"]
        api = DatabaseAPI()
        krequest = kintoneRequest(env=api.get_kintone_env(domain))
        dfe = krequest.download(body)
        _df = dfe.df.copy(deep=True)

        predictor = Predictor.load_from_env(krequest.env, app_id)
        pred = predictor.predict(dfe.df)

        pred_column = pred.name + "_prediction"
        _df[pred_column] = pred
        type_header = {}
        for c in _df.columns:
            if c in dfe.df.columns.tolist() + [pred.name, pred_column]:
                _c = c if c != pred_column else pred.name
                type_header[c] = FTypeNames[dfe.ftypes[_c]]
            else:
                type_header[c] = ""
            if c == pred.name:
                type_header[c] += "/TGT"
            elif c == pred_column:
                type_header[c] += "/PRED"

            type_header[c] = [type_header[c]]  # for from_dict columns
        dfe = None  # free memory
        ordered = [c for c in _df.columns if c not in [pred.name, pred_column]] + [pred.name, pred_column]
        _df = _df[ordered]
        self.download_file(_df, "prediction.csv", type_header)


class UploadHandler(APIHandler):

    @validate_request
    def post(self, domain):
        body = tornado.escape.json_decode(self.request.body)
        print(body)
        app_id = body["app_id"]
        api = DatabaseAPI()
        krequest = kintoneRequest(env=api.get_kintone_env(domain))
        dfe = krequest.download(body)
        _df = dfe.df.copy(deep=True)
        predictor = Predictor.load_from_env(krequest.env, app_id)
        pred = predictor.predict(dfe.df)
        dfe = None  # free memory

        _df.loc[:, "prediction"] = pred

        self.download_file(_df, "prediction.csv")
