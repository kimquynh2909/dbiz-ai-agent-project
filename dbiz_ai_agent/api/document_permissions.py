import frappe
from frappe import _
from frappe.utils import cint, get_url
import json
from typing import List, Optional, Dict, Any
import os
import mimetypes
from frappe.core.doctype.file.utils import find_file_by_url


# ============================================================================
# HELPER FUNCTIONS - Permission Checking Logic (5 cấp độ)
# ============================================================================

def check_document_access(document_id: str, user: Optional[str] = None) -> bool:
    """
    Kiểm tra quyền truy cập document với 2 cấp độ:
    1. Public: Mọi người đều xem được (không check gì cả)
    2. Internal: Chỉ cần đăng nhập là xem được (không check roles/departments)
    
    Args:
        document_id: ID của AI Document
        user: Email của user (mặc định là current user)
        
    Returns:
        bool: True nếu user có quyền truy cập
    """
    if not user:
        user = frappe.session.user
    
    # Administrator luôn có quyền
    if user == "Administrator":
        return True
    
    try:
        doc = frappe.get_doc("AI Document", document_id)
        
        # Owner/Uploader luôn có quyền xem document của mình
        if doc.owner == user or doc.uploaded_by == user:
            return True
        
        access_level = doc.access_level or "Internal"
        
        # PUBLIC: Mọi người đều xem được (không check gì cả)
        if access_level == "Public":
            frappe.logger().info(f"[PERMISSION] Document {document_id} is Public - access granted to {user}")
            return True
        
        # INTERNAL: Chỉ cần đăng nhập là xem được
        elif access_level == "Internal":
            if user == "Guest":
                frappe.logger().info(f"[PERMISSION] Guest denied access to Internal document {document_id}")
                return False
            frappe.logger().info(f"[PERMISSION] Document {document_id} is Internal - access granted to logged-in user {user}")
            return True
        
        # Mặc định là Internal nếu không match
        if user == "Guest":
            return False
        return True
        
    except frappe.DoesNotExistError:
        frappe.logger().warning(f"Document {document_id} not found")
        return False
    except Exception as e:
        frappe.log_error(f"Error checking document access: {str(e)}")
        return False


def _extract_roles_allowed(doc) -> List[str]:
    """Normalize roles_allowed which may be a comma string or child table."""
    raw_value = getattr(doc, "roles_allowed", None)
    if not raw_value:
        return []

    if isinstance(raw_value, str):
        return [r.strip() for r in raw_value.split(",") if r.strip()]

    roles = []
    for row in raw_value:
        role_name = getattr(row, "role_name", None)
        if not role_name and isinstance(row, dict):
            role_name = row.get("role_name")
        if role_name:
            roles.append(role_name)
    return roles


def _extract_departments_allowed(doc) -> List[str]:
    """Normalize departments_allowed which may be a comma string or child table."""
    raw_value = getattr(doc, "departments_allowed", None)
    if not raw_value:
        return []

    if isinstance(raw_value, str):
        return [d.strip() for d in raw_value.split(",") if d.strip()]

    departments = []
    for row in raw_value:
        dept_name = getattr(row, "department", None)
        if not dept_name and isinstance(row, dict):
            dept_name = row.get("department")
        if dept_name:
            departments.append(dept_name)
    return departments


