# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType


class DatetimeToCategoricalInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_preprocessing()
        self.automatic = True
        self._categorized = []

    def adopt(self, dfe, interpreted=None):
        targets = self.get_insight_targets(dfe)
        self._categorized = targets

        for t in targets:
            month = dfe.df[t].dt.month.rename(t + "_month").astype("category")
            day = dfe.df[t].dt.day.rename(t + "_day").astype("category")
            dfe.df = pd.concat([dfe.df, month, day], axis=1)
            dfe.to_categorical((month.name, day.name))
        
        dfe.df.drop(targets, axis=1, inplace=True)  # drop original column
        dfe.sync()
        return True

    def get_insight_targets(self, dfe):
        return dfe.get_columns(FType.datetime, include_target=False)

    def get_transformer(self, dfe):
        return DatetimeToCategoricalTransformer(dfe, self)


class DatetimeToCategoricalTransformer(BaseEstimator, TransformerMixin):

    def __init__(self, dfe, datetime_to_categorical_insight):
        self.model_features = dfe.df.columns.tolist()
        self.targets = datetime_to_categorical_insight._categorized

    def fit(self, X, y=None):
        return self  # do nothing
    
    def transform(self, X, y=None, copy=None):
        for t in self.targets:
            month_name = t + "_month"
            day_name = t + "_day"
            if month_name in self.model_features:
                month = X[t].dt.month.rename(month_name).astype("category")
                X = pd.concat([X, month], axis=1)
            if day_name in self.model_features:
                day = X[t].dt.day.rename(day_name).astype("category")
                X = pd.concat([X, day], axis=1)

            X.drop(t, axis=1, inplace=True)

        return X
