import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.datasets import make_regression
from karura.core.insights.feature_selection_insight import FeatureSelectionInsight
from karura.core.dataframe_extension import DataFrameExtension


class TestFeatureSelectionInsight(unittest.TestCase):

    def test_insight_classification(self):
        candidates = 3
        X, y = make_classification(
            n_samples=1000, n_features=25, n_informative=candidates,
            n_redundant=2, n_repeated=0, n_classes=5,
            n_clusters_per_class=1, random_state=0)
        
        df = pd.DataFrame(np.hstack((X, y.reshape([-1, 1]))), columns=["c_{}".format(i) for i in range(X.shape[1])] + ["target"])
        dfe = DataFrameExtension(df, categoricals=["target"], target="target")

        insight = FeatureSelectionInsight()
        insight.adopt(dfe)

        print("selected classifier features {}".format(dfe.ftypes.keys()))
        self.assertTrue(candidates <= len(dfe.ftypes) - 1 < candidates * 2)  # -1 is target ftype
    
    def test_insight_regression(self):
        candidates = 4
        X, y = make_regression(
            n_samples=1000, n_features=15, n_informative=candidates,
            n_targets=1)
        
        df = pd.DataFrame(np.hstack((X, y.reshape([-1, 1]))), columns=["c_{}".format(i) for i in range(X.shape[1])] + ["target"])
        dfe = DataFrameExtension(df, numericals=["target"], target="target")

        insight = FeatureSelectionInsight()
        insight.adopt(dfe)

        print("selected regressor features {}".format(dfe.ftypes.keys()))
        self.assertTrue(candidates <= len(dfe.ftypes) - 1 < candidates * 2)  # -1 is target ftype


if __name__ == "__main__":
    unittest.main()


