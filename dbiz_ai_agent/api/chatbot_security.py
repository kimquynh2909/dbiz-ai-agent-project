import frappe
from frappe import _
import json
import re
from datetime import datetime, timedelta
import hashlib


class ChatbotSecurityMiddleware:
	"""Security middleware for chatbot queries"""
	
	def __init__(self):
		self.rate_limits = {}
		self.sensitive_patterns = [
			r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
			r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
			r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
			r'\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b',  # Phone
			r'\bpassword\s*[:=]\s*\S+\b',  # Password
		]
	
	def validate_query(self, query, user=None):
		"""Validate and sanitize query"""
		if not user:
			user = frappe.session.user
		
		start_time = datetime.now()
		
		# 1. Rate limiting
		if self.exceeds_rate_limit(user):
			self.log_security_event(user, query, "RATE_LIMIT_EXCEEDED")
			frappe.throw(_("Rate limit exceeded. Please try again later."))
		
		# 2. Input sanitization
		sanitized_query = self.sanitize_input(query)
		
		# 3. Check for sensitive data patterns
		security_flags = []
		if self.contains_sensitive_pattern(query):
			security_flags.append("SENSITIVE_DATA_DETECTED")
			self.log_security_event(user, query, "SENSITIVE_DATA_IN_QUERY")
		
		# 4. Check for injection attempts
		if self.detect_injection_attempt(query):
			security_flags.append("INJECTION_ATTEMPT")
			self.log_security_event(user, query, "INJECTION_ATTEMPT")
			frappe.throw(_("Invalid query detected. Please rephrase your question."))
		
		# 5. Check query length
		if len(query) > 5000:
			security_flags.append("QUERY_TOO_LONG")
			frappe.throw(_("Query too long. Please shorten your question."))
		
		return {
			"sanitized_query": sanitized_query,
			"security_flags": security_flags,
			"validation_time": (datetime.now() - start_time).total_seconds() * 1000
		}
	
	def exceeds_rate_limit(self, user):
		"""Check if user exceeds rate limit"""
		from dbiz_ai_agent.dbiz_ai_agent.doctype.chatbot_permission.chatbot_permission import get_user_chatbot_permissions
		
		permissions = get_user_chatbot_permissions(user)
		if not permissions:
			return False
		
		# Get the most restrictive rate limit
		min_rate_limit = min([perm.get("rate_limit_per_hour", 100) for perm in permissions])
		
		# Check current hour's usage
		current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
		
		usage_count = frappe.db.count("Chatbot Access Log", {
			"user": user,
			"timestamp": [">=", current_hour]
		})
		
		return usage_count >= min_rate_limit
	
	def sanitize_input(self, query):
		"""Sanitize user input"""
		# Remove potentially dangerous characters
		sanitized = re.sub(r'[<>"\']', '', query)
		
		# Remove SQL injection patterns
		sql_patterns = [
			r'\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)\b',
			r'--',
			r'/\*.*?\*/',
			r'\bunion\b.*\bselect\b',
			r'\bor\b.*\b1\s*=\s*1\b'
		]
		
		for pattern in sql_patterns:
			sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
		
		return sanitized.strip()
	
	def contains_sensitive_pattern(self, query):
		"""Check if query contains sensitive data patterns"""
		for pattern in self.sensitive_patterns:
			if re.search(pattern, query, re.IGNORECASE):
				return True
		return False
	
	def detect_injection_attempt(self, query):
		"""Detect potential injection attempts"""
		injection_patterns = [
			r'\b(script|javascript|vbscript)\b',
			r'<[^>]*>',  # HTML tags
			r'\b(eval|exec|system|shell_exec)\b',
			r'\$\{.*\}',  # Template injection
			r'\{\{.*\}\}',  # Template injection
		]
		
		for pattern in injection_patterns:
			if re.search(pattern, query, re.IGNORECASE):
				return True
		return False
	
	def filter_response(self, response, user=None):
		"""Filter and mask sensitive data in response"""
		if not user:
			user = frappe.session.user
		
		from dbiz_ai_agent.dbiz_ai_agent.doctype.chatbot_permission.chatbot_permission import get_user_chatbot_permissions
		
		permissions = get_user_chatbot_permissions(user)
		should_mask = any(perm.get("sensitive_data_masking") for perm in permissions)
		
		if not should_mask:
			return response
		
		# Apply masking
		if isinstance(response, str):
			return self.mask_sensitive_text(response)
		elif isinstance(response, dict):
			return self.mask_sensitive_dict(response)
		elif isinstance(response, list):
			return [self.filter_response(item, user) for item in response]
		
		return response
	
	def mask_sensitive_text(self, text):
		"""Mask sensitive patterns in text"""
		masked_text = text
		
		# Mask email addresses
		masked_text = re.sub(
			r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
			lambda m: m.group()[:2] + '*' * (len(m.group()) - 4) + m.group()[-2:],
			masked_text
		)
		
		# Mask phone numbers
		masked_text = re.sub(
			r'\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b',
			'***-***-****',
			masked_text
		)
		
		# Mask SSN
		masked_text = re.sub(
			r'\b\d{3}-\d{2}-\d{4}\b',
			'***-**-****',
			masked_text
		)
		
		# Mask credit card numbers
		masked_text = re.sub(
			r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
			'****-****-****-****',
			masked_text
		)
		
		return masked_text
	
	def mask_sensitive_dict(self, data):
		"""Mask sensitive fields in dictionary"""
		sensitive_fields = [
			'password', 'pin', 'ssn', 'social_security', 'credit_card',
			'bank_account', 'salary', 'wage', 'income', 'tax_id'
		]
		
		masked_data = {}
		for key, value in data.items():
			if any(field in key.lower() for field in sensitive_fields):
				masked_data[key] = self.mask_value(value)
			elif isinstance(value, (dict, list)):
				masked_data[key] = self.filter_response(value)
			else:
				masked_data[key] = value
		
		return masked_data
	
	def mask_value(self, value):
		"""Mask a single value"""
		if not value:
			return value
		
		value_str = str(value)
		if len(value_str) <= 4:
			return "*" * len(value_str)
		else:
			return value_str[:2] + "*" * (len(value_str) - 4) + value_str[-2:]
	
	def log_security_event(self, user, query, event_type):
		"""Log security events"""
		try:
			frappe.get_doc({
				"doctype": "Chatbot Access Log",
				"user": user,
				"query_text": query[:500],  # Truncate for storage
				"query_type": "Security Event",
				"security_flags": event_type,
				"blocked_reason": event_type if event_type in ["INJECTION_ATTEMPT", "RATE_LIMIT_EXCEEDED"] else None,
				"admin_notified": event_type in ["INJECTION_ATTEMPT", "SENSITIVE_DATA_IN_QUERY"]
			}).insert(ignore_permissions=True)
			
			frappe.db.commit()
		except Exception as e:
			frappe.log_error(f"Failed to log security event: {str(e)}")


