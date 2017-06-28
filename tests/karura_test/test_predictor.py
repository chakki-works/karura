import os
import shutil
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import unittest
import pandas as pd
from sklearn.metrics import accuracy_score
from karura.default_config import make_autorun
from karura.core.predictor import Predictor
import karura.core.insights as I


class TestPredictor(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../data/titanic_train.csv")

    def test_classifier_predictor(self):
        df = pd.read_csv(self.FILE_NAME)
        autorun = make_autorun(df)
        autorun.dfe.target = "Survived"
        autorun.dfe.drop("PassengerId")
        autorun.dfe.drop("Ticket")
        autorun.dfe.drop("Name")
        
        descriptions = autorun.execute()
        for d in descriptions:
            print(d)
        
        predictor = autorun.to_predictor()
        path = os.path.dirname(__file__)
        saved_path = predictor.save(path , "test_predictor")

        predictor = Predictor.load(path, "test_predictor")
        shutil.rmtree(saved_path)

        df2 = pd.read_csv(self.FILE_NAME)
        y_true = df2["Survived"]
        pred = predictor.predict(df2)
        score = accuracy_score(y_true, pred)
        print(score)


if __name__ == "__main__":
    unittest.main()
