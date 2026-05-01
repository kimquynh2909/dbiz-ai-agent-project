# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AIAgentSettings(Document):
    def validate(self):
        """Validate settings"""
        if self.temperature and (self.temperature < 0 or self.temperature > 1):
            frappe.throw("Temperature must be between 0 and 1")
        
        if self.max_tokens and self.max_tokens < 1:
            frappe.throw("Max tokens must be greater than 0")
        
        if self.chunk_size and self.chunk_size < 100:
            frappe.throw("Chunk size must be at least 100")
    
    def before_save(self):
        # Only process secret_key if it exists in the doctype
        if hasattr(self, 'secret_key') and self.secret_key:
            self.secret_key = self.secret_key.strip()
    
    @frappe.whitelist()
    def test_openai_connection(self):
        """Test OpenAI API connection"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            # Test with a simple completion
            response = openai.ChatCompletion.create(
                model=self.model or "gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {"success": True, "message": "Connection successful"}
        except Exception as e:
            return {"success": False, "message": str(e)}
