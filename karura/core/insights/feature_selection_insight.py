# -*- coding: utf-8 -*-
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFECV
import numpy as np
from karura.core.insight import Insight
from karura.core.insights.model_selection_insight import ModelSelectionInsight
from karura.core.dataframe_extension import FType


class FeatureSelectionInsight(ModelSelectionInsight):

    def __init__(self):
        super().__init__()
        self.cv_count = 3
        self.index.as_feature_selection()
    
    def adopt(self, dfe, interpreted=None):
        models = []
        # about scoring, please see following document
        # http://scikit-learn.org/stable/modules/model_evaluation.html#common-cases-predefined-values
        scoring = "accuracy"

        if dfe.get_target_ftype() == FType.categorical:
            #models = [RandomForestClassifier(), SVC(kernel="linear")]
            models = [RandomForestClassifier()]
            if self.is_binary_classification(dfe):
                scoring = "f1"
            else:
                # see reference about f1 score
                # http://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html#sklearn.metrics.f1_score
                scoring = "f1_micro"  # if prediction does not occur to some label, macro is too worse to evaluate
        elif dfe.get_target_ftype() == FType.numerical:
            models = [ElasticNet(), RandomForestRegressor()]
            scoring = "r2"
        else:
            raise Exception("Target type is None or un-predictable type.")
        
        features = dfe.get_features()
        target = dfe.get_target()
        best_rfecv = None
        feature_masks = []
        for m in models:
            rfecv = RFECV(estimator=m, step=1, cv=self.cv_count, scoring=scoring)
            rfecv.fit(features, target)
            
            feature_masks.append(rfecv.support_)
        
        if len(feature_masks) < 2:
            eliminates = np.logical_not(feature_masks[0])
        else:
            eliminates = np.logical_not(np.logical_or(*feature_masks))
        eliminated = features.columns[eliminates]
        dfe.df.drop(eliminated, inplace=True, axis=1)
        dfe.sync()

        self.description = {
                "ja": "項目{}は、予測に有効でないため削除しました。".format(eliminated),
                "en": "Columns {} are eliminated because they are not useful for prediction.".format(eliminated)
            }
        return True
