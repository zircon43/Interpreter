

class ParseError(Exception):
    pass

class LoxRuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token
        self.message = message

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
