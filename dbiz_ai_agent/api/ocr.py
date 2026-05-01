import base64
import io
import json
import mimetypes
import time
import random
import string

import frappe
import requests
from frappe import _  # type: ignore[import]
from frappe.utils import now  # type: ignore[import]
from frappe.utils.data import flt, getdate, nowdate  # type: ignore[import]

from pdf2image import convert_from_bytes  # type: ignore[import]


# n8n OCR webhook URL (production)
N8N_OCR_WEBHOOK_URL = (
    getattr(frappe.conf, "n8n_ocr_webhook_url", None)
    or "https://bpm.digitalbiz.com.vn/webhook/fb1275f3-99bc-474c-8f68-a3f23b53b75a"
)


@frappe.whitelist()
def get_document_types():
    """Get list of active OCR Document Types"""
    try:
        doc_types = frappe.get_all(
            "OCR Document Type",
            filters={"is_active": 1},
            fields=["name", "document_type_code", "document_type_name", "description"],
            order_by="document_type_name"
        )
        
        # If no document types found, return empty array (not error)
        if not doc_types:
            frappe.logger().info("OCR: No active document types found")
        
        return {"success": True, "data": doc_types or []}
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi lấy document types: {str(e)}")
        return {"success": False, "error": str(e), "data": []}


@frappe.whitelist()
def get_transactions(filters=None, limit=50, start=0):
    """Get OCR Transactions with filters"""
    try:
        filters = filters or {}
        conditions = {}
        
        if filters.get("status"):
            conditions["status"] = filters["status"]
        if filters.get("document_type"):
            conditions["document_type"] = filters["document_type"]
        if filters.get("company"):
            conditions["company"] = filters["company"]
        
        transactions = frappe.get_all(
            "OCR Transaction",
            filters=conditions,
            fields=[
                "name", "file_name", "file_attachment", "document_type",
                "status", "tenant", "company", "description",
                "destination", "tokens_used", "processing_time",
                "modified", "creation"
            ],
            order_by="modified desc",
            limit=limit,
            start=start
        )
        
        return {"success": True, "data": transactions}
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi lấy transactions: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_transaction_detail(transaction_id):
    """Get detail of a transaction"""
    try:
        transaction = frappe.get_doc("OCR Transaction", transaction_id)
        details_info = {}
        if transaction.details_info:
            try:
                details_info = json.loads(transaction.details_info)
            except:
                details_info = {"raw": transaction.details_info}
        
        return {
            "success": True,
            "data": {
                "name": transaction.name,
                "file_name": transaction.file_name,
                "file_attachment": transaction.file_attachment,
                "document_type": transaction.document_type,
                "status": transaction.status,
                "tenant": transaction.tenant,
                "company": transaction.company,
                "description": transaction.description,
                "details_info": details_info,
                "destination": transaction.destination,
                "tokens_used": transaction.tokens_used,
                "processing_time": transaction.processing_time,
                "modified": transaction.modified,
                "creation": transaction.creation
            }
        }
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi lấy transaction detail: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_recent_transactions(limit=3):
    """Get recent OCR Transactions for history display"""
    try:
        transactions = frappe.get_all(
            "OCR Transaction",
            fields=[
                "name", "file_name", "status", "modified", "creation"
            ],
            order_by="modified desc",
            limit=limit
        )
        
        return {"success": True, "data": transactions}
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi lấy recent transactions: {str(e)}")
        return {"success": False, "error": str(e), "data": []}


