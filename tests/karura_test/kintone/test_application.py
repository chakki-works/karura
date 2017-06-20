import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import unittest
import numpy as np
import pandas as pd
from karura.core.kintone.application import Application


class TestkintoneApplication(unittest.TestCase):
    APP_ID = 333  # it depends on environment
    APP_NAME = "物件管理"

    def test_get_fields(self):
        app = Application()
        f = app.get_fields(self.APP_ID)
        self.assertTrue(f)
        print(f)

    def test_get_data(self):
        app = Application()
        dfe = app.load(self.APP_ID)
        self.assertTrue(dfe)
        print(dfe.df.columns)
        print(dfe.ftypes)
    
    def test_get_app_id(self):
        app = Application()
        app_id = app.get_app_id(self.APP_NAME)
        print(app_id)


if __name__ == "__main__":
    unittest.main()
