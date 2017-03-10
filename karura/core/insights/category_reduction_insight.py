# -*- coding: utf-8 -*-
import pandas as pd
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType


class CategoryReductionInsight(Insight):
    DUMMY_FLAG = "__OTHERS__"

    def __init__(self, count_threshold=10, freq_threshold=0.05):
        super().__init__()
        self.index.as_preprocessing()
        self.count_threshold = count_threshold
        self.freq_threshold = freq_threshold
        self.automatic = True
    
    def adopt(self, dfe, interpreted=None):
        targets = self.get_insight_targets(dfe)
        if len(targets) == 0:
            return True
        
        length = dfe.df.shape[0]
        for t in targets:
            freq = dfe.df[t].value_counts() / length < self.freq_threshold
            target = freq[freq].index
            dfe.df[t] = dfe.df[t].apply(lambda s: self.DUMMY_FLAG if s in target else s)

        self.description = {
            "ja": "項目{}では分類の数が多すぎるため、出現頻度が{}を超えない低頻度のものはその他に置換しました".format(targets, self.freq_threshold),
            "en": "Columns {} have many categories, so replaced the value to 'others' if its frequency under {}.".format(targets, self.freq_threshold)
        }
        return True

    def get_insight_targets(self, dfe):
        category_features = dfe.get_features(FType.categorical)
        if category_features is None:
            return []

        length = category_features.shape[0]
        targets = []
        for c in category_features.columns:
            categories = category_features[c].value_counts()
            if categories.index.size < self.count_threshold:
                continue
            else:
                freq = categories / length
                have_row_freq_vs = freq[freq < self.freq_threshold].count()
                if have_row_freq_vs > 0:
                    targets.append(c)
        return targets
