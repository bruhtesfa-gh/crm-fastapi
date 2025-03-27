from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.deps import verify_access_token
from app.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
    unhandled_exception_handler,
)
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
        RequestValidationError, request_validation_exception_handler  # type: ignore
    )
    application.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
    application.add_exception_handler(Exception, unhandled_exception_handler)

    return application


app: FastAPI = create_application()


# Define a custom middleware for token verification
class CustomMiddleware(BaseHTTPMiddleware): 
    def __init__(
        self,
        app: Any,
    ) -> None:
        super().__init__(app)

    async def dispatch(self, request, call_next):  # type: ignore
        try:
            # Call the verify_access_token function to validate the token
            token = request.headers.get("Authorization")
            if (token is None) or (token == ""):
                # print("Token is None or empty",)
                request.state.sub = "anonymous"
            else:
                try:
                    token = token.split(" ")[1]
                    if token is None:
                        request.state.sub = "anonymous"
                    else:
                        data = verify_access_token(token)
                        request.state.sub = data.sub
                        request.state.user = data.user
                except Exception:
                    request.state.sub = "anonymous"
            
            return await call_next(request)
        except Exception as e:
            print(f"Error in middleware: {repr(e)}")
            return await call_next(request)


# Add the custom middleware to the FastAPI app
app.add_middleware(CustomMiddleware)

@app.get("/")
async def health_check():
    """
    Root path
    """
    return {
        "status": "ok",
        "message": "Hello from Async CRM Backend!",
    }
