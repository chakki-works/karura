# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType


class CategoricalToDummyInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_feature_augmentation()
        self.automatic = True
        self._categorical_to_dummy = {}
    
    def adopt(self, dfe, interpreted=None):
        self._categorical_to_dummy = {}
        targets = self.get_insight_targets(dfe)
        dummies = pd.get_dummies(dfe.df[targets])

        for t in targets:
            self._categorical_to_dummy[t] = []
            for d in dummies.columns:
                if d.startswith(t):
                    self._categorical_to_dummy[t].append(d)

        dfe.df = pd.concat([dfe.df, dummies], axis=1)
        dfe.df.drop(targets, axis=1, inplace=True)  # drop original column
        dfe.to_categorical(dummies.columns.tolist())
        dfe.sync()
        return True

    def get_insight_targets(self, dfe):
        return dfe.get_columns(FType.categorical, include_target=False)

    def get_transformer(self, dfe):
        return CategoricalToDummyTransformer(dfe, self)


class CategoricalToDummyTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, dfe, categorical_to_dummy_insight):
        self.model_features = dfe.df.columns.tolist()
        self.categorical_to_dummy = categorical_to_dummy_insight._categorical_to_dummy

    def fit(self, X, y=None):
        return self  # do nothing
    
    def transform(self, X, y=None, copy=None):
        for c in self.categorical_to_dummy:
            categoricals = X[c]
            dummies = self.categorical_to_dummy[c]
            useful_dummies = [d for d in dummies if d in self.model_features]

            for ud in useful_dummies:
                name, value = ud.rsplit("_")
                d = categoricals.map(lambda v: 1 if str(v) == value else 0).rename(ud)
                X = pd.concat([X, d], axis=1)
            X.drop(c, axis=1, inplace=True)

        return X
