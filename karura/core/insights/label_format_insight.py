# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType


class LabelFormatInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_feature_augmentation()
        self.automatic = True
        self._label_conversion = None
    
    def adopt(self, dfe, interpreted=None):
        targets = self.get_insight_targets(dfe)
        if len(targets) > 0:
            target = targets[0]
            self._label_conversion = LabelEncoder()
            dfe.df[target] = self._label_conversion.fit_transform(dfe.df[target])
        return True

    def get_insight_targets(self, dfe):
        if dfe.get_target_ftype() == FType.categorical:
            return [dfe.target]
        else:
            return []
