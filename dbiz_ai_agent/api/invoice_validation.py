# -*- coding: utf-8 -*-
"""
Invoice Validation API
Validates invoice data against various rules and checks
"""

import frappe
from frappe import _
import re
import hashlib
from datetime import datetime
from difflib import SequenceMatcher
import unicodedata


@frappe.whitelist()
def validate_invoice_data(invoice_data):
    """
    Main validation function for invoice data
    
    Args:
        invoice_data: JSON string containing invoice information
        
    Returns:
        dict: Validation results with status and details
    """
    try:
        import json
        if isinstance(invoice_data, str):
            invoice_data = json.loads(invoice_data)
        
        results = {
            "success": True,
            "overall_status": "PASS",
            "checks": []
        }
        
        # 1. Check duplicate invoice
        duplicate_check = check_duplicate_invoice(invoice_data)
        results["checks"].append(duplicate_check)
        if duplicate_check["status"] == "FAIL":
            results["overall_status"] = "FAIL"
        
        # 2. Validate Tax ID (MST)
        tax_id_check = validate_tax_id(invoice_data.get("seller", {}).get("tax_code"))
        results["checks"].append(tax_id_check)
        if tax_id_check["status"] == "FAIL":
            results["overall_status"] = "FAIL"
        
        # 3. Check supplier information
        supplier_check = check_supplier_info(invoice_data.get("seller", {}))
        results["checks"].append(supplier_check)
        if supplier_check["status"] in ["FAIL", "NEED REVIEW"]:
            if results["overall_status"] == "PASS":
                results["overall_status"] = supplier_check["status"]
        
        # 4. Cross-check with Purchase Order (if PO reference exists)
        po_check = cross_check_with_po(invoice_data)
        results["checks"].append(po_check)
        if po_check["status"] in ["FAIL", "NEED REVIEW"]:
            if results["overall_status"] == "PASS":
                results["overall_status"] = po_check["status"]
        
        return results
        
    except Exception as e:
        frappe.log_error(f"Error in validate_invoice_data: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "overall_status": "ERROR"
        }


def check_duplicate_invoice(invoice_data):
    """
    Check for duplicate invoices based on unique key
    """
    try:
        check_name = "Kiểm tra hóa đơn trùng lặp"
        
        # Extract key fields
        seller_tax_id = invoice_data.get("seller", {}).get("tax_code", "")
        invoice_symbol = invoice_data.get("invoice_symbol", "")
        invoice_number = invoice_data.get("invoice_number", "")
        invoice_date = invoice_data.get("invoice_date", "")
        total_amount = invoice_data.get("financial", {}).get("total_amount", 0)
        
        # Create unique hash
        unique_key = f"{seller_tax_id}_{invoice_symbol}_{invoice_number}_{invoice_date}_{total_amount}"
        invoice_hash = hashlib.md5(unique_key.encode()).hexdigest()
        
        # Check in OCR Transaction table
        existing = frappe.db.sql("""
            SELECT name, invoice_number, invoice_date, status
            FROM `tabOCR Transaction`
            WHERE invoice_hash = %s
            LIMIT 1
        """, (invoice_hash,), as_dict=True)
        
        if existing:
            return {
                "name": check_name,
                "status": "FAIL",
                "message": f"Hóa đơn đã tồn tại trong hệ thống (#{existing[0].name})",
                "details": {
                    "duplicate_id": existing[0].name,
                    "invoice_number": existing[0].invoice_number,
                    "invoice_date": existing[0].invoice_date,
                    "hash": invoice_hash
                }
            }
        
        return {
            "name": check_name,
            "status": "PASS",
            "message": "Hóa đơn chưa tồn tại, không bị trùng lặp",
            "details": {"hash": invoice_hash}
        }
        
    except Exception as e:
        frappe.log_error(f"Error in check_duplicate_invoice: {str(e)}")
        return {
            "name": "Kiểm tra hóa đơn trùng lặp",
            "status": "ERROR",
            "message": f"Lỗi khi kiểm tra: {str(e)}"
        }


