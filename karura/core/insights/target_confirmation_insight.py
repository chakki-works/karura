# -*- coding: utf-8 -*-
from karura.core.insight import Insight


class TargetConfirmInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_column_check()

    def is_applicable(self, dfe):
        if dfe.target:
            return False
        else:
            self.description = {
                "ja": "予測対象の項目を指定してください",
                "en": "Please select the prediction target column"
            }
            return True
    
    def adopt(self, dfe, interpreted=None):
        if not interpreted or interpreted not in dfe.df.columns:
            self.description = {
                "ja": "指定された予測対象の項目は存在しません。データ項目の中から選んでください",
                "en": "Directed target is not found. You have to select it from your data columns."
            }
            return False
        else:
            dfe.target = interpreted
            return True
    
    def interpret(self, reply):
        return str(reply).strip()
