class kintoneException(Exception):

    def __init__(self, message):
        super(kintoneException, self).__init__(message)
        self.message = message
