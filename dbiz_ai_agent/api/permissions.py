import frappe
from frappe import _

@frappe.whitelist()
def get_user_permissions():
    """Get current user permissions for AI Agent"""
    user = frappe.session.user
    
    if user == "Administrator":
        return [
            "view_dashboard",
            "use_chat", 
            "upload_documents",
            "delete_documents",
            "manage_users",
            "change_settings"
        ]
    
    # Get user roles
    user_roles = frappe.get_roles(user)
    permissions = []
    
    # Basic permissions for all users
    permissions.append("view_dashboard")
    permissions.append("use_chat")
    
    # Role-based permissions
    if "AI Agent Admin" in user_roles or "System Manager" in user_roles:
        permissions.extend([
            "upload_documents",
            "delete_documents", 
            "manage_users",
            "change_settings"
        ])
    elif "AI Agent User" in user_roles:
        permissions.append("upload_documents")
    
    return permissions

@frappe.whitelist()
def check_permission(permission):
    """Check if current user has specific permission"""
    user_permissions = get_user_permissions()
    return permission in user_permissions
