"""
AI Assistant Platform - Main Application Entry Point

This module contains the main FastAPI application setup and configuration.
"""

import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from backend.app.api.v1.api import api_router
from backend.app.core.config import get_settings
from backend.app.core.database import check_db_connection, engine, get_db, init_db
from backend.app.core.error_responses import CommonErrors, handle_validation_errors
from backend.app.core.i18n import I18nMiddleware, i18n_manager, t
from backend.app.core.opentelemetry_config import (
    initialize_opentelemetry,
    shutdown_opentelemetry,
)
from backend.app.core.redis_client import (
    check_redis_connection,
    close_redis,
    get_redis_info,
    init_redis,
    redis_client,
)
from backend.app.core.security_middleware import setup_security_middleware
from backend.app.core.sso_manager import init_sso_manager
from backend.app.core.weaviate_client import (
    check_weaviate_connection,
    close_weaviate,
    create_schema_if_not_exists,
    init_weaviate,
)
from backend.app.monitoring import PerformanceMiddleware, get_performance_monitor
from backend.app.services.audit_service import audit_service
from backend.app.services.enhanced_background_job_service import job_manager


@asynccontextmanager
async def lifespan(_: Any) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AI Assistant Platform...")
    logger.info(f"Environment: {get_settings().environment}")
    logger.info(f"Debug mode: {get_settings().debug}")

    def raise_runtime_error(msg):
        raise RuntimeError(msg)

    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        if not check_db_connection():
            logger.error("Database connection failed")
            raise_runtime_error("Database connection failed")
        logger.info("Database initialized successfully")

        # Initialize Redis with graceful degradation
        logger.info("Initializing Redis...")
        redis_client = await init_redis()
        if redis_client is None:
            logger.warning("Redis not available - continuing without caching")
        else:
            logger.info("Redis initialized successfully")

        # Initialize Weaviate
        logger.info("Initializing Weaviate...")
        init_weaviate()
        if not check_weaviate_connection():
            logger.error("Weaviate connection failed")
            raise_runtime_error("Weaviate connection failed")
        create_schema_if_not_exists()
        logger.info("Weaviate initialized successfully")

        # Start audit service
        await audit_service.start()
        logger.info("Audit service started")

        # Start enhanced job manager
        job_manager.start()
        logger.info("Enhanced job manager started")

        # Initialize SSO manager
        init_sso_manager()
        logger.info("SSO manager initialized")

        # Get database session for performance monitor
        db = next(get_db())

        # Initialize performance monitor
        performance_monitor = get_performance_monitor(db)
        await performance_monitor.start_monitoring()
        logger.info("Performance monitor started")

        logger.info("All services initialized successfully")

    except Exception as exc:  # noqa: BLE001
        logger.error(f"Failed to initialize services: {exc}")

        def raise_inner(exc=exc):
            raise RuntimeError("Failed to initialize services: " + str(exc))

        raise_inner()

    yield

    # Shutdown
    logger.info("Shutting down AI Assistant Platform...")
    try:
        await audit_service.stop()
        job_manager.stop()

        # Stop performance monitor
        db = next(get_db())
        performance_monitor = get_performance_monitor(db)
        await performance_monitor.stop_monitoring()

        await close_redis()
        close_weaviate()
        shutdown_opentelemetry()
        logger.info("All services closed successfully")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error during shutdown: {e}")


