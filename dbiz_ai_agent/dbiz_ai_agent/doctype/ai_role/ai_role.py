import frappe
from frappe import _
from frappe.core.doctype.user.user import create_contact
from frappe.model.document import Document

class AIRole(Document):
    def validate(self):
        self.validate_role_code()
        self.validate_permissions()
    
    def before_save(self):
        if not self.role_code:
            self.role_code = self.generate_role_code()
    
    def generate_role_code(self):
        """Generate role code from role name"""
        if self.role_name:
            return self.role_name.lower().replace(' ', '_').replace('-', '_')
        return ''
    
    def validate_role_code(self):
        """Validate role code uniqueness"""
        if self.role_code:
            existing = frappe.get_all("AI Role", 
                                    filters={"role_code": self.role_code, "name": ["!=", self.name]})
            if existing:
                frappe.throw(_("Role Code {0} already exists").format(self.role_code))
    
    def validate_permissions(self):
        """Validate permission settings"""
        # Basic validation - can be extended later
        pass
    
    def get_user_count(self):
        """Get count of users assigned to this role via Users Allowed child rows."""
        return frappe.db.count(
            "Users Allowed",
            {
                "parent": self.name,
                "parenttype": "AI Role",
                "parentfield": "users_allowed",
                "is_active": 1,
            },
        )
    
    def get_permission_summary(self):
        """Get summary of permissions for this role"""
        summary = {
            "user_management": self.user_management,
            "is_active": self.is_active,
            "priority": self.priority
        }
        return summary
    
    def has_permission(self, doctype, permission_type="read"):
        """Check if role has specific permission"""
        # Always allow reading/updating AI Role records; access control is handled elsewhere.
        return True
    
    def get_document_access_level(self, doctype):
        """Get access level for specific document type"""
        # Basic access level - can be extended later
        return "Read" if self.is_active else "None"
    
    def get_database_access_level(self, table_name):
        """Get access level for specific database table"""
        # Basic access level - can be extended later
        return "Read" if self.is_active else "None"
    
    def get_api_permissions(self, endpoint):
        """Get API permissions for specific endpoint"""
        # Basic API permissions - can be extended later
        return [{"method": "GET", "rate_limit": 100, "restrictions": []}] if self.is_active else []

    def on_update(self):
        self.sync_contact_ai_roles()

    def sync_contact_ai_roles(self, full_sync: bool = False):
        """Sync AI Role assignments to related Contact records."""
        previous_doc = self.get_doc_before_save()

        previous_users = set()
        if previous_doc:
            previous_users = {
                row.user for row in previous_doc.get("users_allowed", []) if getattr(row, "user", None)
            }

        current_users = {
            row.user for row in self.get("users_allowed", []) if getattr(row, "user", None)
        }

        added_users = current_users - previous_users
        retained_users = current_users & previous_users
        removed_users = previous_users - current_users

        for user_id in added_users | retained_users:
            self._upsert_contact_role_entry(user_id)

        for user_id in removed_users:
            self._remove_contact_role_entry(user_id)

        if full_sync or not previous_doc:
            self._cleanup_stale_contact_entries(current_users)

    def _upsert_contact_role_entry(self, user_id: str):
        """Ensure Contact for the user contains an entry for this AI Role."""
        contact_name = frappe.db.get_value("Contact", {"user": user_id}, "name")

        if not contact_name:
            try:
                user_doc = frappe.get_doc("User", user_id)
            except frappe.DoesNotExistError:
                frappe.log_error(
                    title="AI Role Contact Sync",
                    message=f"User {user_id} referenced in AI Role {self.name} does not exist.",
                )
                return

            try:
                create_contact(user_doc, ignore_links=True, ignore_mandatory=True)
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    "AI Role Contact Sync: Failed to auto-create contact",
                )
                return

            contact_name = frappe.db.get_value("Contact", {"user": user_id}, "name")

        if not contact_name:
            return

        contact_doc = frappe.get_doc("Contact", contact_name)

        existing_rows = {
            row.role_name: row for row in contact_doc.get("ai_roles", []) if getattr(row, "role_name", None)
        }

        if self.role_name in existing_rows:
            row = existing_rows[self.role_name]
            row.description = self.description
            row.is_active = self.is_active
            row.priority = self.priority
            row.color = self.color
            row.icon = self.icon
        else:
            contact_doc.append(
                "ai_roles",
                {
                    "role_name": self.role_name,
                    "description": self.description,
                    "is_active": self.is_active,
                    "priority": self.priority,
                    "color": self.color,
                    "icon": self.icon,
                },
            )

        contact_doc.save(ignore_permissions=True)

    def _remove_contact_role_entry(self, user_id: str):
        """Remove AI Role entry from user's Contact when unassigned."""
        contact_name = frappe.db.get_value("Contact", {"user": user_id}, "name")
        if not contact_name:
            return

        contact_doc = frappe.get_doc("Contact", contact_name)
        rows = contact_doc.get("ai_roles", [])
        updated_rows = [row for row in rows if getattr(row, "role_name", None) != self.role_name]

        if len(updated_rows) == len(rows):
            return

        contact_doc.set("ai_roles", updated_rows)
        contact_doc.save(ignore_permissions=True)

    def _cleanup_stale_contact_entries(self, current_users):
        """Remove AI Role entries from contacts for users no longer assigned."""
        current_users = current_users or set()

        child_rows = frappe.get_all(
            "AI Role Child",
            filters={
                "parenttype": "Contact",
                "role_name": self.role_name,
            },
            fields=["name", "parent"],
        )

        contacts_to_update = {}
        for row in child_rows:
            contact_user = frappe.db.get_value("Contact", row["parent"], "user")
            if not contact_user or contact_user in current_users:
                continue

            contacts_to_update.setdefault(row["parent"], []).append(row["name"])

        for contact_name, child_names in contacts_to_update.items():
            try:
                contact_doc = frappe.get_doc("Contact", contact_name)
                filtered_rows = [
                    row for row in contact_doc.get("ai_roles", [])
                    if row.name not in child_names
                ]

                if len(filtered_rows) == len(contact_doc.get("ai_roles", [])):
                    continue

                contact_doc.set("ai_roles", filtered_rows)
                contact_doc.save(ignore_permissions=True)
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    f"AI Role Contact Sync: Failed to cleanup Contact {contact_name}",
                )

