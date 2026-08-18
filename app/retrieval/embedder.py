from sentence_transformers import SentenceTransformer
from typing import List
from app.config import settings
import torch

class Embedder:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            # Load the compact embedding model
            # We use CPU by default for the hackathon, but can switch to CUDA if available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            cls._instance.model = SentenceTransformer(settings.embedding_model_name, device=device)
            # We can quantize or cast to float16 to save space if needed
            if device == "cuda":
                cls._instance.model = cls._instance.model.half()
        return cls._instance

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Returns float32 embeddings natively, can be downcast to save space
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        # Convert to list of lists for ChromaDB
        return embeddings.tolist()

embedder = Embedder()
