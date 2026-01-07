from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse

from api.graphql.schema import create_graphql_router
from api.helpers.error.error_handler import (
    general_exception_handler,
    http_exception_handler,
)
from api.helpers.error.exceptions import APIValidationError
from config.settings import settings
from shared.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    try:
        logger.info("Initializing API with startup event")
        yield
    finally:
        logger.info("Shutting down API with shutdown event")


def init_app() -> FastAPI:
    """Initialize and configure the FastAPI application."""
    app = FastAPI(
        title="Backend API with GraphQL",
        description="FastAPI + Strawberry GraphQL backend",
        version="1.0.0",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        lifespan=lifespan,
    )

    # Register exception handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    async def validation_exception_handler(request, exc):
        return await http_exception_handler(request, APIValidationError(str(exc)))

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # CORS configuration
    origins = [str(origin).strip("/") for origin in settings.CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint (REST)
    @app.get("/health", response_class=JSONResponse, status_code=status.HTTP_200_OK)
    def health() -> JSONResponse:
        return JSONResponse({"status": "healthy", "service": "backend-api"})

    # Root endpoint
    @app.get("/", response_class=JSONResponse, status_code=status.HTTP_200_OK)
    def root() -> JSONResponse:
        return JSONResponse(
            {
                "message": "Backend API is running",
                "graphql": "/graphql",
                "docs": "/docs" if not settings.is_production else None,
            }
        )

    # Include GraphQL router
    graphql_router = create_graphql_router()
    app.include_router(graphql_router)

    # Include REST routers (for auth, etc.)
    # from api.routers import auth
    # app.include_router(auth.router, prefix="/auth", tags=["auth"])

    return app


app = init_app()
