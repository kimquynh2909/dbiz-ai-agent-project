from typing import Optional
import json
import frappe
from frappe import _
from frappe.utils.password import update_password


def Get_Chatbot_Config(title: Optional[str] = None):
    """Helper: trả về Chatbot Configuration đang hoạt động hoặc theo title."""
    if title:
        name = frappe.db.get_value("Chatbot Configuration", {"title": title}, "name")
        if name:
            return frappe.get_doc("Chatbot Configuration", name)

    active_name = frappe.db.get_value("Chatbot Configuration", {"is_active": 1}, "name")
    if active_name:
        return frappe.get_doc("Chatbot Configuration", active_name)
    frappe.throw(_("Vui lòng thiết lập một cấu hình Chatbot đang hoạt động trước khi sử dụng trợ lý."))

@frappe.whitelist(allow_guest=True)
def get_assistant_config():
    # Cache 5 phút để giảm truy vấn
    cached = frappe.cache().get_value("active_chatbot_config")
    if cached:
        return cached

    cfg = Get_Chatbot_Config()
    quick_questions = [
        {
            "question_text": q.question_text,
            "icon": q.icon or "MessageSquare",
            "is_active": q.is_active,
            "sort_order": q.sort_order,
        }
        for q in cfg.quick_questions if q.is_active
    ]
    quick_questions.sort(key=lambda x: x.get("sort_order", 0))

    result = {
        "title": cfg.greeting_message or cfg.title,
        "description": cfg.description,
        "assistant_name": cfg.assistant_name or "AI Assistant",
        "greeting_message": cfg.greeting_message,
        "support_info": cfg.support_info,
        "avatar_image": cfg.avatar_image,
        "quick_questions": quick_questions,
    }
    frappe.cache().set_value("active_chatbot_config", result, expires_in_sec=300)
    return result


@frappe.whitelist(allow_guest=True, methods=["GET", "OPTIONS"])
def get_chatbot_config():
    """
    Lấy cấu hình chatbot cho widget (avatar, title, etc)
    Hỗ trợ CORS
    """
    # Xử lý CORS headers
    origin = frappe.get_request_header("Origin")
    if origin:
        frappe.local.response["Access-Control-Allow-Origin"] = origin
        frappe.local.response["Access-Control-Allow-Credentials"] = "true"
        frappe.local.response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        frappe.local.response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        frappe.local.response["Access-Control-Max-Age"] = "86400"
    
    # Xử lý OPTIONS preflight
    if frappe.request.method == "OPTIONS":
        return {"success": True}
    
    # Trả về config từ get_assistant_config
    return get_assistant_config()


@frappe.whitelist(allow_guest=True)
def reset_password(user, new_password):
    # Validate
    if not user or not new_password:
        frappe.throw(_("User and new password are required"))
    if not frappe.db.exists("User", user):
        frappe.throw(_("User not found"))
    user_doc = frappe.get_doc("User", user)
    if not user_doc.enabled:
        frappe.throw(_("User account is disabled"))
    if len(new_password) < 8:
        frappe.throw(_("Password must be at least 8 characters long"))

    update_password(user, new_password)
    frappe.logger().info(f"Password reset successful for user: {user}")
    return {"success": True, "message": _("Password reset successfully")}




@frappe.whitelist(allow_guest=True)
def get_socketio_client_config():
    """Return Socket.IO client config if server URL is set in site_config.

    Read `socketio_server_url` and optional `socketio_namespace`,
    `socketio_auth_token`, and `socketio_path` from site_config or env vars.
    
    In production, automatically converts localhost URLs to public URLs
    based on the current request origin.
    """
    try:
        server_url = None
        namespace = '/'
        auth_token = None
        path = '/socket.io/'
        try:
            server_url = (getattr(frappe, 'conf', {}) or {}).get('socketio_server_url')
            namespace = (getattr(frappe, 'conf', {}) or {}).get('socketio_namespace') or '/'
            auth_token = (getattr(frappe, 'conf', {}) or {}).get('socketio_auth_token')
            path = (getattr(frappe, 'conf', {}) or {}).get('socketio_path') or '/socket.io/'
        except Exception:
            server_url = None
            namespace = '/'
            auth_token = None
            path = '/socket.io/'

        # Allow env var override in development
        import os
        if not server_url:
            server_url = os.environ.get('SOCKETIO_SERVER_URL')
        if not namespace:
            namespace = os.environ.get('SOCKETIO_NAMESPACE', '/')
        if not auth_token:
            auth_token = os.environ.get('SOCKETIO_AUTH_TOKEN')
        if not path or path == '/socket.io/':
            path = os.environ.get('SOCKETIO_PATH', '/socket.io/')

        # CRITICAL FIX: Auto-detect production and convert localhost to public URL
        if server_url:
            try:
                # Get request origin/host from headers
                origin = frappe.get_request_header("Origin")
                host_header = frappe.get_request_header("Host")
                
                # Determine actual hostname
                current_host = None
                current_protocol = 'https'  # Default to HTTPS for production
                
                if origin:
                    # Origin is full URL like "https://ai.dbiz.com"
                    if origin.startswith('http://') or origin.startswith('https://'):
                        current_protocol = 'https' if origin.startswith('https://') else 'http'
                        current_host = origin.split('://')[-1].split('/')[0].split(':')[0]
                    else:
                        current_host = origin.split(':')[0]
                elif host_header:
                    # Host header is just hostname like "ai.dbiz.com:443" or "ai.dbiz.com"
                    current_host = host_header.split(':')[0]
                    # Check if HTTPS from request
                    if frappe.get_request_header("X-Forwarded-Proto") == 'https':
                        current_protocol = 'https'
                
                # Check if server_url is localhost but we're in production
                is_localhost_url = server_url and (
                    'localhost' in server_url.lower() or 
                    '127.0.0.1' in server_url or
                    server_url.startswith('http://localhost') or
                    server_url.startswith('http://127.0.0.1')
                )
                
                # Check if request is from production (not localhost)
                is_production_request = current_host and (
                    'localhost' not in current_host.lower() and
                    '127.0.0.1' not in current_host and
                    current_host not in ['localhost', '127.0.0.1']
                )
                
                # If localhost URL but production request, convert to public URL
                if is_localhost_url and is_production_request and current_host:
                    # Use current request protocol and host
                    server_url = f"{current_protocol}://{current_host}"
                    frappe.logger().info(
                        f"[Socket.IO Config] Converted localhost URL to public URL: {server_url} "
                        f"(origin: {origin}, host: {host_header}, protocol: {current_protocol})"
                    )
            except Exception as url_convert_err:
                # Log but don't fail - use original URL
                frappe.log_error(f"Failed to convert localhost URL: {url_convert_err}")

        enabled = bool(server_url)
        return {
            'enabled': enabled,
            'serverUrl': server_url,
            'namespace': namespace,
            'authToken': auth_token,
            'path': path,  # Explicit path for proxy compatibility
        }
    except Exception as e:
        frappe.log_error(f"get_socketio_client_config error: {e}")
        # Return disabled config rather than raising (so FE can fallback)
        return {
            'enabled': False,
            'serverUrl': None,
            'namespace': '/',
            'path': '/socket.io/',
        }

