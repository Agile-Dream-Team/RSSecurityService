from fastapi import HTTPException


class AuthorizationException(HTTPException):
    def __init__(self, detail: str = "Authorization failed"):
        super().__init__(status_code=401, detail=detail)


class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(CustomException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class BadRequestException(CustomException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)
