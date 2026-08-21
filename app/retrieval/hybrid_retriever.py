import logging
from app.retrieval.chroma_client import chroma_db
from app.retrieval.embedder import embedder
from app.config import settings
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# ChromaDB uses cosine *distance* in the range [0, 2], not [0, 1].
# Distance 0   = identical vectors  (similarity = 1.0)
# Distance 1   = orthogonal vectors (similarity = 0.0)
# Distance 2   = opposite vectors   (similarity = -1.0)
# We reject chunks with distance > 1.2, i.e. cosine similarity < -0.2
# (truly unrelated). This is intentionally lenient so we don't throw away
# weakly-relevant chunks — the LLM's system prompt handles "no answer" cases.
_MAX_COSINE_DISTANCE = 1.2


class HybridRetriever:
    def __init__(self, top_k: int = None):
        self.collection = chroma_db.collection
        self.top_k = top_k or settings.retrieval_top_k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        doc_count = self.collection.count()
        logger.debug("[RAG] Collection has %d documents. Querying top-%d.", doc_count, self.top_k)

        if doc_count == 0:
            logger.warning(
                "[RAG] ChromaDB collection is empty — retrieval returned 0 chunks. "
                "Run `bash scripts/ingest.sh` to index the dataset."
            )
            return []

        # Generate query embedding
        query_embedding = embedder.embed_texts([query])[0]

        # Dense retrieval from ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(self.top_k, doc_count),
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        if results and results["ids"] and len(results["ids"]) > 0:
            raw_count = len(results["ids"][0])
            logger.debug("[RAG] ChromaDB returned %d raw candidates for query: %r", raw_count, query[:80])

            for i in range(raw_count):
                distance = results["distances"][0][i]
                similarity = 1.0 - (distance / 2.0)  # map [0,2] → [1,-1]
                doc_text = results["documents"][0][i]
                doc_id = results["ids"][0][i]

                logger.debug(
                    "[RAG] Candidate %d | id=%s | distance=%.4f | similarity=%.4f | text=%r",
                    i,
                    doc_id,
                    distance,
                    similarity,
                    doc_text[:100],
                )

                if distance > _MAX_COSINE_DISTANCE:
                    logger.debug(
                        "[RAG] Skipping chunk %s — distance %.4f exceeds threshold %.2f",
                        doc_id,
                        distance,
                        _MAX_COSINE_DISTANCE,
                    )
                    continue

                chunks.append({
                    "id": doc_id,
                    "text": doc_text,
                    "metadata": results["metadatas"][0][i],
                    "score": round(similarity, 4),
                })

        logger.info(
            "[RAG] Retrieved %d/%d chunks after distance filtering (threshold=%.2f).",
            len(chunks),
            self.top_k,
            _MAX_COSINE_DISTANCE,
        )
        return chunks
