import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import pandas as pd
from karura.core.insights.categorical_to_dummy_insight import CategoricalToDummyInsight
from karura.core.dataframe_extension import DataFrameExtension


class TestCategoricalToDummyInsight(unittest.TestCase):

    def test_insight(self):
        d = {
            "category1": pd.Series(["a", "b", "c", "b", "c", "a", "a", "b"]),
            "category2": pd.Series(["z", "z", "x", "y", "z", "z", "z", "x"]),
            "numericals": pd.Series([1, 2, 3, 2, 1, 2, 2, 1]),
        }
        category_columns = ["category1", "category2"]
        dfe = DataFrameExtension(pd.DataFrame(d), categoricals=category_columns)

        insight = CategoricalToDummyInsight()
        targets = insight.get_insight_targets(dfe)
        self.assertEqual(len(category_columns), len(targets))

        insight.adopt(dfe)
        self.assertEqual("numericals", dfe.df.columns[0])
        for c in category_columns:
            categories = d[c].value_counts().index
            dummy_columns = ["{}_{}".format(c, v) for v in categories]  # default prefix            
            converted = dfe.df.columns[[v.startswith(c) for v in dfe.df.columns]]
            for cv in converted:
                self.assertTrue(cv in dummy_columns)
        
        print(dfe.ftypes)


if __name__ == "__main__":
    unittest.main()


