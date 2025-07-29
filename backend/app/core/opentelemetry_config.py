"""
OpenTelemetry Configuration for the AI Assistant Platform.

This module provides centralized OpenTelemetry configuration for distributed tracing,
metrics collection, and observability.
"""

import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from backend.app.core.config import get_settings


class OpenTelemetryConfig:
    """OpenTelemetry configuration manager."""

    def __init__(self):
        self.settings = get_settings()
        self.tracer_provider: TracerProvider | None = None
        self.meter_provider: MeterProvider | None = None
        self.is_initialized = False

    def initialize(self, app=None, db_engine=None, redis_client=None):
        """Initialize OpenTelemetry with the application."""
        if self.is_initialized:
            return

        # Check if OpenTelemetry is enabled
        if not self._is_enabled():
            return

        try:
            # Create resource
            resource = Resource.create(
                {
                    "service.name": os.getenv(
                        "OTEL_SERVICE_NAME", "ai-assistant-platform"
                    ),
                    "service.version": self.settings.app_version,
                    "deployment.environment": self.settings.environment,
                    "service.instance.id": os.getenv("HOSTNAME", "unknown"),
                }
            )

            # Initialize tracing
            self._setup_tracing(resource)

            # Initialize metrics
            self._setup_metrics(resource)

            # Instrument FastAPI if app is provided
            if app:
                self._instrument_fastapi(app)

            # Instrument database if engine is provided
            if db_engine:
                self._instrument_database(db_engine)

            # Instrument Redis if client is provided
            if redis_client:
                self._instrument_redis(redis_client)

            # Instrument HTTP clients
            self._instrument_http_clients()

            self.is_initialized = True

        except Exception as e:
            # Log error but don't fail application startup
            import logging

            logging.exception(f"Failed to initialize OpenTelemetry: {e}")

    def _is_enabled(self) -> bool:
        """Check if OpenTelemetry is enabled."""
        # Disable in debug mode unless explicitly enabled
        if self.settings.debug and os.getenv("DISABLE_OTEL", "false").lower() == "true":
            return False

        # Check if OTLP endpoint is configured
        return os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    def _setup_tracing(self, resource: Resource):
        """Setup tracing with OTLP exporter."""
        self.tracer_provider = TracerProvider(resource=resource)

        # Configure span processor
        otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
        )
        insecure = os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"

        if otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=insecure)
            span_processor = BatchSpanProcessor(otlp_exporter)
        else:
            # Fallback to console exporter for development
            span_processor = BatchSpanProcessor(ConsoleSpanExporter())

        self.tracer_provider.add_span_processor(span_processor)
        trace.set_tracer_provider(self.tracer_provider)

    def _setup_metrics(self, resource: Resource):
        """Setup metrics with OTLP exporter."""
        # Configure metric reader
        otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
        )
        insecure = os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"

        if otlp_endpoint:
            metric_exporter = OTLPMetricExporter(
                endpoint=otlp_endpoint, insecure=insecure
            )
        else:
            # Fallback to console exporter for development
            metric_exporter = ConsoleMetricExporter()

        metric_reader = PeriodicExportingMetricReader(
            metric_exporter, export_interval_millis=60000  # Export every minute
        )

        self.meter_provider = MeterProvider(
            resource=resource, metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(self.meter_provider)

    def _instrument_fastapi(self, app):
        """Instrument FastAPI application."""
        FastAPIInstrumentor.instrument_app(app)

    def _instrument_database(self, db_engine):
        """Instrument SQLAlchemy database."""
        SQLAlchemyInstrumentor().instrument(engine=db_engine)

    def _instrument_redis(self, redis_client):
        """Instrument Redis client."""
        RedisInstrumentor().instrument()

    def _instrument_http_clients(self):
        """Instrument HTTP clients."""
        HTTPXClientInstrumentor().instrument()
        RequestsInstrumentor().instrument()

    def get_tracer(self, name: str = None):
        """Get a tracer instance."""
        if not self.is_initialized:
            return trace.get_tracer(__name__)
        return trace.get_tracer(name or __name__)

    def get_meter(self, name: str = None):
        """Get a meter instance."""
        if not self.is_initialized:
            return metrics.get_meter(__name__)
        return metrics.get_meter(name or __name__)

    def shutdown(self):
        """Shutdown OpenTelemetry."""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
        if self.meter_provider:
            self.meter_provider.shutdown()


# Global instance
opentelemetry_config = OpenTelemetryConfig()


def get_tracer(name: str = None):
    """Get a tracer instance."""
    return opentelemetry_config.get_tracer(name)


def get_meter(name: str = None):
    """Get a meter instance."""
    return opentelemetry_config.get_meter(name)


def initialize_opentelemetry(app=None, db_engine=None, redis_client=None):
    """Initialize OpenTelemetry."""
    opentelemetry_config.initialize(app, db_engine, redis_client)


def shutdown_opentelemetry():
    """Shutdown OpenTelemetry."""
    opentelemetry_config.shutdown()