def validate_tax_id(tax_id):
    """
    Validate Tax ID (MST) format and checksum
    """
    try:
        check_name = "Kiểm tra Mã số thuế"
        
        if not tax_id:
            return {
                "name": check_name,
                "status": "FAIL",
                "message": "Mã số thuế không được để trống"
            }
        
        # Clean tax_id
        tax_id = str(tax_id).strip()
        
        # Rule 1: Check format (10 or 13 digits)
        if not re.match(r'^\d{10}(\d{3})?$', tax_id):
            return {
                "name": check_name,
                "status": "FAIL",
                "message": f"MST không đúng định dạng. MST phải là 10 hoặc 13 chữ số. Nhận được: {tax_id}",
                "details": {"tax_id": tax_id, "length": len(tax_id)}
            }
        
        # Rule 2: Check length
        if len(tax_id) not in [10, 13]:
            return {
                "name": check_name,
                "status": "FAIL",
                "message": f"MST phải có 10 chữ số (doanh nghiệp) hoặc 13 chữ số (chi nhánh). Nhận được: {len(tax_id)} chữ số",
                "details": {"tax_id": tax_id, "length": len(tax_id)}
            }
        
        # Rule 3: Validate checksum (if applicable)
        # Vietnam Tax ID checksum validation
        checksum_valid = validate_tax_id_checksum(tax_id[:10])
        
        if not checksum_valid:
            return {
                "name": check_name,
                "status": "FAIL",
                "message": "MST không hợp lệ (checksum sai)",
                "details": {"tax_id": tax_id, "checksum": "invalid"}
            }
        
        # All checks passed
        tax_type = "Chi nhánh" if len(tax_id) == 13 else "Doanh nghiệp"
        return {
            "name": check_name,
            "status": "PASS",
            "message": f"MST hợp lệ ({tax_type})",
            "details": {
                "tax_id": tax_id,
                "type": tax_type,
                "checksum": "valid"
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in validate_tax_id: {str(e)}")
        return {
            "name": "Kiểm tra Mã số thuế",
            "status": "ERROR",
            "message": f"Lỗi khi kiểm tra: {str(e)}"
        }


def validate_tax_id_checksum(tax_id_10):
    """
    Validate Vietnam Tax ID checksum using Luhn algorithm variant
    """
    try:
        if len(tax_id_10) != 10:
            return False
        
        # Vietnam uses a weighted checksum algorithm
        weights = [31, 29, 23, 19, 17, 13, 7, 5, 3]
        total = sum(int(tax_id_10[i]) * weights[i] for i in range(9))
        check_digit = (10 - (total % 11)) % 10
        
        return int(tax_id_10[9]) == check_digit
        
    except Exception:
        return False


def normalize_text(text):
    """
    Normalize Vietnamese text for comparison
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove Vietnamese diacritics
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # Remove common company suffixes
    remove_words = ['cong ty', 'tnhh', 'co phan', 'cp', 'ltd', 'company', 'corporation']
    for word in remove_words:
        text = text.replace(word, '')
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text


def fuzzy_match_ratio(str1, str2):
    """
    Calculate fuzzy match ratio between two strings
    """
    norm1 = normalize_text(str1)
    norm2 = normalize_text(str2)
    return SequenceMatcher(None, norm1, norm2).ratio()


def check_supplier_info(seller_data):
    """
    Check supplier information against database
    """
    try:
        check_name = "Kiểm tra thông tin nhà cung cấp"
        
        tax_id = seller_data.get("tax_code", "")
        seller_name = seller_data.get("name", "")
        
        if not tax_id and not seller_name:
            return {
                "name": check_name,
                "status": "FAIL",
                "message": "Thiếu thông tin nhà cung cấp"
            }
        
        # Search for supplier in ERPNext
        filters = {}
        if tax_id:
            filters["tax_id"] = tax_id
        
        suppliers = frappe.get_all(
            "Supplier",
            filters=filters,
            fields=["name", "supplier_name", "tax_id", "supplier_type", "disabled"],
            limit=5
        )
        
        if not suppliers:
            # Try fuzzy match by name
            all_suppliers = frappe.get_all(
                "Supplier",
                fields=["name", "supplier_name", "tax_id", "disabled"],
                limit=100
            )
            
            best_match = None
            best_ratio = 0
            
            for supplier in all_suppliers:
                ratio = fuzzy_match_ratio(seller_name, supplier.supplier_name)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = supplier
            
            if best_match and best_ratio >= 0.7:
                return {
                    "name": check_name,
                    "status": "NEED REVIEW",
                    "message": f"Tìm thấy nhà cung cấp tương tự: {best_match.supplier_name} (độ khớp: {best_ratio*100:.0f}%)",
                    "details": {
                        "matched_supplier": best_match.name,
                        "matched_name": best_match.supplier_name,
                        "match_ratio": best_ratio,
                        "tax_id": best_match.tax_id
                    }
                }
            
            return {
                "name": check_name,
                "status": "FAIL",
                "message": "Không tìm thấy nhà cung cấp trong hệ thống",
                "details": {"seller_name": seller_name, "tax_id": tax_id}
            }
        
        # Found exact match
        supplier = suppliers[0]
        
        if supplier.disabled:
            return {
                "name": check_name,
                "status": "FAIL",
                "message": f"Nhà cung cấp {supplier.supplier_name} đã bị vô hiệu hóa trong hệ thống",
                "details": {"supplier_id": supplier.name, "status": "disabled"}
            }
        
        # Check name similarity
        name_ratio = fuzzy_match_ratio(seller_name, supplier.supplier_name)
        
        if name_ratio < 0.7:
            return {
                "name": check_name,
                "status": "NEED REVIEW",
                "message": f"Tên NCC trên hóa đơn khác với hệ thống (độ khớp: {name_ratio*100:.0f}%)",
                "details": {
                    "invoice_name": seller_name,
                    "system_name": supplier.supplier_name,
                    "match_ratio": name_ratio
                }
            }
        
        return {
            "name": check_name,
            "status": "PASS",
            "message": f"Nhà cung cấp hợp lệ: {supplier.supplier_name}",
            "details": {
                "supplier_id": supplier.name,
                "supplier_name": supplier.supplier_name,
                "tax_id": supplier.tax_id,
                "match_ratio": name_ratio
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in check_supplier_info: {str(e)}")
        return {
            "name": "Kiểm tra thông tin nhà cung cấp",
            "status": "ERROR",
            "message": f"Lỗi khi kiểm tra: {str(e)}"
        }


def cross_check_with_po(invoice_data):
    """
    Cross-check invoice data with Purchase Order
    """
    try:
        check_name = "Kiểm tra đối chiếu PO"
        
        # Look for PO reference in document_code or items
        po_reference = invoice_data.get("document_code") or invoice_data.get("po_reference")
        
        if not po_reference:
            return {
                "name": check_name,
                "status": "PASS",
                "message": "Không có tham chiếu PO, bỏ qua kiểm tra",
                "details": {"po_required": False}
            }
        
        # Search for PO in ERPNext
        pos = frappe.get_all(
            "Purchase Order",
            filters={"name": ["like", f"%{po_reference}%"]},
            fields=["name", "supplier", "supplier_name", "transaction_date", "status", "grand_total"],
            limit=1
        )
        
        if not pos:
            return {
                "name": check_name,
                "status": "FAIL",
                "message": f"Không tìm thấy PO {po_reference} trong hệ thống",
                "details": {"po_reference": po_reference}
            }
        
        po = pos[0]
        po_doc = frappe.get_doc("Purchase Order", po.name)
        
        warnings = []
        errors = []
        
        # Layer 1: General information
        seller_name = invoice_data.get("seller", {}).get("name", "")
        seller_tax_id = invoice_data.get("seller", {}).get("tax_code", "")
        
        supplier_match = fuzzy_match_ratio(seller_name, po.supplier_name)
        if supplier_match < 0.7:
            errors.append(f"NCC trên HĐ ({seller_name}) khác NCC trên PO ({po.supplier_name})")
        
        # Check invoice date >= PO date
        invoice_date_str = invoice_data.get("invoice_date", "")
        if invoice_date_str:
            try:
                invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d")
                po_date = datetime.strptime(str(po.transaction_date), "%Y-%m-%d")
                if invoice_date < po_date:
                    warnings.append(f"Ngày HĐ ({invoice_date_str}) sớm hơn ngày PO ({po.transaction_date})")
            except Exception:
                pass
        
        # Layer 2: Line items
        invoice_items = invoice_data.get("items", [])
        po_items = po_doc.items
        
        for inv_item in invoice_items:
            inv_desc = inv_item.get("description", "")
            inv_qty = inv_item.get("quantity", 0)
            inv_price = inv_item.get("unit_price", 0)
            
            # Find matching item in PO
            best_match = None
            best_ratio = 0
            
            for po_item in po_items:
                ratio = fuzzy_match_ratio(inv_desc, po_item.item_name or po_item.description)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = po_item
            
            if best_match and best_ratio >= 0.6:
                # Check quantity
                if inv_qty > best_match.qty:
                    warnings.append(f"Số lượng '{inv_desc}' ({inv_qty}) vượt PO ({best_match.qty})")
                
                # Check unit price (±2%)
                price_diff = abs(inv_price - best_match.rate) / best_match.rate if best_match.rate > 0 else 0
                if price_diff > 0.02:
                    warnings.append(f"Đơn giá '{inv_desc}' chênh lệch {price_diff*100:.1f}% so với PO")
            else:
                warnings.append(f"Không tìm thấy '{inv_desc}' trong PO")
        
        # Layer 3: Total amount
        invoice_total = invoice_data.get("financial", {}).get("total_amount", 0)
        if invoice_total > po.grand_total * 1.05:  # Allow 5% variance
            errors.append(f"Tổng tiền HĐ ({invoice_total:,.0f}) vượt PO ({po.grand_total:,.0f})")
        
        # Determine status
        if errors:
            return {
                "name": check_name,
                "status": "FAIL",
                "message": f"Đối chiếu PO thất bại: {'; '.join(errors)}",
                "details": {
                    "po_id": po.name,
                    "po_supplier": po.supplier_name,
                    "errors": errors,
                    "warnings": warnings
                }
            }
        elif warnings:
            return {
                "name": check_name,
                "status": "NEED REVIEW",
                "message": f"Đối chiếu PO cần xem xét: {'; '.join(warnings[:2])}",
                "details": {
                    "po_id": po.name,
                    "po_supplier": po.supplier_name,
                    "warnings": warnings
                }
            }
        
        return {
            "name": check_name,
            "status": "PASS",
            "message": f"Đối chiếu PO thành công ({po.name})",
            "details": {
                "po_id": po.name,
                "po_supplier": po.supplier_name,
                "po_total": po.grand_total
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in cross_check_with_po: {str(e)}")
        return {
            "name": "Kiểm tra đối chiếu PO",
            "status": "ERROR",
            "message": f"Lỗi khi kiểm tra: {str(e)}"
        }
