@frappe.whitelist()
def secure_chatbot_query(query, query_type="General Chat"):
	"""Secure wrapper for chatbot queries"""
	user = frappe.session.user
	start_time = datetime.now()
	
	# Initialize security middleware
	security = ChatbotSecurityMiddleware()
	
	try:
		# Validate query
		validation_result = security.validate_query(query, user)
		sanitized_query = validation_result["sanitized_query"]
		security_flags = validation_result["security_flags"]
		
		# Get user permissions
		from dbiz_ai_agent.dbiz_ai_agent.doctype.chatbot_permission.chatbot_permission import (
			get_user_chatbot_permissions, get_chatbot_query_filters
		)
		
		user_permissions = get_user_chatbot_permissions(user)
		query_filters = get_chatbot_query_filters(user)
		
		# Process query (implement your actual chatbot logic here)
		response = process_chatbot_query(sanitized_query, query_filters, user_permissions)
		
		# Filter response
		filtered_response = security.filter_response(response, user)
		
		# Calculate response time
		response_time = (datetime.now() - start_time).total_seconds() * 1000
		
		# Log access
		from dbiz_ai_agent.dbiz_ai_agent.doctype.chatbot_access_log.chatbot_access_log import log_chatbot_access
		
		log_chatbot_access(
			query_text=query,
			query_type=query_type,
			accessed_documents=response.get("accessed_documents", []) if isinstance(response, dict) else [],
			vector_collections_used=",".join(query_filters.get("collections", [])) if query_filters.get("collections") else None,
			permissions_applied=user_permissions,
			response_time_ms=int(response_time),
			results_count=len(response.get("results", [])) if isinstance(response, dict) else 1,
			sensitive_data_masked=any("SENSITIVE" in flag for flag in security_flags),
			security_flags=",".join(security_flags) if security_flags else None
		)
		
		return {
			"success": True,
			"response": filtered_response,
			"response_time_ms": int(response_time),
			"security_applied": len(security_flags) > 0
		}
		
	except Exception as e:
		# Log error
		from dbiz_ai_agent.dbiz_ai_agent.doctype.chatbot_access_log.chatbot_access_log import log_chatbot_access
		
		log_chatbot_access(
			query_text=query,
			query_type=query_type,
			blocked_reason=str(e),
			response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
		)
		
		return {
			"success": False,
			"error": str(e),
			"response_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
		}


