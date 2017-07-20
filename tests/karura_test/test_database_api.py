import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
import unittest
from karura.database_api import DatabaseAPI


class TestDatabaseAPI(unittest.TestCase):
    DBNAME = "test_database_uri"
    API = None

    @classmethod
    def setUpClass(cls):
        cls.API = DatabaseAPI(alternative_db=cls.DBNAME)
        cls.API.connect()

    @classmethod
    def tearDownClass(cls):
        if cls.API is not None:
            cls.API.close(with_drop=True)

    def test_database(self):
        self.assertEqual(self.API._get_database().name, self.DBNAME)

    def test_user(self):
        domain = "karura31"
        user = "karura99"
        password = "karura@1010"
        gen_new = lambda: password + "__new_password"

        self.assertRaises(Exception, lambda: self.API.register_user("", "", ""))
        self.assertRaises(Exception, lambda: self.API.register_user("domain", "", ""))
        self.assertRaises(Exception, lambda: self.API.register_user("domain", "user", ""))
        self.assertRaises(Exception, lambda: self.API.register_user("domain", "", "password"))
        self.assertRaises(Exception, lambda: self.API.register_user("", "user", ""))
        self.assertRaises(Exception, lambda: self.API.register_user("", "user", "password"))
        self.assertRaises(Exception, lambda: self.API.register_user("domain", "user", "pas"))
        self.assertRaises(Exception, lambda: self.API.register_user("domain", "usr", "password"))
        self.assertRaises(Exception, lambda: self.API.register_user("domain", "usr", "pas"))

        user_obj = self.API.register_user(domain, user, password)
        self.assertTrue(user_obj)
        login = self.API.authenticate_user(domain, user, password)
        self.assertTrue(login)
        self.API.change_user_password(domain, user, password, gen_new())
        login = self.API.authenticate_user(domain, user, gen_new())
        self.assertTrue(login)
        self.API.delete_user(domain, user, gen_new())
        

if __name__ == "__main__":
    unittest.main()
