import frappe
from frappe import _
import json

def get_ai_agent_settings():
    """Return (settings_doc, chunk_size, chunk_overlap) for AI Agent Settings."""
    try:
        settings = frappe.get_single("AI Agent Settings")
        chunk_size = getattr(settings, "chunk_size", 1000)
        chunk_overlap = getattr(settings, "chunk_overlap", 200)
        return settings, chunk_size, chunk_overlap
    except Exception as e:
        frappe.log_error(f"get_ai_agent_settings failed: {str(e)}")
        return None, 1000, 200

@frappe.whitelist()
def get_settings():
    """Get AI Agent Settings"""
    try:
        # Get AI Agent Settings document (single doctype)
        settings_doc = None
        try:
            settings_doc = frappe.get_single("AI Agent Settings")
        except frappe.DoesNotExistError:
            # Create default settings if doesn't exist
            settings_doc = frappe.get_doc({
                "doctype": "AI Agent Settings",
                "system_name": "AI IT Assistant",
                "language": "vi",
                "theme": "light",
                "timezone": "Asia/Ho_Chi_Minh",
                "date_format": "dd/mm/yyyy",
                "openai_api_key": "",
                "model": "gpt-4o-mini",
                "embedding_model": "text-embedding-3-small",
                "temperature": 0.7,
                "max_tokens": 1000,
                "context_window": 5,
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "retrieval_docs": 3
            })
            settings_doc.insert(ignore_permissions=True)
            frappe.db.commit()
        
        # Format settings for frontend
        settings_data = {
            "general": {
                "system_name": getattr(settings_doc, 'system_name', 'AI IT Assistant'),
                "language": getattr(settings_doc, 'language', 'vi'),
                "theme": getattr(settings_doc, 'theme', 'light'),
                "timezone": getattr(settings_doc, 'timezone', 'Asia/Ho_Chi_Minh'),
                "date_format": getattr(settings_doc, 'date_format', 'dd/mm/yyyy')
            },
            "ai": {
                "openai_api_key": getattr(settings_doc, 'openai_api_key', ''),
                "model": getattr(settings_doc, 'model', 'gpt-4o-mini'),
                "embedding_model": getattr(settings_doc, 'embedding_model', 'text-embedding-3-small'),
                "temperature": float(getattr(settings_doc, 'temperature', 0.7)),
                "max_tokens": int(getattr(settings_doc, 'max_tokens', 1000)),
                "context_window": int(getattr(settings_doc, 'context_window', 5))
            },
            "rag": {
                "chunk_size": int(getattr(settings_doc, 'chunk_size', 1000)),
                "chunk_overlap": int(getattr(settings_doc, 'chunk_overlap', 200)),
                "retrieval_docs": int(getattr(settings_doc, 'retrieval_docs', 3))
            }
        }
        
        return {
            "success": True,
            "data": settings_data
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Settings API Error")
        frappe.throw(_("Failed to get settings: {0}").format(str(e)))

@frappe.whitelist()
def save_settings(settings_data):
    """Save AI Agent Settings"""
    try:
        # Parse settings data if it's a string
        if isinstance(settings_data, str):
            settings_data = json.loads(settings_data)
        
        # Get or create AI Agent Settings document
        try:
            settings_doc = frappe.get_single("AI Agent Settings")
        except frappe.DoesNotExistError:
            settings_doc = frappe.get_doc({"doctype": "AI Agent Settings"})
        
        # Update general settings
        if "general" in settings_data:
            general = settings_data["general"]
            settings_doc.system_name = general.get("system_name", "AI IT Assistant")
            settings_doc.language = general.get("language", "vi")
            settings_doc.theme = general.get("theme", "light")
            settings_doc.timezone = general.get("timezone", "Asia/Ho_Chi_Minh")
            settings_doc.date_format = general.get("date_format", "dd/mm/yyyy")
        
        # Update AI settings
        if "ai" in settings_data:
            ai = settings_data["ai"]
            settings_doc.openai_api_key = ai.get("openai_api_key", "")
            settings_doc.model = ai.get("model", "gpt-4o-mini")
            settings_doc.embedding_model = ai.get("embedding_model", "text-embedding-ada-002")
            settings_doc.temperature = float(ai.get("temperature", 0.7))
            settings_doc.max_tokens = int(ai.get("max_tokens", 1000))
            settings_doc.context_window = int(ai.get("context_window", 5))
        
        # Update RAG settings
        if "rag" in settings_data:
            rag = settings_data["rag"]
            settings_doc.chunk_size = int(rag.get("chunk_size", 1000))
            settings_doc.chunk_overlap = int(rag.get("chunk_overlap", 200))
            settings_doc.retrieval_docs = int(rag.get("retrieval_docs", 3))
        
        # Save the document
        if settings_doc.is_new():
            settings_doc.insert(ignore_permissions=True)
        else:
            settings_doc.save(ignore_permissions=True)
        
        frappe.db.commit()
        
        # Log the update
        frappe.logger().info("AI Agent Settings updated successfully")
        
        return {
            "success": True,
            "message": _("Settings saved successfully")
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Save Settings API Error")
        frappe.throw(_("Failed to save settings: {0}").format(str(e)))

@frappe.whitelist()
def test_openai_connection(api_key, model="gpt-4o-mini"):
    """Test OpenAI API connection"""
    try:
        import openai
        
        # Set API key
        openai.api_key = api_key
        
        # Test with a simple completion
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        if response and response.choices:
            return {
                "success": True,
                "message": _("OpenAI API connection successful"),
                "response": response.choices[0].message.content.strip()
            }
        else:
            return {
                "success": False,
                "message": _("No response from OpenAI API")
            }
            
    except ImportError:
        return {
            "success": False,
            "message": _("OpenAI library not installed. Please install: pip install openai")
        }
    except Exception as e:
        return {
            "success": False,
            "message": _("OpenAI API test failed: {0}").format(str(e))
        }

@frappe.whitelist()
def get_available_models():
    """Get available OpenAI models"""
    try:
        # Return predefined list of models
        models = [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Most capable GPT-3.5 model, optimized for chat",
                "max_tokens": 4096,
                "cost_per_1k": 0.002
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "More capable than GPT-3.5, better at complex tasks",
                "max_tokens": 8192,
                "cost_per_1k": 0.03
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "Latest GPT-4 model with improved performance",
                "max_tokens": 128000,
                "cost_per_1k": 0.01
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "description": "Multimodal flagship model, cheaper and faster than GPT-4 Turbo",
                "max_tokens": 128000,
                "cost_per_1k": 0.005
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "description": "Affordable and intelligent small model for fast, lightweight tasks",
                "max_tokens": 128000,
                "cost_per_1k": 0.00015
            }
        ]
        
        embedding_models = [
            {
                "id": "text-embedding-ada-002",
                "name": "text-embedding-ada-002",
                "description": "Most capable embedding model",
                "dimensions": 1536,
                "cost_per_1k": 0.0001
            },
            {
                "id": "text-embedding-3-small",
                "name": "text-embedding-3-small",
                "description": "Increased performance over 2nd generation ada embedding model",
                "dimensions": 1536,
                "cost_per_1k": 0.00002
            },
            {
                "id": "text-embedding-3-large",
                "name": "text-embedding-3-large",
                "description": "Most capable embedding model for both english and non-english tasks",
                "dimensions": 3072,
                "cost_per_1k": 0.00013
            }
        ]
        
        return {
            "success": True,
            "data": {
                "chat_models": models,
                "embedding_models": embedding_models
            }
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Available Models API Error")
        frappe.throw(_("Failed to get available models: {0}").format(str(e)))

@frappe.whitelist()
def get_system_info():
    """Get system information for settings page"""
    try:
        import platform
        import sys
        
        system_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "frappe_version": frappe.__version__,
            "site": frappe.local.site,
            "user": frappe.session.user,
            "timezone": frappe.utils.get_system_timezone(),
            "database": frappe.conf.db_type or "mariadb"
        }
        
        return {
            "success": True,
            "data": system_info
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get System Info API Error")
        frappe.throw(_("Failed to get system info: {0}").format(str(e)))

@frappe.whitelist()
def reset_to_defaults():
    """Reset settings to default values"""
    try:
        # Get AI Agent Settings document
        try:
            settings_doc = frappe.get_single("AI Agent Settings")
        except frappe.DoesNotExistError:
            settings_doc = frappe.get_doc({"doctype": "AI Agent Settings"})
        
        # Reset to default values
        settings_doc.system_name = "AI IT Assistant"
        settings_doc.language = "vi"
        settings_doc.theme = "light"
        settings_doc.timezone = "Asia/Ho_Chi_Minh"
        settings_doc.date_format = "dd/mm/yyyy"
        settings_doc.model = "gpt-4o-mini"
        settings_doc.embedding_model = "text-embedding-ada-002"
        settings_doc.temperature = 0.7
        settings_doc.max_tokens = 1000
        settings_doc.context_window = 5
        settings_doc.chunk_size = 1000
        settings_doc.chunk_overlap = 200
        settings_doc.retrieval_docs = 3
        
        # Don't reset API key for security
        
        # Save the document
        if settings_doc.is_new():
            settings_doc.insert(ignore_permissions=True)
        else:
            settings_doc.save(ignore_permissions=True)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Settings reset to defaults successfully")
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reset Settings API Error")
        frappe.throw(_("Failed to reset settings: {0}").format(str(e)))
