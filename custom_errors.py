class CustomizedError(Exception):
    def __init__(self, message):
        self.message = message


class NoneFloatError(Exception):
    def __init__(self, message):
        self.message = message
