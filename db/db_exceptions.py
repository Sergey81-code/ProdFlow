from sqlalchemy.exc import SQLAlchemyError


class DBException(SQLAlchemyError):
    """Base class for handling any SQLAlchemy-related errors."""

    pass
