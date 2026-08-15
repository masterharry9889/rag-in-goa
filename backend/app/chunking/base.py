from abc import ABC, abstractmethod
from typing import List, Dict

class ChunkerStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str, metadata: Dict = None) -> List[str]:
        """Split text into chunks."""
        pass