import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insights.na_frequency_insight import NAFrequencyCheckInsight


class TestNAFrequencyInsight(unittest.TestCase):

    def test_insight(self):
        d = {
            "category": pd.Series(["a", "b", "c", "b", "c", "a", "a", "b"]),
            "with_50_na": pd.Series(["a", None, "c", None, None, None, "a", "b"]),
            "with_20_na": pd.Series(["a", "b", "c", "b", None, "a", None, "b"])
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df)

        insight = NAFrequencyCheckInsight()
        self.assertTrue(insight.is_applicable(dfe))
        insight.init_description()

        insight.adopt(dfe)
        self.assertEqual(len(dfe.df.columns), 2)


if __name__ == "__main__":
    unittest.main()


