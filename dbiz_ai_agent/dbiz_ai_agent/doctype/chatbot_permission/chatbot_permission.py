# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class ChatbotPermission(Document):
	def before_insert(self):
		"""Set created_by_user before inserting"""
		if not self.created_by_user:
			self.created_by_user = frappe.session.user
	
	def validate(self):
		"""Validate the permission configuration"""
		# Validate JSON format for custom_filters
		if self.custom_filters:
			try:
				json.loads(self.custom_filters)
			except json.JSONDecodeError:
				frappe.throw("Custom Filters must be valid JSON format")
		
		# Ensure at least one target is specified
		if not any([self.role, self.department, self.user_specific]):
			frappe.throw("Please specify at least one of: Role, Department, or Specific User")
		
		# Validate priority range
		if self.priority < 1 or self.priority > 10:
			frappe.throw("Priority must be between 1 (highest) and 10 (lowest)")
	
	def on_update(self):
		"""Clear permission cache when updated"""
		frappe.cache().delete_key("chatbot_permissions")
		frappe.cache().delete_key(f"user_permissions_{frappe.session.user}")
	
	def on_trash(self):
		"""Clear permission cache when deleted"""
		frappe.cache().delete_key("chatbot_permissions")
		frappe.cache().delete_key(f"user_permissions_{frappe.session.user}")


@frappe.whitelist()
def get_user_chatbot_permissions(user=None):
	"""Get all applicable permissions for a user"""
	if not user:
		user = frappe.session.user
	
	# Try cache first
	cache_key = f"user_permissions_{user}"
	cached_permissions = frappe.cache().get_value(cache_key)
	if cached_permissions:
		return cached_permissions
	
	user_roles = frappe.get_roles(user)
	user_doc = frappe.get_doc("User", user)
	user_department = getattr(user_doc, 'department', None)
	
	# Get all active permissions
	permissions = frappe.get_all(
		"Chatbot Permission",
		filters={"is_active": 1},
		fields=[
			"name", "permission_name", "role", "department", "user_specific",
			"access_level", "document_tags", "vector_collections", "custom_filters",
			"rate_limit_per_hour", "max_results_per_query", "sensitive_data_masking",
			"audit_access", "priority"
		],
		order_by="priority ASC"
	)
	
	applicable_permissions = []
	
	for perm in permissions:
		# Check if permission applies to user
		applies = False
		
		# Check role match
		if perm.role and perm.role in user_roles:
			applies = True
		
		# Check department match
		if perm.department and perm.department == user_department:
			applies = True
		
		# Check specific user match
		if perm.user_specific and perm.user_specific == user:
			applies = True
		
		if applies:
			# Get field restrictions
			field_restrictions = frappe.get_all(
				"Chatbot Field Restriction",
				filters={"parent": perm.name},
				fields=["doctype", "field_name", "access_type"]
			)
			perm["field_restrictions"] = field_restrictions
			applicable_permissions.append(perm)
	
	# Cache for 5 minutes
	frappe.cache().set_value(cache_key, applicable_permissions, expires_in_sec=300)
	
	return applicable_permissions


@frappe.whitelist()
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
	
	# Then check chatbot-specific permissions
	user_permissions = get_user_chatbot_permissions(user)
	
	# If no chatbot permissions defined, allow (fallback to Frappe permissions)
	if not user_permissions:
		return True
	
	# Check if any permission allows access to this doctype
	for perm in user_permissions:
		allowed_doctypes = perm.get("allowed_doctypes", [])
		if not allowed_doctypes or doctype in allowed_doctypes:
			return True
	
	return False


@frappe.whitelist()
def get_chatbot_query_filters(user=None):
	"""Get query filters for Qdrant based on user permissions
	
	QUAN TRỌNG: Hàm này CHỈ LẤY AI ROLES TỪ CONTACT, KHÔNG DÙNG FRAPPE SYSTEM ROLES
	"""
	if not user:
		user = frappe.session.user
	
	user_permissions = get_user_chatbot_permissions(user)
	
	# LẤY AI ROLES TỪ CONTACT - KHÔNG DÙNG frappe.get_roles()
	user_ai_roles = []
	user_department = None
	
	try:
		contact_name = frappe.db.get_value("Contact", {"user": user}, "name")
		if contact_name:
			contact_doc = frappe.get_doc("Contact", contact_name)
			# Lấy AI Roles từ child table ai_roles
			ai_roles_child = contact_doc.get("ai_roles") or []
			user_ai_roles = [
				row.role_name for row in ai_roles_child
				if getattr(row, "role_name", None)
			]
			user_department = getattr(contact_doc, "department", None)
			frappe.logger().info(f"[PERMISSION] User {user} has AI Roles: {user_ai_roles}, Department: {user_department}")
	except Exception as e:
		frappe.logger().warning(f"[PERMISSION] Could not fetch AI Roles for user {user}: {str(e)}")
	
	# Build Qdrant where clause
	where_conditions = []
	
	# KHÔNG filter tại Qdrant level - để post-filtering xử lý
	# Vì logic phân quyền (Public, Internal) được xử lý ở post-filtering
	# để đảm bảo kiểm tra chính xác quyền truy cập
	
	# Chỉ filter theo access_level nếu có trong permissions
	allowed_access_levels = []
	for perm in user_permissions:
		access_level = perm.get("access_level")
		if access_level and access_level not in allowed_access_levels:
			allowed_access_levels.append(access_level)
	
	# Không dùng OR logic nữa - để post-filtering kiểm tra chính xác
	# Chỉ trả về metadata để post-filtering sử dụng
	
	return {
		"user_ai_roles": user_ai_roles,
		"user_department": user_department,
		"allowed_access_levels": allowed_access_levels,
		"max_results": min([perm.get("max_results_per_query", 10) for perm in user_permissions] + [10]),
		"rate_limit": min([perm.get("rate_limit_per_hour", 100) for perm in user_permissions] + [100])
	}


@frappe.whitelist()
def mask_sensitive_data(data, user=None):
	"""Mask sensitive data based on user permissions"""
	if not user:
		user = frappe.session.user
	
	user_permissions = get_user_chatbot_permissions(user)
	
	# Check if any permission has sensitive data masking enabled
	should_mask = any(perm.get("sensitive_data_masking") for perm in user_permissions)
	
	if not should_mask:
		return data
	
	# Apply masking logic
	if isinstance(data, dict):
		masked_data = {}
		for key, value in data.items():
			if is_sensitive_field(key):
				masked_data[key] = mask_value(value)
			else:
				masked_data[key] = value
		return masked_data
	elif isinstance(data, list):
		return [mask_sensitive_data(item, user) for item in data]
	else:
		return data


def is_sensitive_field(field_name):
	"""Check if field contains sensitive data"""
	sensitive_patterns = [
		"password", "pin", "ssn", "social_security", "credit_card",
		"bank_account", "salary", "wage", "income", "tax_id",
		"phone", "mobile", "email", "address"
	]
	
	field_lower = field_name.lower()
	return any(pattern in field_lower for pattern in sensitive_patterns)


def mask_value(value):
	"""Mask sensitive value"""
	if not value:
		return value
	
	value_str = str(value)
	if len(value_str) <= 4:
		return "*" * len(value_str)
	else:
		return value_str[:2] + "*" * (len(value_str) - 4) + value_str[-2:]
