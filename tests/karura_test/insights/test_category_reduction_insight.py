import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import numpy as np
import pandas as pd
from karura.core.insights import CategoryReductionInsight
from karura.core.dataframe_extension import DataFrameExtension


class TestCategoryReductionInsight(unittest.TestCase):

    def test_category_insight(self):
        d = {
            "have_peak": np.floor(np.random.normal(loc=0.5, scale=0.3, size=100) * 10) + 1,
            "random": np.floor(np.random.uniform(size=100) * 10) + 1,
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df, categoricals=list(d.keys()))

        ci = CategoryReductionInsight()
        ts = ci.get_insight_targets(dfe)
        self.assertEqual("have_peak", ts[0])

        result = ci.adopt(dfe)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()


