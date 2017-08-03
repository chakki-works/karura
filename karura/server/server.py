# -*- coding: utf-8 -*-
import os
from functools import wraps
from urllib.parse import urlparse
import tornado.web
import tornado.escape
import karura.server.site as site
import karura.server.api as api


class PingHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("welcome.")

    def post(self):
        body = tornado.escape.json_decode(self.request.body)
        self.write(body)


def application(debug=False):
    app = tornado.web.Application(
        [
            (r"/ping", PingHandler),
            (r"/train", api.TrainingHandler),
            (r"/predict", api.PredictionHandler),
            (r"/download", api.DownloadHandler),
            (r"/", site.IndexHandler),
            (r"/auth", site.AuthenticationHandler),
            (r"/user", site.UserHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret=os.environ.get("SECRET_TOKEN", "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
        login_url="/",
        xsrf_cookies=True,
        debug=True,
    )
    return app
