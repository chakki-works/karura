# -*- coding: utf-8 -*-
import os
from functools import wraps
from urllib.parse import urlparse
import tornado.web
import tornado.escape
from karura.env import EnvironmentalSettingException
from karura.core.kintone.kintone_exception import kintoneException
from karura.core.kintone.kintone_request import kintoneRequest
from karura.core.dataframe_extension import FType
from karura.default_config import make_autorun
from karura.core.predictor import Predictor
from karura.database_api import DatabaseAPI


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


"""
karura web page handlers
"""

class PageHandler(tornado.web.RequestHandler):
    COOKIE_NAME = "karura_key"

    def get_current_user(self):
        user = self.get_secure_cookie(self.COOKIE_NAME)
        if user:
            user = tornado.escape.xhtml_escape(user)
        return user

    def prepare(self):
        method = self.get_body_argument("_method", default="").upper()
        if self.request.method == "POST" and method in ("PUT", "DELETE"):
            self.request.method = method


class IndexHandler(PageHandler):

    def get(self):
        if not self.current_user:
            self.render("index.html")
        else:
            self.render("user.html", user=self.current_user)


class AuthenticationHandler(PageHandler):

    def post(self):
        domain = self.get_body_argument("domain", default="")
        user = self.get_body_argument("user", default="")
        password = self.get_body_argument("password", default="")
        password_re = self.get_body_argument("password_re", default="")
        kind = self.get_body_argument("kind", default="login")

        error = None
        if not domain or not user or not password:
            error = ErrorMessage.create("ユーザーID、またはパスワードが入力されていません")
        elif sum(len(x) < 3 for x in (domain, user, password)) > 0:
            error = ErrorMessage.create("ユーザーID、またはパスワードの長さが不十分です")
        elif kind == "register" and password != password_re:
            error = ErrorMessage.create("パスワードが一致しません")

        key = ""
        if error is not None:
            self.set_status(400)
        else:
            api = DatabaseAPI()
            if kind == "register":
                try:
                    registered = api.register_user(domain, user, password)
                    key = registered["key"]
                except Exception as ex:
                    print(ex)
                    self.set_status(400)
                    error = ErrorMessage.create("ユーザー登録時にエラーが発生しました")
            elif kind == "login":
                try:
                    login = api.authenticate_user(domain, user, password)
                    key = login["key"]
                except Exception as ex:
                    print(ex)
                    self.set_status(401)
                    error = ErrorMessage.create("ログイン認証時にエラーが発生しました")
            else:
                self.set_status(400)
                error = ErrorMessage.create("想定されていない認証リクエストです")                

        if key:
            self.set_secure_cookie(self.COOKIE_NAME, key)
            self.render("user.html", user=self.current_user)
        else:
            self.render("index.html", kind=kind, error=error["error"])

    @tornado.web.authenticated
    def put(self):
        password_old = self.get_body_argument("password_old", default="")
        password = self.get_body_argument("password", default="")
        password_re = self.get_body_argument("password_re", default="")

        error = None
        if not password_old or not password or not password_re:
            error = ErrorMessage.create("パスワードが入力されていません")
        if len(password) < 3 or password != password_re:
            error = ErrorMessage.create("パスワードの長さが不十分、または一致しません")

        api = DatabaseAPI()
        user, domain = api.key_split(self.current_user)

        try:
            change_ok = api.change_user_password(domain, user, password_old, password)
        except Exception as ex:
            print(ex)
            self.set_status(401)
            error = ErrorMessage.create("パスワードの変更に失敗しました")

        if error:
            self.render("user.html", user=self.current_user, error=error["error"])
        else:
            self.render("user.html", user=self.current_user, success="パスワードを変更しました")

    @tornado.web.authenticated
    def delete(self):
        password = self.get_body_argument("password", default="")

        error = None
        if not password:
            error = ErrorMessage.create("パスワードが入力されていません")

        api = DatabaseAPI()
        user, domain = api.key_split(self.current_user)

        try:
            delete_ok = api.delete_user(domain, user, password)
        except Exception as ex:
            print(ex)
            self.set_status(401)
            error = ErrorMessage.create("アカウントの削除に失敗しました")

        if error:
            self.render("user.html", user=self.current_user, error=error["error"])
        else:
            self.clear_cookie(self.COOKIE_NAME)
            self.render("index.html")


class UserHandler(PageHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("user.html", user=self.current_user)


"""
karura api handlers
"""

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


def application(debug=False):
    app = tornado.web.Application(
        [
            (r"/ping", PingHandler),
            (r"/train", TrainingHandler),
            (r"/predict", PredictionHandler),
            (r"/", IndexHandler),
            (r"/auth", AuthenticationHandler),
            (r"/user", UserHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret=os.environ.get("SECRET_TOKEN", "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
        login_url="/",
        xsrf_cookies=True,
        debug=True,
    )
    return app