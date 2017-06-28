# -*- coding: utf-8 -*-
import os
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.externals import joblib


class NumericalScalingInsight(Insight):

    def __init__(self, minmax_scale=False):
        super().__init__()

        self.minmax_scale  = minmax_scale
        self.scaler = StandardScaler() if not minmax_scale else MinMaxScaler()
        self.index.as_preprocessing()
        self.automatic = True
        self._scaled_columns = []
    
    def save(self, path):
        self.path = path
        joblib.dump(self.scaler, self._make_file_path(path))

    def adopt(self, dfe, interpreted=None):
        targets = self.get_insight_targets(dfe)
        self._scaled_columns = targets
        dfe.df.dropna(subset=targets, inplace=True)
        dfe.df[targets] = self.scaler.fit_transform(dfe.df[targets])
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
        transformer.fit(dfe.df)
        return transformer


class NumericalScalingTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, dfe, numerical_scaling_insight):
        self.model_features = dfe.df.columns.tolist()
        self.targets = numerical_scaling_insight._scaled_columns
        self.scaler = StandardScaler() if not numerical_scaling_insight.minmax_scale else MinMaxScaler()

    def fit(self, X, y=None):
        _X = X.dropna(subset=self.model_features)
        _ = self.scaler.fit_transform(_X[self.model_features])
        return self  # do nothing

    def transform(self, X, y=None, copy=None):
        erased = []
        useful = []
        for t in self.targets:
            if t in self.model_features:
                useful.append(t)
            else:
                erased.append(t)
            
        X.drop(erased, axis=1, inplace=True)
        X[useful] = X[useful].fillna(0)
        X[useful] = self.scaler.transform(X[useful])
        return X
