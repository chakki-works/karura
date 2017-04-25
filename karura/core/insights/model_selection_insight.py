# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import r2_score
from karura.core.insight import Insight
from karura.core.dataframe_extension import FType
from karura.core.analysis_stop_exception import AnalysisStopException
from karura.core.description import ImageFile, Description


class ModelSelectionInsight(Insight):

    def __init__(self, test_size=0.2):
        super().__init__()
        self.test_size = test_size
        self.cv_count = 3
        self.index.as_model_selection()
        self.model = None
        self.score = 0
        self.automatic = True
    
    def is_applicable(self, dfe):
        self.description = {}
        if dfe.get_target_ftype() is None:
            self.description = {
                "ja": "予測対象、またその項目の種別(数値か、分類か)を指定する必要があります。",
                "en": "You have to define prediction and its type."
            }
        elif not dfe.get_target_ftype() in (FType.categorical, FType.numerical):
            self.description = {
                "ja": "予測対象{}は、数値か、分類かの項目にする必要があります".format(dfe.target),
                "en": "You have to make prediction target as numerical or categorical.".format(dfe.target)
            }
        
        if len(self.description) > 0:
            raise AnalysisStopException(self)

        return True

    def adopt(self, dfe, interpreted=None):
        model_and_params = []
        scoring = "accuracy"

        if dfe.get_target_ftype() == FType.categorical:
            svm = (
                SVC(),
                [
                    {"C": [1, 10, 100], "kernel": ["linear"]},
                    {"C": [1, 10, 100], 'gamma': [0.001, 0.0001], "kernel": ["rbf"]},
                ]
            )
            random_forests = (
                RandomForestClassifier(),
                {
                    "n_estimators": [5, 10, 20],
                    "max_features": ["auto", "sqrt", "log2"]
                }
            )

            model_and_params = [
                random_forests, # svm
            ]
            if self.is_binary_classification(dfe):
                scoring = "f1"
            else:
                scoring = "f1_micro"

        elif dfe.get_target_ftype() == FType.numerical:
            elastic = (
                ElasticNet(),
                {
                    "alpha": [0.1, 1, 2],
                    "l1_ratio": [0.2, 0.5, 0.8]
                }
            )
            svr = (
                SVR(),
                [
                    {"C": [1, 10, 100], "kernel": ["linear"]}
                ]
            )

            random_forests = (
                RandomForestRegressor(),
                {
                    "n_estimators": [5, 10, 20],
                    "max_features": ["auto", "sqrt", "log2"]
                }                
            )
            model_and_params = [
                random_forests
            ]
            scoring = "r2"
        else:
            raise Exception("Target type is None or un-predictable type.")
    
        train, test = train_test_split(dfe.df, test_size=self.test_size)

        train_y = train[dfe.target]
        train_x = train.drop(dfe.target, axis=1)
        best_gv = None
        score = 0
        for m, p in model_and_params:
            gv = GridSearchCV(m, p, scoring=scoring, cv=self.cv_count)
            gv.fit(train_x, train_y)

            if score < gv.best_score_:
                best_gv = gv
                score = gv.best_score_
        
        self.model = best_gv.best_estimator_

        test_y = test[dfe.target]
        test_x = test.drop(dfe.target, axis=1)

        predictions = self.model.predict(test_x)

        if dfe.get_target_ftype() == FType.categorical:
            self.score = accuracy_score(test_y, predictions)
        else:
            self.score = r2_score(test_y, predictions)
        
        self._set_description(dfe)

        return True

    @classmethod
    def is_binary_classification(self, dfe):
        is_binary = False
        if dfe.get_target_ftype() == FType.categorical:
            elements = dfe.get_target().value_counts().index
            if elements.size == 2:
                is_binary = True

        return is_binary

    def _set_description(self, dfe):
        importances = pd.Series(self.model.feature_importances_, index=dfe.get_features().columns).sort_values(ascending=False)
        pic = ImageFile.create()
        with pic.plot() as plt_fig:
            importances.plot.bar()
        
        params = (self.score, self.model.__class__.__name__)
        self.description = {
            "ja": Description("モデルの精度は{:.3f}です(利用モデル:{})。各項目の貢献度は図のようになっています。".format(*params), pic),
            "en": Description("The model accuracy is {:.3f}(model is {}). The contributions of each features are here.".format(*params), pic)
        }

