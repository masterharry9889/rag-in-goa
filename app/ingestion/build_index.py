"""
build_index.py — Ingestion pipeline for MSMARCO-XI Hindi Validation dataset.

Dataset schema (hinval.parquet):
  - query_id        : int   — unique query identifier
  - query           : str   — Hindi question
  - Answer          : str   — Hindi reference answer
  - passages        : dict  — {
        "English_passages"   : list[str],
        "Translated_passages": list[str],   ← we index these (Hindi)
        "is_selected"        : list[int]    ← 1 = relevant, 0 = not
    }
  - query_type      : str   — e.g. DESCRIPTION, NUMERIC, ...
  - Eng_Query       : str   — English question (for reference)

We index each Hindi passage as a separate document so the retriever can
surface the exact passage relevant to an incoming Hindi query.
"""

import hashlib
import logging

import pandas as pd
from tqdm import tqdm

from app.chunking.chunker_router import chunker_router
from app.config import settings
from app.ingestion.download_dataset import download_hinval_dataset
from app.retrieval.chroma_client import chroma_db
from app.retrieval.embedder import embedder

logger = logging.getLogger(__name__)

BATCH_SIZE = 256  # larger batch = fewer embedding calls = faster ingestion


def build_index():
    collection = chroma_db.collection

    # ── Skip if already indexed ───────────────────────────────────────────────
    existing_count = collection.count()
    if existing_count > 0:
        print(
            f"[build_index] Collection '{settings.collection_name}' already contains "
            f"{existing_count} documents. Skipping re-ingestion.\n"
            f"  To force a full rebuild: delete data/chroma/ then re-run."
        )
        return

    # 1. Download dataset
    file_path = download_hinval_dataset()

    # 2. Load parquet
    print(f"[build_index] Loading parquet from {file_path} ...")
    df = pd.read_parquet(file_path)
    print(f"[build_index] Dataset shape: {df.shape}, columns: {list(df.columns)}")

    # Limit corpus size as configured
    total_rows = min(len(df), settings.max_indexed_passages)
    df = df.head(total_rows)
    print(f"[build_index] Processing {total_rows} rows (max_indexed_passages={settings.max_indexed_passages}) ...")

    docs_batch = []
    meta_batch = []
    ids_batch  = []
    seen_hashes = set()
    total_passages_seen = 0
    total_passages_indexed = 0

    for idx, row in tqdm(df.iterrows(), total=total_rows, desc="Indexing"):
        query_id   = str(row.get("query_id", idx))
        query_text = str(row.get("query", ""))
        answer     = str(row.get("Answer", ""))

        # ── Extract Hindi passages from the nested `passages` dict ──────────
        passages_dict = row.get("passages", {})
        if not isinstance(passages_dict, dict):
            continue

        raw_passages = passages_dict.get("Translated_passages")
        raw_selected = passages_dict.get("is_selected")
        # Use list() directly — avoids numpy truth-value ambiguity from 'or []'
        hindi_passages = list(raw_passages) if raw_passages is not None else []
        is_selected    = list(raw_selected)  if raw_selected  is not None else []

        if len(hindi_passages) == 0:
            continue

        for passage_idx, passage_text in enumerate(hindi_passages):
            passage_text = str(passage_text).strip()
            if not passage_text:
                continue

            total_passages_seen += 1
            selected = bool(is_selected[passage_idx]) if passage_idx < len(is_selected) else False

            base_meta = {
                "query_id"     : query_id,
                "passage_idx"  : passage_idx,
                "is_selected"  : int(selected),
                "lang"         : "hi",
                "query_preview": query_text[:80],
            }

            # Use only metadata_aware strategy for ingestion.
            # SemanticSplitChunker re-embeds every sentence during chunking
            # (to find split points), causing 2x embedding overhead and multi-hour
            # runtimes. MSMARCO passages are already pre-split — metadata_aware
            # is the right strategy: zero embedding cost during chunking.
            chunks = chunker_router.chunk(
                passage_text,
                source_doc_id=f"{query_id}_{passage_idx}",
                base_metadata=base_meta,
                active_strategies=["metadata_aware"],
            )

            for chunk in chunks:
                # Content-based deduplication
                content_hash = hashlib.sha256(chunk.text.encode("utf-8")).hexdigest()
                if content_hash in seen_hashes:
                    continue
                seen_hashes.add(content_hash)

                docs_batch.append(chunk.text)
                meta_batch.append({
                    "strategy"     : chunk.strategy,
                    "query_id"     : query_id,
                    "passage_idx"  : passage_idx,
                    "is_selected"  : int(selected),
                    "position"     : chunk.metadata.get("position", 0),
                    "query_preview": query_text[:80],
                })
                # Use content_hash as the Chroma ID — guaranteed unique per unique text,
                # unlike chunk.id which is structural (source_doc_id + position) and can
                # collide when two different passages produce the same positional hash.
                ids_batch.append(content_hash)

                # Flush batch
                if len(docs_batch) >= BATCH_SIZE:
                    embeddings = embedder.embed_texts(docs_batch)
                    collection.upsert(
                        ids=ids_batch,
                        documents=docs_batch,
                        embeddings=embeddings,
                        metadatas=meta_batch,
                    )
                    total_passages_indexed += len(docs_batch)
                    docs_batch = []
                    meta_batch = []
                    ids_batch  = []

    # Flush remaining
    if docs_batch:
        embeddings = embedder.embed_texts(docs_batch)
        collection.upsert(
            ids=ids_batch,
            documents=docs_batch,
            embeddings=embeddings,
            metadatas=meta_batch,
        )
        total_passages_indexed += len(docs_batch)

    final_count = collection.count()
    print(
        f"\n[build_index] ✅ Done.\n"
        f"  Passages seen      : {total_passages_seen}\n"
        f"  Unique chunks indexed: {len(seen_hashes)}\n"
        f"  Collection count   : {final_count}"
    )


if __name__ == "__main__":
    build_index()
