"""
PDF Extractor - Extract text and images from PDF documents
Supports both digital PDFs and scanned PDFs (using Tesseract OCR)
"""
import hashlib
import io
import frappe
import fitz
from typing import Dict, List, Optional, Tuple

from ..utils.image_utils import save_image

# Lazy import for OCR dependencies
_PIL_Image = None
_pytesseract = None
_TESSERACT_AVAILABLE = None


def _init_ocr():
    """Initialize OCR dependencies lazily."""
    global _PIL_Image, _pytesseract, _TESSERACT_AVAILABLE
    
    if _TESSERACT_AVAILABLE is not None:
        return _TESSERACT_AVAILABLE
    
    try:
        from PIL import Image as PIL_Image_module
        import pytesseract as pytesseract_module
        
        # Test if tesseract binary is available
        pytesseract_module.get_tesseract_version()
        
        _PIL_Image = PIL_Image_module
        _pytesseract = pytesseract_module
        _TESSERACT_AVAILABLE = True
        frappe.logger().info("✅ Tesseract OCR is available")
    except ImportError as e:
        _TESSERACT_AVAILABLE = False
        install_msg = (
            "⚠️ Tesseract OCR dependencies not installed. "
            "To enable OCR for scanned PDFs, run:\n"
            "  pip install pytesseract pillow\n"
            f"  Error: {str(e)}"
        )
        frappe.logger().warning(install_msg)
    except Exception as e:
        _TESSERACT_AVAILABLE = False
        install_msg = (
            "⚠️ Tesseract OCR binary not found. "
            "To enable OCR for scanned PDFs, install Tesseract:\n"
            "  macOS: brew install tesseract tesseract-lang\n"
            "  Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-vie\n"
            f"  Error: {str(e)}"
        )
        frappe.logger().warning(install_msg)
    
    return _TESSERACT_AVAILABLE


def _ocr_image_bytes(image_bytes: bytes, lang: str = "vie+eng") -> str:
    """
    Perform OCR on image bytes using Tesseract.
    
    Args:
        image_bytes: Raw image bytes
        lang: Tesseract language code (default: Vietnamese + English)
    
    Returns:
        Extracted text from image
    """
    if not _init_ocr():
        return ""
    
    try:
        image = _PIL_Image.open(io.BytesIO(image_bytes))
        # Convert to RGB if necessary (handles RGBA, P mode, etc.)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        
        # OCR with Vietnamese + English language support
        text = _pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    except Exception as e:
        frappe.log_error(f"OCR failed: {str(e)}")
        return ""


def _ocr_page_as_image(page: fitz.Page, lang: str = "vie+eng", dpi: int = 300) -> str:
    """
    Render PDF page as image and perform OCR.
    
    Args:
        page: PyMuPDF page object
        lang: Tesseract language code
        dpi: Resolution for rendering (higher = better quality but slower)
    
    Returns:
        Extracted text from page
    """
    if not _init_ocr():
        return ""
    
    try:
        # Render page to image at specified DPI
        zoom = dpi / 72  # 72 is default PDF DPI
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)
        
        # Convert to PIL Image
        image_bytes = pix.tobytes("png")
        image = _PIL_Image.open(io.BytesIO(image_bytes))
        
        # Perform OCR
        text = _pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    except Exception as e:
        frappe.log_error(f"Page OCR failed: {str(e)}")
        return ""


def _is_scanned_pdf(doc: fitz.Document) -> bool:
    """
    Detect if entire PDF is scanned (has no text at all).
    
    Args:
        doc: PyMuPDF document object
    
    Returns:
        True if PDF is scanned (no text found), False otherwise
    """
    total_text = ""
    for page in doc:
        text = page.get_text("text").strip()
        total_text += text
        # Nếu tìm thấy text, không cần kiểm tra thêm
        if total_text:
            return False
    
    # Không có text nào → là scanned PDF
    return True


