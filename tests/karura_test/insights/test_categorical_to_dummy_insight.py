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

    def test_get_transformer(self):
        d = {
            "category1": ["a", "b", "c", "d"],
            "category2": [1, 2, 3, 4] 
        }
        df = pd.DataFrame.from_dict(d)
        dfe = DataFrameExtension(df, categoricals=("category1", "category2"))
        insight = CategoricalToDummyInsight()
        insight.adopt(dfe)

        self.assertEqual(8, len(dfe.ftypes))  # expand to dummy

        dfe.df.drop(["category1_a", "category2_3"], axis=1, inplace=True)  # drop 2 column (like useless feature)

        transformer = insight.get_transformer(dfe)
        df_t = transformer.transform(pd.DataFrame.from_dict(d))
        print(df_t.head())
        self.assertEqual(6, len(df_t.columns))
        for c in ["category1_b", "category1_c", "category1_d"]:
            self.assertTrue(c in df_t.columns)
            self.assertEqual(1, len(df_t[df_t[c] == 1]))
        for c in ["category2_1", "category2_2", "category2_4"]:
            self.assertTrue(c in df_t.columns)
            self.assertEqual(1, len(df_t[df_t[c] == 1]))


if __name__ == "__main__":
    unittest.main()


