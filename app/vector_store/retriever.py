from app.vector_store.chroma_client import ChromaClient
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
import nltk
from nltk.tokenize import word_tokenize

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class Retriever:
    """Hybrid retriever combining semantic + keyword search"""
    
    def __init__(self):
        self.vector_store = ChromaClient()
        self.bm25_index = None
        self.corpus = []
        self._build_bm25_index()
    
    def _build_bm25_index(self):
        """Build BM25 index for keyword search"""
        try:
            # Get all documents from collection
            all_docs = self.vector_store.collection.get(
                include=["documents"]
            )
            
            if all_docs and all_docs["documents"]:
                self.corpus = all_docs["documents"]
                tokenized_corpus = [
                    word_tokenize(doc.lower()) for doc in self.corpus
                ]
                self.bm25_index = BM25Okapi(tokenized_corpus)
                print(f"✅ Built BM25 index with {len(self.corpus)} documents")
        except Exception as e:
            print(f"⚠️ BM25 index not built: {e}")
    
    def hybrid_search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Perform hybrid search (semantic + BM25)"""
        if k is None:
            from app.config import settings
            k = settings.TOP_K
        
        # Semantic search
        semantic_results = self.vector_store.search(query, k=k*2)
        
        # Keyword search (BM25)
        bm25_results = []
        if self.bm25_index and self.corpus:
            tokenized_query = word_tokenize(query.lower())
            scores = self.bm25_index.get_scores(tokenized_query)
            
            # Get top BM25 results
            top_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True
            )[:k*2]
            
            for idx in top_indices:
                if scores[idx] > 0:
                    bm25_results.append({
                        "document": self.corpus[idx],
                        "score": scores[idx] / max(scores) if max(scores) > 0 else 0,
                        "source": "bm25"
                    })
        
        # Combine and deduplicate
        combined = {}
        
        # Add semantic results
        for item in semantic_results:
            doc_key = item["document"][:100]  # Use first 100 chars as key
            combined[doc_key] = {
                "document": item["document"],
                "score": item["score"] * 0.7,  # Weight semantic
                "metadata": item.get("metadata", {}),
                "source": "semantic"
            }
        
        # Add BM25 results
        for item in bm25_results:
            doc_key = item["document"][:100]
            if doc_key in combined:
                combined[doc_key]["score"] += item["score"] * 0.3  # Add BM25 weight
                combined[doc_key]["source"] = "hybrid"
            else:
                combined[doc_key] = {
                    "document": item["document"],
                    "score": item["score"] * 0.3,
                    "metadata": {},
                    "source": "bm25"
                }
        
        # Sort by score and return top k
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x["score"],
            reverse=True
        )[:k]
        
        return sorted_results