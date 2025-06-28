from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1 import auth
from app.core.settings import settings


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


app.include_router(auth.router, prefix="/api/v1/auth")
