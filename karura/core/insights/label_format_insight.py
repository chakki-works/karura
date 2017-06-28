# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.base import BaseEstimator, TransformerMixin
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType


class LabelFormatInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_label_format()
        self.automatic = True
        self._label_transformer = None
    
    def adopt(self, dfe, interpreted=None):
        target = self.get_insight_targets(dfe)[0]  # target column must exist

        if dfe.get_target_ftype() == FType.categorical:
            self._label_transformer = LabelEncoder()
            dfe.df[target] = self._label_transformer.fit_transform(dfe.df[target])
        else:
            self._label_transformer = StandardScaler()
            y = dfe.df[target].values.reshape(-1, 1).astype(float)
            dfe.df[target] = self._label_transformer.fit_transform(y)
        
        return True

    def get_insight_targets(self, dfe):
        return [dfe.target]

    def get_transformer(self, dfe):
        return self._label_transformer
