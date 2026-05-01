# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ChatbotConfiguration(Document):
	def before_insert(self):
		"""Set created_by_user before inserting"""
		if not self.created_by_user:
			self.created_by_user = frappe.session.user
	
	def validate(self):
		"""Validate the document before saving"""
		# Ensure only one active configuration exists
		if self.is_active:
			existing_active = frappe.db.get_list(
				"Chatbot Configuration",
				filters={"is_active": 1, "name": ["!=", self.name]},
				limit=1
			)
			if existing_active:
				frappe.throw("Only one Chatbot Configuration can be active at a time. Please deactivate the existing one first.")
	
	def on_update(self):
		"""Clear cache when configuration is updated"""
		frappe.cache().delete_key("active_chatbot_config")