def _get_user_roles_and_departments(user: str) -> tuple[List[str], List[str]]:
    """Lấy AI Roles và Departments của user từ Contact.
    
    Returns:
        tuple: (user_ai_roles, user_departments)
    """
    contact_name = frappe.db.get_value("Contact", {"user": user}, "name")
    contact_doc = None
    
    if contact_name:
        try:
            contact_doc = frappe.get_doc("Contact", contact_name)
            caller = frappe.session.user
            # Chỉ cho phép nếu caller là Administrator hoặc chính user đó
            if caller != "Administrator" and caller != user:
                try:
                    if not contact_doc.has_permission("read", user=caller):
                        contact_doc = None
                except Exception:
                    contact_doc = None
        except Exception:
            contact_doc = None
    
    user_ai_roles = []
    user_departments = []
    
    if contact_doc:
        # Lấy AI Roles
        ai_roles_child = contact_doc.get("ai_roles") or []
        user_ai_roles = [
            row.role_name for row in ai_roles_child
            if getattr(row, "role_name", None)
        ]
        
        # Lấy Departments
        # Giả sử Contact có field department hoặc child table departments
        dept_field = getattr(contact_doc, "department", None)
        if dept_field:
            if isinstance(dept_field, str):
                user_departments = [dept_field]
            else:
                user_departments = [dept_field]
        
        # Hoặc từ child table
        dept_child = contact_doc.get("departments") or []
        for row in dept_child:
            dept_name = getattr(row, "department", None)
            if dept_name and dept_name not in user_departments:
                user_departments.append(dept_name)
    
    return user_ai_roles, user_departments


# DEPRECATED: Hàm này không còn được dùng vì access_level chỉ còn Public và Internal.
# Giữ lại để tránh lỗi nếu có tham chiếu từ code cũ.
def _check_restricted_access(doc, user: str) -> bool:
    """Kiểm tra quyền truy cập cho Access Level = Restricted (DEPRECATED).
    
    Logic: Thỏa 1 trong 2 điều kiện:
    - User có AI Role nằm trong roles_allowed HOẶC
    - User có Department nằm trong departments_allowed
    
    Nếu document không set roles_allowed và departments_allowed → TẤT CẢ logged-in users xem được
    """
    if user == "Guest":
        frappe.logger().info(f"[PERMISSION] Guest denied access to Restricted document {doc.name}")
        return False
    
    user_ai_roles, user_departments = _get_user_roles_and_departments(user)
    roles_allowed = _extract_roles_allowed(doc)
    departments_allowed = _extract_departments_allowed(doc)
    
    frappe.logger().info(
        f"[PERMISSION CHECK] Doc: {doc.name}, Access Level: Restricted\n"
        f"  User: {user}\n"
        f"  User AI Roles: {user_ai_roles}\n"
        f"  User Departments: {user_departments}\n"
        f"  Roles Allowed: {roles_allowed}\n"
        f"  Departments Allowed: {departments_allowed}"
    )
    
    # Nếu không set roles và departments → TẤT CẢ logged-in users xem được
    if not roles_allowed and not departments_allowed:
        frappe.logger().info(
            f"[PERMISSION] Document {doc.name} has no restrictions - "
            f"access granted to logged-in user {user}"
        )
        return True
    
    # Check AI Roles
    role_match = False
    if roles_allowed and user_ai_roles:
        role_match = any(role in user_ai_roles for role in roles_allowed)
    
    # Check Departments
    dept_match = False
    if departments_allowed and user_departments:
        dept_match = any(dept in user_departments for dept in departments_allowed)
    
    # Thỏa 1 trong 2 → granted
    has_access = role_match or dept_match
    
    if has_access:
        frappe.logger().info(
            f"[PERMISSION] User {user} has matching Role={role_match} or Dept={dept_match} - "
            f"access granted to {doc.name}"
        )
    else:
        frappe.logger().info(
            f"[PERMISSION] User {user} does not match Role or Dept requirements - "
            f"access denied to {doc.name}"
        )
    
    return has_access


