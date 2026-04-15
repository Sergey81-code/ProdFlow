from typing import Protocol, Type


class ApiExceptionProtocol(Protocol):
    def __init__(self, *, status_code: int, detail: str) -> None: ...


class ApiExceptions:
    _exc_class: Type[ApiExceptionProtocol] | None = None

    def __new__(cls, *args, **kwargs):
        raise TypeError("ApiExceptions cannot be instantiated")

    @classmethod
    def configure(cls, exc_class: Type[ApiExceptionProtocol]) -> None:
        cls._exc_class = exc_class

    @classmethod
    def _get_exc_class(cls) -> Type[ApiExceptionProtocol]:
        if cls._exc_class is None:
            raise RuntimeError("ApiExceptions is not configured")

        return cls._exc_class

    @classmethod
    def _raise_exception(cls, status_code: int, message: str):
        exc_class = cls._get_exc_class()
        raise exc_class(status_code=status_code, detail=message)

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
