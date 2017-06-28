# -*- coding: utf-8 -*-
import os
import tornado.web
import tornado.escape
from karura.env import EnvironmentalSettingException
from karura.core.kintone.kintone_exception import kintoneException
from karura.core.kintone.kintone_request import kintoneRequest
from karura.core.dataframe_extension import FType
from karura.default_config import make_autorun


class ErrorMessage():

    @classmethod
    def create(cls, message):
        return {
            "error": message
        }

class PingHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("welcome.")

    def post(self):
        body = tornado.escape.json_decode(self.request.body)
        self.write(body)


class TrainingHandler(tornado.web.RequestHandler):

    def post(self):
        """
        response = {'messages': [
            {'error': 0, 'message': 'hoge'},
            {'error': 1, 'message': 'hoge'},
        ], 'score': 0.8}
        self.write(response)
        """

        result = {}
        try:
            body = tornado.escape.json_decode(self.request.body)
            krequest = kintoneRequest()
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
        except EnvironmentalSettingException as eex:
            self.set_status(400)
            result = ErrorMessage.create("kintone/Slackにアクセスするための環境変数が設定されていません")
        except kintoneException as kex:
            self.set_status(400)
            result = ErrorMessage.create(str(kex))            
        except Exception as ex:
            import traceback
            self.set_status(500)
            ex = traceback.format_exc()
            result = ErrorMessage.create(ex)

        self.write(result)


class PredictionHandler(tornado.web.RequestHandler):

    def post(self):
        """
        dummy = {
            'prediction': {
                "house_price": 0
            }
        }
        self.write(dummy)
        """
        body = tornado.escape.json_decode(self.request.body)
        result = {}
        try:
            app_id = body["appId"]
            values = body["values"]
            model_manager = ModelManager.load(app_id)
            prediction = model_manager.predict(values)

            result = {
                "prediction": {
                    model_manager.field_manager.target.field_code: prediction
                }
            }
        except Exception as ex:
            print(ex)
            result = ErrorMessage.create(str(ex))
        self.write(result)


def application(debug=False):
    app = tornado.web.Application(
        [
            (r"/ping", PingHandler),
            (r"/train", TrainingHandler),
            (r"/predict", PredictionHandler)
        ],
        cookie_secret=os.environ.get("SECRET_TOKEN", "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
        debug=debug,
    )
    return app