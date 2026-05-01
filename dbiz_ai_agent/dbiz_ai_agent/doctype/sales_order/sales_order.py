import frappe
from frappe.model.document import Document
from datetime import date

class SalesOrder(Document):
	def validate(self):
		"""Calculate totals before saving"""
		# Set default order date if not provided
		if not self.order_date:
			self.order_date = date.today()
		
		# Calculate subtotal from items
		subtotal = 0.0
		if self.items:
			for item in self.items:
				# Calculate item total if not already calculated
				if not item.total_amount or item.total_amount == 0:
					if item.quantity and item.unit_price:
						item.total_amount = float(item.quantity) * float(item.unit_price)
				
				if item.total_amount:
					subtotal += float(item.total_amount)
		
		self.subtotal = subtotal
		
		# Calculate total amount (subtotal + tax)
		tax = float(self.tax_amount) if self.tax_amount else 0.0
		self.total_amount = subtotal + tax

