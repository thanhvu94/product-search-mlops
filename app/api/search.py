from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.api.schemas import ProductMetadata
from PIL import Image
import io
import torch
from transformers import CLIPProcessor, CLIPModel
import numpy as np
import json
from app.model.pinecone_client import PineConeManager

router = APIRouter(prefix="/search", tags=["Search"])

## Initialize model & pinecone
clip_model_name = "openai/clip-vit-base-patch32"
# Convert raw images & texts to the tensors CLIP expect
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = CLIPModel.from_pretrained(clip_model_name).to(device)
clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
# Init Pinecone helper
pinecone = PineConeManager(index_name="product-search-index", dimension=512)

def get_image_embedding(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = clip_processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        image_emb = clip_model.get_image_features(**inputs)
    image_emb = image_emb / image_emb.norm(p=2, dim=-1, keepdim=True)
    return image_emb.cpu().numpy()[0]

@router.post("/image")
async def search_by_image(file: bytes, top_k: int = 5):
    embedding = get_image_embedding(file)
    results = pinecone.search(embedding, top_k=top_k, namespace="products")
    # Return metadata of 1st matching result
    return {"results": results['matches'][0]['metadata']}

def get_text_embedding(text: str) -> np.ndarray:
    inputs = clip_processor(text=[text], return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        text_emb = clip_model.get_text_features(**inputs)
    text_emb = text_emb / text_emb.norm(p=2, dim=-1, keepdim=True)
    return text_emb.cpu().numpy()[0]

@router.post("/text")
async def search_by_text(query: str = Form(...), top_k: int = 5):
    embedding = get_text_embedding(query)
    results = pinecone.search(embedding, top_k=top_k, namespace="products")
    return {"results": results["matches"][0]['metadata']}

@router.post("/upsert-product")
async def upsert_product(image: UploadFile = File(...), metadata_json: str = Form(...)):
    # Parse metadata JSON into dict
    metadata_dict = json.loads(metadata_json)

    # Validate metadata with Pydantic
    metadata = ProductMetadata(**metadata_dict).dict()

    # Read image bytes
    image_bytes = await image.read()

    # Upsert to Pinecone
    result = pinecone.upsert_product_image(
        image_bytes=image_bytes,
        metadata=metadata,
        namespace="products"
    )

    return JSONResponse(
        content={"message": "Upsert successful", "result": result},
        status_code=200
    )