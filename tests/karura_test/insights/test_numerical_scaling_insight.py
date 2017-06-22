import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import shutil
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.insights.numerical_scaling_insight import NumericalScalingInsight


class TestNumericalScalingInsight(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../../data/ftypes_data.csv")

    def test_insight_targets(self):
        dfe = DataFrameExtension.read_csv(self.FILE_NAME)
        insight = NumericalScalingInsight()

        targets = insight.get_insight_targets(dfe)
        self.assertTrue(len(targets) > 0)

    def test_adopt(self):
        dfe = DataFrameExtension.read_csv(self.FILE_NAME)
        insight = NumericalScalingInsight()

        targets = insight.get_insight_targets(dfe)

        scaled = (dfe.df[targets] - dfe.df[targets].mean()) / dfe.df[targets].std()

        insight.adopt(dfe)
        scaled1 = dfe.df[targets]
        self.assertTrue(scaled1.mean().sum() < 1.0e-10)
        self.assertTrue(scaled1.std().mean() - 1 < 0.1)

        dfe2 = DataFrameExtension.read_csv(self.FILE_NAME)
        transformer = insight.get_transformer(dfe2)
        scaled2 = transformer.transform(dfe2.df)
        scaled2 = scaled2[targets]
        self.assertTrue(scaled2.mean().sum() < 1.0e-10)
        self.assertTrue(scaled2.std().mean() -1 < 0.1)

        for c in scaled1.columns:
            self.assertEqual(0, (scaled1[c] != scaled2[c]).sum())


if __name__ == "__main__":
    unittest.main()