@frappe.whitelist(allow_guest=True)
def send_contact_request(full_name, email, phone, company, subject, message):
    """
    Handle contact form submission
    """
    if not all([full_name, email, phone, subject, message]):
        frappe.throw(_("All required fields must be filled"))
    contact_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company": company or "",
        "subject": subject,
        "message": message,
        "timestamp": frappe.utils.now(),
    }
    frappe.logger().info(f"Contact request received: {json.dumps(contact_data, indent=2)}")
    return {"success": True, "message": _("Contact request submitted successfully")}

@frappe.whitelist(allow_guest=True, methods=["POST", "OPTIONS"])
def login(username=None, password=None):
    """
    Đăng nhập cho widget
    Hỗ trợ CORS preflight (OPTIONS) và POST request
    """
    # Xử lý CORS headers
    origin = frappe.get_request_header("Origin")
    if origin:
        frappe.local.response["Access-Control-Allow-Origin"] = origin
        frappe.local.response["Access-Control-Allow-Credentials"] = "true"
        frappe.local.response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        frappe.local.response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Frappe-CSRF-Token"
        frappe.local.response["Access-Control-Max-Age"] = "86400"
    
    # Xử lý OPTIONS preflight
    if frappe.request.method == "OPTIONS":
        return {"success": True}
    
    if not username or not password:
        frappe.throw(_("Username/email và mật khẩu là bắt buộc"))

    login_manager = frappe.auth.LoginManager()
    login_manager.authenticate(user=username, pwd=password)
    login_manager.post_login()

    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)
    return {
        "success": True,
        "user": {
            "name": user_doc.name,
            "full_name": user_doc.full_name,
            "email": user_doc.email,
            "roles": [r.role for r in user_doc.get("roles", [])],
        },
    }

 
        
@frappe.whitelist()
def Get_Current_User():
    return frappe.session.user


@frappe.whitelist(allow_guest=True)
def get_logged_user():
    user = frappe.session.user
    if not user or user == "Guest":
        return None
    return user

@frappe.whitelist(allow_guest=True, methods=["POST", "OPTIONS"])
def verify_widget_secret(secret=None):
    """
    Xác thực widget secret cho embedded widget
    Hỗ trợ CORS preflight (OPTIONS) và POST request
    """
    # Xử lý CORS headers cho mọi request
    origin = frappe.get_request_header("Origin")
    if origin:
        frappe.local.response["Access-Control-Allow-Origin"] = origin
        frappe.local.response["Access-Control-Allow-Credentials"] = "true"
        frappe.local.response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        frappe.local.response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Frappe-CSRF-Token"
        frappe.local.response["Access-Control-Max-Age"] = "86400"
    
    # Xử lý OPTIONS preflight request
    if frappe.request.method == "OPTIONS":
        return {"success": True}
    
    # Tạm thời bypass verification cho development
    # TODO: Implement proper secret verification khi deploy production
    return {"success": True, "verified": True}
    
    # Code verification thực sự (comment lại tạm thời):
    # settings_secret = None
    # try:
    #     settings = frappe.get_cached_doc('AI Agent Settings')
    #     settings_secret = settings.get_password('secret_key', raise_exception=False)
    # except Exception:
    #     settings_secret = None
    # 
    # expected = (
    #     settings_secret
    #     or frappe.conf.get('dbiz_widget_secret')
    #     or frappe.conf.get('widget_secret')
    #     or frappe.conf.get('dbiz_embed_secret')
    # )
    # if not expected:
    #     frappe.throw(_('Widget secret chưa được cấu hình'), frappe.PermissionError)
    # if not secret:
    #     frappe.throw(_('Thiếu khóa xác thực widget'), frappe.PermissionError)
    # if str(secret) != str(expected):
    #     frappe.throw(_('Khóa xác thực widget không hợp lệ'), frappe.PermissionError)
    # return {"success": True}


 
