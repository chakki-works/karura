# -*- coding: utf-8 -*-
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import RFECV
import numpy as np
from karura.core.insight import Insight
from karura.core.insights.model_selection_insight import ModelSelectionInsight
from karura.core.dataframe_extension import FType


class FeatureSelectionInsight(ModelSelectionInsight):

    def __init__(self):
        super().__init__()
        self.index.as_feature_selection()
    
    def adopt(self, dfe, interpreted=None):
        models = []
        # about scoring, please see following document
        # http://scikit-learn.org/stable/modules/model_evaluation.html#common-cases-predefined-values
        scoring = "accuracy"

        # todo: now, text and datetime colum is ignored
        for t in (FType.text, FType.datetime):
            columns = dfe.get_columns(t, include_target=False)
            dfe.df.drop(columns, inplace=True, axis=1)
            dfe.sync()

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
            # About the model to select the feature, please refer
            # http://scikit-learn.org/stable/modules/feature_selection.html
            models = [Lasso(alpha=.1), RandomForestRegressor()]
            scoring = "r2"
        else:
            raise Exception("Target type is None or un-predictable type.")
        
        features = dfe.get_features()
        target = dfe.get_target()
        best_rfecv = None
        feature_masks = []
        for m in models:
            rfecv = RFECV(estimator=m, step=1, cv=self.cv_count, scoring=scoring, n_jobs=self.n_jobs)
            rfecv.fit(features, target)
            feature_masks.append(rfecv.support_)
        
        selected_mask = []
        if len(feature_masks) < 2:
            selected_mask = feature_masks[0]
        else:
            selected_mask = np.logical_and(*feature_masks)  # take the feature that some models take

        eliminates = features.columns[np.logical_not(selected_mask)]
        dfe.df.drop(eliminates, inplace=True, axis=1)
        dfe.sync()

        selected = features.columns[selected_mask].tolist()

        ss = self.a2t(selected)
        self.description = {
                "ja": "項目{}は予測に有効な項目です。これらを利用し、モデルを構築します。".format(ss),
                "en": "Columns {} are useful to predict. I'll use these to make model.".format(ss)
            }
        return True
