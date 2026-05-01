import frappe
from frappe import _
from frappe.utils import validate_email_address
import json

@frappe.whitelist()
def get_user_profile():
    """Get current user profile information"""
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            frappe.throw(_("User not authenticated"))
        
        # Get user document
        user_doc = frappe.get_doc("User", user)
        
        # Get additional profile information if exists
        profile_data = {
            "name": user_doc.name,
            "email": user_doc.email,
            "first_name": user_doc.first_name or "",
            "last_name": user_doc.last_name or "",
            "full_name": user_doc.full_name or "",
            "mobile_no": user_doc.mobile_no or "",
            "phone": user_doc.phone or "",
            "gender": user_doc.gender or "",
            "birth_date": user_doc.birth_date or "",
            "location": user_doc.location or "",
            "bio": user_doc.bio or "",
            "user_image": user_doc.user_image or "",
            "language": user_doc.language or "vi",
            "time_zone": user_doc.time_zone or "Asia/Ho_Chi_Minh",
            "enabled": user_doc.enabled,
            "role_profile_name": user_doc.role_profile_name or "",
            "roles": [role.role for role in user_doc.roles],
            "creation": user_doc.creation,
            "modified": user_doc.modified
        }
        
        return {
            "success": True,
            "data": profile_data
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get User Profile API Error")
        frappe.throw(_("Failed to get user profile: {0}").format(str(e)))

@frappe.whitelist()
def update_user_profile(profile_data):
    """Update current user profile information"""
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            frappe.throw(_("User not authenticated"))
        
        # Parse profile data if it's a string
        if isinstance(profile_data, str):
            profile_data = json.loads(profile_data)
        
        # Get user document
        user_doc = frappe.get_doc("User", user)
        
        # Define updatable fields
        updatable_fields = [
            'first_name', 'last_name', 'mobile_no', 'phone', 
            'gender', 'birth_date', 'location', 'bio', 
            'language', 'time_zone', 'user_image'
        ]
        
        # Update allowed fields
        updated_fields = []
        for field in updatable_fields:
            if field in profile_data:
                old_value = getattr(user_doc, field, None)
                new_value = profile_data[field]
                
                # Special validation for email
                if field == 'email' and new_value:
                    validate_email_address(new_value)
                
                # Only update if value changed
                if old_value != new_value:
                    setattr(user_doc, field, new_value)
                    updated_fields.append(field)
        
        # Update full_name if first_name or last_name changed
        if 'first_name' in updated_fields or 'last_name' in updated_fields:
            full_name = f"{user_doc.first_name or ''} {user_doc.last_name or ''}".strip()
            user_doc.full_name = full_name
            updated_fields.append('full_name')
        
        # Save the document if there are changes
        if updated_fields:
            user_doc.save(ignore_permissions=True)
            frappe.db.commit()
            
            # Log the update
            frappe.logger().info(f"User profile updated for {user}: {updated_fields}")
            
            return {
                "success": True,
                "message": _("Profile updated successfully"),
                "updated_fields": updated_fields
            }
        else:
            return {
                "success": True,
                "message": _("No changes to update"),
                "updated_fields": []
            }
        
    except frappe.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), "Update User Profile Validation Error")
        frappe.throw(str(e))
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Update User Profile API Error")
        frappe.throw(_("Failed to update user profile: {0}").format(str(e)))

@frappe.whitelist()
def upload_profile_image():
    """Upload and update user profile image"""
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            frappe.throw(_("User not authenticated"))
        
        # Get uploaded file
        if not frappe.request.files:
            frappe.throw(_("No file uploaded"))
        
        file_obj = frappe.request.files.get('file')
        if not file_obj:
            frappe.throw(_("No file found in request"))
        
        # Validate file type
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
        filename = file_obj.filename.lower()
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            frappe.throw(_("Only image files (jpg, jpeg, png, gif) are allowed"))
        
        # Save file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": file_obj.filename,
            "content": file_obj.read(),
            "is_private": 0,
            "folder": "Home/Attachments"
        })
        file_doc.save()
        
        # Update user profile image
        user_doc = frappe.get_doc("User", user)
        user_doc.user_image = file_doc.file_url
        user_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Profile image updated successfully"),
            "file_url": file_doc.file_url
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Upload Profile Image API Error")
        frappe.throw(_("Failed to upload profile image: {0}").format(str(e)))

@frappe.whitelist()
def change_password(current_password, new_password):
    """Change user password"""
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            frappe.throw(_("User not authenticated"))
        
        # Validate input
        if not current_password or not new_password:
            frappe.throw(_("Current password and new password are required"))
        
        # Validate current password
        from frappe.utils.password import check_password
        if not check_password(user, current_password):
            frappe.throw(_("Current password is incorrect"))
        
        # Validate new password strength
        if len(new_password) < 8:
            frappe.throw(_("New password must be at least 8 characters long"))
        
        # Update password
        from frappe.utils.password import update_password
        update_password(user, new_password)
        
        # Log the password change
        frappe.logger().info(f"Password changed successfully for user: {user}")
        
        return {
            "success": True,
            "message": _("Password changed successfully")
        }
        
    except frappe.ValidationError as e:
        frappe.log_error(frappe.get_traceback(), "Change Password Validation Error")
        frappe.throw(str(e))
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Change Password API Error")
        frappe.throw(_("Failed to change password: {0}").format(str(e)))

@frappe.whitelist()
def get_user_activity():
    """Get user activity statistics"""
    try:
        user = frappe.session.user
        if not user or user == "Guest":
            frappe.throw(_("User not authenticated"))
        
        # Get user activity data
        activity_data = {
            "login_count": frappe.db.count("Activity Log", {
                "user": user,
                "status": "Success",
                "operation": "Login"
            }),
            "last_login": frappe.db.get_value("User", user, "last_login"),
            "last_active": frappe.db.get_value("User", user, "last_active"),
            "total_sessions": frappe.db.count("Sessions", {"user": user}),
            "documents_created": frappe.db.count("Version", {
                "owner": user,
                "docname": ["!=", ""]
            })
        }
        
        return {
            "success": True,
            "data": activity_data
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get User Activity API Error")
        frappe.throw(_("Failed to get user activity: {0}").format(str(e)))
