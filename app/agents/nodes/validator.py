"""Validation node for DocIntel."""
from app.agents.state import AgentState
from app.config import settings

def validate_response(state: AgentState) -> AgentState:
    """Validate response and calculate confidence"""
    print("🔍 Validating response...")
    
    response = state.get("response", "")
    documents = state.get("documents", [])
    current_confidence = state.get("confidence", 0.0)
    
    if not response:
        state["validated"] = False
        state["confidence"] = 0.0
        print("❌ No response to validate")
        return state
    
    # Factor 1: Document relevance (40% weight)
    doc_scores = [d.get("score", 0) for d in documents[:3]]
    avg_doc_score = sum(doc_scores) / len(doc_scores) if doc_scores else 0
    
    # Factor 2: Response length (20% weight) - longer responses indicate more content
    length_score = min(1.0, len(response) / 500)  # Cap at 500 chars
    
    # Factor 3: Number of sources (20% weight)
    source_score = min(1.0, len(documents) / settings.TOP_K) if documents else 0
    
    # Factor 4: Confidence from retrieval (20% weight)
    retrieval_score = min(1.0, current_confidence * 2)  # Scale up
    
    # Calculate weighted confidence
    confidence = (
        avg_doc_score * 0.40 +
        length_score * 0.20 +
        source_score * 0.20 +
        retrieval_score * 0.20
    )
    
    # Cap at 0.95
    confidence = min(0.95, confidence)
    
    # If no documents, low confidence
    if not documents:
        confidence = 0.1
    
    state["confidence"] = confidence
    state["validated"] = confidence > 0.3  # Threshold for validation
    
    print(f"✅ Confidence: {confidence:.3f} (doc: {avg_doc_score:.2f}, len: {length_score:.2f}, src: {source_score:.2f}, ret: {retrieval_score:.2f})")
    
    return state