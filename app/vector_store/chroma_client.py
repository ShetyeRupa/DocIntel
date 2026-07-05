import chromadb
from chromadb.config import Settings
from app.config import settings
from app.vector_store.embeddings import EmbeddingManager
from typing import List, Dict, Any
import uuid

class ChromaClient:
    """Wrapper for ChromaDB vector database"""
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"✅ Connected to ChromaDB collection: {settings.COLLECTION_NAME}")
        print(f"📊 Current documents: {self.collection.count()}")
    
    def add_documents(self, documents: List[Any]) -> List[str]:
        """Add documents to vector store"""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [str(uuid.uuid4()) for _ in documents]
        
        # Generate embeddings
        embeddings = self.embedding_manager.embed_texts(texts)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return ids
    
    def search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if k is None:
            k = settings.TOP_K
        
        # Generate query embedding
        query_embedding = self.embedding_manager.embed_query(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "score": 1 - results["distances"][0][i]  # Convert to similarity
                })
        
        return formatted_results
    
    def delete_all(self):
        """Clear all documents (for testing)"""
        self.client.delete_collection(settings.COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        print("🗑️ Cleared all documents")
    
    def count(self) -> int:
        """Get total document count"""
        return self.collection.count()