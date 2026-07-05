"""Retrieval node for DocIntel."""
from app.agents.state import AgentState
from app.vector_store.retriever import Retriever
from app.config import settings

retriever = Retriever()

def retrieve_documents(state: AgentState) -> AgentState:
    """Retrieve relevant documents"""
    try:
        print(f"🔍 Searching for: {state['query']}")
        results = retriever.hybrid_search(state["query"], k=settings.TOP_K)
        print(f"📄 Found {len(results)} documents")
        
        state["documents"] = results
        
        if results:
            # Calculate confidence with better scaling
            scores = [r.get("score", 0) for r in results]
            avg_score = sum(scores) / len(scores)
            
            # Scale confidence: if avg_score < 0.3, scale it up to show some confidence
            # but still reflect that it's not a great match
            if avg_score < 0.3:
                # For very low scores, scale to 0-30% range
                confidence = avg_score * 1.0  # Keep as is but show as percentage
            else:
                confidence = min(0.95, avg_score)
            
            state["confidence"] = confidence
            print(f"🎯 Average score: {avg_score:.3f}, Confidence: {confidence:.3f}")
        else:
            state["confidence"] = 0.0
            
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        state["documents"] = []
        state["confidence"] = 0.0
        state["error"] = str(e)
    
    return state
