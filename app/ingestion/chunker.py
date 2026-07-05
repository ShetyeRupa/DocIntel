# Updated import for langchain 0.1.x
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from app.config import settings
from typing import List, Dict, Any
import hashlib
import json

class SemanticChunker:
    """Intelligent chunking with overlap and metadata preservation"""
    
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " ", ""],
            length_function=len,
        )
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Document]:
        """Split documents into chunks with metadata"""
        # Convert to LangChain Documents if needed
        lc_docs = []
        for doc in documents:
            if isinstance(doc, dict):
                lc_docs.append(Document(
                    page_content=doc.get("page_content", ""),
                    metadata=doc.get("metadata", {})
                ))
            else:
                lc_docs.append(doc)
        
        # Split
        chunks = self.splitter.split_documents(lc_docs)
        
        # Add chunk IDs
        for chunk in chunks:
            chunk.metadata["chunk_id"] = hashlib.md5(
                chunk.page_content.encode()
            ).hexdigest()
            chunk.metadata["chunk_size"] = len(chunk.page_content)
        
        return chunks