def configure_opentelemetry(
    app: FastAPI, db_engine: Any = None, redis_client: Any = None
) -> None:
    """Configure OpenTelemetry for the application."""
    initialize_opentelemetry(app, db_engine, redis_client)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Configure logging to console for now (file logging disabled due to permission issues)
    logger.add(
        sys.stdout.write,
        level=get_settings().log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    )

    # Create FastAPI app
    app = FastAPI(
        title="AI Assistant Platform",
        version=get_settings().app_version,
        description="AI Assistant Platform with multiple assistants and extensive tool support",
        docs_url="/docs" if get_settings().debug else None,
        redoc_url="/redoc" if get_settings().debug else None,
        openapi_url="/openapi.json" if get_settings().debug else None,
        lifespan=lifespan,
    )

    configure_opentelemetry(app, db_engine=engine, redis_client=redis_client)

    # Setup security middleware first
    setup_security_middleware(app)

    # Add CORS middleware with secure configuration
    cors_origins = [
        origin.strip()
        for origin in get_settings().cors.cors_origins.split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=get_settings().cors.cors_allow_credentials,
        allow_methods=get_settings().cors.cors_allow_methods,
        allow_headers=get_settings().cors.cors_allow_headers,
        max_age=get_settings().cors.cors_max_age,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=(
            ["*"]
            if get_settings().debug
            else [
                "localhost",
                "127.0.0.1",
                "yourdomain.com",
                "testserver",
                "testserver.local",
            ]
        ),
    )

    # Add i18n middleware
    app.add_middleware(I18nMiddleware, i18n_manager=i18n_manager)

    # Add session middleware for OAuth
    app.add_middleware(SessionMiddleware, secret_key=get_settings().security.secret_key)

    # Add performance monitoring middleware
    if get_settings().monitoring.performance_monitoring_enabled:
        db = next(get_db())
        performance_monitor = get_performance_monitor(db)
        app.add_middleware(
            PerformanceMiddleware,
            metrics_collector=performance_monitor.metrics_collector,
        )

    # Add exception handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _: Any, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
        # Translate error message
        translated_detail = t(
            f"errors.{exc.detail.lower().replace(' ', '_')}",
            None,
            fallback=exc.detail,
        )

        # Create standardized error response
        error_response = CommonErrors.internal_server_error(
            message=translated_detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump() if hasattr(error_response, "model_dump") else error_response.dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Any, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation exceptions."""
        logger.warning(f"Validation error: {exc.errors()}")

        # Convert validation errors to standardized format
        details = handle_validation_errors(exc.errors())
        error_response = CommonErrors.validation_error(
            message="Request validation failed",
            details=details,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump() if hasattr(error_response, "model_dump") else error_response.dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_: Any, exc: Exception) -> JSONResponse:
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}")
        error_response = CommonErrors.internal_server_error(
            message="An unexpected error occurred",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump() if hasattr(error_response, "model_dump") else error_response.dict(),
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, Any]:
        """Health check endpoint with service status."""
        # Check Redis status
        try:
            redis_connected = await check_redis_connection()
            redis_info = await get_redis_info()
            redis_status = "connected" if redis_connected else "unavailable"
        except (ConnectionError, TimeoutError) as e:
            redis_status = "error"
            redis_info = {"error": str(e)}
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.error("Unexpected error in health check: %s", str(e))
            redis_status = "error"
            redis_info = {"error": "Internal error"}

        return {
            "status": "healthy",
            "app_name": get_settings().app_name,
            "version": get_settings().app_version,
            "environment": get_settings().environment,
            "timestamp": datetime.now(UTC).isoformat(),
            "services": {"redis": {"status": redis_status, "info": redis_info}},
        }

    # Config endpoint for frontend (must be before API routers)
    @app.get("/api/config")
    async def get_config() -> dict[str, Any]:
        """Get application configuration for frontend."""
        return {
            "apiUrl": "/api",
            "wsUrl": get_settings().ws_url,
            "isDevelopment": get_settings().debug,
            "isProduction": not get_settings().debug,
            "enableDebug": get_settings().debug,
            "wsEndpoints": {
                "chat": "/api/v1/chat/ws/",
                "notifications": "/api/v1/ws/notifications",
            },
            "apiEndpoints": {
                "auth": "/api/v1/auth",
                "users": "/api/v1/users",
                "conversations": "/api/v1/conversations",
                "chat": "/api/v1/chat",
                "tools": "/api/v1/tools",
                "assistants": "/api/v1/assistants",
                "knowledge": "/api/v1/knowledge",
                "health": "/api/v1/health",
            },
        }

    # Add missing endpoints for frontend compatibility (must be before API routers)
    @app.get("/api/assistants")
    async def get_assistants_legacy() -> dict[str, str]:
        """Legacy assistants endpoint."""
        return {"message": "Use /api/v1/assistants instead"}

    @app.get("/api/knowledge/documents")
    async def get_knowledge_documents_legacy() -> dict[str, str]:
        """Legacy knowledge documents endpoint."""
        return {"message": "Use /api/v1/knowledge/documents instead"}

    @app.get("/api/ai/models")
    async def get_ai_models_legacy() -> dict[str, str]:
        """Legacy AI models endpoint."""
        return {"message": "Use /api/v1/ai/models instead"}

    # Add routes
    app.include_router(api_router, prefix="/api/v1")

    # Root endpoint
    @app.get("/")
    async def root() -> dict[str, Any]:
        """Root endpoint."""
        return {
            "message": "Welcome to AI Assistant Platform",
            "version": get_settings().app_version,
            "docs": (
                "/docs"
                if get_settings().debug
                else "Documentation disabled in production"
            ),
        }

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=get_settings().host,
        port=get_settings().port,
        reload=get_settings().debug,
        log_level=get_settings().log_level.lower(),
    )
