from chunking.base import ChunkerStrategy
from typing import List, Dict

class RecursiveChunker(ChunkerStrategy):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Define separators in order of priority
        self.separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, text: str, metadata: dict = None) -> list[str]:
        # Simplified recursive character text splitter
        def split_text(text: str, separators: list) -> list[str]:
            final_chunks = []
            # Get the separator to split on
            separator = separators[-1]
            new_separators = separators[:-1]

            if separators:
                splits = text.split(separator)
            else:
                splits = list(text)

            # Now go merging things, recursively splitting longer texts.
            good_splits = []
            for s in splits:
                if len(s) < self.chunk_size:
                    good_splits.append(s)
                else:
                    if good_splits:
                        merged = self._merge_splits(good_splits, separators)
                        final_chunks.extend(merged)
                        good_splits = []
                    # Recursively split the large chunk
                    other_info = split_text(s, new_separators)
                    good_splits.extend(other_info)
            if good_splits:
                merged = self._merge_splits(good_splits, separators)
                final_chunks.extend(merged)
            return final_chunks

        def _merge_splits(splits: list, separators: list) -> list[str]:
            # We now want to merge our smaller chunks together to meet the chunk_size and chunk_overlap
            separator = separators[-1] if separators else ""
            new_separators = separators[:-1] if separators else []

            merged = []
            current_chunk = []
            current_length = 0
            for s in splits:
                s_len = len(s)
                if current_length + s_len + len(separator) > self.chunk_size:
                    if current_chunk:
                        merged.append(separator.join(current_chunk))
                        # Reset with overlap
                        while current_chunk and len(separator.join(current_chunk)) > self.chunk_overlap:
                            current_chunk.pop(0)
                        current_length = len(separator.join(current_chunk)) if current_chunk else 0
                    else:
                        # Edge case: single item larger than chunk_size
                        merged.append(s)
                        current_chunk = []
                        current_length = 0
                current_chunk.append(s)
                current_length += s_len + (len(separator) if current_chunk else 0)
            if current_chunk:
                merged.append(separator.join(current_chunk))
            return merged

        return split_text(text, self.separators)