# -*- coding: utf-8 -*-
import os
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.externals import joblib


class NumericalScalingInsight(Insight):

    def __init__(self, load_path="", standard_than_minmax=True):
        super().__init__()

        if load_path and os.path.isfile(self._make_file_path(load_path)):
            self.path = load_path
            self.scaler = joblib.load(self._make_file_path(self.path))
            self._freeze = True
        else:
            self.scaler = StandardScaler() if standard_than_minmax else MinMaxScaler()
            self._freeze = False

        self.index.as_preprocessing()
        self.automatic = True
    
    def save(self, path):
        self.path = path
        joblib.dump(self.scaler, self._make_file_path(path))

    def adopt(self, dfe, interpreted=None):
        targets = self.get_insight_targets(dfe)
        dfe.df.dropna(inplace=True)
        if not self._freeze:
            dfe.df[targets] = self.scaler.fit_transform(dfe.df[targets])
        else:
            dfe.df[targets] = self.scaler.transform(dfe.df[targets])
        
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

