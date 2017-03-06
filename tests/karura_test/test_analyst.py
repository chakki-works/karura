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
from karura.default_analyst import make_analyst
import karura.core.insights as I


class TestAnalyst(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../data/titanic_train.csv")

    def xtest_analyst(self):
        df = pd.read_csv(self.FILE_NAME)
        analyst = make_analyst(df)
        """
        analyst.dfe.target = "Survived"
        analyst.dfe.to_unique("PassengerId")
        analyst.dfe.df.drop("Cabin", axis=1, inplace=True)
        analyst.dfe.df.drop("Ticket", axis=1, inplace=True)
        analyst.dfe.df.drop("Name", axis=1, inplace=True)
        """
        
        while not analyst.has_done():
            d = analyst.step()
            if not d:
                continue

            if analyst.have_to_ask():
                print(d)
                if isinstance(analyst._insight, I.TargetConfirmInsight):
                    reply = "Survived"
                    print(">{}".format(reply))
                    analyst.get_reply(reply)
                elif isinstance(analyst._insight, I.ColumnIgnoranceInsight):
                    reply = "PassengerId, Ticket, Name"
                    print(">{}".format(reply))
                    analyst.get_reply(reply)
                elif isinstance(analyst._insight, I.NAFrequencyCheckInsight):
                    reply = True
                    print(">{}".format(reply))
                    analyst.get_reply(reply)
                elif isinstance(analyst._insight, I.CategoricalItemInsight):
                    reply = "+ Cabin"
                    print(">{}".format(reply))
                    analyst.get_reply(reply)
                else:
                    print("xxxx")
                    reply = True
                    print(">{}".format(reply))
                    analyst.get_reply(reply)
            else:
                print(d)

        if analyst.get_model_insight():
            m = analyst.get_model_insight()
            print("Accuracy is {}".format(m.score))

    def test_model_describe(self):
        X, y = make_classification(n_samples=1000, n_features=10, n_informative=3, n_classes=3, random_state=0)

        df = pd.DataFrame(np.hstack((y.reshape(-1, 1), X)), columns=["y"]+["f_" + str(i) for i in range(X.shape[1])])
        analyst = Analyst(df, [I.ModelSelectionInsight()])
        analyst.dfe.target = "y"
        analyst.dfe.to_categorical("y")
        d = analyst.step()
        print(d)
        analyst.step()
        self.assertTrue(analyst.has_done())
        d = analyst.interpret()
        self.assertTrue(d)
        print(d)


if __name__ == "__main__":
    unittest.main()
