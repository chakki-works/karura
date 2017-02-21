# -*- coding: utf-8 -*-
from karura.core.insight import Insight


class CategoricalItemInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_column_check()
    
    def adopt(self, dfe, interpreted=None):
        if not interpreted:
            return 0
        targets = self.get_insight_targets(dfe)
        dfe.to_categorical(targets)
    
    def get_insight_targets(self, dfe):
        df = dfe.df
        def is_categorical(s):
            if s.dtype == float:
                return False

            c = s.count()
            freq = s.value_counts()

            if len(freq) / c <= 0.5:
                # records have to be accumulated by elements
                return True
            
            return False

        ts = []
        for c in df.columns:
            if is_categorical(df[c]):
                ts.append(c)
        
        if len(ts) > 0:
            self.description = {
                "ja": "{} は分類項目のようです。分類項目として処理してよいですか？".format(ts),
                "en": "{} seems to be categorical column. ok?".format(ts)
            }

        return ts