@frappe.whitelist()
def get_ocr_statistics():
    """Get OCR statistics by date and status"""
    try:
        from frappe.utils import today, add_days, get_first_day
        
        today_date = today()
        week_start = add_days(today_date, -6)  # 7 days including today
        month_start = get_first_day(today_date)
        
        # Count today
        today_count = frappe.db.count(
            "OCR Transaction",
            filters={
                "creation": [">=", today_date],
                "status": ["in", ["Processing", "Completed"]]
            }
        )
        
        # Count this week
        week_count = frappe.db.count(
            "OCR Transaction",
            filters={
                "creation": [">=", week_start],
                "status": ["in", ["Processing", "Completed"]]
            }
        )
        
        # Count this month
        month_count = frappe.db.count(
            "OCR Transaction",
            filters={
                "creation": [">=", month_start],
                "status": ["in", ["Processing", "Completed"]]
            }
        )
        
        # Count total
        total_count = frappe.db.count(
            "OCR Transaction",
            filters={
                "status": ["in", ["Processing", "Completed"]]
            }
        )
        
        return {
            "success": True,
            "data": {
                "today": today_count,
                "week": week_count,
                "month": month_count,
                "total": total_count
            }
        }
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi lấy statistics: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "today": 0,
                "week": 0,
                "month": 0,
                "total": 0
            }
        }


@frappe.whitelist()
def create_ocr_document(transaction_id, posting_date, items):
    """Create OCR Document from Transaction"""
    try:
        transaction = frappe.get_doc("OCR Transaction", transaction_id)
        
        if transaction.status != "Completed":
            frappe.throw("Chỉ có thể tạo document từ transaction đã hoàn thành")
        
        # Create OCR Document
        ocr_doc = frappe.get_doc({
            "doctype": "OCR Document",
            "transaction": transaction_id,
            "document_type": transaction.document_type,
            "posting_date": posting_date,
            "status": "Draft",
            "items": items
        })
        ocr_doc.insert(ignore_permissions=True)
        
        # Update transaction
        transaction.ocr_document = ocr_doc.name
        transaction.destination = "OCR Document"
        transaction.save(ignore_permissions=True)
        
        return {"success": True, "document_id": ocr_doc.name}
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi tạo document: {str(e)}")
        return {"success": False, "error": str(e)}


def _get_default_company():
    company = frappe.defaults.get_user_default("company")
    if company:
        return company
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if company:
        return company
    first_company = frappe.get_all("Company", fields=["name"], limit=1)
    return first_company[0].name if first_company else None


def _get_default_tenant_name():
    tenant = frappe.defaults.get_user_default("tenant")
    if tenant:
        return tenant
    return frappe.conf.get("default_tenant")


def _ensure_tenant(tenant_name):
    if not tenant_name:
        return None
    tenant = frappe.db.exists("Tenant", tenant_name)
    if tenant:
        return tenant

    try:
        tenant_doc = frappe.get_doc(
            {
                "doctype": "Tenant",
                "tenant_name": tenant_name
            }
        )
        tenant_doc.insert(ignore_permissions=True)
        return tenant_doc.name
    except Exception as e:
        frappe.log_error(f"OCR: Không thể tạo Tenant '{tenant_name}': {str(e)}")
        return None


def _get_default_expense_account(company):
    if not company:
        return None
    result = frappe.db.sql(
        """
        SELECT name FROM `tabAccount`
        WHERE company=%s
          AND (account_type IN ('Expense Account', 'Cost of Goods Sold') OR root_type='Expense')
        ORDER BY lft
        LIMIT 1
        """,
        company,
    )
    return result[0][0] if result else None


def _get_default_cost_center(company):
    if not company:
        return None
    cost_center = frappe.db.get_value("Company", company, "default_cost_center")
    if cost_center:
        return cost_center
    fallback = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
    return fallback


def _ensure_supplier(name, tax_id=None):
    if not name:
        return None
    supplier = frappe.db.exists("Supplier", name)
    if supplier:
        return supplier

    try:
        supplier_doc = frappe.get_doc(
            {
                "doctype": "Supplier",
                "supplier_name": name,
                "supplier_type": "Company",
                "tax_id": tax_id or "",
            }
        )
        supplier_doc.insert(ignore_permissions=True)
        return supplier_doc.name
    except Exception as e:
        frappe.log_error(f"OCR: Không thể tạo Supplier '{name}': {str(e)}")
        return None


