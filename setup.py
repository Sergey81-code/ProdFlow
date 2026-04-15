from fastapi import HTTPException

from app.core.exceptions.api_exceptions import ApiExceptions
from app.core.exceptions.db_exceptions import DbExceptions


from db.db_exceptions import DBException as DBExceptionFromDbModule


def configure_exceptions() -> None:
    # configure API-level exceptions
    ApiExceptions.configure(HTTPException)

    # configure DB-level exceptions
    DbExceptions.configure(DBExceptionFromDbModule)
