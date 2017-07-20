import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import json
import unittest
from karura.core.kintone.application import Application
from karura.core.kintone.kintone_request import kintoneRequest
from karura.default_config import make_analyst, make_autorun
import karura.core.insights as I


class TestOnKintone(unittest.TestCase):
    APP_ID = 333  # it depends on environment

    def test_analyst(self):
        print("Analyst --------------")
        app = Application()
        dfe = app.load(self.APP_ID)
        analyst = make_analyst(dfe, feature_type_estimation=False)
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

    def test_autorun(self):
        print("AutoRun --------------")
        app = Application()
        dfe = app.load(self.APP_ID)
        dfe.target = "家賃"
        dfe.drop("物件名")
        dfe.drop("担当者")
        autorun = make_autorun(dfe, feature_type_estimation=False)

        descriptions = autorun.execute()
        for d in descriptions:
            print(d)

    def test_autorun_from_request(self):
        print("AutoRun from Request --------------")
        request = json.loads(KINTONE_REQUEST.replace("###", str(self.APP_ID)))
        krequest = kintoneRequest()
        dfe = krequest.request_to_dfe(request)
        dfe.to_categorical(["向き"])
        autorun = make_autorun(dfe, feature_type_estimation=False)
        descriptions = autorun.execute()
        for d in descriptions:
            print(d)


        print("Predict from kintone Request --------------")
        record = json.loads(KINTONE_RECORD.replace("###", str(self.APP_ID)))
        df = krequest.record_to_df(record)
        predictor = autorun.to_predictor()
        pred = predictor.predict(df)
        print("estimated value: {}".format(pred))
        

KINTONE_REQUEST = """
{"app_id":"###","fields":{"house_price":{"usage":1},"name":{"usage":-1},"direction":{"usage":0},"area_value":{"usage":0},"years_old_value":{"usage":0},"walk_time_value":{"usage":0},"stairs_value":{"usage":0}},
"view": "分析用一覧"}
"""

KINTONE_RECORD = """
{"app_id":"###","values":{"direction":"SW","area_value":"21.56","years_old_value":"23","walk_time_value":"8","stairs_value":"4"}}
"""


if __name__ == "__main__":
    unittest.main()