# DEPRECATED: Hàm này không còn được dùng vì access_level chỉ còn Public và Internal.
# Giữ lại để tránh lỗi nếu có tham chiếu từ code cũ.
def _check_confidential_access(doc, user: str) -> bool:
    """Kiểm tra quyền truy cập cho Access Level = Confidential (DEPRECATED).
    
    Logic: Phải thỏa CẢ 2 điều kiện:
    - User có AI Role nằm trong roles_allowed VÀ
    - User có Department nằm trong departments_allowed
    
    Nếu document không set roles_allowed hoặc departments_allowed → TẤT CẢ logged-in users xem được
    """
    if user == "Guest":
        frappe.logger().info(f"[PERMISSION] Guest denied access to Confidential document {doc.name}")
        return False
    
    user_ai_roles, user_departments = _get_user_roles_and_departments(user)
    roles_allowed = _extract_roles_allowed(doc)
    departments_allowed = _extract_departments_allowed(doc)
    
    frappe.logger().info(
        f"[PERMISSION CHECK] Doc: {doc.name}, Access Level: Confidential\n"
        f"  User: {user}\n"
        f"  User AI Roles: {user_ai_roles}\n"
        f"  User Departments: {user_departments}\n"
        f"  Roles Allowed: {roles_allowed}\n"
        f"  Departments Allowed: {departments_allowed}"
    )
    
    # Nếu không set cả 2 → TẤT CẢ logged-in users xem được
    if not roles_allowed and not departments_allowed:
        frappe.logger().info(
            f"[PERMISSION] Document {doc.name} has no restrictions - "
            f"access granted to logged-in user {user}"
        )
        return True
    
    # Nếu chỉ set 1 trong 2 → check cái đó
    if not roles_allowed:
        dept_match = any(dept in user_departments for dept in departments_allowed) if departments_allowed and user_departments else False
        frappe.logger().info(
            f"[PERMISSION] Only dept restriction: {dept_match} - "
            f"{'granted' if dept_match else 'denied'} for {user}"
        )
        return dept_match
    
    if not departments_allowed:
        role_match = any(role in user_ai_roles for role in roles_allowed) if roles_allowed and user_ai_roles else False
        frappe.logger().info(
            f"[PERMISSION] Only role restriction: {role_match} - "
            f"{'granted' if role_match else 'denied'} for {user}"
        )
        return role_match
    
    # Phải thỏa CẢ 2
    role_match = any(role in user_ai_roles for role in roles_allowed) if user_ai_roles else False
    dept_match = any(dept in user_departments for dept in departments_allowed) if user_departments else False
    
    has_access = role_match and dept_match
    
    if has_access:
        frappe.logger().info(
            f"[PERMISSION] User {user} has both Role AND Dept match - "
            f"access granted to {doc.name}"
        )
    else:
        frappe.logger().info(
            f"[PERMISSION] User {user} missing Role={not role_match} or Dept={not dept_match} - "
            f"access denied to {doc.name}"
        )
    
    return has_access


def _check_internal_access(doc, user: str) -> bool:
    """Legacy function - không còn dùng nữa vì Internal chỉ cần đăng nhập."""
    if user == "Guest":
        return False
    return True


# ============================================================================
# API ENDPOINTS - Whitelisted functions
# ============================================================================

