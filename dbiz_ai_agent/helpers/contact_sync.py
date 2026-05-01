import frappe


def sync_ai_role_contacts():
    """Ensure Contact AI Roles table mirrors AI Role assignments."""
    # During fresh install, AI Role doctype (and its table) may not exist yet.
    # In that case, safely skip syncing to avoid errors in install/migrate hooks.
    if not frappe.db.table_exists("AI Role"):
        return

    role_names = frappe.get_all("AI Role", pluck="name")

    for role_name in role_names:
        try:
            role_doc = frappe.get_doc("AI Role", role_name)
            if hasattr(role_doc, "sync_contact_ai_roles"):
                role_doc.sync_contact_ai_roles(full_sync=True)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"AI Role Contact Sync Hook failed for role {role_name}",
            )

