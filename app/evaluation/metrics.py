"""Metrics calculation for DocIntel evaluation."""
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class MetricsCalculator:
    """Calculate evaluation metrics for document intelligence."""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def calculate_mrr(self, results: List[Dict[str, Any]]) -> float:
        """Calculate Mean Reciprocal Rank."""
        reciprocal_ranks = []
        
        for result in results:
            if result.get('relevant_documents'):
                for idx, doc in enumerate(result['relevant_documents']):
                    if doc.get('is_relevant', False):
                        reciprocal_ranks.append(1 / (idx + 1))
                        break
                else:
                    reciprocal_ranks.append(0)
        
        return np.mean(reciprocal_ranks) if reciprocal_ranks else 0
    
    def calculate_precision_at_k(self, results: List[Dict[str, Any]], k: int = 5) -> float:
        """Calculate Precision@k."""
        precisions = []
        
        for result in results:
            relevant = result.get('relevant_documents', [])
            retrieved = result.get('retrieved_documents', [])[:k]
            
            if retrieved:
                relevant_retrieved = sum(1 for doc in retrieved if doc.get('is_relevant', False))
                precisions.append(relevant_retrieved / len(retrieved))
            else:
                precisions.append(0)
        
        return np.mean(precisions) if precisions else 0
    
    def calculate_recall_at_k(self, results: List[Dict[str, Any]], k: int = 5) -> float:
        """Calculate Recall@k."""
        recalls = []
        
        for result in results:
            relevant = result.get('relevant_documents', [])
            retrieved = result.get('retrieved_documents', [])[:k]
            
            if relevant:
                relevant_retrieved = sum(1 for doc in retrieved if doc.get('is_relevant', False))
                recalls.append(relevant_retrieved / len(relevant))
            else:
                recalls.append(0)
        
        return np.mean(recalls) if recalls else 0
    
    def calculate_ndcg(self, results: List[Dict[str, Any]], k: int = 5) -> float:
        """Calculate Normalized Discounted Cumulative Gain."""
        ndcg_scores = []
        
        for result in results:
            retrieved = result.get('retrieved_documents', [])[:k]
            relevance_scores = [doc.get('relevance_score', 0) for doc in retrieved]
            
            if relevance_scores:
                # Calculate DCG
                dcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(relevance_scores))
                
                # Calculate IDCG
                ideal = sorted(relevance_scores, reverse=True)
                idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal))
                
                ndcg = dcg / idcg if idcg > 0 else 0
                ndcg_scores.append(ndcg)
        
        return np.mean(ndcg_scores) if ndcg_scores else 0
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        embeddings = self.embedding_model.encode([text1, text2])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(similarity)
    
    def calculate_response_accuracy(self, response: str, ground_truth: str) -> float:
        """Calculate response accuracy against ground truth."""
        return self.calculate_semantic_similarity(response, ground_truth)
    
    def calculate_hallucination_rate(self, responses: List[Dict[str, Any]]) -> float:
        """Calculate hallucination rate from validation results."""
        if not responses:
            return 0
        
        hallucinated = sum(1 for r in responses if not r.get('validated', False))
        return hallucinated / len(responses)
    
    def calculate_confidence_calibration(self, results: List[Dict[str, Any]]) -> float:
        """Calculate confidence calibration (correlation between confidence and accuracy)."""
        confidences = [r.get('confidence', 0) for r in results]
        accuracies = [1 if r.get('passed', False) else 0 for r in results]
        
        return np.corrcoef(confidences, accuracies)[0, 1] if len(confidences) > 1 else 0
    
    def calculate_token_efficiency(self, total_tokens: int, num_queries: int) -> float:
        """Calculate tokens per query."""
        return total_tokens / num_queries if num_queries > 0 else 0
    
    def generate_full_report(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive metrics report."""
        results = test_results.get('results', [])
        
        return {
            "accuracy": test_results.get('accuracy', 0),
            "precision_at_5": self.calculate_precision_at_k(results, k=5),
            "recall_at_5": self.calculate_recall_at_k(results, k=5),
            "ndcg_at_5": self.calculate_ndcg(results, k=5),
            "hallucination_rate": self.calculate_hallucination_rate(results),
            "confidence_calibration": self.calculate_confidence_calibration(results),
            "avg_confidence": np.mean([r.get('confidence', 0) for r in results]) if results else 0,
            "pass_rate": test_results.get('accuracy', 0),
            "total_queries": len(results),
            "successful_queries": sum(1 for r in results if r.get('passed', False)),
            "failed_queries": sum(1 for r in results if not r.get('passed', False))
        }