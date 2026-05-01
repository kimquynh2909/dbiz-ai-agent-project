import frappe
from frappe import _
from frappe.utils import cint
import json

@frappe.whitelist(allow_guest=True)
def get_roles():
    """Get all roles with statistics"""
    try:
        roles = frappe.get_all("AI Role", 
                              fields=["name", "role_name", "role_code", "description", 
                                     "is_active", "priority", "color", "icon", 
                                     "user_management", "creation", "modified"],
                              order_by="priority asc, creation desc")
        
        result = []
        for role in roles:
            role_doc = frappe.get_doc("AI Role", role.name)
            
            # Get user count for this role
            user_count = role_doc.get_user_count()
            
            # Get permission summary
            permission_summary = role_doc.get_permission_summary()
            
            result.append({
                "name": role.name,  # Changed from "id" to "name" for consistency
                "id": role.name,  # Keep "id" for backwards compatibility
                "role_name": role.role_name,
                "role_code": role.role_code,
                "description": role.description,
                "is_active": role.is_active,
                "priority": role.priority,
                "color": role.color or "#6b7280",
                "icon": role.icon or role.role_name[0].upper(),
                "user_count": user_count,
                "user_management": role.user_management,
                "permissions": permission_summary,
                "creation": role.creation,
                "modified": role.modified
            })
        
        return {
            "success": True,
            "data": result,
            "total": len(result)
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting roles: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist(allow_guest=True)
def create_role(role_data):
    """Create a new role"""
    try:
        if isinstance(role_data, str):
            role_data = json.loads(role_data)
        
        # Validate required fields
        required_fields = ["role_name"]
        for field in required_fields:
            if not role_data.get(field):
                frappe.throw(_("Field {0} is required").format(field))
        
        # Check if role name already exists
        existing = frappe.get_all("AI Role", filters={"role_name": role_data["role_name"]})
        if existing:
            frappe.throw(_("Role with name {0} already exists").format(role_data["role_name"]))
        
        # Create role document
        role_doc = frappe.get_doc({
            "doctype": "AI Role",
            "role_name": role_data["role_name"],
            "description": role_data.get("description", ""),
            "is_active": role_data.get("is_active", True),
            "priority": role_data.get("priority", 1),
            "color": role_data.get("color", "#6b7280"),
            "icon": role_data.get("icon", role_data["role_name"][0].upper()),
            "user_management": role_data.get("user_management", False)
        })
        
        # Permissions will be handled in future versions
        
        role_doc.insert()
        
        return {
            "success": True,
            "message": f"Role '{role_data['role_name']}' created successfully",
            "data": {
                "id": role_doc.name,
                "role_name": role_doc.role_name,
                "role_code": role_doc.role_code
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating role: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist(allow_guest=True)
def update_role(role_id, role_data):
    """Update an existing role"""
    try:
        if isinstance(role_data, str):
            role_data = json.loads(role_data)
        
        # Get existing role
        role_doc = frappe.get_doc("AI Role", role_id)
        old_name = role_doc.name
        new_role_name = role_data.get("role_name")
        
        # Check if role_name is being changed
        if new_role_name and new_role_name != old_name:
            # Validate new name doesn't exist
            if frappe.db.exists("AI Role", new_role_name):
                frappe.throw(_("Role with name '{0}' already exists").format(new_role_name))
            
            # Update role_name first
            role_doc.role_name = new_role_name
            role_doc.save()
            
            # Rename the document (this also updates all links automatically)
            frappe.rename_doc("AI Role", old_name, new_role_name, force=True, merge=False)
            
            # Reload the document with new name
            role_doc = frappe.get_doc("AI Role", new_role_name)
            role_id = new_role_name  # Update role_id for further operations
        
        # Update other fields
        if "description" in role_data:
            role_doc.description = role_data["description"]
        if "is_active" in role_data:
            role_doc.is_active = role_data["is_active"]
        if "priority" in role_data:
            role_doc.priority = role_data["priority"]
        if "color" in role_data:
            role_doc.color = role_data["color"]
        if "icon" in role_data:
            role_doc.icon = role_data["icon"]
        if "user_management" in role_data:
            role_doc.user_management = role_data["user_management"]
        
        # Permissions will be handled in future versions
        
        role_doc.save()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Role '{role_doc.role_name}' updated successfully",
            "data": {
                "id": role_doc.name,
                "role_name": role_doc.role_name,
                "role_code": role_doc.role_code
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error updating role: {str(e)}")
        frappe.db.rollback()
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist(allow_guest=True)
def delete_role(role_id):
    """Delete a role"""
    try:
        role_doc = frappe.get_doc("AI Role", role_id)
        role_name = role_doc.role_name
        
        # Check if role has users assigned
        user_count = frappe.db.count(
            "Users Allowed",
            {
                "parent": role_id,
                "parenttype": "AI Role",
                "parentfield": "users_allowed"
            }
        )
        if user_count > 0:
            frappe.throw(_("Cannot delete role '{0}' because it has {1} users assigned").format(role_name, user_count))
        
        role_doc.delete()
        
        return {
            "success": True,
            "message": f"Role '{role_name}' deleted successfully"
        }
        
    except Exception as e:
        frappe.log_error(f"Error deleting role: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist(allow_guest=True)
def get_role_details(role_id):
    """Get detailed information about a specific role"""
    try:
        role_doc = frappe.get_doc("AI Role", role_id)
        
        # Get user count
        user_count = role_doc.get_user_count()
        
        # Get permission summary
        permission_summary = role_doc.get_permission_summary()
        
        # Build users list from child table assignments
        user_links = [
            row for row in (role_doc.get("users_allowed") or [])
            if getattr(row, "user", None)
        ]

        users = []
        if user_links:
            user_ids = [row.user for row in user_links]
            user_docs = {
                user.name: user
                for user in frappe.get_all(
                    "User",
                    filters={"name": ["in", user_ids]},
                    fields=["name", "full_name", "email", "enabled", "last_login"]
                )
            }

            for row in user_links:
                user_row = user_docs.get(row.user)
                if not user_row:
                    continue

                users.append({
                    "name": user_row.get("name"),
                    "full_name": user_row.get("full_name"),
                    "email": user_row.get("email"),
                    "enabled": user_row.get("enabled"),
                    "last_login": user_row.get("last_login"),
                    "assigned_via_role": role_doc.role_name,
                    "is_role_active": bool(role_doc.is_active),
                    "assignment_active": bool(getattr(row, "is_active", 1)),
                })
        
        return {
            "success": True,
            "data": {
                "id": role_doc.name,
                "role_name": role_doc.role_name,
                "role_code": role_doc.role_code,
                "description": role_doc.description,
                "is_active": role_doc.is_active,
                "priority": role_doc.priority,
                "color": role_doc.color,
                "icon": role_doc.icon,
                "user_management": role_doc.user_management,
                "user_count": user_count,
                "permissions": permission_summary,
                "document_permissions": [],
                "database_permissions": [],
                "api_permissions": [],
                "users": users,
                "creation": role_doc.creation,
                "modified": role_doc.modified
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting role details: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist(allow_guest=True)
def toggle_role_status(role_id, is_active):
    """Toggle role active status"""
    try:
        role_doc = frappe.get_doc("AI Role", role_id)
        new_status = cint(is_active)
        role_doc.db_set('is_active', new_status)

        return {
            "success": True,
            "message": f"Role '{role_doc.role_name}' {'activated' if new_status else 'deactivated'} successfully",
            "data": {
                "id": role_doc.name,
                "is_active": bool(new_status)
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error toggling role status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist(allow_guest=True)
def get_role_statistics():
    """Get overall role statistics"""
    try:
        total_roles = frappe.db.count("AI Role")
        active_roles = frappe.db.count("AI Role", {"is_active": 1})
        total_users = frappe.db.count("User", {"enabled": 1})
        protected_docs = frappe.db.count(
            "AI Document",
            {"access_level": "Internal"}
        )

        database_name = frappe.db.sql("SELECT DATABASE()")[0][0]
        database_tables = frappe.db.sql(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = %s
            """,
            database_name
        )[0][0]

        # Get role distribution
        role_stats = frappe.db.sql("""
            SELECT 
                ar.role_name,
                ar.is_active,
                COUNT(ua.name) as user_count
            FROM `tabAI Role` ar
            LEFT JOIN `tabUsers Allowed` ua
                ON ua.parent = ar.name
                AND ua.parenttype = 'AI Role'
                AND ua.parentfield = 'users_allowed'
                AND (ua.is_active = 1 OR ua.is_active IS NULL)
            GROUP BY ar.name, ar.role_name, ar.is_active
            ORDER BY user_count DESC
        """, as_dict=True)
        
        return {
            "success": True,
            "data": {
                "total_roles": total_roles,
                "active_roles": active_roles,
                "total_users": total_users,
                "protected_docs": protected_docs,
                "database_tables": database_tables,
                "role_distribution": role_stats
            }
        }

    except Exception as e:
        frappe.log_error(f"Error getting role statistics: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
