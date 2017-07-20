if __name__ == "__main__":
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    key = key.decode("utf-8")
    print(key)
