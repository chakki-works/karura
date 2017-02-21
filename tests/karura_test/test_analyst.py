import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import math
import unittest
import pandas as pd
from karura.core.dataframe_extension import DataFrameExtension
from karura.default_analyst import make_analyst
import karura.core.insights as I


class TestAnalyst(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../data/titanic_train.csv")

    def test_analyst(self):
        df = pd.read_csv(self.FILE_NAME)
        analyst = make_analyst(df)
        """
        analyst.dfe.target = "Survived"
        analyst.dfe.to_unique("PassengerId")
        analyst.dfe.df.drop("Cabin", axis=1, inplace=True)
        analyst.dfe.df.drop("Ticket", axis=1, inplace=True)
        analyst.dfe.df.drop("Name", axis=1, inplace=True)
        """
        
        while not analyst.analyze():
            if len(analyst.get_descriptions()) > 0:
                for d in analyst.get_descriptions():
                    print(d)
            if analyst.has_insight():
                print(analyst.describe_insight())
                if isinstance(analyst._insight, I.TargetConfirmInsight):
                    reply = "Survived"
                    print(">{}".format(reply))
                    analyst.resolve(reply)
                elif isinstance(analyst._insight, I.ColumnIgnoranceInsight):
                    reply = "PassengerId, Cabin, Ticket, Name"
                    print(">{}".format(reply))
                    analyst.resolve(reply)
                else:
                    reply = True
                    print(">{}".format(reply))
                    analyst.resolve(reply)
        
        if analyst.get_model_insight():
            m = analyst.get_model_insight()
            print("Accuracy is {}".format(m.score))

if __name__ == "__main__":
    unittest.main()
