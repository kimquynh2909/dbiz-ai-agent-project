"""
Image Utils Module - Image handling and AI metadata generation
"""
import frappe
import json
from typing import Dict, Optional

# Constants
_DOCUMENT_IMAGE_FOLDER = "Home/AI Documents/Images"


def _get_setting(settings, name, default=None):
    """Helper to read a named setting with a default when settings may be None."""
    return getattr(settings, name, default) if settings else default


def save_image(
    image_bytes: bytes,
    filename: str,
    is_private: int = 0,
    *,
    parent_document: Optional[str] = None,
    page_number: Optional[int] = None,
    position: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """
    Save image bytes to Frappe File and optionally create Document Image record.
    
    Args:
        image_bytes: Raw image bytes
        filename: Desired filename
        is_private: Whether file should be private (0 or 1)
        parent_document: Parent AI Document name
        page_number: Page number in source document
        position: Position identifier in document
    
    Returns:
        Tuple of (file_url, document_image_name or None)
    """
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "is_private": is_private,
        "folder": _DOCUMENT_IMAGE_FOLDER,
        "content": image_bytes,
    })
    file_doc.insert(ignore_permissions=True)

    doc_image_name: Optional[str] = None
    if parent_document:
        try:
            image_doc = frappe.get_doc({
                "doctype": "Document Image",
                "title": filename,
                "image_file": file_doc.file_url,
                "parent_document": parent_document,
                "page_number": page_number,
                "position_in_document": position,
                "extraction_method": "PDF",
                "processing_status": "Completed",
                "confidence_score": 1.0,
            })
            image_doc.insert(ignore_permissions=True)
            doc_image_name = image_doc.name
        except Exception as err:
            frappe.log_error(f"Failed to create Document Image for {filename}: {str(err)}")
    
    return file_doc.file_url, doc_image_name


def generate_ai_metadata(text_content: str, settings=None) -> Dict[str, str]:
    """
    Generate AI-powered metadata (description and keywords) for document content.
    
    Args:
        text_content: Document text content
        settings: AI Agent Settings object (optional)
    
    Returns:
        Dictionary with 'description' and 'keywords'
    """
    try:
        preview = text_content[:2500] if len(text_content) > 2500 else text_content
        api_key = _get_setting(settings, 'openai_api_key', '')
        
        if not api_key:
            frappe.log_error("OpenAI API key not configured")
            raise Exception("OpenAI API key not configured")
        
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Bạn là trợ lý phân tích tài liệu chuyên nghiệp."
            }, {
                "role": "user",
                "content": f"""Phân tích đoạn văn bản sau và tạo:
                1. Mô tả ngắn gọn (1-2 câu, tối đa 150 từ) bằng tiếng Việt
                2. 5-8 từ khóa quan trọng nhất, phân tách bằng dấu phẩy

                Văn bản:
                {preview}

                Trả về JSON:
                {{
                    "description": "Mô tả...",
                    "keywords": "từ khóa 1, từ khóa 2, ..."
                }}"""
            }],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        desc = result.get("description", "")
        kw = result.get("keywords", "")
        
        return {
            "description": desc,
            "keywords": kw
        }
    except Exception as e:
        frappe.log_error(f"AI metadata generation failed: {str(e)}")
        raise

