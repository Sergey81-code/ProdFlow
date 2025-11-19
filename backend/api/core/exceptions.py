from fastapi import HTTPException


class AppExceptions:

    @staticmethod
    def _raise_exception(status_code: int, message: str):
        raise HTTPException(status_code=status_code, detail=message)

    @classmethod
    def bad_request_exception(cls, message: str):
        """Raise HTTPException with status_code 400 and message"""
        cls._raise_exception(400, message)

    @classmethod
    def unauthorized_exception(cls, message: str):
        """Raise HTTPException with status_code 401 and message"""
        cls._raise_exception(401, message)

    @classmethod
    def forbidden_exception(cls, message: str = "Forbidden."):
        """Raise HTTPException with status_code 403 and message"""
        cls._raise_exception(403, message)

    @classmethod
    def not_found_exception(cls, message: str):
        """Raise HTTPException with status_code 404 and message"""
        cls._raise_exception(404, message)

    @classmethod
    def validation_exception(cls, message: str):
        """Raise HTTPException with status_code 422 and message"""
        cls._raise_exception(422, message)

    @classmethod
    def service_unavailable_exception(cls, message: str):
        """Raise HTTPException with status_code 503 and message"""
        cls._raise_exception(503, message)
