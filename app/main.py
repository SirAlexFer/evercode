from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware


from app.api.v1 import auth, category, transaction, analytics
from app.core.settings import settings


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)



app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(category.router, prefix="/api/v1/category")
app.include_router(transaction.router, prefix="/api/v1/transaction")
app.include_router(analytics.router, prefix="/api/v1")