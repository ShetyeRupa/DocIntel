"""Unit tests for retrieval system."""
import pytest
from app.vector_store.retriever import Retriever
from app.vector_store.chroma_client import ChromaClient

class TestRetrieval:
    
    def test_retriever_init(self):
        """Test retriever initialization."""
        retriever = Retriever()
        assert retriever is not None
        assert retriever.vector_store is not None
    
    def test_hybrid_search(self):
        """Test hybrid search functionality."""
        retriever = Retriever()
        
        # Add some test documents
        test_docs = [
            {"document": "This is a test document about contracts.", "metadata": {"source": "test1"}},
            {"document": "This document discusses payment terms and conditions.", "metadata": {"source": "test2"}},
            {"document": "This is about legal liability and termination clauses.", "metadata": {"source": "test3"}}
        ]
        
        # Search
        results = retriever.hybrid_search("contract terms", k=2)
        
        assert results is not None
        assert len(results) <= 2
    
    def test_semantic_search(self):
        """Test semantic search."""
        retriever = Retriever()
        
        results = retriever.vector_store.search("test query", k=3)
        
        assert results is not None
    
    def test_bm25_index(self):
        """Test BM25 index building."""
        retriever = Retriever()
        assert retriever.bm25_index is not None

if __name__ == "__main__":
    pytest.main([__file__])