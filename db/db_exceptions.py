from sqlalchemy.exc import SQLAlchemyError


class DBException(SQLAlchemyError):
    """Base class for handling any SQLAlchemy-related errors."""

    def __init__(self, *, message: str):
        super().__init__(message)
