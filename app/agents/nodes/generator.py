"""Response generation node for DocIntel."""
from app.agents.state import AgentState
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_response(state: AgentState) -> AgentState:
    """Generate response based on retrieved documents"""
    
    # Build context from retrieved documents
    context = ""
    if state.get("documents"):
        print(f"📄 Generating response with {len(state['documents'])} documents")
        for i, doc in enumerate(state["documents"][:3]):
            doc_text = doc.get("document", "")
            if doc_text:
                context += f"\n[Source {i+1}]:\n{doc_text}\n"
    else:
        print("⚠️ No documents retrieved - using fallback")
        context = "No specific documents found for this query."
    
    # Build prompt based on intent
    intent = state.get("intent", "qa")
    query = state.get("query", "")
    
    if intent == "summary":
        prompt = f"""
        Generate a concise executive summary of these documents.
        
        Documents:
        {context}
        
        Summary should:
        - Highlight key points
        - Be 2-3 paragraphs
        - Include main conclusions
        - If no documents, say so clearly
        """
    elif intent == "email":
        prompt = f"""
        Draft a professional email based on these documents:
        {context}
        
        Email should:
        - Have a clear subject line
        - Be professional and concise
        - Include key information
        - End with appropriate call to action
        """
    elif intent == "extract":
        prompt = f"""
        Extract all relevant entities and data from these documents:
        {context}
        
        Extract:
        - Dates
        - Monetary amounts
        - Names
        - Key numbers
        - Important facts
        """
    else:  # qa
        prompt = f"""
        Answer the user's question based on the documents below.
        If the answer is not in the documents, say so clearly.
        
        User Question: {query}
        
        Documents:
        {context}
        
        Provide a clear, accurate answer. If you use specific information, cite the source number.
        """
    
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        state["response"] = response.choices[0].message.content
        print(f"✅ Response generated: {len(state['response'])} characters")
        
    except Exception as e:
        print(f"❌ Generation error: {e}")
        state["response"] = f"I encountered an error generating the response. Please try again. Error: {str(e)}"
        state["error"] = str(e)
    
    return state
