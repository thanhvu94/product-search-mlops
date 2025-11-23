import os
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import logging

def setup_tracing(app: FastAPI, service_name: str):
    """
    Configures OpenTelemetry tracing for the FastAPI application.
    """
    logger = logging.getLogger(__name__)
    
    # Set up a resource to identify this service
    resource = Resource(attributes={
        "service.name": service_name
    })

    # --- THIS IS THE FIX ---
    # We no longer pass 'endpoint' to the constructor.
    # The SDK will automatically find and use the 'OTEL_EXPORTER_OTLP_ENDPOINT'
    # environment variable that we set in docker-compose.yml.
    # This correctly handles the 'http://jaeger-all-in-one:4317' URL.
    try:
        span_exporter = OTLPSpanExporter()
        logger.info("OTLP Span Exporter initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize OTLP Span Exporter: {e}", exc_info=True)
        return

    # Set up a TracerProvider
    provider = TracerProvider(resource=resource)
    
    # Use a BatchSpanProcessor for better performance
    processor = BatchSpanProcessor(span_exporter)
    provider.add_span_processor(processor)

    # Set this as the global tracer provider
    trace.set_tracer_provider(provider)
    
    # Automatically instrument FastAPI
    # This will create traces for all incoming requests
    FastAPIInstrumentor.instrument_app(app, excluded_urls="health,metrics")
    logger.info("FastAPI instrumentation complete.")