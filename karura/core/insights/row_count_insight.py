# -*- coding: utf-8 -*-
from karura.core.insight import Insight


class RowCountInsight(Insight):

    def __init__(self, max_row=10000):
        super().__init__()
        self.index.as_row_check()
        self.max_row = max_row
        self.automatic = True
    
    def is_applicable(self, dfe):
        if dfe.df.shape[0] > self.max_row:
            self.description = {
                "ja": "データが最大件数({})を超えています。最大件数までのレコードを使用します。",
                "en": "Your data's row count exceeds the limit({}). So I'll limit the row."
            }
            return True
        else:
            return False

    def adopt(self, dfe, interpreted=None):
        if not interpreted:
            return 0
        dfe.df = dfe.df.head(self.max_row)
