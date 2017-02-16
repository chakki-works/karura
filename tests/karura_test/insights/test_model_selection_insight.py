import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.datasets import make_regression
from karura.core.insights.model_selection_insight import ModelSelectionInsight
from karura.core.dataframe_extension import DataFrameExtension


class TestModelSelectionInsight(unittest.TestCase):

    def test_insight_classification(self):
        X, y = make_classification(n_samples=1000, n_features=7, n_informative=4, n_classes=3)

        df = pd.DataFrame(np.hstack((X, y.reshape([-1, 1]))), columns=["c_{}".format(i) for i in range(X.shape[1])] + ["target"])
        dfe = DataFrameExtension(df, categoricals=["target"], target="target")

        insight = ModelSelectionInsight()
        insight.adopt(dfe)

        self.assertTrue(insight.score > 0)
        print(insight.score)
    
    def test_insight_regression(self):
        candidates = 4
        X, y = make_regression(
            n_samples=1000, n_features=15, n_informative=candidates,
            n_targets=1)
        
        df = pd.DataFrame(np.hstack((X, y.reshape([-1, 1]))), columns=["c_{}".format(i) for i in range(X.shape[1])] + ["target"])
        dfe = DataFrameExtension(df, numericals=["target"], target="target")

        insight = ModelSelectionInsight()
        insight.adopt(dfe)

        self.assertTrue(insight.score > 0)
        print(insight.score)


if __name__ == "__main__":
    unittest.main()


