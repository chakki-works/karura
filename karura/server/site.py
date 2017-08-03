# -*- coding: utf-8 -*-
import os
from functools import wraps
from urllib.parse import urlparse
import tornado.web
import tornado.escape
from karura.server.message import ErrorMessage
from karura.database_api import DatabaseAPI


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
            self.render("user.html", key=DatabaseAPI.key_to_dict(self.current_user))


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
            self.render("user.html", key=DatabaseAPI.key_to_dict(key))
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
            self.render("user.html", key=DatabaseAPI.key_to_dict(self.current_user), error=error["error"])
        else:
            self.render("user.html", key=DatabaseAPI.key_to_dict(self.current_user), success="パスワードを変更しました")

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
            self.render("user.html", key=DatabaseAPI.key_to_dict(self.current_user), error=error["error"])
        else:
            self.clear_cookie(self.COOKIE_NAME)
            self.render("index.html")


class UserHandler(PageHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("user.html", key=DatabaseAPI.key_to_dict(self.current_user))

    @tornado.web.authenticated
    def post(self):
        self.clear_cookie(self.COOKIE_NAME)
        self.render("index.html")
