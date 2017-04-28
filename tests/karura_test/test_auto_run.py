import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import unittest
import pandas as pd
from karura.default_config import make_autorun
import karura.core.insights as I


class TestAutoRun(unittest.TestCase):
    FILE_NAME = os.path.join(os.path.dirname(__file__), "../data/titanic_train.csv")

    def test_analyst(self):
        df = pd.read_csv(self.FILE_NAME)
        autorun = make_autorun(df)
        autorun.dfe.target = "Survived"
        autorun.dfe.drop("PassengerId")
        autorun.dfe.drop("Ticket")
        autorun.dfe.drop("Name")
        
        descriptions = autorun.execute()
        for d in descriptions:
            print(d)
        
        result = autorun.result()
        print(result.describe().picture.path)


if __name__ == "__main__":
    unittest.main()