def process_chatbot_query(query, filters, permissions):
	"""Process chatbot query with permissions (implement your logic here)"""
	# This is a placeholder - implement your actual chatbot processing logic
	# This should integrate with your Qdrant vector store, LLM, and other components
	
	return {
		"response": f"Processed query: {query}",
		"accessed_documents": ["DOC-001", "DOC-002"],
		"results": [
			{"title": "Sample Result 1", "content": "Sample content 1"},
			{"title": "Sample Result 2", "content": "Sample content 2"}
		]
	}


@frappe.whitelist()
def get_ai_documents_with_permission(filters=None, fields=None):
	"""Get AI Documents with both Frappe and Chatbot permissions"""
	user = frappe.session.user
	
	# Check Frappe permission
	if not frappe.has_permission("AI Document", "read", user=user):
		frappe.throw(_("Insufficient permissions to access AI Documents"))
	
	# Get user permissions for filtering
	from dbiz_ai_agent.dbiz_ai_agent.doctype.chatbot_permission.chatbot_permission import get_user_chatbot_permissions
	
	user_permissions = get_user_chatbot_permissions(user)
	user_roles = frappe.get_roles(user)
	
	# Build access level filter
	allowed_access_levels = []
	for perm in user_permissions:
		access_level = perm.get("access_level")
		if access_level and access_level not in allowed_access_levels:
			allowed_access_levels.append(access_level)
	
	# Apply filters
	final_filters = filters or {}
	
	# Add access level filter if permissions exist
	if allowed_access_levels:
		final_filters["access_level"] = ["in", allowed_access_levels]
	
	# Apply custom filters from permissions
	for perm in user_permissions:
		if perm.get("custom_filters"):
			try:
				custom_filters = json.loads(perm["custom_filters"])
				final_filters.update(custom_filters)
			except json.JSONDecodeError:
				continue
	
	# Get allowed fields
	allowed_fields = get_allowed_fields_for_doctype("AI Document", user_permissions)
	final_fields = fields or allowed_fields
	
	# Query data
	data = frappe.get_all(
		"AI Document",
		filters=final_filters,
		fields=final_fields,
		limit_page_length=min([perm.get("max_results_per_query", 20) for perm in user_permissions] + [20])
	)
	
	# Filter by role-based access
	filtered_data = []
	for item in data:
		doc = frappe.get_doc("AI Document", item.name)
		
		# Check role-based access
		if doc.roles_allowed:
			doc_roles = [role.strip() for role in doc.roles_allowed.split(",") if role.strip()]
			if doc_roles and not any(role in user_roles for role in doc_roles):
				continue
		
		filtered_data.append(item)
	
	# Apply field-level masking
	security = ChatbotSecurityMiddleware()
	masked_data = [security.filter_response(item, user) for item in filtered_data]
	
	return masked_data


def get_allowed_fields_for_doctype(doctype, user_permissions):
	"""Get allowed fields for a doctype based on user permissions"""
	# Get all fields for the doctype
	meta = frappe.get_meta(doctype)
	all_fields = [field.fieldname for field in meta.fields]
	
	# Check field restrictions
	restricted_fields = set()
	for perm in user_permissions:
		field_restrictions = perm.get("field_restrictions", [])
		for restriction in field_restrictions:
			if restriction.get("doctype") == doctype and restriction.get("access_type") == "Hidden":
				restricted_fields.add(restriction.get("field_name"))
	
	# Return allowed fields
	allowed_fields = [field for field in all_fields if field not in restricted_fields]
	
	# Always include basic fields
	basic_fields = ["name", "creation", "modified", "owner"]
	for field in basic_fields:
		if field not in allowed_fields:
			allowed_fields.append(field)
	
	return allowed_fields


def check_chatbot_access(doctype, doc_name=None, user=None):
	"""Check if user has access to specific document/doctype"""
	if not user:
		user = frappe.session.user
	
	# First check Frappe permission
	if doc_name:
		if not frappe.has_permission(doctype, "read", doc_name, user=user):
			return False
	else:
		if not frappe.has_permission(doctype, "read", user=user):
			return False
	
	# For now, just return True after Frappe permission check
	# Can be extended with custom chatbot permissions later
	return True
