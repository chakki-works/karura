import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import math
import unittest
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.analyst import Analyst
import karura.core.insights as I


class TestAnalysisFlow(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../data/titanic_train.csv")

    def test_flow(self):
        df = pd.read_csv(self.FILE_NAME)
        c_insight = I.CategoricalItemInsight()
        analyst = Analyst(df, [c_insight])
        analyst.check_columns()
        if analyst.has_insight():
            print(analyst.describe_insight())
            analyst.resolve(True)


if __name__ == "__main__":
    unittest.main()


