from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        """Embed a list of texts into vectors."""
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        """Embed a single query text."""
        return self.model.encode([text])[0].tolist()