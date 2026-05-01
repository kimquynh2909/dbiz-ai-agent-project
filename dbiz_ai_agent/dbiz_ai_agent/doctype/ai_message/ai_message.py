# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

class AIMessage(Document):
    def before_insert(self):
        """Set default values before inserting"""
        if not self.timestamp:
            self.timestamp = datetime.now()
    
    @frappe.whitelist()
    def set_feedback(self, helpful):
        """Set feedback for the message"""
        self.feedback = "Helpful" if helpful else "Not Helpful"
        self.save()
        return {"success": True}
