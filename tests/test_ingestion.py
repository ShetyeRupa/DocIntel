"""Unit tests for ingestion pipeline."""
import pytest
import os
import tempfile
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.parsers.pdf_parser import PDFParser
from app.ingestion.chunker import SemanticChunker

class TestIngestion:
    
    def test_pdf_parser(self):
        """Test PDF parser functionality."""
        parser = PDFParser()
        
        # Create a temporary PDF (simulated)
        # In real tests, you'd have a sample PDF
        assert parser is not None
    
    def test_chunker(self):
        """Test semantic chunker."""
        chunker = SemanticChunker()
        
        sample_text = "This is a test document. " * 100
        documents = [{
            "page_content": sample_text,
            "metadata": {"source": "test"}
        }]
        
        chunks = chunker.chunk_documents(documents)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert hasattr(chunk, "page_content")
            assert hasattr(chunk, "metadata")
            assert "chunk_id" in chunk.metadata
    
    def test_ingestion_pipeline(self):
        """Test full ingestion pipeline."""
        pipeline = IngestionPipeline()
        assert pipeline is not None
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".txt",
            mode="w",
            delete=False
        ) as f:
            f.write("This is a test document for ingestion.")
            temp_path = f.name
        
        # Process
        try:
            result = pipeline.process_document(temp_path)
            assert result is not None
            assert "chunks" in result
        finally:
            os.unlink(temp_path)

if __name__ == "__main__":
    pytest.main([__file__])