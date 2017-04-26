import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import json
import unittest
import numpy as np
import pandas as pd
from karura.core.kintone.kintone_request import kintoneRequest


class TestkintoneRequeset(unittest.TestCase):
    APP_ID = 69  # depends on environment

    def test_request_to_dfe(self):
        request = json.loads(KINTONE_REQUEST.replace("###", str(self.APP_ID)))
        krequest = kintoneRequest()
        dfe = krequest.request_to_dfe(request)
        print(dfe.ftypes)
        print(dfe.df.shape)


KINTONE_REQUEST = """
{"app_id":"###","fields":{"数値_3":{"usage":1},"文字列__1行_":{"usage":-1},"ドロップダウン":{"usage":0},"数値_0":{"usage":0},"数値_2":{"usage":0},"数値_1":{"usage":0},"ドロップダウン_0":{"usage":0},"数値":{"usage":0}},
"view": "分析用一覧"}
"""


if __name__ == "__main__":
    unittest.main()
