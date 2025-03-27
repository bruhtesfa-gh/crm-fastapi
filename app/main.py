import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users
from app.util.setting import get_settings

settings = get_settings()


logger = logging.getLogger("app")


# def create_application() -> FastAPI:
#     """
#     Create the FastAPI application
#     """
#     # create the FastAPI application
#     application = FastAPI(
#         title="Async CRM Backend",
#         root_path="",
#         openapi_url="/openapi.json",
#         swagger_ui_parameters={"docExpansion": "none"},
#         debug=False,
#     )
#     #
#     # CORS
#     application.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.ALLOWED_HOSTS,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )
#     return application


app: FastAPI = FastAPI(
    title="Async CRM Backend",
    root_path="",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"docExpansion": "none"},
    debug=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
async def health_check():
    """
    Root path
    """
    return {
        "status": "ok",
        "message": "Hello from Async CRM Backend!",
    }
