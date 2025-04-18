import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auditlog, auth, leads, quotations, roles, users
from app.util.setting import get_settings

settings = get_settings()


logger = logging.getLogger("app")


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


@app.get("/")
async def health_check():
    """
    Root path
    """
    return {
        "status": "ok",
        "message": "Hello from Async CRM Backend!",
    }


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(leads.router)
app.include_router(quotations.router)
app.include_router(auditlog.router)
