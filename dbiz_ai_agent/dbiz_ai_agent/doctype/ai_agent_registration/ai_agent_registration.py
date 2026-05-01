# Copyright (c) 2025, DBIZ and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AIAgentRegistration(Document):
	def before_insert(self):
		if not self.status:
			self.status = "Pending"
		if not self.registration_date:
			from frappe.utils import today
			self.registration_date = today()