def _convert_pdf_to_image_bytes(pdf_bytes, dpi=300):
    if not pdf_bytes:
        return None

    try:
        images = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=1, last_page=1)
        if not images:
            return None

        buffer = io.BytesIO()
        images[0].save(buffer, format="JPEG", quality=90)
        return buffer.getvalue()
    except Exception as e:
        frappe.log_error(f"OCR: Không thể chuyển PDF sang ảnh: {str(e)}")
        return None


@frappe.whitelist()
def create_ap_invoice_from_ocr(invoice_data, ocr_result=None, scanned_file=None):
    """Create an AP Invoice using OCR results"""
    try:
        if isinstance(invoice_data, str):
            invoice_data = json.loads(invoice_data)
        invoice_data = frappe._dict(invoice_data or {})
        scanned_file = frappe._dict(scanned_file or {})
        
        seller = frappe._dict(invoice_data.get("seller") or {})
        buyer = frappe._dict(invoice_data.get("buyer") or {})
        financial = frappe._dict(invoice_data.get("financial") or {})
        items = invoice_data.get("items") or []
        
        if not isinstance(items, list):
            items = []
        
        posting_date = (
            invoice_data.get("invoice_date")
            or invoice_data.get("posting_date")
            or nowdate()
        )
        posting_date = getdate(posting_date)
        
        company = invoice_data.get("company") or _get_default_company()
        if not company:
            frappe.throw(_("Vui lòng cấu hình company mặc định trong hệ thống."))
        
        supplier_name = seller.name or seller.company_name or buyer.name or _("Nhà cung cấp chưa rõ")
        supplier_tax_id = seller.tax_code or seller.tax_id or ""
        
        # Prepare items
        if not items:
            items = [
                {
                    "description": financial.get("amount_in_words")
                    or invoice_data.get("description")
                    or _("Dòng chi tiết mặc định"),
                    "quantity": 1,
                    "unit_price": financial.get("total_amount") or flt(financial.get("subtotal") or 0.0),
                }
            ]
        
        ap_items = []
        for idx, item in enumerate(items or []):
            item = frappe._dict(item or {})
            qty = flt(item.get("quantity") or item.get("qty") or 1)
            rate = flt(item.get("unit_price") or item.get("rate") or 0)
            amount = flt(item.get("amount") or (qty * rate))
            description = item.get("description") or item.get("item_name") or _("Dòng {0}").format(idx + 1)
            ap_items.append(
                {
                    "item_name": description,
                    "description": description,
                    "qty": qty,
                    "rate": rate,
                    "amount": amount,
                    "uom": item.get("unit") or item.get("uom") or _("Unit"),
                    "sort_order": idx + 1
                }
            )
        
        # Create AP Invoice
        ap_invoice_doc = frappe.get_doc(
            {
                "doctype": "AP Invoice",
                "company": company,
                "supplier": supplier_name,
                "supplier_name": supplier_name,
                "supplier_tax_id": supplier_tax_id,
                "posting_date": posting_date,
                "invoice_date": posting_date,
                "due_date": posting_date,
                "bill_no": invoice_data.get("invoice_number") or invoice_data.get("invoice_symbol") or "",
                "invoice_symbol": invoice_data.get("invoice_symbol") or "",
                "currency": financial.get("currency") or "VND",
                "supplier_address": seller.address or "",
                "subtotal": flt(financial.get("subtotal") or 0),
                "vat_rate": flt(financial.get("vat_rate") or 0),
                "vat_amount": flt(financial.get("vat_amount") or 0),
                "total_amount": flt(financial.get("total_amount") or 0),
                "remarks": invoice_data.get("notes") or _("Tự động tạo từ OCR"),
                "scanned_file_name": scanned_file.get("name") or "",
                "status": "Draft"
            }
        )
        
        # Append items to the document
        for item_data in ap_items:
            ap_invoice_doc.append("items", item_data)
        
        # Recalculate totals if not provided
        if not financial.get("subtotal") and ap_items:
            ap_invoice_doc.subtotal = sum(flt(item.get("amount", 0)) for item in ap_items)
        if not financial.get("vat_amount") and ap_invoice_doc.vat_rate:
            ap_invoice_doc.vat_amount = flt(ap_invoice_doc.subtotal * ap_invoice_doc.vat_rate / 100)
        if not financial.get("total_amount"):
            ap_invoice_doc.total_amount = flt(ap_invoice_doc.subtotal + ap_invoice_doc.vat_amount)
        
        # Link OCR Transaction if available
        txn_id = None
        if ocr_result:
            if isinstance(ocr_result, str):
                try:
                    ocr_result = json.loads(ocr_result)
                except Exception:
                    ocr_result = {}
            txn_id = ocr_result.get("transaction_id") or ocr_result.get("transactionId")
            if txn_id:
                ap_invoice_doc.ocr_transaction = txn_id
        
        ap_invoice_doc.insert(ignore_permissions=True)
        
        # Save scanned file
        if scanned_file.get("base64"):
            try:
                file_doc = frappe.get_doc(
                    {
                        "doctype": "File",
                        "file_name": scanned_file.get("name") or f"OCR-{ap_invoice_doc.name}",
                        "content": scanned_file.get("base64"),
                        "is_private": 0,
                        "content_type": scanned_file.get("type") or "application/octet-stream",
                        "attached_to_doctype": "AP Invoice",
                        "attached_to_name": ap_invoice_doc.name,
                        "attached_to_field": "attachments"
                    }
                )
                file_doc.insert(ignore_permissions=True)
                ap_invoice_doc.scanned_file_path = file_doc.file_url or file_doc.file_name
                ap_invoice_doc.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(
                    f"OCR: Không thể lưu tệp scan vào AP Invoice {ap_invoice_doc.name}: {str(e)}"
                )
        
        # Update OCR Transaction
        if txn_id:
            try:
                txn = frappe.get_doc("OCR Transaction", txn_id)
                txn.destination = "AP Invoice"
                txn.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"OCR: Không thể cập nhật transaction {txn_id}: {str(e)}")
        
        return {"success": True, "name": ap_invoice_doc.name}
    except frappe.ValidationError as ve:
        frappe.log_error(f"OCR: Lỗi tạo AP Invoice: {str(ve)}")
        return {"success": False, "error": str(ve)}
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi tạo AP Invoice: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def create_purchase_invoice_from_ocr(invoice_data, ocr_result=None, scanned_file=None):
    """Create a Purchase Invoice in ERPNext using OCR results"""
    try:
        if isinstance(invoice_data, str):
            invoice_data = json.loads(invoice_data)
        invoice_data = frappe._dict(invoice_data or {})
        scanned_file = frappe._dict(scanned_file or {})

        seller = frappe._dict(invoice_data.get("seller") or {})
        buyer = frappe._dict(invoice_data.get("buyer") or {})
        financial = frappe._dict(invoice_data.get("financial") or {})
        items = invoice_data.get("items") or []

        if not isinstance(items, list):
            items = []

        posting_date = (
            invoice_data.get("invoice_date")
            or invoice_data.get("posting_date")
            or nowdate()
        )
        posting_date = getdate(posting_date)

        company = invoice_data.get("company") or _get_default_company()
        if not company:
            frappe.throw(_("Vui lòng cấu hình company mặc định trong hệ thống."))

        supplier_name = seller.name or seller.company_name or buyer.name or _("Nhà cung cấp chưa rõ")
        supplier_tax_id = seller.tax_code or seller.tax_id or ""
        supplier_link = _ensure_supplier(supplier_name, supplier_tax_id)
        if not supplier_link:
            frappe.throw(_("Không thể xác định nhà cung cấp để tạo hóa đơn."))

        expense_account = _get_default_expense_account(company)
        if not expense_account:
            frappe.throw(_("Không tìm thấy tài khoản chi phí hợp lệ cho công ty {0}.").format(company))

        cost_center = _get_default_cost_center(company)

        if not items:
            items = [
                {
                    "description": financial.get("amount_in_words")
                    or invoice_data.get("description")
                    or _("Dòng chi tiết mặc định"),
                    "quantity": 1,
                    "unit_price": financial.get("total_amount") or flt(financial.get("subtotal") or 0.0),
                }
            ]

        pi_items = []
        for idx, item in enumerate(items or []):
            item = frappe._dict(item or {})
            qty = flt(item.get("quantity") or item.get("qty") or 1)
            rate = flt(item.get("unit_price") or item.get("rate") or 0)
            amount = flt(item.get("amount") or (qty * rate))
            description = item.get("description") or item.get("item_name") or _("Dòng {0}").format(idx + 1)
            pi_items.append(
                {
                    "doctype": "Purchase Invoice Item",
                    "description": description,
                    "item_name": description,
                    "qty": qty,
                    "rate": rate,
                    "amount": amount,
                    "uom": item.get("unit") or item.get("uom") or _("Unit"),
                    "expense_account": expense_account,
                    "cost_center": cost_center,
                }
            )

        pi_doc = frappe.get_doc(
            {
                "doctype": "Purchase Invoice",
                "company": company,
                "supplier": supplier_link,
                "supplier_name": supplier_name,
                "supplier_tax_id": supplier_tax_id,
                "posting_date": posting_date,
                "invoice_date": posting_date,
                "due_date": posting_date,
                "bill_no": invoice_data.get("invoice_number") or invoice_data.get("invoice_symbol") or "",
                "currency": financial.get("currency") or "VND",
                "items": pi_items,
                "set_posting_time": 1,
                "supplier_address": seller.address or "",
                "remarks": invoice_data.get("notes") or _("Tự động tạo từ OCR"),
            }
        )

        pi_doc.insert(ignore_permissions=True)

        if scanned_file.get("base64"):
            try:
                file_doc = frappe.get_doc(
                    {
                        "doctype": "File",
                        "file_name": scanned_file.get("name") or f"OCR-{pi_doc.name}",
                        "content": scanned_file.get("base64"),
                        "is_private": 0,
                        "content_type": scanned_file.get("type") or "application/octet-stream",
                        "attached_to_doctype": "Purchase Invoice",
                        "attached_to_name": pi_doc.name,
                        "attached_to_field": "attachments"
                    }
                )
                file_doc.insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(
                    f"OCR: Không thể lưu tệp scan vào Purchase Invoice {pi_doc.name}: {str(e)}"
                )

        txn_id = None
        if ocr_result:
            if isinstance(ocr_result, str):
                try:
                    ocr_result = json.loads(ocr_result)
                except Exception:
                    ocr_result = {}
            txn_id = ocr_result.get("transaction_id") or ocr_result.get("transactionId")

        if txn_id:
            try:
                txn = frappe.get_doc("OCR Transaction", txn_id)
                txn.destination = "Purchase Invoice"
                txn.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(f"OCR: Không thể cập nhật transaction {txn_id}: {str(e)}")

        return {"success": True, "name": pi_doc.name}
    except frappe.ValidationError as ve:
        frappe.log_error(f"OCR: Lỗi tạo hóa đơn mua hàng: {str(ve)}")
        return {"success": False, "error": str(ve)}
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi tạo hóa đơn mua hàng: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def call_n8n_ocr_api(file_base64, document_type, request_id=None, file_name="document", file_mime_type=None):
    """
    Call n8n OCR API from backend to avoid CORS issues
    """
    try:
        if not file_base64:
            return {"success": False, "error": "file_base64 is required"}
        
        if not document_type:
            return {"success": False, "error": "document_type is required"}
        
        # Generate request_id if not provided
        if not request_id:
            request_id = f"OCR-{int(time.time() * 1000)}-{''.join(random.choices(string.ascii_lowercase + string.digits, k=9))}"
        
        # Prepare request body (exact format as curl command)
        outgoing_base64 = file_base64
        outgoing_mime = file_mime_type
        if file_mime_type and "pdf" in file_mime_type.lower():
            try:
                decoded = base64.b64decode(file_base64)
                converted = _convert_pdf_to_image_bytes(decoded)
                if converted:
                    outgoing_base64 = base64.b64encode(converted).decode("utf-8")
                    outgoing_mime = "image/jpeg"
            except Exception as err:
                frappe.log_error(f"OCR: Không thể convert PDF trước khi gọi n8n: {str(err)}")
        request_body = {
            "document_type": "invoice_in",
            "request_id": request_id,
            "file_base64": outgoing_base64,
            "file_mime_type": outgoing_mime
        }
        
        # Verify Basic Auth encoding
        import base64 as b64
        auth_string = "dbiz_ocr:123456"
        expected_auth = b64.b64encode(auth_string.encode()).decode()
        actual_auth = "ZGJpel9vY3I6MTIzNDU2"
        
        if expected_auth != actual_auth:
            frappe.log_error(f"OCR: Basic Auth mismatch! Expected: {expected_auth}, Actual: {actual_auth}")
            # Use correct encoding
            auth_header = f"Basic {expected_auth}"
        else:
            auth_header = f"Basic {actual_auth}"
        
        # Call n8n API
        api_url = "https://bpm.digitalbiz.com.vn/webhook/api/v1/ocr-document"
        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }
        
        frappe.logger().info(f"Calling n8n OCR API:")
        frappe.logger().info(f"  - URL: {api_url}")
        frappe.logger().info(f"  - document_type: {document_type}")
        frappe.logger().info(f"  - request_id: {request_id}")
        frappe.logger().info(f"  - file_base64 length: {len(file_base64)}")
        frappe.logger().info(f"  - request_body keys: {list(request_body.keys())}")
        frappe.logger().info(f"  - Authorization header: {auth_header[:20]}...")
        
        # Log request details for debugging
        frappe.logger().info(f"Request body structure:")
        frappe.logger().info(f"  - document_type: {type(request_body['document_type']).__name__} = {request_body['document_type']}")
        frappe.logger().info(f"  - request_id: {type(request_body['request_id']).__name__} = {request_body['request_id']}")
        frappe.logger().info(f"  - file_base64: {type(request_body['file_base64']).__name__}, length = {len(request_body['file_base64'])}")
        frappe.logger().info(f"  - file_base64 sample (first 50 chars): {request_body['file_base64'][:50] if request_body['file_base64'] else 'EMPTY'}...")
        
        # Make the request
        try:
            response = requests.post(
                api_url,
                json=request_body,
                headers=headers,
                timeout=120
            )
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"OCR: Request exception: {str(e)}")
            raise
        
        frappe.logger().info(f"n8n OCR API response:")
        frappe.logger().info(f"  - Status code: {response.status_code}")
        frappe.logger().info(f"  - Content length: {len(response.content)}")
        frappe.logger().info(f"  - Headers: {dict(response.headers)}")
        frappe.logger().info(f"  - Response text (first 500 chars): {response.text[:500] if response.text else 'EMPTY'}")
        
        if response.status_code >= 400:
            error_text = response.text[:1000] if response.text else f"HTTP {response.status_code}"
            frappe.log_error(f"OCR: n8n API error {response.status_code}: {error_text}")
            return {
                "success": False,
                "error": f"OCR API failed: {response.status_code}",
                "message": error_text
            }
        
        # Check if response is empty
        if not response.text or response.text.strip() == "":
            frappe.log_error("OCR: n8n API returned empty response")
            return {
                "success": False,
                "error": "OCR API returned empty response"
            }
        
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            frappe.log_error(f"OCR: Failed to parse JSON response: {str(e)}, response_text: {response.text[:500]}")
            return {
                "success": False,
                "error": f"Invalid JSON response: {str(e)}",
                "raw_response": response.text[:500]
            }
        
        # Persist OCR Transaction
        try:
            file_bytes = base64.b64decode(file_base64)
        except Exception:
            file_bytes = None

        transaction_id = None
        try:
            transaction_id = _create_ocr_transaction_from_result(
                file_name, file_bytes, document_type, data
            )
        except Exception as e:
            frappe.log_error(
                f"OCR: Không tạo được OCR Transaction sau khi gọi n8n: {str(e)}"
            )

        return {
            "success": True,
            "data": data,
            "transaction_id": transaction_id
        }
        
    except requests.exceptions.Timeout:
        frappe.log_error("OCR: n8n API timeout")
        return {"success": False, "error": "OCR API timeout. Vui lòng thử lại."}
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"OCR: n8n API connection error: {str(e)}")
        return {"success": False, "error": f"Không thể kết nối OCR API: {str(e)}"}
    except Exception as e:
        frappe.log_error(f"OCR: Unexpected error calling n8n API: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist(allow_guest=True)
def process_ocr():
    """
    Receive an image/PDF file, convert to base64 and forward
    to the n8n OCR webhook with required body:
      - type: INVOICE | CCCD | land_certificate
      - typeApplication: IMG | PDF
      - image_base64: base64 of file content
    """
    form_dict = frappe.form_dict or {}

    raw_type = (form_dict.get("type") or form_dict.get("doc_type") or "").strip()
    allowed_types = {"INVOICE", "CCCD", "land_certificate"}
    document_type = raw_type if raw_type in allowed_types else "INVOICE"

    uploaded_file = None
    if frappe.request and getattr(frappe.request, "files", None):
        uploaded_file = frappe.request.files.get("file")

    if not uploaded_file:
        frappe.throw(_("Không tìm thấy file upload"))

    file_name = uploaded_file.filename or "document"
    content_type = uploaded_file.content_type or mimetypes.guess_type(file_name)[0] or ""

    if "pdf" in content_type.lower() or file_name.lower().endswith(".pdf"):
        type_application = "PDF"
    else:
        type_application = "IMG"

    override_type_app = (form_dict.get("typeApplication") or "").strip()
    if override_type_app in ("IMG", "PDF"):
        type_application = override_type_app

    try:
        file_bytes = uploaded_file.stream.read()
    except Exception as err:
        frappe.log_error(f"OCR: không đọc được file: {str(err)}")
        frappe.throw(_("Không đọc được nội dung file"))

    if not file_bytes:
        frappe.throw(_("File rỗng hoặc không hợp lệ"))

    processed_bytes = file_bytes
    if type_application == "PDF":
        converted = _convert_pdf_to_image_bytes(file_bytes)
        if not converted:
            frappe.throw(_("Không thể chuyển PDF sang ảnh để OCR"))
        processed_bytes = converted

    image_base64 = base64.b64encode(processed_bytes).decode("utf-8")

    payload = {
        "type": document_type,
        "typeApplication": type_application,
        "image_base64": image_base64,
    }

    if not N8N_OCR_WEBHOOK_URL:
        frappe.log_error("OCR: N8N_OCR_WEBHOOK_URL is not configured")
        frappe.throw(_("Hệ thống OCR chưa được cấu hình"))

    try:
        response = requests.post(N8N_OCR_WEBHOOK_URL, json=payload, timeout=120)
    except Exception as err:
        frappe.log_error(f"OCR: lỗi kết nối n8n: {str(err)}")
        frappe.throw(_("Không thể kết nối hệ thống OCR, vui lòng thử lại sau."))

    if response.status_code >= 400:
        error_text = ""
        try:
            error_text = response.text[:1000]
        except Exception:
            error_text = f"HTTP {response.status_code}"
        frappe.log_error(
            f"OCR: n8n trả về lỗi {response.status_code}: {error_text}"
        )
        frappe.throw(_("Xử lý OCR thất bại, vui lòng thử lại sau."))

    try:
        result = response.json()
    except Exception:
        result = {"raw": response.text}

    # Save file to Frappe File
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": file_bytes,
        "is_private": 0
    })
    file_doc.insert(ignore_permissions=True)
    file_url = file_doc.file_url

    # Get document type from OCR Document Type
    doc_type_code = document_type
    doc_type_name = None
    try:
        # Try to find by document_type_code
        doc_type_list = frappe.get_all(
            "OCR Document Type",
            filters={"document_type_code": doc_type_code, "is_active": 1},
            limit=1
        )
        if doc_type_list:
            doc_type_name = doc_type_list[0].name
        else:
            # Create default if not exists
            doc_type_doc = frappe.get_doc({
                "doctype": "OCR Document Type",
                "document_type_code": doc_type_code,
                "document_type_name": doc_type_code,
                "is_active": 1
            })
            doc_type_doc.insert(ignore_permissions=True)
            doc_type_name = doc_type_doc.name
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi xử lý document type: {str(e)}")
        # Fallback: use code as name
        doc_type_name = doc_type_code

    # Create OCR Transaction
    start_time = time.time()
    processing_time = 0
    
    tenant_name = _get_default_tenant_name()
    tenant_link = _ensure_tenant(tenant_name)

    try:
        transaction = frappe.get_doc({
            "doctype": "OCR Transaction",
            "file_name": file_name,
            "file_attachment": file_url,
            "document_type": doc_type_name or doc_type_code,
            "status": "Processing",
            "details_info": json.dumps(result, ensure_ascii=False),
            "tenant": tenant_link,
            "company": frappe.defaults.get_user_default("company") or None
        })
        transaction.insert(ignore_permissions=True)
        transaction_id = transaction.name
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi tạo transaction: {str(e)}")
        transaction_id = None

    processing_time = time.time() - start_time

    # Update transaction with result
    if transaction_id:
        try:
            transaction = frappe.get_doc("OCR Transaction", transaction_id)
            transaction.status = "Completed"
            transaction.processing_time = processing_time
            transaction.tokens_used = result.get("tokens_used", 0) if isinstance(result, dict) else 0
            transaction.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"OCR: Lỗi cập nhật transaction: {str(e)}")

    return {
        "success": True,
        "type": document_type,
        "typeApplication": type_application,
        "result": result,
        "transaction_id": transaction_id,
        "file_url": file_url,
        "processing_time": processing_time
    }


