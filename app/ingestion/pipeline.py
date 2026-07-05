from app.ingestion.parsers.pdf_parser import PDFParser
from app.ingestion.chunker import SemanticChunker
from app.vector_store.chroma_client import ChromaClient
from app.config import settings
from typing import Optional, Dict, Any
import json
import os

class IngestionPipeline:
    """End-to-end document ingestion pipeline"""
    
    def __init__(self):
        self.parser = PDFParser()
        self.chunker = SemanticChunker()
        self.vector_store = ChromaClient()
        
        # Create directories
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    
    def process_document(self, file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a single document"""
        print(f"📄 Processing: {os.path.basename(file_path)}")
        
        # Parse
        documents = self.parser.parse(file_path)
        print(f"✅ Parsed {len(documents)} pages")
        
        # Chunk
        chunks = self.chunker.chunk_documents(documents)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Add custom metadata
        if metadata:
            for chunk in chunks:
                chunk.metadata.update(metadata)
        
        # Store in vector DB
        ids = self.vector_store.add_documents(chunks)
        print(f"✅ Stored in vector database")
        
        # Save processed metadata
        result = {
            "document": os.path.basename(file_path),
            "chunks": len(chunks),
            "chunk_ids": ids,
            "metadata": chunks[0].metadata if chunks else {}
        }
        
        # Save to JSON
        json_path = f"{settings.PROCESSED_DIR}/{ids[0]}_metadata.json"
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def batch_ingest(self, directory: str) -> Dict[str, Any]:
        """Process all documents in a directory"""
        import glob
        files = glob.glob(f"{directory}/*.pdf")
        results = []
        
        for file in files:
            try:
                result = self.process_document(file)
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to process {file}: {e}")
        
        return {
            "total_documents": len(files),
            "successful": len(results),
            "total_chunks": sum(r["chunks"] for r in results),
            "results": results
        }