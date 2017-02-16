# -*- coding: utf-8 -*-
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


class ModelSelectionInsight(Insight):

    def __init__(self, test_size=0.2):
        super().__init__()
        self.min_count = 50  # by scikit-learn choosing model map
        self.test_size = test_size
        self.cv_count = 3
        self.index.as_model_selection()
        self.model = None
        self.score = 0
    
    def is_applicable(self, dfe):
        if dfe.df.shape[0] < self.min_count:
            self.description = {
                "ja": "データが少なすぎます。モデルを作成するには、最低{}件データを集めてください".format(self.min_count),
                "en": "Your data is too small. You have to collect the data at least {} count of data.".format(self.min_count)
            }
            return False
        elif dfe.shape[0] < dfe.shape[1]:
            self.description = {
                "ja": "項目の数に対して、データが少なすぎます。せめて項目の数以上にはデータを集める必要があります。",
                "en": "Your data is too small. You have to collect the data greather than number of columns."
            }
            return False            
        elif dfe.get_target_ftype() is None:
            self.description = {
                "ja": "予測対象、またその項目の種別(数値か、分類か)を指定する必要があります。",
                "en": "You have to define prediction and its type."
            }
            return False
        elif not dfe.get_target_ftype() in (FType.categorical, FType.numerical):
            self.description = {
                "ja": "予測対象{}は、数値か、分類かの項目にする必要があります".format(dfe.target),
                "en": "You have to make prediction target as numerical or categorical.".format(dfe.target)
            }
            return False
        else:
            return True

    def adopt(self, dfe):
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
                random_forests, svm
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
            model_and_params = [
                elastic, svr
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
        
    @classmethod
    def is_binary_classification(self, dfe):
        is_binary = False
        if dfe.get_target_ftype() == FType.categorical:
            elements = dfe.get_target().value_counts().index
            if elements.size == 2:
                is_binary = True

        return is_binary
