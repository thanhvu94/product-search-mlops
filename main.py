from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from app.api.search import search_by_image, search_by_text, upsert_product
from app.telemetry.tracing import setup_tracing
from app.telemetry.metrics import setup_metrics
from app.core.logging import setup_logging
import logging

# Set up JSON logging as the first thing
setup_logging()
# Get a logger instance
logger = logging.getLogger(__name__)

def create_app():
    # Init a FastAPI instance
    app = FastAPI(title="Product search")

    # Init tracing & metrics
    setup_tracing(app, "product-search")
    setup_metrics(app)
    logger.info("Telemetry and metrics initialized.")

    # Register the following function as an HTTP POST handler
    @app.post("/search_by_image")
    async def _search_by_image(file: UploadFile = File(...), top_k: int = 5):
        # Read uploaded image bytes
        img_bytes = await file.read()
        # Call search_by_image from search.py
        return await search_by_image(img_bytes, top_k)
    
    @app.post("/search_by_text")
    async def _search_by_text(query: str = Form(...), top_k: int = 5):
        return await search_by_text(query, top_k)
    
    @app.post("/upsert_product")
    async def _upsert_product(file: UploadFile = File(...), metadata_json: str = Form(...)):
        return await upsert_product(file, metadata_json)

    @app.get("/health")
    def health_check():
        logger.info("Health check endpoint was called.")
        return {"status": "ok"}

    logger.info("Application setup complete.")
    return app

app = create_app()