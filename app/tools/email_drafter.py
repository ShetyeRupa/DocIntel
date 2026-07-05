"""Email drafting tool for DocIntel."""
from groq import Groq
from app.config import settings
from typing import List, Dict, Any

class EmailDrafter:
    """Generate professional emails based on document context."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def draft_email(
        self,
        context: str,
        recipient: str = "client",
        purpose: str = "summary",
        tone: str = "professional"
    ) -> Dict[str, str]:
        """
        Draft a professional email based on document context.
        
        Args:
            context: Document excerpts or summaries
            recipient: Recipient type (client, team, manager, etc.)
            purpose: Email purpose (summary, proposal, follow-up, etc.)
            tone: Email tone (professional, friendly, formal)
            
        Returns:
            Dict with subject, body, and suggested actions
        """
        prompt = f"""
        Draft a professional email based on the following document context.
        
        Context:
        {context}
        
        Email Details:
        - Recipient: {recipient}
        - Purpose: {purpose}
        - Tone: {tone}
        
        Generate an email with:
        1. A clear subject line
        2. Professional greeting
        3. Body that summarizes key information
        4. Clear call to action
        5. Professional closing
        
        Return a JSON with:
        {{
            "subject": "Email subject line",
            "greeting": "Dear [recipient],",
            "body": "Main email content...",
            "closing": "Best regards,",
            "call_to_action": "Clear next step"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Combine into full email
            full_email = f"""
    Subject: {result.get('subject', 'Document Update')}
    
    {result.get('greeting', 'Dear Team,')}
    
    {result.get('body', '')}
    
    {result.get('call_to_action', 'Please review the attached document.')}
    
    {result.get('closing', 'Best regards,')}
    DocIntel AI Assistant
            """.strip()
            
            return {
                "subject": result.get('subject', 'Document Update'),
                "body": result.get('body', ''),
                "full_email": full_email,
                "call_to_action": result.get('call_to_action', ''),
                "suggested_actions": [
                    "Review the summarized points",
                    "Respond with questions",
                    "Schedule a follow-up meeting"
                ]
            }
            
        except Exception as e:
            return {
                "subject": "Document Summary",
                "body": f"Unable to draft email: {str(e)}",
                "full_email": f"Error: {str(e)}",
                "call_to_action": "Please try again",
                "suggested_actions": []
            }
    
    def generate_follow_up(
        self,
        original_email: str,
        recipient: str = "client"
    ) -> Dict[str, str]:
        """Generate a follow-up email based on previous correspondence."""
        
        prompt = f"""
        Generate a professional follow-up email based on this original email.
        
        Original Email:
        {original_email}
        
        Follow-up should:
        - Be polite and professional
        - Reference the original communication
        - Request necessary actions
        - Suggest next steps
        
        Return JSON with same format as the draft_email function.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=600
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            full_email = f"""
    Subject: {result.get('subject', 'Follow-Up: Document Update')}
    
    {result.get('greeting', 'Dear Team,')}
    
    {result.get('body', '')}
    
    {result.get('call_to_action', 'I look forward to your response.')}
    
    {result.get('closing', 'Best regards,')}
    DocIntel AI Assistant
            """.strip()
            
            return {
                "subject": result.get('subject', 'Follow-Up: Document Update'),
                "body": result.get('body', ''),
                "full_email": full_email,
                "call_to_action": result.get('call_to_action', 'Please respond at your earliest convenience.'),
                "suggested_actions": [
                    "Review previous communication",
                    "Prepare required information",
                    "Schedule a call if needed"
                ]
            }
            
        except Exception as e:
            return {
                "subject": "Follow-Up",
                "body": f"Unable to generate follow-up: {str(e)}",
                "full_email": f"Error: {str(e)}",
                "call_to_action": "Please try again",
                "suggested_actions": []
            }