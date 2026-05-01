import frappe
from frappe.model.document import Document

class SalesOrderDetail(Document):
	def validate(self):
		"""Calculate total amount before saving"""
		if self.quantity and self.unit_price:
			self.total_amount = float(self.quantity) * float(self.unit_price)
		else:
			self.total_amount = 0.0

