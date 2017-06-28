import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
from datetime import datetime
import unittest
import numpy as np
import pandas as pd
from karura.core.insights import DatetimeToCategoricalInsight
from karura.core.dataframe_extension import DataFrameExtension, FType


class TestDatetimeToCategoricalInsight(unittest.TestCase):

    def test_adopt(self):
        d = {
            "datetime": [datetime(2010, 1, 1), datetime(2015, 6, 30), datetime(2020, 3, 9)]
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df)

        di = DatetimeToCategoricalInsight()
        ts = di.get_insight_targets(dfe)
        self.assertEqual("datetime", ts[0])

        result = di.adopt(dfe)
        self.assertTrue(result)
        self.assertEqual(len(dfe.df.columns), 2)
        self.assertTrue(dfe.ftypes["datetime_month"], FType.categorical)
        self.assertTrue(dfe.ftypes["datetime_day"], FType.categorical)
        self.assertTrue(dfe.df["datetime_month"].tolist(), [1, 6, 3])
        self.assertTrue(dfe.df["datetime_day"].tolist(), [1, 30, 9])
    
    def test_transform(self):
        d = {
            "datetime": [datetime(2010, 1, 1), datetime(2015, 6, 30), datetime(2020, 3, 9)],
            "datetime2": [datetime(2010, 1, 3), datetime(2015, 6, 15), datetime(2020, 3, 20)]
        }
        df = pd.DataFrame(d)
        dfe = DataFrameExtension(df)
        
        di = DatetimeToCategoricalInsight()
        di.adopt(dfe)

        tf = di.get_transformer(dfe)
        tf.model_features = ["datetime_month", "datetime2_day"]
        transformed = tf.transform(pd.DataFrame(d))
        self.assertEqual(len(transformed.columns), 2)
        self.assertTrue(transformed.columns.tolist, ("datetime_month", "datetime2_day"))
        self.assertTrue(dfe.df["datetime_month"].tolist(), [1, 6, 3])
        self.assertTrue(dfe.df["datetime2_day"].tolist(), [3, 15, 20])


if __name__ == "__main__":
    unittest.main()


