# Copyright (c) 2025, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AIModule(Document):
	def before_save(self):
		"""Update agent count before saving"""
		self.update_agent_count()
	
	def update_agent_count(self):
		"""Count the number of agents in this module"""
		count = frappe.db.count("AI Agent", filters={"module": self.name})
		self.agent_count = count

