import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insights.row_count_insight import RowCountInsight


class TestRowCountInsight(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../../data/titanic_train.csv")

    def test_insight(self):
        df = pd.read_csv(self.FILE_NAME)
        dfe = DataFrameExtension(df)
        insight = RowCountInsight(max_count=50)

        self.assertTrue(insight.is_applicable(dfe))
        self.assertTrue(insight.describe())

        insight.adopt(dfe)
        self.assertEqual(dfe.df.shape[0], insight.max_count)
        print(dfe.df.head(5))


if __name__ == "__main__":
    unittest.main()


