import frappe

def handle_cors():
    """
    Xử lý CORS sau khi request được xử lý
    Set headers cho tất cả response
    """
    # Lấy origin từ request
    origin = frappe.get_request_header("Origin")
    
    if origin:
        # Set CORS headers cho response
        frappe.local.response.setdefault("Access-Control-Allow-Origin", origin)
        frappe.local.response.setdefault("Access-Control-Allow-Credentials", "true")
        frappe.local.response.setdefault("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        frappe.local.response.setdefault("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Frappe-CSRF-Token, X-Requested-With")
        frappe.local.response.setdefault("Access-Control-Max-Age", "86400")
        frappe.local.response.setdefault("Vary", "Origin")

