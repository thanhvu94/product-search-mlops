import os
import uuid
import io
from PIL import Image
import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel
from pinecone import Pinecone, ServerlessSpec


class PineConeManager:
    def __init__(self, index_name="product-search-index", dimension=512, metric="cosine"):
        # Load Pinecone key safely
        api_key = "pcsk_46kXT7_36deFBTV7K74ANhJ6gDcpNvAUQpy9o18pNxVGrHuVESSApnmFrg81SKJKBkMKDR"
        self.pc = Pinecone(api_key=api_key)

        # Create index if needed
        existing = self.pc.list_indexes().names()
        if index_name not in existing:
            print(f"Creating index '{index_name}'...")
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        # Attach to index
        self.index = self.pc.Index(index_name)

        # Device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load CLIP model
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def _generate_image_embedding(self, image_bytes: bytes) -> np.ndarray:
        """Convert image -> normalized CLIP embedding."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            emb = self.model.get_image_features(**inputs)

        emb = emb.cpu().numpy()[0]
        emb = emb / np.linalg.norm(emb)  # normalize
        return emb

    def upsert_product_image(self, image_bytes: bytes, metadata: dict, namespace="products"):
        """
        Upsert a single image embedding + metadata into Pinecone.
        """
        vector_id = metadata.get("id", str(uuid.uuid4()))

        # Compute embedding
        embedding = self._generate_image_embedding(image_bytes)

        # Pinecone v3 format
        vector_record = {
            "id": vector_id,
            "values": embedding.tolist(),
            "metadata": metadata,
        }

        # Upsert
        self.index.upsert(
            vectors=[vector_record],
            namespace=namespace
        )

        return {
            "vector_id": vector_id,
            "status": "success",
            "namespace": namespace
        }

    def search(self, query_embedding, top_k=5, namespace="products"):
        result = self.index.query(vector=query_embedding.tolist(), top_k=top_k, include_metadata=True, namespace=namespace)
        return result