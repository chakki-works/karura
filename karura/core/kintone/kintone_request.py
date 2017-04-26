# -*- coding: utf-8 -*-
import pykintone
from karura.env import get_kintone_env
from karura.core.kintone.application import Application
from karura.core.kintone.kintone_exception import kintoneException


class kintoneRequest():

    def __init__(self, env=None):
        self.env = env if env is not None else get_kintone_env()
    
    def request_to_dfe(self, request_json):
        app_id = request_json["app_id"]
        field_settings = request_json["fields"]
        view_name = request_json["view"]

        # check fields setting
        features = []
        target = ""
        for fs in field_settings:
            if field_settings[fs]["usage"] == 1:
                target = fs
            elif field_settings[fs]["usage"] == 0:
                features.append(fs)
        
        if not target:
            raise kintoneException("予測対象の項目が指定されていません")
            
        if len(features) == 0:
            raise kintoneException("予測に使用する項目が指定されていません")

        # confirm view
        app = pykintone.login(self.env.domain, self.env.login_id, self.env.password).app(app_id)
        view = None

        if view_name:
            views = app.administration().view().get().views
            for v in views:
                if v.name == view_name:
                    view = v
                    break

            if view is None:
                raise kintoneException("指定された名前のビュー{}は、アプリに作成されていません".format(view_name))
        
        # make query
        query = view.filter_cond if view.filter_cond else ""
        query += " order by " + view.sort if view.sort else ""

        # make field setting
        fields = features if view is None else [f for f in view.fields if f in features]
        fields = [target] + fields

        # make dfe
        kapp = Application(self.env)
        dfe = kapp.load(app_id, query, fields, target)

        return dfe
