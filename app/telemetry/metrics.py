from prometheus_fastapi_instrumentator import Instrumentator

def setup_metrics(app):
    """
    Instruments the FastAPI app to expose Prometheus metrics.
    This automatically creates metrics like:
    - http_requests_total
    - http_requests_duration_seconds
    - http_requests_in_progress_total
    """
    instrumentator = Instrumentator(
        excluded_handlers=["/metrics", "/health"], # Don't instrument the metrics/health endpoints
    )
    
    # Instrument the app
    instrumentator.instrument(app)
    
    # Expose the /metrics endpoint
    instrumentator.expose(app, include_in_schema=False, should_gzip=True)