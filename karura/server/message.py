class ErrorMessage():

    @classmethod
    def create(cls, message):
        return {
            "error": message
        }
