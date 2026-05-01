import frappe
from frappe.model.document import Document


class UsersAllowed(Document):
    """Parent DocType listing users explicitly allowed for AI documents."""
    pass
