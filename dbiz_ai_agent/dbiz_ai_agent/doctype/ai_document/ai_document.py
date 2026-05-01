# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import os
import json
from datetime import datetime

class AIDocument(Document):
    def before_insert(self):
        """Set default values before inserting"""
        self.uploaded_by = frappe.session.user
        self.upload_date = datetime.now()
        
        # Set default access level if not specified
        if not self.access_level:
            self.access_level = "Internal"
        
        # Set vector collection based on access level
        if not self.vector_collection:
            self.vector_collection = self.get_collection_name()
        
        # Get file info
        if self.file_attachment:
            file_doc = frappe.get_doc("File", {"file_url": self.file_attachment})
            if file_doc:
                self.file_size = self.format_file_size(file_doc.file_size or 0)
                self.file_type = file_doc.file_type or os.path.splitext(self.file_attachment)[1]
    
    def after_insert(self):
        """Process document after insertion"""
        # Document processing is handled in upload_document() API
        # No need to queue here to avoid duplicate processing
        pass
    
    def format_file_size(self, size_in_bytes):
        """Format file size to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.2f} TB"
    
    @frappe.whitelist()
    def reprocess(self):
        """Reprocess the document"""
        self.status = "Processing"
        self.error_message = None
        self.save()

        frappe.enqueue(
            "dbiz_ai_agent.tasks.process_document",
            queue="long",
            document_name=self.name,
            now=False
        )
        
        return {"success": True, "message": "Document queued for reprocessing"}
    
    def has_permission(self, ptype="read", user=None):
        """Custom permission check combining Frappe + Chatbot permissions"""
        if not user:
            user = frappe.session.user
        
        # For new documents (no name yet), just check basic Frappe permission
        if not self.name:
            return frappe.has_permission(self.doctype, ptype, user=user)
        
        # First check standard Frappe permission using frappe.has_permission
        if not frappe.has_permission(self.doctype, ptype, self.name, user=user):
            return False
        
        # Then check chatbot-specific permissions
        try:
            from dbiz_ai_agent.api.chatbot_security import check_chatbot_access
            return check_chatbot_access("AI Document", self.name, user)
        except ImportError:
            # If chatbot permission module not available, fallback to Frappe permission
            return True
    
    def get_collection_name(self):
        """Generate collection name based on access level"""
        access_level_map = {
            "Public": "public_docs",
            "Internal": "internal_docs"
        }
        return access_level_map.get(self.access_level, "internal_docs")
    
    def get_metadata_for_vector_db(self):
        """Get metadata for Qdrant storage"""
        roles_list = []
        if self.roles_allowed:
            roles_list = [role.strip() for role in self.roles_allowed.split(",") if role.strip()]
        
        departments_list = []
        if self.departments_allowed:
            departments_list = [dept.strip() for dept in self.departments_allowed.split(",") if dept.strip()]
        
        tags_list = []
        if self.tags:
            tags_list = [tag.strip() for tag in self.tags.split(",") if tag.strip()]
        
        return {
            "doc_id": self.name,
            "frappe_doctype": "AI Document",
            "title": self.title,
            "category": self.category,
            "access_level": self.access_level,
            "roles": roles_list,
            "departments": departments_list,
            "tags": tags_list,
            "owner": self.uploaded_by or self.owner,
            "created": str(self.upload_date or self.creation),
            "collection": self.vector_collection
        }


@frappe.whitelist()
def update_access_stats(doc_name):
    """Update document access statistics"""
    doc = frappe.get_doc("AI Document", doc_name)
    doc.access_count = (doc.access_count or 0) + 1
    doc.last_accessed = datetime.now()
    doc.save(ignore_permissions=True)
    frappe.db.commit()
