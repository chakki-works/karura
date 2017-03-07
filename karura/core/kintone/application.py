# -*- coding: utf-8 -*-
from collections import OrderedDict
import pykintone
import numpy as np
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension, FType
from karura.env import get_kintone_env


class Field():

    def __init__(self, code, f_type, label, is_unique):
        self.code = code
        self.f_type = f_type
        self.label = label
        self.is_unique = is_unique
    
    def get_feature_type(self):
        if self.f_type in ["CREATED_TIME", "CREATOR", "MODIFIER", "UPDATED_TIME", "RECORD_NUMBER", "作成日時", "作成者", "更新者", "更新日時", "レコード番号"]:
            return None # ignore
        elif self.f_type in ["FILE", "LINK", "RICH_TEXT", "STATUS_ASSIGNEE", "SUBTABLE"]:
            return None # ignore            
        elif self.is_unique:
            return FType.unique
        elif self.f_type in ["RADIO_BUTTON", "DROP_DOWN", "CHECK_BOX", "MULTI_SELECT", "CATEGORY", "STATUS", "カテゴリー", "ステータス", "USER_SELECT"]:
            # todo: think about multiselect
            return FType.categorical
        elif self.f_type in ["DATE", "DATETIME"]:
            return FType.datetime
        elif self.f_type in ["NUMBER", "CALC"]:
            return FType.numerical
        elif self.f_type in ["MULTI_LINE_TEXT", "SINGLE_LINE_TEXT"]:
            return FType.text
        else:
            return None


class Application():

    def __init__(self, env=None):
        self.env = env if env is not None else get_kintone_env()
    
    def get_app_id(self, app_name):
        kintone = pykintone.login(self.env.domain, self.env.login_id, self.env.password)
        result = kintone.administration().select_app_info()
        if result.ok:
            matched = [a for a in result.infos if a.name == app_name]
            if len(matched) > 0:
                return matched[0].app_id
            else:
                return ""
        else:
            raise Exception("Error occurred when getting the app_id")


    def load(self, app_id):
        app = pykintone.login(self.env.domain, self.env.login_id, self.env.password).app(app_id)
        fields_d = self.get_fields(app_id)

        selected = app.select(query="limit 500", fields=list(fields_d.keys()))  # todo: get over 500 records

        data = []
        columns = OrderedDict()
        for r in selected.records:
            row = []
            if len(columns) == 0:
                for f in r:
                    if f in fields_d:
                        columns[f] = fields_d[f]

            for f in columns:
                v = r[f]["value"]
                row.append(v)

            data.append(row)
        
        fields = list(columns.values())
        labels = [f.label for f in fields]
        df = pd.DataFrame(np.array(data), columns=labels)
        categoricals = [f.label for f in fields if f.get_feature_type() == FType.categorical]
        numericals = [f.label for f in fields if f.get_feature_type() == FType.numerical]
        datetimes = [f.label for f in fields if f.get_feature_type() == FType.datetime]
        texts = [f.label for f in fields if f.get_feature_type() == FType.text]
        uniques = [f.label for f in fields if f.get_feature_type() == FType.unique]

        dfe = DataFrameExtension(df, categoricals, numericals, datetimes, texts, uniques)
        return dfe

    def get_fields(self, app_id):
        # todo: if app_id exists on karura app, get field definition from it.

        app = pykintone.login(self.env.domain, self.env.login_id, self.env.password).app(app_id)
        fields = app.administration().form().get()

        if not fields.ok:
            raise Exception("Error occurred when getting the form information from kintone.")
        
        fs = fields.raw
        d = OrderedDict()

        for f_code in fs:
            f_type = fs[f_code]["type"]
            f_label = fs[f_code]["label"]
            is_unique = False
            if "unique" in fs[f_code]:
                is_unique = fs[f_code]["unique"]

            f = Field(f_code, f_type, f_label, is_unique)
            if f.get_feature_type() is not None:
                d[f_code] = f
        
        return d