def _create_ocr_transaction_from_result(file_name, file_bytes, document_type, result, tenant_name=None):
    doc_type_code = document_type
    doc_type_name = None
    try:
        doc_type_list = frappe.get_all(
            "OCR Document Type",
            filters={"document_type_code": doc_type_code, "is_active": 1},
            limit=1
        )
        if doc_type_list:
            doc_type_name = doc_type_list[0].name
        else:
            doc_type_doc = frappe.get_doc({
                "doctype": "OCR Document Type",
                "document_type_code": doc_type_code,
                "document_type_name": doc_type_code,
                "is_active": 1
            })
            doc_type_doc.insert(ignore_permissions=True)
            doc_type_name = doc_type_doc.name
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi xử lý document type: {str(e)}")
        doc_type_name = doc_type_code

    file_url = None
    tenant_name = tenant_name or _get_default_tenant_name()
    tenant_link = _ensure_tenant(tenant_name)
    if file_bytes:
        try:
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": file_name or "document",
                "content": file_bytes,
                "is_private": 0
            })
            file_doc.insert(ignore_permissions=True)
            file_url = file_doc.file_url
        except Exception as e:
            frappe.log_error(f"OCR: Không tạo được File từ base64: {str(e)}")

    transaction_id = None
    start_time = time.time()
    try:
        transaction = frappe.get_doc({
            "doctype": "OCR Transaction",
            "file_name": file_name,
            "file_attachment": file_url,
            "document_type": doc_type_name or doc_type_code,
            "status": "Processing",
            "details_info": json.dumps(result, ensure_ascii=False),
            "tenant": tenant_link,
            "company": frappe.defaults.get_user_default("company") or None
        })
        transaction.insert(ignore_permissions=True)
        transaction_id = transaction.name
    except Exception as e:
        frappe.log_error(f"OCR: Lỗi tạo transaction tự động: {str(e)}")

    processing_time = time.time() - start_time
    if transaction_id:
        try:
            transaction = frappe.get_doc("OCR Transaction", transaction_id)
            transaction.status = "Completed"
            transaction.processing_time = processing_time
            transaction.tokens_used = result.get("tokens_used", 0) if isinstance(result, dict) else 0
            transaction.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"OCR: Lỗi cập nhật transaction tự động: {str(e)}")

    return transaction_id

