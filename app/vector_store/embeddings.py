from sentence_transformers import SentenceTransformer
from app.config import settings
import numpy as np
from typing import List

class EmbeddingManager:
    """Manage local embeddings (no API cost)"""
    
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"✅ Loaded embedding model: {settings.EMBEDDING_MODEL} (dim: {self.dimension})")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for list of texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        embedding = self.model.encode([query], convert_to_numpy=True)
        return embedding[0].tolist()