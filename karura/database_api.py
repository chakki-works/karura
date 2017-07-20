from collections import namedtuple
from pymongo import MongoClient
from cryptography.fernet import Fernet
from karura.env import get_database_uri, get_private_key, kintoneEnv


class DatabaseAPI():
    USER_COLLECTION = "karura_user"

    def __init__(self, database_uri="", alternative_db=""):
        self.database_uri = database_uri if database_uri else get_database_uri()
        self._alternative_db = alternative_db
        self._database = None
        self.__client = None
    
    def connect(self):
        self._get_database()

    def _get_database(self):
        if self._database is not None:
            return self._database
        else:
            self.__client = MongoClient(self.database_uri)
            db = self.__client.get_default_database()
            if self._alternative_db:
                db = self.__client[self._alternative_db]
            if not db:
                raise Exception("Cannot connect to the database. Please configure database_uri.")
            self._database = db
            return self._database
    
    def __authentication_parameter_check(self, domain, user, password):
        if not domain:
            raise Exception("domain is not specified in register the user.")
        if not user:
            raise Exception("user is not specified in register the user.")
        if not password:
            raise Exception("user is not specified in register the user.")

        if "@" in user:
            raise Exception("user name with '@' is not allowed")

        # see ref: login security on cybozu
        # https://help.cybozu.com/ja/general/admin/passwordpolicy.html
        if len(user) <= 3:
            raise Exception("user's string length is too short.")
            
        if len(password) <= 3:
            raise Exception("password's string length is too short.")
        elif len(password) > 72:
            raise Exception("password's string length is too long.")  # for bcrypt

        return True

    def __encrypt(self, secret_str):
        key = get_private_key()
        f = Fernet(key)
        encoded = f.encrypt(secret_str.encode("utf-8"))
        return encoded

    def __decrypt(self, encoded_str):
        key = get_private_key()
        f = Fernet(key)
        decoded = f.decrypt(encoded_str)
        return decoded.decode("utf-8")

    def __make_user_key(self, domain, user):
        return user + "@" + domain

    def key_split(self, key):
        user, domain = key.rsplit("@")
        return user, domain

    def register_user(self, domain, user, password):
        self.__authentication_parameter_check(domain, user, password)
        db = self._get_database()
        user_db = db[self.USER_COLLECTION]
        key = self.__make_user_key(domain, user)
        if user_db.find_one({"key": key}) is not None:
            raise Exception("The user already exist.")

        password = self.__encrypt(password)
        result = user_db.insert_one({"key": key, "password": password, "domain": domain})
        if result and result.inserted_id:
            return user_db.find_one({"_id": result.inserted_id})
        else:
            raise Exception("Could not register the user.")

    def authenticate_user(self, domain, user, password):
        self.__authentication_parameter_check(domain, user, password)
        db = self._get_database()
        user_db = db[self.USER_COLLECTION]

        key = self.__make_user_key(domain, user)
        registered = user_db.find_one({"key": key})
        if registered is not None and password == self.__decrypt(registered["password"]):
            return registered
        else:
            raise Exception("Authentication of user failed.")

    def delete_user(self, domain, user, password):
        registered = self.authenticate_user(domain, user, password)
        if not registered:
            raise Exception("Faild to delete the user.")
        else:
            db = self._get_database()
            user_db = db[self.USER_COLLECTION]
            result = user_db.delete_one({"_id": registered["_id"]})
            return result.deleted_count == 1

    def change_user_password(self, domain, user, old_password, new_password):
        self.__authentication_parameter_check(domain, user, old_password)
        self.__authentication_parameter_check(domain, user, new_password)
        if old_password == new_password:
            raise Exception("old_password and new_password is same.")

        registered = self.authenticate_user(domain, user, old_password)
        result = False
        if registered is not None:
            db = self._get_database()
            user_db = db[self.USER_COLLECTION]
            _new_password = self.__encrypt(new_password)
            result = user_db.update_one({"_id": registered["_id"]}, {"$set": {"password": _new_password}})
            result = (result.modified_count == 1)
        if not result:
            raise Exception("Change password is failed")

    def get_kintone_env(self, domain):
        db = self._get_database()
        user_db = db[self.USER_COLLECTION]

        registered = user_db.find_one({"domain": domain})
        if not registered:
            return None
        user, domain = self.key_split(registered["key"])        
        env = kintoneEnv(domain, user, self.__decrypt(registered["password"]))
        return env

    def close(self, with_drop=False):
        if self._database is not None:
            if with_drop:
                self.__client.drop_database(self._database.name)
            self.__client.close()
            self.__database = None
