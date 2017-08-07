# -*- coding: utf-8 -*-
from io import BytesIO
import pandas as pd
import pykintone
from karura.env import get_kintone_env
from karura.core.kintone.application import Application
from karura.core.kintone.kintone_exception import kintoneException
from karura.core.dataframe_extension import FType, FTypeNames, DataFrameExtension


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
        query = ""
        if view_name:
            views = app.administration().view().get().views
            for v in views:
                if v.name == view_name:
                    view = v
                    break

            if view is None:
                raise kintoneException("指定された名前のビュー「{}」は、アプリに作成されていません".format(view_name))
        
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

    def record_to_df(self, request_json):
        app_id = request_json["app_id"]
        values = request_json["values"]
        kapp = Application(self.env)
        fields_d = kapp.get_fields(app_id)

        columns = []
        data = []
        for k in values:
            if k not in fields_d:
                continue
            f = fields_d[k]
            columns.append(f.label)
            data.append(values[k])
        df = pd.DataFrame(data=[data], columns=columns)
        return df

    def download(self, request_json):
        app_id = request_json["app_id"]
        view_name = request_json["view"]

        # confirm view
        app = pykintone.login(self.env.domain, self.env.login_id, self.env.password).app(app_id)
        view = None
        query = ""
        fields = []
        if view_name:
            views = app.administration().view().get().views
            for v in views:
                if v.name == view_name:
                    view = v
                    break

            if view is None:
                raise kintoneException("指定された名前のビュー「{}」は、アプリに作成されていません".format(view_name))
        
            # make query
            query = view.filter_cond if view.filter_cond else ""
            query += " order by " + view.sort if view.sort else ""

            fields = view.fields

        # make dfe
        kapp = Application(self.env)
        dfe = kapp.load(app_id, query, fields)

        return dfe

    def file_to_df(self, byte_str):
        fileio = BytesIO(byte_str)
        columns = []
        ftype_names = []
        index = 0
        for line in fileio:
            items = line.decode("utf-8").split("\t")
            items = [i.strip() for i in items]
            if index == 0:
                columns = items
            elif index == 1:
                ftype_names = items
            index += 1
            if index == 2:
                break

        df = pd.read_csv(fileio, encoding="utf-8", sep="\t")
        df.columns = columns
        ignored_columns = []
        _ftype_names = {}
        target = ""

        index = 0
        for c, fn in zip(columns, ftype_names):
            if not fn:
                ignored_columns.append(index)
            else:
                fn_attr = fn.split("/")
                _fn = fn_attr[0]
                attr = "" if len(fn_attr) == 1 else fn_attr[1]
                
                if attr == "PRED":
                    ignored_columns.append(index)
                elif attr == "TGT":
                    target = c
                    _ftype_names[c] = _fn
                else:
                    _ftype_names[c] = _fn

            index += 1

        ftypes = {}
        for ftype in FTypeNames:
            name = FTypeNames[ftype]
            ftypes[ftype] = [k for k, v in _ftype_names.items() if v == name]

        df.drop(df.columns[ignored_columns], axis=1, inplace=True)
        dfe = DataFrameExtension(df, ftypes[FType.categorical], ftypes[FType.numerical], ftypes[FType.datetime], ftypes[FType.text], ftypes[FType.unique])
        dfe.target = target
        return dfe
