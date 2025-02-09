class BaseException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class TOTPException(BaseException):
    def __init__(self, message: str = "TOTP Exception"):
        super().__init__(message)

class TOTPCodeException(TOTPException):
    def __init__(self, message = "TOTP Code Exception"):
        super().__init__(message)

class TOTPSecretException(TOTPException):
    def __init__(self, message = "TOTP Secret Exception"):
        super().__init__(message)

class DatabaseException(BaseException):
    def __init__(self, message: str = "Database Exception"):
        super().__init__(message)