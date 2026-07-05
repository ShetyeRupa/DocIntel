from typing import TypedDict, List, Optional, Dict, Any

class AgentState(TypedDict):
    """State for the LangGraph agent"""
    query: str
    intent: str  # "qa", "summary", "email", "extract"
    documents: List[Dict[str, Any]]
    response: str
    confidence: float
    validated: bool
    actions: List[str]
    error: Optional[str]