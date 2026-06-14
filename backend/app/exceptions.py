"""Consistent API exception handling."""
import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
logger = logging.getLogger(__name__)

class RecordNotFoundError(Exception):
    """Requested record does not exist."""
class InvalidFilterError(Exception):
    """A filter combination is invalid."""
class DataUnavailableError(Exception):
    """Required source data is unavailable."""

def error(code: str, message: str, status: int, details: object = None) -> JSONResponse:
    """Build the standard error envelope."""
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message, "details": details or {}}})

def register_exception_handlers(app: FastAPI) -> None:
    """Register standard exception handlers."""
    app.add_exception_handler(RecordNotFoundError, lambda _r, e: error("RECORD_NOT_FOUND", str(e), 404))
    app.add_exception_handler(InvalidFilterError, lambda _r, e: error("INVALID_FILTER", str(e), 400))
    app.add_exception_handler(DataUnavailableError, lambda _r, e: error("DATA_UNAVAILABLE", str(e), 503))
    app.add_exception_handler(RequestValidationError, lambda _r, e: error("VALIDATION_ERROR", "Request validation failed.", 422, e.errors()))
    async def unhandled(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled API error", exc_info=exc)
        return error("INTERNAL_ERROR", "An unexpected error occurred.", 500)
    app.add_exception_handler(Exception, unhandled)
