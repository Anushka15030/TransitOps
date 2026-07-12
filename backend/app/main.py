# app/main.py
"""
Application entrypoint. Wires middleware, error handlers, and routers.
Kept deliberately thin — all real logic is delegated to its proper layer.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware.error_handler import register_error_handlers
from app.middleware.request_logger import RequestLoggerMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,   # hide Swagger in production
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,     # required so the httpOnly refresh cookie is sent cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggerMiddleware)

register_error_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}