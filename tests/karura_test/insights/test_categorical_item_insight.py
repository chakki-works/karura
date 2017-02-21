import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import pandas as pd
from karura.core.insights import CategoricalItemInsight
from karura.core.dataframe_extension import DataFrameExtension


class TestCategoricalItemInsight(unittest.TestCase):

    def test_category_insight(self):
        d = {
            "category": pd.Series(["a", "b", "c", "b", "c", "a", "a", "b"]),
            "numerical": pd.Series([1.0, 2.0, 2.1, 3.1, 1, 2.1, 3.1, 4]),
            "ids": pd.Series([1, 2, 3, 2, 1, 2, 2, 1]),
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df)

        ci = CategoricalItemInsight()
        ts = ci.get_insight_targets(dfe)

        self.assertEqual(2, len(ts))

        ci.adopt(dfe)
        categoricals = dfe.df.dtypes[dfe.df.dtypes == "category"]
        self.assertEqual(2, categoricals.size)
    
    def test_interpret(self):
        ci = CategoricalItemInsight()

        self.assertTrue(ci.interpret(True))
        self.assertFalse(ci.interpret(False))
        self.assertEqual(ci.interpret("+ hoge,haga")[0], (True, ["hoge", "haga"]))
        self.assertEqual(ci.interpret("- hoge,haga")[0], (False, ["hoge", "haga"]))
        self.assertEqual(ci.interpret("- hoge,haga, + fuga, fufu")[0], (False, ["hoge", "haga"]))
        self.assertEqual(ci.interpret("- hoge,haga, + fuga, fufu")[1], (True, ["fuga", "fufu"]))

    def test_interpret_insight(self):
        d = {
            "category": pd.Series(["a", "b", "c", "b", "c", "a", "a", "b"]),
            "strs": pd.Series(["x", "z", "w", "v", "o", "q", "z", "y"]),
            "ids": pd.Series([1, 2, 5, 7, 8, 9, 3, 1]),
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df)

        ci = CategoricalItemInsight()
        ts = ci.get_insight_targets(dfe)
        self.assertEqual(1, len(ts))

        interpreted = ci.interpret("+ strs, ids, - category")
        ci.adopt(dfe, interpreted)
        categoricals = dfe.df.dtypes[dfe.df.dtypes == "category"]
        self.assertEqual(2, categoricals.size)

if __name__ == "__main__":
    unittest.main()


