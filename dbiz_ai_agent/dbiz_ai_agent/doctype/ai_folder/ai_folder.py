# Copyright (c) 2024, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AIFolder(Document):
	def before_insert(self):
		# Set created_by and created_at
		self.created_by = frappe.session.user
		self.created_at = frappe.utils.now()
	
	def before_save(self):
		# Update modified_by and modified_at
		self.modified_by = frappe.session.user
		self.modified_at = frappe.utils.now()
