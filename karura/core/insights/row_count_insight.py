# -*- coding: utf-8 -*-
from karura.core.insight import Insight
from karura.core.analysis_stop_exception import AnalysisStopException


class RowCountInsight(Insight):

    def __init__(self, min_count=50, max_count=10000):
        super().__init__()
        self.index.as_row_check()
        self.min_count = min_count  # by scikit-learn choosing model map
        self.max_count = max_count
        self.automatic = True
    
    def is_applicable(self, dfe):
        if dfe.df.shape[0] > self.max_count:
            self.description = {
                "ja": "データが最大件数({})を超えています。最大件数までのレコードを使用します。",
                "en": "Your data's row count exceeds the limit({}). So I'll limit the row."
            }
            return True
        elif dfe.df.shape[0] < self.min_count:
            self.description = {
                "ja": "データが少なすぎます。モデルを作成するには、最低{}件データを集めてください".format(self.min_count),
                "en": "Your data is too small. You have to collect the data at least {} count of data.".format(self.min_count)
            }
            raise AnalysisStopException(self)
        elif dfe.df.shape[0] < dfe.df.shape[1]:
            self.description = {
                "ja": "項目の数に対して、データが少なすぎます。せめて項目の数以上にはデータを集める必要があります。",
                "en": "Your data is too small. You have to collect the data greather than number of columns."
            }
            raise AnalysisStopException(self)

        return False

    def adopt(self, dfe, interpreted=None):
        dfe.df.drop(dfe.df.index[self.max_count:], inplace=True)
        return True
