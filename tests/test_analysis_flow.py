import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
import math
import unittest
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.analyst import Analyst
import karura.core.insights as I


class TestFlow(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../data/titanic_train.csv")

    def test_flow(self):
        df = pd.read_csv(self.FILE_NAME)
        c_insight = I.CategoryInsight()
        analyst = Analyst(df, [c_insight])
        analyst.check_columns()
        if analyst.has_insight():
            print(analyst.describe_insight())
            analyst.resolve(True)

    def test_category_insight(self):
        d = {
            "category": pd.Series(["a", "b", "c", "b", "c", "a", "a", "b"]),
            "numerical": pd.Series([1.0, 2.0, 2.1, 3.1, 1, 2.1, 3.1, 4]),
            "ids": pd.Series([1, 2, 3, 2, 1, 2, 2, 1]),
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df)

        ci = I.CategoryInsight()
        ts = ci.get_insight_targets(dfe)
        print(ts)


if __name__ == "__main__":
    unittest.main()


