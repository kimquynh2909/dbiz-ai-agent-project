"""
Sales Order Tools
Contains tools for creating and managing sales orders
"""
import frappe
import json
from typing import List, Dict, Any, Optional
from dbiz_ai_agent.agentic_ai.agents.base_agent import current_request_user

class SalesOrderTools:
    """Provides tools for creating and managing sales orders"""
    
    def __init__(self):
        pass
    
    def get_tools(self) -> List:
        """
        Get all sales order tools that can be used by an agent
        
        Returns:
            List of function_tool decorated functions
        """
        from agents import function_tool
        
        # Reference to self for use in closures
        tools_instance = self
        
        @function_tool
        def create_sales_order(
            customer_name: str,
            items: str,
            customer_email: Optional[str] = None,
            customer_phone: Optional[str] = None,
            order_date: Optional[str] = None,
            tax_amount: Optional[float] = None,
            notes: Optional[str] = None
        ) -> str:
            """🛒 Tạo đơn hàng mới (Sales Order).
            
            Tool này được sử dụng khi người dùng yêu cầu tạo đơn hàng, đặt hàng, hoặc tạo sales order.
            
            Args:
                customer_name (str): Tên khách hàng (bắt buộc)
                items (str): JSON string chứa danh sách sản phẩm. Format:
                    [
                        {
                            "item_name": "Tên sản phẩm",
                            "quantity": 2.0,
                            "unit_price": 100000.0,
                            "description": "Mô tả (tùy chọn)"
                        },
                        ...
                    ]
                customer_email (str, optional): Email khách hàng
                customer_phone (str, optional): Số điện thoại khách hàng
                order_date (str, optional): Ngày đặt hàng (format: YYYY-MM-DD). Mặc định là hôm nay
                tax_amount (float, optional): Số tiền thuế VAT. Mặc định là 0
                notes (str, optional): Ghi chú thêm về đơn hàng
            
            Returns:
                str: JSON object chứa thông tin đơn hàng đã tạo:
                    {
                        "success": true,
                        "order_number": "SO-0001",
                        "order_id": "SO-0001",
                        "total_amount": 200000.0,
                        "message": "Đã tạo đơn hàng thành công"
                    }
                    hoặc thông báo lỗi nếu có lỗi xảy ra
            
            ✅ Ví dụ sử dụng:
            - User: "Tạo đơn hàng cho Nguyễn Văn A với 2 sản phẩm iPhone 15, giá 20 triệu mỗi cái"
            - Tool call: create_sales_order(
                customer_name="Nguyễn Văn A",
                items='[{"item_name": "iPhone 15", "quantity": 2.0, "unit_price": 20000000.0}]'
            )
            """
            try:
                user = current_request_user.get()
                if not user:
                    user = frappe.session.user or "Administrator"
                
                frappe.logger().info(f"🛒 create_sales_order called by user: {user}")
                frappe.logger().info(f"   customer_name: {customer_name}, items: {items}")
                
                # Set user context
                frappe.set_user(user)
                
                # Check if DocType exists
                if not frappe.db.exists("DocType", "Sales Order"):
                    frappe.log_error("Sales Order DocType does not exist. Please run: bench --site [site] migrate")
                    return json.dumps({
                        "success": False,
                        "error": "Sales Order DocType chưa được tạo. Vui lòng chạy: bench --site [site] migrate"
                    }, ensure_ascii=False)
                
                # Parse items JSON
                try:
                    items_list = json.loads(items) if isinstance(items, str) else items
                except json.JSONDecodeError as e:
                    frappe.log_error(f"JSON decode error: {str(e)}, items: {items}")
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid items format. Items must be a valid JSON array. Error: {str(e)}"
                    }, ensure_ascii=False)
                
                if not items_list or len(items_list) == 0:
                    return json.dumps({
                        "success": False,
                        "error": "Items list cannot be empty. Please provide at least one item."
                    }, ensure_ascii=False)
                
                # Validate required fields
                if not customer_name or not customer_name.strip():
                    return json.dumps({
                        "success": False,
                        "error": "Customer name is required."
                    }, ensure_ascii=False)
                
                frappe.logger().info(f"   Creating Sales Order document...")
                
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
                        return json.dumps({
                            "success": False,
                            "error": "Item name is required for all items."
                        }, ensure_ascii=False)
                    
                    sales_order.append("items", {
                        "item_name": item_name,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "description": description
                    })
                
                frappe.logger().info(f"   Inserting Sales Order with {len(sales_order.items)} items...")
                
                # Save the document (this will trigger validation and calculate totals)
                try:
                    sales_order.insert(ignore_permissions=True)
                    frappe.logger().info(f"   Sales Order inserted: {sales_order.name}")
                except Exception as insert_error:
                    frappe.log_error(f"Error during insert: {str(insert_error)}")
                    raise
                
                # Force commit immediately
                frappe.db.commit()
                frappe.logger().info(f"   Database committed")
                
                # Verify the document was saved
                if not frappe.db.exists("Sales Order", sales_order.name):
                    frappe.log_error(f"Sales Order {sales_order.name} was not saved to database!")
                    return json.dumps({
                        "success": False,
                        "error": f"Đơn hàng đã được tạo nhưng không lưu được vào database. Vui lòng thử lại."
                    }, ensure_ascii=False)
                
                # Reload to get calculated values
                sales_order.reload()
                
                # Return success response
                result = {
                    "success": True,
                    "order_number": sales_order.name,
                    "order_id": sales_order.name,
                    "total_amount": float(sales_order.total_amount) if sales_order.total_amount else 0.0,
                    "subtotal": float(sales_order.subtotal) if sales_order.subtotal else 0.0,
                    "tax_amount": float(sales_order.tax_amount) if sales_order.tax_amount else 0.0,
                    "status": sales_order.status,
                    "message": f"Đã tạo đơn hàng thành công. Số đơn hàng: {sales_order.name}"
                }
                
                frappe.logger().info(f"✅ Sales Order created successfully: {sales_order.name} by user {user}")
                frappe.logger().info(f"   Total amount: {result['total_amount']}")
                return json.dumps(result, ensure_ascii=False, indent=2)
                
            except frappe.exceptions.ValidationError as e:
                error_msg = str(e)
                frappe.log_error(f"Validation error creating sales order: {error_msg}")
                return json.dumps({
                    "success": False,
                    "error": f"Validation error: {error_msg}"
                }, ensure_ascii=False)
            except Exception as e:
                error_msg = str(e)
                frappe.log_error(f"Error creating sales order: {error_msg}")
                return json.dumps({
                    "success": False,
                    "error": f"Failed to create sales order: {error_msg}"
                }, ensure_ascii=False)
        
        @function_tool
        def get_sales_revenue(
            period: Optional[str] = "monthly",
            year: Optional[int] = None,
            month: Optional[int] = None,
            day: Optional[int] = None,
            chart_type: Optional[str] = "bar"
        ) -> str:
            """📊 Lấy thống kê doanh thu từ đơn hàng (Sales Order).
            
            Tool này được sử dụng khi người dùng yêu cầu xem doanh thu, thống kê, báo cáo doanh số.
            Kết quả sẽ trả về dưới dạng biểu đồ chart để hiển thị trực quan.
            
            Args:
                period (str, optional): Loại thống kê:
                    - "today": Doanh thu ngày hôm nay (DÙNG KHI USER NÓI "hôm nay", "today", "ngày hôm nay")
                    - "daily": Theo ngày trong tháng hiện tại
                    - "weekly": Theo tuần trong tháng hiện tại
                    - "monthly": Theo tháng trong năm (mặc định)
                    - "yearly": Theo năm (5 năm gần nhất)
                chart_type (str, optional): Loại biểu đồ:
                    - "bar": Biểu đồ cột (mặc định)
                    - "line": Biểu đồ đường
                    - "pie": Biểu đồ tròn
                    - "doughnut": Biểu đồ vòng tròn
                year (int, optional): Năm cần thống kê. KHÔNG TRUYỀN nếu muốn dùng năm hiện tại!
                month (int, optional): Tháng cần thống kê (1-12). KHÔNG TRUYỀN nếu muốn dùng tháng hiện tại!
                day (int, optional): Ngày cụ thể (1-31). KHÔNG TRUYỀN nếu muốn dùng ngày hiện tại!
            
            Returns:
                str: JSON object chứa dữ liệu chart
            
            ✅ Ví dụ sử dụng - QUAN TRỌNG:
            - User: "Doanh thu hôm nay" → get_sales_revenue(period="today")  ← KHÔNG truyền year/month/day
            - User: "Doanh thu tháng này" → get_sales_revenue(period="daily")  ← KHÔNG truyền year/month
            - User: "Doanh thu năm nay" → get_sales_revenue(period="monthly")  ← KHÔNG truyền year
            - User: "Doanh thu năm 2024" → get_sales_revenue(period="monthly", year=2024)  ← CHỈ truyền year cụ thể
            """
            try:
                from datetime import datetime, date, timedelta
                from calendar import monthrange
                
                user = current_request_user.get()
                if not user:
                    user = frappe.session.user or "Administrator"
                
                frappe.logger().info(f"📊 get_sales_revenue called by user: {user}")
                frappe.logger().info(f"   RECEIVED - period: {period}, year: {year}, month: {month}, day: {day}, chart_type: {chart_type}")
                
                # QUAN TRỌNG: Luôn lấy ngày/tháng/năm hiện tại
                today = date.today()
                current_year = today.year
                current_month = today.month
                current_day = today.day
                
                frappe.logger().info(f"   CURRENT DATE: {current_year}-{current_month:02d}-{current_day:02d}")
                
                # ⚠️ FIX: Khi period là "today" hoặc "daily" hoặc "weekly", 
                # BẮT BUỘC dùng năm/tháng HIỆN TẠI bất kể agent truyền gì
                if period in ["today", "daily", "weekly"]:
                    year = current_year
                    month = current_month
                    day = current_day
                    frappe.logger().info(f"   → FORCED current date for period={period}: {year}-{month:02d}-{day:02d}")
                else:
                    # Cho period="monthly" hoặc "yearly", cho phép chỉ định năm cụ thể
                    # Nhưng vẫn validate
                    if year is None or year < 2000 or year > 2100:
                        year = current_year
                        frappe.logger().info(f"   → Using current year: {year}")
                    
                    if month is None or month < 1 or month > 12:
                        month = current_month
                        frappe.logger().info(f"   → Using current month: {month}")
                    
                    if day is None or day < 1 or day > 31:
                        day = current_day
                        frappe.logger().info(f"   → Using current day: {day}")
                
                frappe.logger().info(f"   FINAL - year: {year}, month: {month}, day: {day}")
                
                # Check if DocType exists
                if not frappe.db.exists("DocType", "Sales Order"):
                    return json.dumps({
                        "type": "error",
                        "error": "Sales Order DocType chưa được tạo. Vui lòng chạy: bench --site [site] migrate"
                    }, ensure_ascii=False)
                
                labels = []
                values = []
                summary = {
                    "total_revenue": 0.0,
                    "total_orders": 0,
                    "average_order_value": 0.0
                }
                
                # Lưu giá trị day vào biến riêng để không bị override
                current_day = day
                
                if period == "today":
                    # Doanh thu ngày hôm nay
                    query_date = f"{year}-{month:02d}-{current_day:02d}"
                    title = f"Doanh thu ngày {current_day}/{month}/{year}"
                    
                    frappe.logger().info(f"   Querying today's revenue for date: {query_date}")
                    
                    result = frappe.db.sql("""
                        SELECT COALESCE(SUM(total_amount), 0) as revenue, COUNT(*) as count
                        FROM `tabSales Order`
                        WHERE order_date = %s AND status != 'Cancelled'
                    """, (query_date,), as_dict=True)
                    
                    labels.append(f"Hôm nay ({current_day}/{month})")
                    revenue = float(result[0].revenue) if result else 0.0
                    values.append(revenue)
                    summary["total_revenue"] = revenue
                    summary["total_orders"] = int(result[0].count) if result else 0
                    
                    frappe.logger().info(f"   Today's revenue: {revenue}, orders: {summary['total_orders']}")
                
                elif period == "daily":
                    # Daily revenue for a specific month
                    days_in_month = monthrange(year, month)[1]
                    month_names = ["", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
                                   "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"]
                    title = f"Doanh thu theo ngày - {month_names[month]} {year}"
                    
                    for d in range(1, days_in_month + 1):
                        query_date = f"{year}-{month:02d}-{d:02d}"
                        result = frappe.db.sql("""
                            SELECT COALESCE(SUM(total_amount), 0) as revenue, COUNT(*) as count
                            FROM `tabSales Order`
                            WHERE order_date = %s AND status != 'Cancelled'
                        """, (query_date,), as_dict=True)
                        
                        labels.append(f"Ngày {d}")
                        revenue = float(result[0].revenue) if result else 0.0
                        values.append(revenue)
                        summary["total_revenue"] += revenue
                        summary["total_orders"] += int(result[0].count) if result else 0
                
                elif period == "weekly":
                    # Weekly revenue for a specific month
                    month_names = ["", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
                                   "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"]
                    title = f"Doanh thu theo tuần - {month_names[month]} {year}"
                    
                    first_day = date(year, month, 1)
                    days_in_month = monthrange(year, month)[1]
                    last_day = date(year, month, days_in_month)
                    
                    week_num = 1
                    current_start = first_day
                    
                    while current_start <= last_day:
                        days_to_sunday = (6 - current_start.weekday()) % 7
                        current_end = min(current_start + timedelta(days=days_to_sunday), last_day)
                        
                        result = frappe.db.sql("""
                            SELECT COALESCE(SUM(total_amount), 0) as revenue, COUNT(*) as count
                            FROM `tabSales Order`
                            WHERE order_date BETWEEN %s AND %s AND status != 'Cancelled'
                        """, (current_start.isoformat(), current_end.isoformat()), as_dict=True)
                        
                        labels.append(f"Tuần {week_num}")
                        revenue = float(result[0].revenue) if result else 0.0
                        values.append(revenue)
                        summary["total_revenue"] += revenue
                        summary["total_orders"] += int(result[0].count) if result else 0
                        
                        week_num += 1
                        current_start = current_end + timedelta(days=1)
                
                elif period == "monthly":
                    # Monthly revenue for a year
                    title = f"Doanh thu theo tháng - Năm {year}"
                    month_names = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
                    
                    for m in range(1, 13):
                        result = frappe.db.sql("""
                            SELECT COALESCE(SUM(total_amount), 0) as revenue, COUNT(*) as count
                            FROM `tabSales Order`
                            WHERE YEAR(order_date) = %s AND MONTH(order_date) = %s AND status != 'Cancelled'
                        """, (year, m), as_dict=True)
                        
                        labels.append(month_names[m-1])
                        revenue = float(result[0].revenue) if result else 0.0
                        values.append(revenue)
                        summary["total_revenue"] += revenue
                        summary["total_orders"] += int(result[0].count) if result else 0
                
                elif period == "yearly":
                    # Yearly revenue for last 5 years
                    title = "Doanh thu theo năm"
                    current_year = today.year
                    
                    for y in range(current_year - 4, current_year + 1):
                        result = frappe.db.sql("""
                            SELECT COALESCE(SUM(total_amount), 0) as revenue, COUNT(*) as count
                            FROM `tabSales Order`
                            WHERE YEAR(order_date) = %s AND status != 'Cancelled'
                        """, (y,), as_dict=True)
                        
                        labels.append(str(y))
                        revenue = float(result[0].revenue) if result else 0.0
                        values.append(revenue)
                        summary["total_revenue"] += revenue
                        summary["total_orders"] += int(result[0].count) if result else 0
                
                else:
                    return json.dumps({
                        "type": "error",
                        "error": f"Invalid period: {period}. Valid options: daily, weekly, monthly, yearly"
                    }, ensure_ascii=False)
                
                # Calculate average
                if summary["total_orders"] > 0:
                    summary["average_order_value"] = summary["total_revenue"] / summary["total_orders"]
                
                # Format currency for display
                def format_currency(value):
                    if value >= 1_000_000_000:
                        return f"{value/1_000_000_000:.1f} tỷ"
                    elif value >= 1_000_000:
                        return f"{value/1_000_000:.1f} triệu"
                    elif value >= 1_000:
                        return f"{value/1_000:.1f} nghìn"
                    else:
                        return f"{value:.0f}"
                
                # Build chart data
                chart_data = {
                    "type": "chart",
                    "chart_type": chart_type or "bar",
                    "title": title,
                    "data": {
                        "labels": labels,
                        "datasets": [{
                            "label": "Doanh thu (VNĐ)",
                            "data": values,
                            "backgroundColor": [
                                "rgba(59, 130, 246, 0.8)",
                                "rgba(16, 185, 129, 0.8)",
                                "rgba(245, 158, 11, 0.8)",
                                "rgba(239, 68, 68, 0.8)",
                                "rgba(139, 92, 246, 0.8)",
                                "rgba(236, 72, 153, 0.8)",
                                "rgba(14, 165, 233, 0.8)",
                                "rgba(34, 197, 94, 0.8)",
                                "rgba(251, 146, 60, 0.8)",
                                "rgba(248, 113, 113, 0.8)",
                                "rgba(167, 139, 250, 0.8)",
                                "rgba(244, 114, 182, 0.8)"
                            ],
                            "borderColor": [
                                "rgba(59, 130, 246, 1)",
                                "rgba(16, 185, 129, 1)",
                                "rgba(245, 158, 11, 1)",
                                "rgba(239, 68, 68, 1)",
                                "rgba(139, 92, 246, 1)",
                                "rgba(236, 72, 153, 1)",
                                "rgba(14, 165, 233, 1)",
                                "rgba(34, 197, 94, 1)",
                                "rgba(251, 146, 60, 1)",
                                "rgba(248, 113, 113, 1)",
                                "rgba(167, 139, 250, 1)",
                                "rgba(244, 114, 182, 1)"
                            ],
                            "borderWidth": 2,
                            "borderRadius": 6
                        }]
                    },
                    "options": {
                        "responsive": True,
                        "maintainAspectRatio": False,
                        "plugins": {
                            "legend": {
                                "display": False
                            },
                            "title": {
                                "display": True,
                                "text": title,
                                "font": {
                                    "size": 16,
                                    "weight": "bold"
                                }
                            }
                        },
                        "scales": {
                            "y": {
                                "beginAtZero": True,
                                "ticks": {
                                    "callback": "formatCurrency"
                                }
                            }
                        }
                    },
                    "summary": {
                        "total_revenue": summary["total_revenue"],
                        "total_revenue_formatted": format_currency(summary["total_revenue"]),
                        "total_orders": summary["total_orders"],
                        "average_order_value": summary["average_order_value"],
                        "average_order_value_formatted": format_currency(summary["average_order_value"]),
                        "period": period,
                        "year": year,
                        "month": month if period in ["daily", "weekly"] else None
                    },
                    "message": f"📊 **{title}**\n\n" +
                               f"💰 **Tổng doanh thu:** {format_currency(summary['total_revenue'])} VNĐ\n" +
                               f"📦 **Tổng đơn hàng:** {summary['total_orders']} đơn\n" +
                               f"📈 **Giá trị trung bình/đơn:** {format_currency(summary['average_order_value'])} VNĐ"
                }
                
                frappe.logger().info(f"✅ Sales revenue retrieved: {summary['total_revenue']} VNĐ, {summary['total_orders']} orders")
                return json.dumps(chart_data, ensure_ascii=False, indent=2)
                
            except Exception as e:
                error_msg = str(e)
                frappe.log_error(f"Error getting sales revenue: {error_msg}")
                return json.dumps({
                    "type": "error",
                    "error": f"Failed to get sales revenue: {error_msg}"
                }, ensure_ascii=False)
        
        return [create_sales_order, get_sales_revenue]

__all__ = ["SalesOrderTools"]

