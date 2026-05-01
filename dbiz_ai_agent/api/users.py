import frappe
from frappe import _
from frappe.utils import validate_email_address, cint, flt
from frappe.utils.password import update_password
import json

def get_contact_of_user(user: str):
    # Try to find contact by user field first, then by email_id
    contact_name = frappe.db.get_value("Contact", {"user": user}, "name")
    if not contact_name:
        contact_name = frappe.db.get_value("Contact", {"email_id": user}, "name")
    return frappe.get_doc("Contact", contact_name) if contact_name else None

@frappe.whitelist()
def get_users(page: int = 1, page_size: int = 20,
            order_by: str = "full_name desc", search_key: str | None = None):
    page = cint(page) or 1
    page_size = cint(page_size) or 20
    offset = (page - 1) * page_size
    users = []

    _users = frappe.get_all(
        "User",
        fields=["name", "full_name", "email", "last_login", "enabled"],
        filters=[
            ["name", "not in", ["Administrator", "Guest"]]
        ],
        order_by=order_by,
        limit_start=offset,
        limit_page_length=page_size
    )
    
    # Get all AI Roles with their users_allowed to build a mapping
    all_roles = frappe.get_all(
        "AI Role",
        fields=["name", "role_name", "role_code", "is_active", "priority", "color"],
        filters={"is_active": 1}
    )
    
    # Build a map: user_email -> list of roles
    user_roles_map = {}
    for role in all_roles:
        try:
            role_doc = frappe.get_doc("AI Role", role.name)
            for user_allowed_row in (role_doc.get("users_allowed") or []):
                user_email = getattr(user_allowed_row, "user", None)
                if not user_email:
                    continue
                
                # Check if user_allowed is active
                is_user_active = getattr(user_allowed_row, "is_active", 1)
                if not is_user_active:
                    continue
                
                if user_email not in user_roles_map:
                    user_roles_map[user_email] = []
                
                user_roles_map[user_email].append({
                    "role_name": role.role_name,
                    "role_code": role.role_code,
                    "name": role.name,
                    "is_active": role.is_active,
                    "priority": role.priority or 9999,
                    "color": role.color
                })
        except Exception as e:
            frappe.log_error(f"Error loading role {role.name}: {str(e)}", "Get Users - Load Role")
            continue
    
    for user in _users:
        user_email = user.get("email")
        user_id = user.get("name")
        
        # Get roles from AI Role.users_allowed mapping
        user_roles = user_roles_map.get(user_email, [])
        
        # Sort roles by priority and is_active
        ordered_roles = sorted(
            user_roles,
            key=lambda role: (0 if role.get("is_active") else 1, role.get("priority") or 9999, role.get("role_name") or "")
        )
        
        # Get contact for department (if exists)
        contacts = get_contact_of_user(user_email)
        
        users.append({
            "id": user_id,
            "full_name": user.get("full_name"),
            "email": user_email,
            "last_login": user.get("last_login"),
            "enabled": user.get("enabled"),
            "department": contacts.department if contacts else None,
            "ai_roles": ordered_roles if ordered_roles else []
        })
    
    print("Users:", users)
    pagination = {
        'page': page,
        'page_size': page_size,
    }

    return {'success': True, 'data': {'users': users, 'pagination': pagination}}

