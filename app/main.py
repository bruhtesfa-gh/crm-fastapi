from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.exception_handlers import (http_exception_handler,
                                    request_validation_exception_handler,
                                    unhandled_exception_handler)
from app.middleware import log_request_middleware
from app.util.setting import get_settings

settings = get_settings()


def create_application() -> FastAPI:
    """
    Create the FastAPI application
    """
    # create the FastAPI application
    application = FastAPI(
        title="Async CRM Backend",
        root_path="",
        openapi_url="/openapi.json",
        swagger_ui_parameters={"docExpansion": "none"},
    )
    #
    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.middleware("http")(log_request_middleware)
    application.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)

    return application


app: FastAPI = create_application()


@app.get("/")
async def health_check():
    """
    Root path
    """
    return {
        "message": "Hello from Async CRM Backend!",
    }
