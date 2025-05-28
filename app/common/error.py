

class BaseError(Exception):
    def __init__(self, message: str, code=None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.message}{', err_code=' + str(self.code) if self.code else ''}"


class SysError(BaseError):
    pass


class TaskError(BaseError):
    pass


class InitError(BaseError):
    pass


class DbDaoError(BaseError):
    pass


class JsonLoadsError(BaseError):
    pass


class JsonDumpsError(BaseError):
    pass