@frappe.whitelist()
def get_user_detail(user_id):
    """Get detailed information of a specific user"""
    try:
        if not user_id:
            frappe.throw(_("User ID is required"))
        # Check if user exists
        if not frappe.db.exists("User", user_id):
            frappe.throw(_("User not found"))
        
        # Get user document
        user_doc = frappe.get_doc("User", user_id)
        
        # Get AI roles from Contact (if exists)
        ai_roles = []
        try:
            contact = frappe.db.get_value("Contact", {"email_id": user_doc.email}, "name")
            if contact:
                contact_doc = frappe.get_doc("Contact", contact)
                # Get ai_roles child table
                if hasattr(contact_doc, 'ai_roles') and contact_doc.ai_roles:
                    ai_roles = [r.role for r in contact_doc.ai_roles if r.role]
        except Exception as e:
            frappe.log_error(f"Error getting AI roles for user {user_id}: {str(e)}", "Get User Detail AI Roles")
        
        # Get Frappe system roles (for reference, but we mainly use AI roles)
        system_roles = frappe.db.sql("""
            SELECT role FROM `tabHas Role` 
            WHERE parent = %s AND parenttype = 'User'
            ORDER BY role
        """, user_id, as_dict=True)
        
        # Get user activity statistics
        activity_stats = {
            "login_count": frappe.db.count("Activity Log", {
                "user": user_id,
                "status": "Success",
                "operation": "Login"
            }),
            "documents_created": frappe.db.count("Version", {
                "owner": user_id,
                "docname": ["!=", ""]
            }),
            "total_sessions": frappe.db.count("Sessions", {"user": user_id})
        }
        
        user_data = {
            "name": user_doc.name,
            "email": user_doc.email,
            "full_name": getattr(user_doc, 'full_name', '') or "",
            "first_name": getattr(user_doc, 'first_name', '') or "",
            "last_name": getattr(user_doc, 'last_name', '') or "",
            "enabled": getattr(user_doc, 'enabled', 1),
            "user_image": getattr(user_doc, 'user_image', '') or "",
            "mobile_no": getattr(user_doc, 'mobile_no', '') or "",
            "phone": getattr(user_doc, 'phone', '') or "",
            "gender": getattr(user_doc, 'gender', '') or "",
            "birth_date": getattr(user_doc, 'birth_date', '') or "",
            "location": getattr(user_doc, 'location', '') or "",
            "bio": getattr(user_doc, 'bio', '') or "",
            "language": getattr(user_doc, 'language', 'vi') or "vi",
            "time_zone": getattr(user_doc, 'time_zone', 'Asia/Ho_Chi_Minh') or "Asia/Ho_Chi_Minh",
            "creation": user_doc.creation,
            "modified": user_doc.modified,
            "last_login": getattr(user_doc, 'last_login', None),
            "last_active": getattr(user_doc, 'last_active', None),
            "roles": ai_roles,  # Return AI roles from Contact
            "system_roles": [r.role for r in system_roles],  # Keep system roles for reference
            "primary_role": system_roles[0].role if system_roles else 'User',
            "status": 'active' if getattr(user_doc, 'enabled', 1) else 'inactive',
            "activity_stats": activity_stats
        }
        
        return {
            "success": True,
            "data": user_data
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get User Detail API Error")
        frappe.throw(_("Failed to get user detail: {0}").format(str(e)))

@frappe.whitelist()
def create_user(email, full_name, first_name="", last_name="", password="", roles=None, enabled=1, **kwargs):
    """Create a new user"""
    try:
        # Validate required fields
        if not email or not full_name:
            frappe.throw(_("Email and full name are required"))
        
        # Validate email format
        validate_email_address(email)
        
        # Check if user already exists
        if frappe.db.exists("User", email):
            frappe.throw(_("User with email {0} already exists").format(email))
        
        # Parse roles if string
        if isinstance(roles, str):
            roles = json.loads(roles) if roles else []
        elif not roles:
            roles = ["System Manager"]  # Default role
        
        # Create user document with only essential fields
        user_doc_data = {
            "doctype": "User",
            "email": email,
            "full_name": full_name,
            "first_name": first_name or full_name.split()[0] if full_name else "",
            "last_name": last_name or " ".join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else "",
            "enabled": cint(enabled),
            "send_welcome_email": 0
        }
        
        # Add optional fields only if they exist in the DocType
        optional_fields = {
            "mobile_no": kwargs.get("mobile_no", ""),
            "gender": kwargs.get("gender", ""),
            "language": kwargs.get("language", "vi")
        }
        
        # Only add fields that are not empty
        for field, value in optional_fields.items():
            if value:
                user_doc_data[field] = value
        
        user_doc = frappe.get_doc(user_doc_data)
        
        # Add roles
        for role in roles:
            user_doc.append("roles", {"role": role})
        
        # Insert user
        user_doc.insert(ignore_permissions=True)
        
        # Set password if provided
        if password:
            update_password(user_doc.name, password)
        
        # Create or update Contact with AI roles
        try:
            contact = None
            # Try to find existing contact by email
            existing_contacts = frappe.get_all("Contact", 
                filters={"email_id": email},
                pluck="name",
                limit=1
            )
            
            if existing_contacts:
                contact = frappe.get_doc("Contact", existing_contacts[0])
            else:
                # Create new contact
                contact = frappe.get_doc({
                    "doctype": "Contact",
                    "first_name": first_name or full_name.split()[0] if full_name else "",
                    "last_name": last_name or " ".join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else "",
                    "email_id": email,
                    "user": email
                })
                contact.insert(ignore_permissions=True)
            
            # Filter out System/Frappe roles, only keep AI roles (AI-ROLE-xxxx format)
            ai_roles = [r for r in roles if r.startswith("AI-ROLE-")]
            
            if ai_roles:
                # Clear existing AI roles
                contact.ai_roles = []
                
                # Add new AI roles
                for ai_role in ai_roles:
                    contact.append("ai_roles", {"role": ai_role})
                
                contact.save(ignore_permissions=True)
                frappe.logger().info(f"Updated Contact {contact.name} with AI roles: {ai_roles}")
        
        except Exception as contact_error:
            frappe.logger().error(f"Failed to update Contact for {email}: {str(contact_error)}")
            # Don't fail the entire user creation if contact update fails
        
        frappe.db.commit()
        
        # Log the creation
        frappe.logger().info(f"User created successfully: {email}")
        
        return {
            "success": True,
            "message": _("User created successfully"),
            "data": {
                "name": user_doc.name,
                "email": user_doc.email,
                "full_name": user_doc.full_name,
                "enabled": user_doc.enabled,
                "roles": roles
            }
        }
        
    except frappe.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), "Create User Validation Error")
        frappe.throw(str(e))
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create User API Error")
        frappe.throw(_("Failed to create user: {0}").format(str(e)))

