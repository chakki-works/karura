import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
from datetime import datetime
import unittest
import numpy as np
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insights import LabelFormatInsight


class TestLabelFormatInsight(unittest.TestCase):

    def test_adopt_categorical(self):
        d = {
            "numerical": [0, 1, 2, 3],
            "categorical": ["a", "b", "c", "a"]
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df, categoricals=("categorical"), target="categorical")

        li = LabelFormatInsight()
        ts = li.get_insight_targets(dfe)
        self.assertEqual("categorical", ts[0])

        result = li.adopt(dfe)
        self.assertTrue(result)
        
        ts = li.get_transformer(dfe)
        inv = ts.inverse_transform(dfe.df["categorical"])
        self.assertEqual(inv.tolist(), d["categorical"])
    
    def test_adopt_numerical(self):
        d = {
            "numerical": [0, 1, 2, 3],
            "categorical": ["a", "b", "c", "a"]
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df, categoricals=("categorical"), target="numerical")

        li = LabelFormatInsight()
        ts = li.get_insight_targets(dfe)
        self.assertEqual("numerical", ts[0])

        result = li.adopt(dfe)
        self.assertTrue(result)
        
        ts = li.get_transformer(dfe)
        inv = ts.inverse_transform(np.array(dfe.df["numerical"]))
        diff = sum(inv.flatten() - np.array(d["numerical"]))
        self.assertTrue(diff < 1e-10)


if __name__ == "__main__":
    unittest.main()


