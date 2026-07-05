"""Test suite for DocIntel evaluation."""
import json
from typing import List, Dict, Any
from app.agents.orchestrator import DocumentAgent

class TestSuite:
    """Comprehensive test suite for evaluating DocIntel performance."""
    
    def __init__(self):
        self.agent = DocumentAgent()
        self.test_queries = self._load_test_queries()
        self.results = []
    
    def _load_test_queries(self) -> List[Dict[str, Any]]:
        """Load test queries with ground truth."""
        return [
            # Q&A Tests
            {
                "query": "What is the termination clause in this contract?",
                "intent": "qa",
                "ground_truth": "Either party may terminate with 30 days written notice.",
                "context": "Contract with termination clause"
            },
            {
                "query": "What are the payment terms?",
                "intent": "qa",
                "ground_truth": "Net 30 days from invoice date.",
                "context": "Payment terms"
            },
            {
                "query": "What is the liability limit?",
                "intent": "qa",
                "ground_truth": "Limited to total contract value.",
                "context": "Liability provisions"
            },
            {
                "query": "What are the key provisions of this document?",
                "intent": "qa",
                "ground_truth": "Termination, payment, liability, and confidentiality.",
                "context": "Key provisions"
            },
            {
                "query": "What is the effective date?",
                "intent": "qa",
                "ground_truth": "January 1, 2026.",
                "context": "Effective date"
            },
            
            # Summary Tests
            {
                "query": "Summarize this document in three paragraphs.",
                "intent": "summary",
                "ground_truth": "Summary of key points in 3 paragraphs.",
                "context": "Document summary"
            },
            {
                "query": "Provide an executive summary of this report.",
                "intent": "summary",
                "ground_truth": "Executive summary with key findings.",
                "context": "Executive summary"
            },
            {
                "query": "What are the main findings?",
                "intent": "summary",
                "ground_truth": "Main findings and conclusions.",
                "context": "Main findings"
            },
            
            # Extraction Tests
            {
                "query": "Extract all dates from this document.",
                "intent": "extract",
                "ground_truth": ["2026-01-15", "2026-02-01", "2026-03-01"],
                "context": "Date extraction"
            },
            {
                "query": "What are the monetary amounts?",
                "intent": "extract",
                "ground_truth": ["$500,000", "$50,000", "$10,000"],
                "context": "Amount extraction"
            },
            {
                "query": "List all the names of individuals mentioned.",
                "intent": "extract",
                "ground_truth": ["John Smith", "Jane Doe", "Robert Johnson"],
                "context": "Name extraction"
            },
            
            # Email Tests
            {
                "query": "Draft an email summarizing this proposal.",
                "intent": "email",
                "ground_truth": "Professional email with proposal summary.",
                "context": "Email drafting"
            },
            {
                "query": "Write an email to my team about this document.",
                "intent": "email",
                "ground_truth": "Team email with document details.",
                "context": "Team communication"
            }
        ]
    
    def run_all(self) -> Dict[str, Any]:
        """Run all test queries."""
        results = []
        passed = 0
        total = len(self.test_queries)
        
        for test in self.test_queries:
            result = self._run_single(test)
            results.append(result)
            if result["passed"]:
                passed += 1
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "accuracy": passed / total if total > 0 else 0,
            "results": results
        }
    
    def _run_single(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test query."""
        try:
            response = self.agent.process_query(test["query"])
            
            # Basic validation
            passed = bool(response.get("response") and response.get("confidence", 0) > 0.5)
            
            return {
                "query": test["query"],
                "intent": test["intent"],
                "response": response.get("response", ""),
                "confidence": response.get("confidence", 0),
                "passed": passed,
                "has_sources": bool(response.get("sources", [])),
                "response_time": response.get("response_time", 0),
                "error": response.get("error")
            }
            
        except Exception as e:
            return {
                "query": test["query"],
                "intent": test["intent"],
                "response": "",
                "confidence": 0,
                "passed": False,
                "has_sources": False,
                "response_time": 0,
                "error": str(e)
            }
    
    def export_results(self, filepath: str = "evaluation_results.json"):
        """Export test results to JSON file."""
        results = self.run_all()
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        return filepath
    
    def print_summary(self):
        """Print summary of test results."""
        results = self.run_all()
        
        print("\n" + "="*60)
        print("📊 DOCINTEL EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Tests: {results['total']}")
        print(f"Passed:      {results['passed']}")
        print(f"Failed:      {results['failed']}")
        print(f"Accuracy:    {results['accuracy']*100:.1f}%")
        print("-"*60)
        
        for result in results['results']:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"{status} | {result['query'][:40]}... | Confidence: {result['confidence']:.2f}")
        
        print("="*60)