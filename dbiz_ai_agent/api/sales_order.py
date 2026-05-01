"""
Sales Order API
API endpoints for creating and managing sales orders
"""
import frappe
from frappe import _
import json

@frappe.whitelist()
def create_sales_order(
    customer_name,
    items,
    customer_email=None,
    customer_phone=None,
    order_date=None,
    tax_amount=None,
    notes=None
):
    """
    Create a new sales order
    
    Args:
        customer_name: Tên khách hàng (required)
        items: JSON string or list of items. Each item should have:
            - item_name: Tên sản phẩm
            - quantity: Số lượng
            - unit_price: Đơn giá
            - description: Mô tả (optional)
        customer_email: Email khách hàng (optional)
        customer_phone: Số điện thoại khách hàng (optional)
        order_date: Ngày đặt hàng YYYY-MM-DD (optional, default: today)
        tax_amount: Số tiền thuế VAT (optional, default: 0)
        notes: Ghi chú (optional)
    
    Returns:
        dict: {
            "success": True,
            "order_number": "SO-0001",
            "order_id": "SO-0001",
            "total_amount": 200000.0,
            "message": "Đã tạo đơn hàng thành công"
        }
    """
    try:
        # Parse items if it's a string
        if isinstance(items, str):
            items_list = json.loads(items)
        else:
            items_list = items
        
        if not items_list or len(items_list) == 0:
            frappe.throw(_("Danh sách sản phẩm không được để trống"))
        
        if not customer_name or not customer_name.strip():
            frappe.throw(_("Tên khách hàng là bắt buộc"))
        
        # Create Sales Order document
        sales_order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer_name": customer_name.strip(),
            "customer_email": customer_email.strip() if customer_email else None,
            "customer_phone": customer_phone.strip() if customer_phone else None,
            "order_date": order_date if order_date else None,
            "status": "Draft",
            "tax_amount": float(tax_amount) if tax_amount else 0.0,
            "notes": notes.strip() if notes else None
        })
        
        # Add items
        for item_data in items_list:
            item_name = item_data.get("item_name", "").strip()
            quantity = float(item_data.get("quantity", 1.0))
            unit_price = float(item_data.get("unit_price", 0.0))
            description = item_data.get("description", "").strip() if item_data.get("description") else None
            
            if not item_name:
                frappe.throw(_("Tên sản phẩm là bắt buộc cho tất cả các sản phẩm"))
            
            sales_order.append("items", {
                "item_name": item_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "description": description
            })
        
        # Save the document
        sales_order.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "order_number": sales_order.name,
            "order_id": sales_order.name,
            "total_amount": float(sales_order.total_amount) if sales_order.total_amount else 0.0,
            "subtotal": float(sales_order.subtotal) if sales_order.subtotal else 0.0,
            "tax_amount": float(sales_order.tax_amount) if sales_order.tax_amount else 0.0,
            "status": sales_order.status,
            "message": f"Đã tạo đơn hàng thành công. Số đơn hàng: {sales_order.name}"
        }
        
    except frappe.exceptions.ValidationError as e:
        frappe.log_error(f"Validation error creating sales order: {str(e)}")
        frappe.throw(_(f"Lỗi xác thực: {str(e)}"))
    except json.JSONDecodeError:
        frappe.throw(_("Định dạng JSON không hợp lệ cho danh sách sản phẩm"))
    except Exception as e:
        frappe.log_error(f"Error creating sales order: {str(e)}")
        frappe.throw(_(f"Không thể tạo đơn hàng: {str(e)}"))


@frappe.whitelist()
def get_sales_order(order_number):
    """
    Get sales order details by order number
    
    Args:
        order_number: Số đơn hàng (e.g., "SO-0001")
    
    Returns:
        dict: Sales order details
    """
    try:
        sales_order = frappe.get_doc("Sales Order", order_number)
        
        items = []
        for item in sales_order.items:
            items.append({
                "item_name": item.item_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_amount": item.total_amount,
                "description": item.description
            })
        
        return {
            "success": True,
            "order_number": sales_order.name,
            "customer_name": sales_order.customer_name,
            "customer_email": sales_order.customer_email,
            "customer_phone": sales_order.customer_phone,
            "order_date": str(sales_order.order_date) if sales_order.order_date else None,
            "status": sales_order.status,
            "subtotal": float(sales_order.subtotal) if sales_order.subtotal else 0.0,
            "tax_amount": float(sales_order.tax_amount) if sales_order.tax_amount else 0.0,
            "total_amount": float(sales_order.total_amount) if sales_order.total_amount else 0.0,
            "items": items,
            "notes": sales_order.notes
        }
    except frappe.DoesNotExistError:
        frappe.throw(_(f"Không tìm thấy đơn hàng: {order_number}"))
    except Exception as e:
        frappe.log_error(f"Error getting sales order: {str(e)}")
        frappe.throw(_(f"Không thể lấy thông tin đơn hàng: {str(e)}"))

