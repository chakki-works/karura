import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import json
import unittest
import numpy as np
import pandas as pd
from karura.core.dataframe_extension import FType
from karura.core.kintone.kintone_request import kintoneRequest


class TestkintoneRequeset(unittest.TestCase):
    APP_ID = 333  # depends on environment

    def test_request_to_dfe(self):
        request = json.loads(KINTONE_REQUEST.replace("###", str(self.APP_ID)))
        krequest = kintoneRequest()
        dfe = krequest.request_to_dfe(request)
        print(dfe.ftypes)
        print(dfe.df.shape)

    def test_file_to_dfe(self):
        krequest = kintoneRequest()
        dfe = krequest.file_to_df(FILE_STR.strip().encode("utf-8"))

        self.assertEqual(dfe.target, "家賃")
        self.assertEqual(dfe.get_columns(FType.categorical), ["向き"])
        self.assertEqual(dfe.get_columns(FType.numerical), ["築年数(年)", "専有面積(mxm)", "家賃"])


KINTONE_REQUEST = """
{"app_id":"###","fields":{"years_old_value":{"usage":0},"house_price":{"usage":1},"walk_time_value":{"usage":0},"stairs_value":{"usage":0},"person":{"usage":-1},"area_value":{"usage":0},"name":{"usage":-1},"direction":{"usage":0}},"view":"分析用一覧"}
"""

FILE_STR = """
築年数(年)	駅からの徒歩時間(分)	階数	担当者	専有面積(mxm)	家賃(予測)	物件名	向き	家賃	家賃_prediction
NUM				NUM			CAT	NUM/TGT	NUM/PRED
23	8	4	鈴木	21.56	6.145777777777778	メゾン145番地	SW	5.9	6.025666666666667
25	5	4	鈴木	22.83	6.57	メゾン144番地	NE	6.5	6.731666666666667
26	15	4	鈴木	16.94		メゾン143番地	SW	4.2	4.700000000000001
"""


if __name__ == "__main__":
    unittest.main()
