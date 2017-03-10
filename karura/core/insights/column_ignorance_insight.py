# -*- coding: utf-8 -*-
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType


class ColumnIgnoranceInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_column_check()

    def is_applicable(self, dfe):
        self.description = {
            "ja": "分析から除外する項目があれば指定してください",
            "en": "Please select columns that you want to exclude."
        }
        return True
    
    def adopt(self, dfe, interpreted=None):
        if interpreted is not None and isinstance(interpreted, list) and len(interpreted) > 0:
            columns = []
            for i in interpreted:
                if i in dfe.df.columns:
                    columns.append(i)

            dfe.df.drop(columns, inplace=True, axis=1)
            dfe.sync()

        return True
    
    def interpret(self, reply):
        if isinstance(reply, bool):
            return []
        else:
            columns = [c.strip() for c in str(reply).strip().split(",")]
            return columns
