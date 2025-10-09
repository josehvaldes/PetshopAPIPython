"""Data structure for vectorized file representation."""
from typing import TypedDict, List, Optional, Dict, Any

class VectorizedFile(TypedDict):
    file_name: str
    vectors: List[List[float]]
    texts: List[str]
    metadata: Dict[str, Any]