@frappe.whitelist(allow_guest=True)
def get_documents(limit: Optional[int] = None, offset: Optional[int] = None):
    """Get AI Documents with basic info, server-side filtering and paginated.

    Supports optional filters via form_dict: q, file_type, access_level, role
    These filters are applied before permission checks so total/count reflects
    the filtered result set across all pages.
    """
    try:
        current_user = frappe.session.user

        # read params from args or form_dict
        limit = cint(limit or frappe.form_dict.get("limit") or 100)
        offset = cint(offset or frappe.form_dict.get("offset") or 0)
        q = (frappe.form_dict.get("q") or None) or None
        file_type = (frappe.form_dict.get("file_type") or None) or None
        access_level = (frappe.form_dict.get("access_level") or None) or None
        role = (frappe.form_dict.get("role") or None) or None
        fetch_all_flag = (frappe.form_dict.get("fetch_all") or None) or None
        fetch_all = False
        if fetch_all_flag is not None:
            try:
                fetch_all = str(fetch_all_flag).lower() in ("1", "true", "yes")
            except Exception:
                fetch_all = False

        if limit <= 0:
            limit = 100
        if offset < 0:
            offset = 0

        base_filters = {}
        if file_type:
            base_filters["file_type"] = file_type
        if access_level:
            base_filters["access_level"] = access_level

        # Fetch candidate documents matching simple filters (no full-text q yet)
        # Include file_attachment and other useful metadata so frontend can
        # preview / download documents without additional per-document fetches.
        candidates = frappe.get_all(
            "AI Document",
            fields=[
                "name",
                "title",
                "file_type",
                "access_level",
                "status",
                "category",
                "file_attachment",
                "file_size",
                "uploaded_by",
                "upload_date",
                "description",
                "tags",
                "folder_id",
            ],
            filters=base_filters,
            order_by="creation desc",
        )

        # Apply q filter (search in title or name) if provided
        if q:
            q_lower = q.lower()
            candidates = [d for d in candidates if q_lower in ((d.get("title") or "") + " " + (d.get("name") or "")).lower()]

        # If role filter provided, keep only documents that list the role in roles_allowed
        if role:
            def doc_has_role(docname):
                try:
                    doc = frappe.get_doc("AI Document", docname)
                    allowed = set()
                    # try child table
                    for r in doc.get("roles_allowed") or []:
                        rl = getattr(r, "role_name", None) or (r.get("role_name") if isinstance(r, dict) else None)
                        if rl:
                            allowed.add(rl.strip())
                    # fallback comma-separated
                    if getattr(doc, "roles_allowed", None) and not allowed:
                        allowed.update([r.strip() for r in (doc.roles_allowed or "").split(",") if r.strip()])
                    return role in allowed
                except Exception:
                    return False

            candidates = [d for d in candidates if doc_has_role(d.get("name"))]

        # Now apply permission filtering for the current user
        filtered_documents_all = [d for d in candidates if check_document_access(d.get("name"), current_user)]

        total = len(filtered_documents_all)
        file_types = sorted({doc.get("file_type") for doc in filtered_documents_all if doc.get("file_type")})
        access_levels = sorted({doc.get("access_level") for doc in filtered_documents_all if doc.get("access_level")})

        if fetch_all:
            # Add absolute fileUrl to each candidate when possible
            for d in filtered_documents_all:
                fa = d.get("file_attachment")
                if fa:
                    try:
                        d["fileUrl"] = get_url(fa)
                    except Exception:
                        d["fileUrl"] = fa

            # return all filtered documents (client will handle filtering/pagination)
            return {
                "success": True,
                "data": filtered_documents_all,
                "pagination": {
                    "limit": total,
                    "offset": 0,
                    "total": total,
                    "next_offset": None,
                },
                "filters": {
                    "file_types": file_types,
                    "access_levels": access_levels,
                },
            }

        # Pagination slice
        start = offset
        end = offset + limit
        page_docs = filtered_documents_all[start:end]

        # Ensure each returned doc has an absolute fileUrl when available
        for d in page_docs:
            fa = d.get("file_attachment")
            if fa:
                try:
                    d["fileUrl"] = get_url(fa)
                except Exception:
                    d["fileUrl"] = fa

        next_offset = offset + limit
        if next_offset >= total:
            next_offset = None

        return {
            "success": True,
            "data": page_docs,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total,
                "next_offset": next_offset,
            },
            "filters": {
                "file_types": file_types,
                "access_levels": access_levels,
            },
        }

    except Exception as e:
        frappe.log_error(f"Error fetching documents: {str(e)}")
        frappe.throw(_("Error fetching documents: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def serve_file(file_url: Optional[str] = None, document_name: Optional[str] = None, download: Optional[int] = 0):
    """
    Serve a file (same-origin) with Content-Disposition inline by default.
    If download=1, serve as attachment to force download.

    Params:
      - file_url: path or url as stored in File.file_url (eg. "/files/...")
      - document_name: alternatively pass a document name to read its file_attachment
      - download: set to 1 to force 'attachment' disposition
    """
    try:
        # Resolve file_url from document if provided
        if document_name and not file_url:
            try:
                doc = frappe.get_doc("AI Document", document_name)
                fa = doc.get("file_attachment")
                if fa:
                    if isinstance(fa, str):
                        file_url = fa
                    elif isinstance(fa, dict):
                        file_url = fa.get("file_url") or fa.get("url") or None
            except Exception:
                pass

        if not file_url:
            frappe.throw("file_url or document_name required")

        # find the File record and content
        file = find_file_by_url(file_url)
        if not file:
            frappe.throw("File not found")

        filename = os.path.basename(file_url)
        content = file.get_content()

        # Guess mime
        mime, _ = mimetypes.guess_type(filename)

        frappe.local.response.filecontent = content
        frappe.local.response.filename = filename
        # Use 'binary' so frappe will stream the file content
        frappe.local.response.type = "binary"

        disposition = 'attachment' if str(download) in ("1", "true", "True") else 'inline'
        headers = {
            'Content-Disposition': f'{disposition}; filename="{filename}"'
        }
        if mime:
            headers['Content-Type'] = mime

        # Optional: allow same-origin fetches — don't open wildcard CORS here
        frappe.local.response_headers = headers

        # No return needed; frappe will use frappe.local.response
        return
    except Exception as e:
        frappe.log_error(f"Error serving file: {str(e)}")
        frappe.throw(str(e))


@frappe.whitelist()
def check_user_document_access(document_id):
    """
    API để check user hiện tại có quyền xem document không
    Sử dụng helper function check_document_access()
    """
    try:
        current_user = frappe.session.user
        has_access = check_document_access(document_id, current_user)
        
        return {
            "success": True,
            "has_access": has_access
        }
    except Exception as e:
        frappe.log_error(f"Error checking user document access: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=True)
def get_roles():
    """Get all available AI Roles"""
    try:
        roles = frappe.get_all("AI Role",
                              fields=["name", "role_name", "is_active", "priority"],
                              order_by="priority asc, role_name asc")
        
        return {
            "success": True,
            "data": roles
        }
    except Exception as e:
        frappe.log_error(f"Error fetching roles: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=True)
def get_document_permissions(document_name):
    """Get permissions for a specific document"""
    try:
        # Check xem user có quyền xem document này không
        current_user = frappe.session.user
        if not check_document_access(document_name, current_user):
            return {
                "success": False,
                "error": "You do not have permission to view this document"
            }
        
        # Get document info
        doc = frappe.get_doc("AI Document", document_name)
        
        # Get all roles (including inactive ones for display purposes)
        roles = frappe.get_all("AI Role",
                              fields=["name", "role_name", "is_active"],
                              order_by="priority asc, role_name asc")
        
        # Build set of allowed role IDs from child table `roles_allowed`
        allowed_role_ids = set()
        for r in doc.get("roles_allowed") or []:
            # Get role ID from child row
            role_id = getattr(r, "role", None) or (r.get("role") if isinstance(r, dict) else None)
            if role_id:
                allowed_role_ids.add(role_id)

        # Get existing permissions
        permissions = {}
        for role in roles:
            # Check if this role ID is in the allowed set
            is_allowed = role.name in allowed_role_ids

            permissions[role.name] = {
                "role_name": role.role_name,
                "can_read": is_allowed,
                "can_write": role.role_name in ["Administrator", "Manager"],
                "can_delete": role.role_name == "Administrator"
            }
        
        return {
            "success": True,
            "data": {
                "document": {
                    "name": doc.name,
                    "title": doc.title,
                    "file_type": doc.file_type,
                    "access_level": doc.access_level,
                    "status": doc.status,
                    "category": doc.category,
                    "description": doc.description,
                    "tags": doc.tags,
                    "roles_allowed": doc.roles_allowed,
                    "departments_allowed": doc.departments_allowed,
                    "content": doc.content
                },
                "permissions": permissions
            }
        }
    except Exception as e:
        frappe.log_error(f"Error fetching document permissions: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=True)
def update_document_permission(document_name, role_name=None, permission_type=None, value=None, updates=None):
    """Update permission for a document-role combination"""
    try:
        # Check xem user có quyền sửa document này không
        current_user = frappe.session.user
        if not check_document_access(document_name, current_user):
            return {
                "success": False,
                "error": "You do not have permission to update this document"
            }
        # Normalize updates: if caller used old-style (role_name + permission_type + value),
        # convert to a small 'updates' payload. Otherwise expect `updates` to be a JSON/dict
        # mapping role_name -> either boolean (can_read) or dict of permissions.
        if updates is None and permission_type is not None and role_name is not None:
            # build updates from single change
            updates = {role_name: {f"{permission_type}": value}}

        # Ensure updates is JSON-serializable dict if passed as string
        if isinstance(updates, str):
            try:
                updates = json.loads(updates)
            except Exception as e:
                frappe.log_error(f"Invalid updates payload: {str(e)}")
                return {"success": False, "error": "Invalid updates payload"}

        if not isinstance(updates, dict):
            return {"success": False, "error": "Missing updates payload"}

        # Enqueue background job to perform the update asynchronously.
        try:
            frappe.enqueue(
                method=_do_update_document_permission,
                queue='long',
                timeout=300,
                document_name=document_name,
                updates=updates,
                user=current_user,
            )
        except Exception as e:
            frappe.log_error(f"Failed to enqueue permission update (callable): {str(e)}")
            return {
                "success": False,
                "error": f"Failed to enqueue background job: {str(e)}"
            }

        # Return immediately; the actual update will run in background
        return {
            "success": True,
            "message": "Permission update enqueued"
        }
    except Exception as e:
        frappe.log_error(f"Error updating document permission: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def _do_update_document_permission(document_name, updates=None, user=None, **kwargs):
    """Background worker: perform permission updates for a document.

    `updates` should be a dict mapping role_name -> boolean or dict. Examples:
      {"AI Role": true}  # shorthand to set can_read
      {"AI Role": {"can_read": true, "can_write": false}}

    This worker applies `can_read` changes by adding/removing rows in the
    `roles_allowed` child table (AI Role Child). Other permission keys are
    currently ignored.
    """
    try:
        frappe.logger().info(f"[BG JOB] Applying updates to {document_name} by {user}: {updates}")

        if not isinstance(updates, dict):
            frappe.log_error("Updates payload must be a dict")
            return {"success": False, "error": "Invalid updates payload"}

        # Load document and ensure child table
        doc = frappe.get_doc("AI Document", document_name)
        if doc is None:
            frappe.log_error(f"AI Document not found: {document_name}")
            return {"success": False, "error": f"Document not found: {document_name}"}

        children = doc.get("roles_allowed") or []

        # Helper to check existence of a role row
        def has_role_row(role_label):
            return any((getattr(c, "role_name", None) == role_label) or (getattr(c, "role_name", None) == role_label) for c in children)

        # Process each role update
        for role_key, payload in updates.items():
            # role_key may be docname or role label
            # Try to load AI Role doc; if not found, use role_key as label
            role_doc = None
            if frappe.db.exists("AI Role", role_key):
                role_doc = frappe.get_doc("AI Role", role_key)

            role_label = None
            if role_doc:
                role_label = getattr(role_doc, "role_name", None) or role_doc.name
            else:
                role_label = role_key

            # Normalize payload to dict
            if isinstance(payload, bool) or isinstance(payload, int):
                # boolean shorthand -> can_read
                perms = {"can_read": bool(payload)}
            elif isinstance(payload, dict):
                perms = payload
            else:
                frappe.log_error(f"Unsupported payload type for role {role_key}: {type(payload)}")
                continue

            # Handle can_read: add/remove child rows
            if "can_read" in perms:
                if perms["can_read"]:
                    # add if missing
                    exists = any((getattr(c, "role_name", None) == role_label) for c in children)
                    if not exists:
                        doc.append("roles_allowed", {"role_name": role_label})
                else:
                    # remove matching rows
                    new_children = [c for c in children if not (getattr(c, "role_name", None) == role_label)]
                    doc.set("roles_allowed", [])
                    for c in new_children:
                        rn = getattr(c, "role_name", None) or (c.get("role_name") if isinstance(c, dict) else None)
                        if rn:
                            doc.append("roles_allowed", {"role_name": rn})
                    # refresh children variable after mutation
                    children = doc.get("roles_allowed") or []

            # Other permission keys can be implemented later (can_write/can_delete)

        # Persist changes
        doc.save(ignore_permissions=True)
        frappe.logger().info(f"[BG JOB] Applied updates to {document_name}")
        return {"success": True, "message": "Background updates applied"}

    except Exception as e:
        frappe.log_error(f"Error in background permission update: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def update_document_metadata(document_name, updates=None):
    """Update basic metadata fields for an AI Document."""
    try:
        current_user = frappe.session.user

        if not document_name:
            return {"success": False, "error": "Missing document name"}

        doc = frappe.get_doc("AI Document", document_name)

        if not doc.has_permission("write", user=current_user):
            return {
                "success": False,
                "error": "You do not have permission to update this document"
            }

        if updates is None:
            updates = frappe.form_dict.get("updates")

        if isinstance(updates, str):
            try:
                updates = json.loads(updates)
            except Exception as err:
                frappe.log_error(f"Invalid metadata updates payload: {err}")
                return {"success": False, "error": "Invalid updates payload"}

        if not isinstance(updates, dict):
            return {"success": False, "error": "Updates must be a dictionary"}

        allowed_fields = {
            "title",
            "category",
            "description",
            "tags",
            "access_level",
            "departments_allowed",
            "content"
        }

        changes = {field: value for field, value in updates.items() if field in allowed_fields}

        if not changes:
            return {"success": False, "error": "No valid fields to update"}

        for field, value in changes.items():
            doc.set(field, value)

        if "access_level" in changes:
            doc.vector_collection = doc.get_collection_name()

        doc.save()
        frappe.db.commit()

        return {
            "success": True,
            "message": "Document updated successfully",
            "data": {
                "document": {
                    "name": doc.name,
                    "title": doc.title,
                    "category": doc.category,
                    "description": doc.description,
                    "tags": doc.tags,
                    "access_level": doc.access_level,
                    "departments_allowed": doc.departments_allowed,
                    "status": doc.status,
                    "file_type": doc.file_type,
                    "vector_collection": doc.vector_collection,
                    "content": doc.get("content")
                }
            }
        }

    except Exception as e:
        frappe.log_error(f"Error updating document metadata: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=True)
def bulk_update_document_permissions(document_name, permissions_data):
    """Update multiple permissions for a document at once"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Check xem user có quyền sửa document này không
        current_user = frappe.session.user
        if not check_document_access(document_name, current_user):
            return {
                "success": False,
                "error": "You do not have permission to update this document"
            }
        
        if isinstance(permissions_data, str):
            permissions_data = json.loads(permissions_data)
        
        # Use logger instead of log_error for debug info
        logger.info(f"Received permissions_data for {document_name}: {json.dumps(permissions_data, indent=2)}")
        
        # Get document
        doc = frappe.get_doc("AI Document", document_name)
        
        logger.info(f"Current roles_allowed: {[r.role for r in doc.get('roles_allowed') or []]}")
        
        # Clear existing roles_allowed
        doc.set("roles_allowed", [])
        
        # Add roles that have can_read = True
        roles_added = []
        for role_id, permissions in permissions_data.items():
            if permissions.get("can_read", False):
                doc.append("roles_allowed", {
                    "role": role_id,
                    "is_active": 1,
                    "priority": 1
                })
                roles_added.append(role_id)
        
        logger.info(f"Adding roles: {roles_added}")
        
        # Save document
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        logger.info(f"Successfully saved. New roles_allowed: {[r.role for r in doc.get('roles_allowed') or []]}")
        
        return {
            "success": True,
            "message": f"Updated permissions for {len(roles_added)} roles"
        }
    except Exception as e:
        # Only log_error for actual errors, with short title
        frappe.log_error(
            title=f"Permissions Update Error: {document_name[:50]}",
            message=f"Document: {document_name}\nError: {str(e)}\nPermissions Data: {json.dumps(permissions_data, indent=2)}"
        )
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=True)
def bulk_update_documents_permissions(document_names=None, role_id=None, grant=None):
    """
    Bulk grant/revoke a single role for multiple AI Document records.

    Args (from frappe.form_dict or direct):
        document_names: JSON list of document names, or Python list
        role_id: AI Role ID (e.g. "AI-ROLE-0001")
        grant: 1/0 or true/false — grant if truthy, revoke otherwise

    Returns:
        { success: bool, updated: int, processed: int, errors: list[str] }
    """
    try:
        # Resolve args from form_dict if not passed explicitly
        if document_names is None:
            document_names = frappe.form_dict.get("document_names")
        if role_id is None:
            role_id = frappe.form_dict.get("role_id")
        if grant is None:
            grant = frappe.form_dict.get("grant")

        # Normalize document_names into a list
        if isinstance(document_names, str):
            try:
                document_names = json.loads(document_names)
            except Exception:
                # fallback: comma-separated
                document_names = [d.strip() for d in document_names.split(',') if d.strip()]

        if not isinstance(document_names, list) or not document_names:
            return {"success": False, "error": "document_names must be a non-empty list"}

        if not role_id:
            return {"success": False, "error": "Missing role_id"}

        # Normalize grant to boolean
        if isinstance(grant, str):
            grant_bool = str(grant).lower() in ("1", "true", "yes", "y")
        else:
            grant_bool = bool(grant)

        current_user = frappe.session.user
        updated = 0
        errors = []

        for name in document_names:
            try:
                # Permission check
                if not check_document_access(name, current_user):
                    errors.append(f"No access to document {name}")
                    continue

                doc = frappe.get_doc("AI Document", name)

                # Build existing set of role ids on child table
                existing_roles = set()
                for r in doc.get("roles_allowed") or []:
                    rid = getattr(r, "role", None) or (r.get("role") if isinstance(r, dict) else None)
                    if rid:
                        existing_roles.add(rid)

                if grant_bool:
                    if role_id not in existing_roles:
                        doc.append("roles_allowed", {
                            "role": role_id,
                            "is_active": 1,
                            "priority": 1,
                        })
                        doc.save(ignore_permissions=True)
                        updated += 1
                else:
                    # revoke: remove rows matching role_id if present
                    if role_id in existing_roles:
                        new_rows = []
                        for r in doc.get("roles_allowed") or []:
                            rid = getattr(r, "role", None) or (r.get("role") if isinstance(r, dict) else None)
                            if rid != role_id:
                                new_rows.append(r)
                        doc.set("roles_allowed", new_rows)
                        doc.save(ignore_permissions=True)
                        updated += 1
            except Exception as err:
                frappe.log_error(f"Bulk update role {role_id} on {name} failed: {err}")
                errors.append(f"{name}: {str(err)}")

        try:
            frappe.db.commit()
        except Exception:
            # In case autocommit is enabled or commit not required
            pass

        return {
            "success": True,
            "processed": len(document_names),
            "updated": updated,
            "errors": errors,
        }
    except Exception as e:
        frappe.log_error(f"Error in bulk_update_documents_permissions: {str(e)}")
        return {"success": False, "error": str(e)}
