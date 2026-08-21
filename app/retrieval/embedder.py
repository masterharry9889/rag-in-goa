import os
from typing import List

import torch
from sentence_transformers import SentenceTransformer

from app.config import settings

# Avoid native crash/hang issues on some Windows CPU builds when tokenizers and
# torch spin up many worker threads during model startup and inference.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
if torch.cuda.is_available():
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
else:
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)


class Embedder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            cls._instance.model = SentenceTransformer(settings.embedding_model_name, device=device)
            if device == "cuda":
                cls._instance.model = cls._instance.model.half()
        return cls._instance

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


embedder = Embedder()
