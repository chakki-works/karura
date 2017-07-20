# -*- coding: utf-8 -*-
import os
import numpy as np
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.externals import joblib


class NumericalScalingInsight(Insight):

    def __init__(self, minmax_scale=False):
        super().__init__()

        self.minmax_scale = minmax_scale
        self.scalers = {}
        self.index.as_preprocessing()
        self.automatic = True
        self._scaled_columns = []
    
    def adopt(self, dfe, interpreted=None):
        targets = self.get_insight_targets(dfe)
        self._scaled_columns = targets
        dfe.df.dropna(subset=targets, inplace=True)

        for t in targets:
            scaler = StandardScaler() if not self.minmax_scale else MinMaxScaler()
            dfe.df[t] = scaler.fit_transform(dfe.df[t].values.reshape(-1, 1).astype(np.float32))
            self.scalers[t] = scaler

        return True

    def get_insight_targets(self, dfe):
        numericals = dfe.get_features(FType.numerical)
        if numericals is not None:
            return numericals.columns.tolist()
        else:
            return []
    
    @classmethod
    def _make_file_path(cls, path):
        f_name = cls.__name__.lower()
        f_path = os.path.join(path, f_name)
        return f_path

    def get_transformer(self, dfe):
        transformer = NumericalScalingTransformer(dfe, self)
        return transformer


class NumericalScalingTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, dfe, ns_insight):
        model_features = dfe.get_columns(include_target=False)
        self.target = [c for c in ns_insight._scaled_columns if c in model_features]
        self.scalers = {t: ns_insight.scalers[t] for t in self.target}

    def transform(self, X, y=None, copy=None):
        X[self.target] = X[self.target].fillna(0)
        for t in self.target:
            X[t] = self.scalers[t].transform(X[t].values.reshape(-1, 1).astype(np.float32))

        return X
