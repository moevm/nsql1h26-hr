from http import HTTPStatus


class AppError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        self.code = HTTPStatus(status_code).name