@frappe.whitelist()
def update_user(user_id, **kwargs):
    """Update user information"""
    try:
        if not user_id:
            frappe.throw(_("User ID is required"))
        
        # Check if user exists
        if not frappe.db.exists("User", user_id):
            frappe.throw(_("User not found"))
        
        # Get user document
        user_doc = frappe.get_doc("User", user_id)
        
        # Define updatable fields
        updatable_fields = [
            'full_name', 'first_name', 'last_name', 'enabled',
            'mobile_no', 'phone', 'gender', 'birth_date', 
            'location', 'bio', 'language', 'time_zone'
        ]
        
        # Update allowed fields
        updated_fields = []
        for field in updatable_fields:
            if field in kwargs and kwargs[field] is not None:
                old_value = getattr(user_doc, field, None)
                new_value = kwargs[field]
                
                # Convert enabled to int
                if field == 'enabled':
                    new_value = cint(new_value)
                
                # Only update if value changed
                if old_value != new_value:
                    setattr(user_doc, field, new_value)
                    updated_fields.append(field)
        
        # Update roles if provided (save to Contact's ai_roles, not User's roles)
        if 'roles' in kwargs and kwargs['roles'] is not None:
            roles = kwargs['roles']
            if isinstance(roles, str):
                roles = json.loads(roles)
            
            print(f"[update_user] Updating roles for user {user_id}: {roles}")
            
            # Get or create Contact for this user
            contact_name = frappe.db.get_value("Contact", {"email_id": user_doc.email}, "name")
            if not contact_name:
                contact_name = frappe.db.get_value("Contact", {"user": user_id}, "name")
            
            old_roles = []
            if contact_name:
                contact_doc = frappe.get_doc("Contact", contact_name)
                
                # Lưu lại roles cũ để so sánh
                old_roles = [r.role for r in contact_doc.ai_roles if r.role]
                
                # Clear existing AI roles
                contact_doc.ai_roles = []
                
                # Add new AI roles
                for role_id in roles:
                    if role_id and frappe.db.exists("AI Role", role_id):
                        contact_doc.append("ai_roles", {"role": role_id})
                
                contact_doc.save(ignore_permissions=True)
                updated_fields.append('ai_roles')
                frappe.logger().info(f"Updated AI roles for contact {contact_name}: {roles}")
                print(f"[update_user] Updated Contact {contact_name} ai_roles")
            else:
                frappe.logger().warning(f"No contact found for user {user_doc.email}, cannot update AI roles")
            
            # ============ Cập nhật ngược lại vào AI Role ============
            # Tìm roles bị xóa và roles mới thêm
            roles_to_remove = set(old_roles) - set(roles)
            roles_to_add = set(roles) - set(old_roles)
            
            print(f"[update_user] Roles to remove: {roles_to_remove}")
            print(f"[update_user] Roles to add: {roles_to_add}")
            
            # Xóa user khỏi các role cũ (so sánh bằng user email, không phải contact name)
            for role_id in roles_to_remove:
                if frappe.db.exists("AI Role", role_id):
                    try:
                        role_doc = frappe.get_doc("AI Role", role_id)
                        # Tìm và xóa user khỏi child table users_allowed (so sánh bằng email)
                        original_count = len(role_doc.users_allowed)
                        role_doc.users_allowed = [u for u in role_doc.users_allowed if u.user != user_doc.email]
                        removed_count = original_count - len(role_doc.users_allowed)
                        
                        if removed_count > 0:
                            role_doc.save(ignore_permissions=True)
                            print(f"[update_user] Removed user {user_doc.email} from role {role_id} ({removed_count} entries)")
                        else:
                            print(f"[update_user] User {user_doc.email} not found in role {role_id}")
                    except Exception as e:
                        frappe.logger().error(f"Failed to remove user from role {role_id}: {str(e)}")
                        print(f"[update_user] Error removing user from role {role_id}: {str(e)}")
            
            # Thêm user vào các role mới (lưu user email, không phải contact name)
            for role_id in roles_to_add:
                if frappe.db.exists("AI Role", role_id):
                    try:
                        role_doc = frappe.get_doc("AI Role", role_id)
                        # Kiểm tra xem user đã tồn tại chưa (so sánh bằng email)
                        existing_users = [u.user for u in role_doc.users_allowed if u.user]
                        if user_doc.email not in existing_users:
                            role_doc.append("users_allowed", {
                                "user": user_doc.email,
                                "is_active": 1
                            })
                            role_doc.save(ignore_permissions=True)
                            print(f"[update_user] Added user {user_doc.email} to role {role_id}")
                        else:
                            print(f"[update_user] User {user_doc.email} already exists in role {role_id}")
                    except Exception as e:
                        frappe.logger().error(f"Failed to add user to role {role_id}: {str(e)}")
                        print(f"[update_user] Error adding user to role {role_id}: {str(e)}")
        
        # Save the document if there are changes
        if updated_fields:
            user_doc.save(ignore_permissions=True)
            frappe.db.commit()
            
            # Log the update
            frappe.logger().info(f"User updated successfully: {user_id}, fields: {updated_fields}")
            
            return {
                "success": True,
                "message": _("User updated successfully"),
                "updated_fields": updated_fields
            }
        else:
            return {
                "success": True,
                "message": _("No changes to update"),
                "updated_fields": []
            }
        
    except frappe.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), "Update User Validation Error")
        frappe.throw(str(e))
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update User API Error")
        frappe.throw(_("Failed to update user: {0}").format(str(e)))

