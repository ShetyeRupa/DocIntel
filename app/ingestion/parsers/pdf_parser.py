# Updated import for langchain 0.1.x
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from typing import List, Dict, Any
import os

class PDFParser:
    """Extract text and metadata from PDFs"""
    
    def __init__(self, use_unstructured: bool = True):
        self.use_unstructured = use_unstructured
    
    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse PDF and return list of document chunks"""
        if self.use_unstructured:
            loader = UnstructuredPDFLoader(file_path)
        else:
            loader = PyPDFLoader(file_path)
        
        documents = loader.load()
        
        # Add metadata
        for doc in documents:
            doc.metadata.update({
                "source": os.path.basename(file_path),
                "file_path": file_path,
                "doc_type": "pdf"
            })
        
        return documents