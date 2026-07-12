"""
Global exception handler. Ensures every error the client sees has a
consistent shape — no leaking stack traces, SQL errors, or internal
details, which would be an information-disclosure vulnerability.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppException

logger = logging.getLogger("transitops")


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {"message": exc.detail}},
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        logger.warning(f"DB integrity error on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=409,
            content={"success": False, "error": {"message": "A conflicting record already exists"}},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": {"message": "Internal server error"}},
        )