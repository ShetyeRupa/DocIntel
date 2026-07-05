"""Main orchestrator for document intelligence."""
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import classify_intent, retrieve_documents, generate_response, validate_response

class DocumentAgent:
    """Main orchestrator for document intelligence"""
    
    def __init__(self):
        self.workflow = self._build_workflow()
        self.agent = self.workflow.compile()
    
    def _build_workflow(self):
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify", classify_intent)
        workflow.add_node("retrieve", retrieve_documents)
        workflow.add_node("generate", generate_response)
        workflow.add_node("validate", validate_response)
        
        # Set entry point
        workflow.set_entry_point("classify")
        
        # Define edges based on intent
        workflow.add_conditional_edges(
            "classify",
            self._route_intent,
            {
                "qa": "retrieve",
                "summary": "retrieve", 
                "email": "generate",
                "extract": "retrieve"
            }
        )
        
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", "validate")
        workflow.add_edge("validate", END)
        
        return workflow
    
    def _route_intent(self, state: AgentState) -> str:
        """Route based on intent"""
        intent = state.get("intent", "qa")
        print(f"🔀 Routing intent: {intent}")
        
        if intent == "email":
            return "email"
        elif intent in ["qa", "summary", "extract"]:
            return "qa"
        else:
            return "qa"
    
    def process_query(self, query: str) -> dict:
        """Process a user query"""
        print(f"🔍 Processing query: {query}")
        
        initial_state = {
            "query": query,
            "intent": "",
            "documents": [],
            "response": "",
            "confidence": 0.0,
            "validated": False,
            "actions": [],
            "error": None
        }
        
        try:
            result = self.agent.invoke(initial_state)
            
            print(f"📊 Intent: {result.get('intent')}")
            print(f"📄 Documents retrieved: {len(result.get('documents', []))}")
            print(f"📝 Response length: {len(result.get('response', ''))}")
            
            return {
                "query": query,
                "response": result.get("response", ""),
                "confidence": result.get("confidence", 0),
                "sources": result.get("documents", []),
                "intent": result.get("intent", "unknown"),
                "error": result.get("error")
            }
        except Exception as e:
            print(f"❌ Agent error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "query": query,
                "response": f"Error: {str(e)}",
                "confidence": 0,
                "sources": [],
                "intent": "error",
                "error": str(e)
            }