@frappe.whitelist()
def delete_user(user_id):
    """Permanently delete a user (hard delete)."""
    try:
        if not user_id:
            frappe.throw(_("User ID is required"))

        # Check if user exists
        if not frappe.db.exists("User", user_id):
            frappe.throw(_("User not found"))

        # Prevent deletion of system users
        if user_id in ["Administrator", "Guest"]:
            frappe.throw(_("Cannot delete system user"))

        # Best-effort: clear Contact.user links to avoid link validation
        try:
            contact_name = frappe.db.get_value("Contact", {"user": user_id}, "name")
            if contact_name:
                contact_doc = frappe.get_doc("Contact", contact_name)
                if hasattr(contact_doc, "user"):
                    contact_doc.user = None
                    contact_doc.save(ignore_permissions=True)
        except Exception:
            # Do not block deletion if contact cleanup fails
            pass

        # Hard delete
        frappe.delete_doc("User", user_id, ignore_permissions=True, force=True)
        frappe.db.commit()

        frappe.logger().info(f"User deleted successfully: {user_id}")

        return {
            "success": True,
            "message": _("User deleted successfully")
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete User API Error")
        frappe.throw(_("Failed to delete user: {0}").format(str(e)))

@frappe.whitelist()
def reset_user_password(user_id, new_password):
    """Reset user password"""
    try:
        if not user_id or not new_password:
            frappe.throw(_("User ID and new password are required"))
        
        # Check if user exists
        if not frappe.db.exists("User", user_id):
            frappe.throw(_("User not found"))
        
        # Validate password strength
        if len(new_password) < 8:
            frappe.throw(_("Password must be at least 8 characters long"))
        
        # Update password
        update_password(user_id, new_password)
        
        # Log the password reset
        frappe.logger().info(f"Password reset successfully for user: {user_id}")
        
        return {
            "success": True,
            "message": _("Password reset successfully")
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reset Password API Error")
        frappe.throw(_("Failed to reset password: {0}").format(str(e)))

@frappe.whitelist()
def get_available_roles():
    """Get list of available roles"""
    try:
        # Get roles from Frappe - only select name field as title may not exist
        roles = frappe.db.sql("""
            SELECT name
            FROM `tabRole` 
            WHERE disabled = 0 OR disabled IS NULL
            AND name NOT IN ('Administrator', 'Guest', 'All')
            ORDER BY name
        """, as_dict=True)
        
        # Format roles for frontend - use name as both name and title
        formatted_roles = []
        for role in roles:
            formatted_roles.append({
                "name": role.name,
                "title": role.name  # Use name as title since title field doesn't exist
            })
        
        return {
            "success": True,
            "data": formatted_roles
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Roles API Error")
        frappe.throw(_("Failed to get roles: {0}").format(str(e)))

@frappe.whitelist()
def get_user_stats():
    """Get user statistics"""
    try:
        # Use SQL queries to avoid issues with non-existent fields
        stats = {}
        
        # Total users (excluding system users)
        stats["total_users"] = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabUser`
            WHERE name NOT IN ('Administrator', 'Guest')
        """, as_dict=True)[0].count
        
        # Active users
        stats["active_users"] = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabUser`
            WHERE name NOT IN ('Administrator', 'Guest')
            AND (enabled = 1 OR enabled IS NULL)
        """, as_dict=True)[0].count
        
        # Inactive users
        stats["inactive_users"] = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabUser`
            WHERE name NOT IN ('Administrator', 'Guest')
            AND enabled = 0
        """, as_dict=True)[0].count
        
        # Users created today
        stats["users_created_today"] = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabUser`
            WHERE name NOT IN ('Administrator', 'Guest')
            AND DATE(creation) = CURDATE()
        """, as_dict=True)[0].count
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get User Stats API Error")
        frappe.throw(_("Failed to get user statistics: {0}").format(str(e)))