def extract_from_pdf(pdf_path: str, document_name: Optional[str] = None, ocr_lang: str = "vie+eng") -> Dict:
    """
    Extract text and images from PDF documents.
    Automatically detects scanned PDFs and uses Tesseract OCR.
    
    Args:
        pdf_path: Path to the PDF file
        document_name: AI Document name for tracking
        ocr_lang: Tesseract language code for OCR (default: vie+eng for Vietnamese + English)
    
    Returns:
        Dictionary containing:
        - text: Extracted text with image placeholders
        - images: List of extracted image metadata
        - document_id: Document identifier
        - ocr_used: Whether OCR was used for extraction
    """
    doc = fitz.open(pdf_path)
    all_text_parts: List[str] = []
    images_output: List[Dict] = []
    parent_document: Optional[str] = document_name
    ocr_used = False
    
    try:
        # Kiểm tra 1 lần cho toàn file: có text hay không
        is_scanned = _is_scanned_pdf(doc)
        
        if is_scanned:
            # === SCANNED PDF: Dùng OCR cho toàn bộ file ===
            frappe.logger().info(f"📄 PDF detected as scanned (no text found), attempting OCR...")
            
            if not _init_ocr():
                frappe.msgprint(
                    msg="PDF này là file scan nhưng Tesseract OCR chưa được cài đặt. "
                        "Chỉ có thể trích xuất ảnh, không thể đọc text.",
                    title="Cần cài đặt Tesseract OCR",
                    indicator="orange"
                )
                frappe.logger().warning("Scanned PDF detected but OCR not available - extracting images only")
            else:
                ocr_used = True
            
            for page_index, page in enumerate(doc):
                page_no = page_index + 1
                
                # OCR toàn trang
                ocr_text = _ocr_page_as_image(page, lang=ocr_lang)
                
                if ocr_text:
                    all_text_parts.append(f"[Page {page_no}]\n")
                    all_text_parts.append(ocr_text)
                    all_text_parts.append("\n\n")
                else:
                    frappe.logger().warning(f"⚠️ Page {page_no}: OCR returned no text")
                
                # Vẫn lưu ảnh để tham khảo
                image_list = page.get_images(full=True)
                img_count_on_page = 0
                for img_info in image_list:
                    img_count_on_page += 1
                    xref = img_info[0]
                    try:
                        extracted = doc.extract_image(xref)
                        image_bytes = extracted["image"]
                        ext = extracted.get("ext", "png")
                        
                        img_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                        filename = f"{document_name}_page{page_no}_img{img_hash}.{ext}"
                        file_url, doc_image = save_image(
                            image_bytes,
                            filename,
                            is_private=0,
                            parent_document=parent_document,
                            page_number=page_no,
                            position=f"page:{page_no};image:{img_count_on_page}",
                        )
                        image_id = f"[[IMAGE::{doc_image}]]"
                        all_text_parts.append(image_id + "\n")
                        images_output.append({
                            "id": image_id,
                            "file_url": file_url,
                            "document_image": doc_image,
                            "parent_document": parent_document,
                        })
                    except Exception as ex:
                        frappe.log_error(f"Image extraction failed on page {page_no}: {str(ex)}")
                        continue
        else:
            # === DIGITAL PDF: Dùng extraction thường cho toàn bộ file ===
            for page_index, page in enumerate(doc):
                page_no = page_index + 1
                layout = page.get_text("dict", flags=fitz.TEXT_PRESERVE_IMAGES) or {}
                blocks = layout.get("blocks", [])
                img_count_on_page = 0
                
                for block in blocks:
                    btype = block.get("type")
                    
                    # --- TEXT BLOCK ---
                    if btype == 0:
                        for line in block.get("lines", []):
                            spans = line.get("spans", [])
                            line_text = "".join(span.get("text", "") for span in spans)
                            if line_text.strip():
                                all_text_parts.append(line_text)
                        all_text_parts.append("\n")
                    
                    # --- IMAGE BLOCK ---
                    elif btype == 1:
                        img_count_on_page += 1
                        raw_img = block.get("image", None)
                        image_bytes = None
                        ext = "png"
                        
                        if isinstance(raw_img, (bytes, bytearray)):
                            image_bytes = raw_img
                            if raw_img[:3] == b"\xff\xd8\xff":
                                ext = "jpg"
                        elif isinstance(raw_img, dict):
                            if isinstance(raw_img.get("image"), (bytes, bytearray)):
                                image_bytes = raw_img["image"]
                                if image_bytes[:3] == b"\xff\xd8\xff":
                                    ext = "jpg"
                            elif isinstance(raw_img.get("xref"), int):
                                try:
                                    extracted = doc.extract_image(raw_img["xref"])
                                    image_bytes = extracted["image"]
                                    ext = extracted.get("ext", "png")
                                except Exception as ex:
                                    frappe.log_error(
                                        f"extract_image failed (dict xref) on page {page_no}: {str(ex)}"
                                    )
                                    image_bytes = None
                        elif isinstance(raw_img, int):
                            try:
                                extracted = doc.extract_image(raw_img)
                                image_bytes = extracted["image"]
                                ext = extracted.get("ext", "png")
                            except Exception as ex:
                                frappe.log_error(
                                    f"extract_image failed (int xref={raw_img}) on page {page_no}: {str(ex)}"
                                )
                                image_bytes = None

                        if not image_bytes:
                            frappe.log_error(
                                f"Cannot get image bytes from block image on page {page_no}"
                            )
                            continue
                        
                        try:
                            img_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                            filename = f"{document_name}_image{img_hash}.{ext}"
                            file_url, doc_image = save_image(
                                image_bytes,
                                filename,
                                is_private=0,
                                parent_document=parent_document,
                                page_number=page_no,
                                position=f"page:{page_no};image:{img_count_on_page}",
                            )
                            # Sau khi lưu image, tạo image_id với doc_image name
                            image_id = f"[[IMAGE::{doc_image}]]"
                            all_text_parts.append(image_id + "\n")
                            images_output.append({
                                "id": image_id,
                                "file_url": file_url,
                                "document_image": doc_image,
                                "parent_document": parent_document,
                            })
                        except Exception as ex:
                            frappe.log_error(
                                f"save_image failed on page {page_no}: {str(ex)}"
                            )
                            continue
        
        frappe.db.commit()
        full_text = "".join(all_text_parts).strip()
        
        return {
            "text": full_text,
            "images": images_output,
            "document_id": parent_document,
            "ocr_used": ocr_used,
        }
    finally:
        doc.close()

