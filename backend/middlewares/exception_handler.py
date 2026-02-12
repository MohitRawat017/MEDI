"""
Exception Handler Middleware: Global error handling for FastAPI
Catches all unhandled exceptions and returns structured error responses
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from logger import setup_logger

logger = setup_logger(__name__)


async def catch_exception_middleware(request: Request, call_next):
    """
    Middleware to catch and handle all unhandled exceptions.

    Args:
        request (Request): Incoming HTTP request
        call_next: Next middleware or route handler

    Returns:
        Response: Either the normal response or error response

    Error response format:
        {
            "error": "Error message"
        }

    Note: All exceptions are logged with full traceback
    """
    try:
        return await call_next(request)
    except Exception as exc:
        logger.exception("UNHANDLED EXCEPTION")
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)}
        )
