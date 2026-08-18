import pytest
from app.chunking.strategies.fixed_overlap import FixedOverlapChunker
from app.chunking.strategies.semantic_split import SemanticSplitChunker
from app.chunking.strategies.sentence_window import SentenceWindowChunker
from app.chunking.strategies.metadata_aware import MetadataAwareChunker

def test_fixed_overlap_chunker():
    chunker = FixedOverlapChunker(chunk_size=10, overlap=2)
    text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12"
    chunks = chunker.chunk(text, "doc_1", {})
    
    assert len(chunks) > 0
    assert "word1" in chunks[0].text
    # Overlap means word9 and word10 should be in the second chunk too, if step is 8
    # chunk 0: 1-10
    # chunk 1: 9-12
    assert "word9" in chunks[1].text
    assert "word12" in chunks[-1].text

def test_metadata_aware_chunker():
    chunker = MetadataAwareChunker(max_tokens=10)
    text = "word1 word2 word3 word4 word5"
    base_meta = {"passage_id": "p123"}
    chunks = chunker.chunk(text, "doc_1", base_meta)
    
    assert len(chunks) == 1
    assert chunks[0].text == text
    assert chunks[0].metadata["passage_id"] == "p123"

def test_sentence_window_chunker():
    chunker = SentenceWindowChunker(window_size=1)
    text = "Sentence 1. Sentence 2. Sentence 3. Sentence 4."
    chunks = chunker.chunk(text, "doc_1", {})
    
    assert len(chunks) == 4
    # Chunk 1 (idx 1) should have window context of 0, 1, 2
    assert chunks[1].text == "Sentence 2."
    assert "Sentence 1." in chunks[1].metadata["window_context"]
    assert "Sentence 3." in chunks[1].metadata["window_context"]
