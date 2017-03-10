# -*- coding: utf-8 -*-
import pandas as pd
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType


class CategoricalToDummyInsight(Insight):

    def __init__(self):
        super().__init__()
        self.index.as_feature_augmentation()
        self.automatic = True
    
    def adopt(self, dfe, interpreted=None):
        targets = self.get_insight_targets(dfe)
        dummies = pd.get_dummies(dfe.df[targets])
        dfe.df = pd.concat([dfe.df, dummies], axis=1)
        dfe.df.drop(targets, axis=1, inplace=True)  # drop original column
        dfe.to_categorical(dummies.columns.tolist())
        dfe.sync()
        return True

    def get_insight_targets(self, dfe):
        return dfe.get_columns(FType.categorical, include_target=False)
