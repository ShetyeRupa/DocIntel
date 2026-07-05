"""Logging and monitoring for DocIntel."""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import wandb

class Logger:
    """Logging and monitoring for DocIntel."""
    
    def __init__(self, project_name: str = "docintel", use_wandb: bool = False):
        self.project_name = project_name
        self.use_wandb = use_wandb
        self.logs = []
        self.log_file = "docintel_logs.json"
        
        if use_wandb:
            try:
                wandb.init(project=project_name, config={
                    "model": "groq",
                    "embedding_model": "all-MiniLM-L6-v2",
                    "chunk_size": 1000
                })
            except:
                self.use_wandb = False
                print("⚠️ WandB initialization failed, logging locally")
        
        self._load_logs()
    
    def _load_logs(self):
        """Load existing logs."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    self.logs = json.load(f)
            except:
                self.logs = []
    
    def _save_logs(self):
        """Save logs to file."""
        with open(self.log_file, "w") as f:
            json.dump(self.logs, f, indent=2)
    
    def log_query(
        self,
        query: str,
        response: str,
        confidence: float,
        sources: list,
        intent: str,
        response_time: float,
        tokens_used: int,
        validation_passed: bool
    ):
        """Log a query and its results."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "confidence": confidence,
            "sources": sources,
            "intent": intent,
            "response_time": response_time,
            "tokens_used": tokens_used,
            "validation_passed": validation_passed
        }
        
        self.logs.append(log_entry)
        self._save_logs()
        
        # Log to WandB
        if self.use_wandb:
            wandb.log({
                "query": query,
                "confidence": confidence,
                "response_time": response_time,
                "tokens_used": tokens_used,
                "validation_passed": validation_passed,
                "intent": intent
            })
    
    def log_feedback(
        self,
        query_id: str,
        rating: int,
        feedback: str,
        corrected_response: Optional[str] = None
    ):
        """Log user feedback."""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "query_id": query_id,
            "rating": rating,
            "feedback": feedback,
            "corrected_response": corrected_response
        }
        
        # Find and update the corresponding query log
        for log in self.logs:
            if log.get("timestamp") == query_id:
                log["feedback"] = feedback_entry
                break
        
        self._save_logs()
        
        if self.use_wandb:
            wandb.log({
                "feedback_rating": rating,
                "feedback_has_correction": bool(corrected_response)
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        if not self.logs:
            return {"total_queries": 0}
        
        total_queries = len(self.logs)
        avg_confidence = sum(l.get("confidence", 0) for l in self.logs) / total_queries
        avg_response_time = sum(l.get("response_time", 0) for l in self.logs) / total_queries
        total_tokens = sum(l.get("tokens_used", 0) for l in self.logs)
        validation_rate = sum(1 for l in self.logs if l.get("validation_passed", False)) / total_queries
        
        return {
            "total_queries": total_queries,
            "avg_confidence": avg_confidence,
            "avg_response_time": avg_response_time,
            "total_tokens": total_tokens,
            "validation_rate": validation_rate,
            "intent_distribution": self._get_intent_distribution()
        }
    
    def _get_intent_distribution(self) -> Dict[str, int]:
        """Get distribution of intents."""
        intent_counts = {}
        for log in self.logs:
            intent = log.get("intent", "unknown")
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        return intent_counts
    
    def get_recent_queries(self, n: int = 10) -> list:
        """Get n most recent queries."""
        return self.logs[-n:] if self.logs else []
    
    def export_logs(self, filepath: str = "logs_export.json"):
        """Export all logs."""
        with open(filepath, "w") as f:
            json.dump(self.logs, f, indent=2)
        return filepath
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        stats = self.get_stats()
        
        return {
            "summary": stats,
            "recent_queries": self.get_recent_queries(5),
            "timestamp": datetime.now().isoformat(),
            "project": self.project_name,
            "monitoring": "wandb" if self.use_wandb else "local"
        }