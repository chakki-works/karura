import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import unittest
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension


class TestDataFrameExtension(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../data/ftypes_data.csv")

    def test_inference(self):
        df = self.make_data_frame()
        print(df.dtypes)
        dfe = DataFrameExtension(df)
        print(dfe.ftypes)

    def make_data_frame(self):
        return pd.read_csv(self.FILE_NAME)


if __name__ == "__main__":
    unittest.main()


