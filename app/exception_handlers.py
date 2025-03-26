import sys
from typing import Union

from fastapi import Request
from fastapi.exception_handlers import http_exception_handler as _http_exception_handler
from fastapi.exception_handlers import (
    request_validation_exception_handler as _request_validation_exception_handler,
)
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from pydantic import ValidationError

from app.logger import logger
from app.util.setting import get_settings

settings = get_settings()


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    This is a wrapper to the default RequestValidationException handler of FastAPI.
    This function will be called when client input is not valid.
    """
    logger.debug("Our custom request_validation_exception_handler was called")
    body = await request.body()
    query_params = request.query_params._dict  # pylint: disable=protected-access
    detail = {
        "errors": exc.errors(),
        "body": body.decode(),
        "query_params": query_params,
    }
    logger.info(detail)
    return await _request_validation_exception_handler(request, exc)


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> Union[JSONResponse, Response]:
    """
    This is a wrapper to the default HTTPException handler of FastAPI.
    This function will be called when a HTTPException is explicitly raised.
    """
    logger.debug("Our custom http_exception_handler was called")
    return await _http_exception_handler(request, exc)


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> PlainTextResponse:
    """
    This middleware will log all unhandled exceptions.
    Unhandled exceptions are all exceptions that are not HTTPExceptions or RequestValidationErrors.
    """
    logger.debug("Our custom unhandled_exception_handler was called")
    getattr(getattr(request, "client", None), "host", None)
    getattr(getattr(request, "client", None), "port", None)
    (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )

    # Fetch exception info
    exception_value = sys.exc_info()

    # Handle ExceptionGroup and ValidationErrors specifically
    if isinstance(exc, ExceptionGroup):
        logger.error("ExceptionGroup detected. Details:")
        for idx, e in enumerate(exc.exceptions):
            logger.error(f"Sub-exception {idx + 1}: {e}")
            if isinstance(e, ValidationError):
                logger.error(f"Validation Error in model: {e.model.__name__}")
                for error in e.errors():
                    logger.error(
                        f"Field: {error['loc']}, Message: {error['msg']}, Type: {error['type']}"
                    )
    if isinstance(exc, ValidationError):
        logger.error("ValidationError detected. Details:")
        for error in exc.errors():
            logger.error(
                f"Field: {error['loc']}, Message: {error['msg']}, Type: {error['type']}"
            )

    return PlainTextResponse(str(exception_value), status_code=500)
