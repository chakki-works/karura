import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import math
import unittest
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from karura.core.dataframe_extension import DataFrameExtension
from karura.core.analyst import Analyst
from karura.core.kintone.application import Application
from karura.default_config import make_analyst
import karura.core.insights as I


class TestAnalystKintone(unittest.TestCase):
    APP_ID = 69  # it depends on environment

    def test_analyst_kintone(self):
        app = Application()
        dfe = app.load(self.APP_ID)
        analyst = make_analyst(dfe)
        while not analyst.has_done():
            d = analyst.step()
            if not d:
                continue
            if analyst.have_to_ask():
                print(d)
                if isinstance(analyst._insight, I.CategoricalItemInsight):
                    reply = "向き"
                    print(">{}".format(reply))
                    analyst.get_reply(reply)
                elif isinstance(analyst._insight, I.TargetConfirmInsight):
                    reply = "家賃"
                    print(">{}".format(reply))
                    analyst.get_reply(reply)
                elif isinstance(analyst._insight, I.ColumnIgnoranceInsight):
                    reply = "物件名, 担当者"
                    print(">{}".format(reply))
                    analyst.get_reply(reply)
                else:
                    reply = True
                    print(">{}".format(reply))
                    analyst.get_reply(reply)

            else:
                print(d)

        m = analyst.interpret()
        print(m)


if __name__ == "__main__":
    unittest.main()
