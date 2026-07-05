"""Cost tracking for DocIntel operations."""
import json
from typing import Dict, Any
from datetime import datetime
import os

class CostTracker:
    """Track operational costs for DocIntel (zero cost implementation)."""
    
    def __init__(self):
        self.cost_data = {
            "total_tokens": 0,
            "total_requests": 0,
            "cost_by_model": {},
            "cost_per_query": {},
            "total_cost": 0.0
        }
        self.log_file = "cost_log.json"
        self._load_data()
    
    def _load_data(self):
        """Load existing cost data."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    self.cost_data = json.load(f)
            except:
                pass
    
    def _save_data(self):
        """Save cost data to file."""
        with open(self.log_file, "w") as f:
            json.dump(self.cost_data, f, indent=2)
    
    def track_request(self, query: str, tokens: int, model: str = "groq"):
        """Track a single request."""
        self.cost_data["total_tokens"] += tokens
        self.cost_data["total_requests"] += 1
        
        # Since we're using free tier, cost is zero
        # But we track it for transparency
        if model not in self.cost_data["cost_by_model"]:
            self.cost_data["cost_by_model"][model] = {
                "tokens": 0,
                "cost": 0.0
            }
        
        self.cost_data["cost_by_model"][model]["tokens"] += tokens
        self.cost_data["cost_by_model"][model]["cost"] = 0.0  # Free tier
        
        # Track per query
        query_id = f"q_{self.cost_data['total_requests']}"
        self.cost_data["cost_per_query"][query_id] = {
            "query": query[:50] + "..." if len(query) > 50 else query,
            "tokens": tokens,
            "cost": 0.0,  # Free tier
            "model": model,
            "timestamp": datetime.now().isoformat()
        }
        
        self._save_data()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        return {
            "total_requests": self.cost_data["total_requests"],
            "total_tokens": self.cost_data["total_tokens"],
            "total_cost": self.cost_data["total_cost"],
            "cost_by_model": self.cost_data["cost_by_model"],
            "cost_per_1000_tokens": 0.0,  # Free tier
            "cost_per_query": 0.0,  # Free tier
            "monthly_estimate": 0.0  # Free tier
        }
    
    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get detailed cost breakdown."""
        return {
            "summary": self.get_summary(),
            "recent_queries": list(self.cost_data["cost_per_query"].values())[-10:],
            "free_tier_status": "Active",
            "free_tier_limit": "30 requests/minute",
            "free_tier_remaining": "Unlimited (free tier)"
        }
    
    def reset(self):
        """Reset cost tracking."""
        self.cost_data = {
            "total_tokens": 0,
            "total_requests": 0,
            "cost_by_model": {},
            "cost_per_query": {},
            "total_cost": 0.0
        }
        self._save_data()
    
    def export_report(self, filepath: str = "cost_report.json"):
        """Export cost report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cost_data": self.cost_data,
            "summary": self.get_summary()
        }
        
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
        
        return filepath