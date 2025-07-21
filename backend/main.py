"""
Main FastAPI application for the AI Assistant Platform.

This module serves as the entry point for the FastAPI application,
configuring middleware, routes, and application lifecycle events.
"""

from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import check_db_connection, init_db
from app.core.i18n import I18nMiddleware, i18n_manager, t
from app.core.redis_client import check_redis_connection, close_redis, init_redis
from app.core.weaviate_client import (
    check_weaviate_connection,
    close_weaviate,
    create_schema_if_not_exists,
    init_weaviate,
)
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AI Assistant Platform...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        if not check_db_connection():
            logger.error("Database connection failed")
            raise RuntimeError("Database connection failed")
        logger.info("Database initialized successfully")

        # Initialize Redis
        logger.info("Initializing Redis...")
        await init_redis()
        if not await check_redis_connection():
            logger.error("Redis connection failed")
            raise RuntimeError("Redis connection failed")
        logger.info("Redis initialized successfully")

        # Initialize Weaviate
        logger.info("Initializing Weaviate...")
        init_weaviate()
        if not check_weaviate_connection():
            logger.error("Weaviate connection failed")
            raise RuntimeError("Weaviate connection failed")
        create_schema_if_not_exists()
        logger.info("Weaviate initialized successfully")

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Assistant Platform...")
    try:
        await close_redis()
        close_weaviate()
        logger.info("All services closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Configure logging
    logger.add(
        settings.log_file,
        rotation="10 MB",
        retention="7 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI Assistant Platform with multiple assistants and extensive tool support",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"],
    )

    # Add i18n middleware
    app.add_middleware(I18nMiddleware, i18n_manager=i18n_manager)

    # Add exception handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
        # Translate error message
        translated_detail = t(
            f"errors.{exc.detail.lower().replace(' ', '_')}",
            request,
            fallback=exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": translated_detail, "status_code": exc.status_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError,
    ):
        """Handle validation exceptions."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors(), "status_code": 422},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "status_code": 500},
        )

    # Add routes
    app.include_router(api_router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        }

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to AI Assistant Platform",
            "version": settings.app_version,
            "docs": "/docs"
            if settings.debug
            else "Documentation disabled in production",
        }

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
