"""
API endpoints for AI Agent Catalog (Products, Modules, Agents)
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_products():
	"""Get all products with their modules from database"""
	try:
		from frappe.utils import get_url
		
		products = frappe.get_all(
			"AI Product",
			filters={"is_active": 1},
			fields=["name", "product_name", "product_code", "icon", "description"],
			order_by="sort_order"
		)
		
		# Get modules for each product
		for product in products:
			product["id"] = product["product_code"]
			product["name"] = product["product_name"]
			
			# Process icon (Attach Image field) - convert to full URL
			if product.get("icon"):
				# icon is a file URL (e.g., "/files/logo.png")
				icon_url = product["icon"]
				if not icon_url.startswith(("http://", "https://")):
					icon_url = get_url(icon_url)
				product["logo"] = icon_url
			else:
				product["logo"] = None
			
			# Get linked modules from AI Module (using product field)
			module_docs = frappe.get_all(
				"AI Module",
				filters={"product": product["product_name"], "is_active": 1},
				fields=["name", "module_code"],
				order_by="sort_order"
			)
			module_codes = [m["module_code"] for m in module_docs]
			module_names = [m["name"] for m in module_docs]
			product["modules"] = module_codes
			
			# Count agents in these modules (module field is link to AI Module name)
			if module_names:
				agent_count = frappe.db.count(
					"AI Agent",
					filters={
						"module": ["in", module_names],
						"is_active": 1
					}
				)
				product["totalAgents"] = agent_count
			else:
				product["totalAgents"] = 0
		
		return {
			"success": True,
			"data": products
		}
	except Exception as e:
		frappe.log_error(f"Error in get_products: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_modules():
	"""Get all AI modules from database"""
	try:
		modules = frappe.get_all(
			"AI Module",
			filters={"is_active": 1},
			fields=["module_code", "module_name", "module_name_en", "icon", "bg_color", "description", "agent_count"],
			order_by="sort_order"
		)
		
		# Format response
		for module in modules:
			module["id"] = module["module_code"]
			module["name"] = module["module_name"]
			module["bgColor"] = module["bg_color"]
			module["count"] = module["agent_count"]
		
		return {
			"success": True,
			"data": modules
		}
	except Exception as e:
		frappe.log_error(f"Error in get_modules: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_agents(module_id=None):
	"""Get all AI agents or filter by module from database"""
	try:
		filters = {"is_active": 1}
		if module_id:
			filters["module"] = module_id
		
		agents = frappe.get_all(
			"AI Agent",
			filters=filters,
			fields=[
				"name", "agent_name", "agent_name_en", "agent_code",
				"module", "icon", "icon_bg", "description",
				"status", "source", "sort_order", "is_new_agent"
			],
			order_by="sort_order"
		)
		
		# Get capabilities for each agent
		for agent in agents:
			# Save DocType name before overwriting
			doc_name = agent["name"]  # This is the DocType name
			
			agent["id"] = agent["sort_order"]
			agent["name"] = agent["agent_name"]  # Display name
			agent["nameEn"] = agent["agent_name_en"]
			agent["iconBg"] = agent["icon_bg"]
			agent["isNew"] = agent.get("is_new_agent", 0)
			agent["docName"] = doc_name  # DocType name for navigation
			# Note: agent["module"] is already module_code, no conversion needed
			
			# Get capabilities using DocType name
			capabilities = frappe.get_all(
				"AI Agent Capability",
				filters={"parent": doc_name},
				fields=["capability"],
				pluck="capability"
			)
			agent["capabilities"] = capabilities if capabilities else []
		
		return {
			"success": True,
			"data": agents
		}
	except Exception as e:
		frappe.log_error(f"Error in get_agents: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_agent_detail(agent_id):
	"""Get detailed information about a specific agent from database"""
	try:
		# Try to find by name first, then by sort_order
		agent = None
		
		# Try by name
		if frappe.db.exists("AI Agent", agent_id):
			agent_name = agent_id
		else:
			# Try to find by sort_order
			agents = frappe.get_all(
				"AI Agent",
				filters={"sort_order": int(agent_id) if str(agent_id).isdigit() else 0},
				fields=["name"],
				limit=1
			)
			if agents:
				agent_name = agents[0]["name"]
			else:
				return {
					"success": False,
					"message": "Agent not found"
				}
		
		# Get agent details
		agent = frappe.get_doc("AI Agent", agent_name)
		
		# Get module name from module_code
		module_name = None
		if agent.module:
			# agent.module is already module_code, get module_name for display
			module_name = frappe.db.get_value(
				"AI Module",
				{"module_code": agent.module},
				"module_name"
			)
		
		# Get URL field - handle case where field might not exist yet
		agent_url = ""
		if hasattr(agent, 'url'):
			agent_url = agent.url or ""
		
		# Format response
		agent_data = {
			"id": agent.sort_order,
			"name": agent.agent_name,
			"nameEn": agent.agent_name_en,
			"agent_code": agent.agent_code,
			"module": agent.module,  # This is already module_code
			"moduleName": module_name,
			"icon": agent.icon,
			"iconBg": agent.icon_bg,
			"description": agent.description,
			"status": agent.status,
			"source": agent.source,
			"isNew": agent.get("is_new_agent", 0),
			"url": agent_url,
			"capabilities": [cap.capability for cap in agent.capabilities] if hasattr(agent, 'capabilities') else []
		}
		
		return {
			"success": True,
			"data": agent_data
		}
	except Exception as e:
		frappe.log_error(f"Error in get_agent_detail: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def get_catalog():
	"""Get complete catalog (products, modules, agents) from database"""
	try:
		products_response = get_products()
		modules_response = get_modules()
		agents_response = get_agents()
		
		return {
			"success": True,
			"data": {
				"products": products_response["data"] if products_response["success"] else [],
				"modules": modules_response["data"] if modules_response["success"] else [],
				"agents": agents_response["data"] if agents_response["success"] else []
			}
		}
	except Exception as e:
		frappe.log_error(f"Error in get_catalog: {str(e)}")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def register_agent_service(agent_id, phone, email, registration_date, user_count, description):
	"""Register for AI Agent service"""
	try:
		# Validate required fields
		if not agent_id:
			return {
				"success": False,
				"message": "Vui lòng chọn AI Agent"
			}
		if not phone:
			return {
				"success": False,
				"message": "Vui lòng nhập số điện thoại"
			}
		if not email:
			return {
				"success": False,
				"message": "Vui lòng nhập email"
			}
		if not registration_date:
			return {
				"success": False,
				"message": "Vui lòng chọn ngày đăng ký"
			}
		if not user_count or user_count < 1:
			return {
				"success": False,
				"message": "Vui lòng nhập số lượng người dùng (tối thiểu 1)"
			}
		
		# Check if agent exists
		agent_name = None
		if frappe.db.exists("AI Agent", agent_id):
			agent_name = agent_id
		else:
			# Try to find by sort_order
			agents = frappe.get_all(
				"AI Agent",
				filters={"sort_order": int(agent_id) if str(agent_id).isdigit() else 0},
				fields=["name"],
				limit=1
			)
			if agents:
				agent_name = agents[0]["name"]
			else:
				return {
					"success": False,
					"message": "AI Agent không tồn tại"
				}
		
		# Create registration record
		registration = frappe.get_doc({
			"doctype": "AI Agent Registration",
			"agent": agent_name,
			"phone": phone,
			"email": email,
			"registration_date": registration_date,
			"user_count": int(user_count),
			"description": description or "",
			"status": "Pending"
		})
		registration.insert(ignore_permissions=True)
		
		# Update agent status to "registered" if not already deployed
		agent_doc = frappe.get_doc("AI Agent", agent_name)
		if agent_doc.status != "deployed":
			agent_doc.status = "registered"
			agent_doc.save(ignore_permissions=True)
		
		frappe.db.commit()
		
		return {
			"success": True,
			"message": "Đăng ký thành công! Chúng tôi sẽ liên hệ lại với bạn sớm nhất.",
			"registration_id": registration.name
		}
	except frappe.ValidationError as ve:
		frappe.log_error(f"Validation error in register_agent_service: {str(ve)}")
		return {
			"success": False,
			"message": str(ve)
		}
	except Exception as e:
		frappe.log_error(f"Error in register_agent_service: {str(e)}")
		return {
			"success": False,
			"message": f"Lỗi khi đăng ký: {str(e)}"
		}


@frappe.whitelist(allow_guest=True)
def log_document_download(agent_id, full_name, phone, email, purpose, description):
	"""Log document download request"""
	try:
		# Validate required fields
		if not agent_id:
			return {
				"success": False,
				"message": "Vui lòng chọn AI Agent"
			}
		if not full_name:
			return {
				"success": False,
				"message": "Vui lòng nhập họ tên"
			}
		if not phone:
			return {
				"success": False,
				"message": "Vui lòng nhập số điện thoại"
			}
		if not email:
			return {
				"success": False,
				"message": "Vui lòng nhập email"
			}
		if not purpose:
			return {
				"success": False,
				"message": "Vui lòng chọn mục đích download"
			}
		
		# Check if agent exists
		agent_name = None
		agent_doc = None
		if frappe.db.exists("AI Agent", agent_id):
			agent_name = agent_id
			agent_doc = frappe.get_doc("AI Agent", agent_id)
		else:
			# Try to find by sort_order
			agents = frappe.get_all(
				"AI Agent",
				filters={"sort_order": int(agent_id) if str(agent_id).isdigit() else 0},
				fields=["name"],
				limit=1
			)
			if agents:
				agent_name = agents[0]["name"]
				agent_doc = frappe.get_doc("AI Agent", agent_name)
			else:
				return {
					"success": False,
					"message": "AI Agent không tồn tại"
				}
		
		# Create download log record
		download_log = frappe.get_doc({
			"doctype": "Agent Document Download",
			"agent": agent_name,
			"full_name": full_name,
			"phone": phone,
			"email": email,
			"purpose": purpose,
			"description": description or "",
			"download_date": frappe.utils.nowdate()
		})
		download_log.insert(ignore_permissions=True)
		frappe.db.commit()
		
		# TODO: Generate document URL or attach document
		# For now, we'll return a placeholder
		document_url = None
		
		# Send email notification with document (optional)
		try:
			frappe.sendmail(
				recipients=[email],
				subject=f"Tài liệu {agent_doc.agent_name}",
				message=f"""
				<p>Xin chào {full_name},</p>
				<p>Cảm ơn bạn đã quan tâm đến dịch vụ <strong>{agent_doc.agent_name}</strong>.</p>
				<p>Chúng tôi sẽ gửi tài liệu chi tiết cho bạn sớm nhất.</p>
				<p>Trân trọng,<br>Đội ngũ hỗ trợ</p>
				"""
			)
		except Exception as email_error:
			frappe.log_error(f"Error sending email: {str(email_error)}")
		
		return {
			"success": True,
			"message": "Đã ghi nhận thông tin của bạn. Tài liệu sẽ được gửi tới email sớm nhất.",
			"download_log_id": download_log.name,
			"document_url": document_url
		}
	except frappe.ValidationError as ve:
		frappe.log_error(f"Validation error in log_document_download: {str(ve)}")
		return {
			"success": False,
			"message": str(ve)
		}
	except Exception as e:
		frappe.log_error(f"Error in log_document_download: {str(e)}")
		return {
			"success": False,
			"message": f"Lỗi khi xử lý yêu cầu: {str(e)}"
		}