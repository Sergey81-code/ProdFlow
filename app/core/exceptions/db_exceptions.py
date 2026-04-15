from typing import Protocol, Type


class DBExceptionProtocol(Protocol):
    def __init__(self, *, message: str) -> None: ...


class DbExceptions:
    _exc_class: Type[DBExceptionProtocol] | None = None

    def __new__(cls, *args, **kwargs):
        raise TypeError("DbExceptions cannot be instantiated")

    @classmethod
    def configure(cls, exc_class: Type[DBExceptionProtocol]) -> None:
        cls._exc_class = exc_class

    @classmethod
    def exc_class(cls) -> Type[DBExceptionProtocol]:
        if cls._exc_class is None:
            raise RuntimeError("DbExceptions is not configured")

        return cls._exc_class

    @classmethod
    def not_found(cls, message: str) -> None:
        """Raise exception for record not found"""
        raise cls.exc_class()(message=message)

    @classmethod
    def integrity_error(cls, message: str) -> None:
        """Raise exception for DB integrity issues"""
        raise cls.exc_class()(message=message)

    @classmethod
    def connection_error(cls, message: str) -> None:
        """Raise exception for DB connection errors"""
        raise cls.exc_class()(message=message)