@frappe.whitelist()
def get_role_stats():
    """Get statistics for all roles"""
    try:
        roles = frappe.get_all("AI Role", 
                              fields=["name", "role_name", "is_active", "priority", "color", "icon"])
        
        stats = {
            "total_roles": len(roles),
            "active_roles": len([r for r in roles if r.is_active]),
            "roles": []
        }
        
        for role in roles:
            role_doc = frappe.get_doc("AI Role", role.name)
            user_count = role_doc.get_user_count()
            permission_summary = role_doc.get_permission_summary()
            
            stats["roles"].append({
                "name": role.name,
                "role_name": role.role_name,
                "is_active": role.is_active,
                "priority": role.priority,
                "color": role.color,
                "icon": role.icon,
                "user_count": user_count,
                "permissions": permission_summary
            })
        
        return stats
        
    except Exception as e:
        frappe.log_error(f"Error getting role stats: {str(e)}")
        frappe.throw(_("Error getting role statistics: {0}").format(str(e)))

@frappe.whitelist()
def create_default_roles():
    """Create default roles if they don't exist"""
    try:
        default_roles = [
            {
                "role_name": "Administrator",
                "description": "Full system access",
                "is_active": 1,
                "priority": 1,
                "color": "#ef4444",
                "icon": "A",
                "user_management": 1
            },
            {
                "role_name": "Manager",
                "description": "Department management access",
                "is_active": 1,
                "priority": 2,
                "color": "#8b5cf6",
                "icon": "M",
                "user_management": 1
            },
            {
                "role_name": "Employee",
                "description": "Basic employee access",
                "is_active": 1,
                "priority": 3,
                "color": "#10b981",
                "icon": "E",
                "user_management": 0
            },
            {
                "role_name": "Guest",
                "description": "Limited guest access",
                "is_active": 0,
                "priority": 4,
                "color": "#6b7280",
                "icon": "G",
                "user_management": 0
            }
        ]
        
        created_roles = []
        
        for role_data in default_roles:
            existing = frappe.get_all("AI Role", filters={"role_name": role_data["role_name"]})
            if not existing:
                role_doc = frappe.get_doc({
                    "doctype": "AI Role",
                    **role_data
                })
                role_doc.insert(ignore_permissions=True)
                created_roles.append(role_data["role_name"])
        
        return {
            "message": f"Created {len(created_roles)} default roles",
            "created_roles": created_roles
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating default roles: {str(e)}")
        frappe.throw(_("Error creating default roles: {0}").format(str(e)))

@frappe.whitelist()
def toggle_role_status(role_name, is_active):
    """Toggle role active status"""
    try:
        role = frappe.get_doc("AI Role", role_name)
        role.is_active = is_active
        role.save()
        
        return {
            "message": f"Role {role_name} {'activated' if is_active else 'deactivated'} successfully",
            "is_active": is_active
        }
        
    except Exception as e:
        frappe.log_error(f"Error toggling role status: {str(e)}")
        frappe.throw(_("Error updating role status: {0}").format(str(e)))

@frappe.whitelist()
def get_role_users(role_name):
    """Get users assigned to specific role"""
    try:
        role_doc = frappe.get_doc("AI Role", role_name)
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
                doc = user_docs.get(row.user)
                if not doc:
                    continue

                users.append({
                    "name": doc.get("name"),
                    "full_name": doc.get("full_name"),
                    "email": doc.get("email"),
                    "enabled": doc.get("enabled"),
                    "last_login": doc.get("last_login"),
                    "assignment_active": bool(getattr(row, "is_active", 1)),
                })
        
        return {
            "role_name": role_name,
            "user_count": len(users),
            "users": users
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting role users: {str(e)}")
        frappe.throw(_("Error getting role users: {0}").format(str(e)))


def sync_ai_role_on_update(doc, method=None):
    """Doc event hook: called when AI Role is updated.

    Keep users_allowed child table clean (no duplicate users) and ensure each row has is_active set.
    """
    try:
        seen = set()
        rows = getattr(doc, 'users_allowed', []) or []
        for row in list(rows):
            user_val = getattr(row, 'user', None)
            if not user_val:
                # remove empty rows
                try:
                    doc.remove(row)
                except Exception:
                    pass
                continue

            if user_val in seen:
                # duplicate - remove
                try:
                    doc.remove(row)
                except Exception:
                    pass
            else:
                seen.add(user_val)
                # ensure is_active boolean
                if getattr(row, 'is_active', None) is None:
                    row.is_active = 1

        # Save cleaned doc if modified
        try:
            doc.save(ignore_permissions=True)
        except Exception:
            # best effort only
            pass
    except Exception as e:
        frappe.log_error(f"Error in sync_ai_role_on_update for {getattr(doc,'name', '')}: {e}")


def sync_ai_role_on_trash(doc, method=None):
    """Doc event hook: called when AI Role is deleted.

    No-op for now (placeholder), but present so hooks don't fail.
    """
    # nothing to do currently
    return


@frappe.whitelist()
def get_roles_for_user(user):
    """Return AI Roles that include the given user in their Users Allowed child table."""
    try:
        if not user:
            return []

        roles = frappe.get_all('AI Role', fields=['name', 'role_name', 'role_code', 'description', 'is_active'])
        matched = []
        for r in roles:
            try:
                doc = frappe.get_doc('AI Role', r.name)
                for row in getattr(doc, 'users_allowed', []) or []:
                    if getattr(row, 'user', None) == user:
                        matched.append({
                            'name': r.name,
                            'role_name': r.role_name,
                            'role_code': r.role_code,
                            'description': r.description,
                            'is_active': r.is_active
                        })
                        break
            except Exception:
                continue

        return matched
    except Exception as e:
        frappe.log_error(f"Error retrieving roles for user {user}: {e}")
        frappe.throw(str(e))


@frappe.whitelist()
def add_user_to_role(user, ai_role):
    """Add a user to AI Role.users_allowed child table."""
    try:
        if not user or not ai_role:
            frappe.throw('Missing user or ai_role')

        role = frappe.get_doc('AI Role', ai_role)
        exists = False
        for row in getattr(role, 'users_allowed', []) or []:
            if getattr(row, 'user', None) == user:
                exists = True
                break

        if not exists:
            role.append('users_allowed', {'user': user, 'is_active': 1})
            role.save(ignore_permissions=True)
            return {'status': 'added', 'ai_role': ai_role}
        else:
            return {'status': 'exists', 'ai_role': ai_role}
    except Exception as e:
        frappe.log_error(f"Error adding user {user} to role {ai_role}: {e}")
        frappe.throw(str(e))


@frappe.whitelist()
def remove_user_from_role(user, ai_role):
    """Remove a user from AI Role.users_allowed child table."""
    try:
        if not user or not ai_role:
            frappe.throw('Missing user or ai_role')

        role = frappe.get_doc('AI Role', ai_role)
        removed = False
        for row in list(getattr(role, 'users_allowed', []) or []):
            if getattr(row, 'user', None) == user:
                try:
                    role.remove(row)
                    removed = True
                except Exception:
                    pass

        if removed:
            role.save(ignore_permissions=True)
            return {'status': 'removed', 'ai_role': ai_role}
        else:
            return {'status': 'not_found', 'ai_role': ai_role}
    except Exception as e:
        frappe.log_error(f"Error removing user {user} from role {ai_role}: {e}")
        frappe.throw(str(e))
