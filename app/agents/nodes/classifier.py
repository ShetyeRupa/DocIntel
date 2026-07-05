"""Intent classification node for DocIntel."""
from app.agents.state import AgentState
from app.config import settings
import json

try:
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
except ImportError:
    client = None

def classify_intent(state: AgentState) -> AgentState:
    """Classify user intent"""
    print(f"📋 Classifying intent for: {state['query']}")
    
    # Simple keyword-based classification first (faster, no API call)
    query = state["query"].lower()
    
    # Check for summary intent
    summary_keywords = ["summarize", "summary", "brief", "overview", "summarise"]
    if any(word in query for word in summary_keywords):
        state["intent"] = "summary"
        print(f"✅ Intent: summary (keyword match)")
        return state
    
    # Check for email intent
    email_keywords = ["email", "draft", "send", "compose", "write an email"]
    if any(word in query for word in email_keywords):
        state["intent"] = "email"
        print(f"✅ Intent: email (keyword match)")
        return state
    
    # Check for extraction intent
    extract_keywords = [
        "extract", "list", "find", "show me", 
        "what are", "dates", "amounts", "numbers",
        "entities", "names", "people", "organizations"
    ]
    if any(word in query for word in extract_keywords):
        state["intent"] = "extract"
        print(f"✅ Intent: extract (keyword match)")
        return state
    
    # Use LLM fallback for better classification
    if client is not None:
        try:
            prompt = f"""
            Analyze this user query and classify it into one of these intents:
            
            1. "qa" - General question about document content
            2. "summary" - Request for document summary
            3. "email" - Need to draft an email based on documents
            4. "extract" - Need specific data extraction (dates, amounts, names, etc.)
            
            Query: {state["query"]}
            
            Return ONLY a JSON object with:
            {{
                "intent": "category",
                "reasoning": "brief explanation"
            }}
            """
            
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            state["intent"] = result.get("intent", "qa")
            print(f"✅ Intent: {state['intent']} (LLM)")
            
        except Exception as e:
            print(f"⚠️ Classification error: {e}")
            state["intent"] = "qa"
            state["error"] = str(e)
    else:
        # Default to Q&A if no client
        state["intent"] = "qa"
        print(f"✅ Intent: qa (no LLM client)")
    
    return state