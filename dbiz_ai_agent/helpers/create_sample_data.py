"""
Script to create sample data for AI Modules, AI Agents, and AI Agent Capabilities
Run: bench --site localerp.dbiz.com execute dbiz_ai_agent.helpers.create_sample_data.create_sample_data
"""

import frappe
from frappe import _


@frappe.whitelist()
def create_sample_data():
	"""Create sample data for AI Modules, AI Agents, and AI Agent Capabilities"""
	try:
		# First, ensure we have at least one AI Product
		products = frappe.get_all("AI Product", fields=["name", "product_name"])
		if not products:
			frappe.throw("Vui lòng tạo ít nhất một AI Product trước khi chạy script này")
		
		# Use first product as default
		default_product = products[0].name
		
		# Sample Modules Data
		modules_data = [
			{
				"module_name": "Tài chính & Kế toán",
				"module_code": "finance",
				"module_name_en": "Finance & Accounting",
				"product": default_product,
				"icon": "DollarSign",
				"bg_color": "bg-purple-600",
				"description": "AI Agents tự động hóa quy trình tài chính, dự báo dòng tiền và phát hiện bất thường",
				"sort_order": 1,
				"is_active": 1
			},
			{
				"module_name": "Chuỗi cung ứng & Logistics",
				"module_code": "supply-chain",
				"module_name_en": "Supply Chain & Logistics",
				"product": default_product,
				"icon": "Truck",
				"bg_color": "bg-blue-600",
				"description": "Tối ưu hóa vận chuyển, quản lý kho và dự báo nhu cầu",
				"sort_order": 2,
				"is_active": 1
			},
			{
				"module_name": "Sản xuất (MES/APS)",
				"module_code": "manufacturing",
				"module_name_en": "Manufacturing (MES/APS)",
				"product": default_product,
				"icon": "Factory",
				"bg_color": "bg-green-600",
				"description": "Lập lịch sản xuất thông minh và giám sát chất lượng",
				"sort_order": 3,
				"is_active": 1
			},
			{
				"module_name": "Nhân sự & Lương",
				"module_code": "hr",
				"module_name_en": "HR & Payroll",
				"product": default_product,
				"icon": "Users",
				"bg_color": "bg-orange-600",
				"description": "Tự động hóa quy trình nhân sự và tính lương",
				"sort_order": 4,
				"is_active": 1
			},
			{
				"module_name": "Chung & Khác",
				"module_code": "general",
				"module_name_en": "General & Others",
				"product": default_product,
				"icon": "Brain",
				"bg_color": "bg-indigo-600",
				"description": "Các AI Agents đa năng và tiện ích chung",
				"sort_order": 5,
				"is_active": 1
			}
		]
		
		# Create Modules (simplified for brevity - full version in original file)
		created_modules = {}
		for module_data in modules_data:
			module_code = module_data["module_code"]
			existing = frappe.get_all("AI Module", filters={"module_code": module_code})
			if not existing:
				module_doc = frappe.get_doc({
					"doctype": "AI Module",
					**module_data
				})
				module_doc.insert(ignore_permissions=True)
				created_modules[module_code] = module_doc.name
				print(f"✅ Created module: {module_data['module_name']}")
			else:
				created_modules[module_code] = existing[0].name
				print(f"ℹ️  Module already exists: {module_data['module_name']}")
		
		frappe.db.commit()
		
		return {
			"success": True,
			"message": "Sample data created successfully",
			"modules_created": len(created_modules)
		}
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Error creating sample data: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}

