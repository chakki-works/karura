import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import unittest
import karura.env as env


class TestEnv(unittest.TestCase):

    def test_slack_token(self):
        token = env.get_slack_token()
        self.assertTrue(token)

    def test_lang(self):
        lang = env.get_lang()
        self.assertTrue(lang)


if __name__ == "__main__":
    unittest.main()


