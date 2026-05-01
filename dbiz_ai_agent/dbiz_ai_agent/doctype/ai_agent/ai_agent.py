# Copyright (c) 2025, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AIAgent(Document):
	def after_insert(self):
		"""Update module agent count after insert"""
		self.update_module_count()
	
	def on_trash(self):
		"""Update module agent count after delete"""
		self.update_module_count()
	
	def update_module_count(self):
		"""Update the agent count in the module"""
		if self.module:
			module_doc = frappe.get_doc("AI Module", self.module)
			module_doc.update_agent_count()
			module_doc.save()

