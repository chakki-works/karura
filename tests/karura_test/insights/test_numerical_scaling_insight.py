import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import shutil
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insights.numerical_scaling_insight import NumericalScalingInsight


class TestNumericalScalingInsight(unittest.TestCase):
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../data/model")
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../../data/ftypes_data.csv")

    def test_insight_targets(self):
        dfe = DataFrameExtension.read_csv(self.FILE_NAME)
        insight = NumericalScalingInsight()

        targets = insight.get_insight_targets(dfe)
        print(targets)
        self.assertTrue(len(targets) > 0)

    def test_adopt(self):
        dfe = DataFrameExtension.read_csv(self.FILE_NAME)
        insight = NumericalScalingInsight()

        targets = insight.get_insight_targets(dfe)

        insight.adopt(dfe)
        if not os.path.exists(self.MODEL_PATH):
            os.mkdir(self.MODEL_PATH)
        insight.save(self.MODEL_PATH)
        scaled1 = dfe.df[targets]

        loaded_insight = NumericalScalingInsight(load_path=self.MODEL_PATH)
        dfe2 = DataFrameExtension.read_csv(self.FILE_NAME)
        loaded_insight.adopt(dfe2)
        scaled2 = dfe2.df[targets]

        for c in scaled1.columns:
            self.assertEqual(0, (scaled1[c] != scaled2[c]).sum())
        
        shutil.rmtree(self.MODEL_PATH)


if __name__ == "__main__":
    unittest.main()


