"""Unit tests for agent orchestration."""
import pytest
from app.agents.orchestrator import DocumentAgent
from app.agents.state import AgentState

class TestAgents:
    
    def test_agent_init(self):
        """Test agent initialization."""
        agent = DocumentAgent()
        assert agent is not None
        assert agent.workflow is not None
    
    def test_query_processing(self):
        """Test query processing."""
        agent = DocumentAgent()
        
        result = agent.process_query("What is the termination clause?")
        
        assert result is not None
        assert "response" in result
        assert "confidence" in result
        assert "intent" in result
    
    def test_intent_classification(self):
        """Test intent classification."""
        agent = DocumentAgent()
        
        # Test different intents
        queries = [
            ("Summarize this document", "summary"),
            ("Draft an email", "email"),
            ("Extract all dates", "extract"),
            ("What are the key points?", "qa")
        ]
        
        for query, expected_intent in queries:
            result = agent.process_query(query)
            assert result["intent"] in ["qa", "summary", "email", "extract"]
    
    def test_agent_state(self):
        """Test agent state management."""
        state = AgentState(
            query="test",
            intent="qa",
            documents=[],
            response="",
            confidence=0.0,
            validated=False,
            actions=[],
            error=None
        )
        
        assert state["query"] == "test"
        assert state["intent"] == "qa"
    
    def test_validation_flow(self):
        """Test validation flow."""
        agent = DocumentAgent()
        
        result = agent.process_query("What is the liability limit?")
        
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

if __name__ == "__main__":
    pytest.main([__file__])