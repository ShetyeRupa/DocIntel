"""Data extraction tool for structured information from documents."""
from groq import Groq
from app.config import settings
from typing import List, Dict, Any, Optional
import re

class DataExtractor:
    """Extract structured data from document text."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.patterns = {
            'dates': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            'amounts': r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'percentages': r'\d+(?:\.\d+)?%',
        }
    
    def extract_by_regex(self, text: str, pattern_type: str) -> List[str]:
        """Extract data using regex patterns."""
        pattern = self.patterns.get(pattern_type)
        if not pattern:
            return []
        
        matches = re.findall(pattern, text)
        return list(set(matches))  # Remove duplicates
    
    def extract_entities(self, text: str, entity_types: List[str]) -> Dict[str, Any]:
        """
        Extract entities from text using LLM.
        
        Args:
            text: Document text to extract from
            entity_types: List of entity types to extract
                (dates, amounts, names, organizations, products, etc.)
        
        Returns:
            Dict with extracted entities
        """
        prompt = f"""
        Extract the following entities from the text below:
        {', '.join(entity_types)}
        
        Text:
        {text}
        
        Return ONLY a JSON object with:
        {{
            "entities": [
                {{
                    "type": "entity_type",
                    "value": "extracted_value",
                    "context": "surrounding text"
                }}
            ],
            "summary": "Brief summary of findings"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "entities": [],
                "summary": f"Error extracting entities: {str(e)}",
                "error": str(e)
            }
    
    def extract_financial_data(self, text: str) -> Dict[str, Any]:
        """Extract financial information from documents."""
        
        prompt = f"""
        Extract financial information from the following text.
        
        Text:
        {text}
        
        Return JSON with:
        {{
            "amounts": [{"value": 10000.00, "currency": "USD", "context": "Payment amount"}],
            "dates": [{"date": "2026-01-15", "context": "Due date"}],
            "total": 500000.00,
            "terms": ["Net 30", "1.5% late fee"],
            "summary": "Financial summary"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "amounts": [],
                "dates": [],
                "total": 0,
                "terms": [],
                "summary": f"Error: {str(e)}"
            }
    
    def extract_contract_clauses(self, text: str) -> Dict[str, Any]:
        """Extract contract clauses and provisions."""
        
        prompt = f"""
        Extract key contract clauses from the following text.
        
        Text:
        {text}
        
        Return JSON with:
        {{
            "termination": "Termination clause content",
            "payment": "Payment terms",
            "liability": "Liability provisions",
            "confidentiality": "Confidentiality clause",
            "governing_law": "Governing law",
            "dispute_resolution": "Dispute resolution mechanism",
            "other_clauses": ["List other important clauses"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "termination": f"Error: {str(e)}",
                "payment": "",
                "liability": "",
                "confidentiality": "",
                "governing_law": "",
                "dispute_resolution": "",
                "other_clauses": []
            }
    
    def extract_dates_timeline(self, text: str) -> List[Dict[str, str]]:
        """Extract dates and create a timeline."""
        
        prompt = f"""
        Extract all dates and create a timeline from the following text.
        
        Text:
        {text}
        
        Return JSON with:
        {{
            "timeline": [
                {{
                    "date": "2026-01-15",
                    "event": "Event description",
                    "context": "Surrounding text"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get("timeline", [])
            
        except Exception as e:
            return [{"date": "Error", "event": str(e), "context": ""}]
    
    def extract_key_people(self, text: str) -> List[Dict[str, str]]:
        """Extract names and roles of key individuals."""
        
        prompt = f"""
        Extract names, roles, and organizations of key individuals from the text.
        
        Text:
        {text}
        
        Return JSON with:
        {{
            "people": [
                {{
                    "name": "Full name",
                    "role": "Position or title",
                    "organization": "Company or institution",
                    "context": "Mention context"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get("people", [])
            
        except Exception as e:
            return [{"name": "Error", "role": str(e), "organization": "", "context": ""}]